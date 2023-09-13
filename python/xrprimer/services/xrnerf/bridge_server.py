import atexit
import os
import signal
import socket
import subprocess
import sys
import threading
import time
from typing import Optional

# TODO: use import paths relative to `xrprimer` rather than the current parent
# TODO: directory to separate the entrypoint and libraries. Unfortunately, the
# TODO: xrprimer cannot be installed on a Windows machine. Need to be tested on
# TODO: MacOS later.
# import xrprimer.services.xrnerf.server as server
import server
from rich import print


def is_port_open(port: int):
    # check whether the given port is open
    try:
        sock = socket.socket()
        sock.bind(('', port))
        sock.close()

        return True
    except OSError:
        return False


def bind_port(target_port: Optional[int] = None) -> int:
    # the user specified a port
    if target_port:
        if is_port_open(target_port):
            return target_port

    # no port specified, returns an available port
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]

    return port


def start_bridge_server(
    websocket_port: int,
    zmq_port: Optional[int] = None,
    ip_address: str = '127.0.0.1',
):
    # run bridge server as a sub-process
    args = [sys.executable, '-u', '-m', server.__name__]

    # find an available port for zmq
    if zmq_port is None:
        zmq_port = bind_port(zmq_port)
        print(f'Using ZMQ port: {zmq_port}')

    args.append('--zmq-port')
    args.append(str(zmq_port))
    args.append('--websocket-port')
    args.append(str(websocket_port))
    args.append('--ip-address')
    args.append(str(ip_address))

    bridge_server_process = subprocess.Popen(args, start_new_session=True)

    def cleanup(process):
        process.kill()
        process.wait()

    def poll_process():
        """Continually check to see if the viewer bridge server process is
        still running and has not failed.

        If it fails, alert the user and exit the entire program.
        """
        while bridge_server_process.poll() is None:
            time.sleep(0.5)

        print('[bold red]'
              'The bridge server subprocess dumped.'
              '[/bold red]')
        cleanup(bridge_server_process)

        # windows system do not have signal.SIGKILL
        # TODO: make sure the kill operation still works on Linux systems
        # os.kill(os.getpid(), signal.SIGKILL)
        os.kill(os.getpid(), signal.SIGINT)

    watcher_thread = threading.Thread(target=poll_process)
    watcher_thread.daemon = True
    watcher_thread.start()
    # clean up process when it has shut down
    atexit.register(cleanup, bridge_server_process)

    return zmq_port
