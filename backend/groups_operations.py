import backend.db_management as db_management
from sqlite3 import OperationalError

SUCCESSFUL_OPERATION = 0
GROUP_NAME_ALREADY_USED = 1
GROUP_DOES_NOT_EXIST = 2
LIGHT_ALREADY_IN_GROUP = 3
LIGHT_NOT_IN_GROUP = 4


current_hub_login: str = ''
current_hub_ip: str = ''
request_prefix: str = ''


def create(group_name: str) -> int:
    if group_name in db_management.select_all('Grupy', 'NazwaGr'):
        return GROUP_NAME_ALREADY_USED
    try:
        group_id = max(db_management.select_all('Grupy', 'IdGr')) + 1
    except OperationalError:
        group_id = 1
    db_management.insert('Grupy', (group_id, group_name))
    return SUCCESSFUL_OPERATION


def delete(group_id: int) -> int:
    if group_id not in db_management.select_all('Grupy', 'IdGr'):
        return GROUP_DOES_NOT_EXIST
    db_management.delete('Grupy', ('IdGr', group_id))
    return SUCCESSFUL_OPERATION


def add_to_group(group_id: int, light_id: int) -> int:
    if light_id in db_management.select('Przypisania', 'IdK', ('IdGr', group_id)):
        return LIGHT_ALREADY_IN_GROUP
    db_management.insert('Przypisania', (group_id, light_id))
    return SUCCESSFUL_OPERATION


def delete_from_group(group_id: int, light_id: int) -> int:
    # TODO Lepiej nie uzywac jeszcze lmao
    if light_id not in db_management.select('Przypisania', 'IdK', ('IdGr', group_id)):
        return LIGHT_NOT_IN_GROUP
    db_management.delete('Przypisania', ('IdK', light_id))
    return SUCCESSFUL_OPERATION


def __change_current_hub_2(mac_address: str) -> None:
    global current_hub_login, current_hub_ip, request_prefix
    current_hub_login = db_management.select('Huby', 'loginH', ('AdresMAC', mac_address))
    current_hub_ip = db_management.select('Huby', 'AdresIP', ('AdresMAC', mac_address))
    request_prefix = f'http://{current_hub_ip}/api/{current_hub_login}'


# print(db_management.select_all('Huby', 'AdresMAC'))