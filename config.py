from telegram import InlineKeyboardButton

# Configuration settings
HEIKIN_ASHI = True
SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'SOL/USDT']
TIMEFRAME = '15m'
LIMIT = 200
INTERVAL_SEC = 1*60  # minutes * 60 sec

# Telegram bot@tf315_bot
# __TOKEN = '6664573909:AAHYISGiUzA2CyhDyMBZSqHbfjmZkFVlz3k'
# Telegram bot@tf315_bot
__TOKEN = '5893898822:AAFFEcx2yPUk6BqPVzq_MXVoANswazBvtsg'
# __CHAT_ID= ['-1001726872887']

# Indicators
INDI:dict = {
    'adl':True,
    'adx':True,
    'apo':True,
    'aroon':True,
    'atr':True,
    'bb':True,
    'cci':True,
    'cmf':True,
    'cmo':True,
    'co':True,
    'di':True,
    'dmdi':True,
    'dpo':True,
    'ema':True,
    'ht_sine':True,
    'keltner':True,
    'klinger':True,
    'lrsi':True,
    'macd':True,
    'mfi':True,
    'mom':True,
    'natr':True,
    'obv':True,
    'ppo':True,
    'roc':True,
    'rsi':True,
    'sar':True,
    'sma':True,
    'stoch':True,
    'stochf':True,
    'tema':True,
    'trix':True,
    'vwap':True,
    'williams':True,
    'composite_rsi':True,
    }
