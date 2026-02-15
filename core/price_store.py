# core/price_store.py
import threading
import time

class PriceStore:
    def __init__(self):
        # Estrutura:
        # {
        #   "BTCUSDT": {
        #       "binance": {"bid": 0, "ask": 0, "ts": 0},
        #       "bybit":   {"bid": 0, "ask": 0, "ts": 0}
        #   }
        # }
        self.prices = {}
        self.lock = threading.Lock()

    def update_price(self, exchange: str, symbol: str, bid: float, ask: float):
        with self.lock:
            if symbol not in self.prices:
                self.prices[symbol] = {}

            self.prices[symbol][exchange] = {
                "bid": bid,
                "ask": ask,
                "ts": time.time()
            }

    def get_prices(self, symbol: str):
        with self.lock:
            return self.prices.get(symbol, {}).copy()

    def get_snapshot(self):
        with self.lock:
            return self.prices.copy()


# Singleton (usado pelo bot inteiro)
price_store = PriceStore()
