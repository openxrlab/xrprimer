# yapf: disable
import glob
import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Tuple, Union

import numpy as np

from .log_utils import get_logger
from .path_utils import (
    Existence,
    check_path,
    check_path_suffix,
    prepare_output_path,
)

# yapf: enable


class VideoInfoReader():
    INFO_KEYS = [
        'index', 'codec_name', 'codec_long_name', 'profile', 'codec_type',
        'codec_time_base', 'codec_tag_string', 'codec_tag', 'width', 'height',
        'coded_width', 'coded_height', 'has_b_frames', 'pix_fmt', 'level',
        'chroma_location', 'refs', 'is_avc', 'nal_length_size', 'r_frame_rate',
        'avg_frame_rate', 'time_base', 'start_pts', 'start_time',
        'duration_ts', 'duration', 'bit_rate', 'bits_per_raw_sample',
        'nb_frames', 'disposition', 'tags'
    ]

    def __init__(self,
                 input_path: str,
                 logger: Union[None, str, logging.Logger] = None) -> None:
        """Get video information from video, mimiced from ffmpeg-python.
        https://github.com/kkroening/ffmpeg-python.

        Args:
            vid_file (str): Path to the video file.
            logger (Union[None, str, logging.Logger], optional):
                Logger for logging. If None, root logger will be selected.
                Defaults to None.

        Raises:
            FileNotFoundError: check the input path.

        Returns:
            None.
        """
        self.logger = get_logger(logger)
        check_path(
            input_path=input_path,
            allowed_existence=[Existence.FileExist],
            allowed_suffix=[
                '.mp4', '.mkv', '.avi', '.gif', '.png', '.jpg', '.jpeg'
            ],
            path_type='file',
            logger=logger)
        cmd = [
            'ffprobe', '-show_format', '-show_streams', '-of', 'json',
            input_path
        ]
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, _ = process.communicate()
        probe = json.loads(out.decode('utf-8'))
        video_stream = next((stream for stream in probe['streams']
                             if stream['codec_type'] == 'video'), None)
        if video_stream is None:
            self.logger.error('No video stream found')
            raise ValueError
        self.video_stream = video_stream

    def __getitem__(self, key: str) -> Any:
        """Get the corresponding information according to the key.

        Args:
            key (str):
                A key in VideoInfoReader.INFO_KEYS
                Such as codec_name, pix_fmt, duration, etc.

        Raises:
            KeyError: key cannot be found in VideoInfoReader.INFO_KEYS

        Returns:
            Any: The expected information.
        """
        if key not in self.__class__.INFO_KEYS:
            self.logger.error(
                'Wronge vid info key.' +
                f'Select one key from {self.__class__.INFO_KEYS}')
            raise KeyError
        return self.video_stream[key]


