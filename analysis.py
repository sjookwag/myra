from pandas import DataFrame
from config import __TOKEN, INDI
from api import send_telegram_message,send_message_md2
from plot import plot_swings,plot_signals_by_volatility,plot_signals_by_momentum,plot_signals_by_trend,plot_signals_by_volume
from prettytable import PrettyTable
import numpy as np
import pandas as pd

# Function to detect price swings using dynamic threshold from a DataFrame
def get_price_swings(chat_id,df: pd.DataFrame, thresholds: pd.Series) -> tuple[list[int], list[int]]:
    try:
        prices = df['close'].values
        last_swing = None  # 1 for upswing, -1 for downswing
        high_swings = [0]
        low_swings = [0]
        last_price = prices[0]

        for i, price in enumerate(prices):
            threshold = thresholds.iloc[i]
            if len(high_swings) == 1 and price >= prices[high_swings[-1]]:
                high_swings[0] = i
                last_swing = 1
            elif len(low_swings) == 1 and price <= prices[low_swings[-1]]:
                low_swings[0] = i
                last_swing = -1
            elif price - threshold > prices[low_swings[-1]] and price > last_price:
                if last_swing == 1:
                    if price > prices[high_swings[-1]]:
                        high_swings[-1] = i
                else:
                    high_swings.append(i)
                last_swing = 1
            elif price + threshold < prices[high_swings[-1]] and price < last_price:
                if last_swing == -1:
                    if price < prices[low_swings[-1]]:
                        low_swings[-1] = i
                else:
                    low_swings.append(i)
                last_swing = -1
            last_price = price
        last_period = len(prices) - 1
        if high_swings[-1] > low_swings[-1] and high_swings[-1] < last_period:
            low_swings.append(last_period)
        elif low_swings[-1] > high_swings[-1] and low_swings[-1] < last_period:
            high_swings.append(last_period)
        return high_swings, low_swings
    except Exception as e:
        print(f"❌ Error in get_price_swings: {e}")
        send_telegram_message(__TOKEN,chat_id,f"❌ Error in get_price_swings: {e}")
        return [], []

def prices_swings(chat_id,symbol:str,df: pd.DataFrame):
    # Compute rolling volatility and dynamic threshold
    volatility = df['close'].rolling(window=10).std().bfill()  # backfill NaNs
    multiplier = 1.5
    thresholds = multiplier * volatility
    # Detect swings
    high_swings, low_swings = get_price_swings(chat_id,df, thresholds)
    plot_swings(chat_id,symbol,df,high_swings,low_swings,f'resource/{symbol.replace("/","_")}_swings.png')

def highs_lows(chat_id,symbol:str,df:DataFrame,ohlc:str='ohlc')->None:
    if ohlc=='hksi':
        high_prices = df['ha_high']
        low_prices = df['ha_low']
        close_prices = df['ha_close']
    else:
        high_prices = df['high']
        low_prices = df['low']
        close_prices = df['close']
    volume = df['volume']
    # Calculate higher highs and lower lows
    df['HH'] = np.where(high_prices > high_prices.shift(1), True, False)  # 이전 고가보다 현재 고가가 높음
    df['LL'] = np.where(low_prices < low_prices.shift(1), True, False)    # 이전 저가보다 현재 저가가 낮음
    df['LH'] = np.where(high_prices < high_prices.shift(1), True, False)  # 이전 고가보다 현재 고가가 낮음
    df['HL'] = np.where(low_prices > low_prices.shift(1), True, False)    # 이전 저가보다 현재 저가가 높음

    print(df[['timestamp','close','HH','LL','LH','HL']].tail())
    send_telegram_message(__TOKEN,chat_id,f"Higher Highs/Lower Lows and Lower Highs/Higher Lows calculated:\n{df[['timestamp','close','HH','LL','LH','HL']].tail().to_string()}")

