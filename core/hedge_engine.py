class HedgeEngine:
    def __init__(self, inventory, orderbook, max_net_btc=0.0002):
        self.inventory = inventory
        self.orderbook = orderbook
        self.max_net_btc = max_net_btc

    def evaluate(self):
        net_btc = self.inventory.net_btc()

        if abs(net_btc) <= self.max_net_btc:
            return None

        side = "sell" if net_btc > 0 else "buy"
        exchange = "BINANCE"  # mais líquida
        price = self.orderbook.best_price(exchange, side)

        if price is None:
            return None

        return {
            "type": "hedge",
            "exchange": exchange,
            "side": side,
            "price": price,
            "qty": abs(net_btc)
        }
