from kivy.app import App
from kivy.clock import Clock

#------------------------------------------------------------------------------

from components.screen import AppScreen
from screens import controller

#------------------------------------------------------------------------------


KVProcessDeadScreen = """
<ProcessDeadScreen>:
    ScrollView:
        do_scroll_x: False
        GridLayout:
            canvas.before:
                Color:
                    rgba: 1, .9, .9, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            cols: 1
            size_hint: None, None
            width: Window.width - 10
            height: self.minimum_height
            Label:
                color: 0, 0, 0, 1 
                markup: True
                text: '[size=94]dead[/size]'
                height: 200
                size_hint_y: None
"""

class ProcessDeadScreen(AppScreen):

    verify_process_health_task = None

    def get_title(self):
        return 'process dead'

    def on_enter(self, *args):
        self.verify_process_health_task = Clock.schedule_interval(App.get_running_app().control.verify_process_health, 3)

    def on_leave(self, *args):
        Clock.unschedule(self.verify_process_health_task)
        self.verify_process_health_task = None
