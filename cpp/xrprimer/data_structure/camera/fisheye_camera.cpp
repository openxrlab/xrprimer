
#include "json_helper_internal.h"
#include <data_structure/camera/fisheye_camera.h>
#include <iostream>
#include <json/json.h>

FisheyeCameraParameter::FisheyeCameraParameter()
    : BaseCameraParameter(), k1_(0), k2_(0), k3_(0), k4_(0), k5_(0), k6_(0),
      p1_(0), p2_(0) {}

std::string FisheyeCameraParameter::ClassName() const {
    return "FisheyeCameraParameter";
}

bool FisheyeCameraParameter::SaveFile(const std::string &filename) const {
    Json::Value obj;
    SaveBaseCameraParameter(obj, *this);
    obj["k1"] = k1_;
    obj["k2"] = k2_;
    obj["k3"] = k3_;
    obj["k4"] = k4_;
    obj["k5"] = k5_;
    obj["k6"] = k6_;
    obj["p1"] = p1_;
    obj["p2"] = p2_;
    return JsonToFile(obj, filename);
}

bool FisheyeCameraParameter::LoadFile(const std::string &filename) {
    Json::Value obj;
    bool ret = false;

    if (JsonFromFile(obj, filename)) {
        if (LoadBaseCameraParameter(obj, *this)) {
            ret = check_and_load_float(&k1_, obj, "k1");
            ret &= check_and_load_float(&k2_, obj, "k2");
            ret &= check_and_load_float(&k3_, obj, "k3");
            ret &= check_and_load_float(&k4_, obj, "k4");
            ret &= check_and_load_float(&k5_, obj, "k5");
            ret &= check_and_load_float(&k6_, obj, "k6");
            ret &= check_and_load_float(&p1_, obj, "p1");
            ret &= check_and_load_float(&p2_, obj, "p2");
            return ret;
        }
    }
    return false;
}
