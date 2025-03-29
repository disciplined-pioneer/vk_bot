import fast_bitrix24

# Пример задачи
tasks = {
    'fields': {
        "TITLE": "ЭТО ПРОСТО ПРОВЕРКА ( ТЕСТ ) 1",
        "UF_CRM_1742556368": "2025-03-26 12:00:00", 
        "UF_CRM_1742556254": "https://example.com/post",  
        "UF_CRM_1742556276": "123456",  
        "UF_CRM_1742556311": 10,  
        "UF_CRM_1742556333": "Цвет: Красный, Размер: M",  
        "UF_CRM_1726722554939": "Комментарий к сделке", 
        "STAGE_ID": "NEW",  
    }
}

# Создание объекта 
bit = fast_bitrix24.Bitrix('https://b24-n8nava.bitrix24.ru/rest/60/7ts1m4u7e3egpyrt/')

# Создание лида
#result = bit.call('crm.lead.add', tasks)
#print(result)

