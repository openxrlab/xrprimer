"""Utils for load annotations from OpenXDLab SynBody dataset.

Requirements:

```
pip install numpy imath openexr flow_vis opencv-python
```

If you encounter any problems with openexr installation,
refer to the following link:
https://github.com/AcademySoftwareFoundation/openexr/blob/main/INSTALL.md
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import cv2
import numpy as np
from scipy.spatial.transform import Rotation as spRotation

from ..data_structure.camera import PinholeCameraParameter
from ..io.exr_reader import ExrReader

try:
    import flow_vis
except ImportError:
    print('warning: please install flow_vis'
          ' in order to visualize optical flows.')

PathLike = Union[str, Path]


class SynbodyReader:
    """Load from SynBody dataset of one sequence.

    Provide utils to get data of various modalities.
    """
    # folder names of each data modal
    MASK = 'mask'
    DEPTH = 'depth'
    OPTICAL_FLOW = 'optical_flow'
    RGB = 'rgb'
    SMPLX = 'smplx'
    NORMAL = 'normal'

    def __init__(self, seq_data_path: PathLike) -> None:
        """Load seq_data.json in SynBody dataset.

        Args:
            seq_data_path (PathLike): Files are named: 'seq_data.json'
        """
        self.seq_data_reader = SeqDataReader(seq_data_path)
        self.sequence_dir = Path(seq_data_path).parent

    def get_mask_colors(self) -> List[Tuple[int, int, int]]:
        """Get all actor models' segmentation mask colors (rgb) from the
        seq_data.

        Returns:
            List[Tuple[int, int, int]]: list of mask colors in (R, G, B)
        """
        return self.seq_data_reader.get_mask_colors()

    def get_rgb(self, frame: int) -> np.ndarray:
        """Get rgb image of the given frame ('rgb/{frame:04d}.jpeg')

        Args:
            frame (int): the frame number (starts from 1)

        Returns:
            np.ndarray: image of shape (H, W, 3)
        """
        folder = self.sequence_dir / self.RGB
        if not folder.exists():
            raise ValueError(f'Folder of rgb images not found: {folder}')
        file_path = folder / f'{frame:04d}.jpeg'
        if not file_path.exists():
            raise ValueError(f'Image of {frame}-frame not found: {file_path}')
        img = cv2.imread(str(file_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    def get_mask(self, frame: int) -> np.ndarray:
        """Get mask of the given frame ('mask/{frame:04d}.exr')

        Args:
            frame (int): the frame number (starts from 1)

        Returns:
            np.ndarray: masks of shape (H, W, 3)
        """
        folder = self.sequence_dir / self.MASK
        if not folder.exists():
            raise ValueError(f'Folder of masks not found: {folder}')
        file_path = folder / f'{frame:04d}.exr'
        if not file_path.exists():
            raise ValueError(f'Mask of {frame}-frame not found: {file_path}')
        return SynbodyExrReader(file_path).get_mask()

    def get_depth(self, frame: int, depth_rescale=1.0) -> np.ndarray:
        """Get depth of the given frame ('depth/{frame:04d}.exr')

        Args:
            frame (int): the frame number (starts from 1)

        Returns:
            np.ndarray: depth of shape (H, W, 3)
        """
        folder = self.sequence_dir / self.DEPTH
        if not folder.exists():
            raise ValueError(f'Folder of depth not found: {folder}')
        file_path = folder / f'{frame:04d}.exr'
        if not file_path.exists():
            raise ValueError(f'Depth of {frame}-frame not found: {file_path}')
        return SynbodyExrReader(file_path).get_depth(
            depth_rescale=depth_rescale)

    def get_flow(self, frame: int):
        """Get optical flow of the given frame ('optical_flow/{frame:04d}.exr')

        Args:
            frame (int): the frame number (starts from 1)
            depth_rescale (float, optional): scaling the depth
                to map it into (0, 255). Depth values great than
                `depth_rescale` will be clipped. Defaults to 1.0.

        Returns:
            np.ndarray: optical flow of shape (H, W, 3)
        """
        folder = self.sequence_dir / self.OPTICAL_FLOW
        if not folder.exists():
            raise ValueError(f'Folder of depth not found: {folder}')
        file_path = folder / f'{frame:04d}.exr'
        if not file_path.exists():
            raise ValueError(f'Depth of {frame}-frame not found: {file_path}')
        return SynbodyExrReader(file_path).get_flow()

    def get_normal(self, frame: int) -> np.ndarray:
        """Get normal map of the given frame ('normal/{frame:04d}.png')

        Args:
            frame (int): the frame number (starts from 1)

        Returns:
            np.ndarray: normal map of shape (H, W, 3)
        """
        folder = self.sequence_dir / self.NORMAL
        if not folder.exists():
            raise ValueError(f'Folder of normal mpa not found: {folder}')
        file_path = folder / f'{frame:04d}.png'
        if not file_path.exists():
            raise ValueError(
                f'Normal map of {frame}-frame not found: {file_path}')
        img = cv2.imread(str(file_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    def get_smplx(self) -> List[Dict[str, np.ndarray]]:
        """Get smplx of actors in the sequence ('smplx/*.npz')

        Returns:
            List[Dict[str, np.ndarray]]: list of all actors' SMPL-X
                annotations. Keys included:

                    - transl: of shape (N, 3)
                    - global_orient: of shape (N, 3)
                    - betas: of shape (10,)
                    - body_pose: of shape (N, 63)
                    - left_hand_pose: of shape (N, 15)
                    - right_hand_pose: of shape (N, 15)
                    - jaw_pose: of shape (N, 3)
                    - leye_pose: of shape (N, 3)
                    - reye_pose: of shape (N, 3)
                    - expression: of shape (N, 10)

                (N is the number of frames + 1,
                    and the 0-th frame is at T-Pose for calibration.)
        """
        smplx = []
        for actor_data in self.seq_data_reader.get_actors():
            actor_transl = actor_data['transl']
            actor_rot = spRotation.from_rotvec(actor_data['global_orient'])
            humandata_smplx = np.load(actor_data['smplx'], allow_pickle=True)
            humandata_smplx = humandata_smplx['smplx'].item()
            # transform according to placement of the actor
            global_rot = spRotation.from_rotvec(
                humandata_smplx['global_orient'])
            global_rot = actor_rot * global_rot
            humandata_smplx['global_orient'] = global_rot.as_rotvec().astype(
                np.float32)
            transl = humandata_smplx['transl']
            transl = actor_rot.apply(transl - transl[0, :]) + transl[
                0, :] + actor_transl
            humandata_smplx['transl'] = transl

            smplx.append(humandata_smplx)
        return smplx

    def get_camera(self) -> PinholeCameraParameter:
        """Get camera parameter used in the sequence.

        Returns:
            PinholeCameraParameter: the camera parameter instance
        """
        return self.seq_data_reader.get_camera()


class SynbodyExrReader(ExrReader):
    """Load `.exr` format file."""

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
            depth_rescale (float, optional): scaling the depth
                to map it into (0, 255). Depth values great than
                `depth_rescale` will be clipped. Defaults to 1.0.

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
    """Load 'seq_data.json' files, which contain sequences composition
    information."""

    def __init__(self, seq_data_path: PathLike) -> None:
        """Load seq_data.json in SynBody dataset.

        Args:
            seq_data_path (PathLike): Files are named: 'seq_data.json'
        """
        with open(seq_data_path, 'r') as f:
            seq_data = json.load(f)
        self._seq_data: Dict = seq_data
        self._actors_data: Dict = seq_data['Actors']['CharacterActors']
        self._actors = None

    def get_actors(self) -> List[Dict[str, Any]]:
        """Get actors transformations.

        Returns:
            List[Dict[str, Union[str, np.ndarray, Tuple[int, int, int]]]]:
                List of actors information in the sequence. Keys included:
                    - name (str): name of the actor
                    - transl (np.ndarray): the actor's global translation
                        in the scene of shape (3,).
                    - global_orient (np.ndarray): the actor's global rotation
                        in the scene (of the axis angle form) of shape (3,).
                    - mask_rgb (Tuple[int, int, int]): the actor segmentation
                        mask's RGB values (0~255).
                    - smplx (str): filename of smplx annotation of the actor
                e.g.
                [
                    {
                        'name': 'rp_aneko_rigged_004_ue4',
                        'transl': np.array([100.0, -300.0, 400.0]),
                        'global_orient': np.array([0.0, 3.141592, 0.0]),
                        'mask_rgb': (153, 0, 120),
                        'smplx': 'rp_aneko_rigged_004_ue4-samba_dancing_1.npz',
                    }
                ]
        """
        if self._actors is None:
            actors = []
            for actor_key in sorted(self._actors_data.keys()):
                value = self._actors_data[actor_key]
                transl = np.array([
                    value['location'][1],
                    -value['location'][2],
                    value['location'][0],
                ]) / 100.0
                global_orient = spRotation.from_euler(
                    'zxy', value['rotation'], degrees=True).as_rotvec()
                mask_rgb = tuple(
                    np.array(value['mask_rgb_value']).astype(int).tolist())
                actors.append(
                    dict(
                        name=value['name'],
                        transl=transl,
                        global_orient=global_orient,
                        mask_rgb_value=mask_rgb,
                        smplx=value['smplx'],
                    ))
            self._actors = actors
        return self._actors

    def get_camera_KRT(
        self, resolution: Tuple[int, int] = (1280, 720)
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Get camera intrinsic matrix K, rotation matrix R, and translation T.
        R, T are defined to transform points from camera to world.

        Args:
            resolution (Tuple[int, int], optional):
                resolution of rgb images (W, H). Defaults to (1280, 720)

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]:
                respectively for K, R, T,
                    - K: intrinsic matrix of shape (3, 3),
                    - R: rotation matrix of shape (3, 3), from camera to world,
                    - T: translation of shape (3,), from camera to world.
        """
        camera_data = self._seq_data['Actors']['CameraActor']
        fov = camera_data['fov']
        w, h = resolution
        fx = fy = max(resolution) / 2 / np.tan(np.deg2rad(fov / 2))
        K = np.array([[fx, 0, w / 2], [0, fy, h / 2], [0, 0, 1]])
        # rotation convert from Unreal to opencv
        R = spRotation.from_euler(
            'zxy', camera_data['rotation'], degrees=True).as_matrix()
        # translation convert from Unreal to opencv with units scaling of 100.0
        T = np.array([
            camera_data['location'][1],
            -camera_data['location'][2],
            camera_data['location'][0],
        ]) / 100.0
        return K, R, T

    def get_camera(
        self, resolution: Tuple[int,
                                int] = (1280, 720)) -> PinholeCameraParameter:
        """Get camera parameter used in the sequence.

        Args:
            resolution (Tuple[int, int], optional):
                resolution of rgb images (W, H). Defaults to (1280, 720)

        Returns:
            PinholeCameraParameter: the camera parameter instance
        """
        K, R, T = self.get_camera_KRT(resolution=resolution)
        w, h = resolution
        return PinholeCameraParameter(
            K=K,
            R=R,
            T=T,
            name='SynBody',
            height=h,
            width=w,
            world2cam=False,
        )

    def get_mask_colors(self) -> List[Tuple[int, int, int]]:
        """Get all actor models' segmentation mask colors (rgb) from the
        seq_data.

        Returns:
            List[Tuple[int, int, int]]: list of mask colors in (R, G, B)
        """
        return [value['mask_rgb'] for value in self.get_actors()]

    def get_actor_names(self) -> List[str]:
        """Get names of all actor models in the sequence.

        Returns:
            List[str]: actor model names
        """
        return [value['name'] for value in self.get_actors()]

    def get_actor_smplx_filenames(self) -> List[str]:
        """Get filenames of smplx annotations of all actors in the sequence.

        Returns:
            List[str]: filenames of actors' smplx annotations.
        """
        return [value['smplx'] for value in self.get_actors()]
