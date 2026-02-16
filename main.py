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
        # ============================================================
        # 🔄 1. SINCRONIZAÇÃO (A PONTE QUE FALTAVA)
        # ============================================================
        # Pega os dados frescos dos WebSockets
        snapshot = price_store.get_snapshot()
        
        # Se tiver dados de BTCUSDT, injeta no OrderBook
        if "BTCUSDT" in snapshot:
            for exchange_name, data in snapshot["BTCUSDT"].items():
                ex_upper = exchange_name.upper()
                # Atualiza apenas as exchanges conhecidas
                if ex_upper in ["BINANCE", "BYBIT", "COINBASE"]:
                    orderbook.update(
                        exchange=ex_upper,
                        bid=data['bid'],
                        ask=data['ask'],
                        bid_qty=0.5,  # Liquidez simulada
                        ask_qty=0.5
                    )
        # ============================================================

# 🔍 2. RAIO-X DE PREÇOS (DEBUG COMPLETO)
        try:
            b_bid = orderbook.get_price("BINANCE", "bid")
            b_ask = orderbook.get_price("BINANCE", "ask")
            by_bid = orderbook.get_price("BYBIT", "bid")
            by_ask = orderbook.get_price("BYBIT", "ask")

            # Verifica se temos TODOS os preços necessários
            if b_bid and b_ask and by_bid and by_ask:
                
                # --- LADO A: Vende Binance / Compra Bybit ---
                spread_1 = (b_bid / by_ask) - 1
                
                # --- LADO B: Vende Bybit / Compra Binance ---
                spread_2 = (by_bid / b_ask) - 1

                # Imprime se houver QUALQUER spread positivo (mesmo 0.0001%)
                # ou se o spread for negativo mas próximo de zero, só pra confirmar que está lendo
                if spread_1 > 0:
                    print(f"👀 OPP A (Vende Bin): Bin {b_bid:.2f} > Byb {by_ask:.2f} | Lucro Bruto: {spread_1*100:.4f}%")
                
                if spread_2 > 0:
                    print(f"👀 OPP B (Vende Byb): Byb {by_bid:.2f} > Bin {b_ask:.2f} | Lucro Bruto: {spread_2*100:.4f}%")

            else:
                # Se cair aqui, o OrderBook ainda está vazio em alguma ponta
                # Isso ajuda a saber se uma das corretoras caiu
                print(f"⚠️ AGUARDANDO DADOS... Bin: {b_bid}/{b_ask} | Byb: {by_bid}/{by_ask}")

        except Exception as e:
            print(f"Erro no Debug: {e}")

        
        # 3. Lógica Original do Bot (Arbitragem)
        intent = engine.evaluate()

        if intent:
            trade = trader.handle_intent(intent)
            if trade:
                inventory.apply_trade(trade["exchange"], trade["side"], trade["filled_qty"])
                stats.record_trade(trade)
                print(f"\n💰 TRADE EXECUTADO: {trade}")
                print(f"   PnL: {pnl_engine.mark_to_market()}")

        # 4. Lógica de Hedge
        hedge_intent = hedge_engine.evaluate()
        if hedge_intent:
            hedge_trade = trader.handle_intent(hedge_intent)
            if hedge_trade:
                inventory.apply_trade(hedge_trade["exchange"], hedge_trade["side"], hedge_trade["filled_qty"])
                stats.record_trade(hedge_trade)
                print(f"\n🛡️ HEDGE EXECUTADO: {hedge_trade}")

        # 5. Heartbeat (Sinal de vida a cada 30s)
        if time.time() - last_heartbeat > 30:
            print(f"⏳ Bot rodando... [Sync OK] [{time.strftime('%H:%M:%S')}]")
            last_heartbeat = time.time()

        time.sleep(0.2)