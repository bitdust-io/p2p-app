from pyobjus import autoclass, objc_str, protocol  # @UnresolvedImport
from plyer.facades import FileChooser
from pyobjus.dylib_manager import load_framework  # @UnresolvedImport

load_framework('/System/Library/Frameworks/Photos.framework')


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


class IOSImageChooser(FileChooser):

    def __init__(self, *args, **kwargs):
        self._on_selection = kwargs["on_selection"]

    def run(self):
        if _Debug:
            print('IOSImageChooser.run')
        picker = self._get_picker()
        UIApplication = autoclass('UIApplication')
        vc = UIApplication.sharedApplication().keyWindow.rootViewController()
        vc.presentViewController_animated_completion_(picker, True, None)

    def _get_picker(self):
        picker = autoclass("UIImagePickerController")
        po = picker.alloc().init()
        po.sourceType = 0
        po.delegate = self
        return po

    @protocol('UIImagePickerControllerDelegate')
    def imagePickerController_didFinishPickingMediaWithInfo_(self, image_picker, frozen_dict):
        image_picker.dismissViewControllerAnimated_completion_(True, None)
        native_image_picker = autoclass("NativeImagePicker").alloc().init()
        path = native_image_picker.writeToPNG_(frozen_dict)
        file_path = path.UTF8String()
        if _Debug:
            print('IOSImageChooser.imagePickerController_didFinishPickingMediaWithInfo_', file_path)
        self._on_selection([file_path, ])
