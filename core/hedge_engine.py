class HedgeEngine:
    def __init__(self, inventory, orderbook, max_net_btc=0.0002):
        self.inventory = inventory
        self.orderbook = orderbook
        self.max_net_btc = max_net_btc

# Em core/hedge_engine.py

    def evaluate(self):
        # MUDANÇA AQUI: De net_btc() para net_exposure()
        net_exposure = self.inventory.net_exposure()

        # Se a exposição for pequena (neutra), não faz nada
        if abs(net_exposure) <= self.max_net_btc:
            return None

        # Se estamos expostos, precisamos fazer o contrário para zerar
        # Se net > 0 (estamos comprados), precisamos VENDER (Shortar)
        side = "sell" if net_exposure > 0 else "buy"
        
        # Escolhe a exchange mais líquida para desovar o risco (ex: Binance)
        exchange = "BINANCE"
        
        # Pega o preço para a ordem
        price = self.orderbook.get_price(exchange, "bid" if side == "sell" else "ask")

        if price is None:
            return None

        return {
            "type": "hedge",
            "exchange": exchange,
            "side": side,
            "price": price,
            "qty": abs(net_exposure) # Zera a exposição
        }