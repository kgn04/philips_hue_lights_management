from requests import put, get
import backend.db_management as backend_management
from json import loads
from time import sleep
from sys import stdin

from backend import db_management

current_hub_login: str = ''
current_hub_ip: str = ''
current_hub_mac_address = ''
request_prefix: str = ''
# TODO Verifying responses


def change_color(light_id: int, rgb: tuple[int, int, int]) -> None:
    """
    :param rgb: (red[0-255], green[0-255], blue[0-255])
    """
    xy = rgb_to_xy(rgb)
    __send_put(light_id, {"xy": xy})
    db_management.update('Kasetony', ('KolorX', xy[0]), ('IdK', light_id))
    db_management.update('Kasetony', ('KolorY', xy[1]), ('IdK', light_id))


def change_brightness(light_id: int, brightness: int) -> None:
    """
    :param brightness: 0-255
    """
    __send_put(light_id, {"bri": brightness})
    db_management.update('Kasetony', ('Jasnosc', brightness), ('IdK', light_id))


def turn_off(light_id: int) -> None:
    __send_put(light_id, {"on": False})
    db_management.update('Kasetony', ('CzyWlaczony', False), ('IdK', light_id))


def turn_on(light_id: int) -> None:
    __send_put(light_id, {"on": True})
    db_management.update('Kasetony', ('CzyWlaczony', True), ('IdK', light_id))


def rgb_to_xy(rgb: tuple[int, int, int]):
    normalized_to_one = [0.0, 0.0, 0.0]
    cred, cgreen, cblue = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
    normalized_to_one[0] = cred
    normalized_to_one[1] = cgreen
    normalized_to_one[2] = cblue

    def adjust_color_channel(channel):
        if channel > 0.04045:
            return (channel + 0.055) / (1.0 + 0.055) ** 2.4
        else:
            return channel / 12.92

    red = adjust_color_channel(normalized_to_one[0])
    green = adjust_color_channel(normalized_to_one[1])
    blue = adjust_color_channel(normalized_to_one[2])

    X = red * 0.649926 + green * 0.103455 + blue * 0.197109
    Y = red * 0.234327 + green * 0.743075 + blue * 0.022598
    Z = red * 0.0000000 + green * 0.053077 + blue * 1.035763

    x = X / (X + Y + Z)
    y = Y / (X + Y + Z)

    return [x, y]


def update_lights_data():
    global request_prefix
    info_dict: dict = loads(get(url=request_prefix).text)
    light_ids = db_management.select_all('Kasetony', 'IdK')
    print(light_ids)
    for light_id in info_dict:
        state_dict = info_dict[(str(light_id))]['state']
        is_on = state_dict['on']
        color_x = state_dict['xy'][0]
        color_y = state_dict['xy'][1]
        brightness = state_dict['bri']
        if light_id not in light_ids:
            global current_hub_mac_address
            db_management.insert('Kasetony',
                                 (light_id, 0, 0, is_on, brightness, color_x, color_y, current_hub_mac_address))
        else:
            for attribute_name, attribute_value in [('CzyWlaczony', int(is_on)), ('KolorX', color_x), ('KolorY', color_y),
                                                    ('Jasnosc', brightness)]:
                db_management.update('Kasetony', (attribute_name, attribute_value),
                                     ('IdK', light_id))

def identify_light(light_id) -> tuple[int, int]:
    global LIGHT_COORD
    while not LIGHT_COORD:  # TODO setting light coord from GUI
        turn_off(light_id)
        sleep(0.25)
        turn_on(light_id)
    result = LIGHT_COORD
    LIGHT_COORD = None
    return result

def __change_current_hub_1(mac_address: str) -> None:
    global current_hub_login, current_hub_ip, current_hub_mac_address, request_prefix
    current_hub_login = db_management.select('Huby', 'loginH', ('AdresMAC', mac_address))[0]
    current_hub_ip = db_management.select('Huby', 'AdresIP', ('AdresMAC', mac_address))[0]
    current_hub_mac_address = mac_address
    request_prefix = f'http://{current_hub_ip}/api/{current_hub_login}/lights/'


def __send_put(light_id: int, body: dict) -> str:
    global request_prefix
    request = f'{request_prefix}{light_id}/state'
    return put(url=request, json=body).text

