import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import numpy as np
from api import send_telegram_message#, send_telegram_photo
from config import __TOKEN

def plot_signals_by_volume(chat_id,symbol:str,df:pd.DataFrame,save_path:str)->None:
    try:
        plt.style.use('_mpl-gallery')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df_slice = df.loc[99:,]
        df_slice.set_index('timestamp', inplace=True)
        buy_mask  = df_slice['signal_volume'] == 1
        sell_mask = df_slice['signal_volume'] == -1

        # Plot the price and swing points
        fig, (ax1, ax2, ax3, ax4,ax5) = plt.subplots(5, 1, sharex=True, gridspec_kw={'height_ratios':[2,1,2,1,1]}, figsize=(12, 10))
        ax1.plot(df_slice.index, df_slice['close'], label='Price', color='blue')
        ax1.scatter(df_slice.index[buy_mask], df_slice['close'][buy_mask], color='green', marker='^', label='Buy Signal')
        ax1.scatter(df_slice.index[sell_mask], df_slice['close'][sell_mask], color='red', marker='v', label='Sell Signal')
        # ax1.plot(df_slice.index, df_slice['adl'], color='orange', linewidth=1.5, label='ADL')
        ax1.set_title('Price with Buy/Sell Signals by Volume')
        ax1.set_xlabel('Date and time')
        ax1.set_ylabel('Price')
        ax1.legend()
        ax1.grid(True, color='grey', linestyle=':')

        bar_width = (df_slice.index[1] - df_slice.index[0]).total_seconds() * 0.8 / (24*3600)  # Width as 80% of the time interval in days
        volume_colors = ['green' if df_slice.loc[idx, 'close'] >= df_slice.loc[idx, 'open'] else 'red' for idx in df_slice.index]
        ax2.bar(df_slice.index, df_slice['volume'], width=bar_width, color=volume_colors, alpha=0.8, label='Volume')
        ax2.set_ylabel("Volume")
        ax2.grid(True, color='grey', linestyle=':')

        rolling_high = df_slice['obv'].cummax()
        rolling_low = df_slice['obv'].cummin()
        point_a = None
        point_b = None
        for i in range(1, len(df_slice)):
            if point_a is None and df_slice['obv'].iloc[i] > rolling_high.iloc[i - 1]:
                point_a = df_slice.index[i]
            if point_b is None and df_slice['obv'].iloc[i] < rolling_low.iloc[i - 1]:
                point_b = df_slice.index[i]
            if point_a and point_b:
                break
        # Plotting
        ax3.plot(df_slice.index, df_slice['obv'], color='blue', linewidth=2.5, label='OBV')
        # Label 'OBV line' near the start
        # ax3.text(df_slice.index[2], df_slice['obv'].iloc[2] + 100, 'OBV line', fontsize=12, color='blue')
        # Mark point A and B
        if point_a:
            ax3.plot(point_a, df_slice.loc[point_a, 'obv'], 'go', markersize=10)
            # ax3.text(point_a, df_slice.loc[point_a, 'obv'] + 100, 'A', fontsize=12, fontweight='bold', color='green')
            ax3.axhline(    y=df_slice.loc[point_a, 'obv'], color='green', linestyle='--', linewidth=1)
            ax3.text(point_a, df_slice.loc[point_a, 'obv'] + 200, 'Bullish Signal', fontsize=10, color='green')
        if point_b:
            ax3.plot(point_b, df_slice.loc[point_b, 'obv'], 'ro', markersize=10)
            # ax3.text(point_b, df_slice.loc[point_b, 'obv'] - 200, 'B', fontsize=12, fontweight='bold', color='red')
            ax3.axhline(    y=df_slice.loc[point_b, 'obv'], color='red', linestyle='--', linewidth=1)
            ax3.text(point_b, df_slice.loc[point_b, 'obv'] - 300, 'Bearish Signal', fontsize=10, color='red')
        # Final touches
        # ax3.plot(df_slice.index, df_slice['obv'], color='purple', linewidth=1.5, label='OBV')
        ax3.set_ylabel("OBV")
        ax3.grid(True, color='grey', linestyle=':')
        ax3.legend()

        ax4.plot(df_slice.index, df_slice['cmf'], color='blue', linewidth=1.5, label='CMF(20)')
        ax4.set_ylabel("CMF(20)")
        ax4.grid(True, color='grey', linestyle=':')
        ax4.legend()

        ax5.plot(df_slice.index, df_slice['adl'], color='orange', linewidth=1.5, label='ADL')
        ax5.set_ylabel("ADL")
        ax5.grid(True, color='grey', linestyle=':')
        ax5.legend()
        # --- Move major y-axis ticks and labels to the right side ---
        for ax in [ax1, ax2, ax3, ax4, ax5]:
            ax.yaxis.tick_right()
            ax.yaxis.set_label_position("right")
        # --- Remove the outer lines (spines) for both subplots ---
        ax1.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        ax3.spines['top'].set_visible(False)
        ax3.spines['bottom'].set_visible(False)
        ax4.spines['top'].set_visible(False)
        ax4.spines['bottom'].set_visible(False)
        ax5.spines['top'].set_visible(False)

        # Format x-axis with timestamp labels
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        fig.autofmt_xdate()
        fig.tight_layout(pad=0.5)  # Reduce overall padding
        # plt.tight_layout()
        # Save the plot to a file
        plt.savefig(save_path)
        plt.close(fig)  # Close the figure to free memory
        # send_telegram_photo(__TOKEN,chat_id,save_path,f"{symbol} Buy/Sell Signals by Volume")
    except Exception as e:
        print(f"❌ Error in plot_signals_by_volume: {e}")
        send_telegram_message(__TOKEN,chat_id,f"❌ Error in plot_signals_by_volume: {e}")

