import re

#------------------------------------------------------------------------------

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.treeview import TreeView, TreeViewNode
from kivy.properties import ListProperty, StringProperty, NumericProperty  # @UnresolvedImport

#------------------------------------------------------------------------------

from components.screen import AppScreen
from components.labels import NormalLabel
from components.buttons import NormalButton, CustomFlatButton
from components.text_input import SingleLineTextInput
from components.layouts import HorizontalLayout, VerticalLayout

from lib import api_client
from lib import websock

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class OptionNameLabel(CustomFlatButton):
    pass


class OptionDescriptionLabel(NormalLabel):
    pass


class OptionValueTextInput(SingleLineTextInput):
    pass


class OptionValueIntInput(OptionValueTextInput):

    def insert_text(self, substring, from_undo=False):
        min_value = self.parent.parent.option_value_min
        max_value = self.parent.parent.option_value_max
        t = self.text
        c = self.cursor[0]
        if c == len(t):
            new_text = self.text + substring
        else:
            new_text = t[:c] + substring + t[c:]
        if new_text != '':
            try:
                new_value = int(new_text)
            except:
                return
            if min_value is not None and min_value > new_value:
                return
            if max_value is not None and max_value < new_value:
                return
            return super(OptionValueIntInput, self).insert_text(substring, from_undo=from_undo)


class OptionValueDiskSpaceInput(OptionValueTextInput):
    pass


class OptionValueSingleChoiceInput(OptionValueTextInput):
    pass


#------------------------------------------------------------------------------

class TreeElement(TreeViewNode):

    item_key = None
    item_data = None

    def __init__(self, **kwargs):
        self.item_key = kwargs.pop('item_key')
        self.item_data = kwargs.pop('item_data')
        super(TreeElement, self).__init__(**kwargs)
        self.no_selection = True
        self.even_color = (1, 1, 1, 1)
        self.odd_color = (1, 1, 1, 1)
        if _Debug:
            print('created element %r : %r' % (self.item_key, id(self), ))

    def __del__(self, **kwargs):
        if _Debug:
            print('erased element %r : %r' % (self.item_key, id(self), ))


class ParentElement(CustomFlatButton, TreeElement):

    text_halign = 'left'

    def __init__(self, **kwargs):
        self.item_clicked_callback = kwargs.pop('item_clicked_callback', None)
        super(ParentElement, self).__init__(**kwargs)


class ServiceElement(HorizontalLayout, TreeElement):

    service_name = StringProperty('')
    service_state = StringProperty('')

    def __init__(self, **kwargs):
        self.service_name = kwargs.pop('service_name')
        self.service_state = kwargs.pop('service_state')
        self.item_clicked_callback = kwargs.pop('item_clicked_callback', None)
        super(ServiceElement, self).__init__(**kwargs)


class OptionElement(TreeElement):

    option_name = StringProperty('')
    option_value = StringProperty(None, allownone=True)
    option_value_default = StringProperty(None, allownone=True)
    option_value_recent = StringProperty(None, allownone=True)
    option_description = StringProperty('')

    def __init__(self, **kwargs):
        self.option_name = kwargs.pop('option_name')
        self.option_value = kwargs.pop('option_value')
        self.option_value_default = kwargs.pop('option_value_default', None)
        self.option_description = kwargs.pop('option_description', '')
        self.option_readonly = kwargs.pop('option_readonly', False)
        self.value_modified_callback = kwargs.pop('value_modified_callback', None)
        self.item_clicked_callback = kwargs.pop('item_clicked_callback', None)
        self.option_value_recent = self.option_value
        kwargs['size_hint'] = (1, None)
        kwargs['padding'] = 0
        kwargs['spacing'] = 0
        super(OptionElement, self).__init__(**kwargs)

    def on_option_value_input_updated(self):
        if _Debug:
            print('on_option_value_input_updated', self.item_key, self.option_value_recent, self.ids.option_value_input.text)
        if self.value_modified_callback:
            self.value_modified_callback(self.item_key, self.ids.option_value_input.text)


