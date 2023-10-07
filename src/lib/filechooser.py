import traceback
from os.path import join, basename
from random import randint

from jnius import autoclass, cast, JavaException  # @UnresolvedImport
from plyer.facades import FileChooser
from plyer import storagepath

from android.config import ACTIVITY_CLASS_NAME  # @UnresolvedImport

from androidstorage4kivy import SharedStorage, Chooser  # @UnresolvedImport

from lib import activity  # @UnresolvedImport

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

Environment = autoclass("android.os.Environment")
String = autoclass('java.lang.String')
Intent = autoclass('android.content.Intent')
Activity = autoclass('android.app.Activity')
DocumentsContract = autoclass('android.provider.DocumentsContract')
ContentUris = autoclass('android.content.ContentUris')
Uri = autoclass('android.net.Uri')
Long = autoclass('java.lang.Long')
IMedia = autoclass('android.provider.MediaStore$Images$Media')
VMedia = autoclass('android.provider.MediaStore$Video$Media')
AMedia = autoclass('android.provider.MediaStore$Audio$Media')
Files = autoclass('android.provider.MediaStore$Files')
FileOutputStream = autoclass('java.io.FileOutputStream')


mActivity = autoclass(ACTIVITY_CLASS_NAME).mBitDustActivity


class AndroidFileChooser(FileChooser):

    select_code = None
    save_code = None
    selection = None
    multiple = False

    mime_type = {
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument." +
                "wordprocessingml.document",
        "ppt": "application/vnd.ms-powerpoint",
        "pptx": "application/vnd.openxmlformats-officedocument." +
                "presentationml.presentation",
        "xls": "application/vnd.ms-excel",
        "xlsx": "application/vnd.openxmlformats-officedocument." +
                "spreadsheetml.sheet",
        "text": "text/*",
        "pdf": "application/pdf",
        "zip": "application/zip",
        "image": "image/*",
        "video": "video/*",
        "audio": "audio/*",
        "application": "application/*",
    }

    selected_mime_type = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.select_code = randint(123456, 654321)
        self.save_code = randint(123456, 654321)
        self.selection = None

        # bind a function for a response from filechooser activity
        activity.bind(on_activity_result=self._on_activity_result)

    @staticmethod
    def _handle_selection(selection):
        return selection

    def _open_file(self, **kwargs):
        self.chooser = Chooser(self.chooser_callback)
        temp = SharedStorage().get_cache_dir()
        if _Debug:
            print('AndroidFileChooser._open_file', temp)
        self.chooser.choose_content("image/*")

    def chooser_callback(self, uri_list):
        if _Debug:
            print('AndroidFileChooser.chooser_callback', uri_list)

    def _open_file2(self, **kwargs):
        if _Debug:
            print('AndroidFileChooser._open_file', mActivity, kwargs)

        # set up selection handler
        # startActivityForResult is async
        # onActivityResult is sync
        self._handle_selection = kwargs.pop(
            'on_selection', self._handle_selection
        )
        self.selected_mime_type = kwargs.pop("filters")[0] if "filters" in kwargs else ""

        # create Intent for opening
        file_intent = Intent(Intent.ACTION_GET_CONTENT)
        if not self.selected_mime_type or type(self.selected_mime_type) != str or self.selected_mime_type not in self.mime_type:
            file_intent.setType("*/*")
        else:
            file_intent.setType(self.mime_type[self.selected_mime_type])
        file_intent.addCategory(
            Intent.CATEGORY_OPENABLE
        )

        if kwargs.get('multiple', self.multiple):
            file_intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, True)

        # start a new activity from PythonActivity
        # which creates a filechooser via intent
        mActivity.startActivityForResult(
            Intent.createChooser(file_intent, cast(
                'java.lang.CharSequence',
                String("FileChooser")
            )),
            self.select_code
        )

    def _save_file(self, **kwargs):
        if _Debug:
            print('AndroidFileChooser._save_file', kwargs)

        self._save_callback = kwargs.pop("callback")

        title = kwargs.pop("title", None)

        self.selected_mime_type = \
            kwargs.pop("filters")[0] if "filters" in kwargs else ""

        file_intent = Intent(Intent.ACTION_CREATE_DOCUMENT)
        if not self.selected_mime_type or \
            type(self.selected_mime_type) != str or \
                self.selected_mime_type not in self.mime_type:
            file_intent.setType("*/*")
        else:
            file_intent.setType(self.mime_type[self.selected_mime_type])
        file_intent.addCategory(
            Intent.CATEGORY_OPENABLE
        )

        if title:
            file_intent.putExtra(Intent.EXTRA_TITLE, title)

        mActivity.startActivityForResult(
            Intent.createChooser(file_intent, cast(
                'java.lang.CharSequence',
                String("FileChooser")
            )),
            self.save_code
        )

    def _on_activity_result(self, request_code, result_code, data):
        if _Debug:
            print('AndroidFileChooser._on_activity_result', request_code, self.select_code, result_code, data)

        if data is None:
            return

        if result_code != Activity.RESULT_OK:
            return

        if request_code == self.select_code:
            selection = []

            try:
                clip_data = data.getClipData()
            except:
                if _Debug:
                    traceback.print_exc()
                clip_data = None
            if _Debug:
                print('AndroidFileChooser._on_activity_result clip_data is', clip_data)
            if clip_data:
                try:
                    for count in range(clip_data.getItemCount()):
                        ele = self._resolve_uri(clip_data.getItemAt(count).getUri()) or []
                        selection.append(ele)
                except Exception as e:
                    if _Debug:
                        traceback.print_exc()
            else:
                try:
                    get_data = data.getData()
                except:
                    if _Debug:
                        traceback.print_exc()
                    get_data = None
                if _Debug:
                    print('AndroidFileChooser._on_activity_result get_data is', get_data)
                selection = [self._resolve_uri(get_data), ]
            self.selection = selection
            self._handle_selection(selection)

        elif request_code == self.save_code:
            uri = data.getData()
            with mActivity.getContentResolver().openFileDescriptor(uri, "w") as pfd:
                with FileOutputStream(pfd.getFileDescriptor()) as fileOutputStream:
                    self._save_callback(fileOutputStream)

    @staticmethod
    def _handle_external_documents(uri):
        file_id = DocumentsContract.getDocumentId(uri)
        file_type, file_name = file_id.split(':')
        primary_storage = storagepath.get_external_storage_dir()
        sdcard_storage = storagepath.get_sdcard_dir()
        directory = primary_storage
        if file_type == "primary":
            directory = primary_storage
        elif file_type == "home":
            directory = join(primary_storage, Environment.DIRECTORY_DOCUMENTS)
        elif sdcard_storage and file_type in sdcard_storage:
            directory = sdcard_storage
        return join(directory, file_name)

    @staticmethod
    def _handle_media_documents(uri):
        file_id = DocumentsContract.getDocumentId(uri)
        file_type, file_name = file_id.split(':')
        if _Debug:
            print('AndroidFileChooser._handle_media_documents', file_id)
        selection = '_id=?'

        if file_type == 'image':
            uri = IMedia.EXTERNAL_CONTENT_URI
        elif file_type == 'video':
            uri = VMedia.EXTERNAL_CONTENT_URI
        elif file_type == 'audio':
            uri = AMedia.EXTERNAL_CONTENT_URI
        else:
            uri = Files.getContentUri("external")
        if _Debug:
            print('AndroidFileChooser._handle_media_documents result', file_name, selection, uri)
        return file_name, selection, uri

    @staticmethod
    def _handle_downloads_documents(uri):
        downloads = [
            'content://downloads/public_downloads',
            'content://downloads/my_downloads',
            'content://downloads/all_downloads'
        ]

        file_id = DocumentsContract.getDocumentId(uri)
        try_uris = [
            ContentUris.withAppendedId(
                Uri.parse(down), Long.valueOf(file_id)
            )
            for down in downloads
        ]

        path = None
        for down in try_uris:
            try:
                path = AndroidFileChooser._parse_content(
                    uri=down, projection=['_data'],
                    selection=None,
                    selection_args=None,
                    sort_order=None
                )

            except JavaException:
                if _Debug:
                    traceback.print_exc()

            if path:
                break

        if not path:
            for down in try_uris:
                try:
                    path = AndroidFileChooser._parse_content(
                        uri=down, projection=None,
                        selection=None,
                        selection_args=None,
                        sort_order=None,
                        index_all=True
                    )

                except JavaException:
                    if _Debug:
                        traceback.print_exc()

                if path:
                    break
        return path

    def _resolve_uri(self, uri):
        uri_authority = uri.getAuthority()
        uri_scheme = uri.getScheme().lower()

        if _Debug:
            print('AndroidFileChooser._resolve_uri', uri_authority, uri_scheme)

        path = None
        file_name = None
        selection = None
        downloads = None

        if uri_authority == 'com.android.externalstorage.documents':
            return self._handle_external_documents(uri)

        elif uri_authority == 'com.android.providers.downloads.documents':
            path = downloads = self._handle_downloads_documents(uri)

        elif uri_authority == 'com.android.providers.media.documents':
            file_name, selection, uri = self._handle_media_documents(uri)

        if _Debug:
            print('AndroidFileChooser._resolve_uri', uri_scheme, uri, selection, file_name)
        
        if uri_scheme == 'content' and not downloads:
            try:
                path = self._parse_content(
                    uri=uri, projection=['_data'], selection=selection,
                    selection_args=file_name, sort_order=None
                )
            except Exception as e:  # handles array error for selection_args
                if _Debug:
                    traceback.print_exc()
                try:
                    path = self._parse_content(
                        uri=uri, projection=['_data'], selection=selection,
                        selection_args=[file_name], sort_order=None
                    )
                except Exception as e:
                    if _Debug:
                        traceback.print_exc()
                    return None

        elif uri_scheme == 'file':
            path = uri.getPath()

        if _Debug:
            print('AndroidFileChooser._resolve_uri path is', path)

        return path

    @staticmethod
    def _parse_content(
            uri, projection, selection, selection_args, sort_order,
            index_all=False
    ):
        result = None
        resolver = mActivity.getContentResolver()
        if _Debug:
            print('AndroidFileChooser._parse_content', resolver, uri)
        read = Intent.FLAG_GRANT_READ_URI_PERMISSION
        write = Intent.FLAG_GRANT_READ_URI_PERMISSION
        persist = Intent.FLAG_GRANT_READ_URI_PERMISSION

        mActivity.grantUriPermission(
            mActivity.getPackageName(),
            uri,
            read | write | persist
        )

        if not index_all:
            cursor = resolver.query(
                uri, projection, selection,
                selection_args, sort_order
            )

            idx = cursor.getColumnIndex(projection[0])
            if idx != -1 and cursor.moveToFirst():
                result = cursor.getString(idx)
        else:
            result = []
            cursor = resolver.query(
                uri, projection, selection,
                selection_args, sort_order
            )
            while cursor.moveToNext():
                for idx in range(cursor.getColumnCount()):
                    result.append(cursor.getString(idx))
            result = '/'.join(result)
        if _Debug:
            print('AndroidFileChooser._parse_content result is', result)
        return result

    def _file_selection_dialog(self, **kwargs):
        mode = kwargs.pop('mode', None)
        if mode == 'open':
            self._open_file(**kwargs)
        elif mode == 'save':
            self._save_file(**kwargs)


def instance():
    return AndroidFileChooser()
