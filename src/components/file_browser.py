import os
import time

from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.treeview import TreeViewNode
from kivy.uix.filechooser import FileSystemAbstract, FileChooserController, FileChooserLayout

from components import screen

from lib import system
from lib import api_client

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class DistributedFileListEntry(FloatLayout, TreeViewNode):

    def apply_context(self, ctx):
        self.path = ctx['path']
        self.global_id = ctx['global_id']
        self.remote_path = ctx['remote_path']
        self.is_leaf = not ctx['isdir'] or ctx['name'].endswith('..' + ctx['sep'])
        self.ids.filename.text = ctx['name']
        self.ids.filename.font_name = ctx['font_name']
        self.ids.file_condition.text = ctx['get_condition']()
        self.ids.file_condition.font_name = ctx['font_name']
        self.ids.file_size.text = ctx['get_nice_size']()
        self.ids.file_size.font_name = ctx['font_name']
        self._entry_touched = ctx['entry_touched']
        self._entry_released = ctx['entry_released']

    def _on_touch_down(self, *args):
        return self.collide_point(*args[1].pos) and self._entry_touched(self, args[1])

    def _on_touch_up(self, *args):
        return self.collide_point(*args[1].pos) and self._entry_released(self, args[1])

#------------------------------------------------------------------------------

class DistributedFileSystem(FileSystemAbstract):

    key_id = None

    def model_name(self):
        raise NotImplementedError()

    def is_hidden(self, fn):
        _, _, fn = fn.rpartition(':')
        return fn.startswith('.')

#------------------------------------------------------------------------------

class PrivateDistributedFileSystem(DistributedFileSystem):

    def model_name(self):
        return 'private_file'

    def is_dir(self, fn):
        if fn == '/':
            return True
        path = fn.lstrip('/')
        indexed_global_id = screen.control().private_files_index.get(path)
        if indexed_global_id:
            pf = screen.model(self.model_name(), snap_id=indexed_global_id)
            if pf:
                return pf['data']['type'] == 'dir'
        for pf in screen.model(self.model_name()).values():
            remote_path = pf['data']['remote_path']
            _, _, path = remote_path.rpartition(':')
            path = '/' + path
            if path == fn:
                return pf['data']['type'] == 'dir'
        return False

    def listdir(self, fn):
        if _Debug:
            print('PrivateDistributedFileSystem.listdir', self.model_name(), fn)
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

    def getsize(self, fn):
        if fn == '/':
            if _Debug:
                print('PrivateDistributedFileSystem.getsize', fn, 'returned 0')
            return 0
        path = fn.lstrip('/')
        indexed_global_id = screen.control().private_files_index.get(path)
        if indexed_global_id:
            details = screen.control().remote_files_details.get(indexed_global_id)
            if details:
                if _Debug:
                    print('PrivateDistributedFileSystem.getsize found indexed', fn, details['size'])
                return details['size']
        if _Debug:
            print('PrivateDistributedFileSystem.getsize', fn, 'model data was not found')
        return 0

    def get_condition(self, fn):
        if fn == '/':
            return ''
        path = fn.lstrip('/')
        indexed_global_id = screen.control().private_files_index.get(path)
        if indexed_global_id:
            details = screen.control().remote_files_details.get(indexed_global_id)
            if details:
                if _Debug:
                    print('PrivateDistributedFileSystem.get_condition found indexed', fn, details)
                return system.make_nice_file_condition(details)
        if _Debug:
            print('PrivateDistributedFileSystem.get_condition', fn, 'model data was not found')
        return ''

#------------------------------------------------------------------------------

