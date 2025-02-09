import os

#------------------------------------------------------------------------------

from lib import system
from lib import api_client
from lib import api_file_transfer

from components import screen
from components import snackbar

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

private_file_info_text = """
[size={header_text_size}]{path}[/size]
[size={text_size}]
[color=#909090]remote path:[/color] {remote_path}
[color=#909090]global ID:[/color] {global_id}
[color=#909090]size:[/color] {size_text}
[color=#909090]downloaded to:[/color] {download_path}
{versions_text}
[/size]
"""

version_info_text = """
[size={header_text_size}]{label}   [u][color=#0000ff][ref=download_{backup_id}]download[/ref][/color][/u][/size]
[color=#909090]    ID:[/color] {backup_id}
[color=#909090]    size:[/color] {size}
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
        self.local_uri = None
        self.file_name = self.details.get('path')
        self.downloaded_path = os.path.join(system.get_downloads_dir(), self.file_name)
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
        if _Debug:
            print('SinglePrivateFileScreen.populate', self.details)
        if system.is_android():
            download_path = self.downloaded_path or ''
        else:
            download_path = (self.downloaded_path if (self.downloaded_path and os.path.exists(self.downloaded_path)) else '') or ''
        ctx = self.details.copy()
        ctx.update(
            text_size='{}sp'.format(self.app().font_size_normal_absolute),
            header_text_size='{}sp'.format(self.app().font_size_large_absolute),
            remote_path=self.remote_path,
            download_path=download_path,
            global_id=self.global_id,
            size_text=system.get_nice_size(self.details.get('size', 0)),
        )
        versions_text = ''
        for v in ctx['versions']:
            v['header_text_size'] = '{}sp'.format(self.app().font_size_medium_absolute)
            v['size'] = system.get_nice_size(v.get('size', 0))
            versions_text += version_info_text.format(**v)
        ctx['versions_text'] = versions_text
        self.ids.private_file_details.text = private_file_info_text.format(**ctx)
        if screen.control().is_local:
            self.ids.open_file_button.disabled = not self.downloaded_path or not os.path.exists(self.downloaded_path)
        else:
            self.ids.open_file_button.disabled = not self.downloaded_path or not os.path.exists(self.downloaded_path)
        self.ids.download_file_button.disabled = screen.main_window().state_file_transfering

    def on_created(self):
        screen.main_window().bind(state_file_transfering=self.ids.download_file_button.setter("disabled"))

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='service_my_data')
        api_client.add_model_listener('remote_version', listener_cb=self.on_remote_version)
        self.populate()

    def on_leave(self, *args):
        api_client.remove_model_listener('remote_version', listener_cb=self.on_remote_version)
        self.ids.state_panel.release()

    def on_download_file_button_clicked(self):
        if _Debug:
            print('SinglePrivateFileScreen.on_download_file_button_clicked remote_path=%s' % self.remote_path)
        screen.main_window().state_file_transfering = True
        api_client.file_download_start(
            remote_path=self.remote_path,
            destination_path=None,
            wait_result=True,
            cb=self.on_file_download_result,
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
        screen.main_window().screen_back()
        screen.main_window().close_screen(screen_id='private_file_{}'.format(self.global_id))

    def on_file_download_result(self, resp):
        if _Debug:
            print('SinglePrivateFileScreen.on_file_download_result', resp)
        screen.main_window().state_file_transfering = False
        if not api_client.is_ok(resp):
            snackbar.error(text=api_client.response_err(resp))
            return
        local_path = api_client.response_result(resp).get('local_path')
        destination_path = os.path.join(system.get_downloads_dir(), self.file_name)
        if not local_path:
            self.downloaded_path = None
            snackbar.error(text='file was not downloaded')
            self.populate()
            return
        if screen.control().is_local:
            if os.path.exists(destination_path):
                # TODO: open popup dialog and ask user if destination file suppose to be overwritten
                # TODO: move all that into a separate thread to no block the main threads
                try:
                    if os.path.isdir(destination_path):
                        system.rmdir_recursive(destination_path, ignore_errors=True)
                    else:
                        os.remove(destination_path)
                except Exception as exc:
                    self.downloaded_path = None
                    snackbar.error(str(exc))
                    self.populate()
                    return
            try:
                os.rename(local_path, destination_path)
            except Exception as exc:
                self.downloaded_path = None
                snackbar.error(str(exc))
                self.populate()
                return
            if os.path.exists(destination_path):
                self.downloaded_path = destination_path
                snackbar.success(text='downloading is complete')
                self.populate()
            else:
                self.downloaded_path = None
                snackbar.error(text='file was not downloaded')
                self.populate()
            return
        screen.main_window().state_file_transfering = True
        api_file_transfer.file_download(
            source_path=local_path,
            destination_path=destination_path,
            result_callback=self.on_file_transfer_result,
        )

    def on_file_transfer_result(self, result):
        if _Debug:
            print('SinglePrivateFileScreen.on_file_transfer_result', result)
        screen.main_window().state_file_transfering = False
        if isinstance(result, Exception):
            snackbar.error(text=str(result))
            return
        destination_path = os.path.join(system.get_downloads_dir(), self.file_name)
        if system.is_android():
            from androidstorage4kivy import SharedStorage  # @UnresolvedImport
            self.local_uri = SharedStorage().copy_to_shared(private_file=destination_path)
        else:
            self.downloaded_path = destination_path
        snackbar.success(text='downloading is complete')
        self.populate()

    def on_open_file_button_clicked(self):
        if _Debug:
            print('SinglePrivateFileScreen.on_open_file_button_clicked')
        if screen.control().is_local:
            if self.downloaded_path and os.path.exists(self.downloaded_path):
                system.open_path_in_os(self.downloaded_path)
        else:
            if system.is_android():
                if self.downloaded_path:
                    from androidstorage4kivy import SharedStorage  # @UnresolvedImport
                    self.local_uri = SharedStorage().copy_to_shared(private_file=self.downloaded_path)
                    if self.local_uri:
                        system.open_path_in_os(self.local_uri)
                # if self.local_uri:
                #     system.open_path_in_os(self.local_uri)
            else:
                if self.downloaded_path:
                    system.open_path_in_os(self.downloaded_path)

    def on_remote_version(self, payload):
        if _Debug:
            print('SinglePrivateFileScreen.on_remote_version', payload)
        remote_path = payload['data'].get('remote_path')
        if remote_path:
            global_id = payload['data']['global_id']
            if remote_path == self.remote_path and global_id == self.global_id:
                api_client.file_info(
                    remote_path=remote_path,
                    cb=lambda resp: self.on_private_file_info_result(resp, remote_path, global_id),
                )

    def on_private_file_info_result(self, resp, remote_path, global_id):
        if _Debug:
            print('SinglePrivateFileScreen.on_private_file_info_result', remote_path, global_id)
        if not api_client.is_ok(resp):
            snackbar.error(text=api_client.response_err(resp))
            return
        self.details = api_client.response_result(resp)
        self.populate()

    def on_private_file_details_ref_pressed(self, *args):
        if _Debug:
            print('SinglePrivateFileScreen.on_private_file_details_ref_pressed', args)
        if screen.main_window().state_file_transfering:
            return
        if args[1].startswith('download_'):
            backup_id = args[1][9:]
            screen.main_window().state_file_transfering = True
            api_client.file_download_start(
                remote_path=backup_id,
                destination_path=None,
                wait_result=True,
                cb=self.on_file_download_result,
            )