class VideoReader:
    """VideoReader for reading video frames as an image ndarray for OpenCV.

    It opens a PIPE from ffmpeg command and reads one frame per call, friendly
    for poor RAM devices.
    """

    def __init__(self,
                 input_path: str,
                 resolution: Union[Tuple[int, int], Tuple[float,
                                                          float]] = None,
                 start: int = 0,
                 end: int = None,
                 disable_log: bool = False,
                 logger: Union[None, str, logging.Logger] = None) -> None:
        """
        Args:
            input_path (str): Input path.
            resolution (Union[Tuple[int, int], Tuple[float, float]],
                    optional):
                Resolution(height, width) of output.
                Defaults to None.
            start (int, optional):
                Start frame index. Inclusive.
                If < 0, will be converted to frame_index range in [0, n_frame].
                Defaults to 0.
            end (int, optional):
                End frame index. Exclusive.
                Could be positive int or negative int or None.
                If None, all frames from start till the last
                frame are included.
                Defaults to None.
            disable_log (bool, optional):
                Whether close the ffmepg command info.
                Defaults to False.
            logger (Union[None, str, logging.Logger], optional):
                Logger for logging. If None, root logger will be selected.
                Defaults to None.

        Raises:
            BrokenPipeError: No buffer received from ffmpeg.
        """
        self.logger = get_logger(logger)
        info = VideoInfoReader(input_path, logger=logger)
        if resolution:
            self.height, self.width = resolution
        else:
            self.width, self.height = int(info['width']), int(info['height'])
        n_frames = int(info['nb_frames'])
        start = min(max(0, start), n_frames - 1)
        end = (min(end, n_frames - 1) + n_frames) % n_frames \
            if end is not None \
            else n_frames
        command = [
            'ffmpeg',
            '-i',
            input_path,
            '-filter_complex',
            f'[0]trim=start_frame={start}:end_frame={end}[v0]',
            '-map',
            '[v0]',
            '-pix_fmt',
            'bgr24',  # bgr24 for matching OpenCV
            '-s',
            f'{int(self.width)}x{int(self.height)}',
            '-f',
            'image2pipe',
            '-vcodec',
            'rawvideo',
            '-loglevel',
            'error',
            'pipe:'
        ]
        if not disable_log:
            self.logger.info(f'Running \"{" ".join(command)}\"')
        # Execute FFmpeg as sub-process with stdout as a pipe
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, bufsize=10**8)
        if process.stdout is None:
            self.logger.error('No buffer received.')
            raise BrokenPipeError
        self.process = process
        self.start = start
        self.end = end

    def get_next_frame(self) -> np.ndarray:
        """Read the next frame as opencv image, from the opened video file.

        Args:
            image_array (np.ndarray):
                An array of a single image, in shape
                [H, W, C].
        """
        # Read decoded video frame (in raw video format) from stdout process.
        buffer = self.process.stdout.read(int(self.width * self.height * 3))
        # Return None if buffer length is not W*H*3\
        # (when FFmpeg streaming ends).
        if len(buffer) != self.width * self.height * 3:
            return None
        img = np.frombuffer(buffer, np.uint8).reshape(self.height, self.width,
                                                      3)
        return img

    def __del__(self) -> None:
        self.process.stdout.close()
        self.process.wait()

    def close(self) -> None:
        """Manually close this video writer."""
        self.__del__()


class VideoWriter:
    """VideoWriter for writing OpenCV image array to a video file.

    It opens a PIPE from ffmpeg command and writes one frame per call, friendly
    for poor RAM devices.
    """

    def __init__(self,
                 output_path: str,
                 resolution: Tuple[int, int],
                 fps: float = 30.0,
                 n_frames: int = 1e9,
                 disable_log: bool = False,
                 logger: Union[None, str, logging.Logger] = None) -> None:
        """Write video file by ffmpeg.

        Args:
            output_path (str):
                Path to the output video file, which shall end with '.mp4'.
            resolution (List[int, int]):
                Resolution of the video, [height, width].
            fps (float, optional):
                Frame per second. Defaults to 30.0.
            n_frames (int, optional):
                Limit number of frames in this video.
                Defaults to 1e9.
            disable_log (bool, optional):
                Whether to disable logs of info level.
                Defaults to False.
            logger (Union[None, str, logging.Logger], optional):
                Logger for logging. If None, root logger will be selected.
                Defaults to None.

        Raises:
            BrokenPipeError: No buffer received.
        """
        self.logger = get_logger(logger)
        prepare_output_path(
            output_path,
            allowed_suffix=['.mp4'],
            tag='output video',
            path_type='file',
            overwrite=True)
        height, width = resolution
        width += width % 2
        height += height % 2
        command = [
            'ffmpeg',
            '-y',  # (optional) overwrite output file if it exists
            '-f',
            'rawvideo',
            '-pix_fmt',
            'bgr24',
            '-s',
            f'{int(width)}x{int(height)}',
            '-r',
            f'{fps}',  # frames per second
            '-loglevel',
            'error',
            '-threads',
            '1',
            '-i',
            '-',  # The input comes from a pipe
            '-vcodec',
            'libx264',
            '-r',
            f'{fps}',  # frames per second
            '-an',  # Tells FFMPEG not to expect any audio
            output_path,
        ]
        if not disable_log:
            self.logger.info(f'Running \"{" ".join(command)}\"')
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if process.stdin is None or process.stderr is None:
            self.logger.error('No buffer received.')
            raise BrokenPipeError
        self.process = process
        self.n_frames = n_frames
        self.len = 0

    def write(self, image_array: np.ndarray):
        """Write an image to the video file.

        Args:
            image_array (np.ndarray):
                An array of a single image, in shape
                [H, W, C].
        """
        if self.len < self.n_frames:
            try:
                self.process.stdin.write(image_array.tobytes())
                self.len += 1
            except KeyboardInterrupt:
                self.__del__()
        if self.len >= self.n_frames:
            self.__del__()

    def __del__(self):
        self.process.stdin.close()
        self.process.stderr.close()
        self.process.wait()

    def close(self):
        """Manually close this video writer."""
        self.__del__()


