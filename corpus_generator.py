import re
import string

import pandas as pd
import os

import psycopg2


def parse_column_to_dir(file_path, output_directory, col_num):
    df = pd.read_excel(file_path)

    if df.shape[1] < col_num:
        raise ValueError(f"Файл должен содержать как минимум {col_num} столбцов.")

    ninth_column = df.iloc[:, col_num - 1]

    os.makedirs(output_directory, exist_ok=True)

    for index, value in enumerate(ninth_column):
        file_name = os.path.join(output_directory, f'{index + 1}.txt')
        with open(file_name, 'w') as f:
            # разметка пока не нужна
            f.write(str(value).replace("*",""))
    print(index)


def clean_text(text):
    # Remove any non-printable characters and return cleaned text
    return re.sub(r'[^\w\s,.!?\'"а-яА-ЯёЁ]', '', text)


def generate_correct_ones(output_directory):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(dbname='prepositions', user='postgres', password='postgres', host='localhost')
    cursor = conn.cursor()

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Query to select distinct contexts
    query = "SELECT DISTINCT context FROM public.phrases WHERE LENGTH(context) > 100 LIMIT 103701"
    cursor.execute(query)

    # Fetch all results
    data = cursor.fetchall()

    # Iterate over fetched data and save each context to a file
    for idx, (context,) in enumerate(data):
        cleaned_context = clean_text(context)
        file_path = os.path.join(output_directory, f"{idx + 1}.txt")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_context)

    # Close the cursor and connection
    cursor.close()
    conn.close()
parse_column_to_dir('errors.xlsx', 'correct', 10)
# generate_correct_ones('correct_parsed')
