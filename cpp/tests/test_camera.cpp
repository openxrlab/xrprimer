#include <data_structure/camera/fisheye_camera.h>
#include <data_structure/camera/omni_camera.h>
#include <data_structure/camera/pinhole_camera.h>

#include <gtest/gtest.h>

TEST(FisheyeCamera, API) {
    auto fishcamera = FisheyeCameraParameter();
    std::cout << fishcamera.ClassName() << std::endl;
    fishcamera.SaveFile("a.json");
    fishcamera.LoadFile("a.json");
}

TEST(OmniCamera, API) {
    auto omnicamera = OmniCameraParameter();
    std::cout << omnicamera.ClassName() << std::endl;
    omnicamera.SaveFile("a.json");
    omnicamera.LoadFile("a.json");
}

TEST(PinholeCamera, API) {
    auto pinholecamera = PinholeCameraParameter();
    std::cout << pinholecamera.ClassName() << std::endl;
    pinholecamera.SaveFile("a.json");
    pinholecamera.LoadFile("a.json");
}