class BooleanElement(OptionElement, VerticalLayout):

    def __init__(self, **kwargs):
        super(BooleanElement, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        if self.option_readonly:
            self.ids.option_value_checkbox.disabled = True


class IntegerElement(OptionElement, VerticalLayout):

    option_value_min = NumericProperty(None, allownone=True)
    option_value_max = NumericProperty(None, allownone=True)

    def __init__(self, **kwargs):
        self.option_value_min = kwargs.pop('option_value_min', None)
        self.option_value_max = kwargs.pop('option_value_max', None)
        super(IntegerElement, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        if self.option_readonly:
            self.ids.option_value_input.read_only = True

    def on_focus_changed(self):
        if self.ids.option_value_input.focus:
            self.option_value_recent = self.ids.option_value_input.text
        else:
            if self.ids.option_value_input.text != self.option_value_recent:
                self.on_option_value_input_updated()
            self.option_value_recent = None


class DiskSpaceElement(OptionElement, VerticalLayout):

    def __init__(self, **kwargs):
        super(DiskSpaceElement, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        if self.option_readonly:
            self.ids.option_value_input.read_only = True

    def split_value(self, txt):
        val, _, suf = txt.rpartition(' ')
        val = ''.join(filter(str.isdigit, val))
        suf = ''.join(filter(lambda c: c in 'bytesmgBMG', suf))
        return val, suf

    def on_focus_changed(self):
        if self.ids.option_value_input.focus:
            self.option_value_recent = self.ids.option_value_input.text
        else:
            _, suf = self.split_value(self.ids.option_value_input.text)
            if suf.lower() not in ['bytes', 'kb', 'mb', 'gb', ]:
                self.ids.option_value_input.text = self.option_value_recent
            if self.ids.option_value_input.text != self.option_value_recent:
                self.on_option_value_input_updated()
            self.option_value_recent = None


class SingleChoiceElement(OptionElement, VerticalLayout):

    option_possible_values = ListProperty([])

    def __init__(self, **kwargs):
        self.option_possible_values = kwargs.pop('option_possible_values', [])
        super(SingleChoiceElement, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        if self.option_readonly:
            self.ids.option_value_input.read_only = True

    def on_focus_changed(self):
        if self.ids.option_value_input.focus:
            self.option_value_recent = self.ids.option_value_input.text
        else:
            if self.ids.option_value_input.text not in self.option_possible_values:
                self.ids.option_value_input.text = self.option_value_recent
            if self.ids.option_value_input.text != self.option_value_recent:
                self.on_option_value_input_updated()
            self.option_value_recent = None


class TextElement(OptionElement, VerticalLayout):

    def __init__(self, **kwargs):
        super(TextElement, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        if self.option_readonly:
            self.ids.option_value_input.read_only = True

    def on_focus_changed(self):
        if self.ids.option_value_input.focus:
            self.option_value_recent = self.ids.option_value_input.text
        else:
            if self.ids.option_value_input.text != self.option_value_recent:
                self.on_option_value_input_updated()
            self.option_value_recent = None

#------------------------------------------------------------------------------

class SettingsStatusMessage(NormalLabel):
    pass


class SettingsTreeView(TreeView):

    def on_node_expand(self, node):
        if _Debug:
            print('on_node_expand', node.item_key, node.item_data)
        self.parent.parent.parent.populate_node(node)

    def on_node_collapse(self, node):
        if _Debug:
            print('on_node_collapse', node.item_key, node.item_data)

#------------------------------------------------------------------------------

class SettingsScreen(AppScreen):

    recent_tree_index = {}

    def get_icon(self):
        return 'cogs'

    def get_title(self):
        return "settings"

    def populate(self):
        api_client.services_list(cb=self.on_services_list_result)

    def populate_node(self, node):
        api_client.config_get(
            key=node.item_key,
            include_info=True,
            cb=lambda resp: self.on_config_get_result(resp, node.item_key, node),
        )

    def build_description(self, src):
        src = re.sub(r'\*\*(.+?)\*\*', r'[b]\g<1>[/b]', src)  # bold
        src = re.sub(r'\`(.+?)\`', r'[size=10sp][font=RobotoMono-Regular]\g<1>[/font][/size]', src)  # monospace
        return src

    def build_item(self, item_key, item_data, known_tree):
        tv = self.ids.settings_tree
        parent = tv.get_root()
        item_path = item_key.split('/')
        built_count = 0
        for sub_path_pos in range(len(item_path)):
            sub_path = item_path[sub_path_pos]
            abs_path = '/'.join(item_path[:sub_path_pos + 1])
            cur_item_data = {} if abs_path != item_key else item_data
            if abs_path not in known_tree:
                if abs_path.startswith('services/') and abs_path.count('/') == 1:
                    svc_name = 'service_'+sub_path.replace('-', '_')
                    sub_element = ServiceElement(
                        id=svc_name,
                        item_key=abs_path,
                        item_data=cur_item_data,
                        is_open=False,
                        is_leaf=False,
                        service_name=sub_path,
                        service_state=self.services_list_result.get(svc_name, {'state': 'OFF'})['state'],
                        item_clicked_callback=self.on_item_clicked,
                    )
                else:
                    if 'type' in cur_item_data:
                        if cur_item_data['type'] == 'boolean':
                            sub_element = BooleanElement(
                                item_key=abs_path,
                                item_data=cur_item_data,
                                is_open=False,
                                is_leaf=True,
                                option_name=cur_item_data.get('label', '') or sub_path,
                                option_value=str(bool(cur_item_data.get('value') or False)).lower().replace('false', ''),
                                option_value_default=cur_item_data.get('default'),
                                option_description=self.build_description(cur_item_data.get('info') or ''),
                                option_readonly=cur_item_data.get('readonly', False),
                                value_modified_callback=self.on_option_value_modified,
                                item_clicked_callback=self.on_item_clicked,
                            )
                        elif cur_item_data['type'] in ['selection', ]:
                            sub_element = SingleChoiceElement(
                                item_key=abs_path,
                                item_data=cur_item_data,
                                is_open=False,
                                is_leaf=True,
                                option_name=cur_item_data.get('label', '') or sub_path,
                                option_value='{}'.format(cur_item_data.get('value') or ''),
                                option_value_default=cur_item_data.get('default'),
                                option_possible_values=cur_item_data.get('possible_values', []) or [],
                                option_description=self.build_description(cur_item_data.get('info') or ''),
                                option_readonly=cur_item_data.get('readonly', False),
                                value_modified_callback=self.on_option_value_modified,
                                item_clicked_callback=self.on_item_clicked,
                            )
                        elif cur_item_data['type'] in ['disk space', ]:
                            sub_element = DiskSpaceElement(
                                item_key=abs_path,
                                item_data=cur_item_data,
                                is_open=False,
                                is_leaf=True,
                                option_name=cur_item_data.get('label', '') or sub_path,
                                option_value='{}'.format(cur_item_data.get('value') or 0),
                                option_value_default=cur_item_data.get('default'),
                                option_description=self.build_description(cur_item_data.get('info') or ''),
                                option_readonly=cur_item_data.get('readonly', False),
                                value_modified_callback=self.on_option_value_modified,
                                item_clicked_callback=self.on_item_clicked,
                            )
                        elif cur_item_data['type'] in ['positive integer', 'integer', 'non zero positive integer', 'port number', ]:
                            sub_element = IntegerElement(
                                item_key=abs_path,
                                item_data=cur_item_data,
                                is_open=False,
                                is_leaf=True,
                                option_name=cur_item_data.get('label', '') or sub_path,
                                option_value='{}'.format(cur_item_data.get('value') or 0),
                                option_value_default=cur_item_data.get('default'),
                                option_description=self.build_description(cur_item_data.get('info') or ''),
                                option_value_min=cur_item_data.get('min'),
                                option_value_max=cur_item_data.get('max'),
                                option_readonly=cur_item_data.get('readonly', False),
                                value_modified_callback=self.on_option_value_modified,
                                item_clicked_callback=self.on_item_clicked,
                            )
                        else:
                            sub_element = TextElement(
                                item_key=abs_path,
                                item_data=cur_item_data,
                                is_open=False,
                                is_leaf=True,
                                option_name=cur_item_data.get('label', '') or sub_path,
                                option_value='{}'.format(cur_item_data.get('value') or ''),
                                option_value_default=cur_item_data.get('default'),
                                option_description=self.build_description(cur_item_data.get('info') or ''),
                                option_readonly=cur_item_data.get('readonly', False),
                                value_modified_callback=self.on_option_value_modified,
                                item_clicked_callback=self.on_item_clicked,
                            )
                    else:
                        sub_element = ParentElement(
                            item_key=abs_path,
                            item_data=cur_item_data,
                            is_open=False,
                            text=cur_item_data.get('label', '') or sub_path,
                            item_clicked_callback=self.on_item_clicked,
                        )
                active_tree_node = tv.add_node(
                    node=sub_element,
                    parent=parent,
                )
                built_count += 1
                known_tree[abs_path] = active_tree_node
            else:
                active_tree_node = known_tree[abs_path]
            parent = active_tree_node
        return built_count

    def build_tree(self, items_list, active_node=None):
        tv = self.ids.settings_tree
        d = {}  # input elements by option key
        a = {}  # absolute path of each tree element
        t = {}  # known tree elements
        o = []  # maintain order of the items
        s = []  # also store order for sub elements
        for item in items_list:
            item_key = item['key']
            if item_key.startswith('interface/'):
                continue
            if item_key.startswith('personal/'):
                continue
            if item_key.startswith('paths/'):
                continue
            if item_key.startswith('services/network/proxy'):
                continue
            if item_key.startswith('services/blockchain/explorer') or item_key.startswith('services/blockchain/wallet') or item_key.startswith('services/blockchain/miner'):
                continue
            if 'value' in item and not item.get('info'):
                continue
            d[item_key] = item
            o.append(item_key)
        if _Debug:
            print('building items:', len(d))
        count_options = 0
        for item_key in o:
            item = d[item_key]
            item_path = item_key.split('/')
            for sub_path_pos in range(len(item_path)):
                abs_path = '/'.join(item_path[:sub_path_pos + 1])
                if abs_path not in a:
                    a[abs_path] = {}
                    s.append(abs_path)
                if abs_path == item_key:
                    a[abs_path] = item.copy()
                    count_options += 1
        opened = set()
        for node in list(tv.iterate_all_nodes()):
            node_item_key = getattr(node, 'item_key', None)
            if node_item_key:
                if node_item_key not in t:
                    t[node.item_key] = node
                if node.is_open:
                    opened.add(node.item_key)
        if _Debug:
            print('known nodes:', len(t), count_options)
        count_built = 0
        if t:
            for abs_path in s:
                parent_path = '/'.join(abs_path.split('/')[:-1])
                if abs_path in t:
                    continue
                if parent_path == abs_path:
                    continue
                if parent_path not in opened:
                    continue
                item = a[abs_path]
                count_built += self.build_item(item_key=abs_path, item_data=item, known_tree=t)
        else:
            for abs_path in ['services', 'logs', ]:
                sub_element = ParentElement(
                    item_key=abs_path,
                    item_data={},
                    is_open=False,
                    is_leaf=False,
                    text=abs_path,
                    item_clicked_callback=self.on_item_clicked,
                )
                active_tree_node = tv.add_node(
                    node=sub_element,
                    parent=tv.get_root(),
                )
                count_built += 1
                t[abs_path] = active_tree_node
        if _Debug:
            print('created elements:', count_built)
        d.clear()
        a.clear()
        t.clear()
        o.clear()
        if active_node:
            if _Debug:
                print('active node:', active_node.item_key, active_node)
            Clock.schedule_once(lambda *dt: self.ids.scroll_view.scroll_to(active_node, padding=dp(5), animate=False), -1)
        self.recent_tree_index.clear()
        for node in list(tv.iterate_all_nodes()):
            node_item_key = getattr(node, 'item_key', None)
            if node_item_key:
                if node_item_key not in t:
                    self.recent_tree_index[node.item_key] = node
        if _Debug:
            print('indexed %d elements' % len(self.recent_tree_index))

    def on_enter(self, *args):
        self.populate()

    def on_service_started_stopped(self, event_id, service_name):
        element_name = 'services/{}'.format(service_name[8:].replace('_', '-'))
        node = self.recent_tree_index.get(element_name, None)
        if not node:
            if _Debug:
                print('element %r not found' % element_name)
            return
        current_state = node.service_state
        node.service_state = 'ON' if event_id == 'service-started' else 'OFF'
        if _Debug:
            print('on_service_started_stopped', event_id, service_name, element_name, current_state, node.service_state)

    def on_services_list_result(self, resp):
        if not websock.is_ok(resp):
            self.ids.status_message_label.text = str(websock.response_errors(resp))
            return
        self.ids.status_message_label.text = ''
        self.services_list_result = {}
        for svc in websock.response_result(resp):
            self.services_list_result[svc['name']] = svc
        api_client.configs_list(sort=True, include_info=False, cb=self.on_configs_list_result)

    def on_configs_list_result(self, resp):
        if not websock.is_ok(resp):
            self.ids.status_message_label.text = str(websock.response_errors(resp))
            return
        self.ids.status_message_label.text = ''
        items_list = websock.response_result(resp)
        if _Debug:
            print('on_configs_list_result', len(items_list))
        self.build_tree(items_list)

    def on_item_clicked(self, option_key, node):
        if _Debug:
            print('on_item_clicked', option_key, node)
        self.ids.settings_tree.toggle_node(node)

    def on_config_get_result(self, resp, option_key, node):
        if not websock.is_ok(resp):
            self.ids.status_message_label.text = str(websock.response_errors(resp))
            return
        self.ids.status_message_label.text = ''
        items_list = websock.response_result(resp)
        if _Debug:
            print('on_config_get_result', list(items_list))
        self.build_tree(items_list, active_node=node)

    def on_option_value_modified(self, option_key, new_value):
        if _Debug:
            print('on_option_value_modified', option_key, new_value)
        api_client.config_set(key=option_key, value=new_value)

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_settings.kv')
