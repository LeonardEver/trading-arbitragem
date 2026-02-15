# kucoin_ws.py
import json
import time
import sys
import requests
import websocket
import ssl
from urllib.parse import urljoin

# escolha sandbox ou prod
KUCOIN_SANDBOX_REST = "https://openapi-sandbox.kucoin.com"
KUCOIN_PROD_REST = "https://api.kucoin.com"

# o topic usa o formato SYMBOL com dash: 'BTC-USDT'
SYMBOL = "BTC-USDT"

def get_bullet_public(rest_base):
    url = rest_base + "/api/v1/bullet-public"
    resp = requests.post(url, timeout=5)
    resp.raise_for_status()
    return resp.json()["data"]

def on_open(ws):
    print("✅ Conectado à KuCoin WS (on_open)")
    # subscribe Level1 topic
    sub = {
        "id": int(time.time() * 1000),
        "type": "subscribe",
        "topic": f"/spotMarket/level1:{SYMBOL}",
        "response": True
    }
    ws.send(json.dumps(sub))

def on_message(ws, message):
    try:
        data = json.loads(message)
    except Exception:
        print("Raw:", message)
        return

    # Mensagens Level1 têm 'subject' ou 'type' com dados em 'data'
    if data.get("topic") and data.get("data"):
        d = data["data"]
        # KuCoin Level1 data fields: bestBidPrice / bestAskPrice or 'bestBid' e 'bestAsk' dependendo da versão
        bid = d.get("bestBidPrice") or d.get("bestBid")
        ask = d.get("bestAskPrice") or d.get("bestAsk")
        if bid and ask:
            print(f"[KUCOIN] Bid: {bid} | Ask: {ask}")
    elif data.get("type") == "ack":
        print("[KUCOIN] subscribe ack:", data)

def on_error(ws, error):
    print("❌ KuCoin WS error:", error)

def on_close(ws, code, reason):
    print("🔒 KuCoin closed:", code, reason)

if __name__ == "__main__":
    rest = KUCOIN_SANDBOX_REST
    if len(sys.argv) > 1 and sys.argv[1].lower() == "prod":
        rest = KUCOIN_PROD_REST

    print("Obtendo token bullet-public via REST:", rest + "/api/v1/bullet-public")
    try:
        info = get_bullet_public(rest)
    except Exception as e:
        print("Erro ao obter token:", e)
        raise SystemExit(1)

    # info deve conter 'instanceServers' (lista) e 'token'
    instance = info["instanceServers"][0]
    endpoint = instance["endpoint"]
    token = info["token"]

    # montar URL final — muitas vezes endpoint já precisa do token como query, mas normalmente conectar e mandar subscribe funciona diretamente.
    ws_url = endpoint
    print("Conectar WS KuCoin endpoint:", ws_url)
    ws = websocket.WebSocketApp(ws_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    # pingInterval / pingTimeout são informados no response; vamos usar ssl opt
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
