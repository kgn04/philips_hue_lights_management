if __name__ == "__main__":
    import pygame
import sys
from threading import Thread
from json import load, dump
from threading import Semaphore
from json.decoder import JSONDecodeError
import os


semaphore = Semaphore()

EMULATOR_ABS_PATH = f'{os.path.join(os.path.dirname(__file__), "..")}/TEST'

EMULATOR_CONFIG_PATH = f'{EMULATOR_ABS_PATH}/emulator_config.json'
EMULATOR_GROUPS_CONFIG_PATH = f'{EMULATOR_ABS_PATH}/emulator_groups.json'



class Light:
    def __init__(self, light_dict):
        self.on = light_dict["on"]
        self.brightness = light_dict["brightness"]
        self.rgb = (light_dict["red"], light_dict["green"], light_dict["blue"])

    def __str__(self):
        return "light"

    def __repr__(self):
        return "light"


class PanelEmulator:
    def __init__(self, width, height, panel_size, gap_size):
        pygame.init()
        self.width = width
        self.height = height
        self.panel_size = panel_size
        self.gap_size = gap_size
        self.screen = pygame.display.set_mode((width, height))
        self.panels: list[list[Light]]
        self.update_lights()

    def update_lights(self):
        global semaphore
        semaphore.acquire()
        try:
            with open(EMULATOR_CONFIG_PATH, 'r+') as f:
                lights_dict = load(f)
        except JSONDecodeError:
            semaphore.release()
            return
        semaphore.release()
        i = 0
        res = []
        self.panels = []
        for key in lights_dict:
            res.append(Light(lights_dict[key]))
            i += 1
            if i == 4:
                i = 0
                self.panels.append(res)
                res = []

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.draw_panels()
            pygame.display.update()

        pygame.quit()
        sys.exit()

    def draw_panels(self):
        panel_width, panel_height = self.panel_size
        gap = self.gap_size
        self.update_lights()
        for y in range(4):
            for x in range(4):
                if self.panels[y][x].on:
                    colors = self.panels[y][x].rgb
                else:
                    colors = 0, 0, 0
                panel_x = x * (panel_width + gap)
                panel_y = y * (panel_height + gap)
                pygame.draw.rect(self.screen, colors, (panel_x, panel_y, panel_width, panel_height))


def turn_on(light_id):
    global semaphore
    semaphore.acquire()
    with open(EMULATOR_CONFIG_PATH, 'r+') as f:
        lights_dict = load(f)
    lights_dict[str(light_id)]["on"] = True
    with open(EMULATOR_CONFIG_PATH, 'w+') as f:
        dump(lights_dict, f)
    semaphore.release()


def turn_off(light_id):
    global semaphore
    semaphore.acquire()
    with open(EMULATOR_CONFIG_PATH, 'r+') as f:
        lights_dict = load(f)
    lights_dict[str(light_id)]["on"] = False
    with open(EMULATOR_CONFIG_PATH, 'w+') as f:
        dump(lights_dict, f)
    semaphore.release()


def change_color(light_id, rgb):
    global semaphore
    semaphore.acquire()
    with open(EMULATOR_CONFIG_PATH, 'r+') as f:
        lights_dict = load(f)
    lights_dict[str(light_id)]["red"] = rgb[0]
    lights_dict[str(light_id)]["green"] = rgb[1]
    lights_dict[str(light_id)]["blue"] = rgb[2]
    with open(EMULATOR_CONFIG_PATH, 'w+') as f:
        dump(lights_dict, f)
    semaphore.release()


def create_group(group_id, group_name, lights):
    with open(EMULATOR_GROUPS_CONFIG_PATH, 'r+') as f:
        groups_dict = load(f)
    groups_dict[str(group_id)] = {'name': group_name, 'lights': lights, 'on': True, 'brightness': 255, 'red': 255,
                                  'green': 255, 'blue': 255}
    with open(EMULATOR_GROUPS_CONFIG_PATH, 'w+') as f:
        dump(groups_dict, f)


def remove_group(group_id):
    with open(EMULATOR_GROUPS_CONFIG_PATH, 'r+') as f:
        groups_dict = load(f)
    del groups_dict[str(group_id)]
    with open(EMULATOR_GROUPS_CONFIG_PATH, 'w+') as f:
        dump(groups_dict, f)


def remove_light_from_group(group_id, light_id):
    with open(EMULATOR_GROUPS_CONFIG_PATH, 'r+') as f:
        groups_dict = load(f)
    groups_dict[str(group_id)]['lights'].remove(light_id)
    with open(EMULATOR_GROUPS_CONFIG_PATH, 'w+') as f:
        dump(groups_dict, f)


def operation_on_group(group_id, operation, operation_arg=None):
    with open(EMULATOR_GROUPS_CONFIG_PATH, 'r+') as f:
        groups_dict = load(f)
    for light_id in groups_dict[str(group_id)]['lights']:
        operation(light_id, operation_arg)


def turn_on_group(group_id):
    with open(EMULATOR_GROUPS_CONFIG_PATH, 'r+') as f:
        groups_dict = load(f)
    for light_id in groups_dict[str(group_id)]['lights']:
        turn_on(light_id)


def turn_off_group(group_id):
    with open(EMULATOR_GROUPS_CONFIG_PATH, 'r+') as f:
        groups_dict = load(f)
    for light_id in groups_dict[str(group_id)]['lights']:
        turn_off(light_id)



def change_color_group(group_id, rgb):
    with open(EMULATOR_GROUPS_CONFIG_PATH, 'r+') as f:
        groups_dict = load(f)
    for light_id in groups_dict[str(group_id)]['lights']:
        change_color(light_id, rgb)



def get_groups_dict():
    with open(EMULATOR_GROUPS_CONFIG_PATH, 'r+') as f:
        groups_dict = load(f)
    return groups_dict


def run_emulator(emul):
    emul.run()


if __name__ == "__main__":
    emulator = PanelEmulator(450, 450, (100, 100), 10)  # Added a gap of 10 pixels
    emulator_thread = Thread(target=run_emulator, args=(emulator,), daemon=True)
    emulator_thread.run()
