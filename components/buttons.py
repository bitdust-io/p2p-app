from kivy.uix.button import Button

#------------------------------------------------------------------------------

KVButton = """
<Button>:
    markup: True
    background_color: 0,0,0,0
    color: 1,1,1,1
    disabled_color: .8,.8,.8,1
    background_disabled_normal: ''
    height: 30
    size_hint_y: None
    bg_normal: .1,.4,.7,1
    bg_pressed: .2,.5,.8,1
    bg_disabled: .3,.3,.3,1
    bg_normal_delta: .2
    bg_disabled_delta: .1
    corner_radius: 5
    canvas.before:
        Color:
            rgba: self.bg_disabled if self.disabled else (self.bg_normal if self.state == 'normal' else self.bg_pressed) 
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.corner_radius+1,]
        Color:
            rgba: (self.bg_disabled[0]+self.bg_disabled_delta,self.bg_disabled[1]+self.bg_disabled_delta,self.bg_disabled[2]+self.bg_disabled_delta,1) if self.disabled else ((self.bg_normal[0]+self.bg_normal_delta,self.bg_normal[1]+self.bg_normal_delta,self.bg_normal[2]+self.bg_normal_delta,1) if self.state == 'normal' else (self.bg_pressed[0]+self.bg_normal_delta,self.bg_pressed[1]+self.bg_normal_delta,self.bg_pressed[2]+self.bg_normal_delta,1))
        RoundedRectangle:
            pos: self.pos[0]+2, self.pos[1]+2
            size: self.size[0]-4, self.size[1]-4
            radius: [self.corner_radius,]
"""

#------------------------------------------------------------------------------

KVNavButton = """
<NavButton>:
    size_hint_x: None
    width: self.texture_size[0] + 20
    on_press: root.parent.parent.parent.ids.screen_manager.current = (self.screen or root.parent.parent.parent.ids.screen_manager.current)  
"""

class NavButton(Button):
    pass

#------------------------------------------------------------------------------
