import base64
import pickle
import time
from typing import Optional, Tuple

import cv2
import numpy as np
import umsgpack
# TODO: use import paths relative to `xrprimer` rather than the current parent
# TODO: directory to separate the entrypoint and libraries. Unfortunately, the
# TODO: xrprimer cannot be installed on a Windows machine. Need to be tested on
# TODO: MacOS later.
# from xrprimer.services.xrnerf.actions import (
#   UPDATE_RENDER_RESULT,
#   UPDATE_STATE
# )
# from xrprimer.services.xrnerf.bridge_server import start_bridge_server
# from xrprimer.services.xrnerf.visualizer import Viewer
from actions import BackendActionsEnum
from bridge_server import start_bridge_server
from visualizer import Viewer


class ViewerState:

    def __init__(self,
                 websocket_port: int = 4567,
                 zmq_port: Optional[int] = None,
                 ip_address: str = '127.0.0.1'):
        # launch the bridge server
        zmq_port = start_bridge_server(
            websocket_port=websocket_port,
            zmq_port=zmq_port,
            ip_address=ip_address)
        websocket_url = f'ws://localhost:{websocket_port}'
        self.viewer_url = f'https://localhost/?websocket_url={websocket_url}'
        self.viewer = Viewer(zmq_port=zmq_port, ip_address=ip_address)
        self.state = None

    def update_scene(self) -> None:
        """update the scene using rendered results."""
        while True:
            serialized_state = umsgpack.unpackb(
                self.viewer.read(BackendActionsEnum.UPDATE_STATE))
            self.state = pickle.loads(serialized_state)
            self.render_image_in_viewer()

    def get_resolution(self) -> Tuple[int, int]:
        if str(self.state.resolution) == '480':
            return 720, 480
        elif str(self.state.resolution) == '720':
            return 1280, 720
        elif str(self.state.resolution) == '1080':
            return 1920, 1080
        else:
            print('invalid resolution')

    def render_image_in_viewer(self) -> None:
        """Draw an image using current camera configuration."""
        # fetch data from state
        camera_translation = np.array(self.state.camera_translation)
        camera_rotation = np.array(self.state.camera_rotation)
        camera_fov = self.state.camera_fov
        render_type = self.state.render_type
        camera_translation = np.round(camera_translation, 2)
        camera_rotation = np.round(camera_rotation, 2)
        # generate a fake image
        img = np.zeros((1080, 1920, 3), np.uint8)
        img.fill(230)
        font = cv2.FONT_HERSHEY_COMPLEX
        color = (10, 20, 20)
        cv2.putText(img, 'translation: ' + str(camera_translation), (10, 100),
                    font, 1, color, 1)
        cv2.putText(img, 'rotation: ' + str(camera_rotation), (10, 200), font,
                    1, color, 1)
        cv2.putText(img, 'fov: ' + str(camera_fov), (10, 300), font, 1, color,
                    1)
        cv2.putText(img, 'render type: ' + str(render_type), (10, 400), font,
                    1, color, 1)
        scaled_resolution = self.get_resolution()
        cv2.putText(
            img, f'resolution: {scaled_resolution[0]}x{scaled_resolution[1]}',
            (10, 500), font, 1, color, 1)
        scaled_image = cv2.resize(
            img, scaled_resolution, interpolation=cv2.INTER_AREA)

        image_format = 'jpeg'

        data = cv2.imencode(
            ext=f'.{image_format}',
            img=scaled_image,
            params=[cv2.IMWRITE_JPEG_QUALITY, 90])[1].tobytes()
        data = str(f'data:image/{image_format};base64,' +
                   base64.b64encode(data).decode('ascii'))
        self.viewer.write(BackendActionsEnum.UPDATE_RENDER_RESULT, data)
        """
        Let the renderer relief for some time
        to avoid websocket blocking
        """
        time.sleep(0.05)
