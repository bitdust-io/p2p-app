"""
All of the available BitDust engine API methods can be found here:
https://github.com/bitdust-io/public/blob/master/bitdust/interface/api.py

"""

import time

#------------------------------------------------------------------------------

from lib import web_sock

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

def run(method, kwargs={}, cb=None):
    if _Debug:
        print('api_client.run %r %r' % (method, time.asctime(), ))
    jd = {'command': 'api_call', 'method': method, 'kwargs': kwargs, }
    return web_sock.ws_call(json_data=jd, cb=cb)

#------------------------------------------------------------------------------

def is_ok(response):
    if not isinstance(response, dict):
        return False
    return response_status(response) == 'OK'


def is_exception(response, exc_message=None):
    if not isinstance(response, Exception):
        return False
    if not exc_message:
        return True
    return response.args[0] == exc_message


def response_payload(response):
    return response.get('payload', {})


def response_errors(response):
    if not isinstance(response, dict):
        return ['no response', ]
    return response_payload(response).get('response', {}).get('errors', [])


def response_err(response):
    return ', '.join(response_errors(response))


def response_status(response):
    if not isinstance(response, dict):
        return ''
    return response_payload(response).get('response', {}).get('status', '')


def response_message(response):
    if not isinstance(response, dict):
        return ''
    return response_payload(response).get('response', {}).get('message', '')


def response_result(response):
    if not isinstance(response, dict):
        return None
    return response_payload(response).get('response', {}).get('result', [])

#------------------------------------------------------------------------------

def status(response):
    return response_status(response)


def message(response):
    return response_message(response)


def result(response):
    return response_result(response) or {}


def red_err(response):
    return '[color=#f00]{}[/color]'.format(response_err(response))


#------------------------------------------------------------------------------
#--- API streaming

def add_model_listener(model_name, listener_cb):
    if listener_cb in (web_sock.model_update_callbacks().get(model_name) or []):
        return False
    if model_name not in web_sock.model_update_callbacks():
        web_sock.model_update_callbacks()[model_name] = []
    web_sock.model_update_callbacks()[model_name].append(listener_cb)
    return True


def remove_model_listener(model_name, listener_cb):
    if model_name not in web_sock.model_update_callbacks():
        return False
    if listener_cb not in web_sock.model_update_callbacks()[model_name]:
        return False
    web_sock.model_update_callbacks()[model_name].remove(listener_cb)
    if not web_sock.model_update_callbacks()[model_name]:
        web_sock.model_update_callbacks().pop(model_name)
    return True


def start_model_streaming(model_name, request_all=False):
    return run('enable_model_listener', kwargs={
        'model_name': model_name,
        'request_all': request_all,
    })


def stop_model_streaming(model_name):
    return run('disable_model_listener', kwargs={'model_name': model_name, })


def request_model_data(model_name, query_details=None):
    return run('request_model_data', kwargs={'model_name': model_name, 'query_details': query_details, })

#------------------------------------------------------------------------------
#--- API methods

def process_health(cb=None):
    return run('process_health', cb=cb)


def process_stop(cb=None):
    return run('process_stop', cb=cb)


def devices_list(sort=False, cb=None):
    return run('devices_list', kwargs={'sort': sort, }, cb=cb)


def device_add(name, routed=False, activate=True, wait_listening=False, web_socket_port=None, key_size=None, cb=None):
    return run('device_add', kwargs={
        'name': name,
        'routed': routed,
        'activate': activate,
        'wait_listening': wait_listening,
        'web_socket_port': web_socket_port,
        'key_size': key_size,
    }, cb=cb)


def device_info(name, cb=None):
    return run('device_info', kwargs={'name': name, }, cb=cb)


def device_client_code_input(name, client_code, cb=None):
    return run('device_client_code_input', kwargs={'name': name, 'client_code': client_code, }, cb=cb)


def identity_get(cb=None):
    return run('identity_get', cb=cb)


def identity_create(username, preferred_servers=[], join_network=False, cb=None):
    return run('identity_create', kwargs={
        'username': username,
        'preferred_servers': preferred_servers,
        'join_network': join_network,
    }, cb=cb)


def identity_recover(private_key_source, known_idurl=None, join_network=False, cb=None):
    return run('identity_recover', kwargs={
        'private_key_source': private_key_source,
        'known_idurl': known_idurl,
        'join_network': join_network,
    }, cb=cb)


def identity_backup(destination_filepath, cb=None):
    return run('identity_backup', kwargs={'destination_filepath': destination_filepath, }, cb=cb)


def network_connected(wait_timeout=0, cb=None):
    return run('network_connected', kwargs={'wait_timeout': wait_timeout, }, cb=cb)


def network_reconnect(cb=None):
    return run('network_reconnect', cb=cb)


def configs_list(sort=True, include_info=False, cb=None):
    return run('configs_list', kwargs={'sort': sort, 'include_info': include_info, }, cb=cb)


def configs_tree(include_info=False, cb=None):
    return run('configs_tree', kwargs={'include_info': include_info, }, cb=cb)


def config_get(key, include_info=False, cb=None):
    return run('config_get', kwargs={'key': key, 'include_info': include_info, }, cb=cb)


def config_set(key, value, cb=None):
    return run('config_set', kwargs={'key': key, 'value': value, }, cb=cb)


def space_donated(cb=None):
    return run('space_donated', cb=cb)


def space_consumed(cb=None):
    return run('space_consumed', cb=cb)


def space_local(cb=None):
    return run('space_local', cb=cb)


def services_list(with_configs=False, cb=None):
    return run('services_list', kwargs={'with_configs': with_configs, }, cb=cb)


