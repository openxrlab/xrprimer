"""Utils for exr format data.

Requirements: requirements/synbody.txt

If you encounter any problems with openexr installation,
refer to the following link:
https://github.com/AcademySoftwareFoundation/openexr/blob/main/INSTALL.md
"""
from pathlib import Path
from typing import List, Tuple, Union

import numpy as np

try:
    import Imath
    import OpenEXR
    has_exr = True
    import_exception = ''
except (ImportError, ModuleNotFoundError):
    has_exr = False
    import traceback
    stack_str = ''
    for line in traceback.format_stack():
        if 'frozen' not in line:
            stack_str += line + '\n'
    import_exception = traceback.format_exc() + '\n'
    import_exception = stack_str + import_exception


class ExrReader:
    """Load `.exr` format file."""

    def __init__(self, exr_path: Union[str, Path]):
        """Initialize with a `.exr` format file.

        Args:
            exr_path (PathLike): path to `.exr` format file
        """
        if not has_exr:
            print(import_exception)
            print('warning: please install Imath and OpenEXR'
                  ' in order to read .exr format files.')
            raise ImportError
        file_ = OpenEXR.InputFile(str(exr_path))
        dw = file_.header()['dataWindow']
        size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
        self.file = file_
        self.size: Tuple[int, int] = size

    @property
    def channels(self) -> List[str]:
        """Get channels in the exr file.

        Returns:
            List[str]: list of channel names
        """
        return self.file.header()['channels']

    def read_channel(self, channel: str) -> np.ndarray:
        """Read channel's data.

        Args:
            channel (str): channel's name

        Returns:
            np.ndarray: channel's data in np.ndarray format with shape (H, W)
        """
        ChannelType = self.file.header()['channels'][channel]
        if ChannelType == Imath.Channel(Imath.PixelType(Imath.PixelType.HALF)):
            PixType = Imath.PixelType(Imath.PixelType.HALF)
            dtype = np.float16
        elif ChannelType == Imath.Channel(
                Imath.PixelType(Imath.PixelType.FLOAT)):
            PixType = Imath.PixelType(Imath.PixelType.FLOAT)
            dtype = np.float32
        else:
            raise ValueError('please specify PixelType')

        img = np.frombuffer(self.file.channel(channel, PixType), dtype=dtype)
        img = np.reshape(img, (self.size[1], self.size[0])).astype(np.float32)
        return img
