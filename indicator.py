import pandas as pd
import logging
import talib
from backtesting import Backtest,Strategy

LOG_FILENAME = "logfile.log"
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)


class Market(Strategy):
    def init(self):
        self.ticker = 'APPL'

    def step_act(self,action): 
        if action == 1:
            self.buy(size=.1)
            for i in self.trades:
                if i.is_short:
                    i.close()
                          
        elif action == 2:
            self.sell(size=.1)
            for i in self.trades:
                if i.is_long:
                    i.close()
                    

    def next(self):
        # self.data.index[-1]
        action = 0
        if self.data['5'] > self.data['15']:
            action = 1
        elif self.data['15'] > self.data['5']:
            action = 2
        
        self.step_act(action)
        if action !=0 and len(self.closed_trades) > 1:
            i =  list(self.closed_trades)[-1]
            if i.is_long:
                t = 'UP'
            else:
                t = 'Down'
            s = f"Ticker {self.ticker}, Size {i.size}, Market Value Bought {i.entry_price}, Market Value Sold {i.exit_bar} Enter Time {i.entry_time} Sell Time {i.exit_time} Trande {t} Profit {i.pl}"
            print(s)
            logging.info(s)  
       
                
        
    


data = pd.read_csv('AAPL.csv')
data['5'] = talib.SMA(data.Close, timeperiod=5)
data['15'] = talib.SMA(data.Close, timeperiod=15)
data.dropna(inplace=True)
data['Gmt time'] = pd.to_datetime(data['Gmt time'])
data.set_index('Gmt time',inplace=True)


bt = Backtest(data, Market, commission=.0002, margin=.05)
print(bt.run())


bt.plot()