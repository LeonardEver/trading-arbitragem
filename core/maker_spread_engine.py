# core/maker_spread_engine.py
from core.price_store import price_store

class MakerSpreadEngine:
    def __init__(
        self,
        maker_offset_pct=0.00002,   # 0.01% fora do best
        fees_pct=0.0004            # maker fee média
    ):
        self.maker_offset_pct = maker_offset_pct
        self.fees_pct = fees_pct

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

                best_bid = buy_book["bid"]
                best_ask = sell_book["ask"]

                # Preços MAKER
                maker_buy_price = best_bid * (1 - self.maker_offset_pct)
                maker_sell_price = best_ask * (1 + self.maker_offset_pct)

                spread_abs = maker_sell_price - maker_buy_price
                spread_pct = spread_abs / maker_buy_price

                net_spread = spread_pct - (2 * self.fees_pct)

                if net_spread <= 0:
                    continue

                opportunities.append({
                    "symbol": symbol,
                    "buy_exchange": buy_ex,
                    "sell_exchange": sell_ex,
                    "maker_buy_price": round(maker_buy_price, 2),
                    "maker_sell_price": round(maker_sell_price, 2),
                    "spread_abs": round(spread_abs, 2),
                    "spread_pct": spread_pct,
                    "net_spread": net_spread
                })

        return opportunities
