import db_management
from lights_operations import turn_on, turn_off
from time import sleep
from threading import Thread


class LightsIdentifier:
    def __init__(self, mac_address):
        self.mac_address = mac_address
        self.coords = None
        Thread(target=self.identify_lights).start()

    def identify_lights(self):
        lights_ids = db_management.select('Kasetony', 'IdK', ('AdresMAC', self.mac_address))
        for light_id in lights_ids:
            row, column = self.identify_light(light_id)
            db_management.update('Kasetony', ('Rzad', row), ('IdK', light_id))
            db_management.update('Kasetony', ('Kolumna', column), ('IdK', light_id))

    def identify_light(self, light_id) -> tuple[int, int]:
        while not self.coords:  # TODO setting light coord from GUI
            turn_off(light_id)
            sleep(0.5)
            turn_on(light_id)
            sleep(0.5)
        print("wow")
        result = self.coords
        self.coords = None
        return result

    def set_light_coord(self, x: int, y: int) -> None:
        self.coords = x, y


if __name__ == '__main__':
    identifier = LightsIdentifier('00:00:00:00:00:00')
    # for i in range(16):
    #     sleep(2.0)
    #     identifier.set_light_coord(2, 4)
