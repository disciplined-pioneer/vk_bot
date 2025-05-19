import fast_bitrix24

# Инициализация клиента Bitrix24 с вашим вебхуком
bitrix = fast_bitrix24.Bitrix('https://b24-n8nava.bitrix24.ru/rest/60/7ts1m4u7e3egpyrt/')

# Параметры для новой открытой линии
params = {
    "NAME": "Новая линия поддержки",  # Название линии
    "SORT": 100,  # Приоритет сортировки
    "ACTIVE": "Y",  # Линия активна
    "TYPE": "CHAT",  # Тип линии: чат, звонки, соцсети и т.д.
    "DESCRIPTION": "Линия для поддержки клиентов",  # Описание линии
    "CONFIG": {
        "WORK_TIME": {
            "ENABLE": "Y",  # Включить рабочее время
            "START": "09:00",  # Начало рабочего времени
            "END": "18:00",  # Конец рабочего времени
        },
    },
}

# Вызов API для создания линии
try:
    response = bitrix.call('imopenlines.line.add', params)
    if response and 'result' in response:
        print(f"Открытая линия успешно создана: {response['result']}")
    else:
        print(f"Ошибка при создании линии: {response}")
except Exception as e:
    print(f"Произошла ошибка: {e}")
