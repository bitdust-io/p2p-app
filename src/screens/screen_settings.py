from kivy.uix.treeview import TreeView, TreeViewNode
from kivy.properties import BooleanProperty, StringProperty  # @UnresolvedImport

#------------------------------------------------------------------------------

from components.screen import AppScreen
from components.labels import NormalLabel
from components.layouts import HorizontalLayout, VerticalLayout

from lib import api_client
from lib import websock

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class SettingsStatusMessage(NormalLabel):
    pass


class SettingsTreeElement(TreeViewNode):

    item_key = None
    item_data = None

    def __init__(self, **kwargs):
        self.item_key = kwargs.pop('item_key')
        self.item_data = kwargs.pop('item_data')
        super(SettingsTreeElement, self).__init__(**kwargs)
        self.no_selection = True
        self.even_color = (1, 1, 1, 1)
        self.odd_color = (1, 1, 1, 1)
        if _Debug:
            print('created element %r : %r' % (self.item_key, id(self), ))

    def __del__(self, **kwargs):
        if _Debug:
            print('erased element %r : %r' % (self.item_key, id(self), ))


class SettingsTreeSubElement(SettingsTreeElement, NormalLabel):
    pass


class SettingsTreeOptionElement(SettingsTreeElement):

    option_name = StringProperty('')
    option_value = BooleanProperty(None, allownone=True)
    option_description = StringProperty('')

    def __init__(self, **kwargs):
        self.option_name = kwargs.pop('option_name')
        self.option_value = kwargs.pop('option_value')
        self.option_description = kwargs.pop('option_description', '')
        self.value_modified_callback = kwargs.pop('value_modified_callback', None)
        kwargs['size_hint'] = (1, None)
        kwargs['padding'] = 0
        kwargs['spacing'] = 0
        super(SettingsTreeOptionElement, self).__init__(**kwargs)


class SettingsTreeBooleanElement(SettingsTreeOptionElement, VerticalLayout):

    def __init__(self, **kwargs):
        super(SettingsTreeBooleanElement, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))


class SettingsTreeIntegerElement(SettingsTreeOptionElement, VerticalLayout):

    def __init__(self, **kwargs):
        super(SettingsTreeIntegerElement, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))


class SettingsTreeTextElement(SettingsTreeOptionElement, VerticalLayout):

    def __init__(self, **kwargs):
        super(SettingsTreeTextElement, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))


class SettingsTreeServiceElement(SettingsTreeElement, HorizontalLayout):

    service_name = StringProperty('')
    service_state = StringProperty('')

    def __init__(self, **kwargs):
        self.service_name = kwargs.pop('service_name')
        self.service_state = kwargs.pop('service_state')
        super(SettingsTreeServiceElement, self).__init__(**kwargs)


class SettingsTreeView(TreeView):

    def on_node_expand(self, node):
        if _Debug:
            print('on_node_expand', node.item_key, node.item_data)
        self.parent.parent.parent.populate()

    def on_node_collapse(self, node):
        if _Debug:
            print('on_node_collapse', node.item_key, node.item_data)


