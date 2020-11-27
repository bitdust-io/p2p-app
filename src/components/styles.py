from kivy.metrics import dp, sp

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

def init(app):
    if _Debug:
        print('dp(1.0):', dp(1.0))
        print('sp(1.0):', sp(1.0))

    #--- FONT SIZE
    app.font_size_extra_small_absolute = 11
    app.font_size_small_absolute = 13
    app.font_size_normal_absolute = 15
    app.font_size_large_absolute = 18
    app.font_size_icon_absolute = 15

    app.font_size_normal = sp(app.font_size_normal_absolute)
    app.font_size_small = sp(app.font_size_small_absolute)
    app.font_size_large = sp(app.font_size_large_absolute)
    app.font_size_icon = sp(app.font_size_icon_absolute)

    #--- PADDING
    app.button_text_padding_x = dp(5)
    app.button_text_padding_y = dp(5)

    app.text_input_padding_x_absolute = 5
    app.text_input_padding_y_absolute = 5
    app.text_input_padding_x = dp(app.text_input_padding_x_absolute)
    app.text_input_padding_y = dp(app.text_input_padding_y_absolute)

    #--- SCROLL BAR
    app.scroll_bar_width = dp(15)

    #--- COLORS
    app.color_transparent = (0,0,0,0)
    app.color_black = (0,0,0,1)
    app.color_white = (1,1,1,1)

    app.color_btn_text_light = (1,1,1,1)
    app.color_btn_text_dark = (.3,.7,1,1)
    app.color_btn_normal = (.2,.5,.8,1)
    app.color_btn_pressed = (.3,.6,.9,1)
    app.color_btn_inactive = (.1,.4,.7,1)
    app.color_btn_disabled = (.8,.8,.8,1)
    app.color_btn_normal_green = (.2,.8,.5,1)
    app.color_btn_pressed_green = (.3,.9,.6,1)
    app.color_btn_inactive_green = (.1,.7,.4,1)
    app.color_btn_disabled_green = (.7,.9,.7,1)

    app.color_text_input_foreground = (.1,.1,.1,1)
    app.color_text_input_foreground_empty = (.5,.5,.5,1)
    app.color_text_input_foreground_disabled = (.5,.5,.5,1)
    app.color_text_input_background = (.92,.92,.92,1)
    app.color_text_input_background_active = (.96,.96,.96,1)
    app.color_text_input_background_disabled = (.8,.8,.8,1)
    app.color_text_input_border = (.75,.75,.75,1)

    #--- NAVIGATION
    app.nav_height = dp(28)

    #--- SCREEN SETTINGS
    app.setting_record_height = sp(app.font_size_large_absolute) + dp(12)
    app.setting_normal_font_size = sp(app.font_size_normal_absolute)
    app.setting_small_font_size = sp(app.font_size_small_absolute)

    #--- SCREEN FRIENDS
    app.friend_record_padding_x = dp(5)
    app.friend_record_padding_y = dp(5)
    app.friend_record_height = sp(16) + dp(12)

    #--- SCREEN CONVERSATIONS
    app.conversation_record_padding_x = dp(5)
    app.conversation_record_padding_y = dp(5)
    app.conversation_record_height = sp(16) + dp(12)

    #--- SCREEN PRIVATE CHAT
    app.chat_input_font_size = sp(app.font_size_normal_absolute)
    # app.chat_input_height = sp(app.font_size_normal_absolute) * 3
