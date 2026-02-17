# ws/binance_ws.py
import json
import websocket
import ssl
import time
from core.price_store import price_store

# URL Base para Futuros (sem a porta 9443 e sem o stream na URL)
PROD_URL = "wss://fstream.binance.com/ws"
TESTNET_URL = "wss://stream.binancefuture.com/ws" 

SYMBOL = "BTCUSDT"
EXCHANGE = "binance" # Deve ser minúsculo para bater com o PriceStore

def on_open(ws):
    print(f"✅ Conectado (on_open) à Binance Futures")
    
    # Payload para se inscrever no BookTicker de Futuros
    # Documentação: https://binance-docs.github.io/apidocs/futures/en/#live-subscribing-unsubscribing-to-streams
    subscribe_message = {
        "method": "SUBSCRIBE",
        "params": [
            "btcusdt@bookTicker"
        ],
        "id": 1
    }
    ws.send(json.dumps(subscribe_message))

def on_message(ws, message):
    try:
        data = json.loads(message)

        # Verifica se é uma mensagem de bookTicker (tem 'b' e 'a')
        # Ignora mensagens de confirmação de subscribe (que têm 'id')
        if 'b' in data and 'a' in data:
            bid = float(data['b'])
            ask = float(data['a'])

            if bid > 0 and ask > 0:
                price_store.update_price(
                    exchange=EXCHANGE,
                    symbol=SYMBOL,
                    bid=bid,
                    ask=ask
                )
                # Opcional: Descomente para debug se necessário
                # print(f"[BINANCE] {bid} / {ask}")

    except Exception as e:
        print(f"⚠️ Erro parse Binance: {e}")

def on_error(ws, error):
    print("❌ Binance WS Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("🔒 Binance WS Closed")

def start_binance_ws():
    # Loop infinito de reconexão
    while True:
        try:
            print(f"➡ Conectando Binance em: {PROD_URL}")
            ws = websocket.WebSocketApp(
                PROD_URL,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            ws.run_forever(
                sslopt={"cert_reqs": ssl.CERT_NONE},
                ping_interval=20,
                ping_timeout=10
            )
        except Exception as e:
            print(f"Erro crítico Binance WS: {e}")
        
        print("Reconectando Binance em 5s...")
        time.sleep(5)