# ws/bybit_ws.py
import json
import websocket
import ssl
from core.price_store import price_store

SYMBOL = "BTCUSDT"
EXCHANGE = "bybit"

# URL CORRIGIDA PARA FUTUROS (LINEAR)
PROD_URL = "wss://stream.bybit.com/v5/public/linear"
TESTNET_URL = "wss://stream-testnet.bybit.com/v5/public/linear"

def on_message(ws, message):
    try:
        data = json.loads(message)
        # O formato da Bybit V5 Linear é similar, mas garantimos o parse
        if "data" in data and data["data"]:
            book = data["data"]
            # Em futuros, o book vem igual: b=[[price, size]], a=[[price, size]]
            bid = float(book["b"][0][0])
            ask = float(book["a"][0][0])

            if bid > 0 and ask > 0:
                price_store.update_price(exchange=EXCHANGE, symbol=SYMBOL, bid=bid, ask=ask)

    except Exception as e:
        pass # Ignora erros de heartbeat/ping para não sujar log

def on_open(ws):
    print(f"✅ Conectado (on_open) à Bybit Futures ({SYMBOL})")
    # Tópico para Futuros é o mesmo: orderbook.1.SYMBOL
    subscribe = {
        "op": "subscribe",
        "args": [f"orderbook.1.{SYMBOL}"]
    }
    ws.send(json.dumps(subscribe))

# ... (O resto das funções on_error, on_close, start_bybit_ws mantém igual)
def on_error(ws, error): print("❌ WebSocket error:", error)
def on_close(ws, c, m): print("🔒 WebSocket closed")

def start_bybit_ws(use_testnet=False):
    url = TESTNET_URL if use_testnet else PROD_URL
    ws = websocket.WebSocketApp(url, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}, ping_interval=20, ping_timeout=10)