def plot_signals_by_momentum(chat_id,symbol:str,df:pd.DataFrame,save_path:str)->None:
    try:
        plt.style.use('_mpl-gallery')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df_slice = df.loc[99:,]
        df_slice.set_index('timestamp', inplace=True)
        buy_mask  = df_slice['signal_momentum'] == 1
        sell_mask = df_slice['signal_momentum'] == -1

        # Plot the price and swing points
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, sharex=True, gridspec_kw={'height_ratios':[2,1,1,1]}, figsize=(12, 6))
        # fig, ax = plt.subplots(figsize=(12, 6))
        ax1.plot(df_slice.index, df_slice['close'], label='Price', color='blue')
        ax1.scatter(df_slice.index[buy_mask], df_slice['close'][buy_mask], color='green', marker='^', label='Buy Signal')
        ax1.scatter(df_slice.index[sell_mask], df_slice['close'][sell_mask], color='red', marker='v', label='Sell Signal')
        ax1.set_title('Price with Buy/Sell Signals by Momentum')
        ax1.set_xlabel('Date and time')
        ax1.set_ylabel('Price')
        ax1.legend()
        ax1.grid(True, color='grey', linestyle=':')

        ax2.plot(df_slice.index, df_slice['rsi'], color='purple', linewidth=1.5, label='RSI(14)')
        ax2.set_ylabel("RSI(14)")
        ax2.grid(True, color='grey', linestyle=':')
        ax2.axhspan(30, 70, color='green', alpha=0.1)
        ax2.legend()

        ax3.plot(df_slice.index, df_slice['fastk'], color='orange', linewidth=1.5, label='%K(14,3)')
        ax3.plot(df_slice.index, df_slice['fastd'], color='red', linewidth=1.5, label='%D(3)')
        ax3.set_ylabel("%K and %D")
        ax3.grid(True, color='grey', linestyle=':')
        ax3.axhspan(20, 80, color='green', alpha=0.1)
        ax3.legend()

        ax4.plot(df_slice.index, df_slice['cci'], color='blue', linewidth=1.5, label='CCI(14)')
        ax4.set_ylabel("CCI(14)")
        ax4.grid(True, color='grey', linestyle=':')
        ax4.axhspan(-100, 100, color='green', alpha=0.1)
        ax4.legend()

        # --- Move major y-axis ticks and labels to the right side ---
        for ax in [ax1, ax2, ax3, ax4]:
            ax.yaxis.tick_right()
            ax.yaxis.set_label_position("right")

        # --- Remove the outer lines (spines) for both subplots ---
        ax1.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        ax3.spines['top'].set_visible(False)
        ax3.spines['bottom'].set_visible(False)
        ax4.spines['top'].set_visible(False)

        # Format x-axis with timestamp labels
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        fig.autofmt_xdate()
        plt.tight_layout()

        # Save the plot to a file
        plt.savefig(save_path)
        plt.close(fig)  # Close the figure to free memory
        # send_telegram_photo(__TOKEN,chat_id,save_path,f"{symbol} Buy/Sell Signals by Momentum")
    except Exception as e:
        print(f"❌ Error in plot_signals_by_momentum: {e}")
        send_telegram_message(__TOKEN,chat_id,f"❌ Error in plot_signals_by_momentum: {e}")

