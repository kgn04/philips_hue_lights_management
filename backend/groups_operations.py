import backend.db_management as db_management
from backend.lights_operations import rgb_to_xy
from sqlite3 import OperationalError, IntegrityError
from requests import delete
from backend.lights_operations import using_emulator
from TEST import emulator
from requests import get, put, post
import os
from json import load, loads
from time import time


SUCCESSFUL_OPERATION = 0
GROUP_NAME_ALREADY_USED = 1
GROUP_DOES_NOT_EXIST = 2
NO_LIGHTS_PROVIDED = 3
HUB_IS_RESTING = 4

LAST_SEND_TIME = time()

current_hub_mac_address: str = ''
current_hub_login: str = ''
current_hub_ip: str = ''
request_prefix: str = ''


def create(group_name: str, lights: list[int]) -> int:
    if not lights:
        return NO_LIGHTS_PROVIDED
    global current_hub_mac_address
    if group_name in db_management.select('Grupy', 'NazwaGr', ('AdresMAC', current_hub_mac_address)):
        return GROUP_NAME_ALREADY_USED
    if using_emulator():
        try:
            group_id = max(db_management.select_all('Grupy', 'IdGr')) + 1
        except (OperationalError, ValueError):
            group_id = 1
        db_management.insert('Grupy', (group_id, group_name, current_hub_mac_address))
        for light_id in lights:
            db_management.insert('Przypisania', (group_id, light_id, current_hub_mac_address))
        emulator.create_group(group_id, group_name, lights)
        return SUCCESSFUL_OPERATION
    else:
        global request_prefix, LAST_SEND_TIME
        if time() - LAST_SEND_TIME > 1.0:
            LAST_SEND_TIME = time()
            response = post(url=request_prefix, json={"name": group_name, "lights": [str(light_id) for light_id in lights]}).text
            update_groups_data()
            return SUCCESSFUL_OPERATION
    return HUB_IS_RESTING


def remove(group_name: str, xd=None) -> int:
    group_id = get_id_from_name(group_name)
    if group_id not in db_management.select_all('Grupy', 'IdGr'):
        return GROUP_DOES_NOT_EXIST
    global current_hub_mac_address
    db_management.delete_with_two_conditions('Grupy', ('IdGr', group_id), ('AdresMAC', current_hub_mac_address))
    db_management.delete_with_two_conditions('Przypisania', ('IdGr', group_id), ('AdresMAC', current_hub_mac_address))
    global request_prefix
    if using_emulator():
        emulator.remove_group(group_id)
    else:
        delete(url=f'{request_prefix}{group_id}')
    return SUCCESSFUL_OPERATION


def get_id_from_name(group_name: str) -> int:
    global current_hub_mac_address
    return db_management.select_with_two_conditions('Grupy', 'IdGr', ('NazwaGr', group_name),
                                                    ('AdresMAC', current_hub_mac_address))[0]


def is_any_on(group_name: str) -> int:
    global current_hub_mac_address
    lights_ids = db_management.select_with_two_conditions('Przypisania', 'IdK',
                                                          ('IdGr', get_id_from_name(group_name)),
                                                          ('AdresMAC', current_hub_mac_address))
    for light_id in lights_ids:
        if db_management.select_with_two_conditions('Kasetony', 'CzyWlaczony',
                                                    ('IdK', light_id), ('AdresMAC', current_hub_mac_address))[0]:
            return True
    return False


def change_color(group_name: str, rgb: tuple[int, int, int], xd=None) -> int:
    """
    :param rgb: (red[0-255], green[0-255], blue[0-255])
    """
    group_id = get_id_from_name(group_name)
    global current_hub_mac_address
    if using_emulator():
        emulator.change_color_group(group_id, rgb)
        response = 'OK'
    else:
        xy = rgb_to_xy(rgb)
        response = __send_put(group_id, {"xy": xy})
    if response:
        for light_id in db_management.select_with_two_conditions('Przypisania', 'IdK', ('IdGr', group_id),
                                                                 ('AdresMAC', current_hub_mac_address)):
            for i, color in enumerate(['R', 'G', 'B']):
                db_management.update_with_two_conditions('Kasetony', (f'Kolor{color}', rgb[i]),
                                                         ('IdK', light_id), ('AdresMAC', current_hub_mac_address))
        return SUCCESSFUL_OPERATION
    return HUB_IS_RESTING