def pad_for_libx264(image_array: np.ndarray) -> np.ndarray:
    """Pad zeros if width or height of image_array is not divisible by 2.
    Otherwise you will get.

    \"[libx264 @ 0x1b1d560] width not divisible by 2 \"

    Args:
        image_array (np.ndarray):
            Image or images load by cv2.imread().
            Possible shapes:
            1. [height, width]
            2. [height, width, channels]
            3. [images, height, width]
            4. [images, height, width, channels]

    Returns:
        np.ndarray:
            A image with both edges divisible by 2.
    """
    if image_array.ndim == 2 or \
            (image_array.ndim == 3 and image_array.shape[2] == 3):
        hei_index = 0
        wid_index = 1
    elif image_array.ndim == 4 or \
            (image_array.ndim == 3 and image_array.shape[2] != 3):
        hei_index = 1
        wid_index = 2
    else:
        return image_array
    hei_pad = image_array.shape[hei_index] % 2
    wid_pad = image_array.shape[wid_index] % 2
    if hei_pad + wid_pad > 0:
        pad_width = []
        for dim_index in range(image_array.ndim):
            if dim_index == hei_index:
                pad_width.append((0, hei_pad))
            elif dim_index == wid_index:
                pad_width.append((0, wid_pad))
            else:
                pad_width.append((0, 0))
        values = 0
        image_array = \
            np.pad(image_array,
                   pad_width,
                   mode='constant', constant_values=values)
    return image_array


def video_to_array(
        input_path: str,
        resolution: Union[Tuple[int, int], Tuple[float, float]] = None,
        start: int = 0,
        end: int = None,
        disable_log: bool = False,
        logger: Union[None, str, logging.Logger] = None) -> np.ndarray:
    """Read a video/gif as an array of (f * h * w * 3).

    Args:
        input_path (str): input path.
        resolution (Union[Tuple[int, int], Tuple[float, float]], optional):
            resolution(height, width) of output. Defaults to None.
        start (int, optional): start frame index. Inclusive.
            If < 0, will be converted to frame_index range in [0, n_frame].
            Defaults to 0.
        end (int, optional): end frame index. Exclusive.
            Could be positive int or negative int or None.
            If None, all frames from start till the last frame are included.
            Defaults to None.
        disable_log (bool, optional): whether close the ffmepg command info.
            Defaults to False.
        logger (Union[None, str, logging.Logger], optional):
            Logger for logging. If None, root logger will be selected.
            Defaults to None.

    Raises:
        FileNotFoundError: check the input path.

    Returns:
        np.ndarray: shape will be (f * h * w * 3).
    """
    info = VideoInfoReader(input_path, logger=logger)
    if resolution:
        height, width = resolution
    else:
        width, height = int(info['width']), int(info['height'])
    n_frames = int(info['nb_frames'])
    start = max(start, 0) % (n_frames + 1)
    end = min(end, n_frames) % (n_frames + 1) if end is not None else n_frames
    command = [
        'ffmpeg',
        '-i',
        input_path,
        '-filter_complex',
        f'[0]trim=start_frame={start}:end_frame={end}[v0]',
        '-map',
        '[v0]',
        '-pix_fmt',
        'bgr24',  # bgr24 for matching OpenCV
        '-s',
        f'{int(width)}x{int(height)}',
        '-f',
        'image2pipe',
        '-vcodec',
        'rawvideo',
        '-loglevel',
        'error',
        'pipe:'
    ]
    if not disable_log:
        logger = get_logger(logger)
        logger.info(f'Running \"{" ".join(command)}\"')
    # Execute FFmpeg as sub-process with stdout as a pipe
    process = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)
    if process.stdout is None:
        raise BrokenPipeError('No buffer received.')
    # Read decoded video frames from the PIPE until no more frames to read
    array = []
    while True:
        # Read decoded video frame (in raw video format) from stdout process.
        buffer = process.stdout.read(int(width * height * 3))
        # Break the loop if buffer length is not W*H*3\
        # (when FFmpeg streaming ends).
        if len(buffer) != width * height * 3:
            break
        img = np.frombuffer(buffer, np.uint8).reshape(height, width, 3)
        array.append(img[np.newaxis])
    process.stdout.flush()
    process.stdout.close()
    process.wait()
    return np.concatenate(array)


