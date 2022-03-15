import os

from weakref import ref

from kivy.clock import Clock
from kivy.uix.filechooser import FileSystemAbstract, FileChooserController, FileChooserLayout

from components import screen

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------


class DistributedFileSystem(FileSystemAbstract):

    def listdir(self, fn):
        if _Debug:
            print('DistributedFileSystem.listdir', fn)
        # api_client.files_list(remote_path=fn)
        dirs = []
        files = []
        sep_count = 1
        if fn != '/':
            sep_count = fn.rstrip('/').count('/') + 1
        for pf in screen.model('private_file').values():
            _, _, path = pf['data']['remote_path'].rpartition(':')
            path = '/' + path
            if not path.startswith(fn):
                continue
            if sep_count != path.count('/'):
                continue
            if pf['data']['type'] == 'dir':
                dirs.append(path)
            else:
                files.append(path)
        dirs.sort()
        files.sort()
        if _Debug:
            print('    dirs=%r files=%r' % (dirs, files, ))
        return dirs + files

    def getsize(self, fn):
        if _Debug:
            print('DistributedFileSystem.getsize', fn)
        if fn == '/':
            return 0
        for pf in screen.model('private_file').values():
            _, _, path = pf['data']['remote_path'].rpartition(':')
            path = '/' + path
            if path == fn:
                return pf['data']['size']
        return 0

    def is_hidden(self, fn):
        if _Debug:
            print('DistributedFileSystem.is_hidden', fn)
        return False

    def is_dir(self, fn):
        if _Debug:
            print('DistributedFileSystem.is_dir', fn)
        if fn == '/':
            return True
        for pf in screen.model('private_file').values():
            _, _, path = pf['data']['remote_path'].rpartition(':')
            path = '/' + path
            if path == fn:
                return pf['data']['type'] == 'dir'
        return False


class DistributedFileChooserListLayout(FileChooserLayout):
    VIEWNAME = 'list'
    _ENTRY_TEMPLATE = 'DistributedFileListEntry'

    def __init__(self, **kwargs):
        super(DistributedFileChooserListLayout, self).__init__(**kwargs)
        self.fbind('on_entries_cleared', self.scroll_to_top)

    def scroll_to_top(self, *args):
        self.ids.scrollview.scroll_y = 1.0


class DistributedFileChooserListView(FileChooserController):

    _ENTRY_TEMPLATE = 'DistributedFileListEntry'

    def _create_entry_widget(self, ctx):
        ret = super()._create_entry_widget(ctx)
        if _Debug:
            print('DistributedFileChooserListView._create_entry_widget', ret, ctx)
        return ret

    def entry_touched(self, entry, touch):
        if _Debug:
            print('DistributedFileChooserListView.entry_touched', entry, touch)
        if 'button' in touch.profile and touch.button in ('scrollup', 'scrolldown', 'scrollleft', 'scrollright'):
            return False

        _dir = self.file_system.is_dir(entry.path)
        dirselect = self.dirselect

        if _dir and dirselect and touch.is_double_tap:
            self.open_entry(entry)
            return

        if self.multiselect:
            if entry.path in self.selection:
                self.selection.remove(entry.path)
            else:
                if _dir and not self.dirselect:
                    self.open_entry(entry)
                    return
                self.selection.append(entry.path)
        else:
            if _dir and not self.dirselect:
                return
            self.selection = [os.path.join(self.path, entry.path), ]

    def open_entry(self, entry):
        if _Debug:
            print('DistributedFileChooserListView.entry', entry)
        if self.file_system.is_dir(entry.path):
            entry.locked = True
        else:
            self.path = os.path.join(self.path, entry.path)
            self.selection = [self.path, ] if self.dirselect else []

    def _update_files(self, *args, **kwargs):
        if _Debug:
            print('DistributedFileChooserListView._update_files', args, kwargs)
        self._gitems = []
        self._gitems_parent = kwargs.get('parent', None)
        self._gitems_gen = self._generate_file_entries(
            path=kwargs.get('path', self.path), parent=self._gitems_parent)

        ev = self._create_files_entries_ev
        if ev is not None:
            ev.cancel()

        self._hide_progress()
        if self._create_files_entries():
            if ev is None:
                ev = self._create_files_entries_ev = Clock.schedule_interval(
                    self._create_files_entries, .1)
            ev()

    def _generate_file_entries(self, *args, **kwargs):
        if _Debug:
            print('DistributedFileChooserListView._generate_file_entries', args, kwargs)
        is_root = False
        path = kwargs.get('path', self.path)
        have_parent = kwargs.get('parent', None) is not None

        if self.rootpath:
            rootpath = self.rootpath
            if not path.startswith(rootpath):
                self.path = rootpath
                return
            elif path == rootpath:
                is_root = True
        else:
            is_root = path in ['', '/', ]

        if not is_root and not have_parent:
            back = '../'
            pardir = self._create_entry_widget(dict(
                name=back, size='', path=back, controller=ref(self),
                isdir=True, parent=None, sep='/  ',
                get_nice_size=lambda: ''))
            yield 0, 1, pardir

        try:
            for index, total, item in self._add_files(path):
                yield index, total, item
        except:
            self.files[:] = []

    def _add_files(self, path, parent=None):
        if _Debug:
            print('DistributedFileChooserListView._add_files', path, parent, self.file_system)
        if not self.file_system.is_dir(path):
            path, _, _ = path.rpartition('/')

        files = []
        fappend = files.append
        for f in self.file_system.listdir(path):
            fappend(os.path.join(path, f))
        # Apply filename filters
        files = self._apply_filters(files)
        # Sort the list of files
        files = self.sort_func(files, self.file_system)
        is_hidden = self.file_system.is_hidden
        if not self.show_hidden:
            files = [x for x in files if not is_hidden(x)]
        self.files[:] = files
        total = len(files)
        wself = ref(self)
        for index, fn in enumerate(files):

            def get_nice_size():
                # Use a closure for lazy-loading here
                return self.get_nice_size(fn)

            _, _, bname = fn.rpartition('/')
            ctx = {'name': bname,
                   'get_nice_size': get_nice_size,
                   'path': fn,
                   'controller': wself,
                   'isdir': self.file_system.is_dir(fn),
                   'parent': parent,
                   'sep': '/', }
            entry = self._create_entry_widget(ctx)
            yield index, total, entry
