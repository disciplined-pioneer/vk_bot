import datetime

# Функция для конвертации временной метки в читаемую дату.
def convert_timestamp_to_date(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
