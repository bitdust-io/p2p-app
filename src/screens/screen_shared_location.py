import os

from kivy.clock import mainthread
from kivy.properties import StringProperty, NumericProperty  # @UnresolvedImport

from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.list import TwoLineIconListItem

from lib import api_client
from lib import system

from components import screen
from components import snackbar

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class SharedFileItem(TwoLineIconListItem):

    type = StringProperty()
    name = StringProperty()
    global_id = StringProperty()
    remote_path = StringProperty()
    customer = StringProperty()
    size = NumericProperty(0)

    def get_secondary_text(self):
        sec_text = ''
        if _Debug:
            print('SharedFileItem.get_secondary_text', self.global_id, sec_text)
        return '[color=dddf]%s[/color]' % sec_text

    def on_pressed(self):
        if _Debug:
            print('SharedFileItem.on_pressed', self)


class UploadSharedFile(OneLineIconListItem):

    def on_pressed(self):
        if _Debug:
            print('UploadSharedFile.on_pressed', self)


class SharedLocationScreen(screen.AppScreen):

    def __init__(self, **kwargs):
        self.key_id = ''
        self.label = ''
        self.automat_index = None
        self.automat_id = None
        super(SharedLocationScreen, self).__init__(**kwargs)

    def init_kwargs(self, **kw):
        if not self.key_id and kw.get('key_id'):
            self.key_id = kw.pop('key_id', '')
        if not self.label and kw.get('label'):
            self.label = kw.pop('label', '')
        if 'automat_index' in kw:
            self.automat_index = kw.pop('automat_index', None)
        if 'automat_id' in kw:
            self.automat_id = kw.pop('automat_id', None)
        return kw

    def get_title(self):
        return self.label

    # def get_icon(self):
    #     return 'file-lock'

    def get_statuses(self):
        return {
            None: 'shared location is currently inactive',
            'AT_STARTUP': 'shared location is currently inactive',
            'DHT_LOOKUP': 'connecting to the distributed hash table',
            'SUPPLIERS?': 'connecting with remote suppliers',
            'DISCONNECTED': 'shared location is disconnected',
            'CONNECTED': 'shared location is synchronized',
            'CLOSED': 'shared location is not active',
        }

    def populate(self, *args, **kwargs):
        pass

    def on_created(self):
        self.ids.files_list_view.init(
            file_system_type='shared',
            key_id=self.key_id,
            file_clicked_callback=self.on_file_clicked,
        )

    def on_destroying(self):
        self.ids.files_list_view.shutdown()

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id=self.automat_id, callback_start=self.on_state_panel_attach)

    def on_leave(self, *args):
        self.ids.files_list_view.close()
        self.ids.state_panel.release(callback_stop=self.on_state_panel_release)

    def on_state_panel_attach(self, resp):
        if _Debug:
            print('SharedLocationScreen.on_state_panel_attach', resp)
        if api_client.is_ok(resp):
            if api_client.result(resp)['active']:
                self.ids.files_list_view.open()
                self.ids.upload_file_button.disabled = False
                self.ids.upload_file_button.md_bg_color = self.app().theme_cls.accent_color
                return
        self.ids.upload_file_button.disabled = True
        self.ids.files_list_view.close()

    def on_state_panel_release(self, resp):
        pass

    @mainthread
    def on_upload_file_button_clicked(self, *args):
        if _Debug:
            print('SharedLocationScreen.on_upload_file_button_clicked', args)
        if system.is_android():
            from lib import filechooser_android
            raw_path = filechooser_android.open_file(
                title="Share a file",
                preview=True,
                show_hidden=False,
                on_selection=self.on_upload_file_selected,
            )
        elif system.is_osx():
            from lib import filechooser_macosx
            fc = filechooser_macosx.MacFileChooser(
                title="Share a file",
                preview=True,
                show_hidden=False,
                on_selection=self.on_upload_file_selected,
            )
            raw_path = fc.run()
        else:
            from plyer import filechooser
            if system.is_windows():
                self._latest_cwd = os.getcwd()
            raw_path = filechooser.open_file(
                title="Share a file",
                preview=True,
                show_hidden=False,
                on_selection=self.on_upload_file_selected,
            )
        if _Debug:
            print('    raw_path', raw_path)

    def on_upload_file_selected(self, *args, **kwargs):
        if _Debug:
            print('SharedLocationScreen.on_upload_file_selected', args, kwargs)
        if system.is_windows():
            try:
                os.chdir(self._latest_cwd)
            except:
                pass
        file_path = args[0][0]
        file_name = os.path.basename(file_path)
        remote_path = '{}:{}'.format(self.key_id, file_name)
        if _Debug:
            print('SharedLocationScreen.on_upload_file_selected', args, kwargs, remote_path)
        api_client.file_create(
            remote_path=remote_path,
            as_folder=False,
            exist_ok=True,
            cb=lambda resp: self.on_file_created(resp, file_path, remote_path),
        )

    def on_file_created(self, resp, file_path, remote_path):
        if _Debug:
            print('SharedLocationScreen.on_file_created', file_path, remote_path, resp)
        if not api_client.is_ok(resp):
            snackbar.error(text=api_client.response_err(resp))
            return
        api_client.file_upload_start(
            local_path=file_path,
            remote_path=remote_path,
            cb=self.on_upload_file_started,
        )

    def on_upload_file_started(self, resp):
        if _Debug:
            print('SharedLocationScreen.on_upload_file_started', resp)

    def on_file_clicked(self, *args, **kwargs):
        if _Debug:
            print('SharedLocationScreen.on_file_clicked', args[0])
        api_client.file_info(
            remote_path=args[0].remote_path,
            cb=lambda resp: self.on_shared_file_info_result(resp, args[0].remote_path, args[0].global_id),
        )

    def on_shared_file_info_result(self, resp, remote_path, global_id):
        if not api_client.is_ok(resp):
            snackbar.error(text=api_client.response_err(resp))
            return
        screen.select_screen(
            screen_id='shared_file_{}'.format(global_id),
            screen_type='single_shared_file_screen',
            global_id=global_id,
            remote_path=remote_path,
            details=api_client.response_result(resp),
        )

    def on_grant_access_button_clicked(self, *args):
        if _Debug:
            print('SharedLocationScreen.on_grant_access_button_clicked', args)
        if self.model('correspondent'):
            self.main_win().select_screen(
                screen_id='select_friend_screen',
                result_callback=self.on_grant_access_user_selected,
                screen_header='Select user to be granted access to the shared location [b]%s[/b]:' % self.label,
            )
        else:
            self.main_win().select_screen(screen_id='friends_screen')

    def on_grant_access_user_selected(self, user_global_id):
        if _Debug:
            print('SharedLocationScreen.on_grant_access_user_selected', user_global_id)
        screen.select_screen(
            screen_id='shared_location_{}'.format(self.key_id),
            screen_type='shared_location_screen',
            key_id=self.key_id,
            label=self.label,
        )
        self.main_win().close_screen(screen_id='select_friend_screen')
        api_client.share_grant(
            key_id=self.key_id,
            trusted_user_id=user_global_id,
            cb=lambda resp: self.on_grant_access_result(resp, user_global_id),
        )

    def on_grant_access_result(self, resp, user_global_id):
        if _Debug:
            print('SharedLocationScreen.on_grant_access_result', resp)
        if api_client.is_ok(resp):
            snackbar.success(text='access granted')
        else:
            snackbar.error(text=api_client.response_err(resp))

    def on_drop_down_menu_item_clicked(self, btn):
        if _Debug:
            print('SharedLocationScreen.on_drop_down_menu_item_clicked', btn.icon)
        if btn.icon == 'information':
            self.main_win().select_screen(
                screen_id='shared_location_info_{}'.format(self.key_id),
                screen_type='shared_location_info_screen',
                key_id=self.key_id,
                label=self.label,
                automat_index=self.automat_index,
                automat_id=self.automat_id,
            )
        elif btn.icon == 'trash-can-outline':
            api_client.share_delete(
                key_id=self.key_id,
                cb=lambda resp: self.on_share_delete_result(resp, self.key_id),
            )
        elif btn.icon == 'folder-cancel':
            api_client.share_close(
                key_id=self.key_id,
                cb=lambda resp: self.on_share_close_result(resp, self.key_id),
            )
        elif btn.icon == 'folder-open':
            api_client.share_open(
                key_id=self.key_id,
                cb=self.on_share_open_result,
            )

    def on_share_open_result(self, resp):
        if _Debug:
            print('SharedLocationScreen.on_share_open_result', resp)
        if api_client.is_ok(resp):
            snackbar.success(text='shared location connected')
            self.ids.state_panel.release()
            self.ids.state_panel.attach(automat_id=api_client.result(resp)['id'], callback_start=self.on_state_panel_attach)
            api_client.request_model_data('shared_file', query_details={'key_id': self.key_id, })
        else:
            snackbar.error(text=api_client.response_err(resp))

    def on_share_close_result(self, resp, key_id):
        if _Debug:
            print('SharedLocationScreen.on_share_close_result', resp)
        if api_client.is_ok(resp):
            self.ids.upload_file_button.disabled = True
            self.ids.files_list_view.close()
            snackbar.success(text='shared location closed')
        else:
            snackbar.error(text=api_client.response_err(resp))

    def on_share_delete_result(self, resp, key_id):
        if _Debug:
            print('SharedLocationScreen.on_share_delete_result', resp)
        if not api_client.is_ok(resp):
            snackbar.error(text=api_client.response_err(resp))
        else:
            self.main_win().select_screen('shares_screen')
            self.main_win().close_screen(screen_id='shared_location_{}'.format(key_id))
            snackbar.success(text='shared location deleted')
