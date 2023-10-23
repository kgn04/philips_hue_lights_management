from sqlite3 import connect, OperationalError

attributes: dict[str, str] = {
    'Huby': '(AdresMAC, AdresIP, LoginH)',
    'Uzytkownicy': '(Email, LoginU, Haslo, AdresMAC)',
    'Kasetony': '(IdK, Rzad, Kolumna, Jasnosc, Czerwony, Zielony, Niebieski, AdresMAC)',
    'Grupy': '(IdGr, NazwaGr)',
    'Przypisania': '(IdGr, IdK)'
}


def run_sql_script(script_name):
    with open(f'database/sql_scripts/{script_name}.sql', 'r') as sql_file:
        cursor.executescript(sql_file.read())


def init_db():
    try:
        run_sql_script('init')
    except OperationalError:
        print("Baza danych już istnieje. Nie podjęto inicjalizacji.")


def insert(table_name: str, tuple_to_insert: tuple):
    cursor.execute(f"INSERT INTO {table_name} {attributes[table_name]} VALUES {tuple_to_insert};")


def delete(table_name: str, where_attribute: tuple):
    parsed_where_value = parse_to_sql(where_attribute[1])
    if table_name == 'Huby':
        cursor.execute(f"SELECT AdresMAC FROM Huby WHERE {where_attribute[0]} = {parsed_where_value};")
        mac_address = cursor.fetchone()[0]
        delete('Kasetony', ('AdresMAC', mac_address))
        update('Uzytkownicy', ('AdresMAC', 'null'), ('AdresMAC', mac_address))
    elif table_name == 'Kasetony':
        cursor.execute(f"SELECT IdK FROM Kasetony WHERE {where_attribute[0]} = {parsed_where_value};")
        IdK = cursor.fetchone()[0]
        delete('Przypisania', ('IdK', IdK))
    elif table_name == 'Grupy':
        cursor.execute(f"SELECT IdGr FROM Grupy WHERE {where_attribute[0]} = {parsed_where_value};")
        IdGr = cursor.fetchone()[0]
        delete('Przypisania', ('IdGr', IdGr))
    cursor.execute(f"DELETE FROM {table_name} WHERE {where_attribute[0]} = {parsed_where_value};")


def update(table_name: str, set_attribute: tuple, where_attribute: tuple):
    parsed_set_value = parse_to_sql(set_attribute[1])
    parsed_where_value = parse_to_sql(where_attribute[1])
    cursor.execute(f"UPDATE {table_name} SET {set_attribute[0]} = {parsed_set_value}"
                   f" WHERE {where_attribute[0]} = {parsed_where_value};")


def parse_to_sql(value):
    return f"'{value}'" if (type(value) == str and value != 'null') else value


def insert_example():
    run_sql_script('insert_example')


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

    # init_db()
    # insert_example()
    # insert('Kasetony', (4, 'D', '3', '100%', 0, 128, 255, '12:34:56:78:90:AB'))
    # update('Uzytkownicy', ('Haslo', 'NewPassword'), ('LoginU', 'User2'))
    # delete('Huby', ('AdresIP', '192.168.1.2'))
    # delete('Kasetony', ('IdK', '2'))
    print_db()

    connection.commit()
    cursor.close()
    connection.close()
