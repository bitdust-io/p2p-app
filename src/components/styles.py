from kivy.metrics import dp, sp

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

base_element_height = 32


class AppStyle(object):

    font_size_extra_small_absolute = 10

    font_size_small_absolute = 12
    font_size_small = sp(12)

    font_size_normal_absolute = 14
    font_size_normal = sp(14)

    font_size_large_absolute = 18
    font_size_large = sp(18)

    font_size_icon_absolute = 14
    font_size_icon = sp(14)

    #--- PADDING
    button_text_padding_x = dp(5)
    button_text_padding_y = dp(5)

    text_input_padding_x_absolute = 5
    text_input_padding_x = dp(5)
    text_input_padding_y_absolute = 5
    text_input_padding_y = dp(5)

    #--- SCROLL BAR
    scroll_bar_width = dp(15)

    #--- COLORS
    color_transparent = (0,0,0,0)
    color_black = (0,0,0,1)
    color_gray = (.5,.5,.5,1)
    color_white = (1,1,1,1)
    color_row_seleted = (.96, .96, 1, 1)
    color_circle_connecting = (.8, .8, .3, 1)
    color_circle_offline = (.9, .9, .9, 1)
    color_circle_online = (.5, .9, .5, 1)

    color_btn_text_light = (1,1,1,1)
    color_btn_text_dark = (.3,.7,1,1)
    color_btn_normal = (.2,.5,.8,1)
    color_btn_pressed = (.3,.6,.9,1)
    color_btn_inactive = (.1,.4,.7,1)
    color_btn_disabled = (.8,.8,.8,1)
    color_btn_normal_green = (.2,.8,.5,1)
    color_btn_normal_red = (.8,.5,.2,1)
    color_btn_pressed_green = (.3,.9,.6,1)
    color_btn_inactive_green = (.1,.7,.4,1)
    color_btn_disabled_green = (.7,.9,.7,1)

    color_text_input_foreground = (.1,.1,.1,1)
    color_text_input_foreground_empty = (.5,.5,.5,1)
    color_text_input_foreground_disabled = (.5,.5,.5,1)
    color_text_input_background = (.92,.92,.92,1)
    color_text_input_background_active = (.96,.96,.96,1)
    color_text_input_background_disabled = (.8,.8,.8,1)
    color_text_input_border = (.75,.75,.75,1)

    #--- NAVIGATION
    nav_height = dp(base_element_height)

    #--- TEXT INPUT
    text_input_height = 26

    #--- SCREEN SETTINGS
    setting_record_height = dp(base_element_height)
    setting_normal_font_size_absolute = 14
    setting_normal_font_size = sp(14)
    setting_small_font_size_absolute = 12
    setting_small_font_size = sp(12)

    #--- SCREEN SEARCH_PEOPLE
    search_result_record_height = dp(base_element_height)

    #--- SCREEN FRIENDS
    friend_record_padding_x = dp(5)
    friend_record_padding_y = dp(5)
    friend_record_height = dp(base_element_height)

    #--- SCREEN CONVERSATIONS
    conversation_record_padding_x = dp(5)
    conversation_record_padding_y = dp(5)
    conversation_record_height = dp(base_element_height)

    #--- SCREEN PRIVATE CHAT
    chat_input_font_size = sp(14)

#------------------------------------------------------------------------------

style = AppStyle()

