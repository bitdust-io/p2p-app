from lib import api_client
from lib import system

from components import screen

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

my_donated_storage_details_temlate_text = """
[size={header_text_size}][b]donated storage[/b][/size]
[size={text_size}][color=#909090]customers:[/color] {customers_num}
[color=#909090]donated:[/color] {donated}
[color=#909090]allocated:[/color] {consumed} ({consumed_percent})
[color=#909090]used:[/color] {used} ({used_percent})
[color=#909090]free:[/color] {free}[/size]
"""

my_consumed_storage_details_temlate_text = """
[size={header_text_size}][b]consumed storage[/b][/size]
[size={text_size}][color=#909090]suppliers:[/color] {suppliers_num}
[color=#909090]requested:[/color] {needed}
[color=#909090]used:[/color] {used} ({used_percent})
[color=#909090]available:[/color] {available}
[color=#909090]requested per supplier:[/color] {needed_per_supplier}
[color=#909090]used per supplier:[/color] {used_per_supplier}
[color=#909090]available per supplier:[/color] {available_per_supplier}[/size]
"""

my_local_storage_details_temlate_text = """
[size={header_text_size}][b]local files info[/b][/size]
[size={text_size}][color=#909090]cache files:[/color] {backups}
[color=#909090]temp files:[/color] {temp}
[color=#909090]used by customers:[/color] {customers}
[color=#909090]total app data size:[/color] {total}
[color=#909090]total disk size:[/color] {disktotal}
[color=#909090]free space available:[/color] {diskfree} ({diskfree_percent})[/size]
"""

#------------------------------------------------------------------------------

class MyStorageInfoScreen(screen.AppScreen):

    def get_title(self):
        return 'storage info'

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
        if _Debug:
            print('MyStorageInfoScreen.populate', args, kwargs)
        refresh = kwargs.get('kwargs')
        if refresh or not self.ids.my_donated_storage_details.text:
            api_client.space_donated(cb=self.on_space_donated_result)
        if refresh or not self.ids.my_consumed_storage_details.text:
            api_client.space_consumed(cb=self.on_space_consumed_result)
        if refresh or not self.ids.my_local_storage_details.text:
            api_client.space_local(cb=self.on_space_local_result)

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='service_my_data')
        self.populate()

    def on_leave(self, *args):
        self.ids.state_panel.release()

    def on_space_donated_result(self, resp):
        if _Debug:
            print('MyStorageInfoScreen.on_space_donated_result', resp)
        if not api_client.is_ok(resp):
            self.ids.my_donated_storage_details.text = '\n'.join(api_client.response_errors(resp))
            return
        result = api_client.response_result(resp)
        if not result:
            self.ids.my_donated_storage_details.text = ''
            return
        self.ids.my_donated_storage_details.text = my_donated_storage_details_temlate_text.format(
            header_text_size='{}sp'.format(self.app().font_size_medium_absolute),
            text_size='{}sp'.format(self.app().font_size_normal_absolute),
            customers_num=result.get('customers_num', 0),
            consumed=system.get_nice_size(result.get('consumed', 0)),
            donated=system.get_nice_size(result.get('donated', 0)),
            free=system.get_nice_size(result.get('free', 0)),
            used=system.get_nice_size(result.get('used', 0)),
            consumed_percent=result.get('consumed_percent', ''),
            used_percent=result.get('used_percent', ''),
        )

    def on_space_consumed_result(self, resp):
        if _Debug:
            print('MyStorageInfoScreen.on_space_consumed_result', resp)
        if not api_client.is_ok(resp):
            self.ids.my_consumed_storage_details.text = '\n'.join(api_client.response_errors(resp))
            return
        result = api_client.response_result(resp)
        if not result:
            self.ids.my_consumed_storage_details.text = ''
            return
        self.ids.my_consumed_storage_details.text = my_consumed_storage_details_temlate_text.format(
            header_text_size='{}sp'.format(self.app().font_size_medium_absolute),
            text_size='{}sp'.format(self.app().font_size_normal_absolute),
            suppliers_num=result.get('suppliers_num', 0),
            needed=system.get_nice_size(result.get('needed', 0)),
            used=system.get_nice_size(result.get('used', 0)),
            available=system.get_nice_size(result.get('available', 0)),
            needed_per_supplier=system.get_nice_size(result.get('needed_per_supplier', 0)),
            used_per_supplier=system.get_nice_size(result.get('used_per_supplier', 0)),
            available_per_supplier=system.get_nice_size(result.get('available_per_supplier', 0)),
            used_percent=result.get('used_percent', ''),
        )

    def on_space_local_result(self, resp):
        if _Debug:
            print('MyStorageInfoScreen.on_space_local_result', resp)
        if not api_client.is_ok(resp):
            self.ids.my_local_storage_details.text = '\n'.join(api_client.response_errors(resp))
            return
        result = api_client.response_result(resp)
        if not result:
            self.ids.my_local_storage_details.text = ''
            return
        self.ids.my_local_storage_details.text = my_local_storage_details_temlate_text.format(
            header_text_size='{}sp'.format(self.app().font_size_medium_absolute),
            text_size='{}sp'.format(self.app().font_size_normal_absolute),
            backups=system.get_nice_size(result.get('backups', 0)),
            temp=system.get_nice_size(result.get('temp', 0)),
            customers=system.get_nice_size(result.get('customers', 0)),
            total=system.get_nice_size(result.get('total', 0)),
            disktotal=system.get_nice_size(result.get('disktotal', 0)),
            diskfree=system.get_nice_size(result.get('diskfree', 0)),
            diskfree_percent=result.get('diskfree_percent', ''),
        )

    def on_my_donated_storage_details_ref_pressed(self, *args):
        if _Debug:
            print('MyStorageInfoScreen.on_my_donated_storage_details_ref_pressed', args)
        # if args[1] == 'new_identity':
        #     self.main_win().select_screen('new_identity_screen')
        # elif args[1] == 'recover_identity':
        #     self.main_win().select_screen('recover_identity_screen')

    def on_drop_down_menu_item_clicked(self, btn):
        if _Debug:
            print('MyStorageInfoScreen.on_drop_down_menu_item_clicked', btn.icon)
        if btn.icon == 'folder-sync':
            pass