def change_brightness(group_name: str, brightness: int, xd=None) -> int:
    """
    :param brightness: 0-255
    """
    group_id = get_id_from_name(group_name)
    if using_emulator():
        response = 'OK'
    else:
        response = __send_put(group_id, {"bri": brightness})
    if response:
        global current_hub_mac_address
        for light_id in db_management.select_with_two_conditions('Przypisania', 'IdK', ('IdGr', group_id),
                                                                 ('AdresMAC', current_hub_mac_address)):
            db_management.update_with_two_conditions('Kasetony', ('Jasnosc', brightness), ('IdK', light_id),
                                                     ('AdresMAC', current_hub_mac_address))
        return SUCCESSFUL_OPERATION
    return HUB_IS_RESTING


def turn_off(group_name: str, xd=None) -> int:
    group_id = get_id_from_name(group_name)
    if using_emulator():
        emulator.turn_off_group(group_id)
        response = 'OK'
    else:
        response = __send_put(group_id, {"on": False})
    if response:
        global current_hub_mac_address
        for light_id in db_management.select_with_two_conditions('Przypisania', 'IdK', ('IdGr', group_id),
                                                                 ('AdresMAC', current_hub_mac_address)):
            db_management.update_with_two_conditions('Kasetony', ('CzyWlaczony', False), ('IdK', light_id),
                                                     ('AdresMAC', current_hub_mac_address))
        return SUCCESSFUL_OPERATION
    return HUB_IS_RESTING


def turn_on(group_name: str, xd=None) -> int:
    group_id = get_id_from_name(group_name)
    if using_emulator():
        emulator.turn_on_group(group_id)
        response = 'OK'
    else:
        response = __send_put(group_id, {"on": True})
    if response:
        global current_hub_mac_address
        for light_id in db_management.select_with_two_conditions('Przypisania', 'IdK', ('IdGr', group_id),
                                                                 ('AdresMAC', current_hub_mac_address)):
            db_management.update_with_two_conditions('Kasetony', ('CzyWlaczony', True), ('IdK', light_id),
                                                     ('AdresMAC', current_hub_mac_address))
        return SUCCESSFUL_OPERATION
    return HUB_IS_RESTING


def update_groups_data():
    global current_hub_mac_address
    if using_emulator():
        with open(f'{os.path.join(os.path.dirname(__file__), "..")}/TEST/emulator_groups.json') as f:
            info_dict: dict = load(f)
    else:
        global request_prefix
        info_dict: dict = loads(get(url=request_prefix).text)
    for group_id in info_dict:
        state_dict = info_dict[(str(group_id))]
        name = state_dict['name']
        lights_ids = state_dict['lights']
        try:
            db_management.insert('Grupy', (group_id, name, current_hub_mac_address))
        except IntegrityError:
            db_management.update_with_two_conditions('Grupy', ('NazwaGr', name),
                                                     ('IdGr', group_id),
                                                     ('AdresMAC', current_hub_mac_address))
        try:
            for light_id in lights_ids:
                db_management.insert('Przypisania', (group_id, light_id, current_hub_mac_address))
        except IntegrityError:
            pass


def __change_current_hub_2(mac_address: str) -> None:
    global current_hub_mac_address, current_hub_login, current_hub_ip, request_prefix
    current_hub_mac_address = mac_address
    current_hub_login = db_management.select('Huby', 'loginH', ('AdresMAC', mac_address))[0]
    current_hub_ip = db_management.select('Huby', 'AdresIP', ('AdresMAC', mac_address))[0]
    request_prefix = f'http://{current_hub_ip}/api/{current_hub_login}/groups/'


def __send_put(group_id: int, body: dict) -> str:
    global request_prefix, LAST_SEND_TIME
    if time() - LAST_SEND_TIME > 2.0:
        LAST_SEND_TIME = time()
        request = f'{request_prefix}{group_id}/action'
        return put(url=request, json=body).text
    return ''


if __name__ == '__main__':
    pass

