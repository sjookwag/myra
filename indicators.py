from time import strftime, localtime
from pandas import DataFrame
import pandas as pd
import talib as ta
from config import INDI,__TOKEN
from api import send_telegram_message
from plot import plot_ohlcv,plot_trend

def indicators(chat_id,dfs:dict,ohlc:str='ohlc')->DataFrame:
    print("🔄 Calculating indicators...")
    # send_telegram_message(__TOKEN,chat_id,f"🔄 Calculating indicators with {ohlc} data...")

    for symbol, df in dfs.items():
        dt:str = strftime("%m-%d %H:%M:%S", localtime())
        df = dfs[symbol]
        print(f'{dt} {symbol} indicators calculation start...')
        # send_telegram_message(__TOKEN,chat_id,f'{dt} {symbol} indicators calculation start...')
        # send_telegram_message(__TOKEN,chat_id,f"DataFrame columns:\n{df.tail(20).to_string()}")
        print(df.tail(2))
        if ohlc=='hksi':
            print('Heikin Ashi applied')
            df = add_heikin_ashi(df)
            high_prices = df['ha_high']
            low_prices = df['ha_low']
            close_prices = df['ha_close']
        else:
            print('Standard OHLC applied')
            high_prices = df['high']
            low_prices = df['low']
            close_prices = df['close']
        volume = df['volume']

        if INDI['adl']:
            print(f'{dt} {symbol} ADL(Accumulation/Distribution Line)')
            adl = ta.AD(high_prices, low_prices, close_prices, volume)
            if adl.empty:
                print(f"❌ ADL calculation returned empty result for {symbol}.")
            else:
                df['adl'] = adl
            # send_telegram_message(__TOKEN,chat_id,f"Accumulation/Distribution Line(ADL) calculated:\n{df['adl'].tail(2).to_string()}")
        if INDI['adx']:
            print(f'{dt} {symbol} ADX')
            # 3개를 한 번에 받지 않고 각각 따로 호출합니다.
            df['di_plus'] = ta.PLUS_DI(high_prices, low_prices, close_prices, timeperiod=14)
            df['di_minus'] = ta.MINUS_DI(high_prices, low_prices, close_prices, timeperiod=14)
            df['adx'] = ta.ADX(high_prices, low_prices, close_prices, timeperiod=14)
            # send_telegram_message(__TOKEN,chat_id,f"ADX calculated:\n{df['adx'].tail(2).to_string()}")
        if INDI['apo']:
            print(f'{dt} {symbol} APO (Absolute Price Oscillator)')
            fastperiod=12
            slowperiod=26
            fast_ema = close_prices.ewm(span=fastperiod, adjust=False).mean()
            slow_ema = close_prices.ewm(span=slowperiod, adjust=False).mean()
            fema_sema = fast_ema - slow_ema
            df['apo'] = fema_sema
            # send_telegram_message(__TOKEN,chat_id,f"APO calculated:\n{df['apo'].tail(2).to_string()}")
        if INDI['aroon']:
            print(f'{dt} {symbol} AROON')
            # 반환되는 순서가 down, up 순서임에 주의하세요!
            aroon_down, aroon_up = ta.AROON(high_prices, low_prices, timeperiod=14)
            df['aroon_up'] = aroon_up
            df['aroon_down'] = aroon_down
            # send_telegram_message(__TOKEN,chat_id,f"AROON calculated:\n{df[['aroon_up','aroon_down']].tail(2).to_string()}")
        if INDI['atr']:
            print(f'{dt} {symbol} ATR')
            df['atr'] = ta.ATR(high_prices, low_prices, close_prices, timeperiod=14)
            # send_telegram_message(__TOKEN,chat_id,f"ATR calculated:\n{df['atr'].tail(2).to_string()}")
        if INDI['bb']:
            print(f'{dt} {symbol} BBANDS')
            upper, middle, lower = ta.BBANDS(close_prices, timeperiod=20)
            df['bb_upper'] = upper
            df['bb_middle'] = middle
            df['bb_lower'] = lower
            # send_telegram_message(__TOKEN,chat_id,f"Bollinger Bands calculated:\n{df[['bb_upper','bb_middle','bb_lower']].tail(2).to_string()}")
        if INDI['cci']:
            print(f'{dt} {symbol} CCI (Commodity Channel Index)')
            df['cci'] = ta.CCI(high_prices, low_prices, close_prices, timeperiod=14)
            # send_telegram_message(__TOKEN,chat_id,f"CCI calculated:\n{df['cci'].tail(2).to_string()}")
        if INDI['cmf']:
            print(f'{dt} {symbol} CMF (Chaikin Money Flow)')
            mfv = ((close_prices - low_prices) - (high_prices - close_prices)) / (high_prices - low_prices)
            mfv = mfv.fillna(0)  # Handle division by zero if high == low
            df['cmf'] = (mfv * volume).rolling(window=20).sum() / volume.rolling(window=20).sum()
            # send_telegram_message(__TOKEN,chat_id,f"CMF calculated:\n{df['cmf'].tail(2).to_string()}")
        if INDI['cmo']:
            print(f'{dt} {symbol} CMO (Chande Momentum Oscillator)')
            df['cmo'] = ta.CMO(close_prices, timeperiod=14)
            # send_telegram_message(__TOKEN,chat_id,f"CMO calculated:\n{df['cmo'].tail(2).to_string()}")
        if INDI['co']:
            print(f'{dt} {symbol} CO (Chaikin Oscillator)')
            # ad = talib.AD(high_prices, low_prices, close_prices, volume)
            df['co'] = ta.ADOSC(high_prices, low_prices, close_prices, volume, fastperiod=3, slowperiod=10)
            # send_telegram_message(__TOKEN,chat_id,f"CO calculated:\n{df['co'].tail(2).to_string()}")
        if INDI['di']:
            print(f'{dt} {symbol} DI (Disparity Index)')
            sma = close_prices.rolling(window=14).mean()
            df['di'] = ((close_prices - sma) / sma) * 100
            # send_telegram_message(__TOKEN,chat_id,f"Disparity Index(DI) calculated:\n{df['di'].tail(2).to_string()}")
        if INDI['ema']:
            print(f'{dt} {symbol} EMA')
            df['ema5'] = close_prices.ewm(span=5, adjust=False).mean()
            df['ema10'] = close_prices.ewm(span=10, adjust=False).mean()
            df['ema50'] = close_prices.ewm(span=50, adjust=False).mean()
            # send_telegram_message(__TOKEN,chat_id,f"Exponential Moving Average calculated:\n{df[['ema5','ema10','ema50']].tail(2).to_string()}")
        if INDI['ht_sine']:
            print(f'{dt} {symbol} HT_SINE')
            sine, leadsine = ta.HT_SINE(close_prices)
            df['htsine'] = sine
            df['htleadsine'] = leadsine
            # send_telegram_message(__TOKEN,chat_id,f"Hilbert Transform Sine calculated:\n{df[['htsine','htleadsine']].tail(2).to_string()}")
        if INDI['keltner']:
            try:
                print(f'{dt} {symbol} KELTNER')
                ema20 = close_prices.ewm(span=20, adjust=False).mean()
                atr10 = ta.ATR(high_prices, low_prices, close_prices, timeperiod=10)
                df['keltner_upper'] = ema20 + (atr10 * 1.5)
                df['keltner_lower'] = ema20 - (atr10 * 1.5)
                # send_telegram_message(__TOKEN,chat_id,f"Keltner calculated:\n{df[['keltner_upper','keltner_lower']].tail(2).to_string()}")
            except Exception as e:
                print(f"❌ Error calculating Keltner: {e}")
                # send_telegram_message(__TOKEN,chat_id,f"❌ Error calculating Keltner: {e}")
        if INDI['macd']:
            print(f'{dt} {symbol} MACD')
            macd, macdsignal, macdhist = ta.MACD(close_prices)
            df['macd'] = macd
            df['macd_signal'] = macdsignal
            df['macd_hist'] = macdhist
            # send_telegram_message(__TOKEN,chat_id,f"Moving Average Convergence/Divergence calculated:\n{df[['macd','macd_signal','macd_hist']].tail(2).to_string()}")
        if INDI['mfi']:
            print(f'{dt} {symbol} MFI')
            df['mfi'] = ta.MFI(high_prices, low_prices, close_prices, volume, timeperiod=14)
            # send_telegram_message(__TOKEN,chat_id,f"MFI calculated:\n{df['mfi'].tail(2).to_string()}")
        if INDI['mom']:
            print(f'{dt} {symbol} MOM')
            df['mom'] = ta.MOM(close_prices, timeperiod=10)
            # 모멘텀의 9-period SMA를 Signal로 사용
            df['mo'] = df['mom'].rolling(window=9).mean()
            # send_telegram_message(__TOKEN,chat_id,f"MOM calculated:\n{df['mom'].tail(2).to_string()}")
        if INDI['natr']:
            print(f'{dt} {symbol} NATR')
            df['natr'] = (df['atr'] / close_prices) * 100
            # send_telegram_message(__TOKEN,chat_id,f"NATR calculated:\n{df['natr'].tail(2).to_string()}")
        if INDI['obv']:
            print(f'{dt} {symbol} OBV')
            df['obv'] = ta.OBV(close_prices, volume)
            # send_telegram_message(__TOKEN,chat_id,f"OBV calculated:\n{df['obv'].tail(2).to_string()}")
        if INDI['ppo']:
            print(f'{dt} {symbol} PPO')
            df['ppo'] = ta.PPO(close_prices)
            # PPO의 9-period EMA를 구하여 Signal로 사용 (Pandas ewm 활용)
            df['ppo_signal'] = df['ppo'].ewm(span=9, adjust=False).mean()
            # Histogram = 메인 라인 - 시그널 라인
            df['ppo_histogram'] = df['ppo'] - df['ppo_signal']
            # send_telegram_message(__TOKEN,chat_id,f"PPO calculated:\n{df['ppo'].tail(2).to_string()}")
        if INDI['roc']:
            print(f'{dt} {symbol} ROC')
            df['roc'] = ta.ROC(close_prices, timeperiod=10)
            # send_telegram_message(__TOKEN,chat_id,f"ROC calculated:\n{df['roc'].tail(2).to_string()}")
        if INDI['rsi']:
            print(f'{dt} {symbol} RSI')
            df['rsi'] = ta.RSI(close_prices)
            # RSI의 14-period SMA를 구하여 Signal로 사용 (Pandas rolling 활용)
            df['rsi_signal'] = df['rsi'].rolling(window=14).mean()
            # send_telegram_message(__TOKEN,chat_id,f"RSI calculated:\n{df['rsi'].tail(2).to_string()}")
        if INDI['sar']:
            print(f'{dt} {symbol} SAR')
            df['sar'] = ta.SAR(high_prices, low_prices, acceleration=0.02, maximum=0.2)
            # send_telegram_message(__TOKEN,chat_id,f"SAR calculated:\n{df['sar'].tail(2).to_string()}")
        if INDI['sma']:
            print(f'{dt} {symbol} SMA')
            df['smaFast'] = close_prices.rolling(window=9).mean()
            df['smaSlow'] = close_prices.rolling(window=26).mean()
            # send_telegram_message(__TOKEN,chat_id,f"Simple Moving Average calculated:\n{df[['smaFast','smaSlow']].tail(2).to_string()}")
        if INDI['stoch']:
            print(f'{dt} {symbol} STOCH')
            # slowk, slowd 2개만 받도록 수정합니다.
            slowk, slowd = ta.STOCH(high_prices, low_prices, close_prices)
            df['slowk'] = slowk
            df['slowd'] = slowd
            # send_telegram_message(__TOKEN,chat_id,f"Slow Stochastic Oscillator(STOCH) calculated:\n{df[['slowk','slowd']].tail(2).to_string()}")
        if INDI['stochf']:
            print(f'{dt} {symbol} STOCHF')
            fastk, fastd = ta.STOCHF(high_prices, low_prices, close_prices) # 주석을 풀고 ta.STOCHF로 변경
            df['fastk'] = fastk
            df['fastd'] = fastd
            # send_telegram_message(__TOKEN,chat_id,f"Fast Stochastic Oscillator(STOCHF) calculated:\n{df[['fastk','fastd']].tail(2).to_string()}")
        if INDI['tema']:
            print(f'{dt} {symbol} TEMA')
            ema1=close_prices.ewm(span=9, adjust=False).mean()
            ema2=ema1.ewm(span=9, adjust=False).mean()
            ema3=ema2.ewm(span=9, adjust=False).mean()
            tema9 = (3 * ema1) - (3 * ema2) + ema3
            df['tema9'] = tema9

            ema1=close_prices.ewm(span=21, adjust=False).mean()
            ema2=ema1.ewm(span=21, adjust=False).mean()
            ema3=ema2.ewm(span=21, adjust=False).mean()
            tema21 = (3 * ema1) - (3 * ema2) + ema3
            df['tema21'] = tema21
            # send_telegram_message(__TOKEN,chat_id,f"Triple Exponential Moving Average calculated:\n{df[['tema9','tema21']].tail(2).to_string()}")
        if INDI['trix']:
            print(f'{dt} {symbol} TRIX')
            df['trix'] = ta.TRIX(close_prices, timeperiod=14)
            # send_telegram_message(__TOKEN,chat_id,f"TRIX calculated:\n{df['trix'].tail(2).to_string()}")
        if INDI['vwap']:
            print(f'{dt} {symbol} VWAP')
            vwap(df)
            # send_telegram_message(__TOKEN,chat_id,f"VWAP calculated:\n{df[['vwap','vwap_upper','vwap_lower']].tail(2).to_string()}")
        if INDI['williams']:
            print(f'{dt} {symbol} WILLIAMS %R')
            df['williams'] = ta.WILLR(high_prices, low_prices, close_prices, timeperiod=14)
            # send_telegram_message(__TOKEN,chat_id,f"WILLIAMS %R calculated:\n{df['williams'].tail(2).to_string()}")
        if INDI['composite_rsi']:
            # Calculate Composite RSI using the defined function
            print(f'{dt} {symbol} Composite RSI')
            composite_rsi_result = composite_rsi(df)
            df['composite_rsi'] = composite_rsi_result['composite_rsi']

        df = df[~pd.isna(df)]
        plot_ohlcv(chat_id,symbol,df,f'resource/{symbol.replace("/","_")}_{ohlc}.png')
        # plot_trend(chat_id,symbol,df,f'resource/{symbol.replace("/","_")}_trend.png')
        print(f'{dt} {symbol} indicators calculation completed.')
        return df

