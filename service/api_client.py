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