def plot_signals_by_trend(chat_id,symbol:str,df:pd.DataFrame,save_path:str)->None:
    try:
        plt.style.use('_mpl-gallery')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df_slice = df.loc[99:,]
        df_slice.set_index('timestamp', inplace=True)
        buy_mask  = df_slice['signal_trend'] == 1
        sell_mask = df_slice['signal_trend'] == -1

        # Plot the price and swing points
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, gridspec_kw={'height_ratios':[2,1]}, figsize=(12, 6))
        ax1.plot(df_slice.index, df_slice['close'], label='Price', color='blue')
        ax1.scatter(df_slice.index[buy_mask], df_slice['close'][buy_mask], color='green', marker='^', label='Buy Signal')
        ax1.scatter(df_slice.index[sell_mask], df_slice['close'][sell_mask], color='red', marker='v', label='Sell Signal')
        ax1.plot(df_slice.index, df_slice['ema10'], color='orange', linewidth=1.5, label='EMA(10)')
        ax1.plot(df_slice.index, df_slice['ema50'], color='red', linewidth=1.5, label='EMA(50)')
        ax1.set_title('Price with Buy/Sell Signals by Trend')
        ax1.set_xlabel('Date and time')
        ax1.set_ylabel('Price')
        ax1.legend()
        ax1.grid(True, color='grey', linestyle=':')

        ax2.plot(df_slice.index, df_slice['adx'], color='orange', linewidth=1.5, label='ADX(14)')
        ax2.set_ylabel("ADX(14)")
        ax2.grid(True, color='grey', linestyle=':')
        # ax2.axhspan(30, 70, color='green', alpha=0.1)
        ax2.legend()
        # Format x-axis with timestamp labels
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        fig.autofmt_xdate()
        plt.tight_layout()

        # Save the plot to a file
        plt.savefig(save_path)
        plt.close(fig)  # Close the figure to free memory
        # send_telegram_photo(__TOKEN,chat_id,save_path,f"{symbol} Buy/Sell Signals by Trend")
    except Exception as e:
        print(f"❌ Error in plot_signals_by_trend: {e}")
        send_telegram_message(__TOKEN,chat_id,f"❌ Error in plot_signals_by_trend: {e}")

