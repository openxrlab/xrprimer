
"""Utils for exr format data.

Requirements:

```
pip install numpy imath openexr
```
"""
from pathlib import Path
from typing import List, Tuple, Union

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

    @property
    def channels(self) -> List[str]:
        """Get channels in the exr file.

        Returns:
            List[str]: list of channel names
        """
        return self.File.header()['channels']

    def read_channel(self, channel: str) -> np.ndarray:
        """Read channel's data.

        Args:
            channel (str): channel's name

        Returns:
            np.ndarray: channel's data in np.ndarray format with shape (H, W)
        """
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
