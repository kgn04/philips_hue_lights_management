from requests import put, get
import db_management
from json import loads


current_hub_login: str = ''
current_hub_ip: str = ''
request_prefix: str = ''
# TODO Verifying responses


def change_color(light_id: int, rgb: tuple[int, int, int]) -> None:
    """
    :param rgb: (red[0-255], green[0-255], blue[0-255])
    """
    __send_put(light_id, {"xy": rgb_to_xy(rgb)})


def change_brightness(light_id: int, brightness: int) -> None:
    """
    :param brightness: 0-255
    """
    __send_put(light_id, {"bri": brightness})


def turn_off(light_id: int) -> None:
    __send_put(light_id, {"on": False})


def turn_on(light_id: int) -> None:
    __send_put(light_id, {"on": True})


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
    info_dict = loads(get(url=request_prefix).text)
    for light_id in info_dict:
        is_on = True  # TODO
        color_x = 0.0
        color_y = 0.0
        brightness = 0
        for attribute_name, attribute_value in [('CzyWlaczony', int(is_on)), ('KolorX', color_x), ('KolorY', color_y),
                                                ('Jasnosc', brightness)]:
            db_management.update('Kasetony', (attribute_name, attribute_value), ('IdK', light_id))


def __change_current_hub_1(mac_address: str) -> None:
    global current_hub_login, current_hub_ip, request_prefix
    current_hub_login = db_management.select('Huby', 'loginH', ('AdresMAC', mac_address))
    current_hub_ip = db_management.select('Huby', 'AdresIP', ('AdresMAC', mac_address))
    request_prefix = f'http://{current_hub_ip}/api/{current_hub_login}/lights/'


def __send_put(light_id: int, body: dict) -> str:
    global request_prefix
    request = f'{request_prefix}{light_id}/state'
    return put(url=request, json=body).text