def plot_signals_by_volatility(chat_id,symbol:str,df:pd.DataFrame,save_path:str)->None:
    try:
        plt.style.use('_mpl-gallery')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df_slice = df.loc[99:,]
        df_slice.set_index('timestamp', inplace=True)
        buy_mask  = df_slice['signal_vol'] == 1
        sell_mask = df_slice['signal_vol'] == -1

        # Plot the price and swing points
        # fig, ax = plt.subplots(figsize=(12, 6))
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, gridspec_kw={'height_ratios':[2,1]}, figsize=(12, 6))
        ax1.plot(df_slice.index, df_slice['close'], label='Price', color='blue')
        ax1.scatter(df_slice.index[buy_mask], df_slice['close'][buy_mask], color='green', marker='^', label='Buy Signal')
        ax1.scatter(df_slice.index[sell_mask], df_slice['close'][sell_mask], color='red', marker='v', label='Sell Signal')
        ax1.fill_between(df_slice.index, df_slice['bb_lower'], df_slice['bb_upper'], color='grey', alpha=0.3, linewidth=0.0, label='Bollinger band') # Fill area between BBands
        ax1.fill_between(df_slice.index, df_slice['keltner_lower'], df_slice['keltner_upper'], alpha=0.3, linewidth=0.0, label='Keltner band') # Fill area between BBands

        ax1.set_title('Price with Buy/Sell Signals by Volatility')
        ax1.set_xlabel('Date and time')
        ax1.set_ylabel('Price')
        ax1.legend()
        ax1.grid(True, color='grey', linestyle=':')

        ax2.plot(df_slice.index, df_slice['atr']*1.5, color='purple', linewidth=1.5, label='ATR(14)*1.5')
        ax2.plot(df_slice.index, df_slice['price_change'], color='green', linewidth=1.5, label='Price chg')
        ax2.set_ylabel("ATR(14)*1.5 and Price chg")
        ax2.grid(True, color='grey', linestyle=':')
        ax2.legend()
        # --- Move major y-axis ticks and labels to the right side ---
        for ax in [ax1, ax2]:
            ax.yaxis.tick_right()
            ax.yaxis.set_label_position("right")
        # --- Remove the outer lines (spines) for both subplots ---
        ax1.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)

        # Format x-axis with timestamp labels
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        fig.autofmt_xdate()
        plt.tight_layout()

        # Save the plot to a file
        plt.savefig(save_path)
        plt.close(fig)  # Close the figure to free memory
        # send_telegram_photo(__TOKEN,chat_id,save_path,f"{symbol} Buy/Sell Signals by Volatility")
    except Exception as e:
        print(f"❌ Error in plot_signals_by_volatility: {e}")
        send_telegram_message(__TOKEN,chat_id,f"❌ Error in plot_signals_by_vol: {e}")

def plot_trend(chat_id,symbol:str,df:pd.DataFrame,save_path:str)->None:
    # aroon,    adx,    trix
    try:
        plt.style.use('_mpl-gallery')
        df.set_index('timestamp', inplace=True)
        # Plot the price and trend points
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, gridspec_kw={'height_ratios':[1,1,1]}, figsize=(12, 10))
        fig.suptitle(f'{symbol} Trend Indicators', fontsize=16) # Overall title for the figure
        ax1.plot(df.index, df['aroon_up'], color='red', linewidth=1.5, label='Aroon Up')
        ax1.plot(df.index, df['aroon_down'], color='blue', linewidth=1.5, label='Aroon Down')
        ax1.set_title('Aroon Indicator')
        ax1.set_xlabel('Date and time')
        ax1.legend()
        ax1.grid(True, color='grey', linestyle=':')

        last_time = df.index[-1]
        ax2.plot(df.index, df['adx'], color='purple', linewidth=1.5, label='ADX(14)')
        ax2.set_ylabel("ADX(14)")
        ax2.grid(True, color='grey', linestyle=':')
        ax2.axhspan(25, 50, color='green', alpha=0.1)
        ax2.axhspan(75,100, color='green', alpha=0.1)
        ax2.legend()
        last_adx = df['adx'].iloc[-1]
        ax2.text(last_time, last_adx, f'{last_adx:.2f}', color='purple', fontsize=9, verticalalignment='center', horizontalalignment='left')

        ax3.plot(df.index, df['trix'], color='purple', linewidth=1.5, label='TRIX(14)')
        ax3.set_ylabel("TRIX(14)")
        ax3.grid(True, color='grey', linestyle=':')
        ax3.legend()
        last_trix = df['trix'].iloc[-1]
        ax3.text(last_time, last_trix, f'{last_trix:.2f}', color='purple', fontsize=9, verticalalignment='center', horizontalalignment='left')

        for ax in [ax1, ax2, ax3]:
            ax.yaxis.tick_right()
            ax.yaxis.set_label_position("right")

        # --- Remove the outer lines (spines) for both subplots ---
        ax1.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        ax3.spines['top'].set_visible(False)
        # Format x-axis with timestamp labels
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        fig.autofmt_xdate()
        plt.tight_layout()

        # Save the plot to a file
        plt.savefig(save_path)
        plt.close(fig)  # Close the figure to free memory
        caption:str = "Trend indicators are tools used in technical analysis to identify the overall direction of the"
        caption+=" market or a particular asset. Traders rely on these indicators to understand whether a stock,"
        caption+=" commodity, or other financial instrument is trending upwards, downwards, or moving"
        caption+=" sideways. Trend indicators are critical for determining the best technical indicator for trend"
        caption+=" reversal, providing insights into when a price trend may be about to change direction."
        # send_telegram_photo(__TOKEN,chat_id,save_path,caption)
    except Exception as e:
        print(f"❌ Error in plot_trend: {e}")
        send_telegram_message(__TOKEN,chat_id,f"❌ Error in plot_trend: {e}")

