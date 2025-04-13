from pyobjus import autoclass, objc_str, protocol  # @UnresolvedImport


_Debug = False


class IOSFileChooser(object):

    def __init__(self, *args, **kwargs):
        self._on_selection = kwargs["on_selection"]

    def run(self):
        if _Debug:
            print('IOSFileChooser.run')
        UIDocumentPickerViewController = autoclass('UIDocumentPickerViewController')
        file_types = [objc_str("public.item")]
        picker = UIDocumentPickerViewController.alloc().initWithDocumentTypes_inMode_(file_types, 0)
        picker.setAllowsMultipleSelection_(False)
        picker.setDelegate_(self)
        UIApplication = autoclass("UIApplication")
        app = UIApplication.sharedApplication()
        window = app.keyWindow
        root_view_controller = window.rootViewController()
        root_view_controller.presentViewController_animated_completion_(picker, True, None)

    @protocol('UIDocumentPickerDelegate')
    def documentPicker_didPickDocumentsAtURLs_(self, picker, urls):
        url = urls.objectAtIndex_(0)
        file_path = url.path.UTF8String()
        if _Debug:
            print('IOSFileChooser.documentPicker_didPickDocumentsAtURLs_', file_path)
        self._on_selection([file_path, ])

    @protocol('UIDocumentPickerDelegate')
    def documentPickerWasCancelled_(self, picker):
        if _Debug:
            print('IOSFileChooser.documentPickerWasCancelled_', picker)
