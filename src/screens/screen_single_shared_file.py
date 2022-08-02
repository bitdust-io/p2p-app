from components import screen

from lib import api_client
from lib import system

from components import snackbar

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

shared_file_info_text = """
[size={header_text_size}]{path}[/size]
[size={text_size}]
[color=#909090]remote path:[/color] {remote_path}
[color=#909090]global ID:[/color] {global_id}
[color=#909090]size:[/color] {size_text}
{versions_text}
[/size]
"""

version_info_text = """
[size={header_text_size}]{label}[/size]
[color=#909090]    fragments:[/color] {fragments}
[color=#909090]    delivered:[/color] {delivered}
[color=#909090]    reliable:[/color] {reliable}
"""


class SingleSharedFileScreen(screen.AppScreen):

    def __init__(self, **kwargs):
        self.global_id = ''
        self.remote_path = ''
        self.details = {}
        super(SingleSharedFileScreen, self).__init__(**kwargs)

    def init_kwargs(self, **kw):
        if _Debug:
            print('SingleSharedFileScreen.init_kwargs', kw)
        self.global_id = kw.pop('global_id', '')
        self.remote_path = kw.pop('remote_path', '')
        self.details = kw.pop('details', {})
        return kw

    def get_title(self):
        return 'shared file'

    def populate(self, **kwargs):
        ctx = self.details.copy()
        ctx.update(
            text_size='{}sp'.format(self.app().font_size_normal_absolute),
            header_text_size='{}sp'.format(self.app().font_size_large_absolute),
            remote_path=self.remote_path,
            global_id=self.global_id,
            size_text=system.get_nice_size(self.details.get('size', 0)),
        )
        if _Debug:
            print('SingleSharedFileScreen.populate', ctx)
        versions_text = ''
        for v in ctx['versions']:
            v['header_text_size'] = '{}sp'.format(self.app().font_size_medium_absolute)
            v['fragments'] = v.get('fragments') or []
            versions_text += version_info_text.format(**v)
        ctx['versions_text'] = versions_text
        self.ids.shared_file_details.text = shared_file_info_text.format(**ctx)

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='service_my_data')
        self.populate()

    def on_leave(self, *args):
        self.ids.state_panel.release()

    def on_download_file_button_clicked(self):
        if _Debug:
            print('SingleSharedFileScreen.on_download_file_button_clicked')
        api_client.file_download_start(remote_path=self.remote_path, cb=self.on_file_download_started)

    def on_delete_file_button_clicked(self):
        if _Debug:
            print('SingleSharedFileScreen.on_delete_file_button_clicked')
        api_client.file_delete(remote_path=self.remote_path, cb=self.on_file_deleted)

    def on_file_deleted(self, resp):
        if _Debug:
            print('SingleSharedFileScreen.on_file_deleted', resp)
        if not api_client.is_ok(resp):
            snackbar.error(text='file delete failed: %s' % api_client.response_err(resp))
        else:
            snackbar.success(text='shared file deleted')
        screen.main_window().screen_back()
        screen.main_window().close_screen(screen_id='shared_file_{}'.format(self.global_id))

    def on_file_download_started(self, resp):
        if _Debug:
            print('SingleSharedFileScreen.on_file_download_started', resp)
        if not api_client.is_ok(resp):
            snackbar.error(text='download file failed: %s' % api_client.response_err(resp))
        else:
            snackbar.success(text='file download started')
        screen.main_window().screen_back()
        screen.main_window().close_screen(screen_id='shared_file_{}'.format(self.global_id))
