import talib
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import numpy as np

# Sample DataFrame (from previous examples)
data = {
    'timestamp': pd.to_datetime([
        '2025-10-03 13:30:00', '2025-10-03 13:45:00', '2025-10-03 14:00:00', '2025-10-03 14:15:00',
        '2025-10-03 14:30:00', '2025-10-03 14:45:00', '2025-10-03 15:00:00', '2025-10-03 15:15:00',
        '2025-10-03 15:30:00', '2025-10-03 15:45:00', '2025-10-03 16:00:00', '2025-10-03 16:15:00',
        '2025-10-03 16:30:00', '2025-10-03 16:45:00', '2025-10-03 17:00:00', '2025-10-03 17:15:00',
        '2025-10-03 17:30:00', '2025-10-03 17:45:00', '2025-10-03 18:00:00', '2025-10-03 18:15:00'
    ]),
    'open': [3.0259, 3.0214, 3.0257, 3.0221, 3.0292, 3.0341, 3.0432, 3.0363, 3.0411, 3.0551, 3.0683, 3.0795, 3.0862, 3.0936, 3.0617, 3.0579, 3.0399, 3.0448, 3.0288, 3.0358],
    'high': [3.0332, 3.0300, 3.0301, 3.0309, 3.0377, 3.0477, 3.0432, 3.0523, 3.0555, 3.0726, 3.0879, 3.0919, 3.0936, 3.0949, 3.0617, 3.0579, 3.0548, 3.0457, 3.0373, 3.0478],
    'low': [3.0154, 3.0202, 3.0168, 3.0168, 3.0244, 3.0337, 3.0262, 3.0363, 3.0410, 3.0501, 3.0683, 3.0753, 3.0808, 3.0588, 3.0125, 3.0369, 3.0344, 3.0226, 3.0205, 3.0336],
    'close': [3.0214, 3.0257, 3.0221, 3.0292, 3.0341, 3.0432, 3.0363, 3.0411, 3.0551, 3.0683, 3.0795, 3.0862, 3.0936, 3.0617, 3.0579, 3.0399, 3.0448, 3.0288, 3.0358, 3.0453],
    'volume': [1.323694e+06, 5.621725e+05, 9.089727e+05, 1.030237e+06, 2.787983e+05, 4.387176e+05, 2.969257e+05, 5.911668e+05, 5.751441e+05, 1.871326e+06, 1.416260e+06, 9.377586e+05, 9.791957e+05, 1.904477e+06, 3.070575e+06, 1.629439e+06, 7.453535e+05, 1.003167e+06, 6.410645e+05, 4.760495e+05],
    'symbol': ['XRP/USDT'] * 20
}
df = pd.DataFrame(data)
df.set_index('timestamp', inplace=True)

# Calculate ADX (note: will produce NaN for a short dataset)
df['ADX'] = talib.ADX(df['high'].astype(float), df['low'].astype(float), df['close'].astype(float), timeperiod=14)

# Create a subplot for the ADX
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df.index, df['ADX'], color='blue', linewidth=1.5, label='ADX')
ax.axhline(25, color='grey', linestyle='--', label='Threshold (25)')
ax.set_title(f'{df["symbol"].iloc} ADX')
ax.set_ylabel("ADX Value")
ax.grid(True, color='grey', linestyle=':')
ax.legend()
plt.show()

# 2. Using ADX in a simple trading strategy
# The ADX is not a directional indicator but rather a filter for trend strength. Here's how you might use it in combination with another indicator, like a moving average crossover, to generate trading signals.

# ```python
# Assuming you have already calculated ADX and EMAs
# Calculate EMAs for trend direction
df['EMA_10'] = talib.EMA(df['close'].astype(float), timeperiod=10)
df['EMA_50'] = talib.EMA(df['close'].astype(float), timeperiod=50)

# Define ADX threshold
adx_threshold = 25

# Generate signals
df['Signal'] = 0

# Buy signal: EMA_10 crosses above EMA_50 AND ADX is trending strong
df.loc[(df['EMA_10'] > df['EMA_50']) & (df['EMA_10'].shift(1) <= df['EMA_50'].shift(1)) & (df['ADX'] > adx_threshold), 'Signal'] = 1

# Sell signal: EMA_10 crosses below EMA_50 AND ADX is trending strong
df.loc[(df['EMA_10'] < df['EMA_50']) & (df['EMA_10'].shift(1) >= df['EMA_50'].shift(1)) & (df['ADX'] > adx_threshold), 'Signal'] = -1

# Display the signals
print(df[['close', 'EMA_10', 'EMA_50', 'ADX', 'Signal']].tail(10))
