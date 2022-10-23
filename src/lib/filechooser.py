from os.path import join, basename
from random import randint

from jnius import autoclass, cast, JavaException  # @UnresolvedImport
from plyer.facades import FileChooser
from plyer import storagepath

from android.config import ACTIVITY_CLASS_NAME  # @UnresolvedImport

from lib import activity  # @UnresolvedImport

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

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


mActivity = autoclass(ACTIVITY_CLASS_NAME).mBitDustActivity


class AndroidFileChooser(FileChooser):

    # filechooser activity <-> result pair identification
    select_code = None

    # default selection value
    selection = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.select_code = randint(123456, 654321)
        self.selection = None

        # bind a function for a response from filechooser activity
        activity.bind(on_activity_result=self._on_activity_result)

    @staticmethod
    def _handle_selection(selection):
        return selection

    def _open_file(self, **kwargs):
        if _Debug:
            print('AndroidFileChooser._open_file', mActivity, kwargs)

        # set up selection handler
        # startActivityForResult is async
        # onActivityResult is sync
        self._handle_selection = kwargs.pop(
            'on_selection', self._handle_selection
        )

        # create Intent for opening
        file_intent = Intent(Intent.ACTION_GET_CONTENT)
        file_intent.setType('*/*')
        file_intent.addCategory(
            Intent.CATEGORY_OPENABLE
        )

        # start a new activity from PythonActivity
        # which creates a filechooser via intent
        mActivity.startActivityForResult(
            Intent.createChooser(file_intent, cast(
                'java.lang.CharSequence',
                String("FileChooser")
            )),
            self.select_code
        )

    def _on_activity_result(self, request_code, result_code, data):
        if _Debug:
            print('AndroidFileChooser._on_activity_result', request_code, result_code, data)

        # not our response
        if request_code != self.select_code:
            return

        if result_code != Activity.RESULT_OK:
            # The action had been cancelled.
            return

        selection = self._resolve_uri(data.getData()) or []

        # return value to object
        self.selection = [selection]
        # return value via callback
        self._handle_selection([selection])

    @staticmethod
    def _handle_external_documents(uri):
        file_id = DocumentsContract.getDocumentId(uri)
        file_type, file_name = file_id.split(':')

        # internal SD card mostly mounted as a files storage in phone
        internal = storagepath.get_external_storage_dir()

        # external (removable) SD card i.e. microSD
        external = storagepath.get_sdcard_dir()
        external_base = basename(external)

        # resolve sdcard path
        sdcard = internal

        # because external might have /storage/.../1 or other suffix
        # and file_type might be only a part of the real folder in /storage
        if file_type in external_base or external_base in file_type:
            sdcard = external

        path = join(sdcard, file_name)
        return path

    @staticmethod
    def _handle_media_documents(uri):
        file_id = DocumentsContract.getDocumentId(uri)
        file_type, file_name = file_id.split(':')
        selection = '_id=?'

        if file_type == 'image':
            uri = IMedia.EXTERNAL_CONTENT_URI
        elif file_type == 'video':
            uri = VMedia.EXTERNAL_CONTENT_URI
        elif file_type == 'audio':
            uri = AMedia.EXTERNAL_CONTENT_URI
        return file_name, selection, uri

    @staticmethod
    def _handle_downloads_documents(uri):
        # known locations, differ between machines
        downloads = [
            'content://downloads/public_downloads',
            'content://downloads/my_downloads',
            # all_downloads requires separate permission
            # android.permission.ACCESS_ALL_DOWNLOADS
            'content://downloads/all_downloads'
        ]

        file_id = DocumentsContract.getDocumentId(uri)
        try_uris = [
            ContentUris.withAppendedId(
                Uri.parse(down), Long.valueOf(file_id)
            )
            for down in downloads
        ]

        # try all known Download folder uris
        # and handle JavaExceptions due to different locations
        # for content:// downloads or missing permission
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
                import traceback
                traceback.print_exc()

            # we got a path, ignore the rest
            if path:
                break

        # alternative approach to Downloads by joining
        # all data items from Activity result
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
                    import traceback
                    traceback.print_exc()

                # we got a path, ignore the rest
                if path:
                    break
        return path

    def _resolve_uri(self, uri):
        if _Debug:
            print('AndroidFileChooser._resolve_uri', uri)

        uri_authority = uri.getAuthority()
        uri_scheme = uri.getScheme().lower()

        path = None
        file_name = None
        selection = None
        downloads = None

        # not a document URI, nothing to convert from
        if not DocumentsContract.isDocumentUri(mActivity, uri):
            return path

        if uri_authority == 'com.android.externalstorage.documents':
            return self._handle_external_documents(uri)

        # in case a user selects a file from 'Downloads' section
        # note: this won't be triggered if a user selects a path directly
        #       e.g.: Phone -> Download -> <some file>
        elif uri_authority == 'com.android.providers.downloads.documents':
            path = downloads = self._handle_downloads_documents(uri)

        elif uri_authority == 'com.android.providers.media.documents':
            file_name, selection, uri = self._handle_media_documents(uri)

        # parse content:// scheme to path
        if uri_scheme == 'content' and not downloads:
            path = self._parse_content(
                uri=uri, projection=['_data'], selection=selection,
                selection_args=[file_name], sort_order=None
            )

        # nothing to parse, file:// will return a proper path
        elif uri_scheme == 'file':
            path = uri.getPath()

        return path

    @staticmethod
    def _parse_content(
            uri, projection, selection, selection_args, sort_order,
            index_all=False
    ):
        result = None
        resolver = mActivity.getContentResolver()
        read = Intent.FLAG_GRANT_READ_URI_PERMISSION
        write = Intent.FLAG_GRANT_READ_URI_PERMISSION
        persist = Intent.FLAG_GRANT_READ_URI_PERMISSION

        # grant permission for our activity
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
        return result

    def _file_selection_dialog(self, **kwargs):
        mode = kwargs.pop('mode', None)
        if mode == 'open':
            self._open_file(**kwargs)


def instance():
    return AndroidFileChooser()
