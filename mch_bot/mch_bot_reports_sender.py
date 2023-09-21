import telebot
import schedule
import time

from routines.db_routines import get_unique_links_with_chat_ids
from routines.reports_routines import send_report


def get_bot_token():
    token_file = open('../tokens/mch_bot_token', 'r')
    token = token_file.read()
    token_file.close()
    return token


bot = telebot.TeleBot(get_bot_token())


def send_all_reports():
    unique_links_with_chat_ids = get_unique_links_with_chat_ids()
    for current_link_and_chat_id in unique_links_with_chat_ids:
        send_report(bot, current_link_and_chat_id[0], current_link_and_chat_id[1])


schedule.every(24).hours.do(send_all_reports)

while True:
    schedule.run_pending()
    time.sleep(1)
