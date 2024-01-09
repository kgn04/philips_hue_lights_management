from sqlite3 import connect, OperationalError, IntegrityError
import os
attributes: dict[str, str] = {
    'Huby': '(AdresMAC, AdresIP, LoginH, Nazwa, Rzedy, Kolumny)',
    'Uzytkownicy': '(Email, Username, Haslo, AdresMAC)',
    'Kasetony': '(IdK, Rzad, Kolumna, CzyWlaczony, Jasnosc, KolorR, KolorG, KolorB, AdresMAC)',
    'Grupy': '(IdGr, NazwaGr, CzyWlaczone, Jasnosc, KolorR, KolorG, KolorB, AdresMAC)',
    'Przypisania': '(IdGr, IdK, AdresMAC)'
}

DB_ABS_PATH = f'{os.path.join(os.path.dirname(__file__), "..")}/database'


def connect_to_db() -> tuple:
    global DB_ABS_PATH
    connection = connect(f'{DB_ABS_PATH}/alpha.db')
    return connection, connection.cursor()


def disconnect_from_db(connection, cursor) -> None:
    connection.commit()
    cursor.close()
    connection.close()


def run_sql_script(script_name) -> None:
    connection, cursor = connect_to_db()
    global DB_ABS_PATH
    with open(f'{DB_ABS_PATH}/sql_scripts/{script_name}.sql', 'r') as sql_file:
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
    cursor_result = cursor.fetchall()
    disconnect_from_db(connection, cursor)
    return [tup[0] for tup in cursor_result]


def select_with_two_conditions(table_name: str, name_of_attribute_to_select: str, where_attribute_1: tuple,
                               where_attribute_2: tuple) -> list:
    connection, cursor = connect_to_db()
    parsed_where_value_1 = parse_to_sql(where_attribute_1[1])
    parsed_where_value_2 = parse_to_sql(where_attribute_2[1])
    cursor.execute(f"SELECT {name_of_attribute_to_select} FROM {table_name} WHERE "
                   f"{where_attribute_1[0]} = {parsed_where_value_1} AND {where_attribute_2[0]} = {parsed_where_value_2};")
    cursor_result = cursor.fetchall()
    disconnect_from_db(connection, cursor)
    return [tup[0] for tup in cursor_result]


def select_all(table_name: str, name_of_attribute_to_select: str) -> list:
    connection, cursor = connect_to_db()
    cursor.execute(f"SELECT {name_of_attribute_to_select} FROM {table_name};")
    cursor_result = cursor.fetchall()
    disconnect_from_db(connection, cursor)
    return [tup[0] for tup in cursor_result]


def insert(table_name: str, tuple_to_insert: tuple):
    connection, cursor = connect_to_db()
    try:
        cursor.execute(f"INSERT INTO {table_name} {attributes[table_name]} VALUES {tuple_to_insert};")
    except IntegrityError:
        raise IntegrityError
    finally:
        disconnect_from_db(connection, cursor)


def delete(table_name: str, where_attribute: tuple):
    parsed_where_value = parse_to_sql(where_attribute[1])
    connection, cursor = connect_to_db()
    if table_name == 'Huby':
        for mac_address in select('Huby', 'AdresMAC', where_attribute):
            delete('Kasetony', ('AdresMAC', mac_address))
            delete('Grupy', ('AdresMAC', mac_address))
            delete('Przypisania', ('AdresMAC', mac_address))
            update('Uzytkownicy', ('AdresMAC', ''), ('AdresMAC', mac_address))
    elif table_name == 'Kasetony':
        for mac_address in select('Kasetony', 'AdresMAC', where_attribute):
            for light_id in select('Kasetony', 'IdK', where_attribute):
                delete_with_two_conditions('Przypisania', ('IdK', light_id), ('AdresMAC', mac_address))
    elif table_name == 'Grupy':
        for mac_address in select('Grupy', 'AdresMAC', where_attribute):
            for group_id in select('Grupy', 'IdGr', where_attribute):
                delete_with_two_conditions('Przypisania', ('IdGr', group_id), ('AdresMAC', mac_address))
    cursor.execute(f"DELETE FROM {table_name} WHERE {where_attribute[0]} = {parsed_where_value};")
    disconnect_from_db(connection, cursor)


