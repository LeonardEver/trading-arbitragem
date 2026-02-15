from core.arbitrage_engine import ArbitrageEngine
from core.price_store import price_store
from core.paper_trader import PaperTrader
import time

price_store.update_price("binance", "BTCUSDT", 70761.15, 70761.16)
price_store.update_price("bybit", "BTCUSDT", 70763.50, 70763.60)

engine = ArbitrageEngine(
    symbol="BTCUSDT",
    min_spread_pct=0.00001,
    cooldown_seconds=1
)

trader = PaperTrader(initial_usd=50, trade_usd=10)

for _ in range(3):
    intent = engine.evaluate()
    result = trader.handle_intent(intent)
    print(result)
    time.sleep(1.2)
