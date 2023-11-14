from socket import gethostname, gethostbyname
from subprocess import Popen, PIPE
from re import search
import backend.db_management as db_management
from requests import get, post
from sys import platform
from time import sleep
from backend.lights_operations import __change_current_hub_1, identify_light, USE_EMULATOR
from backend.groups_operations import __change_current_hub_2
from multiprocessing import Pool

OPERATION_SUCCESSFUL = 0
NO_HUB_IN_NETWORK = 1
TIMEOUT = 2

RESPONSE_BUTTON_NOT_PRESSED = '[{"error":{"type":101,"address":"","description":"link button not pressed"}}]'

current_mac_address = ''


def __is_it_hub(ip_address: str):
    try:
        if get(url=f'http://{ip_address}/api/newdeveloper.', timeout=1, allow_redirects=False).text \
                == '[{"error":{"type":1,"address":"/","description":"unauthorized user"}}]':
            return ip_address
    except Exception:
        return None


def find_hubs() -> list[tuple[str, str]]:  # Might take about 10 seconds
    ip_network_prefix = gethostbyname(gethostname())[:gethostbyname(gethostname()).rfind('.')] + '.'
    result = []
    ips_to_check = [ip_network_prefix+str(i+1) for i in range(254)]
    with Pool(processes=32) as pool:
        hubs_ips = [ip for ip in pool.map(__is_it_hub, ips_to_check) if ip is not None]
    for ip in hubs_ips:
        mac_address = __get_mac_address(ip)
        result.append((ip, mac_address))
    if USE_EMULATOR:
        result.append(('0.0.0.0', '00:00:00:00:00:00'))
    return result


def add_new_hub(ip_address: str, mac_address: str, name: str) -> int:
    login = __get_login(ip_address)
    if login == TIMEOUT:
        return TIMEOUT
    db_management.insert('Huby', (mac_address, ip_address, login, name, 0, 0))
    return OPERATION_SUCCESSFUL


def identify_lights(mac_address: str) -> int:
    lights_ids = db_management.select('Kasetony', 'IdK', ('AdresMAC', mac_address))
    for light_id in lights_ids:
        row, column = identify_light(light_id)
        db_management.update('Kasetony', ('Rzad', row), ('IdK', light_id))
        db_management.update('Kasetony', ('Kolumna', column), ('IdK', light_id))
    return OPERATION_SUCCESSFUL


def __get_login(ip_address: str):
    if ip_address == '0.0.0.0':
        return 'emulator_login'
    timeout = 60  # After using this method user has 60 seconds to press link button on the hub
    while timeout > 0:
        response = post(url=f'http://{ip_address}/api', json={"devicetype": "lights_app#admin"}).text
        if response != RESPONSE_BUTTON_NOT_PRESSED:
            return response.split('"')[-2]
        sleep(1)
        timeout -= 1
        print(timeout)
    return TIMEOUT


def __get_mac_address(ip_address: str) -> str:
    if platform == 'darwin':  # UNIX-like systems
        flag, pattern = '-n', r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})"
    else:
        flag, pattern = '-a', r"(([a-f\d]{1,2}\-){5}[a-f\d]{1,2})"
    message = str(Popen(['arp', flag, ip_address], stdout=PIPE).communicate()[0])
    result = search(pattern, message).groups()[0]
    result = result.replace('-', ':')
    return result


def change_current_hub(mac_address: str) -> None:
    __change_current_hub_1(mac_address)
    __change_current_hub_2(mac_address)
    global current_mac_address
    current_mac_address = mac_address


def lights_count(mac_address: str):
    return len(db_management.select('Kasetony', 'IdK', ('AdresMAC', mac_address)))


def change_name(name: str):
    global current_mac_address
    db_management.update('Huby', ("Nazwa", name), ('AdresMAC', current_mac_address))


def change_grid(x: int, y: int):
    global current_mac_address
    db_management.update('Huby', ("Rzedy", x), ('AdresMAC', current_mac_address))
    db_management.update('Huby', ("Kolumny", y), ('AdresMAC', current_mac_address))


if __name__ == '__main__':
    print(find_hubs())
    # add_new_hub('0.0.0.0', '00:00:00:00:00:00', 'emulator')