def trends_analysis(chat_id,symbol:str,df:DataFrame)->None:
    # --- Detect Trends/Signals Based on Indicators ---
    try:
        if df is not None and not df.empty:
            # --- A. Moving Average Crossover Trend ---
            # 1 = Uptrend, -1 = Downtrend, 0 = No clear trend / flat
            df['MA_Trend'] = 0
            # Uptrend: Fast MA crosses above Slow MA
            df.loc[(df['ema10'] > df['ema50']) & (df['ema10'].shift(1) <= df['ema50'].shift(1)), 'MA_Trend'] = 1
            # Downtrend: Fast MA crosses below Slow MA
            df.loc[(df['ema10'] < df['ema50']) & (df['ema10'].shift(1) >= df['ema50'].shift(1)), 'MA_Trend'] = -1
            # Handle the case where there are no crosses, or NaNs
            # when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value)
            df['MA_Trend'] = df['MA_Trend'].ffill() # Fill forward, assuming trend persists
            df['MA_Trend'] = df['MA_Trend'].fillna(0) # Fill initial NaNs with 0

            # --- B. MACD Zero-Line Cross Trend ---
            df['MACD_Trend'] = 0
            # Uptrend: MACD crosses above zero
            df.loc[(df['macd'] > 0) & (df['macd'].shift(1) <= 0), 'MACD_Trend'] = 1
            # Downtrend: MACD crosses below zero
            df.loc[(df['macd'] < 0) & (df['macd'].shift(1) >= 0), 'MACD_Trend'] = -1

            df['MACD_Trend'] = df['MACD_Trend'].ffill()
            df['MACD_Trend'] = df['MACD_Trend'].fillna(0)

            # --- C. RSI Overbought/Oversold ---
            # 1 = Overbought, -1 = Oversold, 0 = Neutral
            df['RSI_State'] = 0
            df.loc[df['rsi'] > 70, 'RSI_State'] = 1 # Overbought
            df.loc[df['rsi'] < 30, 'RSI_State'] = -1 # Oversold

            # --- D. ADX Trend Strength ---
            # 1 = Trending, 0 = Non-trending (using a threshold, e.g., 25)
            adx_threshold = 25
            df['ADX_Strength'] = 0
            df.loc[df['adx'] > adx_threshold, 'ADX_Strength'] = 1 # Trending

            state_key = PrettyTable()
            state_key.align = "l"  # Align all columns to the left
            state_key.border = True
            state_key.header = True
            state_key.field_names = ["Value","MA",      "MACD","RSI",       "ADX Trend"]
            state_key.add_row(      ["1",    "Up",      "Up",  "Overbought","Trend"])
            state_key.add_row(      ["0",    "No",      "No",  "Neutral",   "No"])
            state_key.add_row(      ["-1",   "Down",    "Down","Oversold",  "N/A"])
            state_key_str = f"```\n{state_key.get_string()}\n```"
            send_message_md2(__TOKEN,chat_id,f"📊 Trend/Signal Key:\n{state_key_str}")
            # --- 4. Display the results ---
            print(df[['MA_Trend','MACD_Trend','RSI_State','ADX_Strength']].tail())
            # msg:str = "Trends/Signals calculated:\n"
            # msg+="- MA/MACD Crossover Trend -\n1 = Uptrend, -1 = Downtrend, 0 = No clear trend / flat\n"
            # msg+="- RSI Overbought/Oversold -\n1 = Overbought, -1 = Oversold, 0 = Neutral\n"
            # msg+="- ADX Trend Strength -\n1 = Trending, 0 = Non-trending\n"
            # msg+=f"{df[['timestamp','MA_Trend', 'MACD_Trend', 'RSI_State', 'ADX_Strength']].tail().to_string()}"
            # send_telegram_message(__TOKEN,chat_id,msg)
            return df

    except Exception as e:
        print(f"❌ Error in trends_analysis: {e}")
        send_telegram_message(__TOKEN,chat_id,f"❌ Error in trends_analysis: {e}")
        return None

