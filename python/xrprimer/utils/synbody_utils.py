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
import numpy as np

from ..io.exr_reader import ExrReader

PathLike = Union[str, Path]


class SynbodyExrReader(ExrReader):
    """Load `.exr` format file.
    """

    @staticmethod
    def float2int(array: np.ndarray) -> np.ndarray:
        """Convert float type data to uint8 that can be display as image."""
        array = np.round(array * 255)
        array = np.clip(array, 0, 255)
        return array.astype(np.uint8)

    def get_mask(self) -> np.ndarray:
        """Get mask in `.exr` format.

        Returns:
            np.ndarray: masks of shape (H, W, 3)
        """
        r = self.read_channel('R')
        g = self.read_channel('G')
        b = self.read_channel('B')
        img = np.stack((r, g, b), axis=2)
        img = self.float2int(img)
        return img

    def get_flow(self) -> np.ndarray:
        """Get optical flow in `.exr` format.

        Returns:
            np.ndarray: optical flow data of (H, W, 3) converted to colors
        """
        flow_r = self.read_channel('R')
        flow_g = self.read_channel('G')
        flow = np.stack((flow_r, flow_g), axis=2)
        img = flow_vis.flow_to_color(flow, convert_to_bgr=False)
        return img

    def get_depth(self, depth_rescale: float = 1.0) -> np.ndarray:
        """Get depth in `.exr` format.

        Args:
            depth_rescale (float, optional): scaling the depth to map it into (0, 255).
                Depth values great than `depth_rescale` will be clipped. Defaults to 1.0.

        Returns:
            np.ndarray: depth data of shape (H, W, 3)
        """
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
        """Load seq_data.json in SynBody dataset

        Args:
            seq_data_path (PathLike): Files are named: 'seq_data.json'
        """
        with open(seq_data_path, 'r') as f:
            seq_data = json.load(f)
        self.seq_data: Dict = seq_data

    def get_mask_colors(self) -> List[Tuple[int, int, int]]:
        """Get all actor models' segmentation mask colors (rgb) from the seq_data.

        Returns:
            List[Tuple[int, int, int]]: list of mask colors in (R, G, B)
        """
        masks_rgb = [
            tuple(np.array(value['mask_rgb_value']).astype(int).tolist())
            for value in self.seq_data['Actors']['CharacterActors'].values()
        ]
        return masks_rgb
