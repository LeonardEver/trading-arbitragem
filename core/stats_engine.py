# core/stats_engine.py

class StatsEngine:
    def __init__(self):
        self.reset()

    def reset(self):
        self.trades = 0

        self.maker_filled = 0
        self.maker_cancelled = 0
        self.maker_timeout = 0
        self.maker_fallback = 0

        self.taker_filled = 0

        self.slippage_sum = 0.0
        self.slippage_count = 0

        self.pnl_by_exchange = {}
        self.pnl_by_mode = {"maker": 0.0, "taker": 0.0}

    # =========================
    # TRADE HOOK
    # =========================
    def record_trade(self, trade):
        self.trades += 1

        mode = trade["mode"]
        exchange = trade["exchange"]

        # contadores maker/taker
        if mode == "maker":
            self.maker_filled += 1
        else:
            self.taker_filled += 1

        # slippage
        if mode == "taker":
            self.slippage_sum += trade.get("slippage", 0)
            self.slippage_count += 1

    # =========================
    # MAKER EVENTS
    # =========================
    def record_maker_event(self, status):
        if status == "cancelled":
            self.maker_cancelled += 1
        elif status == "timeout":
            self.maker_timeout += 1
        elif status == "fallback":
            self.maker_fallback += 1

    # =========================
    # PnL
    # =========================
    def record_pnl(self, exchange, pnl, mode):
        self.pnl_by_exchange.setdefault(exchange, 0.0)
        self.pnl_by_exchange[exchange] += pnl
        self.pnl_by_mode[mode] += pnl

    # =========================
    # SNAPSHOT
    # =========================
    def snapshot(self):
        maker_total = (
            self.maker_filled +
            self.maker_cancelled +
            self.maker_timeout +
            self.maker_fallback
        )

        maker_fill_rate = (
            self.maker_filled / maker_total
            if maker_total > 0 else 0
        )

        avg_slippage = (
            self.slippage_sum / self.slippage_count
            if self.slippage_count > 0 else 0
        )

        return {
            "trades": self.trades,
            "maker_fill_rate": round(maker_fill_rate, 3),
            "maker_filled": self.maker_filled,
            "maker_cancelled": self.maker_cancelled,
            "maker_timeout": self.maker_timeout,
            "maker_fallback": self.maker_fallback,
            "taker_filled": self.taker_filled,
            "avg_taker_slippage": round(avg_slippage, 6),
            "pnl_by_exchange": self.pnl_by_exchange,
            "pnl_by_mode": self.pnl_by_mode
        }
