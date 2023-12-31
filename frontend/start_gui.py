if __name__ == '__main__':
    from array import *
    from multiprocessing import freeze_support
    from kivy.core.window import Window
    from kivymd.toast import toast
    from kivy.uix.togglebutton import ToggleButton
    from kivymd.uix.textfield import MDTextField
    from backend import user_operations, db_management, hub_operations, lights_operations, groups_operations
    from numpy import *
    from kivy.uix.slider import Slider
    from kivy.clock import Clock
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from kivy.uix.popup import Popup
    from kivy.uix.screenmanager import ScreenManager, NoTransition, Screen
    from kivy.uix.scrollview import ScrollView
    from kivymd.app import MDApp
    from kivymd.uix.button import MDFillRoundFlatButton
    from kivy.config import Config
    from backend.lights_identifier import LightsIdentifier
    from functools import partial
    import numpy as np
    from sqlite3 import IntegrityError, OperationalError

    Config.set('graphics', 'resizable', False)
    Config.write()

    Clock.max_iteration = 20
    GRID = [[]]

    current_mac_address = ''
    current_mac_address_after_login = ''

    SCREENS_INITIALIZED = False


    def show_popup(title: str, message: str):
        popup = Popup(title=title, content=Label(text=message), size_hint=(2 / 3, 1 / 4))
        popup.open()
        Clock.schedule_once(popup.dismiss, 1)


    def show_popup2(title: str, message: str):
        label = Label(text=message)

        button_ok = Button(text='OK', size_hint=(1, None))

        # Funkcja do zamknięcia popupa po naciśnięciu przycisku "OK"
        def dismiss_popup(instance):
            popup.dismiss()

        button_ok.bind(on_press=dismiss_popup)

        layout = BoxLayout(orientation='vertical', spacing=10)
        layout.add_widget(label)
        layout.add_widget(button_ok)

        popup = Popup(title=title, content=layout, size_hint=(3 / 4, 1 / 2))
        popup.open()


    class ScreenStart(Screen):
        pass


    class ScreenAddHub(Screen):
        def add_hub(self):
            self.manager.add_widget(ScreenListHubs(name='list'))
            self.manager.current = 'list'


    class ScreenLoading(Screen):
        pass


    class LoadingScreen(BoxLayout):
        def __init__(self, **kwargs):
            super(LoadingScreen, self).__init__(**kwargs)
            self.orientation = 'vertical'
            label = Label(text='Właśnie szukam hubów, może to potrwać kilkanaście sekund, proszę o cierpliwość',
                          color=[128 / 255, 0 / 255, 128 / 255, 1],  # Set text color here
                          )
            self.add_widget(label)

        #     # Animowany pasek postępu  #     progress_bar = ProgressBar(max=1, height=40, size_hint=(0.2, None), pos_hint={'x': 0.4, 'y': 0.8})  #     self.add_widget(progress_bar)  #     self.progress_bar =progress_bar  #  #     # Rozpocznij animację paska postępu  #     self.progress_animation = Clock.schedule_interval(self.update_progress, 1 / 30)  #     self.progress_value = 0  #  # def update_progress(self, dt):  #     # Symuluj postęp ładowania (możesz dostosować to do swoich potrzeb)  #     self.progress_value += 0.25  #     if self.progress_value >= 1:  #         self.progress_value = 0  #     self.progress_bar.value = self.progress_value


    # wyświetlanie listy hubów które są online
    class ScreenListHubs(Screen):
        def __init__(self, **kwargs):
            super(ScreenListHubs, self).__init__(**kwargs)

            # Add loading screen
            loading_screen = LoadingScreen()
            self.add_widget(loading_screen)

            # Schedule the find_hubs function to run after a delay
            global SCREENS_INITIALIZED
            if SCREENS_INITIALIZED:
                Clock.schedule_once(self.find_hubs, 0.1)

        def find_hubs(self, dt):
            self.hubs_available = self.find_hubs_to_add()

            # Remove the loading screen
            self.remove_widget(self.children[0])

            # Schedule the find_hubs_and_display function to run after a delay
            Clock.schedule_once(self.find_hubs_and_display, 0.1)

        def find_hubs_and_display(self, dt):
            layout = BoxLayout(orientation='vertical', spacing=40, padding=40, pos_hint={'x': 0.1, 'y': 0.4},
                               size_hint=(3 / 4, 1 / 2))

            for hub in self.hubs_available:
                ip_address = hub[0]
                mac_address = hub[1]

                # układ poziomy dla jednego huba
                hub_layout = BoxLayout(orientation='horizontal', spacing=70, size_hint=(1, 3 / 4))

                # adres MAC
                mac_label = Label(text=f"Adres MAC: {mac_address}", size_hint=(1 / 3, 1 / 10), color="deepskyblue")
                hub_layout.add_widget(mac_label)

                #  adres IP
                ip_label = Label(text=f"Adres IP: {ip_address}", size_hint=(1 / 3, 1 / 10), color="deepskyblue")
                hub_layout.add_widget(ip_label)

                add_button = Button(text="Dodaj", size_hint=(1 / 5, 1 / 6))
                add_button.hub_mac = mac_address
                add_button.hub_ip = ip_address
                add_button.bind(on_release=self.choose_shape_add_name)
                hub_layout.add_widget(add_button)

                layout.add_widget(hub_layout)

            self.add_widget(layout)

        # szukanie hubów do wyświetlenia na liście
        def find_hubs_to_add(self) -> list:
            hubs_available = hub_operations.find_hubs()
            # self.manager.current = 'list'
            # hubs_available = [("00:11:22:33:44:50", "192.168.1.8"), ("AA:BB:CC:DD:EE:F5", "192.168.1.6")]
            return hubs_available

        def choose_shape_add_name(self, instance):
            # przekierowanie do ekraniu ScreenChooseShape
            self.manager.add_widget(ScreenChooseShape(name='shape'))
            self.manager.current = 'shape'

            global current_mac_address
            current_mac_address = instance.hub_mac

            try:
                hub_operations.add_new_hub(instance.hub_ip, instance.hub_mac, '')
            except IntegrityError:
                pass
            #
            hub_operations.change_current_hub(instance.hub_mac)
            print(f"Dodaj huba o adresie MAC: {instance.hub_mac}")


    # wybieranie z hubów które są już w bazie i łączenie się z nim
    class ScreenChooseHub(Screen):
        def __init__(self, **kwargs):
            super(ScreenChooseHub, self).__init__(**kwargs)

        def on_enter(self, *args):
            hub_data = db_management.select_all("Huby", "Nazwa")

            grid_layout = GridLayout(cols=7, spacing=30, size_hint=(1, 1 / 6), pos_hint={'x': 0.3, 'y': 0.4})

            for hub in hub_data:
                button = Button(text=hub, size_hint=(None, None), size=(100, 100))

                # button.background_normal = 'hub-small.png'  # obrazek tła nie działa
                button.ip_address = db_management.select("Huby", "AdresIP", ("Nazwa", hub))[0]
                button.mac_address = db_management.select("Huby", "AdresMAC", ("Nazwa", hub))[0]
                button.bind(on_release=self.hub_chosen)
                grid_layout.add_widget(button)

            self.add_widget(grid_layout)

        def hub_chosen(self, instance):
            global current_mac_address_after_login
            current_mac_address_after_login = str(instance.mac_address)

            self.manager.add_widget(ManageLightsScreen(name='manage'))
            self.manager.current = 'manage'


    class ScreenChooseShape(Screen):
        def __init__(self, **kwargs):
            super(ScreenChooseShape, self).__init__(**kwargs)
            self.selected_buttons_start = None
            self.selected_buttons_end = None
            self.buttons_array = [[]]
            self.cols = None
            self.rows = None

        def on_enter(self, *args):
            # Ta metoda jest wywoływana, gdy ekran jest już wyświetlony
            super().on_enter(*args)

            grid_size = (6, 6)  # Rozmiar siatki
            self.buttons_array = [[None for _ in range(grid_size[1])] for _ in range(grid_size[0])]

            buttons_layout = self.ids.buttons_layout
            for i in range(36):  # 6x6 siatka, więc 36 przycisków
                button = Button(size_hint=(0.5, 0.5))
                button.button_id = i + 1
                button.bind(on_press=self.button_pressed)
                buttons_layout.add_widget(button)

                row, col = divmod(i, grid_size[1])
                self.buttons_array[row][col] = button.button_id

        def button_pressed(self, instance):
            # Ta metoda zostanie wywołana po naciśnięciu przycisku
            button_id = instance.button_id
            print(f'Naciśnięto przycisk {button_id}')

        def on_touch_down(self, touch):
            print("TOUCH DOWN")
            if super(ScreenChooseShape, self).on_touch_down(touch):
                return True

            if self.ids.buttons_layout.collide_point(*touch.pos):
                touch.grab(self)
                self.selected_buttons_start = self.find_button_at_pos(touch.pos)
                return True

        def on_touch_move(self, touch):
            print("TOUCH MOVE")
            if touch.grab_current == self:
                self.selected_buttons_end = self.find_button_at_pos(touch.pos)
                print(self.selected_buttons_end)
                # self.update_button_colors()
                return True

        def on_touch_up(self, touch):
            # if touch.grab_current == self:
            touch.ungrab(self)
            button_id = self.find_button_at_pos(touch.pos)
            if button_id is not None:
                print(f'Touch up on button {button_id}')

                self.update_button_colors(button_id)

        def find_button_at_pos(self, pos):
            buttons_layout = self.ids.buttons_layout
            for child in buttons_layout.children:
                if child.collide_point(*pos):
                    return getattr(child, 'button_id', None)
            return None

        def update_button_colors(self, button_id):
            buttons_layout = self.ids.buttons_layout

            # siatka 6x6
            a = np.array(self.buttons_array)
            print(a)
            x, y = np.where(a == button_id)
            coord = np.array(list(zip(y, x)))[0]
            rows = coord[0] + 1
            self.rows = rows
            cols = coord[1] + 1
            self.cols = cols

            # zaznaczona siatka
            buttons_to_change = np.arange((cols) * (rows)).reshape(cols, rows)
            for i in range(cols):
                for j in range(rows):
                    buttons_to_change[i][j] = self.buttons_array[i][j]

            global GRID
            GRID = buttons_to_change

            for child in buttons_layout.children:
                child_id = getattr(child, 'button_id', None)
                arr = np.array(buttons_to_change)
                if child_id:
                    if child_id in arr:
                        child.background_color = [0 / 255, 191 / 255, 255 / 255, 1]  # Kolor zielony
                        child.selected = True
                    else:
                        child.background_color = [1, 1, 1, 1]  # Kolor domyślny
                        child.selected = False

        def add_hub_to_database(self):
            hub_name_input = self.ids.hub_name_input
            hub_name = hub_name_input.text.strip()

            hub_operations.change_name(hub_name)

            hub_operations.change_grid(self.rows, self.cols)

            self.manager.add_widget(ScreenIdentifyLights(name='identify'))
            self.manager.current = 'identify'


    class ScreenIdentifyLights(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)  # print(GRID)

        def on_enter(self, *args):
            # Ta metoda jest wywoływana, gdy ekran jest już wyświetlony
            super().on_enter(*args)

            rows = db_management.select('Huby', 'Rzedy', ('AdresMAC', current_mac_address))
            cols = db_management.select('Huby', 'Kolumny', ('AdresMAC', current_mac_address))

            # Convert the returned values to integers
            rows = int(rows[0]) if rows else 0
            cols = int(cols[0]) if cols else 0

            hub_array = np.arange(rows * cols).reshape(rows, cols)

            new_buttons_layout = GridLayout(cols=rows, size_hint=(3 / 4, 1 / 2), pos_hint={'x': 0.15, 'y': 0.25},
                                            spacing=10)

            lights_operations.update_lights_data()

            self.identifier = LightsIdentifier(current_mac_address)

            # Iteruj po macierzy GRID i dodaj przyciski do GridLayout
            for x, row in enumerate(hub_array):
                for y, value in enumerate(row):
                    button = Button(size_hint=(0.5, 0.5))
                    button.bind(on_press=partial(self.identifier.set_light_coord, (x, y)))
                    new_buttons_layout.add_widget(button)

            self.add_widget(new_buttons_layout)
            # Dodaj przycisk do przerwania identyfikacji i zaczęcia od nowa
            reset_button = MDFillRoundFlatButton(text="Przerwij", size_hint=(None, None)
                                                 , theme_text_color="Custom", text_color=[0, 0, 0, 1],
                                                 md_bg_color=[128 / 255, 0 / 255, 128 / 255, 1],
                                                 pos_hint={'center_x': 0.5, 'y': 0.1})

            reset_button.bind(on_press=self.reset_identification)
            self.add_widget(reset_button)

            Clock.schedule_once(self.change_screen, 0.1)

        def reset_identification(self, instance):
            if self.identifier:
                self.identifier.reset_identification()
                toast("Identyfikacja przerwana. Zacznij od nowa.")

        def change_screen(self, dt):
            if self.identifier.done:
                toast("Identyfikacja zakończona, możesz teraz się zalogować")
                self.manager.current = 'login'
            else:
                Clock.schedule_once(self.change_screen, 0.1)


    class ScreenLogin(Screen):
        def login(self, email: str, password: str):
            result = user_operations.login(email, password)
            print(result)
            if result == 0:
                show_popup("Logowanie", "Zalogowano pomyślnie")
                self.manager.current = 'choose'
            elif result == 3:
                show_popup("Logowanie", "Niepoprawny adres email")
            elif result == 4:
                show_popup("Logowanie", "Niepoprawne hasło")
            elif result == 6:
                show_popup("Logowanie", "Brak konta o takim adresie e-mail")

        def _on_keyboard_down(self, keycode):
            if keycode == 'enter' or keycode == 40:  # 40 - Enter key pressed
                self.login((str(self.ids.email.text)), str(self.ids.password.text))
                self.manager.switch_to('addhub')
                # self.manager.current = 'addhub'


    class ScreenRegister(Screen):

        def register(self, email: str, username: str, password1: str, password2: str) -> int:
            result = user_operations.register(email, username, password1, password2)
            if result == 0:
                show_popup("Rejestracja", "Rejestracja przebiegła pomyślnie")
                self.manager.current = 'login'
            elif result == 1:
                show_popup("Rejestracja", "Konto o takim adresie e-mail już istnieje")
            elif result == 2:
                show_popup("Rejestracja", "Hasła się różnią")
            elif result == 3:
                show_popup("Rejestracja", "Niepoprawny adres e-mail")
            elif result == 4:
                show_popup("Rejestracja", "Hasło musi mieć minimum 8 znaków, w tym znak specjalny i dużą literę")
            elif result == 5:
                show_popup("Rejestracja", "Niepoprawna nazwa użytkownika")


    class ManageLightsScreen(Screen):
        def __init__(self, **kwargs):
            super(ManageLightsScreen, self).__init__(**kwargs)
            self.selected_buttons = set()

            self.brightness: int
            self.r_color: int
            self.g_color: int
            self.b_color: int
            self.rows: int
            self.cols: int
            self.selected_buttons_start = None
            self.selected_buttons_end = None
            self.buttons_array = [[]]
            self.group_name_input = None
            self.right_layout = None

            print(current_mac_address_after_login)
            if current_mac_address_after_login:
                hub_operations.change_current_hub(current_mac_address_after_login)
            rows = db_management.select('Huby', 'Rzedy', ('AdresMAC', current_mac_address_after_login))
            cols = db_management.select('Huby', 'Kolumny', ('AdresMAC', current_mac_address_after_login))

            # Convert the returned values to integers
            rows = int(rows[0]) if rows else 0
            cols = int(cols[0]) if cols else 0
            print(rows)
            print(cols)
            self.rows = rows
            self.cols = cols

            self.hub_array = np.arange(rows * cols).reshape(rows, cols)
            print(self.hub_array)

            new_buttons_layout = GridLayout(cols=rows, size_hint=(4 / 5, 3 / 4), pos_hint={'x': 0.15, 'y': 0.25},
                                            spacing=10)

            # Iteruj po macierzy GRID i dodaj przyciski do GridLayout
            for row in self.hub_array:
                for value in row:
                    button = Button(text=str(lights_operations.get_light_id(value % cols, int(value / cols))),
                                    size_hint=(0.5, 0.5))
                    button.bind(on_press=self.show_light_controls)
                    # buttons_layout.add_widget(button)
                    new_buttons_layout.add_widget(button)

            # ScrollView na prawej stronie ekranu
            scroll_view = ScrollView()
            self.right_layout = BoxLayout(orientation='vertical', spacing=20, size_hint_y=None)
            self.right_layout.bind(minimum_height=self.right_layout.setter('height'))
            groups = db_management.select_all("Grupy", "NazwaGr")
            # groups = ["Grupa 1","Grupa 2"]

            # Dodaj utworzone grupy kasetonów
            self.create_right_layout(groups)

            scroll_view.add_widget(self.right_layout)

            # Utwórz główny układ (BoxLayout) dla całego ekranu
            main_layout = BoxLayout(spacing=30, size_hint=(0.9, 0.5), pos_hint={'x': 0.05, 'y': 0.2})
            main_layout.add_widget(new_buttons_layout)
            main_layout.add_widget(scroll_view)

            # Dodaj główny układ do ekranu
            self.add_widget(main_layout)

        def create_right_layout(self, groups):
            for group_name in groups:
                group_button = MDFillRoundFlatButton(text=group_name, size_hint_y=None, size_hint_x=1 / 2,
                                                     theme_text_color="Custom", text_color=[0, 0, 0, 1],
                                                     md_bg_color=[128 / 255, 0 / 255, 128 / 255, 1],
                                                     elevation_normal=20, pos_hint={'x': 0.4, 'y': 0.2})
                # group_button = Button(text=group_name, size_hint_y=None, height=40)
                group_button.bind(on_press=self.show_group_controls)
                self.right_layout.add_widget(group_button)

            # Przycisk do dodawania nowej grupy
            add_group_button = MDFillRoundFlatButton(text="Dodaj nową grupę", size_hint_y=None, size_hint_x=1 / 2,
                                                     theme_text_color="Custom", text_color=[0, 0, 0, 1],
                                                     md_bg_color=[128 / 255, 0 / 255, 128 / 255, 1],
                                                     elevation_normal=20, pos_hint={'x': 0.34})
            add_group_button.bind(on_press=self.add_group_popup)
            self.right_layout.add_widget(add_group_button)
            return self.right_layout

        def show_light_controls(self, instance):
            light_id = int(instance.text)

            # Funkcja wywoływana po naciśnięciu przycisku z kasetonem
            popup_content = BoxLayout(orientation='vertical', spacing=10)

            light_name_label = Label(text=f"Kaseton {instance.text}", halign='center')
            popup_content.add_widget(light_name_label)

            turn_on_button = Button(text="Włącz", size_hint_y=None, )
            turn_off_button = Button(text="Wyłącz", size_hint_y=None, )

            turn_on_button.bind(on_press=partial(lights_operations.turn_on, light_id))
            turn_off_button.bind(on_press=partial(lights_operations.turn_off, light_id))

            self.r_color, self.g_color, self.b_color = tuple(lights_operations.get_rgb(light_id))
            self.brightness = lights_operations.get_brightness(light_id)

            rgb_sliders_layout = BoxLayout(orientation='vertical', spacing=10)
            red_slider = Slider(min=0, max=255, value=self.r_color, orientation='horizontal')
            green_slider = Slider(min=0, max=255, value=self.g_color, orientation='horizontal')
            blue_slider = Slider(min=0, max=255, value=self.b_color, orientation='horizontal')

            def on_slider_r(instance, value):
                self.r_color = int(value)
                lights_operations.change_color(light_id, (self.r_color, self.g_color, self.b_color))

            def on_slider_g(instance, value):
                self.g_color = int(value)
                lights_operations.change_color(light_id, (self.r_color, self.g_color, self.b_color))

            def on_slider_b(instance, value):
                self.b_color = int(value)
                lights_operations.change_color(light_id, (self.r_color, self.g_color, self.b_color))

            def on_slider_brightness(instance, value):
                self.brightness = int(value)
                lights_operations.change_brightness(light_id, self.brightness)

            red_slider.bind(value=on_slider_r)
            green_slider.bind(value=on_slider_g)
            blue_slider.bind(value=on_slider_b)

            brightness_label = Label(text="Jasność")
            brightness_slider = Slider(min=0, max=255, value=self.brightness, orientation='horizontal')
            brightness_slider.bind(value=on_slider_brightness)

            rgb_sliders_layout.add_widget(Label(text="Czerwony"))
            rgb_sliders_layout.add_widget(red_slider)
            rgb_sliders_layout.add_widget(Label(text="Zielony"))
            rgb_sliders_layout.add_widget(green_slider)
            rgb_sliders_layout.add_widget(Label(text="Niebieski"))
            rgb_sliders_layout.add_widget(blue_slider)

            popup_content.add_widget(turn_on_button)
            popup_content.add_widget(turn_off_button)
            popup_content.add_widget(brightness_label)
            popup_content.add_widget(brightness_slider)
            popup_content.add_widget(rgb_sliders_layout)

            light_controls_popup = Popup(title=f"Zarządzaj Kasetonem {instance.text}", content=popup_content,
                                         size_hint=(0.7, 0.8), )
            light_controls_popup.open()

        def show_group_controls(self, instance):
            # Funkcja wywoływana po naciśnięciu przycisku z grupą kasetonów
            group_name = instance.text
            popup_content = BoxLayout(orientation='vertical', spacing=10)

            #  etykieta z nazwą grupy
            group_name_label = Label(text=f"Grupa: {group_name}", halign='center')
            popup_content.add_widget(group_name_label)

            group_controls_popup = Popup(title=f"Zarządzaj Grupą {group_name}", content=popup_content,
                                         size_hint=(None, None), size=(300, 300))
            group_controls_popup.open()

        def add_group_popup(self, instance):
            # Funkcja wywoływana po naciśnięciu przycisku "Dodaj grupę"

            popup_content = self.create_add_group_layout()
            add_group_popup = Popup(title='Dodaj nową grupę', content=popup_content, size_hint=(0.8, 0.7),
                                    )
            add_group_popup.open()

        def create_add_group_layout(self):
            popup_content = BoxLayout(orientation='vertical', spacing=10)

            group_name_label = Label(text='Nazwa grupy:', pos_hint={'x': 0, 'y': 0.1}, padding=(0, 0))
            self.group_name_input = MDTextField(
                mode="rectangle",
                spacing=5,
                size_hint=(0.4, 0.1),
                text_color_normal=(1, 1, 1, 1),
                pos_hint={'x': 0.3, 'y': 0.8},
                line_color_normal='deepskyblue',
                hint_text_color_normal='deepskyblue',
                hint_text='Wprowadź nazwę grupy', padding=10)

            grid_size = (self.rows, self.cols)  # Rozmiar siatki
            self.buttons_array = [[None for _ in range(grid_size[1])] for _ in range(grid_size[0])]

            buttons_layout = GridLayout(cols=self.rows, size_hint=(3 / 4, 3 / 4), pos_hint={'x': 0.15, 'y': 0.7},
                                        spacing=10)

            for row_index, row in enumerate(self.hub_array):
                for col_index, value in enumerate(row):
                    button = ToggleButton(size_hint=(0.2, 0.2))
                    button.button_id = value
                    button.row = row_index
                    button.col = col_index
                    print(value)
                    print(row_index)
                    print(col_index)
                    button.bind(on_press=self.button_pressed)
                    buttons_layout.add_widget(button)

                    row, col = divmod(value, grid_size[1])
                    self.buttons_array[row][col] = button.button_id

            add_group_button = MDFillRoundFlatButton(text="Dodaj grupę", pos_hint={'x': 0.4},
                                                     theme_text_color="Custom", text_color=[0, 0, 0, 1],
                                                     md_bg_color=[128 / 255, 0 / 255, 128 / 255, 1],
                                                     padding=10)
            add_group_button.bind(on_press=self.add_group_action)

            popup_content.add_widget(group_name_label)
            popup_content.add_widget(self.group_name_input)
            popup_content.add_widget(buttons_layout)
            popup_content.add_widget(add_group_button)
            return popup_content

        def button_pressed(self, instance):
            # Funkcja wywoływana po naciśnięciu przycisku (ToggleButton)
            if instance.state == 'down':
                print(f"Przycisk {instance.button_id} włączony")
                self.selected_buttons.add(instance.button_id)  # Dodaj współrzędne do zbioru
            else:
                print(f"Przycisk {instance.button_id} wyłączony")
                self.selected_buttons.discard(instance.button_id)  # Usuń współrzędne ze zbioru

        def add_group_action(self, instance):
            # Funkcja wywoływana po naciśnięciu przycisku "Dodaj grupę"
            group_name = self.group_name_input.text
            print(f"Dodaj grupę o nazwie: {group_name}")
            print("Współrzędne wybranych przycisków:", self.selected_buttons)

            result = groups_operations.create(group_name)
            if result == 0:
                # Tworzenie grupy powiodło się
                toast("Tworzenie grupy powiodło się")
                group_id = db_management.select('Grupy', 'IdGr', ('NazwaGr', group_name))
                for button_id in list(self.selected_buttons):
                    groups_operations.add_to_group(group_id[0], button_id)
                self.update_group_view()

                self.dismiss_popup()
            elif result == 1:
                # Grupa o takiej nazwie już istnieje
                toast("Grupa o takiej nazwie już istnieje, wybierz inną nazwę")
            else:
                toast("Wystąpił błąd podczas tworzenia grupy")

        def update_group_view(self):
            # Funkcja do aktualizacji widoku grup
            groups = db_management.select_all("Grupy", "NazwaGr")
            right_layout = self.right_layout  # Uzyskaj dostęp do kontenera przechowującego przyciski grup
            right_layout.clear_widgets()  # Wyczyść obecne przyciski grup

            self.create_right_layout(groups)

        def dismiss_popup(self):
            # Dismiss the currently open popup
            for widget in Window.children[:]:
                if isinstance(widget, Popup):
                    widget.dismiss()


    class MyApp(MDApp):

        def build(self):
            Config.set('graphics', 'resizable', False)
            # load_file can be called multiple times
            # self.root = Builder.load_file(r"/frontend/my.kv")
            sm = ScreenManager(transition=NoTransition())
            sm.add_widget(ScreenStart(name='start'))
            sm.add_widget(ScreenLogin(name='login'))
            sm.add_widget(ScreenRegister(name='register'))
            sm.add_widget(ScreenAddHub(name='addhub'))
            # sm.add_widget(ScreenListHubs(name='list'))
            sm.add_widget(ScreenChooseHub(name='choose'))
            sm.add_widget(ScreenChooseShape(name='shape'))
            # sm.add_widget(ScreenSimulator(name='simulator'))
            # print(sys.path)
            global SCREENS_INITIALIZED
            SCREENS_INITIALIZED = True
            return sm


    freeze_support()
    MyApp().run()
