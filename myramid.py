from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, constants, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from prettytable import PrettyTable
import logging
import os
import asyncio
from fetcher import fetch_ohlcv_for_symbol, fetch_all_timeframes
from processor import process_data
from util import get_user_settings, update_user_settings
from config import __TOKEN,MAIN_KEYBOARD,ALRM_KEYBOARD,SYMB_KEYBOARD,TFRM_KEYBOARD,OHLC_KEYBOARD,EXCH_KEYBOARD
from indicators import indicators
from api import send_media_group, send_message_md2
from api import send_telegram_message, send_telegram_photo
from analysis import basic_analysis,trends_analysis,highs_lows,prices_swings
from analysis import signal_by_trend,signal_by_momentum,signal_by_volatility,signal_by_volume

periodic_task_handle = None
# Enable logging
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )

# Main menu command
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = MAIN_KEYBOARD
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("Main Menu:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Main Menu:", reply_markup=reply_markup)

# Handle button presses
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global periodic_task_handle

    user_id = update.effective_user.id
    settings = get_user_settings(user_id)

    query = update.callback_query
    await query.answer()
    # chat_id = query.message.chat_id

    if query.data == "menu_alrm":
        keyboard = ALRM_KEYBOARD
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Alarm:", reply_markup=reply_markup)
    elif query.data == "menu_symb":
        keyboard = SYMB_KEYBOARD
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Symbol:", reply_markup=reply_markup)
    elif query.data == "menu_tfrm":
        keyboard = TFRM_KEYBOARD
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Time frame:", reply_markup=reply_markup)
    elif query.data == "menu_ohlc":
        keyboard = OHLC_KEYBOARD
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("OHLC:", reply_markup=reply_markup)
    elif query.data == "menu_exch":
        keyboard = EXCH_KEYBOARD
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Exchange:", reply_markup=reply_markup)
    elif query.data == "menu_subs":
        await subscribe(update, context)
    elif query.data == "menu_unsb":
        await unsubscribe(update, context)
    elif query.data == "menu_back":
        await menu(update, context)
    elif query.data == "menu_setg":
        response = "Your current settings are as follows:\n"
        # Create a PrettyTable object
        table = PrettyTable()
        table.field_names = ["Setting", "Value"]
        table.add_row(["Alarm",     settings['alarm']])
        table.add_row(["Exchange",  settings['exchange']])
        table.add_row(["Symbol",    settings['symbol']])
        table.add_row(["Time frame",settings['timeframe']])
        table.add_row(["OHLC",      settings['ohlc']])
        # Wrap the table string in a code block
        response += f"```\n{table.get_string()}\n```"
        await query.message.reply_text(response, parse_mode=constants.ParseMode.MARKDOWN_V2)
    else:
        key, value = query.data.split("_",1)
        settings[key] = value
        update_user_settings(user_id, settings)
        await query.message.reply_text(f"You selected: {query.data}")

        # Restart periodic task if running
        if not(periodic_task_handle is None or periodic_task_handle.done()):
            # Restart the periodic task with new settings
            await unsubscribe(update, context)
            await query.message.reply_text("🔄 Settings updated and Myramid restarted.")
            await subscribe(update, context)