DESC:dict = {
    'adl'    :"Accumulation/Distribution Line (ADL):\nA volume-based indicator that measures the cumulative flow of money into and out of a security, helping to identify divergences between price and volume.",
    'adx'    :"The Average Directional Index(ADX):\nIt is a technical indicator used to measure the strength of a price trend, rather than the direction itself.\nA rising ADX value indicates a strong trend, while a falling ADX indicates a weak or non-trending market.",
    'aroon'  :"Aroon Indicator:\nA technical indicator that measures the time between highs and lows over a specified period to identify trend changes and the strength of a trend.",
    'apo'    :"Absolute Price Oscillator:\nA momentum oscillator that measures the difference between two moving averages of a security's price, often used to identify trend direction and potential buy/sell signals.",
    'atr'    :"ATR(Average True Range):\nAn indicator that measures market volatility by calculating the average of a security's true price range over a specified period.",
    'bb'     :"Bollinger Bands:\nA volatility indicator consisting of a moving average with an upper and lower band that adjust to market volatility, often used to identify overbought or oversold conditions.",
    'cci'    :"Commodity Channel Index:\nA momentum-based oscillator that measures the deviation of a security's price from its average price over a specified period, often used to identify cyclical trends and overbought or oversold conditions.",
    'cmf'    :"Chaikin Money Flow:\nA volume-weighted average of accumulation and distribution over a specified period, used to measure buying and selling pressure.",
    'cmo'    :"Chande Momentum Oscillator:\nA momentum oscillator that measures the strength of a trend by comparing the sum of recent price gains to the sum of recent price losses.",
    'co'     :"Chaikin Oscillator:\nA momentum indicator that measures the accumulation-distribution line's velocity by subtracting a 10-day exponential moving average (EMA) from a 3-day EMA of the accumulation-distribution.",
    'di'     :"Disparity Index:\nA technical indicator that measures the percentage difference between the current price and a moving average, often used to identify overbought or oversold conditions.",
    'dmdi'   :"Directional Movement Index:\nA set of indicators that measure a security's direction and trend strength, consisting of the Positive Directional Indicator (+DI), Negative Directional Indicator (-DI), and Average Directional Index (ADX).",
    'dpo'    :"Detrended Price Oscillator:\nA technical indicator that removes the long-term trends from price data to help identify short-term cycles and overbought or oversold conditions.",
    'ema'    :"Exponential Moving Average:\nA type of moving average that places a greater weight on more recent price data, making it more responsive to recent price changes than a simple moving average (SMA).",
    'ht_sine':"Hilbert Transform Sine:\nAn indicator that uses the Hilbert Transform to identify cyclical turning points in price action by detecting the current phase of the dominant market cycle. ",
    'keltner':"Keltner Channels:\nA volatility-based envelope indicator that consists of an exponential moving average (EMA) as the middle line, with upper and lower bands set a certain distance away based on the Average True Range (ATR).",
    'klinger':"Klinger Oscillator:\nA volume-based indicator that compares the volume flowing through a security to its price movements, aiming to identify long-term trends in money flow.",
    'lrsi'   :"Linear Regression Slope:\nA statistical measure that calculates the slope of the linear regression line fitted to a security's price data over a specified period, often used to identify trend direction and strength.",
    'macd'   :"Moving Average Convergence/Divergence:\nA trend-following momentum indicator that shows the relationship between two moving averages of a security's price, often used to identify changes in the direction, momentum, and duration of a trend.",
    'mfi'    :"Money Flow Index(MFI):\nIt is a momentum indicator that measures the flow of money into and out of a security over a specified period.\nIt is similar to the Relative Strength Index (RSI) but incorporates volume data. A higher MFI indicates strong buying pressure.",
    'mom'    :"Momentum:\nA momentum oscillator that measures the rate of change of a security's price over a specified period, often used to identify overbought or oversold conditions.",
    'natr'   :"Normalized Average True Range:\nA volatility indicator that measures the average true range of a security's price movements, normalized by the closing price, often used to identify periods of high or low volatility.",
    'obv'    :"On-Balance Volume:\nA momentum indicator that uses volume flow to predict price changes, based on the theory that volume precedes price.",
    'ppo'    :"Percentage Price Oscillator:\nA momentum oscillator that measures the difference between two moving averages as a percentage of the larger moving average, often used to identify trend direction and potential buy/sell signals.",
    'roc'    :"Rate of Change:\nA momentum oscillator that measures the percentage change in price between the current price and the price a certain number of periods ago, often used to identify overbought or oversold conditions.",
    'rsi'    :"Relative Strength Index:\nA momentum oscillator that measures the speed and change of price movements on a scale from 0 to 100, typically used to identify overbought and oversold conditions. ",
    'sar'    :"Parabolic SAR(Stop and Reverse):\nIt  is a technical analysis tool used to determine the direction of a security\'s momentum and to pinpoint potential reversals in price.",
    'sma'    :"Simple Moving Average:\nIt is one of the most basic and widely used technical indicators.\nIts purpose is to smooth out price data over a specified period by calculating the average price, thereby making it easier to identify the direction of the trend and reduce the impact of random, short-term price fluctuations (often referred to as 'noise').",
    'stoch ' :"Slow Stochastic Oscillator(STOCH):\nIt is generally considered to be less sensitive and provide more reliable signals than the Fast Stochastic due to the additional smoothing applied by the slowk_period and slowd_period parameters.",
    'stochf' :"Fast Stochastic Oscillator(STOCHF):\nIt is a momentum indicator that compares a security's closing price to its price range over a given period.\nUnlike the full stochastic oscillator, the fast version does not smooth the %K line, resulting in a more sensitive indicator that reacts more quickly to price changes.",
    'tema'   :"Triple Exponential Moving Average:\nTEMA stands for Triple Exponential Moving Average.\nIt\'s an indicator designed to provide a smoother and more responsive moving average compared to traditional moving averages like the Simple Moving Average (SMA) or even the Exponential Moving Average (EMA).\nThe goal of TEMA is to reduce the lag inherent in moving averages.\nIn summary, TEMA is an advanced type of moving average aimed at providing a faster and more accurate representation of the underlying price trend by minimizing lag.",
    'trix'   :"TRIX (Triple Exponential Average):\nA momentum oscillator that displays the rate of change of a triple exponentially smoothed moving average, often used to identify oversold and overbought markets.",
    'vwap'   :"Volume-Weighted Average Price:\nAn intraday indicator that calculates the average price of a security based on both price and volume, often used by traders to evaluate current price and execution quality.",
    'williams':"Williams %R:\nA momentum indicator that measures overbought and oversold levels, similar to the Stochastic Oscillator, but plotted on a negative scale from -100 to 0.",
    'composite_rsi':"Composite RSI:\nBy combining RSI and ATR this composite indicator should account for momentum (RSI) but also incorporates market volatility (ATR). The idea is that a composite indicator could offer a more rounded view of the market, helping in decision-making by highlighting potential buy or sell signals that consider both price momentum and volatility."
    }

