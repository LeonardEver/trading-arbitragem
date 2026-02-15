class KillSwitch:
    def __init__(self, max_net_btc=0.001):
        self.max_net_btc = max_net_btc

    def check(self, inventory):
        if abs(inventory.net_btc()) > self.max_net_btc:
            return False
        return True
