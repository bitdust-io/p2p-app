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
        self.ids.state_panel.attach(automat_id='service_my_data')

    def on_leave(self, *args):
        self.ids.state_panel.release()

#     def on_private_file(self, payload):
#         if _Debug:
#             print('PrivateFilesScreen.on_private_file', payload)
# 
#     def on_remote_version(self, payload):
#         if _Debug:
#             print('PrivateFilesScreen.on_remote_version', payload)

    @mainthread
    def on_upload_file_button_clicked(self, *args):
        if _Debug:
            print('PrivateFilesScreen.on_upload_file_button_clicked', args)
        from lib import system
        if system.is_android():
            from lib import filechooser as lib_filechooser
            raw_path = lib_filechooser.instance().open_file(
                title="Upload new file",
                preview=True,
                show_hidden=False,
                on_selection=self.on_upload_file_selected,
            )
        else:
            from plyer import filechooser
            raw_path = filechooser.open_file(
                title="Upload new file",
                preview=True,
                show_hidden=False,
                on_selection=self.on_upload_file_selected,
            )
        if _Debug:
            print('raw_path', raw_path)

    def on_upload_file_selected(self, *args, **kwargs):
        if _Debug:
            print('PrivateFilesScreen.on_upload_file_selected', args, kwargs)
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
