# core/inventory.py

class Inventory:
    def __init__(self):
        self.usdt_balance = 1000.0
        # ADICIONADO: KUCOIN
        self.positions = {
            "BINANCE":  {"size": 0.0, "entry_price": 0.0},
            "BYBIT":    {"size": 0.0, "entry_price": 0.0},
            "COINBASE": {"size": 0.0, "entry_price": 0.0},
            "KUCOIN":   {"size": 0.0, "entry_price": 0.0},
        }

    def apply_trade(self, exchange, side, qty, price):
        exchange = exchange.upper()
        if exchange not in self.positions:
            return # Ignora exchanges desconhecidas

        current_size = self.positions[exchange]["size"]
        current_entry = self.positions[exchange]["entry_price"]
        
        # side 'buy' adiciona, 'sell' subtrai (para short)
        new_size = current_size + qty if side == "buy" else current_size - qty
        
        # Atualiza preço médio se aumentou a posição
        if abs(new_size) > abs(current_size):
            total_val = (abs(current_size) * current_entry) + (qty * price)
            # Evita divisão por zero
            if abs(new_size) > 0:
                new_entry = total_val / abs(new_size)
                self.positions[exchange]["entry_price"] = new_entry
        
        self.positions[exchange]["size"] = new_size
        
        # Taxa simulada (0.05%)
        fee = (qty * price) * 0.0005 
        self.usdt_balance -= fee

    def net_exposure(self):
        """Calcula exposição total (soma das posições)"""
        return sum(p["size"] for p in self.positions.values())

    def get_position(self, exchange):
        return self.positions.get(exchange.upper(), {"size": 0.0, "entry_price": 0.0})

    def snapshot(self):
        return {
            "USDT": self.usdt_balance,
            "POSITIONS": self.positions
        }