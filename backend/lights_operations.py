from requests import put, get
from json import loads, load
from TEST import emulator
from backend import db_management
from sqlite3 import IntegrityError
import os

current_hub_login: str = ''
current_hub_ip: str = ''
current_hub_mac_address = ''
request_prefix: str = ''

USE_EMULATOR = True


def get_light_id(column: int, row: int) -> int:
    connection, cursor = db_management.connect_to_db()
    cursor.execute(f"SELECT IdK FROM Kasetony WHERE Kolumna = {column} AND Rzad = {row} AND "
                   f"AdresMAC = '{current_hub_mac_address}';")
    cursor_result = cursor.fetchone()
    db_management.disconnect_from_db(connection, cursor)
    return cursor_result[0]


def get_rgb(light_id: int) -> list[int, int, int]:
    return [db_management.select_with_two_conditions('Kasetony', f'Kolor{color}', ('IdK', light_id),
                                                     ('AdresMAC', current_hub_mac_address))[0]
            for color in ['R', 'G', 'B']
            ]


def get_brightness(light_id: int) -> int:
    return db_management.select_with_two_conditions('Kasetony', f'Jasnosc', ('IdK', light_id),
                                                    ('AdresMAC', current_hub_mac_address))[0]


def change_color(light_id: int, rgb: tuple[int, int, int], xd=None) -> None:
    """
    :param rgb: (red[0-255], green[0-255], blue[0-255])
    """
    global current_hub_mac_address
    if USE_EMULATOR:
        emulator.change_color(light_id, rgb)
    else:
        xy = rgb_to_xy(rgb)
        __send_put(light_id, {"xy": xy})
    for i, color in enumerate(['R', 'G', 'B']):
        db_management.update_with_two_conditions('Kasetony', (f'Kolor{color}', rgb[i]),
                                                 ('IdK', light_id), ('AdresMAC', current_hub_mac_address))


def change_brightness(light_id: int, brightness: int, xd=None) -> None:
    """
    :param brightness: 0-255
    """
    if USE_EMULATOR:
        pass  # TODO
    else:
        __send_put(light_id, {"bri": brightness})
    global current_hub_mac_address
    db_management.update_with_two_conditions('Kasetony', ('Jasnosc', brightness), ('IdK', light_id),
                                             ('AdresMAC', current_hub_mac_address))


def turn_off(light_id: int, xd=None) -> None:
    if USE_EMULATOR:
        emulator.turn_off(light_id)
    else:
        __send_put(light_id, {"on": False})
    global current_hub_mac_address
    db_management.update_with_two_conditions('Kasetony', ('CzyWlaczony', False), ('IdK', light_id),
                                             ('AdresMAC', current_hub_mac_address))


def turn_on(light_id: int, xd=None) -> None:
    if USE_EMULATOR:
        emulator.turn_on(light_id)
    else:
        __send_put(light_id, {"on": True})
    global current_hub_mac_address
    db_management.update_with_two_conditions('Kasetony', ('CzyWlaczony', True), ('IdK', light_id),
                                             ('AdresMAC', current_hub_mac_address))


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
    try:
        x = X / (X + Y + Z)
        y = Y / (X + Y + Z)
    except ZeroDivisionError:
        return [0, 0]
    return [x, y]


def xy_to_rgb(xy: tuple[float, float]):
    x, y = xy

    Y = 1.0
    X = x * Y / y
    Z = (1 - x - y) * Y / y

    def reverse_adjust_color_channel(channel):
        if channel > 0.04045:
            return ((channel + 0.055) / 1.055) ** 2.4
        else:
            return channel / 12.92

    red = reverse_adjust_color_channel(X * 1.656492 - Y * 0.354851 - Z * 0.255038)
    green = reverse_adjust_color_channel(-X * 0.707196 + Y * 1.655397 + Z * 0.036152)
    blue = reverse_adjust_color_channel(X * 0.051713 - Y * 0.121364 + Z * 1.011530)

    # Clamp values to the valid RGB range [0, 1]
    red = max(0, min(1, red))
    green = max(0, min(1, green))
    blue = max(0, min(1, blue))

    # Convert to integer values in the range [0, 255]
    red = int(round(red * 255))
    green = int(round(green * 255))
    blue = int(round(blue * 255))

    return red, green, blue


def update_lights_data():
    global current_hub_mac_address
    if current_hub_mac_address == '00:00:00:00:00:00':
        with open(f'{os.path.join(os.path.dirname(__file__), "..")}/TEST/emulator_config.json') as f:
            info_dict: dict = load(f)
    else:
        global request_prefix
        info_dict: dict = loads(get(url=request_prefix).text)
    for light_id in info_dict:
        if USE_EMULATOR:
            state_dict = info_dict[(str(light_id))]
        else:
            state_dict = info_dict[(str(light_id))]['state']
        is_on = state_dict['on']
        if USE_EMULATOR:
            rgb = state_dict['red'], state_dict['green'], state_dict['blue']
            brightness = state_dict['brightness']
        else:
            color_x = state_dict['xy'][0]
            color_y = state_dict['xy'][1]
            rgb = xy_to_rgb((color_x, color_y))
            brightness = state_dict['bri']
        try:
            db_management.insert('Kasetony',
                                 (light_id, 0, 0, is_on, brightness, rgb[0], rgb[1], rgb[2], current_hub_mac_address))
        except IntegrityError as e:
            print(f'{e} - {light_id}')
            print(('CzyWlaczony', int(is_on)), ('KolorR', rgb[0]), ('KolorG', rgb[1]), ('KolorB', rgb[2]),
                  ('Jasnosc', brightness))
            print(current_hub_mac_address)
            for attribute_name, attribute_value in [('CzyWlaczony', int(is_on)), ('KolorR', rgb[0]), ('KolorG', rgb[1]),
                                                    ('KolorB', rgb[2]), ('Jasnosc', brightness)]:
                db_management.update_with_two_conditions('Kasetony', (attribute_name, attribute_value),
                                                         ('IdK', light_id), ('AdresMAC', current_hub_mac_address))


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


if __name__ == '__main__':
    pass
    # __change_current_hub_1('00:00:00:00:00:00')
    # __change_current_hub_1('ec:b5:fa:98:1c:cd')
    # update_lights_data()