class SharedDistributedFileSystem(DistributedFileSystem):

    def model_name(self):
        return 'shared_file'

    def is_dir(self, fn):
        if fn == '/':
            return True
        path = fn.lstrip('/')
        remote_path = '{}:{}'.format(self.key_id, path)
        indexed_global_id = screen.control().shared_files_index.get(remote_path)
        if indexed_global_id:
            sf = screen.model(self.model_name(), snap_id=indexed_global_id)
            if sf:
                return sf['data']['type'] == 'dir'
        for pf in screen.model(self.model_name()).values():
            remote_path = pf['data']['remote_path']
            _, _, path = remote_path.rpartition(':')
            path = '/' + path
            if path == fn:
                return pf['data']['type'] == 'dir'
        return False

    def listdir(self, fn):
        if _Debug:
            print('SharedDistributedFileSystem.listdir', self.key_id, fn)
        dirs = []
        files = []
        sep_count = 1
        if fn != '/':
            sep_count = fn.rstrip('/').count('/') + 1
        for sf in screen.model(self.model_name()).values():
            if not sf['data']['global_id'].startswith(self.key_id):
                continue
            remote_path = sf['data']['remote_path']
            _, _, path = remote_path.rpartition(':')
            path = '/' + path
            if not path.startswith(fn):
                continue
            if sep_count != path.count('/'):
                continue
            if sf['data']['type'] == 'dir':
                dirs.append(remote_path)
            else:
                files.append(remote_path)
        dirs.sort()
        files.sort()
        if _Debug:
            print('    dirs=%d files=%d' % (len(dirs), len(files), ))
        return dirs + files

    def getsize(self, fn):
        if fn == '/':
            if _Debug:
                print('SharedDistributedFileSystem.getsize', self.key_id, fn, 'returned 0')
            return 0
        path = fn.lstrip('/')
        remote_path = '{}:{}'.format(self.key_id, path)
        indexed_global_id = screen.control().shared_files_index.get(remote_path)
        if indexed_global_id:
            details = screen.control().remote_files_details.get(indexed_global_id)
            if details:
                if _Debug:
                    print('SharedDistributedFileSystem.getsize found indexed', self.key_id, remote_path, details['size'])
                return details['size']
        if _Debug:
            print('SharedDistributedFileSystem.getsize', self.key_id, remote_path, 'model data was not found')
        return 0

    def get_condition(self, fn):
        if fn == '/':
            return ''
        path = fn.lstrip('/')
        remote_path = '{}:{}'.format(self.key_id, path)
        indexed_global_id = screen.control().shared_files_index.get(remote_path)
        if indexed_global_id:
            details = screen.control().remote_files_details.get(indexed_global_id)
            if details:
                if _Debug:
                    print('SharedDistributedFileSystem.get_condition found indexed', self.key_id, remote_path, details)
                return system.make_nice_file_condition(details)
        if _Debug:
            print('SharedDistributedFileSystem.get_condition', self.key_id, remote_path, 'model data was not found')
        return ''

#------------------------------------------------------------------------------

class DistributedFileChooserListLayout(FileChooserLayout):

    VIEWNAME = 'list'
    _ENTRY_TEMPLATE = 'DistributedFileListEntry'

    def __init__(self, **kwargs):
        super(DistributedFileChooserListLayout, self).__init__(**kwargs)
        self.fbind('on_entries_cleared', self.scroll_to_top)

    def scroll_to_top(self, *args):
        self.ids.scrollview.scroll_y = 1.0

#------------------------------------------------------------------------------

