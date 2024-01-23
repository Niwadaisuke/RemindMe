from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from sqlalchemy import create_engine, Table, MetaData, select, text
import telegram as t
import time
import configparser
import psycopg2
import asyncio

async def warning(_msg):
    await bot.send_message(chat_id=Chatid, text=_msg)

# Define a command handler to handle the /edit command
def edit(update, context):
    # Create the inline keyboard
    keyboard = [
        [InlineKeyboardButton("查詢日期及事件", callback_data='SearchData')],
        [InlineKeyboardButton("添加日期及事件", callback_data='AddData')],
        [InlineKeyboardButton("刪除日期及事件", callback_data='DelData')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with the inline keyboard
    update.message.reply_text('請問有什麼能為您服務的嗎？', reply_markup=reply_markup)

# Define a callback function to handle button presses
def button(update, context):
    query = update.callback_query
    query.answer(text='服務處理中')

    # Handle each button according to its data
    if query.data == 'SearchData':
        query.edit_message_text(text="查詢成功")
    elif query.data == 'AddData':
        query.edit_message_text(text="添加成功")
    elif query.data == 'DelData':
        query.edit_message_text(text="刪除成功")


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    # telegram_bot
    telegram_bot_token = config.get('Telegram', 'Access_token')
    bot = t.Bot(telegram_bot_token)
    Chatid = config.get('ChatId', 'Chat_id')

    #connect database
    db_url = config.get('Postgresql', 'Database_URL')

    # 創建一個 SQLAlchemy 引擎
    engine = create_engine(db_url)

    # 定義元數據，這裡的表結構應該與你的實際數據庫表一致
    metadata = MetaData()

    # 替換 'your_table' 為你的實際表名
    bill_data = Table('bill_data', metadata, autoload_with=engine)

    # 建立一個連接
    with engine.connect() as connection:

        # 定義條件：比對 column1 的數字
        condition = 20  # 這裡用你要比對的數字替換

        # 使用 SQLalchemy 的 select 函數來構建 SQL 查詢
        stmt = select(bill_data.c.bill_name).where(bill_data.c.day == condition)

        # 執行 SQL 查詢
        result = connection.execute(stmt)

        # 獲取查詢結果
        for row in result:
            print(row.bill_name)


    setting_time = {'01': '信用卡費', '05': '瓦斯費', '23': '管理費', '12': '測試1號', '13': '測試2號'}
    
    #telegram send messaage
    print(time.strftime("%d", time.localtime()))
    for d in setting_time.keys():
        if d == time.strftime("%d", time.localtime()):
            msg = "今天要繳" + setting_time[d] + "喔"
            asyncio.run(warning(msg))
            print("message sent")
        print("d="+d)

    # Create an instance of the Updater class and add handlers
    updater = Updater(telegram_bot_token)
    updater.dispatcher.add_handler(CommandHandler('edit', edit))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    # Start the bot
    updater.start_polling()
    updater.idle()
