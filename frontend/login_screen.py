from kivy.uix.label import Label

from kivy.animation import Animation
from kivy.lang import Builder
from kivy.properties import ObjectProperty
import sqlite3
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, NoTransition, Screen
from kivymd.app import MDApp
from kivymd.uix.behaviors import CircularRippleBehavior, CommonElevationBehavior, RectangularRippleBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.widget import MDWidget


def show_popup(message):
    popup = Popup(title='Rejestracja', content=Label(text=message), size_hint=(None, None), size=(400, 400))
    popup.open()


class ScreenLogin(Screen):
    def login(self):
        username = self.ids.username.text
        password = self.ids.password.text

        self.cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = self.cursor.fetchone()

        if user:
            self.parent.current = 'screenwelcome'
        else:
            self.show_popup("Błąd logowania")


# def show_popup(self, message):
#     popup = Popup(title='Logowanie', content=Label(text="eeee"))
#     popup.open()


class ScreenRegister(Screen):

    # scr_mng = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenRegister, self).__init__(**kwargs)
        self.conn = sqlite3.connect('users.db')  # Połączenie z bazą danych
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        email TEXT,
                        password TEXT
                    )
                ''')
        self.conn.commit()

    def register(self):
        if self.ids.password.text == self.ids.confirm_password.text:
            try:
                self.cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                                    (self.ids.username.text, self.ids.email.text, self.ids.password.text))
                self.conn.commit()
                show_popup("Rejestracja zakończona pomyślnie")
                self.manager.current = 'login'
            except sqlite3.IntegrityError:
                show_popup("Użytkownik o takiej nazwie już istnieje")
        else:
            show_popup("Hasła się różnią")


sm = ScreenManager(transition=NoTransition())
sm.add_widget(ScreenLogin(name='login'))
sm.add_widget(ScreenRegister(name='register'))


class MyApp(MDApp):
    def build(self):
        pass

        # m = Manager(transition=NoTransition())
    # return m


MyApp().run()
