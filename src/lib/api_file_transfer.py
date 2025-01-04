from kivy.clock import mainthread

#------------------------------------------------------------------------------

from lib import api_client
from lib import strng

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

def file_download(source_path, destination_path, chunk_size=32*1024, result_callback=None):
    if _Debug:
        print('api_file_transfer.file_download', source_path, destination_path)
    try:
        file_dest = open(destination_path, 'wb')
    except Exception as exc:
        if result_callback:
            result_callback(exc)
        return

    @mainthread
    def on_chunk_received(resp, offset):
        if _Debug:
            print('api_file_transfer.file_download.on_chunk_received', offset)
        if not api_client.is_ok(resp):
            try:
                file_dest.close()
            except Exception as exc:
                if _Debug:
                    print('api_file_transfer.file_download.on_chunk_received', exc)
            if result_callback:
                result_callback(Exception(api_client.response_err(resp)))
            return
        result = api_client.response_result(resp)
        text_chunk = result.get('chunk')
        if not text_chunk:
            try:
                file_dest.close()
            except Exception as exc:
                if _Debug:
                    print('api_file_transfer.file_download.on_chunk_received', exc)
            if not result.get('completed'):
                if result_callback:
                    result_callback(Exception('file transfer was not completed successfully'))
                return
            if result_callback:
                result_callback(True)
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
                    print('api_file_transfer.file_download.on_chunk_received', exc)
            if result_callback:
                result_callback(exc)
            return
        do_chunk_request(new_offset)

    @mainthread
    def do_chunk_request(offset):
        if _Debug:
            print('api_file_transfer.file_download.do_chunk_request', source_path, offset)
        api_client.chunk_read(path=source_path, offset=offset, max_size=chunk_size, cb=lambda resp: on_chunk_received(resp, offset))

    do_chunk_request(0)

#------------------------------------------------------------------------------

def file_upload(source_path, chunk_size=32*1024, result_callback=None):
    if _Debug:
        print('api_file_transfer.file_upload', source_path)
    try:
        file_src = open(source_path, 'rb')
    except Exception as exc:
        if result_callback:
            result_callback(exc)
        return

    @mainthread
    def on_chunk_result(resp, destination_path):
        if _Debug:
            print('api_file_transfer.file_upload.on_chunk_result', destination_path, resp)
        if not api_client.is_ok(resp):
            try:
                file_src.close()
            except Exception as exc:
                if _Debug:
                    print('api_file_transfer.file_upload.on_chunk_result', exc)
            if result_callback:
                result_callback(Exception(api_client.response_err(resp)))
            return
        result = api_client.response_result(resp)
        if not destination_path:
            destination_path = result.get('path')
            if not destination_path:
                try:
                    file_src.close()
                except Exception as exc:
                    if _Debug:
                        print('api_file_transfer.file_upload.on_chunk_result', exc)
                if result_callback:
                    result_callback(Exception('file transfer was not completed successfully'))
                return
        do_chunk_send(destination_path)

    @mainthread
    def do_chunk_send(destination_path):
        if _Debug:
            print('api_file_transfer.file_upload.do_chunk_send', destination_path)
        try:
            bin_chunk = file_src.read(chunk_size)
        except Exception as exc:
            try:
                file_src.close()
            except Exception as exc:
                if _Debug:
                    print('api_file_transfer.file_upload.do_chunk_send', exc)
            if result_callback:
                result_callback(exc)
            return
        if not bin_chunk:
            try:
                file_src.close()
            except Exception as exc:
                if _Debug:
                    print('api_file_transfer.file_upload.do_chunk_send', exc)
            if result_callback:
                result_callback(destination_path)
            return
        text_chunk = strng.to_text(bin_chunk, encoding='latin1')
        api_client.chunk_write(data=text_chunk, path=destination_path, cb=lambda resp: on_chunk_result(resp, destination_path))

    do_chunk_send(None)
