import datetime

# Функция для конвертации в дату
def convert_timestamp_to_date(timestamp: float) -> str:
    return datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