class DistributedFileChooserListView(FileChooserController):

    _ENTRY_TEMPLATE = 'DistributedFileListEntry'

    def __init__(self, **kwargs):
        self.opened = False
        super(DistributedFileChooserListView, self).__init__(**kwargs)
        self.index_by_remote_path = {}
        self.index_by_global_id = {}
        self.file_clicked_callback = None
        self.file_system_type = None

    def init(self, file_system_type, key_id=None, file_clicked_callback=None):
        if _Debug:
            print('DistributedFileChooserListView.init file_system_type=%r key_id=%r' % (file_system_type, key_id, ))
        self.file_system_type = file_system_type
        self.file_clicked_callback = file_clicked_callback
        if self.file_system_type == 'private':
            api_client.add_model_listener('private_file', listener_cb=self.on_private_file)
        elif self.file_system_type == 'shared':
            api_client.add_model_listener('shared_file', listener_cb=self.on_shared_file)
            self.file_system.key_id = key_id
        api_client.add_model_listener('remote_version', listener_cb=self.on_remote_version)

    def shutdown(self):
        if _Debug:
            print('DistributedFileChooserListView.shutdown')
        if self.file_system_type == 'private':
            api_client.remove_model_listener('private_file', listener_cb=self.on_private_file)
        elif self.file_system_type == 'shared':
            api_client.remove_model_listener('shared_file', listener_cb=self.on_shared_file)
        api_client.remove_model_listener('remote_version', listener_cb=self.on_remote_version)
        self.file_clicked_callback = None
        self.close()

    def open(self):
        self.opened = True
        self._trigger_update()

    def close(self):
        if _Debug:
            print('DistributedFileChooserListView.close')
        self.opened = False
        self.dispatch('on_entries_cleared')
        self.layout.ids.treeview.clear_widgets()

    def on_private_file(self, payload):
        if _Debug:
            print('DistributedFileChooserListView.on_private_file', payload)
        if not self.opened:
            return
        remote_path = payload['data']['remote_path']
        global_id = payload['data']['global_id']
        if payload.get('deleted'):
            self.index_by_global_id.pop(global_id, None)
            w = self.index_by_remote_path.pop(remote_path, None)
            if not w:
                self._update_files()
            else:
                self.layout.ids.treeview.remove_node(w)
        else:
            if remote_path not in self.index_by_remote_path:
                self._update_files()

    def on_shared_file(self, payload):
        if _Debug:
            print('DistributedFileChooserListView.on_shared_file', self.file_system.key_id, payload)
        if not self.opened:
            return
        remote_path = payload['data']['remote_path']
        global_id = payload['data']['global_id']
        if self.file_system_type == 'shared':
            if not global_id.startswith(self.file_system.key_id):
                return
        if payload.get('deleted'):
            self.index_by_global_id.pop(global_id, None)
            w = self.index_by_remote_path.pop(remote_path, None)
            if not w:
                self._update_files()
            else:
                self.layout.ids.treeview.remove_node(w)
        else:
            if remote_path not in self.index_by_remote_path:
                self._update_files()

    def on_remote_version(self, payload):
        if _Debug:
            print('DistributedFileChooserListView.on_remote_version', payload)
        if not self.opened:
            return
        remote_path = payload['data']['remote_path']
        global_id = payload['data']['global_id']
        if self.file_system_type == 'shared':
            if not global_id.startswith(self.file_system.key_id):
                return
        _, _, path = remote_path.rpartition(':')
        path = '/' + path
        if global_id in self.index_by_global_id:
            self.index_by_global_id[global_id].ids.file_size.text = self.get_nice_size(path)
            self.index_by_global_id[global_id].ids.file_condition.text = self.get_condition(path)
        else:
            if remote_path in self.index_by_remote_path:
                self.index_by_remote_path[remote_path].ids.file_size.text = self.get_nice_size(path)
                self.index_by_remote_path[remote_path].ids.file_condition.text = self.get_condition(path)
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

    def _trigger_update(self, *args):
        if not self.opened:
            return
        FileChooserController._trigger_update(self, *args)

    def _update_files(self, *args, **kwargs):
        if _Debug:
            print('DistributedFileChooserListView._update_files', self.file_system.key_id, args, kwargs)
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
                name=back,
                size='',
                path=back,
                font_name=self.font_name,
                isdir=True, parent=None,
                sep='/  ',
                get_condition=lambda: '',
                get_nice_size=lambda: '',
                entry_touched=self.entry_touched,
                entry_released=self.entry_released,
            ))
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
                'path': fn,
                'global_id': '',
                'remote_path': remote_path,
                'font_name': self.font_name,
                'isdir': self.file_system.is_dir(fn),
                'parent': parent,
                'sep': '/',
                'get_nice_size': get_nice_size,
                'get_condition': get_condition,
                'entry_touched': self.entry_touched,
                'entry_released': self.entry_released,
            }
            entry = self._create_entry_widget(ctx)
            yield index, total, entry

    def _create_entry_widget(self, ctx):
        template = self.layout._ENTRY_TEMPLATE if self.layout else self._ENTRY_TEMPLATE
        _, _, pth = ctx['remote_path'].rpartition(':')
        if self.file_system_type == 'private':
            global_id = screen.control().private_files_index.get(pth)
        else:
            global_id = screen.control().shared_files_index.get(ctx['remote_path'])
        ctx['global_id'] = global_id
        if ctx['remote_path'] in self.index_by_remote_path:
            w = self.index_by_remote_path[ctx['remote_path']]
            w.ids.file_size.text = '{}'.format(self.get_nice_size(ctx['path']))
            w.ids.file_condition.text = '{}'.format(self.get_condition(ctx['path']))
            if _Debug:
                print('    DistributedFileChooserListView._create_entry_widget updated existing item', ctx['remote_path'], global_id)
        else:
            if template == 'DistributedFileListEntry':
                w = DistributedFileListEntry()
                w.apply_context(ctx)
            else:
                raise Exception('Unknown template: %r' % template)
            self.index_by_remote_path[ctx['remote_path']] = w
            if _Debug:
                print('    DistributedFileChooserListView._create_entry_widget created new item', ctx['remote_path'], global_id, template, w)
        if global_id:
            self.index_by_global_id[global_id] = w
        return w

    def _show_progress(self):
        pass

    def _hide_progress(self):
        pass
