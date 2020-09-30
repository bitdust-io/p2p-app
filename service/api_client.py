from service import websock

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

def run(method, kwargs={}, cb=None, ):
    if _Debug:
        print('api_client.run %r cb=%r' % (method, cb, ))
    jd = {'command': 'api_call', 'method': method, 'kwargs': kwargs, }
    return websock.ws_call(json_data=jd, cb=cb)

#------------------------------------------------------------------------------

def process_health(cb=None):
    return run('process_health', cb=cb)


def identity_get(cb=None):
    return run('identity_get', cb=cb)


def network_connected(wait_timeout=0, cb=None):
    return run('network_connected', kwargs={'wait_timeout': wait_timeout, }, cb=cb, )


def user_observe(nickname, attempts=5, cb=None):
    return run('user_observe', kwargs={'nickname': nickname, 'attempts': 5, }, cb=cb, )


def friend_add(global_user_id, alias='', cb=None):
    return run('friend_add', kwargs={'trusted_user_id': global_user_id, 'alias': alias, }, cb=cb, )


def friends_list(cb=None):
    return run('friends_list', cb=cb)
