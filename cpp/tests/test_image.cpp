#include <data_structure/image.h>
#include <gtest/gtest.h>
#include <opencv2/core.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>

TEST(test_image, create) {
    {
        Image img;
        EXPECT_TRUE(img.empty());
    }
    {
        Image img(10, 20, 30, RGB24);
        EXPECT_FALSE(img.empty());
        EXPECT_EQ(10, img.width());
        EXPECT_EQ(20, img.height());
        EXPECT_EQ(RGB24, img.format());
        EXPECT_EQ(1, img.depth());
        EXPECT_EQ(3, img.channels());
        EXPECT_EQ(30, img.step());
    }
}

TEST(test_image, opencv_to_image) {

    // w:20, h:10
    int width = 20;
    int height = 10;
    cv::Mat black = cv::Mat::zeros(height, width, CV_8UC3);
    cv::imwrite("black.bmp", black);

    // proxy cv::Mat data
    Image i_black(black.cols, black.rows, black.step, BGR24, black.data);

    EXPECT_EQ(width, i_black.width());
    EXPECT_EQ(height, i_black.height());
    EXPECT_EQ(i_black.width(), black.cols);
    EXPECT_EQ(i_black.height(), black.rows);
    EXPECT_EQ(i_black.step(), black.step);

    std::cout << black.cols << std::endl;
    std::cout << black.rows << std::endl;
    std::cout << black.step << std::endl;
    std::cout << black.channels() << std::endl;
    std::cout << black.total() << std::endl;

    // get roi data roi:(left:4, top:4, width:6, height:5)
    int left = 4;
    int top = 4;
    int roi_w = 6;
    int roi_h = 5;
    uint8_t *data = (uint8_t *)i_black.mutable_data();
    uintptr_t offset = top * i_black.step() + left * i_black.elemSize();
    data += offset;
    for (int h = 0; h < roi_h; ++h) {
        data += i_black.step();
        memset(data, 255, roi_w * i_black.elemSize());
    }
    cv::imwrite("black_with_white.bmp", black);

    Image new_val = i_black.clone();
    EXPECT_EQ(new_val.width(), black.cols);
    EXPECT_EQ(new_val.height(), black.rows);
    EXPECT_EQ(new_val.step(), black.step);

    Image new_val2;
    i_black.copyTo(&new_val2);
    EXPECT_EQ(new_val2.width(), black.cols);
    EXPECT_EQ(new_val2.height(), black.rows);
    EXPECT_EQ(new_val2.step(), black.step);
}

TEST(test_image, image_to_opencv) {
    int width = 20;
    int height = 10;
    Image img(width, height, BGR24);
    cv::Mat mat_warpper(img.height(), img.width(), CV_8UC3, img.mutable_data());

    EXPECT_EQ(img.width(), mat_warpper.cols);
    EXPECT_EQ(img.height(), mat_warpper.rows);
    EXPECT_EQ(img.step(), mat_warpper.step);

    std::cout << mat_warpper.cols << std::endl;
    std::cout << mat_warpper.rows << std::endl;
    std::cout << mat_warpper.step << std::endl;
    std::cout << mat_warpper.channels() << std::endl;
    std::cout << mat_warpper.total() << std::endl;
    std::cout << (uint64_t)mat_warpper.data << std::endl;
    std::cout << (uint64_t)img.data() << std::endl;
    mat_warpper.setTo(0);
    mat_warpper.setTo(cv::Scalar(255, 0, 0));
    cv::imwrite("blue.bmp", mat_warpper);
    mat_warpper.setTo(cv::Scalar(255, 255, 0));
    cv::imwrite("cyan.bmp", mat_warpper);
    cv::Mat gray;
    cv::cvtColor(mat_warpper, gray, cv::COLOR_BGR2GRAY);
    cv::imwrite("gray.bmp", gray);
}
