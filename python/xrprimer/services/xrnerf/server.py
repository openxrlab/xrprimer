import pickle
from typing import Awaitable, List, Optional, Tuple

import tornado.gen
import tornado.ioloop
import tornado.web
import tornado.websocket
import umsgpack
import zmq
# TODO: use import paths relative to `xrprimer` rather than the current parent
# TODO: directory to separate the entrypoint and libraries. Unfortunately, the
# TODO: xrprimer cannot be installed on a Windows machine. Need to be tested on
# TODO: MacOS later.
# from xrprimer.services.xrnerf.actions import (
#     UPDATE_CAMERA_FOV,
#     UPDATE_CAMERA_ROTATION,
#     UPDATE_CAMERA_TRANSLATION,
#     UPDATE_RENDER_RESULT,
#     UPDATE_RENDER_TYPE,
#     UPDATE_RESOLUTION,
#     UPDATE_STATE,
# )
# from xrprimer.services.xrnerf.state import State
from actions import (
    UPDATE_CAMERA_FOV,
    UPDATE_CAMERA_ROTATION,
    UPDATE_CAMERA_TRANSLATION,
    UPDATE_RENDER_RESULT,
    UPDATE_RENDER_TYPE,
    UPDATE_RESOLUTION,
    UPDATE_STATE,
)
from rich import print
from state import State
from typer import Option, run
from zmq.eventloop.zmqstream import ZMQStream


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """For receiving and sending commands from/to the viewer."""

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def __init__(self, *args, **kwargs):
        self.bridge = kwargs.pop('bridge')
        super().__init__(*args, **kwargs)

    def check_origin(self, origin: str) -> bool:
        return True

    def open(self, *args: str, **kwargs: str):
        self.bridge.websocket_pool.add(self)
        print('[bold green]Viewer connected.[/bold green]')

    async def on_message(self, message: bytearray):
        """parses the message from viewer and calls the appropriate
        function."""
        unpacked_message = umsgpack.unpackb(message)

        type = unpacked_message['type']
        data = unpacked_message['data']

        if type == UPDATE_CAMERA_TRANSLATION:
            self.bridge.state.camera_translation = data
        elif type == UPDATE_CAMERA_ROTATION:
            self.bridge.state.camera_rotation = data
        elif type == UPDATE_RENDER_TYPE:
            self.bridge.state.render_type = data
        elif type == UPDATE_CAMERA_FOV:
            self.bridge.state.camera_fov = data
        elif type == UPDATE_RESOLUTION:
            self.bridge.state.resolution = data
        else:
            # TODO: handle exception
            pass

    def on_close(self) -> None:
        self.bridge.websocket_pool.remove(self)
        print('[bold red]Viewer disconnected.[/bold red]')


class ZMQWebSocketBridge:

    context = zmq.Context()  # pylint: disable=abstract-class-instantiated

    def __init__(self, zmq_port: int, websocket_port: int, ip_address: str):
        self.zmq_port = zmq_port
        self.websocket_pool = set()
        self.app = self.make_app()
        self.ioloop = tornado.ioloop.IOLoop.current()

        # zmq
        zmq_url = f'tcp://{ip_address}:{self.zmq_port:d}'
        self.zmq_socket, self.zmq_stream, self.zmq_url = \
            self.setup_zmq(zmq_url)

        # websocket
        listen_kwargs = {'address': '0.0.0.0'}
        self.app.listen(websocket_port, **listen_kwargs)
        self.websocket_port = websocket_port
        self.websocket_url = f'0.0.0.0:{self.websocket_port}'

        # state
        self.state = State()

    def make_app(self):
        return tornado.web.Application([(r'/', WebSocketHandler, {
            'bridge': self
        })])

    def handle_zmq(self, frames: List[bytes]):

        _type = frames[0].decode('utf-8')

        if _type == UPDATE_RENDER_RESULT:
            self.forward_to_websockets(frames)
            self.zmq_socket.send(umsgpack.packb(b'ok'))
        elif _type == UPDATE_STATE:
            serialized = pickle.dumps(self.state)
            self.zmq_socket.send(serialized)
        elif _type == 'ping':
            self.zmq_socket.send(umsgpack.packb(b'ping received'))
        else:
            print('type: ' + str(_type))
            self.zmq_socket.send(umsgpack.packb(b'error: unknown command'))

    def forward_to_websockets(
            self,
            frames: Tuple[str, str, bytes],
            websocket_to_skip: Optional[WebSocketHandler] = None):
        """forward a zmq message to all websockets."""
        """nerf backend -> viewer"""
        _type, _data = frames  # cmd, data
        for websocket in self.websocket_pool:
            if websocket_to_skip and websocket == websocket_to_skip:
                pass
            else:
                websocket.write_message(_data, binary=True)

    def setup_zmq(self, url: str):
        """setup a zmq socket and connect it to the given url."""
        zmq_socket = self.context.socket(zmq.REP)  # pylint: disable=no-member
        zmq_socket.bind(url)
        zmq_stream = ZMQStream(zmq_socket)
        zmq_stream.on_recv(self.handle_zmq)

        return zmq_socket, zmq_stream, url

    def run(self):
        """starts and runs the websocet bridge."""
        print(f'[bold blue]Start bridge server, '
              f'ZeroMQ port: {self.zmq_port}, '
              f'websocket port: {self.websocket_port}[/bold blue]')
        self.ioloop.start()


def run_bridge_server(
    zmq_port: int = 6000,
    websocket_port: int = 4567,
    ip_address: str = '127.0.0.1',
):
    bridge = ZMQWebSocketBridge(
        zmq_port=zmq_port,
        websocket_port=websocket_port,
        ip_address=ip_address)

    try:
        bridge.run()
    except KeyboardInterrupt:
        pass


def wrapper(zmq_port: int = Option(6000, exists=False),
            websocket_port: int = Option(4567, exists=False),
            ip_address: str = Option('127.0.0.1', exists=False)):
    run_bridge_server(
        zmq_port=zmq_port,
        websocket_port=websocket_port,
        ip_address=ip_address)


if __name__ == '__main__':
    run(wrapper)
