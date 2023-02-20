import os
import shutil

#------------------------------------------------------------------------------

from lib import api_client
from lib import system

from components import screen
from components import snackbar

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

private_file_info_text = """
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


class SinglePrivateFileScreen(screen.AppScreen):

    def __init__(self, **kwargs):
        self.global_id = ''
        self.remote_path = ''
        self.details = {}
        super(SinglePrivateFileScreen, self).__init__(**kwargs)

    def init_kwargs(self, **kw):
        if _Debug:
            print('SinglePrivateFileScreen.init_kwargs', kw)
        self.global_id = kw.pop('global_id', '')
        self.remote_path = kw.pop('remote_path', '')
        self.details = kw.pop('details', {})
        return kw

    def get_title(self):
        return 'private file'

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
            print('SinglePrivateFileScreen.populate', ctx)
        versions_text = ''
        for v in ctx['versions']:
            v['header_text_size'] = '{}sp'.format(self.app().font_size_medium_absolute)
            versions_text += version_info_text.format(**v)
        ctx['versions_text'] = versions_text
        self.ids.private_file_details.text = private_file_info_text.format(**ctx)

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='service_my_data')
        self.populate()

    def on_leave(self, *args):
        self.ids.state_panel.release()

    def on_download_file_button_clicked(self):
        destination_path = None
        if system.is_android():
            import tempfile
            from android.storage import app_storage_path  # @UnresolvedImport
            destination_path = tempfile.mkdtemp(dir=app_storage_path())
        if _Debug:
            print('SinglePrivateFileScreen.on_download_file_button_clicked remote_path=%s destination_path=%s' % (self.remote_path, destination_path, ))
        api_client.file_download_start(
            remote_path=self.remote_path,
            destination_path=destination_path,
            wait_result=True,
            cb=lambda resp: self.on_file_download_result(resp, destination_path),
        )

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
            snackbar.success(text='private file deleted')
        # screen.select_screen('private_files_screen')
        screen.main_window().screen_back()
        screen.main_window().close_screen(screen_id='private_file_{}'.format(self.global_id))

    def on_file_download_result(self, resp, destination_path):
        if _Debug:
            print('SinglePrivateFileScreen.on_file_download_result', resp, destination_path)
        if system.is_android():
            from android.storage import primary_external_storage_path  # @UnresolvedImport
            download_dir = os.path.join(primary_external_storage_path(), 'Download')
            for filename in os.listdir(destination_path):
                srcpath = os.path.join(destination_path, filename)
                destpath = os.path.join(download_dir, filename)
                shutil.copyfile(srcpath, destpath)
                if _Debug:
                    print('SinglePrivateFileScreen.on_file_download_result', srcpath, destpath)
            system.rmdir_recursive(destination_path, ignore_errors=True)
        if not api_client.is_ok(resp):
            snackbar.error(text='download failed: %s' % api_client.response_err(resp))
        else:
            snackbar.success(text='downloading is complete')
        # screen.select_screen('private_files_screen')
        screen.main_window().screen_back()
        screen.main_window().close_screen(screen_id='private_file_{}'.format(self.global_id))
