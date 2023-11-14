import sys
from array import *

import numpy as np
from numpy import *
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, NoTransition, Screen
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton

from backend import user_operations, db_management, hub_operations

from kivy.lang import Builder

from kivy.config import Config

Config.set('graphics', 'resizable', False)
Config.write()

Clock.max_iteration = 20


def show_popup(title: str, message: str):
    popup = Popup(title=title, content=Label(text=message), size_hint=(1 / 2, 1 / 4))
    popup.open()
    Clock.schedule_once(popup.dismiss, 1)


class ScreenStart(Screen):
    pass


class ScreenAddHub(Screen):
    def add_hub(self):
        self.manager.add_widget(ScreenListHubs(name='list'))
        self.manager.current = 'list'


# wyświetlanie listy hubów które są online
class ScreenListHubs(Screen):
    def __init__(self, **kwargs):
        super(ScreenListHubs, self).__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', spacing=40, padding=40,
                           pos_hint={'x': 0.1, 'y': 0.4}, size_hint=(3 / 4, 1 / 2))
        # layout.size = (300, 400)

        hubs_available = self.find_hubs_to_add()
        for hub in hubs_available:
            ip_address = hub[0]
            mac_address = hub[1]

            # układ poziomy dla jednego huba
            hub_layout = BoxLayout(orientation='horizontal', spacing=70, size_hint=(1, 3 / 4))

            # adres MAC
            mac_label = Label(text=f"Adres MAC: {mac_address}", size_hint=(1 / 3, 1 / 10),
                              color="deepskyblue")
            hub_layout.add_widget(mac_label)

            #  adres IP
            ip_label = Label(text=f"Adres IP: {ip_address}", size_hint=(1 / 3, 1 / 10),
                             color="deepskyblue")
            hub_layout.add_widget(ip_label)

            add_button = MDFillRoundFlatButton(text="Dodaj", size_hint=(1 / 5, 1 / 3),
                                               theme_text_color="Primary",
                                               md_bg_color=[128 / 255, 0 / 255, 128 / 255, 1], elevation_normal=10)
            add_button.hub_mac = mac_address
            add_button.hub_ip = ip_address
            add_button.bind(on_release=self.choose_shape_add_name)
            hub_layout.add_widget(add_button)

            layout.add_widget(hub_layout)

        self.add_widget(layout)

    # szukanie hubów do wyświetlenia na liście
    def find_hubs_to_add(self) -> list:
        # hubs_available = hub_operations.find_hubs()
        hubs_available = [("00:11:22:33:44:50", "192.168.1.8"), ("AA:BB:CC:DD:EE:F5", "192.168.1.6")]
        return hubs_available

    def choose_shape_add_name(self, instance):
        # add new hub ?
        # przekierowanie do ekraniu ScreenChooseShape
        self.manager.add_widget(ScreenChooseShape(name='shape'))
        self.manager.current = 'shape'
        print(f"Dodaj huba o adresie MAC: {instance.hub_mac}")


# wybieranie z hubów które są już w bazie i łączenie się z nim
class ScreenChooseHub(Screen):
    def __init__(self, **kwargs):
        super(ScreenChooseHub, self).__init__(**kwargs)

        hub_data = db_management.select_all("Huby", "Nazwa")
        print(hub_data)

        grid_layout = GridLayout(cols=7, spacing=30, size_hint=(1, 1 / 6), pos_hint={'x': 0.3, 'y': 0.4})

        for hub in hub_data:
            button = Button(text=hub, size_hint=(None, None), size=(100, 100))
            # button.background_normal = 'hub-small.png'  # obrazek tła nie działa idk why
            button.ip_address = db_management.select("Huby", "AdresIP", ("Nazwa", hub))
            button.mac_address = db_management.select("Huby", "AdresMAC", ("Nazwa", hub))
            button.bind(on_release=self.hub_chosen)
            grid_layout.add_widget(button)

        self.add_widget(grid_layout)

    def hub_chosen(self, instance):
        # change current hub
        # update lights data
        global chosen_hub
        chosen_hub = str(instance.mac_address)
        print(chosen_hub)
        self.manager.current = 'simulator'


class ScreenChooseShape(Screen):
    def __init__(self, **kwargs):
        super(ScreenChooseShape, self).__init__(**kwargs)
        self.selected_buttons_start = None
        self.selected_buttons_end = None
        self.buttons_array = [[]]

    def on_enter(self, *args):
        # Ta metoda jest wywoływana, gdy ekran jest już wyświetlony
        super().on_enter(*args)

        grid_size = (6, 6)  # Rozmiar siatki
        self.buttons_array = [[None for _ in range(grid_size[1])] for _ in range(grid_size[0])]

        # Dodaj przyciski do siatki
        buttons_layout = self.ids.buttons_layout
        for i in range(36):  # 6x6 siatka, więc 36 przycisków
            button = Button(text=str(i + 1), size_hint=(0.5, 0.5))
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
        cols = coord[1] + 1

        # zaznaczona siatka
        buttons_to_change = np.arange((cols) * (rows)).reshape(cols, rows)
        for i in range(cols):
            for j in range(rows):
                buttons_to_change[i][j] = self.buttons_array[i][j]
        print(buttons_to_change)

        for child in buttons_layout.children:
            child_id = getattr(child, 'button_id', None)
            arr = np.array(buttons_to_change)
            #print(child_id in arr)
            #print(child_id)
            if child_id:
                if child_id in arr:
                    child.background_color = [128 / 255, 0 / 255, 128 / 255, 1]  # Kolor zielony
                    child.selected = True
                else:
                    child.background_color = [1, 1, 1, 1]  # Kolor domyślny
                    child.selected = False


    def add_hub_to_database(self):
        pass


# ScreenIdentifyShape


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
            show_popup("Rejestracja", "Hasło nie spełnia wymagań")
        elif result == 5:
            show_popup("Rejestracja", "Niepoprawna nazwa użytkownika")


class ScreenSimulator(Screen):

    def generate_rectangle(self):
        # Usuń istniejący prostokąt
        rectangle_grid = self.ids.rectangle_grid
        rectangle_grid.clear_widgets()

        # Wygeneruj nowy prostokąt z przyciskami 5x5
        grid_layout = GridLayout(cols=5, spacing=10)
        for i in range(25):  # Maksymalnie 5x5 = 25 przycisków
            button = Button(text=str(i + 1))
            grid_layout.add_widget(button)

        rectangle_grid.add_widget(grid_layout)


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
        # sm.add_widget(ScreenChooseShape(name='shape'))
        sm.add_widget(ScreenSimulator(name='simulator'))
        print(sys.path)
        return sm


MyApp().run()
