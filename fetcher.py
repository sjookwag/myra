# Fetch OHLCV data asynchronously
from config import SYMBOLS, TIMEFRAME, LIMIT, __TOKEN
from exchange import create_exchange
from time import strftime, localtime
from api import send_telegram_message

async def fetch_ohlcv_for_symbol(chat_id,exchange_id:str,symbol:str,timeframe:str=TIMEFRAME)->dict:
    try:
        exchange = await create_exchange(exchange_id)
        if not exchange:
            raise ValueError("Exchange instance is None")

        print(f"🔄 Fetching OHLCV for {symbol} at fetch_ohlcv_for_symbol...")
        # send_telegram_message(__TOKEN,chat_id,f"🔄 Fetching OHLCV for {symbol}...")
        dt:str = strftime("%m-%d %H:%M:%S", localtime())
        print(f'{dt} retrieving {symbol}...')
        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=LIMIT)
        await exchange.close()
        return dict([(symbol, ohlcv)])
    except Exception as e:
        if exchange:
            await exchange.close()
        print(f"❌ Error fetching {symbol}: {e}")
        send_telegram_message(__TOKEN,chat_id,f"❌ Error fetching {symbol}: {e}")
        return dict([(symbol, None)])

async def fetch_ohlcv_for_timeframes(chat_id,exchange,symbol:str,timeframe:str=TIMEFRAME)->tuple:
    try:
        print(f"🔄 Fetching OHLCV for {timeframe} at fetch_ohlcv_for_timeframes...")
        send_telegram_message(__TOKEN,chat_id,f"🔄 Fetching OHLCV for {timeframe} at fetch_ohlcv_for_timeframes...")
        dt:str = strftime("%m-%d %H:%M:%S", localtime())
        print(f'{dt} retrieving {symbol}...')
        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=LIMIT)
        # await exchange.close()
        return timeframe, ohlcv
    except Exception as e:
        if exchange:
            await exchange.close()
        print(f"❌ Error fetching {symbol}: {e}")
        send_telegram_message(__TOKEN,chat_id,f"❌ Error fetching {symbol} for {timeframe}: {e}")
        return timeframe, None

async def fetch_all_timeframes(chat_id,exchange_id:str='bitget',symbol:str='XRP/USDT'):
    try:
        exchange = create_exchange(exchange_id)
        if not exchange:
            raise ValueError("Exchange instance is None")
        timeframes:list = ['15m', '1h', '4h', '1d']
        data = [await fetch_ohlcv_for_timeframes(chat_id,exchange,symbol,tf) for tf in timeframes]
        if exchange:
            await exchange.close()
        return dict(data)
    except Exception as e:
        if exchange:
            await exchange.close()
        print(f"❌ Error fetching {symbol}: {e}")
        send_telegram_message(__TOKEN,chat_id,f"❌ Error fetching {symbol}: {e}")
        return None
