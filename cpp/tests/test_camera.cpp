#include <data_structure/camera/fisheye_camera.h>
#include <data_structure/camera/omni_camera.h>
#include <data_structure/camera/pinhole_camera.h>

#include <iostream>
#define CATCH_CONFIG_MAIN
#include "catch.hpp"

TEST_CASE("FisheyeCamera", "API") {
    auto fishcamera = FisheyeCameraParameter();
    std::cout << fishcamera.ClassName() << std::endl;
    fishcamera.SaveFile("test_fisheye_cam.json");
    fishcamera.LoadFile("test_fisheye_cam.json");
}

TEST_CASE("OmniCamera", "API") {
    auto omnicamera = OmniCameraParameter();
    std::cout << omnicamera.ClassName() << std::endl;
    omnicamera.SaveFile("test_omni_cama.json");
    omnicamera.LoadFile("test_omni_cama.json");
}

TEST_CASE("PinholeCamera", "API") {
    auto pinholecamera = PinholeCameraParameter();
    std::cout << pinholecamera.ClassName() << std::endl;
    pinholecamera.SaveFile("test_pinhole_cam.json");
    pinholecamera.LoadFile("test_pinhole_cam.json");
}
