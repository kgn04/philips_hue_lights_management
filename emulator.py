import pygame
import sys
from time import sleep
from threading import Thread

class PanelEmulator:
    def __init__(self, width, height, panel_size, gap_size):
        pygame.init()
        self.width = width
        self.height = height
        self.panel_size = panel_size
        self.gap_size = gap_size
        self.screen = pygame.display.set_mode((width, height))
        self.panels = [[(255, 255, 255) for _ in range(4)] for _ in range(4)]  # Initialize all panels as white

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
        for y in range(4):
            for x in range(4):
                panel_x = x * (panel_width + gap)
                panel_y = y * (panel_height + gap)
                pygame.draw.rect(self.screen, self.panels[y][x], (panel_x, panel_y, panel_width, panel_height))

    def turn_on(self, x, y):
        if 0 <= x < 4 and 0 <= y < 4:
            self.panels[y][x] = (255, 255, 255)

    def turn_off(self, x, y):
        print("hello")
        if 0 <= x < 4 and 0 <= y < 4:
            self.panels[y][x] = (0, 0, 0)

    def change_color(self, x, y, rgb):
        if 0 <= x < 4 and 0 <= y < 4:
            self.panels[y][x] = rgb

def run_emulator(emul):
    emul.run()


if __name__ == "__main__":
    emulator = PanelEmulator(450, 450, (100, 100), 10)  # Added a gap of 10 pixels
    emulator_thread = Thread(target=run_emulator, args=(emulator,), daemon=True)
    emulator_thread.run()
