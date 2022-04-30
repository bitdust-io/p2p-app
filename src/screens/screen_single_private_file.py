from components import screen

from lib import api_client
from lib import system

from components import snackbar

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

private_file_info_text = """
[size={header_text_size}]{path}[/size]
[size={text_size}]
[color=#909090]remote_path:[/color] {remote_path}
[color=#909090]global_id:[/color] {global_id}
[color=#909090]size:[/color] {size_text}
[/size]
"""


class SinglePrivateFileScreen(screen.AppScreen):

    def __init__(self, **kwargs):
        self.global_id = ''
        self.remote_path = ''
        super(SinglePrivateFileScreen, self).__init__(**kwargs)

    def init_kwargs(self, **kw):
        self.global_id = kw.pop('global_id', '')
        self.remote_path = kw.pop('remote_path', '')
        if _Debug:
            print('SinglePrivateFileScreen.init_kwargs', kw)
        return kw

    def populate(self, **kwargs):
        api_client.file_info(
            remote_path=self.remote_path,
            cb=self.on_private_file_info_result,
        )

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='service_my_data')
        self.populate()

    def on_leave(self, *args):
        self.ids.state_panel.release()

    def on_private_file_info_result(self, resp):
        if not api_client.is_ok(resp):
            snackbar.error(text=api_client.response_err(resp))
            return
        result = api_client.response_result(resp)
        result.update(
            text_size='{}sp'.format(self.app().font_size_normal_absolute),
            header_text_size='{}sp'.format(self.app().font_size_large),
            remote_path=self.remote_path,
            global_id=self.global_id,
            size_text=system.get_nice_size(result['size']),
        )
        if _Debug:
            print('SinglePrivateFileScreen.on_private_file_info_result', result)
        self.ids.private_file_details.text = private_file_info_text.format(**result)

    def on_download_file_button_clicked(self):
        if _Debug:
            print('SinglePrivateFileScreen.on_download_file_button_clicked')
        api_client.file_download_start(remote_path=self.remote_path, cb=self.on_file_download_started)

    def on_delete_file_button_clicked(self):
        if _Debug:
            print('SinglePrivateFileScreen.on_delete_file_button_clicked')
        api_client.file_delete(remote_path=self.remote_path, cb=self.on_file_deleted)

    def on_file_deleted(self, resp):
        if _Debug:
            print('SinglePrivateFileScreen.on_file_deleted', resp)
        if not api_client.is_ok(resp):
            snackbar.error(text='file delete failed: %s' % api_client.response_err(resp))
        else:
            snackbar.success(text='file deleted')
        screen.select_screen('private_files_screen')

    def on_file_download_started(self, resp):
        if _Debug:
            print('SinglePrivateFileScreen.on_file_download_started', resp)
        if not api_client.is_ok(resp):
            snackbar.error(text='download file failed: %s' % api_client.response_err(resp))
        else:
            snackbar.success(text='file download started')
        screen.select_screen('private_files_screen')
