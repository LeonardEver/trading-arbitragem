class Inventory:
    def __init__(self):
        self.balances = {
            "BINANCE": {"BTC": 0.0},
            "BYBIT": {"BTC": 0.0},
            "COINBASE": {"BTC": 0.0},
        }

    def apply_trade(self, exchange, side, qty):
        if side == "buy":
            self.balances[exchange]["BTC"] += qty
        else:
            self.balances[exchange]["BTC"] -= qty

    def net_btc(self):
        return sum(v["BTC"] for v in self.balances.values())


    def snapshot(self):
        return self.balances
