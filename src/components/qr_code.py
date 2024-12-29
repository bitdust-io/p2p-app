from functools import partial
from threading import Thread

import qrcode

from kivy.clock import Clock
from kivy.graphics.texture import Texture  # @UnresolvedImport
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, StringProperty  # @UnresolvedImport
from kivy.uix.floatlayout import FloatLayout


class QRCodeWidget(FloatLayout):

    show_border = BooleanProperty(True)
    """Whether to show border around the widget.

    :data:`show_border` is a :class:`~kivy.properties.BooleanProperty`,
    defaulting to `True`.
    """

    data = StringProperty(None, allow_none=True)
    """Data using which the qrcode is generated.

    :data:`data` is a :class:`~kivy.properties.StringProperty`, defaulting to
    `None`.
    """

    error_correction = NumericProperty(qrcode.constants.ERROR_CORRECT_L)
    """The error correction level for the qrcode.

    :data:`error_correction` is a constant in :module:`~qrcode.constants`,
    defaulting to `qrcode.constants.ERROR_CORRECT_L`.
    """

    background_color = ListProperty((1, 1, 1, 1))
    """Background color of the background of the widget to be displayed
    behind the qrcode.

    :data:`background_color` is a :class:`~kivy.properties.ListProperty`,
    defaulting to `(1, 1, 1, 1)`.
    """

    loading_image = StringProperty('data/images/image-loading.gif')
    """Intermediate image to be displayed while the widget ios being loaded.

    :data:`loading_image` is a :class:`~kivy.properties.StringProperty`,
    defaulting to `'data/images/image-loading.gif'`.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.addr = None
        self.qr = None
        self._qrtexture = None

    def on_data(self, instance, value):
        if not (self.canvas or value):
            return
        img = self.ids.get('qrimage', None)

        if not img:
            # if texture hasn't yet been created delay the texture updating
            Clock.schedule_once(lambda dt: self.on_data(instance, value))
            return
        img.anim_delay = .25
        img.source = self.loading_image
        Thread(target=partial(self.generate_qr, value)).start()

    def on_error_correction(self, instance, value):
        self.update_qr()

    def generate_qr(self, value):
        self.set_addr(value)
        self.update_qr()

    def set_addr(self, addr):
        if self.addr == addr:
            return
        MinSize = 210 if len(addr) < 128 else 500
        self.setMinimumSize((MinSize, MinSize))
        self.addr = addr
        self.qr = None

    def update_qr(self):
        if not self.addr and self.qr:
            return
        QRCode = qrcode.QRCode
        addr = self.addr
        print('update_qr', self, addr)
        try:
            self.qr = qr = QRCode(
                version=None,
                error_correction=self.error_correction,
                box_size=10,
                border=0,
            )
            qr.add_data(addr)
            qr.make(fit=True)
        except Exception as e:
            print(e)
            self.qr = None
        self.update_texture()

    def setMinimumSize(self, size):
        # currently unused, do we need this?
        print('setMinimumSize', size)
        self._texture_size = size

    def _create_texture(self, k, dt):
        self._qrtexture = texture = Texture.create(size=(k, k), colorfmt='rgb')
        # don't interpolate texture
        texture.min_filter = 'nearest'
        texture.mag_filter = 'nearest'

    def update_texture(self):
        if not self.addr:
            return

        matrix = self.qr.get_matrix()
        k = len(matrix)

        # create the texture in main UI thread otherwise
        # this will lead to memory corruption
        Clock.schedule_once(partial(self._create_texture, k), -1)

        cr, cg, cb, ca = self.background_color[:]
        cr, cg, cb = int(cr*255), int(cg*255), int(cb*255)
        # used bytearray for python 3.5 eliminates need for btext
        buff = bytearray()
        for r in range(k):
            for c in range(k):
                buff.extend([0, 0, 0] if matrix[r][c] else [cr, cg, cb])

        # then blit the buffer
        # join not necessary when using a byte array
        # buff =''.join(map(chr, buff))
        # update texture in UI thread.
        Clock.schedule_once(lambda dt: self._upd_texture(buff))

    def _upd_texture(self, buff):
        texture = self._qrtexture
        if not texture:
            # if texture hasn't yet been created delay the texture updating
            Clock.schedule_once(lambda dt: self._upd_texture(buff))
            return

        texture.blit_buffer(buff, colorfmt='rgb', bufferfmt='ubyte')
        texture.flip_vertical()
        img = self.ids.qrimage
        img.anim_delay = -1
        img.texture = texture
        img.canvas.ask_update()
