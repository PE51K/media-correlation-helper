Данный репозиторий содержит исходный код для чат-бота:
https://t.me/MediaCorrelationHelperBot

Пример таблицы для обработки ботом: 
https://docs.google.com/spreadsheets/d/1eeOypc11bHbW188ICc17laMf_B73i87AQ9emz2wwvFo/edit#gid=168741310

Следующая инструкция по установке проверена на arch-linux:

1) ```console 
   git clone https://github.com/PE51K/ai_gp_hack_tg_bot
   cd ai_gp_hack_tg_bot
   pip install -r requirements.txt
   ```
2) ```console  
   mkdir tokens 
   ```
3) В папку tokens добавить:
   1) chat_gpt_token - файл, содержащий токен OpenAI API
   2) history_data_sheet_link - файл, содержащий ссылку на Google Sheet с исторической информацией по кампаниям с колонками вида: 'platform', 'campaign_id', 'campaign_name', 'date', 'impressions', 'clicks'
   3) mch_bot_token - файл, содержащий токен чат-бота Telegram
   4) credentials.json - файл, содержащий данные для доступа к API Google Sheets, как его получить - см. https://developers.google.com/sheets/api/quickstart/python?hl=ru
4) База данных и токен для доступа к Google Sheets API формируются автоматически
5) ```console 
   python *Полный путь к файлу*/mch_bot.py *Полный путь к файлу*/mch_bot_reports_sender.py
   ```

