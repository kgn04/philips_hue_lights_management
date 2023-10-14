from kivy.animation import Animation
from kivy.properties import ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivymd.app import MDApp
from kivymd.uix.behaviors import CircularRippleBehavior, CommonElevationBehavior, RectangularRippleBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.widget import MDWidget

class Manager(ScreenManager):

    screen_one = ObjectProperty(None)
    screen_two = ObjectProperty(None)


class ScreenLogin(MDScreen):
    pass


class ScreenRegister(MDScreen):

    def __init__(self, **kwargs):
        super(ScreenRegister, self).__init__(**kwargs)

    def changeScreen(self):
        if self.manager.current == 'screenlogin':
            self.manager.current = 'screen2'
        else:
            self.manager.current = 'screen1'

class MyApp(MDApp):
    def build(self):
        m = Manager(transition=NoTransition())
        return m

    def login(self):
        # Tutaj dodaj logikę logowania
        pass

    def register(self):
        # Tutaj dodaj logikę rejestracji
        pass


MyApp().run()
