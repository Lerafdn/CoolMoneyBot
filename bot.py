import json

import telebot
from telebot import types

from yf_utils.yf_utils import TickerInfo

CONFIG_PATH = "bot_config.json"


if __name__ == "__main__":
    with open(CONFIG_PATH) as f:
        config = json.load(f)

    TOKEN = config["token"]

    START_MSG = """Привет, {}! 

    Я бот, который умеет собирать для тебя информацию о биржевых котировках! 📈🚀💸

    Если хочешь узнать, что я умею — отправь /help"""

    HELP_MSG = """
    Я могу выдавать информацию по интересующему тебя тикеру (например компания Apple имеет тикер AAPL).

    Тикеры других компаний и не только можно посмотреть на Yahoo Finance (https://finance.yahoo.com/most-active/)

    Чтобы начать работы с каким-либо тикером — отправь /put_ticker
    """

    bot = telebot.TeleBot(TOKEN)

    ticker = ""
    ti = None

    @bot.message_handler(content_types=["text"])
    def start(message):
        if message.text == "/start":
            bot.send_message(
                message.from_user.id, START_MSG.format(message.from_user.username)
            )
        elif message.text == "/help":
            bot.send_message(message.from_user.id, HELP_MSG)
        elif message.text == "/put_ticker":
            bot.send_message(
                message.from_user.id, "Введи код тикера, например AAPL или TSLA:"
            )
            bot.register_next_step_handler(message, get_ticker)
        else:
            bot.send_message(
                message.from_user.id,
                "Я тебя не понимаю 😞.\nНапиши /help для вызова справки",
            )

    def get_ticker(message):
        global ticker
        global ti

        ticker = str(message.text).strip().upper()
        ti = TickerInfo(ticker)
        ticker_info = ti.check_ticker()
        if ticker_info:
            bot.send_message(
                message.from_user.id,
                f"По запросу `{ticker}` нашел информацию о {ticker_info['longName']}",
            )
            get_ticker_actiion(message)
            # bot.register_next_step_handler(message, get_ticker_actiion)
        else:
            bot.send_message(
                message.from_user.id,
                f"По запросу `{ticker}` не удалось ничего найти.\nПопробуй другой тикер, просто введи /put_ticker",
            )

    def get_ticker_actiion(message):

        keyboard = types.InlineKeyboardMarkup()

        key_basic_info = types.InlineKeyboardButton(
            text="Базовая информация",
            callback_data="basic_info",
        )
        keyboard.add(key_basic_info)

        key_today_report = types.InlineKeyboardButton(
            text="Последняя сводка по торгам", callback_data="last_market_report"
        )
        keyboard.add(key_today_report)

        key_last_month_history = types.InlineKeyboardButton(
            text="Динамика цены за последний месяц", callback_data="last_month_history"
        )
        keyboard.add(key_last_month_history)

        key_last_6month_history = types.InlineKeyboardButton(
            text="Динамика цены за последниe 6 месяцев",
            callback_data="last_6month_history",
        )
        keyboard.add(key_last_6month_history)

        bot.send_message(
            message.from_user.id,
            f"Вот что я могу показать про {ticker}",
            reply_markup=keyboard,
        )

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        if call.data == "basic_info":
            s = ti.get_basic_info()
            bot.send_message(
                call.message.chat.id,
                "*Основные сведения* 🧰\n\n".upper() + s,
                parse_mode="Markdown",
            )
        elif call.data == "last_market_report":
            s = ti.get_fresh_report()
            bot.send_message(
                call.message.chat.id,
                "*Свежайшая информация о торгах* 📈\n\n".upper() + s,
                parse_mode="Markdown",
            )
        elif call.data == "last_month_history":
            ti.get_history_data({"days": 31})
            img = open(ti.img_path, "rb")
            bot.send_message(
                call.message.chat.id,
                f"Вот как торговались в последний месяц бумаги {ti.info['longName']} 🚀🚀🚀",
            )
            bot.send_photo(call.message.chat.id, img)
        elif call.data == "last_6month_history":
            ti.get_history_data({"days": 366 // 2})
            img = open(ti.img_path, "rb")
            bot.send_message(
                call.message.chat.id,
                f"Вот как торговались за последние полгода бумаги {ti.info['longName']} 🚀🚀🚀",
            )
            bot.send_photo(call.message.chat.id, img)

    bot.infinity_polling(timeout=10, long_polling_timeout=5)
