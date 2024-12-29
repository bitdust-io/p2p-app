from collections import namedtuple
from pyzbar import pyzbar
from PIL import Image, ImageOps

#------------------------------------------------------------------------------

from kivy.properties import ListProperty  # @UnresolvedImport
from kivy.uix.anchorlayout import AnchorLayout

#------------------------------------------------------------------------------

from components import screen

from lib import system

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

BarSymbol = namedtuple('BarSymbol', ['type', 'data'])

#------------------------------------------------------------------------------

class CameraContainer(AnchorLayout):

    def __init__(self, **kwargs):
        self.is_android = system.is_android()
        super(AnchorLayout, self).__init__(**kwargs)


class ScanQRScreen(screen.AppScreen):

    symbols = ListProperty([])
    code_types = ListProperty(set(pyzbar.ZBarSymbol))

    def __init__(self, **kw):
        self.scan_qr_callback = None
        self.is_android = system.is_android()
        super(ScanQRScreen, self).__init__(**kw)

    def init_kwargs(self, **kw):
        if _Debug:
            print('ScanQRScreen.init_kwargs', kw)
        self.scan_qr_callback = kw.pop('scan_qr_callback', '')
        return kw

    def get_title(self):
        return 'scan QR code'

    def on_enter(self):
        if _Debug:
            print('ScanQRScreen.on_enter')
        self.camera = CameraContainer()
        self.ids.container.add_widget(self.camera)
        self.camera.ids.camera_instance._camera.bind(on_texture=self.on_tex)
        self.camera.ids.camera_instance.play = True

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

    def on_tex(self, camera):
        try:
            image_data = camera.texture.pixels
            size = camera.texture.size
            pil_image = Image.frombytes(mode='RGBA', size=size, data=image_data)
            pil_image = self.fix_android_image(pil_image)
            self.symbols = []
            codes = pyzbar.decode(pil_image, symbols=self.code_types)
            for code in codes:
                symbol = BarSymbol(type=code.type, data=code.data)
                self.symbols.append(symbol)
            if not self.symbols:
                return
            result_text = ', '.join([symbol.data.decode('utf-8') for symbol in self.symbols])
        except Exception as exc:
            if _Debug:
                print('ScanQRScreen.on_tex', exc)
            return
        if _Debug:
            print('ScanQRScreen.on_tex', result_text)
        if self.scan_qr_callback:
            _cb = self.scan_qr_callback
            self.scan_qr_callback = None
            _cb(result_text)
