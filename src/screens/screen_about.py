import webbrowser

from components import screen

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

about_temlate_text = """
BitDust is an [u][color=#0000ff][ref=github_link]open-source[/ref][/color][/u] project of a worldwide distributed network that is aiming to provide online storage, safe personal communications and full control of your own private data.

The BitDust p2p-app is a peer-to-peer application which provides secure distributed data storage and safe private communications.

This is a story about respecting the digital freedoms of all people on this planet and taking full control over our own personal data that we send and receive over the Internet.

We are currently with a small team primarily focusing on the development and supporting the BitDust project and community.

More about the project you can read on [u][color=#0000ff][ref=web_site_link]www.bitdust.io[/ref][/color][/u].

Also you can give us your feedback about the BitDust p2p-app or report a bug directly via that [u][color=#0000ff][ref=feedback_link]link[/ref][/color][/u].
"""

#------------------------------------------------------------------------------

class AboutScreen(screen.AppScreen):

    def get_title(self):
        return 'about BitDust p2p-app'

    def on_enter(self, *args):
        self.ids.about_text.text = about_temlate_text.format()

    def on_about_text_ref_pressed(self, *args):
        if _Debug:
            print('AboutScreen.on_about_text_ref_pressed', args)
        if args[1] == 'github_link':
            webbrowser.open('https://github.com/bitdust-io')
        elif args[1] == 'web_site_link':
            webbrowser.open('https://bitdust.io')
        elif args[1] == 'feedback_link':
            webbrowser.open('https://forms.gle/RkJW3L7NTamZ5K8m6')
