from androidstorage4kivy import SharedStorage, Chooser  # @UnresolvedImport

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

def chooser_callback(cb, uri_list):
    if _Debug:
        print('filechooser.chooser_callback', uri_list)
    result = []
    try:
        ss = SharedStorage()
        for uri in uri_list:
            path = ss.copy_from_shared(uri)
            result.append(path)
            if _Debug:
                print('filechooser.chooser_callback', path)
    except Exception as exc:
        if _Debug:
            print('filechooser.chooser_callback', exc)
    if cb:
        cb(result)
    return result


def open_file(content="*/*", title="Select a file", preview=True, show_hidden=False, on_selection=None):
    if _Debug:
        print('filechooser.open_file', content, title, on_selection)
    cb = lambda *a, **kw: chooser_callback(on_selection, *a, **kw)
    chooser = Chooser(cb)
    return chooser.choose_content(content)