def composite_rsi(df):
        """
        https://medium.com/@corinneroosen/create-a-composite-indicator-for-algorithmic-trading-in-python-0a81920f905b
        Calculate a composite Relative Strength Index (RSI) adjusted by the Average True Range (ATR)
        to make it more dynamic and possibly achieve a broader oscillation range.

        Default Parameter Values:
            window: 14 for RSI
            atr_window: 14 for ATR

        Returns:
            The DataFrame with the composite RSI column.
        """
        rsi_window = 14
        atr_window = 14

        close_delta = df['close'].diff()

        # Calculate gains and losses
        gain = close_delta.clip(lower=0)
        loss = -close_delta.clip(upper=0)

        # Calculate average gain and loss using exponential moving average
        avg_gain = gain.ewm(com=rsi_window - 1, adjust=True, min_periods=rsi_window).mean()
        avg_loss = loss.ewm(com=rsi_window - 1, adjust=True, min_periods=rsi_window).mean()

        # Compute the relative strength and the traditional RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # Calculate ATR for volatility adjustment
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=atr_window).mean()

        # Normalize ATR to adjust the RSI values
        # This is a simple normalization; you may need to adjust the scale based on your data
        normalized_atr = (atr - atr.min()) / (atr.max() - atr.min())

        # Adjust RSI based on ATR
        composite_rsi = rsi * (1 + normalized_atr)  # Simple example to make RSI more dynamic

        # Ensure composite_rsi stays within 0-100 bounds
        composite_rsi = composite_rsi.clip(upper=100)

        # Compile the results into a new DataFrame
        composite_rsi_df = pd.DataFrame({
            'composite_rsi': composite_rsi
        }, index=df.index)

        return composite_rsi_df

