# ws/kucoin_ws.py
import json
import time
import requests
import websocket
import threading
from core.price_store import price_store

# KuCoin exige um "token" via HTTP antes de conectar no WS
HTTP_ENDPOINT = "https://api-futures.kucoin.com/api/v1/bullet-public"
SYMBOL_KUCOIN = "XBTUSDTM"  # Nome na KuCoin
SYMBOL_INTERNAL = "BTCUSDT" # Nome no seu Bot
EXCHANGE_NAME = "kucoin"

def get_ws_token():
    """Busca o token dinâmico e o endpoint para conexão"""
    try:
        response = requests.post(HTTP_ENDPOINT)
        data = response.json()
        if data['code'] == '200000':
            token = data['data']['token']
            endpoint = data['data']['instanceServers'][0]['endpoint']
            return token, endpoint
    except Exception as e:
        print(f"⚠️ Erro ao obter token KuCoin: {e}")
    return None, None

def on_open(ws):
    print(f"✅ Conectado (on_open) à KuCoin Futures ({SYMBOL_KUCOIN})")
    # Mensagem de inscrição (Ticker V2 é mais rápido)
    subscribe_msg = {
        "id": 1,
        "type": "subscribe",
        "topic": f"/contractMarket/tickerV2:{SYMBOL_KUCOIN}", 
        "response": True
    }
    ws.send(json.dumps(subscribe_msg))

def on_message(ws, message):
    try:
        data = json.loads(message)
        
        # O formato da mensagem de ticker da KuCoin é:
        # data: { "bestBidPrice": "...", "bestAskPrice": "..." }
        if data.get('type') == 'message' and 'data' in data:
            ticker = data['data']
            bid = float(ticker.get('bestBidPrice', 0))
            ask = float(ticker.get('bestAskPrice', 0))

            if bid > 0 and ask > 0:
                price_store.update_price(
                    exchange=EXCHANGE_NAME,
                    symbol=SYMBOL_INTERNAL,
                    bid=bid,
                    ask=ask
                )
    except Exception as e:
        pass

def on_error(ws, error):
    print(f"❌ KuCoin WS Error: {error}")

def on_close(ws, c, m):
    print("🔒 KuCoin WS Closed")

def start_kucoin_daemon():
    """Função que gerencia a conexão e reconexão"""
    while True:
        token, endpoint = get_ws_token()
        if token and endpoint:
            # Monta a URL com o token
            connect_url = f"{endpoint}?token={token}"
            
            ws = websocket.WebSocketApp(
                connect_url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever(ping_interval=20, ping_timeout=10)
        
        print("⚠️ Tentando reconectar KuCoin em 10s...")
        time.sleep(10)

def start_kucoin_ws():
    # Roda em thread separada para não travar o main
    t = threading.Thread(target=start_kucoin_daemon, daemon=True)
    t.start()
    return t