class StrategyResult:

    def __init__(self, strategy, symbol, trade_results=None):
        self.strategy = strategy
        self.symbol = symbol
        if trade_results is None:
            self.trade_results = []
        else:
            self.trade_results = trade_results

    def get_ROI(self):
        initial_balance = self.trade_results[0]['balance']
        net_profit = self.trade_results[len(self.trade_results)]['net_profit']
        roi = net_profit*100/initial_balance
        timespan =self.trade_results[len(self.trade_results)]['timestamp']\
                  - self.trade_results[0]['timestamp']
        return roi, f"{roi}% in {timespan}"