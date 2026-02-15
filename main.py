import threading
import time

from ws.binance_ws import start_binance_ws
from ws.bybit_ws import start_bybit_ws
from ws.coinbase_ws import start_coinbase_ws

from core.arbitrage_engine import ArbitrageEngine
from core.paper_trader import PaperTrader
from core.inventory import Inventory
from core.hedge_engine import HedgeEngine
from simulator.wallet import Wallet
from core.pnl_engine import PnLEngine
from core.orderbook import OrderBook
from core.stats_engine import StatsEngine



def run_ws(target, daemon=True):
    t = threading.Thread(target=target, daemon=daemon)
    t.start()
    return t


if __name__ == "__main__":
    print("🚀 Bot de Arbitragem iniciado")

    # ======================
    # OrderBook (GLOBAL)
    # ======================
    orderbook = OrderBook()

    # ⚠️ IMPORTANTE:
    # Seus WS precisam atualizar esse orderbook
    # ex: orderbook.update("BINANCE", bid, ask)

    # ======================
    # WebSockets
    # ======================
    run_ws(start_binance_ws, daemon=True)
    run_ws(start_bybit_ws, daemon=True)
    run_ws(start_coinbase_ws, daemon=False)

    time.sleep(3)

    # ======================
    # Engines
    # ======================
    engine = ArbitrageEngine(
        symbol="BTCUSDT",
        min_net_spread=0.000001,
        cooldown_seconds=1
    )

    wallet = Wallet(initial_usd=50.0)
    trader = PaperTrader(wallet, orderbook)
    inventory = Inventory()
    hedge_engine = HedgeEngine(inventory, orderbook)
    pnl_engine = PnLEngine(wallet, orderbook)
    stats = StatsEngine()


    print("🧠 Loop de arbitragem iniciado")

    # ======================
    # Main Loop
    # ======================
    while True:
        trade = None
        hedge_trade = None

        intent = engine.evaluate()

        if intent:
            trade = trader.handle_intent(intent)

            if trade:
                inventory.apply_trade(
                    exchange=trade["exchange"],
                    side=trade["side"],
                    qty=trade["filled_qty"]
                )

                stats.record_trade(trade)

                print("💰 TRADE:", trade)
                print("📦 INVENTORY:", inventory.snapshot())
                print("💼 WALLET:", wallet.snapshot())

        hedge_intent = hedge_engine.evaluate()

        if hedge_intent:
            hedge_trade = trader.handle_intent(hedge_intent)

            if hedge_trade:
                inventory.apply_trade(
                    exchange=hedge_trade["exchange"],
                    side=hedge_trade["side"],
                    qty=hedge_trade["filled_qty"]
                )

                stats.record_trade(hedge_trade)

                print("🛡️ HEDGE:", hedge_trade)

        pnl = pnl_engine.mark_to_market()
        print("📊 PnL MTM:", pnl)
        print("📈 NET BTC:", inventory.net_btc())
        print("📈 STATS:", stats.snapshot())

        time.sleep(0.2)
