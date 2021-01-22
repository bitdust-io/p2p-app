from kivy.metrics import dp, sp

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

base_element_height = 32

# those can be used to manipulate button's gamma
btn_clr_rgb_top = .7
btn_clr_rgb_mid = .5
btn_clr_rgb_low = .3

#------------------------------------------------------------------------------

class AppStyle(object):

    #--- FONT SIZE
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
    color_gray = (btn_clr_rgb_mid,btn_clr_rgb_mid,btn_clr_rgb_mid,1)
    color_white = (1,1,1,1)
    color_row_seleted = (.96, .96, 1, 1)
    color_circle_connecting = (btn_clr_rgb_top, btn_clr_rgb_top, btn_clr_rgb_low+.1, 1)
    color_circle_offline = (btn_clr_rgb_top+.1, btn_clr_rgb_top+.1, btn_clr_rgb_top+.1, 1)
    color_circle_online = (btn_clr_rgb_mid, btn_clr_rgb_top+.1, btn_clr_rgb_mid, 1)

    color_btn_text_light = (1,1,1,1)
    color_btn_text_dark = (btn_clr_rgb_low+.1,btn_clr_rgb_top-.1,btn_clr_rgb_top+.1,1)
    color_btn_normal = (btn_clr_rgb_low,btn_clr_rgb_mid,btn_clr_rgb_top,1)
    color_btn_normal_blue = (btn_clr_rgb_low,btn_clr_rgb_mid,btn_clr_rgb_top,1)
    color_btn_normal_green = (btn_clr_rgb_low,btn_clr_rgb_top,btn_clr_rgb_mid,1)
    color_btn_normal_red = (btn_clr_rgb_top,btn_clr_rgb_mid,btn_clr_rgb_low,1)
    color_btn_pressed = (btn_clr_rgb_low+.1,btn_clr_rgb_mid+.1,btn_clr_rgb_top+.1,1)
    color_btn_inactive = (btn_clr_rgb_low-.1,btn_clr_rgb_mid-.1,btn_clr_rgb_top-.1,1)
    color_btn_disabled = (btn_clr_rgb_top,btn_clr_rgb_top,btn_clr_rgb_top,1)
    color_btn_pressed_green = (btn_clr_rgb_low+.1,btn_clr_rgb_top+.1,.6,1)
    color_btn_inactive_green = (btn_clr_rgb_low-.1,btn_clr_rgb_top-.1,btn_clr_rgb_mid-.1,1)
    color_btn_disabled_green = (btn_clr_rgb_top-.1,btn_clr_rgb_top+.1,btn_clr_rgb_top-.1,1)

    color_text_input_foreground = (.1,.1,.1,1)
    color_text_input_foreground_empty = (.5,.5,.5,1)
    color_text_input_foreground_disabled = (.5,.5,.5,1)
    color_text_input_background = (.92,.92,.92,1)
    color_text_input_background_active = (.96,.96,.96,1)
    color_text_input_background_disabled = (btn_clr_rgb_top,btn_clr_rgb_top,btn_clr_rgb_top,1)
    color_text_input_border = (.75,.75,.75,1)

    #--- BUTTONS
    btn_icon_small_width = dp(26)
    btn_icon_small_height = dp(26)
    btn_icon_normal_width = dp(32)
    btn_icon_normal_height = dp(32)

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

