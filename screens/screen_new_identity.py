from components.screen import AppScreen


KVNewIdentityScreen = """
<NewIdentityScreen>:
    Label:
        color: 0, 0, 0, 1 
        markup: True
        text: '[size=14]new identity[/size]'

"""

class NewIdentityScreen(AppScreen):

    def get_title(self):
        return 'your identity'
