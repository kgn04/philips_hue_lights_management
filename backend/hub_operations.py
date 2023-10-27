from socket import gethostname, gethostbyname
from subprocess import Popen, PIPE
from re import search
import db_management
from requests import get, post
from requests.exceptions import ConnectTimeout
from sys import platform
from time import sleep
from lights_operations import __change_current_hub_1
from groups_operations import __change_current_hub_2

OPERATION_SUCCESSFUL = 0
NO_HUB_IN_NETWORK = 1
TIMEOUT = 2

RESPONSE_BUTTON_NOT_PRESSED = '[{"error":{"type":101,"address":"","description":"link button not pressed"}}]'


def find_hubs() -> list[tuple[str, str]]:
    ip_network_prefix = gethostbyname(gethostname())[:gethostbyname(gethostname()).rfind('.')] + '.'
    result = []
    for i in range(235,254):  # TODO
        try:
            if get(url=f'http://172.31.0.{i+1}/api/newdeveloper.', timeout=1, allow_redirects=False).text == '[{"error":{"type":1,"address":"/","description":"unauthorized user"}}]':
                ip_address = ip_network_prefix + str(i+1)
                mac_address = __get_mac_address(ip_address)
                result.append((ip_address, mac_address))
        except ConnectTimeout:
            pass
    return result


def add_new_hub(ip_address: str, mac_address: str) -> int:
    login = __get_login(ip_address)
    if login == TIMEOUT:
        return TIMEOUT
    db_management.insert('Huby', (mac_address, ip_address, login, 0, 0))
    return OPERATION_SUCCESSFUL


def __get_login(ip_address: str, ):
    timeout = 60  # After using this method user has 60 seconds to press link button on the hub
    while timeout > 0:
        response = post(url=f'http://{ip_address}/api', json={"devicetype":"lights_app#admin"}).text
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


def lights_count():
    pass  # TODO

