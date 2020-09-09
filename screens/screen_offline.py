from kivy.uix.screenmanager import Screen


KVDisconnectedScreen = """
<DisconnectedScreen>:
    ScrollView:
        do_scroll_x: False
        GridLayout:
            canvas.before:
                Color:
                    rgba: 1, .9, .9, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            cols: 1
            size_hint: None, None
            width: Window.width - 10
            height: self.minimum_height
            Label:
                color: 0, 0, 0, 1 
                markup: True
                text: '[size=94]offline1[/size]'
                height: 200
                size_hint_y: None
            Label:
                color: 0, 0, 0, 1 
                markup: True
                text: '[size=94]offline2[/size]'
                height: 200
                size_hint_y: None
            Label:
                color: 0, 0, 0, 1 
                markup: True
                text: '[size=94]offline3[/size]'
                height: 200
                size_hint_y: None
            Label:
                color: 0, 0, 0, 1 
                markup: True
                text: '[size=94]offline4[/size]'
                height: 200
                size_hint_y: None
            Label:
                color: 0, 0, 0, 1 
                markup: True
                text: '[size=94]offline5[/size]'
                height: 200
                size_hint_y: None
            Label:
                color: 0, 0, 0, 1 
                markup: True
                text: '[size=94]offline6[/size]'
                height: 200
                size_hint_y: None

"""

class DisconnectedScreen(Screen):

    def get_title(self):
        return 'connection'
