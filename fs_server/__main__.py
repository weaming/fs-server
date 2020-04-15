import asyncio
import mimetypes
import os
import select
import socket
import json
import argparse

from httptools import HttpRequestParser
from sendfile import sendfile
from filetree import File

from fs_server.mapping import FileSystem


mapping = None


class HTTP:
    def __init__(self):
        self.url = ''

    def on_url(self, url):
        self.url = url.decode()


async def handler(conn):
    print(conn)

    request = await readall_from_socket(conn)
    # print(request)

    http = HTTP()
    parser = HttpRequestParser(http)
    parser.feed_data(request)
    method = parser.get_method().decode()
    url_path = http.url
    print(method, url_path)

    # Attempt 1
    # with open('requirements.lock', 'rb') as f:
    #     # only python3.5+, and do not support non-bloking socket
    #     conn.sendfile(f)

    # Attempt 2
    fl = None
    for mp in mapping:
        fl = mp.file(url_path or '')
        if fl:
            break
    if fl:
        if fl.exists():
            filepath = fl.path
            if fl.is_file():
                with open(filepath, 'rb') as f:
                    blocksize = os.path.getsize(filepath)
                    conn.send(b'HTTP/1.1 200 OK\r\n')
                    conn.send(f'Content-Length: {blocksize}\r\n'.encode('ascii'))
                    mime = mimetypes.guess_type(filepath)[0]
                    # mime = "text/plain" if mime else "application/octet-stream"
                    mime = mime or "application/octet-stream"
                    conn.send(
                        f'Content-Type: {mime}; charset=utf-8\r\n'.encode('ascii')
                    )
                    # conn.send(b'Transfer-Encoding: chunked')
                    conn.send(b'\r\n')
                    _ = sendfile(conn.fileno(), f.fileno(), 0, blocksize)
            elif fl.is_dir():
                files = fl.listdir()
                body = '<br/>'.join(
                    f'<a href="{url_path.rstrip("/")}/{x.basename}{"/" if x.is_dir() else ""}">{x.basename}{"/" if x.is_dir() else ""}</a>'
                    for x in files
                ).encode('utf8')
                conn.send(b'HTTP/1.1 200 OK\r\n')
                conn.send(f'Content-Length: {len(body)}\r\n'.encode('ascii'))
                conn.send(b'Content-Type: text/html; charset=utf-8\r\n')
                conn.send(b'\r\n')
                conn.sendall(body)

    conn.send(b'HTTP/1.1 404 Not Found\r\n')
    conn.send(b'Content-Type: text/plain; charset=utf-8\r\n')
    conn.send(b'\r\n')
    conn.sendall(b'Not Found')
    conn.close()


async def server(loop, socket):
    while True:
        conn, addr = await loop.sock_accept(socket)
        loop.create_task(handler(conn))


async def readall_from_socket(conn):
    request = b''
    while True:
        rs, _, es = select.select([conn], [], [conn])
        if conn in rs:
            data = recvall(conn)
            request += data
            if len(data) == 0 or request.endswith(b'\r\n\r\n'):
                break
        asyncio.sleep(0.01)
    return request


def recvall(sock):
    BUFF_SIZE = 4096  # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data


def get_mapping(config_path):
    if config_path:
        cfg = File(config_path)
        if cfg.exists():
            with open(cfg.path, 'r') as f:
                cfg_dict = json.load(f)
                assert isinstance(cfg_dict, dict)
                return [FileSystem(k, v) for k, v in cfg_dict.items()]
    return [FileSystem('/', './')]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="file path of config in json format")
    parser.add_argument("--host", help="listen host", default='localhost')
    parser.add_argument("--port", help="listen port", type=int, default=8080)
    parser.add_argument(
        "--backlog",
        help="the number of unaccepted connections that the system will allow before refusing new connections",
        type=int,
        default=1000,
    )
    args = parser.parse_args()

    host = args.host
    port = int(args.port)
    global mapping
    mapping = get_mapping(args.config)
    print(mapping)

    loop = asyncio.get_event_loop()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(False)

    s.bind((host, port))
    s.listen(args.backlog)

    loop.create_task(server(loop, s))
    loop.run_forever()
    loop.close()


if __name__ == '__main__':
    main()
