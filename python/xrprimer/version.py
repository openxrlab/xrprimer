# Copyright (c) OpenXRLab. All rights reserved.
from xrprimer_cpp.common import (
    get_version_major,
    get_version_minor,
    get_version_patch,
    get_version_string,
)


def parse_version_info(version_str):
    """Parse a version string into a tuple.

    Args:
        version_str (str): The version string.
    Returns:
        tuple[int | str]: The version info, e.g., "1.3.0" is parsed into
            (1, 3, 0), and "2.0.0rc1" is parsed into (2, 0, 0, 'rc1').
    """
    version_info = []
    for x in version_str.split('.'):
        if x.isdigit():
            version_info.append(int(x))
        elif x.find('rc') != -1:
            patch_version = x.split('rc')
            version_info.append(int(patch_version[0]))
            version_info.append(f'rc{patch_version[1]}')
    return tuple(version_info)


__version__ = get_version_string()
version_info = (get_version_major(), get_version_minor(), get_version_patch())

__all__ = ['__version__', 'version_info', 'parse_version_info']
