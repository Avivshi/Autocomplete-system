import sqlite3


def create_db():
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    create_table = "CREATE TABLE IF NOT EXISTS options (prefix text, count INTEGER, is_word Bool)"
    cursor.execute(create_table)

    connection.commit()
    connection.close()
