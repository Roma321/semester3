import psycopg2
import stanza

# Инициализация Stanza
stanza.download('ru')  # Загрузка модели для русского языка
nlp = stanza.Pipeline('ru')

# Подключение к базе данных
conn = psycopg2.connect(dbname='prepositions', user='postgres', password='postgres', host='localhost')
cursor = conn.cursor()
conn.autocommit = True
# Выборка всех записей из таблицы
cursor.execute("SELECT id, main_word FROM public.phrases")
rows = cursor.fetchall()

batch_size = 10  # Размер батча
batch_update = []

for i, row in enumerate(rows):
    id, main_word = row
    print(id, main_word)
    # Применение Stanza для определения части речи
    doc = nlp(main_word)
    # print(doc)
    # Получение части речи
    part_of_speech = doc.sentences[0].words[0].upos if doc.sentences else None

    # Подготовка данных для пакетного обновления
    batch_update.append((part_of_speech, id))
    # print(batch_update)
    # Когда достигнут размер батча, выполняем обновление
    if len(batch_update) >= batch_size:
        cursor.executemany("UPDATE public.phrases SET main_part_of_speech = %s WHERE id = %s", batch_update)
        batch_update = []  # Сбрасываем батч

# Обновляем оставшиеся строки, если есть
if batch_update:
    cursor.executemany("UPDATE public.phrases SET main_part_of_speech = %s WHERE id = %s", batch_update)

# Сохранение изменений и закрытие соединения
conn.commit()
cursor.close()
conn.close()
