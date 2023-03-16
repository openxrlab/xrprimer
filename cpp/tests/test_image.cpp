#include <data_structure/image.h>
#include <iostream>
#include <opencv2/core.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>
#define CATCH_CONFIG_MAIN
#include "catch.hpp"

TEST_CASE("Image ops", "Image") {

    SECTION("empty") {
        Image img;
        REQUIRE(img.empty());
    }
    SECTION("create") {
        Image img(10, 20, 30, RGB24);
        REQUIRE_FALSE(img.empty());
        REQUIRE(10 == img.width());
        REQUIRE(20 == img.height());
        REQUIRE(RGB24 == img.format());
        REQUIRE(1 == img.depth());
        REQUIRE(3 == img.channels());
        REQUIRE(30 == img.step());
    }

    SECTION("opencv_to_image") {

        // w:20, h:10
        int width = 20;
        int height = 10;
        cv::Mat black = cv::Mat::zeros(height, width, CV_8UC3);
        cv::imwrite("black.bmp", black);

        // proxy cv::Mat data
        Image i_black(black.cols, black.rows, black.step, BGR24, black.data);

        REQUIRE(width == i_black.width());
        REQUIRE(height == i_black.height());
        REQUIRE(i_black.width() == black.cols);
        REQUIRE(i_black.height() == black.rows);
        REQUIRE(i_black.step() == black.step);

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
        REQUIRE(new_val.width() == black.cols);
        REQUIRE(new_val.height() == black.rows);
        REQUIRE(new_val.step() == black.step);
        REQUIRE(std::memcmp(new_val.data(), black.data,
                            new_val.width() * new_val.height() *
                                new_val.elemSize()) == 0);

        Image new_val2;
        i_black.copyTo(&new_val2);
        REQUIRE(new_val2.width() == black.cols);
        REQUIRE(new_val2.height() == black.rows);
        REQUIRE(new_val2.step() == black.step);
        REQUIRE(std::memcmp(new_val2.data(), black.data,
                            new_val2.width() * new_val2.height() *
                                new_val2.elemSize()) == 0);
    }

    SECTION("image_to_opencv") {
        int width = 20;
        int height = 10;
        Image img(width, height, BGR24);
        cv::Mat mat_warpper(img.height(), img.width(), CV_8UC3,
                            img.mutable_data());

        REQUIRE(img.width() == mat_warpper.cols);
        REQUIRE(img.height() == mat_warpper.rows);
        REQUIRE(img.step() == mat_warpper.step);

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
}
