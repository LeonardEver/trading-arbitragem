# core/arbitrage_engine.py

import time
from core.maker_spread_engine import MakerSpreadEngine


class ArbitrageEngine:
    def __init__(
        self,
        symbol,
        min_net_spread=0.00002,
        cooldown_seconds=5,
        mode="maker"
    ):
        self.symbol = symbol
        self.min_net_spread = min_net_spread
        self.cooldown_seconds = cooldown_seconds
        self.mode = mode

        self.maker_engine = MakerSpreadEngine()
        self.last_trade_ts = {}

        print(f"🤖 Arbitrage Engine iniciado | modo={self.mode}")

    def evaluate(self):
        """
        Avalia oportunidades de arbitragem MAKER
        Retorna um intent ou None
        """

        if self.mode != "maker":
            return None

        opportunities = self.maker_engine.find_opportunities(self.symbol)
        if not opportunities:
            return None

        # Escolhe melhor oportunidade
        best = max(opportunities, key=lambda x: x["net_spread"])

        if best["net_spread"] < self.min_net_spread:
            return None

        route = f"{best['buy_exchange']}->{best['sell_exchange']}"
        now = time.time()

        # Cooldown por rota
        if now - self.last_trade_ts.get(route, 0) < self.cooldown_seconds:
            return None

        self.last_trade_ts[route] = now

        return {
            "type": "MAKER_ARBITRAGE",
            "symbol": self.symbol,
            "buy_exchange": best["buy_exchange"],
            "sell_exchange": best["sell_exchange"],
            "maker_buy_price": best["maker_buy_price"],
            "maker_sell_price": best["maker_sell_price"],
            "net_spread": best["net_spread"],
            "ts": now
        }
