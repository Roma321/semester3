import psycopg2

from parsing import process_text

conn = psycopg2.connect(dbname='prepositions', user='postgres',
                        password='postgres', host='localhost')
conn.autocommit = True
cursor = conn.cursor()

def same_by_words_and_prep(main_lemma, dep_lemma, preposition):
    query = f"select * from phrases where main_word = %s AND dep_word = %s AND preposition = %s;"
    cursor.execute(query,(main_lemma, dep_lemma,preposition))
    return cursor.fetchall()


def get_prep_percentage_full(prep):
    query = """SELECT 
    (COUNT(*) FILTER (WHERE preposition = %s) * 100.0 / COUNT(*)) AS percentage
FROM 
    public.phrases;"""
    cursor.execute(query, (prep,))
    data = cursor.fetchone()
    return float(data[0])

def get_prep_percentage_for_dep_lemma(prep, dep_lemma):
    query = """SELECT 
        (COUNT(*) FILTER (WHERE preposition = %s) * 100.0 / COUNT(*)) AS percentage
    FROM 
        public.phrases where dep_lemma = %s;"""
    cursor.execute(query, (prep,dep_lemma))
    data = cursor.fetchone()
    return float(data[0])


def is_prep_not_common_for_dep_lemma(prep, dep_lemma):
    prep_percentage_all = get_prep_percentage_full(prep)
    prep_percentage_for_dep_lemma = get_prep_percentage_for_dep_lemma(prep, dep_lemma)
    return prep_percentage_for_dep_lemma * 3 < prep_percentage_all


def get_prep_percentage_for_main_lemma(prep, main_lemma):
    query = """SELECT 
        (COUNT(*) FILTER (WHERE preposition = %s) * 100.0 / COUNT(*)) AS percentage
    FROM 
        public.phrases where main_lemma = %s;"""
    cursor.execute(query, (prep, main_lemma))
    data = cursor.fetchone()
    return float(data[0])


def is_prep_not_common_for_main_lemma(prep, main_lemma):
    prep_percentage_all = get_prep_percentage_full(prep)
    prep_percentage_for_main_lemma = get_prep_percentage_for_main_lemma(prep, main_lemma)
    return prep_percentage_for_main_lemma * 3 < prep_percentage_all

def is_prep_not_common_for_case(prep, case):
    prep_percentage_all = get_prep_percentage_full(prep)
    prep_percentage_for_case = get_prep_percentage_for_case(prep, case)
    return prep_percentage_for_case * 3 < prep_percentage_all

def get_prep_percentage_for_case(prep, case):
    query = """SELECT 
        (COUNT(*) FILTER (WHERE preposition = %s) * 100.0 / COUNT(*)) AS percentage
    FROM 
        public.phrases where dep_case = %s;"""
    cursor.execute(query, (prep, case))
    data = cursor.fetchone()
    return float(data[0])

def get_case_percentage_for_prep(prep, case):
    query = """SELECT 
        (COUNT(*) FILTER (WHERE dep_case = %s) * 100.0 / COUNT(*)) AS percentage
    FROM 
        public.phrases where preposition = %s;"""
    cursor.execute(query, (case, prep))
    data = cursor.fetchone()
    return float(data[0])

def looks_correct(phrase):
    main_lemma = phrase[1]
    main_word = phrase[0]
    dep_lemma = phrase[4]
    dep_word = phrase[3]
    preposition = phrase[2]
    case = phrase[5]
    same_in_corpus_arr = same_by_words_and_prep(main_word, dep_word, preposition)

    if len(same_in_corpus_arr) > 1:
        return True

    if is_prep_not_common_for_case(preposition, case):
        return False

    if is_prep_not_common_for_dep_lemma(preposition, dep_lemma):
        return False

    if is_prep_not_common_for_main_lemma(preposition, main_lemma):
        return False

    return True

txt = '''Ю́жный по́люс Земли — точка пересечения оси вращения Земли c её поверхностью в Южном полушарии[1]. Находится в пределах Полярного плато Антарктиды в высоте 2800 м[2]. Южный полюс не следует путать через Южным магнитным полюсом[3].

Южный полюс диаметрально противоположен Северному полюсу, расположенному в Северном Ледовитом океане. Любая другая точка поверхности Земли находится всегда от северном направлении по отношению к Южному полюсу[2]. Географические координаты Южного полюса 90°00′00″ южной широты. Долготы полюс не имеет, так как является точкой схождения всех меридианов. День, как и ночь, здесь продолжается приблизительно по полгода[4].

Толщина льда в районе Южного полюса — 2810 метров[5]. Среднегодовая температура воздуха составляет −48,9 °C (максимальная −12,3 °C, минимальная −82,8 °C).

В декабре 1911 Южного полюса достигла норвежская экспедиция под руководством Руаля Амундсена, включавшая также Олафа Бьоланда, Сверре Хасселя, Хельмера Хансена и Оскара Вистинга, в январе 1912 года — английская экспедиция Роберта Скотта. В 1929 году американец Р. Бэрд первым пролетел на самолёте над Южным полюсом[3]. В 1958 году британско-новозеландская экспедиция В. Фукса и Э. Хиллари осуществила первый трансантарктический санно-гусеничный поход от моря Уэддела через Южный полюс к морю Росса.

С 1957 года на Южном полюсе действует научная станция США Амундсен-Скотт, но из-за движения льдов в 2006 году станция находилась примерно в 100 метрах от полюса. Подо льдами Южного полюса работает детектор высокоэнергичных нейтрино IceCube, использующий в качестве мишени и черенковского радиатора 1 кубический километр прозрачного льда на глубине от 1450 до 2460 м.'''
processed_phrases = process_text(txt)
for phrase in processed_phrases:
    print(phrase, looks_correct(phrase))

