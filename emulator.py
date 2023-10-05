from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from json import load

with open('lights_states.json') as f:
    lights_states = load(f)

class CeilingLightsApp(App):

    def build(self):
        global lights_states
        self.lights = []
        for i in range(4):
            temp = []
            for j in range(4):
                temp.append(lights_states[str(i*4+j+1)]["on"])
            self.lights.append(temp)
        print(self.lights)
        grid_layout = GridLayout(cols=4, spacing=5)

        for row in range(4):
            for col in range(4):
                button = Button(text='', background_color=(0, 0, 0, 1))
                button.bind(on_press=self.toggle_light)
                grid_layout.add_widget(button)

        self.buttons = grid_layout.children
        for i in range(4):
            for j in range(4):
                self.buttons[i * 4 + j].background_color = (1, 1, 0, 1) if self.lights[i][j] else (0.5, 0.5, 0.5, 1)
        return grid_layout

    def toggle_light(self, instance):
        for i, button in enumerate(self.buttons):
            if button == instance:
                row, col = divmod(i, 4)
                # self.lights[row][col] = not self.lights[row][col]
                for row in range(4):
                    for col in range(4):
                        self.update_light_display(row, col)

    def update_light_display(self, row, col):
        with open('lights_states.json') as f:
            lights_states = load(f)
        self.lights = []
        for i in range(4):
            temp = []
            for j in range(4):
                temp.append(lights_states[str(i*4+j+1)]["on"])
            self.lights.append(temp)
        color = (1, 1, 0, 1) if self.lights[row][col] else (0.5, 0.5, 0.5, 1)
        self.buttons[row * 4 + col].background_color = color


if __name__ == '__main__':
    app = CeilingLightsApp()
    app.run()