def basic_analysis(chat_id,symbol:str,df:DataFrame)->None:
    '''
    Perform technical analysis on the given DataFrame and send results via Telegram.

    Parameters:
    - chat_id (int): Telegram chat ID to send messages to.
    - symbol (str): Trading symbol (e.g., 'BTC/USD').
    - df (DataFrame): DataFrame containing OHLCV data with columns ['timestamp', 'open', 'high', 'low', 'close', 'volume'].

    Returns:
    - None
    '''
    try:
        if df is not None and not df.empty:
            summary_indicators:dict = {}
            print(f'{symbol} Analysis start')
            # Ensure the DataFrame is sorted by timestamp
            # df = df.sort_values(by='timestamp').reset_index(drop=True)
            # Calculate technical indicators based on the INDI configuration
            print(df.tail(2).to_string())

            if INDI['adl']:
                print(f'{symbol} ADL in Analysis')
                if df['adl'].iloc[-1]>0:
                    summary_indicators['adl'] = f'buying_pressure'
                elif df['adl'].iloc[-1]<0:
                    summary_indicators['adl'] = f'selling_pressure'
            if INDI['aroon']:
                print(f'{symbol} AROON in Analysis')
                if df['aroon_up'].iloc[-1] > df['aroon_down'].iloc[-1]:
                    summary_indicators['aroon'] = f'bullish'
                elif df['aroon_up'].iloc[-1] < df['aroon_down'].iloc[-1]:
                    summary_indicators['aroon'] = f'bearish'
            if INDI['apo']:
                print(f'{symbol} APO in Analysis')
                if df['apo'].iloc[-1]>0:
                    summary_indicators['apo'] = f'bullish'
                elif df['apo'].iloc[-1]<0:
                    summary_indicators['apo'] = f'bearish'
            if INDI['atr']:
                print(f'{symbol} ATR in Analysis')
                if df['atr'].iloc[-1]>0.05:
                    summary_indicators['atr'] = f'high_volatility'
                elif df['atr'].iloc[-1]<0.02:
                    summary_indicators['atr'] = f'low_volatility'
            if INDI['bb']:
                print(f'{symbol} BBANDS in Analysis')
                if df['close'].iloc[-1] > df['bb_upper'].iloc[-1]:
                    summary_indicators['bbands'] = f'overbought'
                elif df['close'].iloc[-1] < df['bb_lower'].iloc[-1]:
                    summary_indicators['bbands'] = f'oversold'
            if INDI['cci']:
                print(f'{symbol} CCI in Analysis')
                if df['cci'].iloc[-1]>100:
                    summary_indicators['cci'] = f'overbought'
                elif df['cci'].iloc[-1]<-100:
                    summary_indicators['cci'] = f'oversold'
            if INDI['cmf']:
                print(f'{symbol} CMF in Analysis')
                if df['cmf'].iloc[-1]>0:
                    summary_indicators['cmf'] = f'buying_pressure'
                elif df['cmf'].iloc[-1]<0:
                    summary_indicators['cmf'] = f'selling_pressure'
            if INDI['cmo']:
                print(f'{symbol} CMO in Analysis')
                if df['cmo'].iloc[-1]>50:
                    summary_indicators['cmo'] = f'overbought'
                elif df['cmo'].iloc[-1]<-50:
                    summary_indicators['cmo'] = f'oversold'
            if INDI['co']:
                print(f'{symbol} Chaikin Oscillator in Analysis')
                if df['co'].iloc[-1]>0:
                    summary_indicators['co'] = f'bullish'
                elif df['co'].iloc[-1]<0:
                    summary_indicators['co'] = f'bearish'
            if INDI['di']:
                print(f'{symbol} Disparity Index in Analysis')
                if df['di'].iloc[-1]>0:
                    summary_indicators['di'] = f'bullish'
                elif df['di'].iloc[-1]<0:
                    summary_indicators['di'] = f'bearish'
            # if INDI['dmdi']:
            #     print(f'{symbol} DMI in Analysis')
            #     if df['plus_di'].iloc[-1] > df['minus_di'].iloc[-1] and df['adx'].iloc[-1] > 25:
            #         summary_indicators['dmi'] = f'bullish'
            #     elif df['plus_di'].iloc[-1] < df['minus_di'].iloc[-1] and df['adx'].iloc[-1] > 25:
            #         summary_indicators['dmi'] = f'bearish'
            # if INDI['dpo']:
            #     print(f'{symbol} DPO in Analysis')
            #     if df['dpo'].iloc[-1]>0:
            #         summary_indicators['dpo'] = 'bullish'
            #     elif df['dpo'].iloc[-1]<0:
            #         summary_indicators['dpo'] = 'bearish'
            if INDI['ema']:
                print(f'{symbol} EMA in Analysis')
                # Identify golden cross and dead cross signals
                golden_cross = (df['ema5'] > df['ema50']) & (df['ema5'].shift(1) <= df['ema50'].shift(1))
                dead_cross = (df['ema5'] < df['ema50']) & (df['ema5'].shift(1) >= df['ema50'].shift(1))
                if golden_cross.iloc[-1]:
                    summary_indicators['ema'] = f'golden_cross'
                elif dead_cross.iloc[-1]:
                    summary_indicators['ema'] = f'dead_cross'
            if INDI['ht_sine']:
                print(f'{symbol} HT_SINE in Analysis')
                if df['htsine'].iloc[-1] > df['htleadsine'].iloc[-1]:
                    summary_indicators['ht_sine'] = f'bullish'
                elif df['htsine'].iloc[-1] < df['htleadsine'].iloc[-1]:
                    summary_indicators['ht_sine'] = f'bearish'
            # if INDI['klinger']:
            #     print(f'{symbol} KLINGER in Analysis')
            #     if df['klinger'].iloc[-1]>0:
            #         summary_indicators['klinger'] = 'bullish'
            #     elif df['klinger'].iloc[-1]<0:
            #         summary_indicators['klinger'] = 'bearish'
            # if INDI['lrsi']:
            #     print(f'{symbol} LRSI in Analysis')
            #     if df['lrsi'].iloc[-1]>0:
            #         summary_indicators['lrsi'] = f'bullish'
            #     elif df['lrsi'].iloc[-1]<0:
            #         summary_indicators['lrsi'] = f'bearish'
            if INDI['macd']:
                print(f'{symbol} MACD in Analysis')
                if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1] and df['macd_hist'].iloc[-1] > 0:
                    summary_indicators['macd'] = f'bullish'
                elif df['macd'].iloc[-1] < df['macd_signal'].iloc[-1] and df['macd_hist'].iloc[-1] < 0:
                    summary_indicators['macd'] = f'bearish'
            if INDI['mfi']:
                print(f'{symbol} MFI in Analysis')
                if df['mfi'].iloc[-1]>80:
                    summary_indicators['mfi'] = f'overbought'
                elif df['mfi'].iloc[-1]<20:
                    summary_indicators['mfi'] = f'oversold'
            if INDI['mom']:
                print(f'{symbol} MOM in Analysis')
                if df['mom'].iloc[-1]>0:
                    summary_indicators['mom'] = f'bullish'
                elif df['mom'].iloc[-1]<0:
                    summary_indicators['mom'] = f'bearish'
            if INDI['natr']:
                print(f'{symbol} NATR in Analysis')
                if df['natr'].iloc[-1]>0.05:
                    summary_indicators['natr'] = f'high_volatility'
                elif df['natr'].iloc[-1]<0.02:
                    summary_indicators['natr'] = f'low_volatility'
            if INDI['obv']:
                print(f'{symbol} OBV in Analysis')
                if df['obv'].iloc[-1]>0:
                    summary_indicators['obv'] = f'buying_pressure'
                elif df['obv'].iloc[-1]<0:
                    summary_indicators['obv'] = f'selling_pressure'
            if INDI['ppo']:
                print(f'{symbol} PPO in Analysis')
                if df['ppo'].iloc[-1]>0:
                    summary_indicators['ppo'] = f'bullish'
                elif df['ppo'].iloc[-1]<0:
                    summary_indicators['ppo'] = f'bearish'
            if INDI['rsi']:
                print(f'{symbol} RSI in Analysis')
                if df['rsi'].iloc[-1]>70:
                    summary_indicators['rsi'] = f'overbought'
                elif df['rsi'].iloc[-1]<30:
                    summary_indicators['rsi'] = f'oversold'
            if INDI['composite_rsi']:
                print(f'{symbol} Composite RSI in Analysis')
                if df['composite_rsi'].iloc[-1]>70:
                    summary_indicators['composite_rsi'] = f'overbought'
                elif df['composite_rsi'].iloc[-1]<30:
                    summary_indicators['composite_rsi'] = f'oversold'
            if INDI['sar']:
                print(f'{symbol} SAR in Analysis')
                if df['close'].iloc[-1] > df['sar'].iloc[-1]:
                    summary_indicators['sar'] = f'bullish'
                elif df['close'].iloc[-1] < df['sar'].iloc[-1]:
                    summary_indicators['sar'] = f'bearish'
            if INDI['sma']:
                print(f'{symbol} SMA in Analysis')
                if 'smaFast' not in df.columns and 'smaSlow' not in df.columns:
                    if df['smaSlow'].iloc[-1] > df['smaFast'].iloc[-1]:
                        summary_indicators['sma'] = f'bearish'
                    elif df['smaSlow'].iloc[-1] < df['smaFast'].iloc[-1]:
                        summary_indicators['sma'] = f'bullish'
            if INDI['stoch']:
                print(f'{symbol} STOCH in Analysis')
                if df['slowk'].iloc[-1]>80 and df['slowd'].iloc[-1]>80:
                    summary_indicators['stoch'] = f'overbought'
                elif df['slowk'].iloc[-1]<20 and df['slowd'].iloc[-1]<20:
                    summary_indicators['stoch'] = f'oversold'
            if INDI['stochf']:
                print(f'{symbol} STOCHF in Analysis')
                if df['fastk'].iloc[-1]>80 and df['fastd'].iloc[-1]>80:
                    summary_indicators['stochf'] = f'overbought'
                elif df['fastk'].iloc[-1]<20 and df['fastd'].iloc[-1]<20:
                    summary_indicators['stochf'] = f'oversold'
            if INDI['tema']:
                print(f'{symbol} TEMA in Analysis')
                if df['tema9'].iloc[-1] > df['tema21'].iloc[-1]:
                    summary_indicators['tema'] = f'bullish'
                elif df['tema9'].iloc[-1] < df['tema21'].iloc[-1]:
                    summary_indicators['tema'] = f'bearish'
            if INDI['trix']:
                print(f'{symbol} TRIX in Analysis')
                if df['trix'].iloc[-1]>0:
                    summary_indicators['trix'] = f'bullish'
                elif df['trix'].iloc[-1]<0:
                    summary_indicators['trix'] = f'bearish'
            if INDI['vwap']:
                print(f'{symbol} VWAP in Analysis')
                if df['close'].iloc[-1] > df['vwap_upper'].iloc[-1]:
                    summary_indicators['vwap'] = f'overbought'
                elif df['close'].iloc[-1] < df['vwap_lower'].iloc[-1]:
                    summary_indicators['vwap'] = f'oversold'
            if INDI['williams']:
                print(f'{symbol} WILLIAMS %R in Analysis')
                if df['williams'].iloc[-1]>-20:
                    summary_indicators['williams'] = f'overbought'
                elif df['williams'].iloc[-1]<-80:
                    summary_indicators['williams'] = f'oversold'
            if summary_indicators:
                bull_bear_map:dict = {
                    "bullish": "🐂Bullish",
                    "bearish": "🐻Bearish" # Assuming 'bearish' is the only other possible value
                }
                volatility_map:dict = {
                    "high_volatility": "🔥High volatility",
                    "low_volatility": "❄️Low volatility" # Assuming 'low_volatility' is the only other possible value
                }
                pressure_map:dict = {
                    "buying_pressure": "📈Buying pressure",
                    "selling_pressure": "📉Selling pressure" # Assuming 'selling_pressure' is the only other possible value
                }
                over_map:dict = {
                    "overbought": "🚀Overbought",
                    "oversold": "🌕Oversold" # Assuming 'oversold' is the only other possible value
                }
                tableBullBear = PrettyTable()
                tableVolatility = PrettyTable()
                tablePressure = PrettyTable()
                tableOverboughtOversold = PrettyTable()
                for table in [tableBullBear, tableVolatility, tablePressure, tableOverboughtOversold]:
                    table.align = "l"  # Align all columns to the left
                    table.border = True
                    table.header = True
                    table.field_names = ["Indicator", "Value"]

                for key, value in summary_indicators.items():
                    if key in ['aroon','apo','co','di','dmi','ht_sine','lrsi','macd','mom','ppo','sar','tema','trix']:
                        emoji = bull_bear_map.get(value, "") # Default to empty if value isn't
                        tableBullBear.add_row([f"{key.upper()}", emoji])
                    if key in ['atr','natr']:
                        emoji = volatility_map.get(value, "") # Default to empty if value isn't
                        tableVolatility.add_row([f"{key.upper()}", emoji])
                    if key in ['adl','cmf','obv']:
                        emoji = pressure_map.get(value, "") # Default to empty if value isn't
                        tablePressure.add_row([f"{key.upper()}",emoji])
                    if key in ['cci','rsi','stoch','stochf','williams','composite_rsi']:
                        emoji = over_map.get(value, "") # Default to empty if value isn't
                        tableOverboughtOversold.add_row([f"{key.upper()}",emoji])

                analysis_message:str = f"📊 Technical Analysis for {symbol}:\n"
                analysis_message += f"```\n{tableBullBear.get_string()}\n```"
                analysis_message += f"```\n{tableVolatility.get_string()}\n```"
                analysis_message += f"```\n{tablePressure.get_string()}\n```"
                analysis_message += f"```\n{tableOverboughtOversold.get_string()}\n```"
                # send_telegram_message(__TOKEN,chat_id,analysis_message)
                # send_message_md2(__TOKEN,chat_id,analysis_message)
                print(analysis_message)
                print(f'{symbol} Analysis end')
                return analysis_message

    except Exception as e:
        print(f"❌ Error in analysis for {symbol}: {e}")
        return f"❌ Error in analysis for {symbol}: {e}"
        # send_telegram_message(__TOKEN,chat_id,f"❌ Error in analysis for {symbol}: {e}")

