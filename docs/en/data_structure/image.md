# Image

This file introduces the supported image data structure in C++.
It is an extension of OpenCV Mat, and also provides a way to convert between OpenCV Mat and Image.

#### Attributes

Here are attributes of class `Image`.

| Attribute name  | Type                       | Description                                     |
| --------------- | -------------------------- | ----------------------------------------------- |
| width           | int                        |  Image width in pixels                          |
| height          | int                        |  Image height in pixels                         |
| step\_          | int                        |  Size of aligned image row in bytes             |
| ts              | int64\_t                   |  Image timestamp                                |
| stream\_id      | int64\_t                   |  Image stream index                             |
| format\_        | PixelFormat                |  Image format (e.g., RGB24, BGR24, RGBA, GRAY8) |
| storage\_data\_ | std::shared\_ptr<uint8\_t> |  Pointer to image data                          |

Besides the normal attributes for an image, it defines attributes like `timestamp` which is convenient for algorithms like SLAM.

#### Create an Image

Note that `Image` follows the order (width, height).

```C++
// create a color image with w=20 and h=10
Image img(20, 10, RGB24);
```

#### From Image to OpenCV

```C++
int width = 20;
int height = 10;
Image img(width, height, BGR24);

// Image to OpenCV
cv::Mat mat_warpper(img.height(), img.width(), CV_8UC3, img.mutable_data());
```

#### From OpenCV to Image

```C++
int width = 20;
int height = 10;
cv::Mat black = cv::Mat::zeros(height, width, CV_8UC3);
cv::imwrite("black.bmp", black);

// OpenCV to Image
Image i_black(black.cols, black.rows, black.step, BGR24, black.data);
```
