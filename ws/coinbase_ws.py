# ws/coinbase_ws.py
import json
import ssl
import websocket
from core.price_store import price_store

# URLs de conexão
SANDBOX = "wss://ws-feed-public.sandbox.exchange.coinbase.com"
PROD = "wss://ws-feed.exchange.coinbase.com"

# Configuração dos Símbolos
PRODUCT_COINBASE = "BTC-USD"  # O nome que a Coinbase usa para se inscrever
SYMBOL_INTERNAL = "BTCUSDT"   # O nome padronizado que seu bot usa internamente

def on_open(ws):
    print("✅ Conectado à Coinbase (on_open)")
    subscribe_msg = {
        "type": "subscribe",
        "product_ids": [PRODUCT_COINBASE],
        "channels": ["ticker"]
    }
    ws.send(json.dumps(subscribe_msg))

def on_message(ws, message):
    try:
        data = json.loads(message)
        
        # Filtra apenas mensagens do tipo 'ticker'
        if data.get("type") == "ticker":
            # Converte para float (Coinbase envia strings)
            bid = float(data.get("best_bid", 0))
            ask = float(data.get("best_ask", 0))

            if bid > 0 and ask > 0:
                # AQUI ESTÁ O TRUQUE:
                # Recebemos dados de PRODUCT_COINBASE ("BTC-USD")
                # Mas salvamos como SYMBOL_INTERNAL ("BTCUSDT")
                price_store.update_price(
                    exchange="coinbase",  # Nome da exchange minúsculo para padronizar
                    symbol=SYMBOL_INTERNAL, 
                    bid=bid,
                    ask=ask
                )
                
                # print(f"[COINBASE] {SYMBOL_INTERNAL} | Bid: {bid} | Ask: {ask}")

    except Exception as e:
        print(f"⚠️ Erro ao processar msg Coinbase: {e}")

def on_error(ws, error):
    print("❌ Coinbase WS error:", error)

def on_close(ws, code, reason):
    print("🔒 Coinbase closed:", code, reason)

def start_coinbase_ws():
    """
    Função chamada pelo main.py para iniciar a conexão
    """
    ws = websocket.WebSocketApp(
        PROD,
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