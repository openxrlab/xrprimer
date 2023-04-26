# yapf: disable
from collections import defaultdict
from typing import List, Union

import numpy as np

from xrprimer.data_structure.keypoints import Keypoints
from xrprimer.utils.log_utils import get_logger, logging
from . import (
    agora,
    campus,
    coco,
    coco_wholebody,
    crowdpose,
    face3d,
    flame,
    gta,
    h36m,
    human_data,
    hybrik,
    instavariety,
    lsp,
    mano,
    mediapipe,
    mpi_inf_3dhp,
    mpii,
    openpose,
    panoptic,
    penn_action,
    posetrack,
    pw3d,
    smpl,
    smplx,
    spin_smplx,
    star,
)

try:
    import torch
    has_torch = True
    import_exception = ''
except (ImportError, ModuleNotFoundError):
    has_torch = False
    import traceback
    stack_str = ''
    for line in traceback.format_stack():
        if 'frozen' not in line:
            stack_str += line + '\n'
    import_exception = traceback.format_exc() + '\n'
    import_exception = stack_str + import_exception

KEYPOINTS_FACTORY = {
    'human_data': human_data.HUMAN_DATA,
    'agora': agora.AGORA_KEYPOINTS,
    'campus': campus.CAMPUS_KEYPOINTS,
    'coco': coco.COCO_KEYPOINTS,
    'coco_wholebody': coco_wholebody.COCO_WHOLEBODY_KEYPOINTS,
    'crowdpose': crowdpose.CROWDPOSE_KEYPOINTS,
    'smplx': smplx.SMPLX_KEYPOINTS,
    'smpl': smpl.SMPL_KEYPOINTS,
    'smpl_45': smpl.SMPL_45_KEYPOINTS,
    'smpl_54': smpl.SMPL_54_KEYPOINTS,
    'smpl_49': smpl.SMPL_49_KEYPOINTS,
    'smpl_24': smpl.SMPL_24_KEYPOINTS,
    'star': star.STAR_KEYPOINTS,
    'mpi_inf_3dhp': mpi_inf_3dhp.MPI_INF_3DHP_KEYPOINTS,
    'mpi_inf_3dhp_test': mpi_inf_3dhp.MPI_INF_3DHP_TEST_KEYPOINTS,
    'penn_action': penn_action.PENN_ACTION_KEYPOINTS,
    'h36m': h36m.H36M_KEYPOINTS,
    'h36m_mmpose': h36m.H36M_KEYPOINTS_MMPOSE,
    'h36m_smplx': h36m.H36M_KEYPOINTS_SMPLX,
    'pw3d': pw3d.PW3D_KEYPOINTS,
    'mpii': mpii.MPII_KEYPOINTS,
    'lsp': lsp.LSP_KEYPOINTS,
    'posetrack': posetrack.POSETRACK_KEYPOINTS,
    'instavariety': instavariety.INSTAVARIETY_KEYPOINTS,
    'openpose_25': openpose.OPENPOSE_25_KEYPOINTS,
    'openpose_118': openpose.OPENPOSE_118_KEYPOINTS,
    'openpose_135': openpose.OPENPOSE_135_KEYPOINTS,
    'openpose_137': openpose.OPENPOSE_137_KEYPOINTS,
    'hybrik_29': hybrik.HYBRIK_29_KEYPOINTS,
    'hybrik_hp3d': mpi_inf_3dhp.HYBRIK_MPI_INF_3DHP_KEYPOINTS,
    'gta': gta.GTA_KEYPOINTS,
    'flame': flame.FLAME_73_KEYPOINTS,
    'face3d': face3d.FACE3D_IND,
    'spin_smplx': spin_smplx.SPIN_SMPLX_KEYPOINTS,
    'mano': mano.MANO_KEYPOINTS,
    'mano_left': mano.MANO_LEFT_KEYPOINTS,
    'mano_right': mano.MANO_RIGHT_KEYPOINTS,
    'mano_hands': mano.MANO_HANDS_KEYPOINTS,
    'mano_left_reorder': mano.MANO_LEFT_REORDER_KEYPOINTS,
    'mano_right_reorder': mano.MANO_RIGHT_REORDER_KEYPOINTS,
    'mano_hands_reorder': mano.MANO_HANDS_REORDER_KEYPOINTS,
    'mediapipe_whole_body': mediapipe.MP_WHOLE_BODY_KEYPOINTS,
    'mediapipe_body': mediapipe.MP_BODY_KEYPOINTS,
    'panoptic': panoptic.PANOPTIC_KEYPOINTS
}


_KEYPOINTS_MAPPING_CACHE = defaultdict(dict)


