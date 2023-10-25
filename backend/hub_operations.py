from socket import gethostname, gethostbyname
from subprocess import Popen, PIPE
from re import search
import db_management


OPERATION_SUCCESSFUL = 0
NO_HUB_IN_NETWORK = 1


def find_hub(user_email: str):
    ip_network_prefix = gethostbyname(gethostname())[:gethostbyname(gethostname()).rfind('.')] + '.'
    for i in range(254):
        if True:  # TODO proper GET to send
            ip_address = ip_network_prefix + str(i+1)
            login = get_login(ip_address)
            mac_address = get_mac_address(ip_address)  # TODO should only return ip
            db_management.insert('Huby', (mac_address, ip_address, login))
            db_management.insert('Przydzielenia', (user_email, mac_address))
            return OPERATION_SUCCESSFUL
    return NO_HUB_IN_NETWORK


def get_login(ip_address: str) -> str:
    pass  # TODO


def get_mac_address(ip_address: str) -> str:
    message = str(Popen(['arp', '-n', ip_address], stdout=PIPE).communicate()[0])
    return search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", message).groups()[0]

def lights_count():
    pass  # TODO