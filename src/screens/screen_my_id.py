from components.screen import AppScreen

from lib import api_client
from lib import websock

#------------------------------------------------------------------------------

identity_details_temlate_text = """
[size={text_size}][color=#909090]name:[/color] [b]{name}[/b]

[color=#909090]global ID:[/color] [b]{global_id}[/b]

[color=#909090]incoming channels:[/color]
{contacts}

[color=#909090]sources:[/color]
{sources}

[color=#909090]created:[/color] {date}

[color=#909090]revision:[/color] {revision}

[color=#909090]version:[/color]
[size={small_text_size}]{version}[/size]

[color=#909090]public key:[/color]
[size={small_text_size}][font=RobotoMono-Regular]{publickey}[/font][/size]

[/size]
"""

#------------------------------------------------------------------------------

class MyIDScreen(AppScreen):

    def get_icon(self):
        return 'account-box'

    def get_title(self):
        return 'my identity'

    def on_enter(self, *args):
        api_client.identity_get(cb=self.on_identity_get_result)

    def on_identity_get_result(self, resp):
        if not websock.is_ok(resp):
            self.ids.my_id_details.text = str(resp)
            return
        result = websock.response_result(resp)
        if not result:
            self.ids.my_id_details.text = websock.response_errors(resp)
            return
        self.ids.my_id_details.text = identity_details_temlate_text.format(
            text_size='{}sp'.format(self.app().font_size_normal_absolute),
            small_text_size='{}sp'.format(self.app().font_size_small_absolute),
            name=result.get('name', ''),
            global_id=result.get('global_id', ''),
            publickey=result.get('publickey', ''),
            date=result.get('date', ''),
            version=result.get('version', ''),
            revision=result.get('revision', ''),
            sources='\n'.join(result.get('sources', [])),
            contacts='\n'.join(result.get('contacts', [])),
        )


from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_my_id.kv')