def images_to_array_opencv(
        input_folder: str,
        resolution: Union[Tuple[int, int], Tuple[float, float]] = None,
        img_format: Union[str, None] = None,
        start: int = 0,
        end: int = None,
        logger: Union[None, str, logging.Logger] = None) -> np.ndarray:
    """Read a folder of images as an array of (f * h * w * 3).

    Args:
        input_folder (str): folder of input images.
        resolution (Union[Tuple[int, int], Tuple[float, float]]):
            resolution(height, width) of output. Defaults to None.
        img_format (str, optional):
            Format of images to be read, 'jpg' or 'png'.
            Defaults to None.
        start (int, optional): start frame index. Inclusive.
            If < 0, will be converted to frame_index range in [0, n_frame].
            Defaults to 0.
        end (int, optional): end frame index. Exclusive.
            Could be positive int or negative int or None.
            If None, all frames from start till the last frame are included.
            Defaults to None.
        logger (Union[None, str, logging.Logger], optional):
            Logger for logging. If None, root logger will be selected.
            Defaults to None.
    Raises:
        FileNotFoundError: check the input path.

    Returns:
        np.ndarray: shape will be (f * h * w * 3).
    """
    import cv2

    check_path(
        input_path=input_folder,
        allowed_existence=[Existence.DirectoryExistNotEmpty],
        allowed_suffix=[''],
        path_type='dir',
        logger=logger)
    if img_format is None:
        frame_list = []
        frame_names = sorted(os.listdir(input_folder))
        for name in frame_names:
            abs_path = os.path.join(input_folder, name)
            if check_path_suffix(abs_path, ['.jpg', '.jpeg', '.png']):
                frame_list.append(abs_path)
    else:
        frame_list = sorted(
            glob.glob(os.path.join(input_folder, f'*.{img_format}')))
    if end is None:
        frame_list = frame_list[start:]
    else:
        frame_list = frame_list[start:end]
    array_list = []
    for index, frame_path in enumerate(frame_list):
        img = cv2.imread(frame_path)
        if index == 0 and resolution is None:
            resolution = img.shape[0:2]
        else:
            img = cv2.resize(img, (resolution[1], resolution[0]))
        array_list.append(img)
    return np.asarray(array_list)


