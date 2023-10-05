from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button


class CeilingLightsApp(App):

    def build(self):
        self.lights = [[False for _ in range(4)] for _ in range(4)]
        grid_layout = GridLayout(cols=4, spacing=5)

        for row in range(4):
            for col in range(4):
                button = Button(text='', background_color=(0, 0, 0, 1))
                button.bind(on_press=self.toggle_light)
                grid_layout.add_widget(button)

        self.buttons = grid_layout.children
        return grid_layout

    def toggle_light(self, instance):
        for i, button in enumerate(self.buttons):
            if button == instance:
                row, col = divmod(i, 4)
                self.lights[row][col] = not self.lights[row][col]
                self.update_light_display(row, col)

    def update_light_display(self, row, col):
        color = (1, 1, 0, 1) if self.lights[row][col] else (0.5, 0.5, 0.5, 1)
        self.buttons[row * 4 + col].background_color = color


if __name__ == '__main__':
    CeilingLightsApp().run()