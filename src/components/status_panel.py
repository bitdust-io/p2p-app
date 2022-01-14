from kivy.properties import DictProperty  # @UnresolvedImport

from kivymd.uix.card import MDCard
 
#------------------------------------------------------------------------------

from lib import api_client

from components import screen

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class AutomatPanel(object):

    statuses = DictProperty({})
    callback_automat_state_changed = None

    def update_fields(self, **kwargs):
        raise NotImplementedError()

    def start_automat_events(self, index=None, automat_id=None):
        return api_client.automat_events_start(
            index=None if index is None else int(index),
            automat_id=automat_id,
            cb=self.on_automat_events_start_result,
        )

    def stop_automat_events(self, index=None, automat_id=None):
        return api_client.automat_events_stop(
            index=None if index is None else int(index),
            automat_id=automat_id,
        )

    def on_automat_events_start_result(self, resp):
        if _Debug:
            print('AutomatPanel.on_automat_events_start_result', api_client.is_ok(resp))
        if not api_client.is_ok(resp):
            self.update_fields(error=self.statuses.get(None, api_client.red_err(resp)))
            return
        self.update_fields(response=resp)

    def on_automat_state_changed(self, event_data):
        if _Debug:
            print('AutomatPanel.on_automat_state_changed', event_data)
        self.update_fields(state=event_data['newstate'])
        if self.callback_automat_state_changed:
            self.callback_automat_state_changed(event_data)


class AutomatPanelByIndex(AutomatPanel):

    automat_index = None

    def attach(self, automat_index, callback_automat_state_changed=None):
        if self.automat_index is not None:
            if _Debug:
                print('AutomatPanelByIndex.attach SKIP, already attached with automat_index=%r' % self.automat_index)
            return None
        if _Debug:
            print('AutomatPanelByIndex.attach with automat_index:', automat_index)
        self.automat_index = automat_index
        if self.automat_index is None:
            self.update_fields(state=None)
            return None
        self.automat_index = int(self.automat_index)
        self.callback_automat_state_changed = callback_automat_state_changed
        screen.control().add_state_changed_callback(self.automat_index, self.on_automat_state_changed)
        ret = self.start_automat_events(index=int(self.automat_index))
        if not ret:
            self.automat_index = None
            self.update_fields(state=None)
        return ret

    def release(self):
        if self.automat_index is None:
            if _Debug:
                print('AutomatPanelByIndex.release SKIP, already released')
            return None
        if _Debug:
            print('AutomatPanelByIndex.release automat_index was:', self.automat_index)
        _i = self.automat_index
        self.automat_index = None
        self.callback_automat_state_changed = None
        if _i is None:
            self.update_fields(error='unexpected error, automat index was not set')
            return None
        screen.control().remove_state_changed_callback(_i, self.on_automat_state_changed)
        ret = self.stop_automat_events(index=_i)
        self.update_fields(state=None)
        return ret

    def on_automat_state_changed(self, event_data):
        if _Debug:
            print('AutomatPanelByIndex.on_automat_state_changed')
        super().on_automat_state_changed(event_data)
        if event_data['newstate'] in ['CLOSED', ]:
            if _Debug:
                print('AutomatPanelByIndex.on_automat_state_changed   will call release() now, newstate=%r' % event_data['newstate'])
            self.release()


class AutomatPanelByID(AutomatPanel):

    automat_id = None

    def attach(self, automat_id, callback_automat_state_changed=None):
        if self.automat_id is not None:
            if _Debug:
                print('AutomatPanelByID.attach SKIP, already attached with automat_id=%r' % self.automat_id)
            return None
        if _Debug:
            print('AutomatPanelByID.attach with automat_id:', automat_id)
        self.automat_id = automat_id
        if self.automat_id is None:
            self.update_fields(state=None)
            return None
        self.callback_automat_state_changed = callback_automat_state_changed
        screen.control().add_state_changed_callback_by_id(self.automat_id, self.on_automat_state_changed)
        ret = self.start_automat_events(automat_id=self.automat_id)
        if not ret:
            self.automat_id = None
            self.update_fields(state=None)
        return ret

    def release(self):
        if self.automat_id is None:
            if _Debug:
                print('AutomatPanelByID.release SKIP, already released')
            return None
        if _Debug:
            print('AutomatPanelByID.release automat_id was:', self.automat_id)
        _id = self.automat_id
        self.automat_id = None
        self.callback_automat_state_changed = None
        if _id is None:
            self.update_fields(error='unexpected error, automat id was not set')
            return None
        screen.control().remove_state_changed_callback_by_id(_id, self.on_automat_state_changed)
        ret = self.stop_automat_events(automat_id=_id)
        self.update_fields(state=None)
        return ret

    def on_automat_state_changed(self, event_data):
        if _Debug:
            print('AutomatPanelByID.on_automat_state_changed')
        super().on_automat_state_changed(event_data)

#------------------------------------------------------------------------------

class AutomatStatusPanel(AutomatPanelByID, MDCard):

    def update_fields(self, **kwargs):
        if _Debug:
            print('AutomatStatusPanel.update_fields', 'response' in kwargs, kwargs.get('state'), kwargs.get('error'), kwargs.get('response'))
        if 'error' in kwargs:
            self.ids.label_name.text = ''
            self.ids.label_state.text = ''
            self.ids.label_status.text = kwargs['error']
            return
        if 'response' in kwargs:
            r = api_client.result(kwargs['response'])
            self.ids.label_name.text = '#{} {}'.format(r['index'], r['id'])
            self.ids.label_state.text = r['state']
            self.ids.label_status.text = self.statuses.get(r['state'], 'status unknown')
            return
        if 'state' in kwargs:
            self.ids.label_state.text = kwargs['state']
            self.ids.label_status.text = self.statuses.get(kwargs['state'], 'current status is unknown')
            return
        self.ids.label_name.text = kwargs.get('name', '')
        self.ids.label_state.text = kwargs.get('state', '')
        self.ids.label_status.text = kwargs.get('status', '')


class AutomatShortStatusPanel(AutomatPanelByID, MDCard):

    def update_fields(self, **kwargs):
        if _Debug:
            print('AutomatShortStatusPanel.update_fields', 'response' in kwargs, kwargs.get('state'), kwargs.get('error'), kwargs.get('response'))
        if 'error' in kwargs:
            self.ids.label_status.text = kwargs['error']
            return
        if 'response' in kwargs:
            r = api_client.result(kwargs['response'])
            self.ids.label_status.text = self.statuses.get(r['state'], 'current status is unknown')
            return
        if 'state' in kwargs:
            self.ids.label_status.text = self.statuses.get(kwargs['state'], 'current status is unknown')
            return
        self.ids.label_status.text = kwargs.get('status', '')


class AutomatShortStatusPanelByIndex(AutomatPanelByIndex, MDCard):

    def update_fields(self, **kwargs):
        if _Debug:
            print('AutomatShortStatusPanelByIndex.update_fields', 'response' in kwargs, kwargs.get('state'), kwargs.get('error'), kwargs.get('response'))
        if 'error' in kwargs:
            self.ids.label_status.text = kwargs['error']
            return
        if 'response' in kwargs:
            r = api_client.result(kwargs['response'])
            self.ids.label_status.text = self.statuses.get(r['state'], 'current status is unknown')
            return
        if 'state' in kwargs:
            self.ids.label_status.text = self.statuses.get(kwargs['state'], 'current status is unknown')
            return
        self.ids.label_status.text = kwargs.get('status', '')