def images_to_array(
        input_folder: str,
        resolution: Union[Tuple[int, int], Tuple[float, float]] = None,
        img_format: str = '%06d.png',
        start: int = 0,
        end: int = None,
        remove_raw_files: bool = False,
        disable_log: bool = False,
        logger: Union[None, str, logging.Logger] = None) -> np.ndarray:
    """Read a folder of images as an array of (f * h * w * 3).

    Args:
        input_folder (str): folder of input images.
        resolution (Union[Tuple[int, int], Tuple[float, float]]):
            resolution(height, width) of output. Defaults to None.
        img_format (str, optional): format of images to be read.
            Defaults to '%06d.png'.
        start (int, optional): start frame index. Inclusive.
            If < 0, will be converted to frame_index range in [0, n_frame].
            Defaults to 0.
        end (int, optional): end frame index. Exclusive.
            Could be positive int or negative int or None.
            If None, all frames from start till the last frame are included.
            Defaults to None.
        remove_raw_files (bool, optional): whether remove raw images.
            Defaults to False.
        disable_log (bool, optional): whether close the ffmepg command info.
            Defaults to False.
    Raises:
        FileNotFoundError: check the input path.

    Returns:
        np.ndarray: shape will be (f * h * w * 3).
    """
    check_path(
        input_path=input_folder,
        allowed_existence=[Existence.DirectoryExistNotEmpty],
        allowed_suffix=[''],
        path_type='dir',
        logger=logger)

    input_folder_info = Path(input_folder)

    temp_input_folder = None
    if img_format is None:
        temp_input_folder = os.path.join(input_folder_info.parent,
                                         input_folder_info.name + '_temp')
        img_format = images_to_sorted_images(
            input_folder=input_folder, output_folder=temp_input_folder)
        input_folder = temp_input_folder

    info = VideoInfoReader(f'{input_folder}/{img_format}' % start)
    width, height = int(info['width']), int(info['height'])
    if resolution:
        height, width = resolution
    else:
        width, height = int(info['width']), int(info['height'])

    n_frames = len(os.listdir(input_folder))
    start = max(start, 0) % (n_frames + 1)
    end = min(end, n_frames) % (n_frames + 1) \
        if end is not None else n_frames
    command = [
        'ffmpeg',
        '-y',
        '-threads',
        '1',
        '-start_number',
        f'{start}',
        '-i',
        f'{input_folder}/{img_format}',
        '-frames:v',
        f'{end - start}',
        '-f',
        'rawvideo',
        '-pix_fmt',
        'bgr24',  # bgr24 for matching OpenCV
        '-s',
        f'{int(width)}x{int(height)}',
        '-loglevel',
        'error',
        '-'
    ]
    if not disable_log:
        logger = get_logger(logger)
        logger.info(f'Running \"{" ".join(command)}\"')
    process = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)
    if process.stdout is None:
        raise BrokenPipeError('No buffer received.')
    # Read decoded video frames from the PIPE until no more frames to read
    array = []
    while True:
        # Read decoded video frame (in raw video format) from stdout process.
        buffer = process.stdout.read(int(width * height * 3))
        # Break the loop if buffer length is not W*H*3\
        # (when FFmpeg streaming ends).

        if len(buffer) != width * height * 3:
            break
        img = np.frombuffer(buffer, np.uint8).reshape(height, width, 3)
        array.append(img[np.newaxis])
    process.stdout.flush()
    process.stdout.close()
    process.wait()
    if temp_input_folder is not None and\
            os.path.isdir(temp_input_folder):
        shutil.rmtree(temp_input_folder)
    if remove_raw_files and\
            os.path.isdir(input_folder):
        shutil.rmtree(input_folder)

    return np.concatenate(array)


def images_to_sorted_images(input_folder, output_folder, img_format='%06d'):
    """Copy and rename a folder of images into a new folder following the
    `img_format`.

    Args:
        input_folder (str): input folder.
        output_folder (str): output folder.
        img_format (str, optional): image format name, do not need extension.
            Defaults to '%06d'.

    Returns:
        str: image format of the rename images.
    """
    img_format = img_format.rsplit('.', 1)[0]
    file_list = []
    os.makedirs(output_folder, exist_ok=True)
    pngs = glob.glob(os.path.join(input_folder, '*.png'))
    if pngs:
        ext = 'png'
    file_list.extend(pngs)
    jpgs = glob.glob(os.path.join(input_folder, '*.jpg'))
    if jpgs:
        ext = 'jpg'
    file_list.extend(jpgs)
    file_list.sort()
    for index, file_name in enumerate(file_list):
        shutil.copy(
            file_name,
            os.path.join(output_folder, (img_format + '.%s') % (index, ext)))
    return img_format + '.%s' % ext


