import os

from kivy.clock import mainthread
from kivy.properties import StringProperty, NumericProperty  # @UnresolvedImport

from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.list import TwoLineIconListItem

from lib import api_client

from components import screen
from components import snackbar

#------------------------------------------------------------------------------

_Debug = True

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
        # self.ids.state_panel.attach(automat_id='service_shared_data')
        self.ids.state_panel.attach(automat_id=self.automat_id)

    def on_leave(self, *args):
        self.ids.state_panel.release()

#     def on_shared_file(self, payload):
#         if _Debug:
#             print('SharedLocationScreen.on_shared_file', payload)
# 
#     def on_remote_version(self, payload):
#         if _Debug:
#             print('SharedLocationScreen.on_remote_version', payload)

    @mainthread
    def on_upload_file_button_clicked(self, *args):
        if _Debug:
            print('SharedLocationScreen.on_upload_file_button_clicked', args)
        from lib import system
        if system.is_android():
            from lib import filechooser as lib_filechooser
            raw_path = lib_filechooser.instance().open_file(
                title="Share new file",
                preview=True,
                show_hidden=False,
                on_selection=self.on_upload_file_selected,
            )
        else:
            from plyer import filechooser
            raw_path = filechooser.open_file(
                title="Share new file",
                preview=True,
                show_hidden=False,
                on_selection=self.on_upload_file_selected,
            )
        if _Debug:
            print('raw_path', raw_path)

    def on_upload_file_selected(self, *args, **kwargs):
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
            snackbar.success(text='access granted for user %s' % user_global_id)
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
        elif btn.icon == 'lan-check':
            api_client.share_open(
                key_id=self.key_id,
                cb=self.on_share_open_result,
            )

    def on_share_open_result(self, resp):
        if _Debug:
            print('SharedLocationScreen.on_share_delete_result', resp)
        if api_client.is_ok(resp):
            snackbar.success(text='shared location synchronized')
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
