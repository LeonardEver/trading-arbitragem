# # simulator/wallet.py
# class Wallet:
#     def __init__(self, initial_usd: float = 100.0):
#         self.usd = initial_usd
#         self.btc = 0.0

#     def buy_btc(self, usd_amount: float, price: float):
#         if usd_amount > self.usd:
#             raise Exception("Saldo USD insuficiente")

#         btc_bought = usd_amount / price
#         self.usd -= usd_amount
#         self.btc += btc_bought
#         return btc_bought

#     def sell_btc(self, btc_amount: float, price: float):
#         if btc_amount > self.btc:
#             raise Exception("Saldo BTC insuficiente")

#         usd_received = btc_amount * price
#         self.btc -= btc_amount
#         self.usd += usd_received
#         return usd_received

#     def snapshot(self):
#         return {
#             "usd": round(self.usd, 2),
#             "btc": round(self.btc, 8)
#         }


####################################################

class Wallet:
    def __init__(self, initial_usd=50.0):
        self.balances = {
            "BINANCE": {"USD": initial_usd, "BTC": 0.0},
            "BYBIT": {"USD": 0.0, "BTC": 0.0},
            "COINBASE": {"USD": 0.0, "BTC": 0.0},
        }

    def apply_trade(self, exchange, side, price, qty):
        if side == "buy":
            self.balances[exchange]["USD"] -= price * qty
            self.balances[exchange]["BTC"] += qty
        else:
            self.balances[exchange]["USD"] += price * qty
            self.balances[exchange]["BTC"] -= qty

    def snapshot(self):
        return self.balances
