from lib import api_client

from components import webfont
from components import screen
from components import buttons
from components import labels

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class WelcomeScreen(screen.AppScreen):

    def get_statuses(self):
        return {
            None: '',
            'AT_STARTUP': 'starting',
            'LOCAL': 'initializing local environment',
            'MODULES': 'starting sub-modules',
            'INSTALL': 'installing application',
            'READY': 'application is ready',
            'STOPPING': 'application is shutting down',
            'SERVICES': 'starting network services',
            'INTERFACES': 'starting application interfaces',
            'EXIT': 'application is closed',
        }

    def populate(self):
        process_health = self.main_win().state_process_health
        identity_get = self.main_win().state_identity_get
        network_connected = self.main_win().state_network_connected
        if _Debug:
            print('WelcomeScreen.populate process_health=%r identity_get=%r network_connected=%r' % (
                process_health, identity_get, network_connected, ))
        if process_health != 1:
            self.ids.spinner.start(label='starting')
            for w in self.ids.central_widget.children:
                if isinstance(w, buttons.FillRoundFlatButton):
                    self.ids.central_widget.remove_widget(w)
                if isinstance(w, labels.HFlexMarkupLabel):
                    self.ids.central_widget.remove_widget(w)
            if _Debug:
                print('    spinner starting, removed widgets')
        else:
            if identity_get == 0:
                self.ids.spinner.start(label='starting')
                for w in self.ids.central_widget.children:
                    if isinstance(w, buttons.FillRoundFlatButton):
                        self.ids.central_widget.remove_widget(w)
                    if isinstance(w, labels.HFlexMarkupLabel):
                        self.ids.central_widget.remove_widget(w)
                if _Debug:
                    print('    spinner starting, removed widgets')
            else:
                if identity_get == -1:
                    self.ids.spinner.stop()
                    if _Debug:
                        print('    spinner stopped')
                    btn_exists = False
                    for w in self.ids.central_widget.children:
                        if isinstance(w, buttons.FillRoundFlatButton):
                            btn_exists = True
                            break
                    if not btn_exists:
                        btn = buttons.FillRoundFlatButton(
                            text="[size=22sp]{}[/size]  [size=16sp][b]create new identity[/b][/size]".format(webfont.md_icon("account-plus")),
                            pos_hint={'center_x': .5},
                            md_bg_color=self.app().color_success_green,
                            text_color=self.app().color_white99,
                            on_release=self.on_create_identity_button_clicked,
                        )
                        lbl = labels.HFlexMarkupLabel(
                            pos_hint={'center_x': .5},
                            markup=True,
                            text="[u][color=#0000ff][ref=link]restore existing identity[/ref][/color][/u]",
                        )
                        lbl.bind(on_ref_press=self.on_restore_existing_identity_pressed)
                        self.ids.central_widget.add_widget(btn)
                        self.ids.central_widget.add_widget(lbl)
                        if _Debug:
                            print('    added create/restore identity buttons')
                else:
                    for w in self.ids.central_widget.children:
                        if isinstance(w, buttons.FillRoundFlatButton):
                            self.ids.central_widget.remove_widget(w)
                        if isinstance(w, labels.HFlexMarkupLabel):
                            self.ids.central_widget.remove_widget(w)
                    if _Debug:
                        print('    removed widgets')
                    if network_connected != 1:
                        self.ids.spinner.start(label='connecting')
                        if _Debug:
                            print('    spinner connecting')
                    else:
                        self.ids.spinner.stop()
                        if _Debug:
                            print('    spinner stopped')
                        if identity_get == 1:
                            link_exists = False
                            for w in self.ids.central_widget.children:
                                if isinstance(w, labels.HFlexMarkupLabel):
                                    if w.text.count('search people'):
                                        link_exists = True
                                        break
                            if not link_exists:
                                link_search_people = labels.HFlexMarkupLabel(
                                    pos_hint={'center_x': .5}, markup=True,
                                    text="[u][color=#0000ff][ref=link]search people[/ref][/color][/u]",
                                )
                                link_search_people.bind(on_ref_press=self.on_search_people_link_pressed)
                                self.ids.central_widget.add_widget(link_search_people)
                                link_chat = labels.HFlexMarkupLabel(
                                    pos_hint={'center_x': .5}, markup=True,
                                    text="[u][color=#0000ff][ref=link]chat with friends[/ref][/color][/u]",
                                )
                                link_chat.bind(on_ref_press=self.on_chat_with_friends_link_pressed)
                                self.ids.central_widget.add_widget(link_chat)
                                link_upload_file = labels.HFlexMarkupLabel(
                                    pos_hint={'center_x': .5}, markup=True,
                                    text="[u][color=#0000ff][ref=link]upload a file[/ref][/color][/u]",
                                )
                                link_upload_file.bind(on_ref_press=self.on_upload_file_link_pressed)
                                self.ids.central_widget.add_widget(link_upload_file)
                                link_share_file = labels.HFlexMarkupLabel(
                                    pos_hint={'center_x': .5}, markup=True,
                                    text="[u][color=#0000ff][ref=link]share a file[/ref][/color][/u]",
                                )
                                link_share_file.bind(on_ref_press=self.on_share_file_link_pressed)
                                self.ids.central_widget.add_widget(link_share_file)
                                if _Debug:
                                    print('    added links')

    def on_search_people_link_pressed(self, instance, value):
        screen.select_screen('search_people_screen')

    def on_chat_with_friends_link_pressed(self, instance, value):
        screen.select_screen('conversations_screen')

    def on_upload_file_link_pressed(self, instance, value):
        screen.select_screen('private_files_screen')

    def on_share_file_link_pressed(self, instance, value):
        screen.select_screen('shares_screen')

    def call_identity_get(self):
        api_client.identity_get(cb=self.on_identity_get_result)

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='initializer')
    
    def on_leave(self, *args):
        self.ids.state_panel.release()

    def on_nav_button_clicked(self):
        pass

    def on_create_identity_button_clicked(self, *args):
        screen.select_screen('new_identity_screen')

    def on_identity_get_result(self, resp):
        if _Debug:
            print('WelcomeScreen.on_identity_get_result', self.main_win().state_process_health, self.main_win().state_identity_get, resp)
        if self.main_win().state_process_health == 1 and self.main_win().state_identity_get != 1 and not api_client.is_ok(resp):
            self.populate()
        else:
            if self.main_win().state_process_health != 1:
                self.populate()
            else:
                self.populate()

    def on_upload_file_button_clicked(self, *args):
        if _Debug:
            print('WelcomeScreen.on_upload_file_button_clicked', args)

    def on_restore_existing_identity_pressed(self, instance, value):
        screen.select_screen('recover_identity_screen')
