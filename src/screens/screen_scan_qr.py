from collections import namedtuple
from PIL import Image, ImageOps

#------------------------------------------------------------------------------

from kivy.uix.anchorlayout import AnchorLayout

from kivy.clock import Clock

#------------------------------------------------------------------------------

from components import screen

from lib import system
from lib import strng

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

BarSymbol = namedtuple('BarSymbol', ['type', 'data'])

#------------------------------------------------------------------------------

class CameraContainer(AnchorLayout):

    def __init__(self, **kwargs):
        self.is_android = system.is_android()
        self.is_ios = system.is_android()
        super(AnchorLayout, self).__init__(**kwargs)


class ScanQRScreen(screen.AppScreen):

    def __init__(self, **kw):
        self.scan_qr_callback = None
        self.is_android = system.is_android()
        self.is_ios = system.is_ios()
        super(ScanQRScreen, self).__init__(**kw)

    def init_kwargs(self, **kw):
        if _Debug:
            print('ScanQRScreen.init_kwargs', kw)
        self.scan_qr_callback = kw.pop('scan_qr_callback', None)
        return kw

    # def get_title(self):
    #     return 'scan QR code'

    def on_enter(self):
        self.camera = CameraContainer()
        self.ids.container.add_widget(self.camera)
        if _Debug:
            print('ScanQRScreen.on_enter', type(self.camera.ids.camera_instance), type(self.camera.ids.camera_instance._camera))
        if not self.is_ios:
            self.camera.ids.camera_instance._camera.bind(on_texture=self.on_tex)
        self.camera.ids.camera_instance.play = True
        if self.is_ios:
            self.camera.ids.camera_instance._camera.start_metadata_analysis(callback=self.on_tex_ios)

    def on_leave(self):
        if _Debug:
            print('ScanQRScreen.on_leave')
        self.camera.ids.camera_instance.play = False
        if self.is_android:
            try:
                self.camera.ids.camera_instance._camera._release_camera()
            except Exception as exc:
                if _Debug:
                    print('ScanQRScreen.on_leave', exc)
        else:
            if not self.is_ios:
                try:
                    self.camera.ids.camera_instance._camera._device.release()
                except Exception as exc:
                    if _Debug:
                        print('ScanQRScreen.on_leave', exc)
        self.ids.container.remove_widget(self.camera)
        del self.camera
        self.camera = None

    def fix_android_image(self, pil_image):
        if not self.is_android:
            return pil_image
        pil_image = pil_image.rotate(90)
        pil_image = ImageOps.mirror(pil_image)
        return pil_image

    def on_tex_ios(self, *args, **kwargs):
        if _Debug:
            print('ScanQRScreen.on_tex_ios', args, kwargs, self.scan_qr_callback)
        if args and self.scan_qr_callback:
            _cb = self.scan_qr_callback
            self.scan_qr_callback = None
            # _cb(strng.to_text(args[1]))
            Clock.schedule_once(lambda dt: _cb(strng.to_text(args[1])))

    def on_tex(self, camera):
        if _Debug:
            print('ScanQRScreen.on_tex', camera)
        from pyzbar import pyzbar
        try:
            image_data = camera.texture.pixels
            size = camera.texture.size
            pil_image = Image.frombytes(mode='RGBA', size=size, data=image_data)
            pil_image = self.fix_android_image(pil_image)
            result_symbols = []
            codes = pyzbar.decode(pil_image, symbols=set(pyzbar.ZBarSymbol))
            for code in codes:
                symbol = BarSymbol(type=code.type, data=code.data)
                result_symbols.append(symbol)
            if not result_symbols:
                return
            result_text = ', '.join([symbol.data.decode('utf-8') for symbol in result_symbols])
        except Exception as exc:
            if _Debug:
                print('ScanQRScreen.on_tex', exc)
            return
        if _Debug:
            print('ScanQRScreen.on_tex', result_text)
        if self.scan_qr_callback:
            _cb = self.scan_qr_callback
            self.scan_qr_callback = None
            # _cb(result_text)
            Clock.schedule_once(lambda dt: _cb(result_text))
