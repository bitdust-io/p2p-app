import time

#------------------------------------------------------------------------------

from lib import websock

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

def run(method, kwargs={}, cb=None, ):
    if _Debug:
        print('api_client.run %r %r' % (method, time.asctime(), ))
    jd = {'command': 'api_call', 'method': method, 'kwargs': kwargs, }
    return websock.ws_call(json_data=jd, cb=cb)

#------------------------------------------------------------------------------

def process_health(cb=None):
    return run('process_health', cb=cb)


def process_stop(cb=None):
    return run('process_stop', cb=cb)


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


def services_list(with_configs=False, cb=None):
    return run('services_list', kwargs={'with_configs': with_configs, }, cb=cb)


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


def group_join(group_key_id, publish_events=False, cb=None):
    return run('group_join', kwargs={'group_key_id': group_key_id, 'publish_events': publish_events, }, cb=cb)


def group_leave(group_key_id, erase_key=False, cb=None):
    return run('group_leave', kwargs={'group_key_id': group_key_id, 'erase_key': erase_key, }, cb=cb)


def group_share(group_key_id, trusted_user_id, publish_events=False, cb=None):
    return run('group_share', kwargs={'group_key_id': group_key_id, 'trusted_user_id': trusted_user_id, 'publish_events': publish_events, }, cb=cb)


def automat_events_start(index, cb=None):
    return run('automat_events_start', kwargs={'index': index, }, cb=cb)


def automat_events_stop(index, cb=None):
    return run('automat_events_stop', kwargs={'index': index, }, cb=cb)
