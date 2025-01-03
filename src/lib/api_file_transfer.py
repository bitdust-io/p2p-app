import os

#------------------------------------------------------------------------------

from kivy.clock import mainthread

#------------------------------------------------------------------------------

from lib import api_client
from lib import strng

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

def file_download(source_path, destination_path, chunk_size=32*1024, result_callback=None):
    offset = 0

    try:
        file_dest = open(destination_path, 'wb')
    except Exception as exc:
        if result_callback:
            result_callback(exc)
        return

    @mainthread
    def on_chunk_received(resp):
        if _Debug:
            print('api_file_transfer.file_download.on_chunk_received', resp)
        if not api_client.is_ok(resp):
            if result_callback:
                result_callback(Exception(api_client.response_err(resp)))
            return
        result = api_client.response_result(resp)
        text_chunk = result.get('chunk')
        if not text_chunk:
            file_dest.close()
            if not result.get('completed'):
                if result_callback:
                    result_callback(Exception('file transfer was not completed successfully'))
                return
            if result_callback:
                result_callback(True)
            return
        try:
            bin_chunk = strng.to_bin(text_chunk)
            file_dest.write(bin_chunk)
            offset += len(bin_chunk)
        except Exception as exc:
            if result_callback:
                result_callback(exc)
            return
        do_chunk_request()

    @mainthread
    def do_chunk_request():
        if _Debug:
            print('api_file_transfer.file_download.do_chunk_request', source_path, offset)
        api_client.chunk_read(path=source_path, offset=offset, max_size=chunk_size, cb=on_chunk_received)

    do_chunk_request()
