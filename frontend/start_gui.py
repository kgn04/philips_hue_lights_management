import sys

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
    popup = Popup(title=title, content=Label(text=message), size_hint=(1/2, 1/4))
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
                           pos_hint={'x': 0.1, 'y': 0.4}, size_hint=(3/4,1/2))
        #layout.size = (300, 400)

        hubs_available = self.find_hubs_to_add()
        for hub in hubs_available:
            ip_address = hub[0]
            mac_address = hub[1]

            # układ poziomy dla jednego huba
            hub_layout = BoxLayout(orientation='horizontal', spacing=70, size_hint=(1,3/4))

            # adres MAC
            mac_label = Label(text=f"Adres MAC: {mac_address}", size_hint=(1/3,1/10),
                              color="deepskyblue")
            hub_layout.add_widget(mac_label)

            #  adres IP
            ip_label = Label(text=f"Adres IP: {ip_address}", size_hint=(1/3,1/10),
                             color="deepskyblue")
            hub_layout.add_widget(ip_label)

            add_button = MDFillRoundFlatButton(text="Dodaj", size_hint=(1/5,1/3),
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
        self.manager.add_widget(ScreenChooseShape( name='shape'))
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
    def __init__(self,  **kw):
        #  super(ScreenChooseShape, self, hub_data,).__init__(**kwargs)
        super(ScreenChooseShape,self).__init__(**kw)
        #self.hub_data = hub_data  # Pobierz dane z bazy lub przykładowe dane (ilość możliwych kombinacji siatek)
        data_from_database = [
            {"label": "4x4", "selected": False},
            {"label": "2x8", "selected": False},
            {"label": "6x6", "selected": False},
            {"label": "4x4", "selected": False},
            {"label": "2x8", "selected": False},
            {"label": "6x6", "selected": False},
            {"label": "4x4", "selected": False},
            {"label": "2x8", "selected": False},
            {"label": "6x6", "selected": False},
            {"label": "4x4", "selected": False},
            {"label": "2x8", "selected": False},
            {"label": "6x6", "selected": False},
        ]

        # Wyczyść aktualne checkboxy (jeśli istnieją)
        checkboxes_layout = GridLayout(cols=6, pos_hint={'x': 0, 'y': 0.45}, height=200, size_hint=(1, 1 / 4))

        # Wygeneruj dynamicznie checkboxy i ich opisy na podstawie danych
        for item in data_from_database:
            checkbox = CheckBox(size=(20, 20), width=50, height=50)
            checkbox.active = item["selected"]

            label = Label(text=item["label"])
            checkboxes_layout.add_widget(checkbox)
            checkboxes_layout.add_widget(label)

        self.add_widget(checkboxes_layout)

        for item in data_from_database:
            checkbox.bind(active=self.checkbox_changed)

    def checkbox_changed(self, instance, value):
        pass

    # Funkcja obsługi zdarzenia po zaznaczeniu checkboxa
    # print(f"Checkbox z tekstem '{instance.parent.children[1].text}' został zaznaczony: {value}")

    def add_hub_to_database(self):
        db_management.insert("Huby", ())


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
