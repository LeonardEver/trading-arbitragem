# core/arbitrage_engine.py
import time

class ArbitrageEngine:
    def __init__(self, symbol, min_net_spread=0.001, cooldown_seconds=3):
        self.symbol = symbol
        self.min_net_spread = min_net_spread
        self.cooldown = cooldown_seconds
        self.last_trade_time = 0
        self.orderbook = None  # Será injetado pelo main.py ou passado no evaluate

    def evaluate(self, orderbook=None):
        """
        Analisa o OrderBook em busca de oportunidades de arbitragem entre QUAISQUER exchanges disponíveis.
        """
        # Se o orderbook não foi passado no init nem aqui, não faz nada
        if orderbook is None and self.orderbook is None:
            return None
        
        book = orderbook if orderbook else self.orderbook
        
        # Respeita o Cooldown
        if time.time() - self.last_trade_time < self.cooldown:
            return None

        best_opportunity = None
        best_spread = -999.0

        # Identifica todas as exchanges disponíveis no OrderBook
        # Ex: ["BINANCE", "BYBIT", "KUCOIN", "COINBASE"]
        exchanges = list(book.books.keys())

        # Compara todas contra todas (A vs B)
        for i in range(len(exchanges)):
            for j in range(len(exchanges)):
                if i == j: continue  # Não compara a mesma exchange

                ex_buy = exchanges[i]  # Onde vamos comprar (Long)
                ex_sell = exchanges[j] # Onde vamos vender (Short)

                # Pega preços
                price_buy = book.get_price(ex_buy, "ask") # Preço de compra (Ask)
                price_sell = book.get_price(ex_sell, "bid") # Preço de venda (Bid)

                if price_buy and price_sell and price_buy > 0:
                    # Calcula Spread Bruto
                    # (Venda - Compra) / Compra
                    gross_spread = (price_sell - price_buy) / price_buy

                    # Estimativa de Taxas (Futuros Taker ~0.05% + 0.06% = 0.11%)
                    # Aqui você pode ajustar para ser mais realista ou otimista
                    total_fee = 0.0011 # 0.11%

                    net_spread = gross_spread - total_fee

                    # Verifica se supera o mínimo configurado (que pode ser negativo para testes)
                    if net_spread > self.min_net_spread:
                        if net_spread > best_spread:
                            best_spread = net_spread
                            best_opportunity = {
                                "type": "arbitrage",
                                "buy_exchange": ex_buy,  # Abre Long
                                "sell_exchange": ex_sell, # Abre Short
                                "buy_price": price_buy,
                                "sell_price": price_sell,
                                "spread": gross_spread,
                                "net_spread": net_spread,
                                "qty": 0.005 # Qtd fixa para teste
                            }

        if best_opportunity:
            self.last_trade_time = time.time()
            return best_opportunity

        return None