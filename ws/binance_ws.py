# ws/binance_ws.py
import json
import websocket
import ssl
import time
import sys

from core.price_store import price_store

TESTNET_URL = "wss://ftestnet.binance.vision/ws/btcusdt@bookTicker"
PROD_URL = "wss://fstream.binance.com:9443/ws/btcusdt@bookTicker"

SYMBOL = "BTCUSDT"
EXCHANGE = "binance"

def on_open(ws):
    print("✅ Conectado (on_open) à Binance websocket")

def on_message(ws, message):
    try:
        data = json.loads(message)

        bid = float(data.get('b', 0))
        ask = float(data.get('a', 0))

        if bid > 0 and ask > 0:
            price_store.update_price(
                exchange=EXCHANGE,
                symbol=SYMBOL,
                bid=bid,
                ask=ask
            )

#            print(f"[BINANCE] {SYMBOL} | Bid: {bid} | Ask: {ask}")

    except Exception as e:
        print("⚠️ Erro ao parsear mensagem:", e)

def on_error(ws, error):
    print("❌ WebSocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print("🔒 WebSocket closed:", close_status_code, close_msg)

def try_connect(url):
    print(f"\n➡ Conectando em: {url}")
    ws = websocket.WebSocketApp(
        url,
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
        
def start_binance_ws():
    try_connect(PROD_URL)
