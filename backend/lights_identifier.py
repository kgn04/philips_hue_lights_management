import backend.db_management as db_management
from backend.lights_operations import turn_on, turn_off
from time import sleep
from threading import Thread


class LightsIdentifier:
    def __init__(self, mac_address, kivy_manager):
        self.mac_address = mac_address
        self.coords = None
        self.kivy_manager = kivy_manager
        Thread(target=self.identify_lights).start()
        self.done = False

    def identify_lights(self):
        lights_ids = db_management.select('Kasetony', 'IdK', ('AdresMAC', self.mac_address))
        print(lights_ids)
        for light_id in lights_ids:
            print(light_id)
            row, column = self.identify_light(light_id)
            db_management.update_with_two_conditions('Kasetony', ('Rzad', row), ('IdK', light_id), ('AdresMAC', self.mac_address))
            db_management.update_with_two_conditions('Kasetony', ('Kolumna', column), ('IdK', light_id), ('AdresMAC', self.mac_address))
        # self.kivy_manager.current = 'login'
        self.done = True

    def identify_light(self, light_id) -> tuple[int, int]:
        while not self.coords:
            turn_off(light_id)
            sleep(0.5)
            turn_on(light_id)
            sleep(0.5)
        result = self.coords
        self.coords = None
        print(result)
        return result

    def set_light_coord(self, coords: tuple[int, int], xd=None) -> None:
        self.coords = coords


if __name__ == '__main__':
    pass
    # identifier = LightsIdentifier('00:00:00:00:00:00')
    # for i in range(16):
    #     sleep(2.0)
    #     identifier.set_light_coord(2, 4)