def get_keypoints_factory() -> dict:
    """Get the KEYPOINTS_FACTORY defined in keypoints convention.

    Returns:
        dict:
            KEYPOINTS_FACTORY whose keys are convention
            names and values are keypoints lists.
    """
    return KEYPOINTS_FACTORY


def get_keypoint_num(convention: str = 'smplx',
                     keypoints_factory: dict = KEYPOINTS_FACTORY) -> List[int]:
    """Get number of keypoints of specified convention.

    Args:
        convention (str): data type from keypoints_factory.
        keypoints_factory (dict, optional):
            A dict to store the attributes.
            Defaults to KEYPOINTS_FACTORY.
    Returns:
        List[int]: part keypoint indices
    """
    keypoints = keypoints_factory[convention]
    return len(keypoints)


def get_keypoint_idx(name: str,
                     convention: str = 'smplx',
                     approximate: bool = False,
                     keypoints_factory: dict = KEYPOINTS_FACTORY) -> List[int]:
    """Get keypoint index from specified convention with keypoint name.

    Args:
        name (str): keypoint name
        convention (str): data type from keypoints_factory.
        approximate (bool): control whether approximate mapping is allowed.
        keypoints_factory (dict, optional): A class to store the attributes.
            Defaults to keypoints_factory.
    Returns:
        List[int]: keypoint index
    """
    keypoints = keypoints_factory[convention]
    try:
        idx = keypoints.index(name)
    except ValueError:
        idx = -1  # not matched
    if approximate and idx == -1:
        try:
            part_list = human_data.APPROXIMATE_MAP[name]
        except KeyError:
            return idx
        for approximate_name in part_list:
            try:
                idx = keypoints.index(approximate_name)
            except ValueError:
                idx = -1
            if idx >= 0:
                return idx
    return idx


def get_mapping_dict(src: str,
                     dst: str,
                     approximate: bool = False,
                     keypoints_factory: dict = KEYPOINTS_FACTORY) -> dict:
    """Call get_mapping from mmhuman3d and make a dict mapping src index to dst
    index.

    Args:
        src (str):
            The name of source convention.
        dst (str):
            The name of destination convention.
        approximate (bool, optional):
            Whether approximate mapping is allowed.
            Defaults to False.
        keypoints_factory (dict, optional):
            A dict to store all the keypoint conventions.
            Defaults to KEYPOINTS_FACTORY.

    Returns:
        dict:
            A mapping dict whose keys are src indexes
            and values are dst indexes.
    """
    mapping_back = get_mapping(
        src=src,
        dst=dst,
        keypoints_factory=keypoints_factory,
        approximate=approximate)
    inter_to_dst, inter_to_src = mapping_back[:2]
    mapping_dict = {}
    for index in range(len(inter_to_dst)):
        mapping_dict[inter_to_src[index]] = inter_to_dst[index]
    return mapping_dict


def get_mapping(src: str,
                dst: str,
                approximate: bool = False,
                keypoints_factory: dict = KEYPOINTS_FACTORY,
                logger: Union[None, str, logging.Logger] = None):
    """Get mapping list from src to dst.

    Args:
        src (str): source data type from keypoints_factory.
        dst (str): destination data type from keypoints_factory.
        approximate (bool): control whether approximate mapping is allowed.
        keypoints_factory (dict, optional): A class to store the attributes.
            Defaults to keypoints_factory.

    Returns:
        list:
            [src_to_intersection_idx, dst_to_intersection_index,
             intersection_names]
    """
    if src in _KEYPOINTS_MAPPING_CACHE and \
        dst in _KEYPOINTS_MAPPING_CACHE[src] and \
            _KEYPOINTS_MAPPING_CACHE[src][dst][3] == approximate:
        return _KEYPOINTS_MAPPING_CACHE[src][dst][:3]
    else:
        src_names = keypoints_factory[src.lower()]
        dst_names = keypoints_factory[dst.lower()]

        dst_idxs, src_idxs, intersection = [], [], []
        unmapped_names, approximate_names = [], []
        for dst_idx, dst_name in enumerate(dst_names):
            matched = False
            try:
                src_idx = src_names.index(dst_name)
            except ValueError:
                src_idx = -1
            if src_idx >= 0:
                matched = True
                dst_idxs.append(dst_idx)
                src_idxs.append(src_idx)
                intersection.append(dst_name)
            # approximate mapping
            if approximate and not matched:

                try:
                    part_list = human_data.APPROXIMATE_MAP[dst_name]
                except KeyError:
                    continue
                for approximate_name in part_list:
                    try:
                        src_idx = src_names.index(approximate_name)
                    except ValueError:
                        src_idx = -1
                    if src_idx >= 0:
                        dst_idxs.append(dst_idx)
                        src_idxs.append(src_idx)
                        intersection.append(dst_name)
                        unmapped_names.append(src_names[src_idx])
                        approximate_names.append(dst_name)
                        break

        if unmapped_names:
            warn_message = \
                f'Approximate mapping {unmapped_names}' +\
                f' to {approximate_names}'
            logger = get_logger(logger)
            logger.warning(warn_message)

        mapping_list = [dst_idxs, src_idxs, intersection, approximate]

        if src not in _KEYPOINTS_MAPPING_CACHE:
            _KEYPOINTS_MAPPING_CACHE[src] = {}
        _KEYPOINTS_MAPPING_CACHE[src][dst] = mapping_list
        return mapping_list[:3]