def plot_swings(chat_id,symbol:str,df:pd.DataFrame,high_swings,low_swings,save_path:str)->None:
    try:
        plt.style.use('_mpl-gallery')
        # df.set_index('timestamp', inplace=True)
        # Plot the price and swing points
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df.index, df['close'], label='Price', color='blue')
        ax.scatter(df.index[high_swings], df['close'].iloc[high_swings], color='green', marker='^', label='Swing Highs')
        ax.scatter(df.index[low_swings], df['close'].iloc[low_swings], color='red', marker='v', label='Swing Lows')
        ax.set_title('Price Swings with Dynamic Threshold (Volatility x 1.5)')
        ax.set_xlabel('Date and time')
        ax.set_ylabel('Price')
        ax.legend()
        ax.grid(True)
        # Format x-axis with timestamp labels
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        fig.autofmt_xdate()
        ax.legend()
        ax.grid(True, color='grey', linestyle=':')
        plt.tight_layout()
        # Save the plot to a file
        plt.savefig(save_path)
        plt.close(fig)  # Close the figure to free memory
        # send_telegram_photo(__TOKEN,chat_id,save_path,f"{symbol} Swings Chart")
    except Exception as e:
        print(f"❌ Error in plot_swings: {e}")
        send_telegram_message(__TOKEN,chat_id,f"❌ Error in plot_swings: {e}")

