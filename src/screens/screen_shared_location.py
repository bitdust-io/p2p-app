import os

from kivy.clock import mainthread
from kivy.properties import StringProperty, NumericProperty  # @UnresolvedImport

from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.list import TwoLineIconListItem

from lib import api_client

from components import screen

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

    def get_title(self):
        return 'shared files'

    # def get_icon(self):
    #     return 'file-lock'

    def populate(self, *args, **kwargs):
        pass

    def on_created(self):
        self.ids.files_list_view.init(file_clicked_callback=self.on_file_clicked)

    def on_destroying(self):
        self.ids.files_list_view.shutdown()

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='service_shared_data')

    def on_leave(self, *args):
        self.ids.state_panel.release()

    def on_shared_file(self, payload):
        if _Debug:
            print('SharedLocationScreen.on_shared_file', payload)

    def on_remote_version(self, payload):
        if _Debug:
            print('SharedLocationScreen.on_remote_version', payload)

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
        if _Debug:
            print('SharedLocationScreen.on_upload_file_selected', args, kwargs)
        file_path = args[0][0]
        file_name = os.path.basename(file_path)
        # api_client.file_create(
        #     remote_path=file_name,
        #     as_folder=False,
        #     exist_ok=True,
        #     cb=lambda resp: self.on_file_created(resp, file_path),
        # )

    def on_file_created(self, resp, file_path):
        if _Debug:
            print('SharedLocationScreen.on_file_created', file_path, resp)
        file_name = os.path.basename(file_path)
        # api_client.file_upload_start(
        #     local_path=file_path,
        #     remote_path=file_name,
        #     cb=self.on_upload_file_started,
        # )

    def on_upload_file_started(self, resp):
        if _Debug:
            print('SharedLocationScreen.on_upload_file_started', resp)

    def on_file_clicked(self, *args, **kwargs):
        if _Debug:
            print('SharedLocationScreen.on_file_clicked', args[0])
        # screen.select_screen(
        #     screen_id='shared_file_{}'.format(args[0].global_id),
        #     screen_type='single_private_file_screen',
        #     global_id=args[0].global_id,
        #     remote_path=args[0].remote_path,
        # )