MAIN_KEYBOARD = [
    [InlineKeyboardButton("Subscribe",    callback_data="menu_subs") ,
     InlineKeyboardButton("View settings",callback_data="menu_setg")],
    [InlineKeyboardButton("Exchange",     callback_data="menu_exch") ,
     InlineKeyboardButton("Alarm",        callback_data="menu_alrm")],
    [InlineKeyboardButton("Symbols",      callback_data="menu_symb") ,
     InlineKeyboardButton("Time frame",   callback_data="menu_tfrm")],
    [InlineKeyboardButton("OHLC type",    callback_data="menu_ohlc") ,
     InlineKeyboardButton("Unsubscribe",   callback_data="menu_unsb")],
]
ALRM_KEYBOARD = [
    [InlineKeyboardButton("15m", callback_data="alarm_15m") ,
     InlineKeyboardButton("30m", callback_data="alarm_30m")],
    [InlineKeyboardButton("60m", callback_data="alarm_60m") ,
     InlineKeyboardButton("1d",  callback_data="alarm_1d") ],
    [InlineKeyboardButton("⬅️ Back", callback_data="menu_back")]
]
SYMB_KEYBOARD = [
    [InlineKeyboardButton("BTC/USDT", callback_data="symbol_BTC/USDT") ,
     InlineKeyboardButton("ETH/USDT", callback_data="symbol_ETH/USDT")],
    [InlineKeyboardButton("XRP/USDT", callback_data="symbol_XRP/USDT") ,
     InlineKeyboardButton("BNB/USDT", callback_data="symbol_BNB/USDT")],
    [InlineKeyboardButton("⬅️ Back", callback_data="menu_back")]
]
TFRM_KEYBOARD = [
    [InlineKeyboardButton("15m", callback_data="timeframe_15m") ,
     InlineKeyboardButton("30m", callback_data="timeframe_30m")],
    [InlineKeyboardButton("60m", callback_data="timeframe_60m") ,
     InlineKeyboardButton("1d",  callback_data="timeframe_1d") ],
    [InlineKeyboardButton("⬅️ Back", callback_data="menu_back")]
]
OHLC_KEYBOARD = [
    [InlineKeyboardButton("Standard OHLC",callback_data="ohlc_ohlc"),
     InlineKeyboardButton("HEIKIN ASHI",  callback_data="ohlc_hksi")],
    [InlineKeyboardButton("⬅️ Back", callback_data="menu_back")]
]
EXCH_KEYBOARD = [
    [InlineKeyboardButton("Binance",    callback_data="exchange_binance")   ,
     InlineKeyboardButton("Bybit",      callback_data="exchange_bybit")    ],
    [InlineKeyboardButton("Bitget",     callback_data="exchange_bitget")    ,
     InlineKeyboardButton("Crypto.com", callback_data="exchange_cryptocom")],
    [InlineKeyboardButton("Gate.io",    callback_data="exchange_gate")      ,
     InlineKeyboardButton("HTX(Huobi)", callback_data="exchange_htx")      ],
    [InlineKeyboardButton("MEXC",       callback_data="exchange_mexc")      ,
     InlineKeyboardButton("OKX",        callback_data="exchange_okx")      ],
    [InlineKeyboardButton("⬅️ Back",   callback_data="menu_back")]
]
