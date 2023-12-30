import backend.db_management as db_management
from sqlite3 import OperationalError
from requests import delete, get
from lights_operations import USE_EMULATOR
import TEST.emulator as emulator

SUCCESSFUL_OPERATION = 0
GROUP_NAME_ALREADY_USED = 1
GROUP_DOES_NOT_EXIST = 2
LIGHT_ALREADY_IN_GROUP = 3
LIGHT_NOT_IN_GROUP = 4

current_hub_mac_address: str = ''
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
    global current_hub_mac_address
    db_management.insert('Grupy', (group_id, group_name, current_hub_mac_address))
    if USE_EMULATOR:
        emulator.create_group(group_id, group_name)
    else:
        pass  # TODO
    return SUCCESSFUL_OPERATION


def remove(group_id: int) -> int:
    if group_id not in db_management.select_all('Grupy', 'IdGr'):
        return GROUP_DOES_NOT_EXIST
    db_management.delete('Grupy', ('IdGr', group_id))
    global request_prefix
    if USE_EMULATOR:
        emulator.remove_group(group_id)
    else:
        delete(url=f'{request_prefix}{group_id}')  # TODO
    return SUCCESSFUL_OPERATION


def add_to_group(group_id: int, light_id: int) -> int:
    if light_id in db_management.select('Przypisania', 'IdK', ('IdGr', group_id)):
        return LIGHT_ALREADY_IN_GROUP
    db_management.insert('Przypisania', (group_id, light_id))
    if USE_EMULATOR:
        emulator.add_light_to_group(group_id, light_id)
    else:
        pass  # TODO
    return SUCCESSFUL_OPERATION


def delete_from_group(group_id: int, light_id: int) -> int:
    # TODO Lepiej nie uzywac jeszcze lmao
    if light_id not in db_management.select('Przypisania', 'IdK', ('IdGr', group_id)):
        return LIGHT_NOT_IN_GROUP
    db_management.delete('Przypisania', ('IdK', light_id))
    if USE_EMULATOR:
        emulator.remove_light_from_group(group_id, light_id)
    else:
        pass  # TODO
    return SUCCESSFUL_OPERATION


def __change_current_hub_2(mac_address: str) -> None:
    global current_hub_mac_address, current_hub_login, current_hub_ip, request_prefix
    current_hub_mac_address = mac_address
    current_hub_login = db_management.select('Huby', 'loginH', ('AdresMAC', mac_address))[0]
    current_hub_ip = db_management.select('Huby', 'AdresIP', ('AdresMAC', mac_address))[0]
    request_prefix = f'http://{current_hub_ip}/api/{current_hub_login}/groups/'


if __name__ == '__main__':
    pass
    # __change_current_hub_2('ec:b5:fa:98:1c:cd')
    # print(get(url=request_prefix).text)