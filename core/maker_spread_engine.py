# core/maker_spread_engine.py
from core.price_store import price_store

class MakerSpreadEngine:
    def __init__(
        self,
        maker_offset_pct=0.0002,
        fees=None
    ):
        self.maker_offset_pct = maker_offset_pct
        self.fees = fees or {
            "default": {"maker": 0.001, "taker": 0.001}
        }

    def get_fee(self, exchange: str, side: str):
        return self.fees.get(exchange, self.fees["default"])[side]

    def find_opportunities(self, symbol: str):
        prices = price_store.get_prices(symbol)
        if len(prices) < 2:
            return []

        exchanges = list(prices.keys())
        opportunities = []

        for buy_ex in exchanges:
            for sell_ex in exchanges:
                if buy_ex == sell_ex:
                    continue

                buy_book = prices[buy_ex]
                sell_book = prices[sell_ex]

                best_ask = buy_book["ask"]   # comprar
                best_bid = sell_book["bid"]  # vender


                maker_buy_price = best_ask * (1 - self.maker_offset_pct)
                maker_sell_price = best_bid * (1 + self.maker_offset_pct)

                spread_abs = maker_sell_price - maker_buy_price
                spread_pct = spread_abs / maker_buy_price

                buy_fee = self.get_fee(buy_ex, "maker")
                sell_fee = self.get_fee(sell_ex, "maker")

                net_spread = spread_pct - (buy_fee + sell_fee)

                if net_spread <= 0:
                    continue

                opportunities.append({
                    "symbol": symbol,
                    "buy_exchange": buy_ex,
                    "sell_exchange": sell_ex,
                    "net_spread": net_spread,
                    "spread_pct": spread_pct,
                    "fees_total": buy_fee + sell_fee,
                })

        return opportunities