def signal_by_trend(chat_id,symbol:str,df:DataFrame)->None:
    try:
        # Define ADX threshold
        adx_threshold = 25
        # Generate signals
        df['signal_trend'] = 0
        # Buy signal: ema10 crosses above ema50 AND ADX is trending strong
        df.loc[(df['ema10'] > df['ema50']) & (df['ema10'].shift(1) <= df['ema50'].shift(1)) & (df['adx'] > adx_threshold), 'signal_trend'] = 1
        # Sell signal: ema10 crosses below ema50 AND ADX is trending strong
        df.loc[(df['ema10'] < df['ema50']) & (df['ema10'].shift(1) >= df['ema50'].shift(1)) & (df['adx'] > adx_threshold), 'signal_trend'] = -1
        # Handle the case where there are no crosses, or NaNs
        # when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value)
        df['signal_trend'] = df['signal_trend'].ffill() # Fill forward, assuming trend persists
        df['signal_trend'] = df['signal_trend'].fillna(0) # Fill initial NaNs with 0
        plot_signals_by_trend(chat_id,symbol,df,f'resource/{symbol.replace("/","_")}_trend_signals.png')
    except Exception as e:
        print(f"❌ Error in signal_by_trend: {e}")
        send_telegram_message(__TOKEN,chat_id,f"❌ Error in signal_by_trend: {e}")

