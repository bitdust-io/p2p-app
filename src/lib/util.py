

def UrlParseFast(url):
    """
    Return a 5-items tuple from url address :
        ( proto, host, port, path, filename )
    """
    proto, _, tail = url.partition('://')
    head, _, filename = tail.rpartition('/')
    host_port, _, path = head.partition('/')
    host, _, port = host_port.partition(':')
    return proto, host, port, path, filename


def IDUrlToGlobalID(idurl):
    if not idurl:
        return idurl
    _, host, port, _, filename = UrlParseFast(idurl)
    if filename.count('.'):
        username = filename.split('.')[0]
    else:
        username = filename
    if port:
        host = '%s_%s' % (host, port)
    return '%s@%s' % (username, host)
