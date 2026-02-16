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
from core.price_store import price_store



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
    # ======================
    # Main Loop (Limpo)
    # ======================
    last_heartbeat = time.time()

    while True:
        # --- SINCRONIZAÇÃO PRICE_STORE -> ORDERBOOK ---
        # (Mantendo a correção que fizemos antes)
        snapshot = price_store.get_snapshot()
        if "BTCUSDT" in snapshot:
            for exchange_name, data in snapshot["BTCUSDT"].items():
                ex_upper = exchange_name.upper()
                if ex_upper in ["BINANCE", "BYBIT", "COINBASE"]:
                    orderbook.update(
                        exchange=ex_upper,
                        bid=data['bid'],
                        ask=data['ask'],
                        bid_qty=0.5,
                        ask_qty=0.5
                    )
        # -----------------------------------------------

        # 1. Avalia Arbitragem
        intent = engine.evaluate()

        if intent:
            # Tenta executar
            trade = trader.handle_intent(intent)

            if trade:
                # SUCESSO
                inventory.apply_trade(
                    exchange=trade["exchange"],
                    side=trade["side"],
                    qty=trade["filled_qty"]
                )
                stats.record_trade(trade)
                
                # Imprime Detalhes COMPLETOS apenas no sucesso
                print(f"\n💰 === TRADE REALIZADO [{time.strftime('%H:%M:%S')}] ===")
                print(f"   Detalhes: {trade}")
                print(f"   PnL Atual: {pnl_engine.mark_to_market()}")
                print(f"   Carteira: {wallet.snapshot()}")
                print("==========================================\n")
            
            else:
                # FALHA NA EXECUÇÃO
                print(f"\n⚠️  FALHA DE EXECUÇÃO [{time.strftime('%H:%M:%S')}]")
                print(f"   Intenção: {intent}")
                print(f"   Motivo: Liquidez insuficiente ou erro no PaperTrader\n")

        # 2. Avalia Hedge (Proteção)
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

                print(f"\n🛡️ === HEDGE REALIZADO [{time.strftime('%H:%M:%S')}] ===")
                print(f"   Detalhes: {hedge_trade}")
                print(f"   Net BTC: {inventory.net_btc()}")
                print("==========================================\n")

        # 3. Heartbeat (Sinal de vida a cada 30 segundos)
        if time.time() - last_heartbeat > 30:
            print(f"⏳ Bot rodando... buscando oportunidades... [{time.strftime('%H:%M:%S')}]")
            last_heartbeat = time.time()

        time.sleep(0.2)