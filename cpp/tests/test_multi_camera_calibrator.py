import xrprimer_cpp as xr
import os
import re
import sys


calib_config = """
    {
      "chessboard_width": 6,
      "chessboard_height": 7,
      "chessboard_square_size": 100
    }
"""

image_folder = "test/data/calib_pinhole_camera/input/images/"
camera_folder = "test/data/calib_pinhole_camera/input/config/"

if __name__ == "__main__":

    if len(sys.argv) >=3:
        image_folder = sys.argv[1]
        camera_folder = sys.argv[2]
    print("image folder: ", image_folder)
    print("camera folder: ", camera_folder)

    pinhole_cam_list = []
    # pinhole_list = []
    for root, dirs, files in os.walk(camera_folder):
        camera_cnt = len(list(files))
        pinhole_list = [""] * camera_cnt
        pinhole_cam_list = [xr.camera.PinholeCameraParameter() for i in range(camera_cnt)]

        for file in files:
            camera_idx = int(os.path.splitext(file.split("_")[1])[0])
            # pinhole_list[camera_idx] = os.path.join(root, file)
            cam_path = os.path.join(root, file)
            pinhole_cam_list[camera_idx].LoadFile(cam_path)
            # pinhole_cam_list[camera_idx].SaveFile(str(camera_idx) + ".json")


    max_img_idx = 0
    frames = []
    for root, dirs, files in os.walk(image_folder):
        for file in files:
            img = os.path.join(root, file)
            matched = re.match(r"img(?P<img_index>\d+)_cam(?P<camera_index>\d+).jpg", file)
            if max_img_idx < int(matched.group("img_index")):
                max_img_idx = int(matched.group("img_index"))

        frames = [[]] * (max_img_idx + 1)
        for x in range(max_img_idx + 1):
            frames[x] = [""] * 10

        for file in files:
            img = os.path.join(root, file)
            matched = re.match(r"img(?P<img_index>\d+)_cam(?P<camera_index>\d+).jpg", file)
            frames[int(matched.group("img_index"))][
                int(matched.group("camera_index"))
            ] = img


    vc = xr.VectorPinholeCameraParameter(pinhole_cam_list)
    xr.calibrator.CalibrateMultiPinholeCamera(calib_config, frames, vc)
    print(vc[1].extrinsic_r)

    for idx, pin in enumerate(vc):
        print("save file:", str(idx) + ".json")
        pin.SaveFile(str(idx) + ".json")

