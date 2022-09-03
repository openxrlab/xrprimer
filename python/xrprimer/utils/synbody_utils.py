"""Utils for load annotations from OpenXDLab SynBody dataset.

Requirements:

```
pip install numpy imath openexr flow_vis
```
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple, Union

import flow_vis
import Imath
import OpenEXR
import numpy as np

PathLike = Union[str, Path]


class ExrReader:
    """Load `.exr` format file.
    """

    def __init__(self, exr_path: PathLike):
        File = OpenEXR.InputFile(str(exr_path))
        dw = File.header()['dataWindow']
        size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
        self.File = File
        self.size: Tuple[int, int] = size

    @staticmethod
    def float2int(array: np.ndarray) -> np.ndarray:
        array = np.round(array * 255)
        array = np.clip(array, 0, 255)
        return array.astype(np.uint8)

    @property
    def channels(self) -> List[str]:
        return self.File.header()['channels']

    def read_channel(self, channel: str) -> np.ndarray:
        ChannelType = self.File.header()['channels'][channel]
        if ChannelType == Imath.Channel(Imath.PixelType(Imath.PixelType.HALF)):
            PixType = Imath.PixelType(Imath.PixelType.HALF)
            dtype = np.float16
        elif ChannelType == Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT)):
            PixType = Imath.PixelType(Imath.PixelType.FLOAT)
            dtype = np.float32
        else:
            raise ValueError('please specify PixelType')

        img = np.frombuffer(self.File.channel(channel, PixType), dtype=dtype)
        img = np.reshape(img, (self.size[1], self.size[0])).astype(np.float32)
        return img

    def get_mask(self) -> np.ndarray:
        """Get mask in `.exr` format."""
        r = self.read_channel('R')
        g = self.read_channel('G')
        b = self.read_channel('B')
        img = np.stack((r, g, b), axis=2)
        img = self.float2int(img)
        return img

    def get_flow(self, bgr: bool = True) -> np.ndarray:
        """Get optical flow in `.exr` format."""
        flow_r = self.read_channel('R')
        flow_g = self.read_channel('G')
        flow = np.stack((flow_r, flow_g), axis=2)
        img = flow_vis.flow_to_color(flow, convert_to_bgr=bgr)
        return img

    def get_depth(self, depth_rescale: float = 1.0) -> np.ndarray:
        """Get depth in `.exr` format."""
        r = self.read_channel('R')
        g = self.read_channel('G')
        b = self.read_channel('B')
        depth = np.stack((r, g, b), axis=2)

        img = self.float2int(depth / depth_rescale)
        img[img == 0] = 255
        return img


class SeqDataReader:
    """Load 'seq_data.json' files, which contain sequences composition information.
    """
    def __init__(self, seq_data_path: PathLike) -> None:
        with open(seq_data_path, 'r') as f:
            seq_data = json.load(f)
        self.seq_data: Dict = seq_data

    def get_mask_colors(self):
        """Load seq_data.json, get mask colors (rgb).
        'seq_data.json'
        """
        masks_rgb = [
            np.array(value['mask_rgb_value']).astype(int).tolist()
            for value in self.seq_data['Actors']['CharacterActors'].values()
        ]
        return masks_rgb
