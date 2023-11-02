import db_management
from sqlite3 import OperationalError

SUCCESSFUL_OPERATION = 0
GROUP_NAME_ALREADY_USED = 1
LIGHT_ALREADY_IN_GROUP = 2
LIGHT_NOT_IN_GROUP = 3


current_hub_login: str = ''
current_hub_ip: str = ''
request_prefix: str = ''


def create(group_name: str, lights_ids: list[int]) -> int:
    if group_name in db_management.select_all('Grupy', 'NazwaGr'):
        return GROUP_NAME_ALREADY_USED
    try:
        id = max(db_management.select_all('Grupy', 'IdGr')) + 1
    except OperationalError:
        id = 1


def add_to_group(group_id: int, light_id: int) -> int:
    pass


def delete_from_group(group_id: int, light_id: int) -> int:
    pass


def __change_current_hub_2(mac_address: str) -> None:
    global current_hub_login, current_hub_ip, request_prefix
    current_hub_login = db_management.select('Huby', 'loginH', ('AdresMAC', mac_address))
    current_hub_ip = db_management.select('Huby', 'AdresIP', ('AdresMAC', mac_address))
    request_prefix = f'http://{current_hub_ip}/api/{current_hub_login}'


# print(db_management.select_all('Huby', 'AdresMAC'))