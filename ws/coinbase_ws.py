# coinbase_ws.py
import json
import sys
import websocket
import ssl

SANDBOX = "wss://ws-feed-public.sandbox.exchange.coinbase.com"
PROD = "wss://ws-feed.exchange.coinbase.com"

PRODUCT = "BTC-USD"  # Coinbase usa formato BTC-USD; mapeie conforme necessário

def on_open(ws):
    print("✅ Conectado à Coinbase (on_open)")
    subscribe_msg = {
        "type": "subscribe",
        "product_ids": [PRODUCT],
        "channels": ["ticker"]
    }
    ws.send(json.dumps(subscribe_msg))

def on_message(ws, message):
    data = json.loads(message)
    # ticker messages têm 'best_bid' e 'best_ask'
    if data.get("type") == "ticker":
        bid = data.get("best_bid")
        ask = data.get("best_ask")
 #       if bid and ask:
#            print(f"[COINBASE] Bid: {bid} | Ask: {ask}")

def on_error(ws, error):
    print("❌ Coinbase WS error:", error)

def on_close(ws, code, reason):
    print("🔒 Coinbase closed:", code, reason)

def start_coinbase_ws():
    """
    Função padrão para ser chamada pelo main.py
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