def array_to_video(image_array: np.ndarray,
                   output_path: str,
                   fps: Union[int, float] = 30,
                   resolution: Union[Tuple[int, int], Tuple[float,
                                                            float]] = None,
                   disable_log: bool = False,
                   logger: Union[None, str, logging.Logger] = None) -> None:
    """Convert an array to a video directly, gif not supported.

    Args:
        image_array (np.ndarray): shape should be (f * h * w * 3).
        output_path (str): output video file path.
        fps (Union[int, float, optional): fps. Defaults to 30.
        resolution (Optional[Union[Tuple[int, int], Tuple[float, float]]], \
            optional): (height, width) of the output video. Defaults to None.
        disable_log (bool, optional): whether close the ffmepg command info.
            Defaults to False.

    Raises:
        FileNotFoundError: check output path.
        TypeError: check input array.

    Returns:
        None.
    """
    if not isinstance(image_array, np.ndarray):
        raise TypeError('Input should be np.ndarray.')
    assert image_array.ndim == 4
    assert image_array.shape[-1] == 3
    prepare_output_path(
        output_path,
        allowed_suffix=['.mp4'],
        tag='output video',
        path_type='file',
        overwrite=True,
        logger=logger)
    if resolution:
        height, width = resolution
        width += width % 2
        height += height % 2
    else:
        image_array = pad_for_libx264(image_array)
        height, width = image_array.shape[1], image_array.shape[2]
    command = [
        'ffmpeg',
        '-y',  # (optional) overwrite output file if it exists
        '-f',
        'rawvideo',
        '-s',
        f'{int(width)}x{int(height)}',  # size of one frame
        '-pix_fmt',
        'bgr24',
        '-r',
        f'{fps}',  # frames per second
        '-loglevel',
        'error',
        '-threads',
        '4',
        '-i',
        '-',  # The input comes from a pipe
        '-vcodec',
        'libx264',
        '-an',  # Tells FFMPEG not to expect any audio
        output_path,
    ]
    if not disable_log:
        logger = get_logger(logger)
        logger.info(f'Running \"{" ".join(command)}\"')
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.stdin is None or process.stderr is None:
        raise BrokenPipeError('No buffer received.')
    index = 0
    while True:
        if index >= image_array.shape[0]:
            break
        process.stdin.write(image_array[index].tobytes())
        index += 1
    process.stdin.close()
    process.stderr.close()
    process.wait()


def array_to_images(image_array: np.ndarray,
                    output_folder: str,
                    img_format: str = '%06d.png',
                    resolution: Union[Tuple[int, int], Tuple[float,
                                                             float]] = None,
                    disable_log: bool = False,
                    logger: Union[None, str, logging.Logger] = None) -> None:
    """Convert an array to images directly.

    Args:
        image_array (np.ndarray): shape should be (f * h * w * 3).
        output_folder (str): output folder for the images.
        img_format (str, optional): format of the images.
            Defaults to '%06d.png'.
        resolution (Optional[Union[Tuple[int, int], Tuple[float, float]]], \
            optional): (height, width) of the output images. Defaults to None.
        disable_log (bool, optional): whether close the ffmepg command info.
            Defaults to False.

    Raises:
        FileNotFoundError: check output folder.
        TypeError: check input array.

    Returns:
        None
    """
    logger = get_logger(logger)
    prepare_output_path(
        output_folder,
        allowed_suffix=[],
        tag='output image folder',
        path_type='dir',
        overwrite=True)

    if not isinstance(image_array, np.ndarray):
        raise TypeError('Input should be np.ndarray.')
    assert image_array.ndim == 4
    assert image_array.shape[-1] == 3
    if resolution:
        height, width = resolution
        logger.error('Resolution not correctly implemented.')
        raise NotImplementedError
    else:
        height, width = image_array.shape[1], image_array.shape[2]
    command = [
        'ffmpeg',
        '-y',  # (optional) overwrite output file if it exists
        '-f',
        'rawvideo',
        '-s',
        f'{int(width)}x{int(height)}',  # size of one frame
        '-pix_fmt',
        'bgr24',  # bgr24 for matching OpenCV
        '-loglevel',
        'error',
        '-threads',
        '4',
        '-i',
        '-',  # The input comes from a pipe
        '-f',
        'image2',
        '-start_number',
        '0',
        os.path.join(output_folder, img_format),
    ]
    if not disable_log:
        logger = get_logger(logger)
        logger.info(f'Running \"{" ".join(command)}\"')
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=10**8,
        close_fds=True)
    if process.stdin is None or process.stderr is None:
        raise BrokenPipeError('No buffer received.')
    index = 0
    while True:
        if index >= image_array.shape[0]:
            break
        process.stdin.write(image_array[index].tobytes())
        index += 1
    process.stdin.close()
    process.stderr.close()
    process.wait()