def vwap(df:DataFrame)->None:
    '''
    The Volume-Weighted Average Price (VWAP) is a technical indicator that is not included in the TA-Lib library
    because it requires intraday data (volume and price for each transaction or a high-resolution time interval like 1-minute bars).
    TA-Lib is primarily designed for end-of-day data. To calculate VWAP in Python,
    you can use pandas to perform a cumulative calculation on a DataFrame containing intraday data.
    The formula for VWAP is the cumulative typical price times volume, divided by the cumulative volume.

    Args:
        df (DataFrame): DataFrame .

    Returns:
        None:
    '''
    # Calculate the "typical price" for each bar
    # Typical Price = (High + Low + Close) / 3
    df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3

    # Calculate the cumulative sum of (Typical Price * Volume)
    df['tp_volume_cumulative'] = (df['typical_price'] * df['volume']).cumsum()

    # Calculate the cumulative sum of Volume
    df['volume_cumulative'] = df['volume'].cumsum()

    # Calculate VWAP by dividing the two cumulative sums
    df['vwap'] = df['tp_volume_cumulative'] / df['volume_cumulative']

    window:int = 14
    df['price_vwap_diff'] = df['close'] - df['vwap']
    df['rolling_std_dev'] = df['price_vwap_diff'].rolling(window=window).std()

    std_multiplier:int = 2
    df['vwap_upper'] = df['vwap'] + (df['rolling_std_dev']*std_multiplier)
    df['vwap_lower'] = df['vwap'] - (df['rolling_std_dev']*std_multiplier)

def add_heikin_ashi(df:DataFrame)->DataFrame:
    ha_df = pd.DataFrame(index=df.index)

    # Heikin Ashi Close
    ha_df['ha_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4

    # heikin ashi open
    ha_df['ha_open'] = 0.0
    for i in range(len(df)):
        if i == 0:
            ha_df.iloc[i, ha_df.columns.get_loc('ha_open')] = (df['open'].iloc[i] + df['close'].iloc[i]) / 2
        else:
            ha_df.iloc[i, ha_df.columns.get_loc('ha_open')] = (
                ha_df['ha_open'].iloc[i-1] + ha_df['ha_close'].iloc[i-1]
            ) / 2

    # heikin ashi high and low
    ha_df['ha_high'] = df[['high']].join(ha_df[['ha_open', 'ha_close']]).max(axis=1)
    ha_df['ha_low'] = df[['low']].join(ha_df[['ha_open', 'ha_close']]).min(axis=1)

    # heikin ashi volume (same as original)
    ha_df['ha_volume'] = df['volume']

    # Combine original and Heikin Ashi columns
    return pd.concat([df, ha_df], axis=1)
