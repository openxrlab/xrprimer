# Image

This file introduces the supported image data structure in C++.


why we need to define a new image class?


It is an extension of OpenCV Mat, and also provides a way to convert between OpenCV Mat and Image.

Besides the normal attributes for an Image, it defines attributes like `timestamp` which is convenient for algorithms like SLAM.

#### Attributes

Here are attributes of class `PinholeCameraParameter`:

| Attribute name | Type     | Description                                                  |
| -------------- | -------- | ------------------------------------------------------------ |
| name           | string   | Name of the camera.                                          |

#### Create an Image

Note that `Image` follows a more CV tradition like using (w, h)

```C++
Image img(10, 20, 30, RGB24);
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
