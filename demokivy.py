from random import randint

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.widget import Widget

from kivy.properties import ListProperty, ObjectProperty

from kivy.uix.codeinput import CodeInput
from kivy.extras.highlight import KivyLexer

from configurehue import UserLayer, Manager

class ScanResult(FloatLayout):
    results = ListProperty([{'hostname':r} for r in ['10.161.129.197','10.161.129.1']*10])

    def __init__(self, cm):
        self.cm = cm
        super().__init__()

    def schedulable_get(self):
        self.hues = self.cm.get()
        self.results.clear()
        for hue in self.hues.values():
            self.results.append({'hostname':hue.hostname,
                                 'username':hue.username
            })

    def scan(self):
        import asyncio
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self.schedulable_get)


class LinkPopup(Popup):
    pass


class KivyInterface(UserLayer):
    def __init__(self, p):
        self.popupz = p
        self.popupz.bind(on_dismiss=self._kv_popup_dismissed)
    def prompt_for_button(self):
        self.dismissed = False
        self.popupz.open()
        while not self.dismissed:
            Clock.usleep(1000)
    def message_not_pressed(self):
        pass
        # raise NotImplementedError
    def _kv_popup_dismissed(self, _):
        self.dismissed = True


class DeviceListApp(App):
    def build(self):
        # TODO: why must this be instantiated here to get formatting?
        p = LinkPopup()
        z = Manager(userlayer=KivyInterface(p))
        demo = ScanResult(z)
        return demo


if __name__ == '__main__':
    DeviceListApp().run()