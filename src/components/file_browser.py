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

    def model_name(self):
        raise NotImplementedError()

    def listdir(self, fn):
        if _Debug:
            print('DistributedFileSystem.listdir', fn)
        dirs = []
        files = []
        sep_count = 1
        if fn != '/':
            sep_count = fn.rstrip('/').count('/') + 1
        for pf in screen.model(self.model_name()).values():
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

    def is_hidden(self, fn):
        _, _, fn = fn.rpartition(':')
        return fn.startswith('.')

    def is_dir(self, fn):
        if fn == '/':
            return True
        for pf in screen.model(self.model_name()).values():
            remote_path = pf['data']['remote_path']
            _, _, path = remote_path.rpartition(':')
            path = '/' + path
            if path == fn:
                return pf['data']['type'] == 'dir'
        return False


class PrivateDistributedFileSystem(DistributedFileSystem):

    def model_name(self):
        return 'private_file'

    def getsize(self, fn):
        if fn == '/':
            if _Debug:
                print('PrivateDistributedFileSystem.getsize', fn, 'returned 0')
            return 0
        path = fn.lstrip('/')
        indexed_global_id = screen.control().private_files_by_path.get(path)
        if indexed_global_id:
            indexed_pf = screen.model('private_file', snap_id=indexed_global_id)
            if indexed_pf:
                if _Debug:
                    print('PrivateDistributedFileSystem.getsize found indexed', fn)
                return indexed_pf['data']['size']
        for pf in screen.model(self.model_name()).values():
            remote_path = pf['data']['remote_path']
            _, _, path = remote_path.rpartition(':')
            path = '/' + path
            if path == fn:
                if _Debug:
                    print('PrivateDistributedFileSystem.getsize', fn)
                return pf['data']['size']
        if _Debug:
            print('PrivateDistributedFileSystem.getsize', fn, 'model data was not found')
        return 0

    def get_condition(self, fn):
        if fn == '/':
            return ''
        path = fn.lstrip('/')
        indexed_global_id = screen.control().private_files_by_path.get(path)
        if indexed_global_id:
            indexed_pf = screen.model('private_file', snap_id=indexed_global_id)
            if indexed_pf:
                if _Debug:
                    print('PrivateDistributedFileSystem.get_condition found indexed', fn)
                return '{}/{}'.format(indexed_pf['data'].get('delivered', '0%'), indexed_pf['data'].get('reliable', '0%'))
        for pf in screen.model(self.model_name()).values():
            remote_path = pf['data']['remote_path']
            _, _, path = remote_path.rpartition(':')
            path = '/' + path
            if path == fn:
                if _Debug:
                    print('PrivateDistributedFileSystem.get_condition', fn)
                return '{}/{}'.format(pf['data'].get('delivered', '0%'), pf['data'].get('reliable', '0%'))
        if _Debug:
            print('PrivateDistributedFileSystem.get_condition', fn, 'model data was not found')
        return 0


class SharedDistributedFileSystem(DistributedFileSystem):

    def model_name(self):
        return 'shared_file'


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
        self.file_system_type = 'private'

    def init(self, file_system_type='private', file_clicked_callback=None):
        if _Debug:
            print('DistributedFileChooserListView.init show_hidden=%r' % self.show_hidden)
        self.file_system_type = file_system_type
        self.file_clicked_callback = file_clicked_callback
        if self.file_system_type == 'private':
            api_client.add_model_listener('private_file', listener_cb=self.on_private_file)
        elif self.file_system_type == 'shared':
            api_client.add_model_listener('shared_file', listener_cb=self.on_shared_file)
        api_client.add_model_listener('remote_version', listener_cb=self.on_remote_version)
        self._trigger_update()

    def shutdown(self):
        if _Debug:
            print('DistributedFileChooserListView.shutdown')
        if self.file_system_type == 'private':
            api_client.remove_model_listener('private_file', listener_cb=self.on_private_file)
        elif self.file_system_type == 'shared':
            api_client.remove_model_listener('shared_file', listener_cb=self.on_shared_file)
        api_client.remove_model_listener('remote_version', listener_cb=self.on_remote_version)
        self.file_clicked_callback = None

    def on_private_file(self, payload):
        if _Debug:
            print('DistributedFileChooserListView.on_private_file', payload)
        remote_path = payload['data']['remote_path']
        global_id = payload['data']['global_id']
        _, _, path = remote_path.rpartition(':')
        path = '/' + path
        if payload.get('deleted'):
            self.index_by_global_id.pop(global_id, None)
            w = self.index_by_path.pop(path, None)
            if not w:
                self._update_files()
            else:
                self.layout.ids.treeview.remove_node(w)
        else:
            if path not in self.index_by_path:
                self._update_files()

    def on_remote_version(self, payload):
        if _Debug:
            print('DistributedFileChooserListView.on_remote_version', payload)
        remote_path = payload['data']['remote_path']
        global_id = payload['data']['global_id']
        _, _, path = remote_path.rpartition(':')
        path = '/' + path
        if global_id in self.index_by_global_id:
            self.index_by_global_id[global_id].ids.file_size.text = self.get_nice_size(path)
            self.index_by_global_id[global_id].ids.file_condition.text = self.get_condition(path)
        else:
            if path in self.index_by_path:
                self.index_by_path[path].ids.file_size.text = self.get_nice_size(path)
                self.index_by_path[path].ids.file_condition.text = self.get_condition(path)
            else:
                if _Debug:
                    print('        updating files')
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

    def get_condition(self, fn):
        if self.file_system.is_dir(fn):
            return ''
        return self.file_system.get_condition(fn)

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
            print('DistributedFileChooserListView._create_files_entries', args)
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
                get_condition=lambda: '',
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

        for index, remote_path in enumerate(files):
            _, _, fn = remote_path.rpartition(':')
            fn = '/' + fn

            def get_nice_size():
                return self.get_nice_size(fn)

            def get_condition():
                return self.get_condition(fn)

            _, _, bname = fn.rpartition('/')
            ctx = {
                'name': bname,
                'get_nice_size': get_nice_size,
                'get_condition': get_condition,
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
        template = self.layout._ENTRY_TEMPLATE if self.layout else self._ENTRY_TEMPLATE
        _, _, pth = ctx['remote_path'].rpartition(':')
        global_id = screen.control().private_files_by_path.get(pth)
        ctx['global_id'] = global_id
        if ctx['path'] in self.index_by_path:
            w = self.index_by_path[ctx['path']]
            w.ids.file_size.text = '{}'.format(self.get_nice_size(ctx['path']))
            w.ids.file_condition.text = '{}'.format(self.get_condition(ctx['path']))
            if _Debug:
                print('    DistributedFileChooserListView._create_entry_widget updated existing item', ctx['remote_path'], global_id)
        else:
            if _Debug:
                print('    DistributedFileChooserListView._create_entry_widget created new item', ctx['remote_path'], global_id)
            w = Builder.template(template, **ctx)
            self.index_by_path[ctx['path']] = w
        if global_id:
            self.index_by_global_id[global_id] = w
        return w

    def _show_progress(self):
        pass

    def _hide_progress(self):
        pass
