

#include <Eigen/Eigen>
#include <iostream>
#include <json/json.h>
#include <opencv2/core.hpp>
#include <xrprimer/data_structure/image.h>

int main() {
    std::cout << "Hello XRPrimer" << std::endl;
    Eigen::Matrix3f mat3x3(Eigen::Matrix3f::Identity()); // use Eigen
    cv::Mat mat(10, 20, CV_8UC3);                        // use opencv
    auto value = Json::Value(10);                        // use json
    auto image = Image(10, 20, 30, BGR24);               // use xrprimer
}