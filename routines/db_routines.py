from google_sheets_parser.google_sheets_parser import GSheetsParser
from routines.dataframe_routines import pretty_dataframe
import pandas as pd
import sqlite3


def initialize_db():
    connection = sqlite3.connect('../mch_bot/database.db')
    cursor = connection.cursor()

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT UNIQUE
            )
        ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                link TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            campaign_name TEXT UNIQUE,
            drug_name TEXT,
            medic_group TEXT,
            adv_format TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            date TEXT,
            impressions INTEGER,
            clicks INTEGER,
            click_rate REAL,
            campaign_number INTEGER,
            rolled_3 REAL,
            rolled_5 REAL,
            rolled_7 REAL,
            trend TEXT,
            moving_average_change REAL,
            day INTEGER,
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
        )
    ''')

    add_history_data_to_db(cursor)

    connection.commit()
    cursor.close()
    connection.close()


def add_user(chat_id):
    connection = sqlite3.connect('../mch_bot/database.db')
    cursor = connection.cursor()

    cursor.execute('INSERT OR IGNORE INTO users (chat_id) VALUES (?)', (chat_id,))

    connection.commit()
    cursor.close()
    connection.close()


def add_timeseries_source_table(chat_id, link):
    connection = sqlite3.connect('../mch_bot/database.db')
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM users WHERE chat_id = ?', (chat_id,))
    user_id = cursor.fetchone()[0]

    cursor.execute('INSERT OR IGNORE INTO links (user_id, link) VALUES (?, ?)', (user_id, link))

    connection.commit()
    cursor.close()
    connection.close()


def delete_timeseries_source_table(chat_id, link):
    connection = sqlite3.connect('../mch_bot/database.db')
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM users WHERE chat_id = ?', (chat_id,))
    user_id = cursor.fetchone()[0]

    cursor.execute('DELETE FROM links WHERE user_id = ? AND link = ?', (user_id, link))

    connection.commit()
    cursor.close()
    connection.close()


def get_unique_links_with_chat_ids():
    connection = sqlite3.connect('../mch_bot/database.db')
    cursor = connection.cursor()

    cursor.execute('''
            SELECT DISTINCT chat_id, link 
            FROM links 
            JOIN users 
            WHERE users.id == links.user_id
        ''')
    links_with_ids = cursor.fetchall()

    connection.commit()
    cursor.close()
    connection.close()

    return links_with_ids


def get_saved_links(chat_id):
    connection = sqlite3.connect('../mch_bot/database.db')
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM users WHERE chat_id = ?', (chat_id,))
    user_id = cursor.fetchone()[0]

    cursor.execute('SELECT link FROM links WHERE user_id = ?', (user_id,))
    links = [row[0] for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return links


def get_history_data_sheet_link():
    sheet_link_file = open('../tokens/history_data_sheet_link', 'r')
    sheet_link = sheet_link_file.read()
    sheet_link_file.close()
    return sheet_link


def is_table_empty(table_name):
    connection = sqlite3.connect('../mch_bot/database.db')
    cursor = connection.cursor()

    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result[0] == 0


def convert_timestamp_to_string(timestamp):
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')


def add_history_data_to_db(cursor):
    if is_table_empty('campaigns') or is_table_empty('metrics'):
        parser = GSheetsParser(get_history_data_sheet_link())
        history_timeseries = pretty_dataframe(pd.DataFrame(parser.parse()))

        for index, row in history_timeseries.iterrows():
            campaign_data = (row['campaign_name'], row['drug_name'], row['medic_group'], row['adv_format'])
            cursor.execute(
                "INSERT OR IGNORE INTO campaigns (campaign_name, drug_name, medic_group, adv_format) VALUES (?, ?, ?, ?)",
                campaign_data)

            cursor.execute("SELECT id FROM campaigns WHERE campaign_name = ?", (row['campaign_name'],))
            campaign_id = cursor.fetchone()[0]

            metrics_data = (
                campaign_id, convert_timestamp_to_string(row['date']), row['impressions'], row['clicks'],
                row['click_rate'], row['campaign_number'],
                row['rolled_3'], row['rolled_5'], row['rolled_7'], row['trend'], row['moving_average_change'], row['day'])
            cursor.execute(
                "INSERT OR IGNORE INTO metrics (campaign_id, date, impressions, clicks, click_rate, campaign_number, rolled_3, rolled_5, rolled_7, trend, moving_average_change, day) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                metrics_data)


def select_campaign_metrics(drug_name=None, medic_group=None, adv_format=None):
    connection = sqlite3.connect('../mch_bot/database.db')
    cursor = connection.cursor()

    query = """
            SELECT campaigns.campaign_name, metrics.date, metrics.impressions, metrics.clicks, metrics.click_rate, campaigns.drug_name, campaigns.medic_group, campaigns.adv_format, metrics.campaign_number, metrics.rolled_3, metrics.rolled_5, metrics.rolled_7, metrics.trend, metrics.moving_average_change, metrics.day
            FROM campaigns
            INNER JOIN metrics ON campaigns.id = metrics.campaign_id
        """

    conditions = []
    if drug_name is not None:
        conditions.append("campaigns.drug_name = ?")
    if medic_group is not None:
        conditions.append("campaigns.medic_group = ?")
    if adv_format is not None:
        conditions.append("campaigns.adv_format = ?")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    params = [param for param in [drug_name, medic_group, adv_format] if param is not None]
    cursor.execute(query, params)
    rows = cursor.fetchall()

    dataframe = pd.DataFrame(rows, columns=['campaign_name', 'date', 'impressions', 'clicks', 'click_rate', 'drug_name',
                                            'medic_group', 'adv_format', 'campaign_number', 'rolled_3', 'rolled_5',
                                            'rolled_7',
                                            'trend', 'moving_average_change', 'day'])
    dataframe['date'] = pd.to_datetime(dataframe['date'])

    cursor.close()
    connection.close()

    return dataframe
