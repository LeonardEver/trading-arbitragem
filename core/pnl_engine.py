# core/pnl_engine.py

class PnLEngine:
    def __init__(self, wallet, orderbook):
        self.wallet = wallet
        self.orderbook = orderbook

    def mark_to_market(self):
        pnl = {}

        for ex, bal in self.wallet.balances.items():
            usd = bal.get("USD", 0.0)
            btc = bal.get("BTC", 0.0)

            book = self.orderbook.books.get(ex)

            # book ainda não inicializado
            if not book:
                pnl[ex] = round(usd, 2)
                continue

            bid = book.get("bid")
            ask = book.get("ask")

            # preço ainda incompleto
            if bid is None or ask is None:
                pnl[ex] = round(usd, 2)
                continue

            mid = (bid + ask) / 2
            pnl[ex] = round(usd + btc * mid, 2)

        return pnl
