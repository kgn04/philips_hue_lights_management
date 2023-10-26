from sqlite3 import connect, OperationalError

attributes: dict[str, str] = {
    'Huby': '(AdresMAC, AdresIP, LoginH, Rzedy, Kolumny)',
    'Uzytkownicy': '(Email, Username, Haslo)',
    'Przydzielenia': '(Email, AdresMAC)',
    'Kasetony': '(IdK, Rzad, Kolumna, CzyWlaczony, Jasnosc, Czerwony, Zielony, Niebieski, AdresMAC)',
    'Grupy': '(IdGr, NazwaGr)',
    'Przypisania': '(IdGr, IdK)'
}


def connect_to_db() -> tuple:
    connection = connect('../database/alpha.db')
    return connection, connection.cursor()


def disconnect_from_db(connection, cursor) -> None:
    connection.commit()
    cursor.close()
    connection.close()


def run_sql_script(script_name) -> None:
    connection, cursor = connect_to_db()
    with open(f'../database/sql_scripts/{script_name}.sql', 'r') as sql_file:
        cursor.executescript(sql_file.read())
    disconnect_from_db(connection, cursor)


def init_db() -> None:
    try:
        run_sql_script('init')
    except OperationalError:
        print("Baza danych już istnieje. Nie podjęto inicjalizacji.")


def select(table_name: str, name_of_attribute_to_select: str, where_attribute: tuple) -> list:
    connection, cursor = connect_to_db()
    parsed_where_value = parse_to_sql(where_attribute[1])
    cursor.execute(f"SELECT {name_of_attribute_to_select} FROM {table_name} WHERE {where_attribute[0]} = {parsed_where_value};")
    disconnect_from_db(connection, cursor)
    return [tup[0] for tup in cursor.fetchall()]


def insert(table_name: str, tuple_to_insert: tuple):
    connection, cursor = connect_to_db()
    cursor.execute(f"INSERT INTO {table_name} {attributes[table_name]} VALUES {tuple_to_insert};")
    disconnect_from_db(connection, cursor)


def delete(table_name: str, where_attribute: tuple):
    parsed_where_value = parse_to_sql(where_attribute[1])
    connection, cursor = connect_to_db()
    if table_name == 'Huby':
        cursor.execute(f"SELECT AdresMAC FROM Huby WHERE {where_attribute[0]} = {parsed_where_value};")
        mac_address = cursor.fetchone()[0]
        delete('Kasetony', ('AdresMAC', mac_address))
        delete('Przydzielenia', ('AdresMAC', mac_address))
    elif table_name == 'Kasetony':
        cursor.execute(f"SELECT IdK FROM Kasetony WHERE {where_attribute[0]} = {parsed_where_value};")
        try:
            IdK = cursor.fetchone()[0]
            delete('Przypisania', ('IdK', IdK))
        except TypeError:
            pass
    elif table_name == 'Grupy':
        cursor.execute(f"SELECT IdGr FROM Grupy WHERE {where_attribute[0]} = {parsed_where_value};")
        try:
            IdGr = cursor.fetchone()[0]
            delete('Przypisania', ('IdGr', IdGr))
        except TypeError:
            pass
    elif table_name == 'Uzytkownicy':
        try:
            cursor.execute(f"SELECT Email FROM Uzytkownicy WHERE {where_attribute[0]} = {parsed_where_value};")
            email = cursor.fetchone()[0]
            delete('Przydzielenia', ('Email', email))
        except TypeError:
            pass
    cursor.execute(f"DELETE FROM {table_name} WHERE {where_attribute[0]} = {parsed_where_value};")
    disconnect_from_db(connection, cursor)


def update(table_name: str, set_attribute: tuple, where_attribute: tuple):
    connection, cursor = connect_to_db()
    parsed_set_value = parse_to_sql(set_attribute[1])
    parsed_where_value = parse_to_sql(where_attribute[1])
    cursor.execute(f"UPDATE {table_name} SET {set_attribute[0]} = {parsed_set_value}"
                   f" WHERE {where_attribute[0]} = {parsed_where_value};")
    disconnect_from_db(connection, cursor)


def parse_to_sql(value):
    return f"'{value}'" if (type(value) == str and value != 'null') else value


def insert_example():
    run_sql_script('insert_example')


def print_db():
    connection, cursor = connect_to_db()
    for table_name in ['Huby', 'Uzytkownicy', 'Przydzielenia', 'Kasetony', 'Grupy', 'Przypisania']:
        print('- - - - - - - - - - - - - - - - -')
        print(table_name)
        cursor.execute(f"SELECT * FROM {table_name};")
        for row in cursor.fetchall():
            print(row)
    disconnect_from_db(connection, cursor)


if __name__ == '__main__':
    # init_db()
    # insert_example()
    # insert('Kasetony', (4, 2, 1, 64, 64, 64, 196, '00:11:22:33:44:55'))
    # update('Uzytkownicy', ('Haslo', 'NewPassword'), ('Email', 'user3@example.com'))
    # update('Uzytkownicy', ('AdresMAC', 'AA:BB:CC:DD:EE:FF'), ('LoginU', 'User3'))
    # delete('Huby', ('AdresIP', '192.168.1.2'))
    # delete('Uzytkownicy', ('Username', 'User1'))
    # delete('Kasetony', ('IdK', 2))
    # print(select('Uzytkownicy', 'AdresMAC', ('Haslo', 'NewPassword')))
    print_db()
