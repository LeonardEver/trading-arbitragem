class OrderBook:
    def __init__(self):
        self.books = {
            "BINANCE": {"bids": [], "asks": []},
            "BYBIT": {"bids": [], "asks": []},
            "COINBASE": {"bids": [], "asks": []},
        }

    def update(self, exchange, bid, ask, bid_qty=1.0, ask_qty=1.0):
        self.books[exchange]["bids"] = [(float(bid), float(bid_qty))]
        self.books[exchange]["asks"] = [(float(ask), float(ask_qty))]

    def simulate_market_order(self, exchange, side, qty):
        """
        Walk the book and return avg_price, filled_qty
        """
        book = self.books[exchange]["asks" if side == "buy" else "bids"]

        remaining = qty
        cost = 0.0
        filled = 0.0

        for price, available in book:
            take = min(available, remaining)
            cost += take * price
            filled += take
            remaining -= take

            if remaining <= 0:
                break

        if filled == 0:
            return None, 0.0

        avg_price = cost / filled
        return avg_price, filled
