import json
import websocket
import ssl

from core.price_store import price_store

SYMBOL = "BTCUSDT"
EXCHANGE = "bybit"

PROD_URL = "wss://stream.bybit.com/v5/public/spot"
TESTNET_URL = "wss://stream-testnet.bybit.com/v5/public/spot"

def on_message(ws, message):
    try:
        data = json.loads(message)

        if "data" in data and data["data"]:
            book = data["data"]

            bid = float(book["b"][0][0])
            ask = float(book["a"][0][0])

            if bid > 0 and ask > 0:
                price_store.update_price(
                    exchange=EXCHANGE,
                    symbol=SYMBOL,
                    bid=bid,
                    ask=ask
                )

#                print(f"[BYBIT] {SYMBOL} | Bid: {bid} | Ask: {ask}")

    except Exception as e:
        print("⚠️ Erro ao processar mensagem Bybit:", e)

def on_open(ws):
    print("✅ Conectado (on_open) à Bybit websocket")

    subscribe = {
        "op": "subscribe",
        "args": [f"orderbook.1.{SYMBOL}"]
    }

    ws.send(json.dumps(subscribe))

def on_error(ws, error):
    print("❌ WebSocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print("🔒 WebSocket closed:", close_status_code, close_msg)

def start_bybit_ws(use_testnet=False):
    url = TESTNET_URL if use_testnet else PROD_URL

    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}, ping_interval=20, ping_timeout=10)