def convert_keypoints(
    keypoints: Keypoints,
    dst: str,
    approximate: bool = False,
    keypoints_factory: dict = KEYPOINTS_FACTORY,
    logger: Union[None, str, logging.Logger] = None
) -> Keypoints:
    """Convert keypoints following the mapping correspondence between src and
    dst keypoints definition.

    Args:
        keypoints (Keypoints):
            An instance of Keypoints class.
        dst (str):
            The name of destination convention.
        approximate (bool, optional):
            Whether approximate mapping is allowed.
            Defaults to False.
        keypoints_factory (dict, optional):
            A dict to store all the keypoint conventions.
            Defaults to KEYPOINTS_FACTORY.

    Returns:
        Keypoints:
            An instance of Keypoints class, whose convention is dst,
            and dtype, device are same as input.
    """
    logger = get_logger(logger)
    src = keypoints.get_convention()
    src_arr = keypoints.get_keypoints()
    n_frame, n_person, kps_n, dim = src_arr.shape
    flat_arr = src_arr.reshape(-1, kps_n, dim)
    flat_mask = keypoints.get_mask().reshape(-1, kps_n)

    if not has_torch:
        logger.error(import_exception)
        raise ImportError
    if isinstance(src_arr, torch.Tensor):
        def new_array_func(shape, value, ref_data, if_uint8):
            if if_uint8:
                dtype = torch.uint8
            else:
                dtype = ref_data.dtype
            if value == 1:
                return torch.ones(
                    size=shape, dtype=dtype, device=ref_data.device)
            elif value == 0:
                return torch.zeros(
                    size=shape, dtype=dtype, device=ref_data.device)
            else:
                raise ValueError

    elif isinstance(src_arr, np.ndarray):

        def new_array_func(shape, value, ref_data, if_uint8):
            if if_uint8:
                dtype = np.uint8
            else:
                dtype = ref_data.dtype
            if value == 1:
                return np.ones(shape=shape)
            elif value == 0:
                return np.zeros(shape=shape, dtype=dtype)
            else:
                raise ValueError

    dst_n_kps = get_keypoint_num(
        convention=dst, keypoints_factory=keypoints_factory)
    dst_idxs, src_idxs, _ = \
        get_mapping(src, dst, approximate, keypoints_factory, logger=logger)
    # multi frame multi person kps
    dst_arr = new_array_func(
        shape=(n_frame * n_person, dst_n_kps, dim),
        value=0,
        ref_data=src_arr,
        if_uint8=False)
    # multi frame multi person mask
    dst_mask = new_array_func(
        shape=(n_frame * n_person, dst_n_kps),
        value=0,
        ref_data=src_arr,
        if_uint8=True)
    # mapping from source
    dst_mask[:, dst_idxs] = flat_mask[:, src_idxs]
    dst_arr[:, dst_idxs, :] = flat_arr[:, src_idxs, :]
    multi_mask = dst_mask.reshape(n_frame, n_person, dst_n_kps)
    multi_arr = dst_arr.reshape(n_frame, n_person, dst_n_kps, dim)
    ret_kps = Keypoints(
        dtype=keypoints.dtype,
        kps=multi_arr,
        mask=multi_mask,
        convention=dst,
        logger=keypoints.logger)
    return ret_kps


def get_keypoint_names(
        convention: str = 'smplx',
        keypoints_factory: dict = KEYPOINTS_FACTORY) -> List[str]:
    """Get names of keypoints of specified convention.

    Args:
        convention (str): data type from keypoints_factory.
        keypoints_factory (dict, optional): A class to store the attributes.
            Defaults to KEYPOINTS_FACTORY.
    Returns:
        List[str]: keypoint names
    """
    keypoints = keypoints_factory[convention]
    return keypoints
