# core/spread_engine.py

from core.price_store import price_store

class SpreadEngine:
    def __init__(self):
        self.fees = {
            "binance": 0.001,
            "bybit": 0.001
        }

    def find_opportunities(self, symbol):
        prices = price_store.get_prices(symbol)
        exchanges = list(prices.keys())

        opportunities = []

        for buy_ex in exchanges:
            for sell_ex in exchanges:
                if buy_ex == sell_ex:
                    continue

                buy_ask = prices[buy_ex]["ask"]
                sell_bid = prices[sell_ex]["bid"]

                if buy_ask <= 0 or sell_bid <= 0:
                    continue

                spread_abs = sell_bid - buy_ask
                spread_pct = spread_abs / buy_ask

                fee_buy = self.fees.get(buy_ex, 0)
                fee_sell = self.fees.get(sell_ex, 0)

                total_fee = fee_buy + fee_sell

                # spread líquido
                net_spread = spread_pct - total_fee

                if net_spread > 0:
                    opportunities.append({
                        "symbol": symbol,
                        "buy_exchange": buy_ex,
                        "sell_exchange": sell_ex,
                        "buy_price": buy_ask,
                        "sell_price": sell_bid,
                        "spread_abs": round(spread_abs, 2),
                        "spread_pct": spread_pct,
                        "net_spread": net_spread
                    })

        return opportunities
