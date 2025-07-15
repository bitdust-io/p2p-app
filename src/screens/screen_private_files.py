import os

from kivy.clock import mainthread

from lib import api_client
from lib import api_file_transfer
from lib import system
from lib import util

from components import screen
from components import snackbar
from components import buttons
from components import webfont

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class PrivateFilesScreen(screen.AppScreen):

    # def get_title(self):
    #     return 'private files'

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
        if screen.main_window().state_my_data != 1:
            self.ids.upload_file_button.disabled = True
        else:
            self.ids.upload_file_button.disabled = screen.main_window().state_file_transfering
        if system.is_ios() and self.upload_multimedia_button:
            self.upload_multimedia_button.disabled = screen.main_window().state_file_transfering

    def on_created(self):
        self.ids.files_list_view.init(
            file_system_type='private',
            key_id='master${}'.format(self.control().my_global_id) if self.control().my_global_id else None,
            file_clicked_callback=self.on_file_clicked,
        )
        screen.main_window().bind(state_file_transfering=self.ids.upload_file_button.setter("disabled"))
        self.upload_multimedia_button = None
        if system.is_ios():
            self.upload_multimedia_button = buttons.FillRoundFlatButton(
                text="[size=22sp]{}[/size] [size=16sp]photo[/size]".format(webfont.md_icon("image")),
                md_bg_color=self.app().theme_cls.accent_color,
                theme_text_color="Custom",
                text_color=self.app().color_white99,
                on_release=self.on_upload_multimedia_button_clicked,
            )
            self.ids.top_buttons_container.add_widget(self.upload_multimedia_button, index=1)
            screen.main_window().bind(state_file_transfering=self.upload_multimedia_button.setter("disabled"))

    def on_destroying(self):
        self.upload_multimedia_button = None
        self.ids.files_list_view.shutdown()

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='service_my_data', callback_start=self.on_state_panel_attach)
        self.populate()

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
            from lib import filechooser_android
            filechooser_android.open_file(
                title="Upload a file",
                preview=True,
                show_hidden=False,
                on_selection=self.on_upload_file_selected,
            )
        elif system.is_osx():
            from lib import filechooser_macosx
            fc = filechooser_macosx.MacFileChooser(
                title="Upload a file",
                preview=True,
                show_hidden=False,
                on_selection=self.on_upload_file_selected,
            )
            fc.run()
        elif system.is_ios():
            from lib import filechooser_ios
            fc = filechooser_ios.IOSFileChooser(
                on_selection=self.on_upload_file_selected,
            )
            fc.run()
        else:
            from plyer import filechooser
            if system.is_windows():
                self._latest_cwd = os.getcwd()
            filechooser.open_file(
                title="Upload a file",
                preview=True,
                show_hidden=False,
                on_selection=self.on_upload_file_selected,
            )

    @mainthread
    def on_upload_multimedia_button_clicked(self, *args):
        if _Debug:
            print('PrivateFilesScreen.on_upload_multimedia_button_clicked', args)
        if system.is_ios():
            from lib import filechooser_ios
            fc = filechooser_ios.IOSImageChooser(
                on_selection=self.on_upload_file_selected,
            )
            fc.run()

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
        if not system.is_android():
            if not os.path.isfile(file_path):
                if _Debug:
                    print('PrivateFilesScreen.on_upload_file_selected file do not exist', file_path)
                snackbar.error(text='file not found')
                return
        remote_path = util.clean_remote_path(file_name)
        api_client.file_create(
            remote_path=remote_path,
            as_folder=False,
            exist_ok=True,
            cb=lambda resp: self.on_file_created(resp, file_path, remote_path),
        )

    def on_file_created(self, resp, file_path, remote_path):
        if _Debug:
            print('PrivateFilesScreen.on_file_created', file_path, remote_path, resp)
        if not api_client.is_ok(resp):
            snackbar.error(text=api_client.response_err(resp))
            return
        target_remote_path = api_client.result(resp).get('remote_path')
        screen.main_window().state_file_transfering = True
        if screen.control().is_local:
            api_client.file_upload_start(
                local_path=file_path,
                remote_path=target_remote_path,
                wait_result=True,
                cb=self.on_upload_file_started,
            )
        else:
            api_file_transfer.FileUploader(
                source_path=file_path,
                chunk_size=128*1024,
                result_callback=lambda result: self.on_file_transfer_result(result, target_remote_path),
                progress_callback=lambda *a, **kw: self.on_file_transfer_progress(target_remote_path, *a, **kw),
            ).start()

    @mainthread
    def on_file_transfer_progress(self, remote_path, source_path, destination_path, bytes_sent):
        if _Debug:
            print('PrivateFilesScreen.on_file_transfer_progress', remote_path, bytes_sent)
        if remote_path in self.ids.files_list_view.index_by_remote_path:
            self.ids.files_list_view.index_by_remote_path[remote_path].ids.file_condition.text = '[size=10sp][color=bbbf]%s uploaded[/color][/size]' % system.make_nice_size(bytes_sent)

    def on_file_transfer_result(self, result, remote_path):
        if _Debug:
            print('PrivateFilesScreen.on_file_transfer_result', result, remote_path)
        screen.main_window().state_file_transfering = False
        if isinstance(result, Exception):
            snackbar.error(text=str(result))
            return
        screen.main_window().state_file_transfering = True
        api_client.file_upload_start(
            local_path=result,
            remote_path=remote_path,
            wait_result=True,
            cb=self.on_upload_file_started,
        )

    def on_upload_file_started(self, resp):
        if _Debug:
            print('PrivateFilesScreen.on_upload_file_started', resp)
        screen.main_window().state_file_transfering = False
        if not api_client.is_ok(resp):
            snackbar.error(text=api_client.response_err(resp))

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
