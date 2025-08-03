import threading

#------------------------------------------------------------------------------

from kivy.clock import mainthread

#------------------------------------------------------------------------------

from lib import api_client
from lib import strng

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

DEFAULT_CHUNK_SIZE = 32 * 1024

#------------------------------------------------------------------------------

_DownloadsRemotePathIndex = {}
_DownloadsDestinationPathIndex = {}
_LatestDownloadID = 0
_ActiveDownloads = {}
_DownloadingTrackingCallback = None

_UploadsRemotePathIndex = {}
_UploadsDestinationPathIndex = {}
_LatestUploadID = 0
_ActiveUploads = {}
_UploadingTrackingCallback = None

#------------------------------------------------------------------------------

def get_downloading_remote_path(destination_path):
    global _DownloadsDestinationPathIndex
    return _DownloadsDestinationPathIndex.get(destination_path)


def get_uploading_remote_path(destination_path):
    global _UploadsDestinationPathIndex
    return _UploadsDestinationPathIndex.get(destination_path)

#------------------------------------------------------------------------------

def set_downloading_progress_tracking_callback(cb):
    global _DownloadingTrackingCallback
    _DownloadingTrackingCallback = cb


def call_downloading_progress_tracking_callback(bytes_received, source_path, destination_path, remote_path, thread_id):
    global _DownloadingTrackingCallback
    if _DownloadingTrackingCallback:
        _DownloadingTrackingCallback(bytes_received, source_path, destination_path, remote_path, thread_id)

#------------------------------------------------------------------------------

def set_uploading_progress_tracking_callback(cb):
    global _UploadingTrackingCallback
    _UploadingTrackingCallback = cb


def call_uploading_progress_tracking_callback(bytes_sent, source_path, destination_path, remote_path, thread_id):
    global _UploadingTrackingCallback
    if _UploadingTrackingCallback:
        _UploadingTrackingCallback(bytes_sent, source_path, destination_path, remote_path, thread_id)

#------------------------------------------------------------------------------

def start_downloader(source_path, destination_path, chunk_size=None, remote_path=None, result_callback=None):
    global _ActiveDownloads
    global _LatestDownloadID
    if not chunk_size:
        chunk_size = DEFAULT_CHUNK_SIZE
    _LatestDownloadID += 1
    _ActiveDownloads[_LatestDownloadID] = FileDownloader(
        thread_id=_LatestDownloadID,
        remote_path=remote_path,
        source_path=source_path,
        destination_path=destination_path,
        chunk_size=chunk_size,
        result_callback=result_callback,
        progress_callback=call_downloading_progress_tracking_callback,
    )
    if _Debug:
        print('api_file_transfer.start_downloader', _LatestDownloadID, source_path, destination_path, remote_path)
    _ActiveDownloads[_LatestDownloadID].start()
    return _LatestDownloadID


def close_downloader(thread_id):
    global _ActiveDownloads
    if thread_id not in _ActiveDownloads:
        if _Debug:
            print('api_file_transfer.close_downloader was not active', thread_id)
        return False
    _ActiveDownloads.pop(thread_id)
    if _Debug:
        print('api_file_transfer.close_downloader', thread_id)

#------------------------------------------------------------------------------

def start_uploader(source_path, chunk_size=None, remote_path=None, result_callback=None):
    global _ActiveUploads
    global _LatestUploadID
    if not chunk_size:
        chunk_size = DEFAULT_CHUNK_SIZE
    _LatestUploadID += 1
    _ActiveUploads[_LatestUploadID] = FileUploader(
        thread_id=_LatestUploadID,
        remote_path=remote_path,
        source_path=source_path,
        chunk_size=chunk_size,
        result_callback=result_callback,
        progress_callback=call_uploading_progress_tracking_callback,
    )
    if _Debug:
        print('api_file_transfer.start_uploader', _LatestUploadID, source_path, remote_path)
    _ActiveUploads[_LatestUploadID].start()
    return _LatestUploadID


def close_uploader(thread_id):
    global _ActiveUploads
    if thread_id not in _ActiveUploads:
        if _Debug:
            print('api_file_transfer.close_uploader was not active', thread_id)
        return False
    _ActiveUploads.pop(thread_id)
    if _Debug:
        print('api_file_transfer.close_uploader', thread_id)

#------------------------------------------------------------------------------

