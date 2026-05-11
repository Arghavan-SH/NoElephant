from telegram import ReplyKeyboardMarkup, KeyboardButton

def build_keyboard(options: list[list[str]]) ->ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text) for text in row] for row in options]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )