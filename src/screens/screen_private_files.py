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

class PrivateFileItem(TwoLineIconListItem):

    type = StringProperty()
    name = StringProperty()
    global_id = StringProperty()
    remote_path = StringProperty()
    customer = StringProperty()
    size = NumericProperty(0)

    def get_secondary_text(self):
        sec_text = ''
        if _Debug:
            print('PrivateFileItem.get_secondary_text', self.global_id, sec_text)
        return '[color=dddf]%s[/color]' % sec_text

    def on_pressed(self):
        if _Debug:
            print('PrivateFileItem.on_pressed', self)


class UploadPrivateFile(OneLineIconListItem):

    def on_pressed(self):
        if _Debug:
            print('UploadPrivateFile.on_pressed', self)


class PrivateFilesScreen(screen.AppScreen):

    def get_title(self):
        return 'private files'

    # def get_icon(self):
    #     return 'file-lock'

    def get_statuses(self):
        return {
            None: 'files are not available at the moment',
            'ON': 'distributed storage is ready',
            'OFF': 'private storage service is not started',
            'NOT_INSTALLED': 'private storage service was not installed',
            'INFLUENCE': 'verifying related network services',
            'DEPENDS_OFF': 'related network services not yet started',
            'STARTING': 'starting distributed private storage service',
            'STOPPING': 'turning off distributed private storage service',
            'CLOSED': 'private storage service is stopped',
        }

    def populate(self, *args, **kwargs):
        pass

    def on_created(self):
        self.ids.files_list_view.init(
            file_system_type='private',
            file_clicked_callback=self.on_file_clicked,
        )

    def on_destroying(self):
        self.ids.files_list_view.shutdown()

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='service_my_data', callback_start=self.on_state_panel_attach)

    def on_leave(self, *args):
        self.ids.files_list_view.close()
        self.ids.state_panel.release(callback_stop=self.on_state_panel_release)

    def on_state_panel_attach(self, resp):
        if api_client.is_ok(resp):
            self.ids.files_list_view.open()

    def on_state_panel_release(self, resp):
        pass

    @mainthread
    def on_upload_file_button_clicked(self, *args):
        if _Debug:
            print('PrivateFilesScreen.on_upload_file_button_clicked', args)
        if system.is_android():
            from lib import filechooser as lib_filechooser
            raw_path = lib_filechooser.open_file(
                title="Upload a file",
                preview=True,
                show_hidden=False,
                on_selection=self.on_upload_file_selected,
            )
        else:
            from plyer import filechooser
            if system.is_windows():
                self._latest_cwd = os.getcwd()
            raw_path = filechooser.open_file(
                title="Upload a file",
                preview=True,
                show_hidden=False,
                on_selection=self.on_upload_file_selected,
            )
        if _Debug:
            print('raw_path', raw_path)

    def on_upload_file_selected(self, *args, **kwargs):
        if _Debug:
            print('PrivateFilesScreen.on_upload_file_selected', args, kwargs)
        if system.is_windows():
            try:
                os.chdir(self._latest_cwd)
            except:
                pass
        file_path = args[0][0]
        file_name = os.path.basename(file_path)
        api_client.file_create(
            remote_path=file_name,
            as_folder=False,
            exist_ok=True,
            cb=lambda resp: self.on_file_created(resp, file_path),
        )

    def on_file_created(self, resp, file_path):
        if _Debug:
            print('PrivateFilesScreen.on_file_created', file_path, resp)
        if not api_client.is_ok(resp):
            snackbar.error(text=api_client.response_err(resp))
            return
        file_name = os.path.basename(file_path)
        api_client.file_upload_start(
            local_path=file_path,
            remote_path=file_name,
            cb=self.on_upload_file_started,
        )

    def on_upload_file_started(self, resp):
        if _Debug:
            print('PrivateFilesScreen.on_upload_file_started', resp)

    def on_file_clicked(self, *args, **kwargs):
        if _Debug:
            print('PrivateFilesScreen.on_file_clicked', args[0])
        api_client.file_info(
            remote_path=args[0].remote_path,
            cb=lambda resp: self.on_private_file_info_result(resp, args[0].remote_path, args[0].global_id),
        )

    def on_private_file_info_result(self, resp, remote_path, global_id):
        if not api_client.is_ok(resp):
            snackbar.error(text=api_client.response_err(resp))
            return
        screen.select_screen(
            screen_id='private_file_{}'.format(global_id),
            screen_type='single_private_file_screen',
            global_id=global_id,
            remote_path=remote_path,
            details=api_client.response_result(resp),
        )