def files_list(remote_path=None, key_id=None, recursive=False, all_customers=False, include_uploads=False, include_downloads=False, cb=None):
    return run('files_list', kwargs={
        'remote_path': remote_path,
        'key_id': key_id,
        'recursive': recursive,
        'all_customers': all_customers,
        'include_uploads': include_uploads,
        'include_downloads': include_downloads,
    }, cb=cb)


def files_sync(force=False, cb=None):
    return run('files_sync', kwargs={'force': force}, cb=cb)


def file_info(remote_path, include_uploads=False, include_downloads=False, cb=None):
    return run('file_info', kwargs={
        'remote_path': remote_path,
        'include_uploads': include_uploads,
        'include_downloads': include_downloads,
    }, cb=cb)


def file_create(remote_path, as_folder=False, exist_ok=False, force_path_id=None, cb=None):
    return run('file_create', kwargs={
        'remote_path': remote_path,
        'as_folder': as_folder,
        'exist_ok': exist_ok,
        'force_path_id': force_path_id,
    }, cb=cb)


def file_delete(remote_path, cb=None):
    return run('file_delete', kwargs={'remote_path': remote_path, }, cb=cb)


def file_upload_start(local_path, remote_path, wait_result=False, cb=None):
    return run('file_upload_start', kwargs={
        'local_path': local_path,
        'remote_path': remote_path,
        'wait_result': wait_result,
    }, cb=cb)


def file_download_start(remote_path, destination_path=None, wait_result=False, cb=None):
    return run('file_download_start', kwargs={
        'remote_path': remote_path,
        'destination_path': destination_path,
        'wait_result': wait_result,
    }, cb=cb)


def shares_list(only_active=False, include_mine=True, include_granted=True, cb=None):
    return run('shares_list', kwargs={
        'only_active': only_active,
        'include_mine': include_mine,
        'include_granted': include_granted,
    }, cb=cb)


def share_create(owner_id=None, key_size=None, label='', cb=None):
    return run('share_create', kwargs={'owner_id': owner_id, 'key_size': key_size, 'label': label, }, cb=cb)


def share_delete(key_id, cb=None):
    return run('share_delete', kwargs={'key_id': key_id, }, cb=cb)


def share_open(key_id, publish_events=False, cb=None):
    return run('share_open', kwargs={'key_id': key_id, 'publish_events': publish_events, }, cb=cb)


def share_close(key_id, cb=None):
    return run('share_close', kwargs={'key_id': key_id, }, cb=cb)


def share_grant(key_id, trusted_user_id, cb=None):
    return run('share_grant', kwargs={'key_id': key_id, 'trusted_user_id': trusted_user_id, }, cb=cb)


def share_info(key_id, cb=None):
    return run('share_info', kwargs={'key_id': key_id, }, cb=cb)


def user_observe(nickname, attempts=5, cb=None):
    return run('user_observe', kwargs={'nickname': nickname, 'attempts': attempts, }, cb=cb)


def friends_list(cb=None):
    return run('friends_list', cb=cb)


def friend_add(global_user_id, alias='', cb=None):
    return run('friend_add', kwargs={'trusted_user_id': global_user_id, 'alias': alias, }, cb=cb)


def friend_remove(global_user_id, cb=None):
    return run('friend_remove', kwargs={'user_id': global_user_id, }, cb=cb)


def message_history(recipient_id=None, sender_id=None, message_type=None, offset=0, limit=100, cb=None):
    return run('message_history', kwargs={
        'recipient_id': recipient_id,
        'sender_id': sender_id,
        'message_type': message_type,
        'offset': offset,
        'limit': limit,
    }, cb=cb)


def message_conversations_list(message_types=[], offset=0, limit=100, cb=None):
    return run('message_conversations_list', kwargs={
        'message_types': message_types,
        'offset': offset,
        'limit': limit,
    }, cb=cb)


def message_send(recipient_id, data, ping_timeout=30, message_ack_timeout=15, cb=None):
    return run('message_send', kwargs={
        'recipient_id': recipient_id,
        'data': data,
        'ping_timeout': ping_timeout,
        'message_ack_timeout': message_ack_timeout,
    }, cb=cb)


def message_send_group(group_key_id, data, cb=None):
    return run('message_send_group', kwargs={
        'group_key_id': group_key_id,
        'data': data,
    }, cb=cb)


def group_create(label=None, cb=None):
    return run('group_create', kwargs={'label': label, }, cb=cb)


def group_join(group_key_id, publish_events=False, wait_result=True, cb=None):
    return run('group_join', kwargs={
        'group_key_id': group_key_id,
        'publish_events': publish_events,
        'wait_result': wait_result,
    }, cb=cb)


def group_leave(group_key_id, erase_key=False, cb=None):
    return run('group_leave', kwargs={'group_key_id': group_key_id, 'erase_key': erase_key, }, cb=cb)


def group_info(group_key_id, cb=None):
    return run('group_info', kwargs={'group_key_id': group_key_id, }, cb=cb)


def group_share(group_key_id, trusted_user_id, publish_events=False, cb=None):
    return run('group_share', kwargs={'group_key_id': group_key_id, 'trusted_user_id': trusted_user_id, 'publish_events': publish_events, }, cb=cb)


def group_reconnect(group_key_id, cb=None):
    return run('group_reconnect', kwargs={'group_key_id': group_key_id, }, cb=cb)


def dht_user_random(layer_id=0, count=1, cb=None):
    return run('dht_user_random', kwargs={'layer_id': layer_id, 'count': count, }, cb=cb)


def automat_events_start(index=None, automat_id=None, cb=None):
    return run('automat_events_start', kwargs={'index': index, 'automat_id': automat_id, }, cb=cb)


def automat_events_stop(index=None, automat_id=None, cb=None):
    return run('automat_events_stop', kwargs={'index': index, 'automat_id': automat_id, }, cb=cb)
