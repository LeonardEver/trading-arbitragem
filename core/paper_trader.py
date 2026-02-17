# core/paper_trader.py

import time
import random


class PaperTrader:
    def __init__(self, wallet, orderbook, max_fill_ratio=1.0):
        self.wallet = wallet
        self.orderbook = orderbook
        self.max_fill_ratio = max_fill_ratio

        self.maker_timeout = 0.15
        self.latency_budget_ms = {
            "BINANCE": 120,
            "BYBIT": 150,
            "COINBASE": 180
        }

        self.max_drift_ratio = 0.00015

        print("🧪 PaperTrader iniciado (maker/taker + latency + partial fill)")

    # =========================
    # ENTRY
    # =========================
    def handle_intent(self, intent):
        mode = intent.get("mode", "taker")

        if mode == "maker":
            result = self._try_maker(intent)
            return result

        return self._execute_taker(intent)

    # =========================
    # TAKER
    # =========================
    def _execute_taker(self, intent):
            # ... (código anterior de pegar preço e qty mantém igual) ...
            
            avg_price, filled_qty = self.orderbook.simulate_market_order(exchange, side, qty)

            if filled_qty <= 0: return None

            # MUDANÇA AQUI: Passamos o preço para o Inventory calcular Posição
            # Nota: self.wallet aqui deve ser referenciado ao seu Inventory atualizado
            # Se você estiver usando a classe Wallet separada, ignore, mas idealmente use o Inventory
            
            # Vamos assumir que self.wallet aqui é o objeto Inventory modificado acima:
            self.wallet.apply_trade(
                        exchange=exchange,
                        side=side,
                        price=avg_price, # <--- A ordem desses argumentos pode estar errada ou nomeada incorretamente
                        qty=filled_qty
        )

            return {
                "status": "filled",
                "mode": "taker",
                "exchange": exchange,
                "side": side, # buy=LONG, sell=SHORT
                "avg_price": avg_price,
                "filled_qty": filled_qty,
                "type": "futures_entry" # Tag para log
            }

    # =========================
    # MAKER COM PARTIAL
    # =========================
    def _try_maker(self, intent):
        exchange = intent["exchange"]
        side = intent["side"]
        price = intent["price"]
        qty = intent["qty"]

        best_bid, best_ask = self.orderbook.best(exchange)

        # proteção post-only
        if side == "buy" and price >= best_ask:
            return self._execute_taker(intent)

        if side == "sell" and price <= best_bid:
            return self._execute_taker(intent)

        # =====================
        # SIMULA FILA
        # =====================
        available_liquidity = self.orderbook.top_liquidity(exchange, side)

        if available_liquidity <= 0:
            return self._execute_taker(intent)

        # probabilidade de pegar parte da fila
        queue_factor = random.uniform(0.2, 0.8)

        maker_fill = min(qty, available_liquidity * queue_factor)

        total_filled = 0
        total_cost = 0

        # =====================
        # PARTE MAKER
        # =====================
        if maker_fill > 0:
            self.wallet.apply_trade(
                exchange=exchange,
                side=side,
                price=price,
                qty=maker_fill
            )

            total_filled += maker_fill
            total_cost += maker_fill * price

        remaining = qty - maker_fill

        # =====================
        # FALLBACK AUTOMÁTICO
        # =====================
        if remaining > 0:
            avg_price_taker, taker_fill = self.orderbook.simulate_market_order(
                exchange, side, remaining
            )

            if taker_fill > 0:
                self.wallet.apply_trade(
                    exchange=exchange,
                    side=side,
                    price=avg_price_taker,
                    qty=taker_fill
                )

                total_filled += taker_fill
                total_cost += taker_fill * avg_price_taker

        if total_filled <= 0:
            return None

        blended_price = total_cost / total_filled

        return {
            "status": "filled",
            "mode": "maker_partial",
            "exchange": exchange,
            "side": side,
            "avg_price": blended_price,
            "filled_qty": total_filled,
            "requested_qty": qty,
            "maker_component": maker_fill,
            "taker_component": total_filled - maker_fill
        }
