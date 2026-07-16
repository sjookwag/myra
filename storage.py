# Save processed data to CSV files
import os
from time import strftime, localtime
from pandas import DataFrame
import technical.indicators as ftt

def save_to_csv(dfs:dict):
    os.makedirs("data", exist_ok=True)
    for symbol, df in dfs.items():
        dt:str = strftime("%m_%d %H_%M_%S", localtime())
        filename = f"data/{dt}_{symbol.replace('/', '_')}.csv"
        df.to_csv(filename, index=False)
