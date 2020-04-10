import asyncio
import socket
import os, select
from sendfile import sendfile

host = 'localhost'
port = 9527
loop = asyncio.get_event_loop()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setblocking(False)
s.bind((host, port))
s.listen(10)


async def handler(conn):
    print(conn)
    request = b''
    while True:
        rs, _, es = select.select([conn], [], [conn])
        if conn in rs:
            data = recvall(conn)
            request += data
            if data.endswith(b'\r\n\r\n'):
                break
        asyncio.sleep(0.01)
    print(data)

    # Attempt 1
    # with open('requirements.lock', 'rb') as f:
    #     # only python3.5+, and do not support non-bloking socket
    #     conn.sendfile(f)

    # Attempt 2
    filepath = 'requirements.lock'
    with open(filepath, 'rb') as f:
        blocksize = os.path.getsize(filepath)
        sent = sendfile(conn.fileno(), f.fileno(), 0, blocksize)
    conn.close()


async def server():
    while True:
        conn, addr = await loop.sock_accept(s)
        loop.create_task(handler(conn))


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


loop.create_task(server())
loop.run_forever()
loop.close()
