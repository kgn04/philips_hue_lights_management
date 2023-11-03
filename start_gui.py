import sys

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, NoTransition, Screen, SlideTransition, FadeTransition
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
import backend.user_operations as user_operations
import backend.db_management as db_management
import backend.hub_operations as hub_operations

from kivy.lang import Builder

Clock.max_iteration = 20




def show_popup(title: str, message: str):
    popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
    popup.open()
    Clock.schedule_once(popup.dismiss, 2)


class ScreenStart(Screen):
    pass


class ScreenAddHub(Screen):
    pass


class ScreenChooseHub(Screen):
    def __init__(self, **kwargs):
        super(ScreenChooseHub, self).__init__(**kwargs)

        # Pobierz dane o hubach z bazy danych (przykład - zastąp tym prawdziwą logiką bazy danych)
        hub_data = db_management.select_all("Huby", "Nazwa")
        print(hub_data)

        grid_layout = GridLayout(cols=7, spacing=30, size_hint=(1, 1 / 6), height=100, pos_hint={'x': 0.3, 'y': 0.5})

        for hub in hub_data:
            button = Button(text=hub, size_hint=(None, None), size=(100, 100))
            # button.background_normal = 'hub-small.png'  # Ustaw obrazek tła przycisku
            button.ip_address = db_management.select("Huby", "AdresIP", ("Nazwa", hub))
            button.mac_address = db_management.select("Huby", "AdresMAC", ("Nazwa", hub))
            # print(button.ip_address)# Przypisz adres IP jako atrybut do przycisku
            button.bind(on_release=self.hub_chosen)  # Przypisz funkcję obsługi zdarzenia przycisku
            grid_layout.add_widget(button)

        self.add_widget(grid_layout)

    def hub_chosen(self, instance):
        # change current hub
        # update lights data
        global chosen_hub
        chosen_hub = str(instance.mac_address)
        print(chosen_hub)
        self.manager.current = 'shape'


class ScreenChooseShape(Screen):
    pass


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
        # load_file can be called multiple times
        self.root = Builder.load_file(r"C:\Users\weron\PycharmProjects\lights\frontend\my.kv")
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(ScreenStart(name='start'))
        sm.add_widget(ScreenLogin(name='login'))
        sm.add_widget(ScreenRegister(name='register'))
        sm.add_widget(ScreenAddHub(name='addhub'))
        sm.add_widget(ScreenChooseHub(name='choose'))
        sm.add_widget(ScreenChooseShape(name='shape'))
        sm.add_widget(ScreenSimulator(name='simulator'))
        print(sys.path)
        return sm


MyApp().run()
