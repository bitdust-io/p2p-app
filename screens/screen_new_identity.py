from components.screen import AppScreen


class NewIdentityScreen(AppScreen):

    def is_closable(self):
        return False

    def on_create_identity_button_clicked(self, *args):
        pass

    def on_recover_identity_button_clicked(self, *args):
        self.main_win().select_screen('recover_identity_screen')


from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_new_identity.kv')
