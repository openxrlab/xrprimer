import sys
from threading import Thread
from typing import Dict, Optional, Union

import umsgpack
import zmq
from rich import print


class ViewerWindow:
    context = zmq.Context()  # pylint: disable=abstract-class-instantiated

    def __init__(self, zmq_port: int = 6000, ip_address: str = '127.0.0.1'):
        self.zmq_port = zmq_port
        self.client = self.context.socket(zmq.REQ)
        zmq_url = f'tcp://{ip_address}:{self.zmq_port}'
        self.client.connect(zmq_url)
        self.assert_connected()

    def send(self, command):
        """Send a message to bridge server."""
        self.client.send_multipart(
            [command['type'].encode('utf-8'),
             umsgpack.packb(command)])

        return umsgpack.packb(self.client.recv())

    def send_ping(self):
        """Ping to the bridge server."""
        type = 'ping'
        data = umsgpack.packb({'type': type})
        self.client.send_multipart([type.encode('utf-8'), data])
        res = self.client.recv()

        return umsgpack.unpackb(res)

    def timeout_ping(self, timeout_in_sec: int = 12):
        res = [
            Exception(f'Failed to connect to bridge server in '
                      f'{timeout_in_sec} seconds.')
        ]

        def wrapper_func():
            res[0] = self.send_ping()

        thread = Thread(target=wrapper_func, daemon=True)

        try:
            thread.start()
            thread.join(timeout_in_sec)
        except Exception as e:
            print('[bold red]Failed to start thread[/bold red]')
            raise e

        ret = res[0]
        if isinstance(ret, BaseException):
            raise ret

        return ret

    def assert_connected(self, timeout_in_sec: int = 10):
        """Check whether the connection has been established properly."""
        try:
            print('[bold blue]Sending ping to the bridge server[bold blue]')
            _ = self.timeout_ping(timeout_in_sec)
            print('[bold green]Successfully connected to the'
                  ' bridge server.[/bold green]')
        except Exception as e:
            print(e)
            sys.exit()


class Viewer:
    """for connecting to the bridge server."""

    def __init__(self,
                 zmq_port: Optional[int] = None,
                 window: Optional[ViewerWindow] = None,
                 ip_address: str = '127.0.0.1'):
        if zmq_port is None and window is None:
            raise ValueError('Must specify either zmq_port or window')
        if window is None:
            self.window = ViewerWindow(zmq_port, ip_address)
        else:
            self.window = window

    @staticmethod
    def view_into(window: ViewerWindow):
        """Returns a new viewer while keeping the same viewer window."""
        viewer = Viewer(window=window)

        return viewer

    def write(self, type: str, data: Union[Dict, str, None] = None):
        """write data to bridge server."""
        return self.window.send({'type': type, 'data': data})

    def read(self, type: str):
        """read data from bridge server."""
        res = self.window.send({'type': type})
        return res
