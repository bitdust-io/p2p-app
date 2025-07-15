import threading

#------------------------------------------------------------------------------

from kivy.clock import mainthread

#------------------------------------------------------------------------------

from lib import api_client
from lib import strng

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class FileDownloader(threading.Thread):

    def __init__(self, *args, **kwargs):
        self._source_path = kwargs.pop('source_path')
        self._destination_path = kwargs.pop('destination_path')
        self._chunk_size = kwargs.pop('chunk_size', 64 * 1024)
        self._result_callback = kwargs.pop('result_callback', None)
        self._progress_callback = kwargs.pop('progress_callback', None)
        threading.Thread.__init__(self, *args, **kwargs)

    @mainthread
    def _call_result_callback(self, ret):
        if self._result_callback:
            self._result_callback(ret)
        self._result_callback = None

    @mainthread
    def _call_progress_callback(self, source_path, destination_path, offset):
        if self._progress_callback:
            self._progress_callback(source_path, destination_path, offset)
        self._progress_callback = None

    def run(self):
        if _Debug:
            print('api_file_transfer.FileDownloader.run', self._source_path, self._destination_path)
        try:
            file_dest = open(self._destination_path, 'wb')
        except Exception as exc:
            self._call_result_callback(exc)
            return

        def on_chunk_received(resp, offset):
            if _Debug:
                print('api_file_transfer.FileDownloader.on_chunk_received', offset)
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
            if not text_chunk:
                try:
                    file_dest.close()
                except Exception as exc:
                    if _Debug:
                        print('api_file_transfer.FileDownloader.on_chunk_received', exc)
                if not result.get('completed'):
                    self._call_result_callback(Exception('file transfer was not completed successfully'))
                    return
                self._call_result_callback(True)
                return
            try:
                bin_chunk = strng.to_bin(text_chunk, encoding='latin1')
                file_dest.write(bin_chunk)
                new_offset = offset + len(bin_chunk)
            except Exception as exc:
                try:
                    file_dest.close()
                except Exception as exc:
                    if _Debug:
                        print('api_file_transfer.FileDownloader.on_chunk_received', exc)
                self._call_result_callback(exc)
                return
            do_chunk_request(new_offset)

        def do_chunk_request(offset):
            if _Debug:
                print('api_file_transfer.FileDownloader.do_chunk_request', self._source_path, self._destination_path, offset)
            if offset:
                self._call_progress_callback(self._source_path, self._destination_path, offset)

            api_client.chunk_read(path=self._source_path, offset=offset, max_size=self._chunk_size, cb=lambda resp: on_chunk_received(resp, offset))

        do_chunk_request(0)

#------------------------------------------------------------------------------

class FileUploader(threading.Thread):

    def __init__(self, *args, **kwargs):
        self._source_path = kwargs.pop('source_path')
        self._chunk_size = kwargs.pop('chunk_size', 64 * 1024)
        self._result_callback = kwargs.pop('result_callback', None)
        self._progress_callback = kwargs.pop('progress_callback', None)
        threading.Thread.__init__(self, *args, **kwargs)

    @mainthread
    def _call_result_callback(self, ret):
        if self._result_callback:
            self._result_callback(ret)
        self._result_callback = None

    @mainthread
    def _call_progress_callback(self, source_path, destination_path, offset):
        if self._progress_callback:
            self._progress_callback(source_path, destination_path, offset)
        self._progress_callback = None

    def run(self)->None:
        if _Debug:
            print('api_file_transfer.FileUploader.run', self._source_path)
        try:
            file_src = open(self._source_path, 'rb')
        except Exception as exc:
            self._call_result_callback(exc)
            return

        def on_chunk_result(resp, destination_path, bytes_sent):
            if _Debug:
                print('api_file_transfer.FileUploader.on_chunk_result', destination_path, bytes_sent, resp)
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
                print('api_file_transfer.FileUploader.do_chunk_send', destination_path, bytes_sent)
            if destination_path:
                self._call_progress_callback(self._source_path, destination_path, bytes_sent)
            try:
                bin_chunk = file_src.read(self._chunk_size)
            except Exception as exc:
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
                self._call_result_callback(destination_path)
                return
            text_chunk = strng.to_text(bin_chunk, encoding='latin1')
            api_client.chunk_write(
                data=text_chunk,
                path=destination_path,
                cb=lambda resp: on_chunk_result(resp, destination_path, bytes_sent + len(bin_chunk)),
            )

        do_chunk_send(None, 0)
