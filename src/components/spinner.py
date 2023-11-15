from kivy.uix.progressbar import ProgressBar
from kivy.core.text import Label
from kivy.metrics import sp
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.clock import Clock


class CircularProgressBar(ProgressBar):

    def __init__(self, **kwargs):
        super(CircularProgressBar, self).__init__(**kwargs)
        self._task = None
        self._shown = False
        self.thickness = 5
        self.text_label = 'starting'
        self.label = Label(text=self.text_label, font_size=sp(12), font_name='RobotoMono-Regular')
        self.texture_size = None
        self.refresh_text()
        self.draw()

    def draw(self):
        with self.canvas:
            self.canvas.clear()
            if not self._shown:
                return
            Color(0.95, 0.95, 0.95)
            Ellipse(pos=self.pos, size=self.size)
            Color(0.85, 0.85, 0.85)
            Ellipse(pos=self.pos, size=self.size,
                angle_end=(0.001 if self.value_normalized == 0 else self.value_normalized * self.max))
            Color(1, 1, 1, 1)
            Ellipse(pos=(self.pos[0] + self.thickness / 2, self.pos[1] + self.thickness / 2),
                size=(self.size[0] - self.thickness, self.size[1] - self.thickness))
            Color(0.2, 0.2, 0.2, 1)
            Rectangle(texture=self.label.texture, size=self.texture_size,
                pos=(self.size[0] / 2 - self.texture_size[0] / 2 + self.pos[0],
                     self.size[1] / 2 - self.texture_size[1] / 2 + self.pos[1]))

    def refresh_text(self):
        self.label.refresh()
        self.texture_size = list(self.label.texture.size)

    def set_value(self, value):
        self.value = value
        self.label.text = '  ' + self.text_label + '  \n  ' + '.' * int(len(self.text_label) * value / self.max)
        self.refresh_text()
        self.draw()

    def start(self, label='starting'):
        self.text_label = label
        self._shown = True
        if self._task:
            self._task.cancel()
        self._task = None
        self._task = Clock.schedule_interval(self._animate, 0.02)

    def stop(self):
        if self._task:
            self._task.cancel()
        self._task = None
        self._shown = False
        self.label.text = ''
        self.refresh_text()
        self.draw()

    def _animate(self, dt):
        if self.value < self.max:
            self.set_value(self.value + 5)
        else:
            self.set_value(0)
