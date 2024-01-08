import backend.db_management as db_management
from backend.lights_operations import turn_on, turn_off
from time import sleep
from threading import Thread


class LightsIdentifier:
    def __init__(self, mac_address):
        self.mac_address = mac_address
        self.coords = None
        self.coords_history = []
        Thread(target=self.identify_lights).start()
        self.done = False
        self.lock = False
        self.stop = False

    def identify_lights(self):
        lights_ids = db_management.select('Kasetony', 'IdK', ('AdresMAC', self.mac_address))
        for light_id in lights_ids:
            row, column = self.identify_light(light_id)
            if self.done:
                return
            db_management.update_with_two_conditions('Kasetony', ('Rzad', row), ('IdK', light_id),
                                                     ('AdresMAC', self.mac_address))
            db_management.update_with_two_conditions('Kasetony', ('Kolumna', column), ('IdK', light_id),
                                                     ('AdresMAC', self.mac_address))
            self.lock = False
        self.done = True

    def identify_light(self, light_id) -> tuple[int, int]:
        while not self.coords:
            turn_off(light_id)
            sleep(1.0)
            turn_on(light_id)
            sleep(1.0)
            self.__reset_if_requested()
            if self.done:
                return 0, 0
        result = self.coords
        self.coords = None
        return result

    def set_light_coord(self, coords: tuple[int, int], instance=None) -> None:
        if not self.lock and coords not in self.coords_history:
            self.coords = coords
            self.coords_history.append(coords)
            instance.background_color = [0 / 255, 191 / 255, 255 / 255, 1]
            self.lock = True

    def __reset_if_requested(self):
        if self.stop:
            self.stop = False
            self.coords_history = []
            self.identify_lights()

    def reset_identification(self):
        self.stop = True


if __name__ == '__main__':
    pass
    # identifier = LightsIdentifier('00:00:00:00:00:00')
    # for i in range(16):
    #     sleep(2.0)
    #     identifier.set_light_coord(2, 4)