def delete_with_two_conditions(table_name: str, where_attribute_1: tuple, where_attribute_2: tuple):
    parsed_where_value_1 = parse_to_sql(where_attribute_1[1])
    parsed_where_value_2 = parse_to_sql(where_attribute_2[1])
    connection, cursor = connect_to_db()
    if table_name == 'Huby':
        for mac_address in select_with_two_conditions('Huby', 'AdresMAC', where_attribute_1, where_attribute_2):
            delete('Kasetony', ('AdresMAC', mac_address))
            delete('Grupy', ('AdresMAC', mac_address))
            delete('Przypisania', ('AdresMAC', mac_address))
            update('Uzytkownicy', ('AdresMAC', ''), ('AdresMAC', mac_address))
    elif table_name == 'Kasetony':
        for mac_address in select_with_two_conditions('Kasetony', 'AdresMAC', where_attribute_1, where_attribute_2):
            for light_id in select_with_two_conditions('Kasetony', 'IdK', where_attribute_1, where_attribute_2):
                delete_with_two_conditions('Przypisania', ('IdK', light_id), ('AdresMAC', mac_address))
    elif table_name == 'Grupy':
        for mac_address in select_with_two_conditions('Grupy', 'AdresMAC', where_attribute_1, where_attribute_2):
            for group_id in select_with_two_conditions('Grupy', 'IdGr', where_attribute_1, where_attribute_2):
                delete_with_two_conditions('Przypisania', ('IdGr', group_id), ('AdresMAC', mac_address))
    cursor.execute(f"DELETE FROM {table_name} WHERE {where_attribute_1[0]} = {parsed_where_value_1} "
                   f"AND {where_attribute_2[0]} = {parsed_where_value_2};")
    disconnect_from_db(connection, cursor)


def update(table_name: str, set_attribute: tuple, where_attribute: tuple):
    connection, cursor = connect_to_db()
    parsed_set_value = parse_to_sql(set_attribute[1])
    parsed_where_value = parse_to_sql(where_attribute[1])
    cursor.execute(f"UPDATE {table_name} SET {set_attribute[0]} = {parsed_set_value}"
                   f" WHERE {where_attribute[0]} = {parsed_where_value};")
    disconnect_from_db(connection, cursor)


def update_with_two_conditions(table_name: str, set_attribute: tuple, where_attribute_1: tuple, where_attribute_2: tuple):
    connection, cursor = connect_to_db()
    parsed_set_value = parse_to_sql(set_attribute[1])
    parsed_where_value_1 = parse_to_sql(where_attribute_1[1])
    parsed_where_value_2 = parse_to_sql(where_attribute_2[1])
    cursor.execute(f"UPDATE {table_name} SET {set_attribute[0]} = {parsed_set_value}"
                   f" WHERE {where_attribute_1[0]} = {parsed_where_value_1} AND "
                   f"{where_attribute_2[0]} = {parsed_where_value_2};")
    disconnect_from_db(connection, cursor)


def parse_to_sql(value):
    return f"'{value}'" if (type(value) == str and value != 'null') else value


def insert_example():
    run_sql_script('insert_example')


def print_db():
    connection, cursor = connect_to_db()
    for table_name in ['Huby', 'Uzytkownicy', 'Kasetony', 'Grupy', 'Przypisania']:
        print('- - - - - - - - - - - - - - - - -')
        print(table_name)
        cursor.execute(f"SELECT * FROM {table_name};")
        for row in cursor.fetchall():
            print(row)
    disconnect_from_db(connection, cursor)


if __name__ == '__main__':
    # init_db()
    print_db()
