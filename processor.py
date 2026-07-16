# Process raw OHLCV data into pandas DataFrames
import pandas as pd
from api import send_telegram_message
from config import __TOKEN

def process_data(chat_id,raw_data_dict:dict)->dict:
    dfs = {}
    for symbol, data in raw_data_dict.items():
        if data:
            print(f"🔄 Processing data for {symbol} at process_data...")
            # send_telegram_message(__TOKEN,chat_id,f"🔄 Processing data for {symbol}...")
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['symbol'] = symbol
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            dfs[symbol] = df
            # df.set_index('timestamp', inplace=True)
    return dfs
