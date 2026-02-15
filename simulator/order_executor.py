# simulator/order_executor.py

import time
import random


class OrderExecutor:
    def __init__(self):
        """
        Executor de ordens:
        - TAKER (execução imediata)
        - MAKER (ordens pendentes com fill probabilístico avançado)
        """

        self.fees = {
            "binance": {
                "taker": 0.001,
                "maker": 0.0004
            },
            "bybit": {
                "taker": 0.001,
                "maker": 0.0004
            }
        }

        self.open_orders = []

    # =========================================================
    # ======================= TAKER ===========================
    # =========================================================

    def execute_buy(self, wallet, usd_amount, price, exchange):
        if wallet.usd < usd_amount:
            return 0.0

        fee = self.fees.get(exchange, {}).get("taker", 0.001)
        usd_after_fee = usd_amount * (1 - fee)
        btc_bought = usd_after_fee / price

        wallet.usd -= usd_amount
        wallet.btc += btc_bought

        return btc_bought

    def execute_sell(self, wallet, btc_amount, price, exchange):
        if wallet.btc < btc_amount:
            return 0.0

        fee = self.fees.get(exchange, {}).get("taker", 0.001)
        gross_usd = btc_amount * price
        usd_after_fee = gross_usd * (1 - fee)

        wallet.btc -= btc_amount
        wallet.usd += usd_after_fee

        return usd_after_fee

    # =========================================================
    # ======================= MAKER ===========================
    # =========================================================

    def place_maker_order(self, side, price, amount, exchange):
        order = {
            "side": side,                 # buy | sell
            "price": price,
            "amount": amount,             # USD (buy) ou BTC (sell)
            "exchange": exchange,
            "created_at": time.time(),
            "filled": False,
            "filled_amount": 0.0
        }

        self.open_orders.append(order)
        return order

    def try_fill_order(
        self,
        order,
        best_bid,
        best_ask,
        bid_volume,
        ask_volume
    ):
        """
        Simula fill baseado em:
        - Distância ao book
        - Liquidez do lado correto
        - Tempo na fila
        """

        if order["filled"]:
            return False

        now = time.time()
        time_alive = now - order["created_at"]

        # Define referência correta
        if order["side"] == "buy":
            reference_price = best_bid
            available_liquidity = bid_volume
        else:
            reference_price = best_ask
            available_liquidity = ask_volume

        # Distância percentual até o book
        price_distance = abs(order["price"] - reference_price) / reference_price

        # Fator distância (quanto mais perto, melhor)
        distance_factor = max(0.0, 1 - (price_distance * 80))

        # Fator liquidez (quanto mais volume, melhor)
        liquidity_factor = min(1.0, available_liquidity / (order["amount"] * 5))

        # Fator tempo (ordens antigas têm prioridade)
        time_factor = min(1.0, time_alive / 10)

        # Probabilidade final
        fill_probability = (
            0.5 * distance_factor +
            0.3 * liquidity_factor +
            0.2 * time_factor
        )

        # Piso mínimo
        fill_probability = max(0.01, min(fill_probability, 0.95))

        if random.random() > fill_probability:
            return False

        # Fill parcial ou total
        fill_ratio = random.uniform(0.25, 1.0)
        filled_amount = order["amount"] * fill_ratio

        order["filled_amount"] += filled_amount

        if order["filled_amount"] >= order["amount"] * 0.98:
            order["filled"] = True
            order["filled_amount"] = order["amount"]

        return True

    def settle_filled_order(self, wallet, order):
        fee = self.fees.get(order["exchange"], {}).get("maker", 0.0004)

        if order["side"] == "buy":
            usd_spent = order["filled_amount"]
            usd_after_fee = usd_spent * (1 - fee)
            btc_bought = usd_after_fee / order["price"]

            if wallet.usd < usd_spent:
                return False

            wallet.usd -= usd_spent
            wallet.btc += btc_bought

        else:
            btc_sold = order["filled_amount"]
            gross_usd = btc_sold * order["price"]
            usd_after_fee = gross_usd * (1 - fee)

            if wallet.btc < btc_sold:
                return False

            wallet.btc -= btc_sold
            wallet.usd += usd_after_fee

        return True

    def cleanup_filled_orders(self):
        self.open_orders = [
            o for o in self.open_orders if not o["filled"]
        ]
