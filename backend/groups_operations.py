import backend.db_management as db_management
from backend.lights_operations import rgb_to_xy, xy_to_rgb
from sqlite3 import OperationalError, IntegrityError
from requests import delete
from backend.lights_operations import USE_EMULATOR
from TEST import emulator
from requests import get, put, post
import os
from json import load, loads
from time import time


SUCCESSFUL_OPERATION = 0
GROUP_NAME_ALREADY_USED = 1
GROUP_DOES_NOT_EXIST = 2
NO_LIGHTS_PROVIDED = 3

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
    if USE_EMULATOR:
        try:
            group_id = max(db_management.select_all('Grupy', 'IdGr')) + 1
        except (OperationalError, ValueError):
            group_id = 1
        db_management.insert('Grupy', (group_id, group_name, 0, 0, 0, 0, 0, current_hub_mac_address))
        emulator.create_group(group_id, group_name)
    else:
        global request_prefix, LAST_SEND_TIME
        if time() - LAST_SEND_TIME > 1.0:
            LAST_SEND_TIME = time()
            response = post(url=request_prefix, json={"name": group_name, "lights": [str(light_id) for light_id in lights]}).text
            update_groups_data()
    return SUCCESSFUL_OPERATION


def remove(group_name: str, xd=None) -> int:
    group_id = get_id_from_name(group_name)
    if group_id not in db_management.select_all('Grupy', 'IdGr'):
        return GROUP_DOES_NOT_EXIST
    global current_hub_mac_address
    db_management.delete_with_two_conditions('Grupy', ('IdGr', group_id), ('AdresMAC', current_hub_mac_address))
    db_management.delete_with_two_conditions('Przypisania', ('IdGr', group_id), ('AdresMAC', current_hub_mac_address))
    global request_prefix
    if USE_EMULATOR:
        emulator.remove_group(group_id)
    else:
        delete(url=f'{request_prefix}{group_id}')
    return SUCCESSFUL_OPERATION


def get_rgb(group_name: str) -> list[int, int, int]:
    return [db_management.select_with_two_conditions('Grupy', f'Kolor{color}', ('NazwaGr', group_name),
                                                     ('AdresMAC', current_hub_mac_address))[0]
            for color in ['R', 'G', 'B']
            ]


def get_brightness(group_name: str) -> int:
    return db_management.select_with_two_conditions('Grupy', f'Jasnosc', ('NazwaGr', group_name),
                                                    ('AdresMAC', current_hub_mac_address))[0]


def get_id_from_name(group_name: str) -> int:
    global current_hub_mac_address
    return db_management.select_with_two_conditions('Grupy', 'IdGr', ('NazwaGr', group_name),
                                                    ('AdresMAC', current_hub_mac_address))[0]


def change_color(group_name: str, rgb: tuple[int, int, int], xd=None) -> None:
    """
    :param rgb: (red[0-255], green[0-255], blue[0-255])
    """
    group_id = get_id_from_name(group_name)
    global current_hub_mac_address
    if USE_EMULATOR:
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
        for i, color in enumerate(['R', 'G', 'B']):
            db_management.update_with_two_conditions('Grupy', (f'Kolor{color}', rgb[i]),
                                                     ('IdGr', group_id), ('AdresMAC', current_hub_mac_address))


def change_brightness(group_name: str, brightness: int, xd=None) -> None:
    """
    :param brightness: 0-255
    """
    group_id = get_id_from_name(group_name)
    if USE_EMULATOR:
        response = 'OK'
    else:
        response = __send_put(group_id, {"bri": brightness})
    if response:
        global current_hub_mac_address
        for light_id in db_management.select_with_two_conditions('Przypisania', 'IdK', ('IdGr', group_id),
                                                                 ('AdresMAC', current_hub_mac_address)):
            db_management.update_with_two_conditions('Kasetony', ('Jasnosc', brightness), ('IdK', light_id),
                                                     ('AdresMAC', current_hub_mac_address))
        db_management.update_with_two_conditions('Grupy', ('Jasnosc', brightness), ('IdGr', group_id),
                                                 ('AdresMAC', current_hub_mac_address))


def turn_off(group_name: str, xd=None) -> None:
    group_id = get_id_from_name(group_name)
    if USE_EMULATOR:
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
        db_management.update_with_two_conditions('Grupy', ('CzyWlaczone', False), ('IdGr', group_id),
                                                 ('AdresMAC', current_hub_mac_address))


def turn_on(group_name: str, xd=None) -> None:
    group_id = get_id_from_name(group_name)
    if USE_EMULATOR:
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
        db_management.update_with_two_conditions('Grupy', ('CzyWlaczone', True), ('IdGr', group_id),
                                                 ('AdresMAC', current_hub_mac_address))


def update_groups_data():
    global current_hub_mac_address
    if current_hub_mac_address == '00:00:00:00:00:00':
        with open(f'{os.path.join(os.path.dirname(__file__), "..")}/TEST/emulator_config.json') as f:
            info_dict: dict = load(f)
    else:
        global request_prefix
        info_dict: dict = loads(get(url=request_prefix).text)
    for group_id in info_dict:
        state_dict = info_dict[(str(group_id))]
        if USE_EMULATOR:
            is_on = state_dict['on']
            name = state_dict['name']
            rgb = state_dict['red'], state_dict['green'], state_dict['blue']
            brightness = state_dict['brightness']
            lights_ids = state_dict['lights']
        else:
            is_on = state_dict['action']['on']
            name = state_dict['name']
            xy = state_dict['action']['xy']
            rgb = xy_to_rgb((xy[0], xy[1]))
            brightness = state_dict['action']['bri']
            lights_ids = state_dict['lights']
        try:
            db_management.insert('Grupy',
                                 (group_id, name, is_on, brightness, rgb[0], rgb[1], rgb[2], current_hub_mac_address))
        except IntegrityError:
            for attribute_name, attribute_value in [('NazwaGr', name), ('CzyWlaczone', int(is_on)), ('KolorR', rgb[0]),
                                                    ('KolorG', rgb[1]), ('KolorB', rgb[2]), ('Jasnosc', brightness)]:
                db_management.update_with_two_conditions('Grupy', (attribute_name, attribute_value),
                                                         ('IdGr', group_id), ('AdresMAC', current_hub_mac_address))
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
    if time() - LAST_SEND_TIME > 1.0:
        LAST_SEND_TIME = time()
        request = f'{request_prefix}{group_id}/action'
        return put(url=request, json=body).text
    return ''


if __name__ == '__main__':
    print(__change_current_hub_2('ec:b5:fa:98:1c:cd'))
    # update_groups_data()
    # print(post(url=request_prefix, json={"name": "NewOne", "lights": ["1"]}).text)
    print(request_prefix)
    # from time import sleep
    # sleep(2)
    # create('NewOne')
    update_groups_data()
    db_management.print_db()

