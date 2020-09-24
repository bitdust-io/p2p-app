from kivy.app import App

from kivy.config import Config

from kivy.lang import Builder

#------------------------------------------------------------------------------

from screens import controller

#------------------------------------------------------------------------------ 

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # disable multi-touch
Config.set('graphics', 'resizable', True)
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '740')

#------------------------------------------------------------------------------

Builder.load_string("""
#:import NoTransition kivy.uix.screenmanager.NoTransition
#:import Window kivy.core.window.Window
#:import fa_icon components.webfont.fa_icon
""")

#------------------------------------------------------------------------------

class BitDustApp(App):

    control = None
    main_window = None

    def build(self):
        from components import layouts
        from components import colors
        from components import labels
        from components import buttons
        from components import text_input
        from components import navigation
        from components import main_window

        self.control = controller.Controller(self)
        self.main_window = main_window.MainWindow()
        return self.main_window

    def on_start(self):
        self.main_window.register_screens(controller.all_screens())
        self.main_window.register_controller(self.control)
        self.main_window.select_screen('process_dead_screen')
        self.control.start()

    def on_stop(self):
        self.control.stop()
        self.main_window.unregister_controller()
        self.main_window.unregister_screens()

#------------------------------------------------------------------------------

if __name__ == '__main__':
    BitDustApp().run()
