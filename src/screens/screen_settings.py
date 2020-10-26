from kivy.clock import Clock
from kivy.uix.treeview import TreeView, TreeViewNode
from kivy.properties import BooleanProperty, StringProperty  # @UnresolvedImport

#------------------------------------------------------------------------------

from components.screen import AppScreen
from components.labels import NormalLabel
from components.buttons import NormalButton
from components.layouts import HorizontalLayout, VerticalLayout

from lib import api_client
from lib import websock

#------------------------------------------------------------------------------

_Debug = True

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


class ParentElement(TreeElement, NormalButton):

    def __init__(self, **kwargs):
        self.item_clicked_callback = kwargs.pop('item_clicked_callback', None)
        super(ParentElement, self).__init__(**kwargs)


class ServiceElement(TreeElement, HorizontalLayout):

    service_name = StringProperty('')
    service_state = StringProperty('')

    def __init__(self, **kwargs):
        self.service_name = kwargs.pop('service_name')
        self.service_state = kwargs.pop('service_state')
        self.item_clicked_callback = kwargs.pop('item_clicked_callback', None)
        super(ServiceElement, self).__init__(**kwargs)


class OptionElement(TreeElement):

    option_name = StringProperty('')
    option_value = BooleanProperty(None, allownone=True)
    option_description = StringProperty('')

    def __init__(self, **kwargs):
        self.option_name = kwargs.pop('option_name')
        self.option_value = kwargs.pop('option_value')
        self.option_description = kwargs.pop('option_description', '')
        self.value_modified_callback = kwargs.pop('value_modified_callback', None)
        self.item_clicked_callback = kwargs.pop('item_clicked_callback', None)
        kwargs['size_hint'] = (1, None)
        kwargs['padding'] = 0
        kwargs['spacing'] = 0
        super(OptionElement, self).__init__(**kwargs)


class BooleanElement(OptionElement, VerticalLayout):

    def __init__(self, **kwargs):
        super(BooleanElement, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))


class IntegerElement(OptionElement, VerticalLayout):

    def __init__(self, **kwargs):
        super(IntegerElement, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))


class TextElement(OptionElement, VerticalLayout):

    def __init__(self, **kwargs):
        super(TextElement, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))

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

    def on_enter(self, *args):
        self.populate()

    def populate(self):
        api_client.services_list(cb=self.on_services_list_result)

    def populate_node(self, node):
        api_client.config_get(
            key=node.item_key,
            cb=lambda resp: self.on_config_get_result(resp, node.item_key, node),
        )

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
                    sub_element = ServiceElement(
                        item_key=abs_path,
                        item_data=cur_item_data,
                        is_open=False,
                        is_leaf=False,
                        service_name=sub_path,
                        service_state=self.services_list_result.get('service_'+sub_path.replace('-', '_'), {'state': 'OFF'})['state'],
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
                                option_value=cur_item_data.get('value') or False,
                                option_description=cur_item_data.get('info') or '',
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
                                option_description=cur_item_data.get('info') or '',
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
                                option_description=cur_item_data.get('info') or '',
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
        for item in items_list:
            item_key = item['key']
            if item_key.startswith('interface/'):
                continue
            if item_key.startswith('personal/'):
                continue
            if item_key.startswith('paths/'):
                continue
            d[item_key] = item
        if _Debug:
            print('building items:', len(d))
        count_options = 0
        for item_key, item in d.items():
            item_path = item_key.split('/')
            for sub_path_pos in range(len(item_path)):
                abs_path = '/'.join(item_path[:sub_path_pos + 1])
                if abs_path not in a:
                    a[abs_path] = {}
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
        if not t:
            for abs_path in ['services', 'logs', ]:
                if abs_path in t:
                    continue
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
                t[abs_path] = active_tree_node
            return
        count_built = 0
        for abs_path in sorted(a.keys()):
            parent_path = '/'.join(abs_path.split('/')[:-1])
            if abs_path in t:
                continue
            if parent_path == abs_path:
                continue
            if parent_path not in opened:
                continue
            item = a[abs_path]
            count_built += self.build_item(item_key=abs_path, item_data=item, known_tree=t)
        if _Debug:
            print('created elements:', count_built)
        if active_node:
            if _Debug:
                print('active node:', active_node.item_key, active_node)
            Clock.schedule_once(lambda *dt: self.ids.scroll_view.scroll_to(active_node, padding=10), -1)

    def on_services_list_result(self, resp):
        if not websock.is_ok(resp):
            self.ids.status_message_label.text = str(websock.response_errors(resp))
            return
        self.ids.status_message_label.text = ''
        self.services_list_result = {}
        for svc in websock.response_result(resp):
            self.services_list_result[svc['name']] = svc
        api_client.configs_list(sort=False, cb=self.on_configs_list_result)

    def on_configs_list_result(self, resp):
        if not websock.is_ok(resp):
            self.ids.status_message_label.text = str(websock.response_errors(resp))
            return
        self.ids.status_message_label.text = ''
        items_list = websock.response_result(resp)
        if _Debug:
            print('on_configs_list_result', items_list)
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
            print('on_config_get_result', items_list)
        self.build_tree(items_list, active_node=node)

    def on_option_value_modified(self, option_key, new_value):
        if _Debug:
            print('on_option_value_modified', option_key, new_value)
        api_client.config_set(key=option_key, value=new_value)

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_settings.kv')
