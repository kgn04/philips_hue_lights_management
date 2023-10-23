from sqlite3 import connect, OperationalError
from os.path import exists
from os import remove


def run_sql_script(script_name):
    with open(f'database/sql_scripts/{script_name}.sql', 'r') as sql_file:
        cursor.executescript(sql_file.read())


def init_db():
    try:
        run_sql_script('init')
    except OperationalError:
        print("Baza danych już istnieje. Nie podjęto inicjalizacji.")


def insert_example():
    run_sql_script('insert_example')


def delete_example():
    run_sql_script('delete_example')


def update_example():
    run_sql_script('update_example')


def print_db():
    for table_name in ['Huby', 'Uzytkownicy', 'Kasetony', 'Grupy', 'Przypisania']:
        print(table_name)
        cursor.execute(f"SELECT * FROM {table_name};")
        for row in cursor.fetchall():
            print(row)
        print('- - - - - - - - - - - - - - - - -')


if __name__ == '__main__':
    connection = connect('database/alpha.db')
    cursor = connection.cursor()

    # USE METHODS HERE
    init_db()
    insert_example()
    update_example()
    delete_example()
    print_db()

    connection.commit()
    cursor.close()
    connection.close()
