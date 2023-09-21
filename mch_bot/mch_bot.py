import telebot
import re

from routines.db_routines import initialize_db, add_user, add_timeseries_source_table, delete_timeseries_source_table, \
    get_saved_links
from routines.reports_routines import send_report
from google_sheets_parser.google_sheets_parser import GSheetsParser

initialize_db()


def get_bot_token():
    token_file = open('../tokens/mch_bot_token', 'r')
    token = token_file.read()
    token_file.close()
    return token


bot = telebot.TeleBot(get_bot_token())


def create_keyboard_with_links_to_delete(links):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

    for link in links:
        keyboard.add(telebot.types.KeyboardButton(link))

    return keyboard


def create_keyboard_with_commands():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

    keyboard.add(telebot.types.KeyboardButton('/save_link'))
    keyboard.add(telebot.types.KeyboardButton('/delete_link'))
    keyboard.add(telebot.types.KeyboardButton('/get_reports'))

    return keyboard


def validate_link(link):
    pattern = r'^https:\/\/docs\.google\.com\/spreadsheets\/d\/[a-zA-Z0-9-_]'
    if re.match(pattern, link):
        parser = GSheetsParser(link)
        return parser.validate_user_table_link()
    else:
        return False


# noinspection SpellCheckingInspection
@bot.message_handler(commands=['start'])
def handle_start(message):
    add_user(message.chat.id)
    description = "Салют! ID вашего чата был записан для дальнейшей отправки отчётов. Вам доступны следующие команды для взаимодействия с ботом:\n\n"
    description += "/save_link - Добавить ссылку на источник данных Google Sheets для формирования отчётов.\n"
    description += "/delete_link - Удалить ссылку из списка отслеживаемых.\n"
    description += "/get_reports - Получить отчёты прямо сейчас.\n\n"
    description += "Все отчёты отправляются автоматически раз в 24 часа."
    bot.reply_to(message, description, reply_markup=create_keyboard_with_commands())


# noinspection SpellCheckingInspection
@bot.message_handler(commands=['save_link'])
def handle_save_link(message):
    bot.reply_to(message, "Укажите ссылку на источник данных:\n\nВажно! Таблица должна содержать следующие колонки:\n'platform', 'campaign_id', 'campaign_name', 'date', 'impressions', 'clicks'", reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, save_link_step)


# noinspection SpellCheckingInspection
def save_link_step(message):
    link = message.text
    if not validate_link(link):
        bot.reply_to(message, 'Предоставленна неверная ссылка, она не была сохранена.', reply_markup=create_keyboard_with_commands())
    else:
        add_timeseries_source_table(message.chat.id, link)
        bot.reply_to(message, 'Ссылка была успешно сохранена.', reply_markup=create_keyboard_with_commands())


# noinspection SpellCheckingInspection
@bot.message_handler(commands=['delete_link'])
def handle_delete_link(message):
    links = get_saved_links(message.chat.id)
    if not links:
        bot.reply_to(message, 'Нет ссылок для удаления.', reply_markup=create_keyboard_with_commands())
    else:
        bot.reply_to(message, 'Выберите ссылку для удаления:', reply_markup=create_keyboard_with_links_to_delete(links))
        bot.register_next_step_handler(message, delete_link_step)


# noinspection SpellCheckingInspection
def delete_link_step(message):
    link = message.text
    delete_timeseries_source_table(message.chat.id, link)
    bot.reply_to(message, 'Ссылка была успешно удалена.', reply_markup=create_keyboard_with_commands())


# noinspection SpellCheckingInspection
@bot.message_handler(commands=['get_reports'])
def handle_get_reports(message):
    links = get_saved_links(message.chat.id)
    if not links:
        bot.reply_to(message, 'Нет ссылок для формирования отчётов.', reply_markup=create_keyboard_with_commands())
    else:
        for current_link in links:
            send_report(bot, message.chat.id, current_link, validation=True)


# noinspection SpellCheckingInspection
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, 'Я могу отвечать только на команды: /save_link и /delete_link.', reply_markup=create_keyboard_with_commands())


bot.polling(none_stop=True)
