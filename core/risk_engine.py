class RiskEngine:
    def __init__(self, initial_capital, max_daily_loss_pct=0.03):
        self.initial_capital = initial_capital
        self.max_daily_loss = initial_capital * max_daily_loss_pct
        self.starting_equity = initial_capital

    def check(self, current_equity):
        pnl = current_equity - self.starting_equity

        if pnl <= -self.max_daily_loss:
            return False

        return True