def signal_by_momentum(chat_id,symbol:str,df:DataFrame)->None:
    df['signal_momentum'] = 0
    df.loc[(df['rsi'] < 30) & (df['fastk'] < 20) & (df['cci'] < -100), 'signal_momentum'] = 1
    df.loc[(df['rsi'] > 70) & (df['fastk'] > 80) & (df['cci'] > 100), 'signal_momentum'] = -1
    df['signal_momentum'] = df['signal_momentum'].ffill() # Fill forward, assuming trend persists
    df['signal_momentum'] = df['signal_momentum'].fillna(0) # Fill initial NaNs with 0
    plot_signals_by_momentum(chat_id,symbol,df,f'resource/{symbol.replace("/","_")}_momentum_signals.png')

def signal_by_volatility(chat_id,symbol:str,df:DataFrame)->None:
    try:
        # Signal logic
        def generate_signals(row):
            if row['close'] < row['bb_lower'] and row['close'] < row['keltner_lower'] and row['price_change'] > row['atr'] * 1.5:
                return 1
            elif row['close'] > row['bb_upper'] and row['close'] > row['keltner_upper'] and row['price_change'] > row['atr'] * 1.5:
                return -1
            else:
                return 0
        df['price_change'] = df['close'].diff().abs()
        df['signal_vol'] = df.apply(generate_signals, axis=1)
        plot_signals_by_volatility(chat_id,symbol,df,f'resource/{symbol.replace("/","_")}_volatility_signals.png')
        # send_telegram_message(__TOKEN,chat_id,f"Volatility-Based Signals calculated:\n{df[['close','bb_lower','bb_upper','keltner_lower','keltner_upper','atr','price_change','signal_vol']].tail().to_string()}")
    except Exception as e:
        print(f"❌ Error in signal_by_volatility: {e}")
        send_telegram_message(__TOKEN,chat_id,f"❌ Error in signal_by_volatility: {e}")

def signal_by_volume(chat_id,symbol:str,df:DataFrame)->None:
    df['signal_volume'] = 0
    df.loc[(df['obv'].diff() > 0) & (df['adl'].diff() > 0) & (df['cmf'] > 0), 'signal_volume'] = 1
    df.loc[(df['obv'].diff() < 0) & (df['adl'].diff() < 0) & (df['cmf'] < 0), 'signal_volume'] = -1
    df['signal_volume'] = df['signal_volume'].ffill() # Fill forward, assuming trend persists
    df['signal_volume'] = df['signal_volume'].fillna(0) # Fill initial NaNs with 0
    plot_signals_by_volume(chat_id,symbol,df,f'resource/{symbol.replace("/","_")}_volume_signals.png')

def Trend_Momentum(chat_id,symbol:str,df:DataFrame)->None:
    pass
def Trend_Volume(chat_id,symbol:str,df:DataFrame)->None:
    pass
def Momentum_Volatility(chat_id,symbol:str,df:DataFrame)->None:
    pass
def Triple_Combo(chat_id,symbol:str,df:DataFrame)->None:
    pass
