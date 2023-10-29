from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, NoTransition, Screen, SlideTransition, FadeTransition
from kivymd.app import MDApp

def show_popup(message):
    popup = Popup(title='Rejestracja', content=Label(text=message), size_hint=(None, None), size=(400, 400))
    popup.open()

class ScreenStart(Screen):
    pass

class ScreenAddHub(Screen):
    pass

class ScreenLogin(Screen):
    pass


class ScreenRegister(Screen):
    pass


sm = ScreenManager(transition=FadeTransition())
sm.add_widget(ScreenLogin(name='login'))
sm.add_widget(ScreenRegister(name='register'))
sm.add_widget(ScreenStart(name='start'))


class MyApp(MDApp):
    def build(self):
        pass


MyApp().run()
