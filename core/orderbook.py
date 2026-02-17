# core/orderbook.py
class OrderBook:
    def __init__(self):
        # ADICIONADO: "KUCOIN"
        self.books = {
            "BINANCE": {"bids": [], "asks": []},
            "BYBIT":   {"bids": [], "asks": []},
            "COINBASE": {"bids": [], "asks": []},
            "KUCOIN":  {"bids": [], "asks": []}, 
        }

    def get_price(self, exchange, side):
        exchange = exchange.upper()
        if not side.endswith("s"):
            side += "s"
            
        if exchange in self.books:
            orders = self.books[exchange].get(side)
            if orders and len(orders) > 0:
                return orders[0][0]
        return None

    def update(self, exchange, bid, ask, bid_qty=1.0, ask_qty=1.0):
        # Garante que exchange esteja em maiúsculo para evitar KeyError
        exchange = exchange.upper()
        if exchange in self.books:
            self.books[exchange]["bids"] = [(float(bid), float(bid_qty))]
            self.books[exchange]["asks"] = [(float(ask), float(ask_qty))]

    def simulate_market_order(self, exchange, side, qty):
        exchange = exchange.upper()
        # Proteção extra caso a exchange não exista
        if exchange not in self.books:
            return None, 0.0
            
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