class SettingsScreen(AppScreen):

    def on_enter(self, *args):
        self.populate()

    def populate(self):
        api_client.services_list(cb=self.on_services_list_result)

    def build_item(self, item_key, item_data, known_tree):
        tv = self.ids.settings_tree
        parent = tv.get_root()
        item_path = item_key.split('/')
        for sub_path_pos in range(len(item_path)):
            sub_path = item_path[sub_path_pos]
            abs_path = '/'.join(item_path[:sub_path_pos + 1])
            cur_item_data = {} if abs_path != item_key else item_data
            if abs_path not in known_tree:
                if abs_path.startswith('services/') and abs_path.count('/') == 1:
                    sub_element = SettingsTreeServiceElement(
                        item_key=abs_path,
                        item_data=cur_item_data,
                        is_open=False,
                        is_leaf=False,
                        service_name=sub_path,
                        service_state=self.services_list_result['service_'+sub_path.replace('-', '_')]['state'],
                    )
                else:
                    if 'type' in cur_item_data:
                        if cur_item_data['type'] == 'boolean':
                            sub_element = SettingsTreeBooleanElement(
                                item_key=abs_path,
                                item_data=cur_item_data,
                                is_open=False,
                                is_leaf=True,
                                option_name=cur_item_data.get('label', '') or sub_path,
                                option_value=cur_item_data.get('value') or False,
                                option_description=cur_item_data.get('info') or '',
                                value_modified_callback=self.on_option_value_modified,
                            )
                        elif cur_item_data['type'] in ['positive integer', 'integer', 'non zero positive integer', 'port number', ]:
                            sub_element = SettingsTreeIntegerElement(
                                item_key=abs_path,
                                item_data=cur_item_data,
                                is_open=False,
                                is_leaf=True,
                                option_name=cur_item_data.get('label', '') or sub_path,
                                option_value='{}'.format(cur_item_data.get('value') or 0),
                                option_description=cur_item_data.get('info') or '',
                                value_modified_callback=self.on_option_value_modified,
                            )
                        else:
                            sub_element = SettingsTreeTextElement(
                                item_key=abs_path,
                                item_data=cur_item_data,
                                is_open=False,
                                is_leaf=True,
                                option_name=cur_item_data.get('label', '') or sub_path,
                                option_value='{}'.format(cur_item_data.get('value') or ''),
                                option_description=cur_item_data.get('info') or '',
                                value_modified_callback=self.on_option_value_modified,
                            )
                    else:
                        sub_element = SettingsTreeSubElement(
                            item_key=abs_path,
                            item_data=cur_item_data,
                            is_open=False,
                            text=cur_item_data.get('label', '') or sub_path,
                        )
                active_tree_node = tv.add_node(
                    node=sub_element,
                    parent=parent,
                )
                known_tree[abs_path] = active_tree_node
            else:
                active_tree_node = known_tree[abs_path]
            parent = active_tree_node
        return parent

    def on_services_list_result(self, resp):
        if not websock.is_ok(resp):
            self.ids.status_message_label.text = str(websock.response_errors(resp))
            return
        self.services_list_result = {}
        for svc in websock.response_result(resp):
            self.services_list_result[svc['name']] = svc
        api_client.configs_list(sort=False, cb=self.on_configs_list_result)

    def on_configs_list_result(self, resp):
        if not websock.is_ok(resp):
            self.ids.status_message_label.text = str(websock.response_errors(resp))
            return

        d = {}  # data
        a = {}  # absolute path
        t = {}  # tree
        for item in websock.response_result(resp):
            item_key = item['key']
            if item_key.startswith('interface/'):
                continue
            if item_key.startswith('personal/'):
                continue
            if item_key.startswith('paths/'):
                continue
            d[item_key] = item

        if _Debug:
            print('received items:', len(d))

        count_items = 0
        for item_key, item in d.items():
            item_path = item_key.split('/')
            for sub_path_pos in range(len(item_path)):
                abs_path = '/'.join(item_path[:sub_path_pos + 1])
                if abs_path not in a:
                    a[abs_path] = {}
                if abs_path == item_key:
                    a[abs_path] = item.copy()
                    count_items += 1

        tv = self.ids.settings_tree
        opened = set()
        for node in list(tv.iterate_all_nodes()):
            node_item_key = getattr(node, 'item_key', None)
            if node_item_key:
                if node_item_key not in t:
                    t[node.item_key] = node
                if node.is_open:
                    opened.add(node.item_key)

        if _Debug:
            print('current nodes:', len(t), count_items)

        if not t:
            for abs_path in ['services', 'logs', ]:
                if abs_path in t:
                    continue
                sub_element = SettingsTreeSubElement(
                    item_key=abs_path,
                    item_data={},
                    is_open=False,
                    is_leaf=False,
                    text=abs_path,
                )
                active_tree_node = tv.add_node(
                    node=sub_element,
                    parent=tv.get_root(),
                )
                t[abs_path] = active_tree_node
            return

        count_built = 1
        for abs_path in sorted(a.keys()):
            parent_path = '/'.join(abs_path.split('/')[:-1])
            if abs_path in t:
                continue
            if parent_path == abs_path:
                continue
            if parent_path not in opened:
                continue
            item = a[abs_path]
            self.build_item(item_key=abs_path, item_data=item, known_tree=t)
            count_built += 1

    def on_option_value_modified(self, option_key, new_value):
        if _Debug:
            print('on_option_value_modified', option_key, new_value)
        api_client.config_set(key=option_key, value=new_value)

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_settings.kv')