def plot_ohlcv(chat_id,symbol:str,df:pd.DataFrame,save_path:str)->None:
    # Set up the figure and two subplots sharing the x-axis (dates)
    # gridspec_kw={'height_ratios': [3, 1]} makes the top subplot (price) taller than the bottom (volume)
    try:
        plt.style.use('_mpl-gallery')
        df_slice = df.loc[99:,]
        df_slice.set_index('timestamp', inplace=True)
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, sharex=True, gridspec_kw={'height_ratios':[2,1,1,1]}, figsize=(12, 10))
        fig.suptitle(f'{symbol} OHLCV Chart', fontsize=16) # Overall title for the figure

        # --- Plot Close Price (Line Chart) on ax1 ---
        ax1.plot(df_slice.index, df_slice['close'], color='blue', linewidth=1.5, label='Close Price', marker='o', markersize=4,markerfacecolor='white',markeredgecolor='blue')
        ax1.plot(df_slice.index, df_slice['smaFast'], color='orange', linewidth=1.5, label='Fast MA(9)')
        ax1.plot(df_slice.index, df_slice['smaSlow'], color='red', linewidth=1.5, label='Slow MA(26)')
        ax1.fill_between(df_slice.index, df_slice['bb_lower'], df_slice['bb_upper'], color='grey', alpha=0.3, linewidth=0.0, label='Bollinger band') # Fill area between BBands
        ax1.fill_between(df_slice.index, df_slice['vwap_lower'], df_slice['vwap_upper'], alpha=0.3, linewidth=0.0, label='VWAP band') # Fill area between BBands
        ax1.plot(df_slice.index, df_slice['vwap'], color='magenta', linewidth=1.5, label='VWAP')
        ax1.set_ylabel("Price")
        ax1.grid(True, color='grey', linestyle=':')
        ax1.legend() # Display the legend for the Close Price line

        last_time = df_slice.index[-1]
        last_price = df_slice['close'].iloc[-1]
        ax1.text(last_time, last_price, f'{last_price:.2f}', color='blue', fontsize=9, verticalalignment='center', horizontalalignment='left')

        # --- Plot Volume (Bar Chart) on ax2 ---
        # Color volume bars based on close price direction (optional, but common)
        bar_width = (df_slice.index[1] - df_slice.index[0]).total_seconds() * 0.8 / (24*3600)  # Width as 80% of the time interval in days
        volume_colors = ['green' if df_slice.loc[idx, 'close'] >= df_slice.loc[idx, 'open'] else 'red' for idx in df_slice.index]
        ax2.bar(df_slice.index, df_slice['volume'], width=bar_width, color=volume_colors, alpha=0.8, label='Volume')
        ax2.set_ylabel("Volume")
        ax2.grid(True, color='grey', linestyle=':')

        ax3.plot(df_slice.index, df_slice['rsi'], color='purple', linewidth=1.5, label='RSI(14)')
        ax3.plot(df_slice.index, df_slice['composite_rsi'], color='orange', linewidth=1.5, label='Composite RSI(14)')
        ax3.set_ylabel("RSI(14)")
        ax3.grid(True, color='grey', linestyle=':')
        ax3.axhspan(30, 70, color='green', alpha=0.1)
        ax3.legend()
        last_rsi = df_slice['rsi'].iloc[-1]
        ax3.text(last_time, last_rsi, f'{last_rsi:.2f}', color='purple', fontsize=9, verticalalignment='center', horizontalalignment='left')
        last_composite_rsi = df_slice['composite_rsi'].iloc[-1]
        ax3.text(last_time, last_composite_rsi, f'{last_composite_rsi:.2f}', color='purple', fontsize=9, verticalalignment='center', horizontalalignment='left')

        # --- Plot MACD (Line and Histogram) on ax3 ---
        # MACD and Signal lines
        ax4.plot(df_slice.index, df_slice['macd'], color='blue', linewidth=1, label='MACD')
        ax4.plot(df_slice.index, df_slice['macd_signal'], color='orange', linewidth=1, label='Signal')
        # MACD Histogram bars
        # Determine bar colors based on positive/negative values
        hist_colors = ['red' if h < 0 else 'green' for h in df_slice['macd_hist']]
        ax4.bar(df_slice.index, df_slice['macd_hist'], width=bar_width, color=hist_colors, alpha=0.7, label='Histogram')
        ax4.set_ylabel("MACD")
        ax4.grid(True, color='grey', linestyle=':')
        ax4.legend()

        # --- Move major y-axis ticks and labels to the right side ---
        for ax in [ax1, ax2, ax3, ax4]:
            ax.yaxis.tick_right()
            ax.yaxis.set_label_position("right")

        # --- Remove the outer lines (spines) for both subplots ---
        ax1.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        ax3.spines['top'].set_visible(False)
        ax3.spines['bottom'].set_visible(False)
        ax4.spines['top'].set_visible(False)

        # Create a date formatter for the desired format
        date_fmt = mdates.DateFormatter('%Y-%m-%d %H:%M')

        # Apply the formatter to the x-axis
        ax1.xaxis.set_major_formatter(date_fmt)

        # Automatically adjust date labels to prevent overlap
        fig.autofmt_xdate()

        # 4. Format the volume axis (ax2) labels to 'k' for thousands
        def thousands_formatter(x, pos):
            """Function to format thousands as 'k'."""
            return f'{x/1000:.0f}k'

        ax2.yaxis.set_major_formatter(ticker.FuncFormatter(thousands_formatter))
        # Adjust layout to prevent elements from overlapping
        plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # [left, bottom, right, top] for title

        # Save the plot to a file
        plt.savefig(save_path)

        plt.close(fig)  # Close the figure to free memory
        # send_telegram_photo(__TOKEN,chat_id,save_path,f"{symbol} OHLCV Chart")
        # Show the plot
        # plt.show()
    except Exception as e:
        print(f"❌ Error in plot_ohlcv: {e}")
        send_telegram_message(__TOKEN,chat_id,f"❌ Error in plot_ohlcv: {e}")
