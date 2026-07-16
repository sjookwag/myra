# Exchange setup using ccxt.async_support
import ccxt.async_support as ccxt

EXCH:dict = {'binance':ccxt.binance
    ,'bybit':ccxt.bybit
    ,'bitget':ccxt.bitget
    ,'cryptocom':ccxt.cryptocom
    ,'gate':ccxt.gateio
    ,'htx':ccxt.htx
    ,'mexc':ccxt.mexc
    ,'okx':ccxt.okx
    }

async def create_exchange(exchange_id: str = 'bitget'):
# def create_exchange(exchange_id: str = 'bitget'):
    print(f"🔄 Creating exchange for {exchange_id}...")
    return EXCH.get(exchange_id, ccxt.bitget)()
