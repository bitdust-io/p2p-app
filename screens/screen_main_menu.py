from kivy.app import App

from kivy.uix.screenmanager import Screen

from components import buttons


KVMainMenuScreen = """
<MainMenuScreen>:
    GridLayout:
        cols: 1
        padding: 10
        spacing: 2
        row_force_default: True
        row_default_height: 40
        Button:
            text: 'menuA'
            on_press: root.on_menu_item_clicked()
"""

class MainMenuScreen(Screen):

    counter = 0

    def on_menu_item_clicked(self):
        app = App.get_running_app()
        if app:
            self.counter += 1
            screen = Screen(name='screen_%d' % self.counter)
            screen.add_widget(buttons.Button(text='Title %d' % self.counter))
            app.root.ids.screen_manager.add_widget(screen)
            btn = buttons.NavButton(
                id='nav_btn_%d' % self.counter,
                text='title %d: %s' % (self.counter, 'a' * self.counter),
                screen='screen_%d' % self.counter,
            )
            app.root.ids.nav_buttons_layout.add_widget(btn)
            app.root.ids.screen_manager.current = 'screen_%d' % self.counter