def images_to_video(input_folder: str,
                    output_path: str,
                    remove_raw_file: bool = False,
                    img_format: str = '%06d.png',
                    fps: Union[int, float] = 30,
                    resolution: Union[Tuple[int, int], Tuple[float,
                                                             float]] = None,
                    start: int = 0,
                    end: int = None,
                    disable_log: bool = False,
                    logger: Union[None, str, logging.Logger] = None) -> None:
    """Convert a folder of images to a video.

    Args:
        input_folder (str): input image folder
        output_path (str): output video file path
        remove_raw_file (bool, optional): whether remove raw images.
            Defaults to False.
        img_format (str, optional): format to name the images].
            Defaults to '%06d.png'.
        fps (Union[int, float], optional): output video fps. Defaults to 30.
        resolution (Optional[Union[Tuple[int, int], Tuple[float, float]]],
            optional): (height, width) of output.
            defaults to None.
        start (int, optional): start frame index. Inclusive.
            If < 0, will be converted to frame_index range in [0, frame_num].
            Defaults to 0.
        end (int, optional): end frame index. Exclusive.
            Could be positive int or negative int or None.
            If None, all frames from start till the last frame are included.
            Defaults to None.
        disable_log (bool, optional): whether close the ffmepg command info.
            Defaults to False.
    Raises:
        FileNotFoundError: check the input path.
        FileNotFoundError: check the output path.
    Returns:
        None
    """
    logger = get_logger(logger)
    check_path(
        input_path=input_folder,
        allowed_existence=[Existence.DirectoryExistNotEmpty],
        allowed_suffix=[''],
        path_type='dir',
        logger=logger)
    prepare_output_path(
        output_path,
        allowed_suffix=['.mp4'],
        tag='output video',
        path_type='file',
        overwrite=True,
        logger=logger)
    n_frames = len(os.listdir(input_folder))
    start = max(start, 0) % (n_frames + 1)
    end = min(end, n_frames) % (n_frames + 1) \
        if end is not None else n_frames
    command = [
        'ffmpeg',
        '-y',
        '-threads',
        '4',
        '-start_number',
        f'{start}',
        '-r',
        f'{fps}',
        '-i',
        f'{input_folder}/{img_format}',
        '-frames:v',
        f'{end - start}',
        '-profile:v',
        'baseline',
        '-level',
        '3.0',
        '-c:v',
        'libx264',
        '-pix_fmt',
        'yuv420p',
        '-an',
        '-v',
        'error',
        '-loglevel',
        'error',
        output_path,
    ]
    if resolution:
        height, width = resolution
        width += width % 2
        height += height % 2
        command.insert(1, '-s')
        command.insert(2, '%dx%d' % (width, height))
    if not disable_log:
        print(f'Running \"{" ".join(command)}\"')
    subprocess.call(command)
    if remove_raw_file:
        if Path(input_folder).is_dir():
            shutil.rmtree(input_folder)