class FileDownloader(threading.Thread):

    def __init__(self, *args, **kwargs):
        global _DownloadsRemotePathIndex
        global _DownloadsDestinationPathIndex
        self._thread_id = kwargs.pop('thread_id')
        self._remote_path = kwargs.pop('remote_path', None)
        self._source_path = kwargs.pop('source_path')
        self._destination_path = kwargs.pop('destination_path')
        if self._remote_path:
            _DownloadsRemotePathIndex[self._remote_path] = {
                'source_path': self._source_path,
                'destination_path': self._destination_path,
                'thread_id': self._thread_id,
            }
            _DownloadsDestinationPathIndex[self._destination_path] = self._remote_path
        self._bytes_received = 0
        self._chunk_size = kwargs.pop('chunk_size', 32 * 1024)
        self._result_callback = kwargs.pop('result_callback', None)
        self._progress_callback = kwargs.pop('progress_callback', None)
        self._stop_state = False
        threading.Thread.__init__(self, *args, **kwargs)

    @mainthread
    def _close_downloader(self):
        if self._progress_callback:
            self._progress_callback(None, self._source_path, self._destination_path, self._remote_path, self._thread_id)
        close_downloader(self._thread_id)

    @mainthread
    def _call_result_callback(self, ret):
        if self._result_callback:
            self._result_callback(ret)
        self._result_callback = None

    @mainthread
    def _call_progress_callback(self, bytes_received):
        if self._progress_callback:
            self._progress_callback(bytes_received, self._source_path, self._destination_path, self._remote_path, self._thread_id)

    def turn_off(self):
        self._stop_state = True

    def run(self):
        if _Debug:
            print('api_file_transfer.FileDownloader.run', self._source_path, self._destination_path)
        try:
            file_dest = open(self._destination_path, 'wb')
        except Exception as exc:
            if _Debug:
                print('api_file_transfer.FileDownloader.run ERROR: ', exc)
            self._call_result_callback(exc)
            self._close_downloader()
            return

        def on_chunk_received(resp, offset):
            if _Debug:
                print('api_file_transfer.FileDownloader.on_chunk_received', offset)
            if self._stop_state:
                try:
                    file_dest.close()
                except Exception as exc:
                    if _Debug:
                        print('api_file_transfer.FileDownloader.on_chunk_received', exc)
                return
            if not api_client.is_ok(resp):
                try:
                    file_dest.close()
                except Exception as exc:
                    if _Debug:
                        print('api_file_transfer.FileDownloader.on_chunk_received', exc)
                self._call_result_callback(Exception(api_client.response_err(resp)))
                return
            result = api_client.response_result(resp)
            text_chunk = result.get('chunk')
            stats = result.get('stats')
            if not text_chunk:
                try:
                    file_dest.close()
                except Exception as exc:
                    if _Debug:
                        print('api_file_transfer.FileDownloader.on_chunk_received', exc)
                if not result.get('completed'):
                    self._call_result_callback(Exception('file transfer was not completed successfully'))
                    return
                if _Debug:
                    print('api_file_transfer.FileDownloader.on_chunk_received stats=%r' % stats)
                if stats:
                    if stats['bytes'] != self._bytes_received:
                        raise Exception('Bytes received count is not matching')
                self._call_result_callback(True)
                return
            try:
                bin_chunk = strng.to_bin(text_chunk, encoding='latin1')
                chunk_sz = len(bin_chunk)
                file_dest.write(bin_chunk)
                file_dest.flush()
                new_offset = offset + chunk_sz
            except Exception as exc:
                if _Debug:
                    print('api_file_transfer.FileDownloader.on_chunk_received ERROR: ', exc)
                try:
                    file_dest.close()
                except Exception as exc:
                    if _Debug:
                        print('api_file_transfer.FileDownloader.on_chunk_received', exc)
                self._call_result_callback(exc)
                return
            self._bytes_received += chunk_sz
            if _Debug:
                print('api_file_transfer.FileDownloader.on_chunk_received _bytes_received=%r' % self._bytes_received)
            do_chunk_request(new_offset)

        def do_chunk_request(offset):
            if _Debug:
                print('api_file_transfer.FileDownloader.do_chunk_request', self._remote_path, self._source_path, self._destination_path, offset)
            if self._stop_state:
                try:
                    file_dest.close()
                except Exception as exc:
                    if _Debug:
                        print('api_file_transfer.FileDownloader.do_chunk_request', exc)
                return
            if offset:
                self._call_progress_callback(offset)
            api_client.chunk_read(path=self._source_path, offset=offset, max_size=self._chunk_size, cb=lambda resp: on_chunk_received(resp, offset))

        do_chunk_request(0)
        self._close_downloader()

#------------------------------------------------------------------------------

