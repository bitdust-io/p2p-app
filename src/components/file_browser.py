import os
import time

from weakref import ref

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.treeview import TreeViewNode
from kivy.uix.filechooser import FileSystemAbstract, FileChooserController, FileChooserLayout

from components import screen

from lib import api_client

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class DistributedFileListEntry(FloatLayout, TreeViewNode):
    pass


class DistributedFileSystem(FileSystemAbstract):

    def listdir(self, fn):
        if _Debug:
            print('DistributedFileSystem.listdir', fn)
        dirs = []
        files = []
        sep_count = 1
        if fn != '/':
            sep_count = fn.rstrip('/').count('/') + 1
        for pf in screen.model('private_file').values():
            remote_path = pf['data']['remote_path']
            _, _, path = remote_path.rpartition(':')
            path = '/' + path
            if not path.startswith(fn):
                continue
            if sep_count != path.count('/'):
                continue
            if pf['data']['type'] == 'dir':
                dirs.append(remote_path)
            else:
                files.append(remote_path)
        dirs.sort()
        files.sort()
        if _Debug:
            print('    dirs=%d files=%d' % (len(dirs), len(files), ))
        return dirs + files

    def getsize(self, fn):
        # if _Debug:
        #     print('DistributedFileSystem.getsize', fn)
        if fn == '/':
            return 0
        for pf in screen.model('private_file').values():
            remote_path = pf['data']['remote_path']
            _, _, path = remote_path.rpartition(':')
            path = '/' + path
            if path == fn:
                return pf['data']['size']
        return 0

    def is_hidden(self, fn):
        # if _Debug:
        #     print('DistributedFileSystem.is_hidden', fn, fn.lstrip('/').startswith('.'))
        _, _, fn = fn.rpartition(':')
        # return False
        return fn.startswith('.')

    def is_dir(self, fn):
        if fn == '/':
            # if _Debug:
            #     print('DistributedFileSystem.is_dir', fn, True)
            return True
        for pf in screen.model('private_file').values():
            remote_path = pf['data']['remote_path']
            _, _, path = remote_path.rpartition(':')
            path = '/' + path
            if path == fn:
                # if _Debug:
                #     print('DistributedFileSystem.is_dir', fn, pf['data']['type'] == 'dir')
                return pf['data']['type'] == 'dir'
        # if _Debug:
        #     print('DistributedFileSystem.is_dir', fn, False)
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

    def __init__(self, **kwargs):
        super(DistributedFileChooserListView, self).__init__(**kwargs)
        self.index_by_path = {}
        self.index_by_global_id = {}
        self.file_clicked_callback = None
        # self.show_hidden = True

    def init(self, file_clicked_callback=None):
        if _Debug:
            print('DistributedFileChooserListView.init show_hidden=%r' % self.show_hidden)
        self.file_clicked_callback = file_clicked_callback
        api_client.add_model_listener('private_file', listener_cb=self.on_private_file)
        api_client.add_model_listener('remote_version', listener_cb=self.on_remote_version)
        self._trigger_update()

    def shutdown(self):
        if _Debug:
            print('DistributedFileChooserListView.shutdown')
        api_client.remove_model_listener('private_file', listener_cb=self.on_private_file)
        api_client.remove_model_listener('remote_version', listener_cb=self.on_remote_version)
        self.file_clicked_callback = None

    def on_private_file(self, payload):
        if _Debug:
            print('DistributedFileChooserListView.on_private_file', payload)
        remote_path = payload['data']['remote_path']
        global_id = payload['data']['global_id']
        _, _, path = remote_path.rpartition(':')
        if payload.get('deleted'):
            self.index_by_path.pop(path, None)
            self.index_by_global_id.pop(global_id, None)
            self._update_files()
        else:
            if path not in self.index_by_path:
                self._update_files()

    def on_remote_version(self, payload):
        if _Debug:
            print('DistributedFileChooserListView.on_remote_version', payload)
        remote_path = payload['data']['remote_path']
        global_id = payload['data']['global_id']
        _, _, path = remote_path.rpartition(':')
        if path not in self.index_by_path:
            self._update_files()
        else:
            if global_id in self.index_by_global_id:
                self.index_by_global_id[global_id].ids.file_size.text = self.get_nice_size(path)
            else:
                self._update_files()

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
            if self.file_clicked_callback:
                self.file_clicked_callback(entry)

    def open_entry(self, entry):
        if _Debug:
            print('DistributedFileChooserListView.open_entry', entry)
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
            path=kwargs.get('path', self.path),
            parent=self._gitems_parent,
            files=kwargs.get('files', None),
        )

        ev = self._create_files_entries_ev
        if ev is not None:
            ev.cancel()

        self._hide_progress()
        if self._create_files_entries():
            if ev is None:
                ev = self._create_files_entries_ev = Clock.schedule_interval(
                    self._create_files_entries, .1)
            ev()

    def _create_files_entries(self, *args):
        if _Debug:
            print('DistributedFileChooserListView._create_files_entries')
        start = time.time()
        finished = False
        index = total = count = 1
        while time.time() - start < 0.05 or count < 10:
            try:
                index, total, item = next(self._gitems_gen)
                self._gitems.append(item)
                count += 1
            except StopIteration:
                finished = True
                break
            except TypeError:  # in case _gitems_gen is None
                finished = True
                break

        # if this wasn't enough for creating all the entries, show a progress
        # bar, and report the activity to the user.
        if not finished:
            self._show_progress()
            # self._progress.total = total
            # self._progress.index = index
            return True

        # we created all the files, now push them on the view
        self._items = items = self._gitems
        parent = self._gitems_parent
        if parent is None:
            self.dispatch('on_entries_cleared')
            for entry in items:
                self.dispatch('on_entry_added', entry, parent)
        else:
            parent.entries[:] = items
            for entry in items:
                self.dispatch('on_subentry_to_entry', entry, parent)
        self.files[:] = self._get_file_paths(items)

        # stop the progression / creation
        self._hide_progress()
        self._gitems = None
        self._gitems_gen = None
        ev = self._create_files_entries_ev
        if ev is not None:
            ev.cancel()
        return False

    def _generate_file_entries(self, *args, **kwargs):
        if _Debug:
            print('DistributedFileChooserListView._generate_file_entries', kwargs.get('parent', None), self.path, kwargs.get('files', None))
        is_root = False
        path = kwargs.get('path', self.path)
        have_parent = kwargs.get('parent', None) is not None
        files = kwargs.get('files', None)

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
            for index, total, item in self._add_files(path, files=files):
                yield index, total, item
        except Exception as exc:
            if _Debug:
                print('DistributedFileChooserListView._generate_file_entries', exc)
            self.files[:] = []

    def _add_files(self, path, parent=None, **kwargs):
        if _Debug:
            print('    DistributedFileChooserListView._add_files', path, parent, kwargs.get('files', []))
        if not self.file_system.is_dir(path):
            path, _, _ = path.rpartition('/')

        files = []
        extra_files = kwargs.get('files', []) or []
        fappend = files.append
        if extra_files:
            for remote_path in extra_files:
                fappend(remote_path)
        else:
            for remote_path in self.file_system.listdir(path):
                # fappend(os.path.join(path, f))
                fappend(remote_path)
        print('!!!!!! files', files, 'extra_files', extra_files)
        # files += extra_files
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

        # if _Debug:
        #     print('    files=%r' % files)

        for index, remote_path in enumerate(files):
            _, _, fn = remote_path.rpartition(':')
            fn = '/' + fn

            # if fn in self.index_by_path:
            #     w = self.index_by_path[fn]
            #     w.ids.file_size.text = '{}'.format(self.get_nice_size(fn))
            #     continue

            def get_nice_size():
                # Use a closure for lazy-loading here
                return self.get_nice_size(fn)

            _, _, bname = fn.rpartition('/')
            ctx = {
                'name': bname,
                'get_nice_size': get_nice_size,
                'path': fn,
                'global_id': '',
                'remote_path': remote_path,
                'controller': wself,
                'isdir': self.file_system.is_dir(fn),
                'parent': parent,
                'sep': '/',
            }
            entry = self._create_entry_widget(ctx)
            yield index, total, entry

    def _create_entry_widget(self, ctx):
        template = self.layout._ENTRY_TEMPLATE\
            if self.layout else self._ENTRY_TEMPLATE
        global_id = screen.control().private_files_by_path.get(ctx['remote_path'])
        ctx['global_id'] = global_id
        if _Debug:
            print('    DistributedFileChooserListView._create_entry_widget', ctx['remote_path'], ctx['isdir'], global_id)
        w = Builder.template(template, **ctx)
        self.index_by_path[ctx['path']] = w
        if global_id:
            self.index_by_global_id[global_id] = w
        return w

    def _show_progress(self):
        pass

    def _hide_progress(self):
        pass
