# Keypoints visualization

- [Visualize keypoints2d](#visualize-keypoints2d)
  - [Output options](#output-options)
  - [Background options](#background-options)
  - [Plotting options](#plotting-options)
  - [DIY guidance](#diy-guidance)

### Visualize keypoints2d

#### Output options:

Function `visualize_keypoints2d` visualizes keypoints2d defined by class Keypoints, saves frames to file. If you want the plotted image array, set `return_array=True`, and make sure that you have enough RAM for the returned image array.

```python
from xrprimer.visualization.keypoints.visualize_keypoints2d import visualize_keypoints2d


# saving results to an mp4 video
visualize_keypoints2d(
        keypoints=keypoints2d,
        output_path='output_video.mp4',
        width=1920,
        height=1080)
# saving results to png images in a folder
visualize_keypoints2d(
        keypoints=keypoints2d,
        output_path='output_folder/',
        width=1920,
        height=1080)
# saving results to png images in a folder
mframe_array = visualize_keypoints2d(
        keypoints=keypoints2d,
        output_path='output_folder/',
			  return_array=True,
        width=1920,
        height=1080)
```

#### Background options:

For background configuration, there are 4 options, please choose one and only one when calling `visualize_keypoints2d`:

- Multi-frame image ndarray, in shape [n_frame, height, width, 3].
- Path to a multi-frame image directory, make sure that number of files equals to `keypoints2d.get_frame_number()`, and the files are well-sorted by names.
- Path to a video.
- White background, whose resolution is defined by both `width`  and `height` arguments.

```python
# multi-frame image ndarray
visualize_keypoints2d(
        keypoints=keypoints2d,
        output_path=output_path,
        background_arr=np.zeros(
          shape=(keypoints2d.get_frame_number(), 1080, 1920, 3),
					dtype=np.uint8)
# multi-frame image directory
visualize_keypoints2d(
        keypoints=keypoints2d,
        output_path=output_path,
        background_dir='image_dir/')
# video
visualize_keypoints2d(
        keypoints=keypoints2d,
        output_path=output_path,
        background_video='video.mp4')
# 1080p white background
visualize_keypoints2d(
        keypoints=keypoints2d,
        output_path=output_path,
        width=1920,
        height=1080)
```

#### Plotting options:

For plotting configuration, there are 2 options, at least one of them must be set as True:

- plot_points: whether to plot points according to keypoints' location.
- plot_lines: whether to plot lines according to keypoints' limbs.

```python
# Plot only keypoints
# connections between points, and points whose mask==0 are not plotted
visualize_keypoints2d(
        keypoints=keypoints2d,
        output_path='output_folder/',
        plot_points=True,
    		plot_lines=False,
        width=1920,
        height=1080)
# Plot only limbs
# if either of the two limb ends has mask==0, the limb is not plotted
visualize_keypoints2d(
        keypoints=keypoints2d,
        output_path='output_folder/',
        plot_points=False,
    		plot_lines=True,
        width=1920,
        height=1080)
# Plot both limbs and keypoints, which is the default setting
visualize_keypoints2d(
        keypoints=keypoints2d,
        output_path='output_folder/',
        width=1920,
        height=1080)
```

#### DIY guidance:

If our visualization implement does not fulfill your demands, here are some useful references for DIY your own visualization function:

- For colors: `LinePalette ` and `PointPalette` in `python/xrprimer/visualization/palette`.
- For thickness and radius: `plot_frame` in `python/xrprimer/visualization/opencv`.
- For background and RAM control: `plot_video` in `python/xrprimer/visualization/opencv`.
- For per-keypoint visibility: `Keypoints` in `python/xrprimer/data_structure`.
- For auto limbs definition: `get_limbs_from_keypoints` in `python/xrprimer/transform/limbs`.