async def periodic_task(settings:dict)->None:
    try:
        required_keys = ['exchange', 'symbol', 'timeframe','alarm','chat_id']
        if all(key in settings for key in required_keys):
            # print("✅ All keys are present!")
            exchange_id:str = settings['exchange']
            interval:int = int(settings['alarm'][:-1])*60
            symbol:str = settings['symbol']
            timeframe:str = settings['timeframe']
            chat_id = settings['chat_id']
            print(f"chat_id:{chat_id}")

            while True:
                try:
                    print("🔄 Retrieving OHLC...")
                    raw_data = await fetch_ohlcv_for_symbol(chat_id,exchange_id,symbol,timeframe)

                    if raw_data.get(symbol) is None:
                        print(f"No data returned for {symbol}")
                        # send_telegram_message(__TOKEN,chat_id,f"No data returned for {symbol}")
                    else:
                        dfs = process_data(chat_id,raw_data)
                        ohlc_type = settings.get('ohlc', 'ohlc')
                        df = indicators(chat_id,dfs,ohlc_type)
                        # df = indicators(chat_id,dfs,settings['ohlc'] if 'ohlc' in settings else 'ohlc' )
                        # prices_swings(chat_id,symbol,df)
                        # basic_analysis(chat_id,symbol,df)
                        analysis_msg = basic_analysis(chat_id, symbol, df)
                        signal_by_trend(chat_id,symbol,df)
                        signal_by_momentum(chat_id,symbol,df)
                        signal_by_volatility(chat_id,symbol,df)
                        signal_by_volume(chat_id,symbol,df)
                        # trends_analysis(chat_id,symbol,df)
                        # highs_lows(chat_id,symbol,df,settings['ohlc'] if 'ohlc' in settings else 'ohlc')
                        # 2. 통합 텍스트 메시지 전송 (1번 알림)
                        if analysis_msg:
                            send_message_md2(__TOKEN, chat_id, analysis_msg)

                        sym_name = symbol.replace("/", "_")
                        image_paths = [
                            f'resource/{sym_name}_{ohlc_type}.png',
                            f'resource/{sym_name}_trend_signals.png',
                            f'resource/{sym_name}_momentum_signals.png',
                            f'resource/{sym_name}_volatility_signals.png',
                            f'resource/{sym_name}_volume_signals.png'
                        ]
                        # 혹시 에러로 생성되지 않은 이미지가 있을 수 있으니 실제 존재하는 파일만 필터링
                        valid_images = [p for p in image_paths if os.path.exists(p)]
                        if valid_images:
                            send_media_group(__TOKEN, chat_id, valid_images)
                    # raw_data = await fetch_all_timeframes(chat_id,exchange_id,symbol)
                    # print('-------------------------------- Fetched Data --------------------------------')
                    # for tf, data in raw_data.items():
                    #     print(tf,data.__len__())
                except Exception as loop_e:
                    print(f"❌ 분석 루프 내러 에러 발생: {loop_e}")
                await asyncio.sleep(interval)
        else:
            print(f"❌ 필수 설정이 누락되었습니다. (현재 설정: {settings})")
    except asyncio.CancelledError:
        print("🛑 Myramid stopped gracefully.")
    except Exception as e:
        # 👉 백그라운드 태스크가 알 수 없는 이유로 죽을 때 로그를 남김
        print(f"🔥 백그라운드 태스크 치명적 오류: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE)->None:
    user_id = update.effective_user.id
    settings = get_user_settings(user_id)
    chat_id = update.effective_chat.id
    settings['chat_id'] = chat_id
    update_user_settings(user_id, settings)
    # print(f"🔄 Your User id: {user_id} / chat_id: {chat_id}")
    # path:str = os.path.join('resource', 'myramid(2).png')
    # send_telegram_photo(__TOKEN,chat_id,path,"Myramid started.")
    # await context.bot.send_message(chat_id=chat_id, text=f"🔄 Your User id: {user_id} / chat_id: {chat_id}")
    # 🙋‍♂️ 인사말 추가 부분
    greeting_msg = (
        "🙋‍♂️안녕하세요! 🤖 암호화폐 기술적 분석 봇, Myra입니다.\n"
        "원하시는 거래소, 코인, 타임프레임을 설정하고 분석 알림을 받아보세요!"
    )
    reply_keyboard = [
        ['/menu', '/subscribe'],
        ['/unsubscribe', '/help']
    ]
    # resize_keyboard=True 로 설정해야 버튼이 화면의 절반을 가리지 않고 예쁘게 작아집니다.
    persistent_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    # 인사말을 보낼 때 고정 키보드를 함께 부착합니다.
    await context.bot.send_message(chat_id=chat_id, text=greeting_msg, reply_markup=persistent_markup)

    keyboard = MAIN_KEYBOARD
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("Main Menu:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Main Menu:", reply_markup=reply_markup)

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global periodic_task_handle
    user_id = update.effective_user.id
    settings: dict = get_user_settings(user_id)

    if periodic_task_handle is None or periodic_task_handle.done():
        periodic_task_handle = asyncio.create_task(periodic_task(settings))
        response = "✅ Subscribe started."
    else:
        response = "⚠️ Subscribe is already running."
    # Send response to the correct message object
    if update.message:
        await update.message.reply_text(response)
    elif update.callback_query:
        await update.callback_query.message.reply_text(response)

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global periodic_task_handle
    if periodic_task_handle and not periodic_task_handle.done():
        periodic_task_handle.cancel()
        response = "🛑 Myramid stopped."
    else:
        response = "⚠️ Myramid is not running."
    if update.message:
        await update.message.reply_text(response)
    elif update.callback_query:
        await update.callback_query.message.reply_text(response)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_html = (
        "<b>❓ Myra 봇 도움말</b>\n\n"
        "이 봇은 암호화폐 거래소의 데이터를 실시간으로 분석하여 기술적 지표와 매매 시그널을 제공합니다.\n\n"
        "<b>📌 주요 명령어</b>\n"
        "• /menu : 거래소, 코인, 알람 주기 등 설정을 변경합니다.\n"
        "• /subscribe : 실시간 분석 구독을 시작합니다.\n"
        "• /unsubscribe : 구독을 중지합니다.\n"
        "• /start : 봇 초기화 및 고정 메뉴를 호출합니다.\n\n"
        "<b>📊 분석 알림 정보</b>\n"
        "• 설정한 시간(예: 15분)마다 텍스트 요약과 차트 앨범을 전송합니다.\n"
        "• <b>Heikin Ashi</b>와 <b>Composite RSI</b> 등 고급 지표가 포함되어 있습니다.\n"
        "• 지표 계산 및 이미지 생성 시 약 5~10초의 시간이 소요될 수 있습니다."
    )

    if update.message:
        await update.message.reply_text(help_html, parse_mode=constants.ParseMode.HTML)
    elif update.callback_query:
        await update.callback_query.message.reply_text(help_html, parse_mode=constants.ParseMode.HTML)

# Setup bot
def main():
    app = Application.builder().token(__TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    app.add_handler(CallbackQueryHandler(menu_handler,
        pattern=r"^alarm_|^symbol_|^exchange_|^timeframe_|^ohlc_|^menu_"))
    app.run_polling()

if __name__ == "__main__":
    main()