class FileUploader(threading.Thread):

    def __init__(self, *args, **kwargs):
        self._thread_id = kwargs.pop('thread_id')
        self._remote_path = kwargs.pop('remote_path', None)
        self._source_path = kwargs.pop('source_path')
        self._destination_path = None
        self._bytes_sent = 0
        self._chunk_size = kwargs.pop('chunk_size', 32 * 1024)
        self._result_callback = kwargs.pop('result_callback', None)
        self._progress_callback = kwargs.pop('progress_callback', None)
        self._stop_state = False
        threading.Thread.__init__(self, *args, **kwargs)

    @mainthread
    def _close_uploader(self):
        if self._progress_callback:
            self._progress_callback(None, self._source_path, self._destination_path, self._remote_path, self._thread_id)
        close_uploader(self._thread_id)

    @mainthread
    def _call_result_callback(self, ret):
        if self._result_callback:
            self._result_callback(ret)
        self._result_callback = None

    @mainthread
    def _call_progress_callback(self, bytes_sent):
        if self._progress_callback:
            self._progress_callback(bytes_sent, self._source_path, self._destination_path, self._remote_path, self._thread_id)

    def turn_off(self):
        self._stop_state = True

    def run(self)->None:
        global _UploadsRemotePathIndex
        global _UploadsDestinationPathIndex
        if _Debug:
            print('api_file_transfer.FileUploader.run', self._source_path)
        try:
            file_src = open(self._source_path, 'rb')
        except Exception as exc:
            self._call_result_callback(exc)
            self._close_uploader()
            return

        def on_chunk_result(resp, destination_path, bytes_sent):
            if _Debug:
                print('api_file_transfer.FileUploader.on_chunk_result', destination_path, bytes_sent, resp)
            if self._stop_state:
                try:
                    file_src.close()
                except Exception as exc:
                    if _Debug:
                        print('api_file_transfer.FileUploader.on_chunk_result', exc)
                return
            if not api_client.is_ok(resp):
                try:
                    file_src.close()
                except Exception as exc:
                    if _Debug:
                        print('api_file_transfer.FileUploader.on_chunk_result', exc)
                self._call_result_callback(Exception(api_client.response_err(resp)))
                return
            result = api_client.response_result(resp)
            if not destination_path:
                destination_path = result.get('path')
                self._destination_path = destination_path
                if self._remote_path:
                    _UploadsRemotePathIndex[self._remote_path] = {
                        'source_path': self._source_path,
                        'destination_path': self._destination_path,
                        'thread_id': self._thread_id,
                    }
                    if self._destination_path:
                        _UploadsDestinationPathIndex[self._destination_path] = self._remote_path
                if not destination_path:
                    try:
                        file_src.close()
                    except Exception as exc:
                        if _Debug:
                            print('api_file_transfer.FileUploader.on_chunk_result', exc)
                    self._call_result_callback(Exception('file transfer was not completed successfully'))
                    return
            do_chunk_send(destination_path, bytes_sent)

        def do_chunk_send(destination_path, bytes_sent):
            if _Debug:
                print('api_file_transfer.FileUploader.do_chunk_send', self._remote_path, destination_path, bytes_sent)
            if self._stop_state:
                try:
                    file_src.close()
                except Exception as exc:
                    if _Debug:
                        print('api_file_transfer.FileUploader.do_chunk_send', exc)
                return
            if destination_path:
                self._call_progress_callback(bytes_sent)
            try:
                bin_chunk = file_src.read(self._chunk_size)
            except Exception as exc:
                if _Debug:
                    print('api_file_transfer.FileUploader.do_chunk_send ERROR: ', exc)
                try:
                    file_src.close()
                except Exception as exc:
                    if _Debug:
                        print('api_file_transfer.FileUploader.do_chunk_send', exc)
                self._call_result_callback(exc)
                return
            if not bin_chunk:
                try:
                    file_src.close()
                except Exception as exc:
                    if _Debug:
                        print('api_file_transfer.FileUploader.do_chunk_send', exc)
                if _Debug:
                    print('api_file_transfer.FileUploader.do_chunk_send COMPLETE %r bytes_sent=%r' % (destination_path, self._bytes_sent))
                self._call_result_callback(destination_path)
                return
            chunk_sz = len(bin_chunk)
            text_chunk = strng.to_text(bin_chunk, encoding='latin1')
            self._bytes_sent += chunk_sz
            api_client.chunk_write(
                data=text_chunk,
                path=destination_path,
                cb=lambda resp: on_chunk_result(resp, destination_path, bytes_sent + chunk_sz),
            )

        do_chunk_send(None, 0)
        self._close_uploader()
