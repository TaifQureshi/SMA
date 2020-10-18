import logging
import talib
import pandas as pd
from kiteconnect import KiteConnect
import datetime


LOG_FILENAME = "logfile.log"
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)


#Connect to api
kite = KiteConnect(api_key="your_api_key")
instrument_token = 'enter tocken'
data = kite.generate_session("request_token_here", api_secret="your_secret")
kite.set_access_token(data["access_token"])
buy_order = []
sell_order = []
done = False
# Main loop
while not done:
    #Get the data
    h_data = kite.historical_data(instrument_token, from_date=datetime.datetime.now() - datetime.timedelta(minutes=30), to_date=datetime.datetime.now(), interval=minute, continuous=False, oi=False)
    # Calaculate SMA
    h_data['5'] = talib.SMA(h_data.close, timeperiod=5)
    h_data['15'] = talib.SMA(h_data.close, timeperiod=15)

    #Slice to get only current data
    h_data = h_data.iloc[-1]

    action = 0
    if h_data['5'] > h_data['15']:
        try:
            #Place Buy Order
            order_id = kite.place_order(tradingsymbol="INFY",
                                        exchange=kite.EXCHANGE_NSE,
                                        transaction_type='BUY',
                                        quantity=1,
                                        order_type=kite.ORDER_TYPE_MARKET,
                                        product=kite.PRODUCT_NRML)

            logging.info("Order placed. ID is: {}".format(order_id))
            buy_order.append(order_id)

            #Close Sell Orde
            ko=kite.orders()
            ko=pd.DataFrame(ko)
            OID=[]
            for i in range(len(ko)):
                if ko['order_id'].iloc[i] in sell_order:
                    OID.append((ko['order_id'].iloc[i].values,ko['parent_order_id'].iloc[i].values))
                    sell_order.remove(ko['order_id'].iloc[i].values)
            for i,j in OID:
                kite.order_cancel(order_id=i,parent_order_id=j)

        except Exception as e:
            logging.info("Order placement failed: {}".format(e.message))
    elif h_data['15'] > h_data['5']:
        try:
            #Place Sell Order
            order_id = kite.place_order(tradingsymbol=instrument_token,
                                        exchange=kite.EXCHANGE_NSE,
                                        transaction_type='SELL',
                                        quantity=1,
                                        order_type=kite.ORDER_TYPE_MARKET,
                                        product=kite.PRODUCT_NRML)

            logging.info("Order placed. ID is: {}".format(order_id))
            sell_order.append(order_id)

            #Closing Buy order
            ko=kite.orders()
            ko=pd.DataFrame(ko)
            OID=[]
            for i in range(len(ko)):
                if ko['order_id'].iloc[i] in buy_order:
                    OID.append((ko['order_id'].iloc[i].values,ko['parent_order_id'].iloc[i].values))
                    buy_order.remove(ko['order_id'].iloc[i].values)
            for i,j in OID:
                kite.order_cancel(order_id=i,parent_order_id=j)
        except Exception as e:
            logging.info("Order placement failed: {}".format(e.message))

    