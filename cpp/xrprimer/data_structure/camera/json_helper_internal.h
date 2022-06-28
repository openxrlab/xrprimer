#pragma once

#include <data_structure/camera/camera.h>
#include <iostream>
#include <json/json.h>

template <typename T>
static void SaveMatrixToJson(Json::Value &obj, const std::string &key, T mat) {
    int rows = mat.rows();
    int cols = mat.cols();

    Json::Value array;
    if (cols == 1) {
        for (int r = 0; r < rows; r++) {
            array.append(mat(r, 0));
        }
    } else {
        for (int r = 0; r < rows; r++) {
            Json::Value inner_arr;
            for (int c = 0; c < cols; c++) {
                inner_arr.append(mat(r, c));
            }
            array.append(inner_arr);
        }
    }
    obj[key] = array;
}

template <typename T>
static bool LoadMatrixFromJson(const Json::Value &obj, const std::string &key,
                               T &mat) {
    int rows = mat.rows();
    int cols = mat.cols();

    Json::Value array = obj[key];

    if (array.empty()) {
        std::cerr << "Not found key:[" << key << "] in json file" << std::endl;
        return false;
    }

    if (cols == 1) {
        for (int r = 0; r < rows; r++) {
            mat(r, 0) = array[r].asFloat();
        }
    } else {
        for (int r = 0; r < rows; r++) {
            Json::Value inner_arr = array[r];
            for (int c = 0; c < cols; c++) {
                mat(r, c) = inner_arr[c].asFloat();
            }
        }
    }
    return true;
}

static void SaveBaseCameraParameter(Json::Value &obj,
                                    const BaseCameraParameter &param) {
    obj["class_name"] = param.ClassName();
    obj["name"] = param.name_;
    obj["height"] = param.height_;
    obj["width"] = param.width_;
    SaveMatrixToJson(obj, "intrinsic", param.intrinsic_);
    SaveMatrixToJson(obj, "extrinsic_r", param.extrinsic_r_);
    SaveMatrixToJson(obj, "extrinsic_t", param.extrinsic_t_);
    obj["convention"] = param.convention_;
    obj["world2cam"] = param.world2cam_;
}

static bool LoadBaseCameraParameter(const Json::Value &obj,
                                    BaseCameraParameter &param) {

    std::string cls_name = obj["class_name"].asString();
    bool ret = false;

    if (cls_name != "" && cls_name != param.ClassName()) {
        std::cerr << "Invalid " << param.ClassName() << " format json file\n";
        return ret;
    }

    param.name_ = obj["name"].asString();
    param.height_ = obj["height"].asInt();
    param.width_ = obj["width"].asInt();
    param.convention_ = obj["convention"].asString();
    param.world2cam_ = obj["world2cam"].asBool();

    ret = LoadMatrixFromJson(obj, "intrinsic", param.intrinsic_);
    ret &= LoadMatrixFromJson(obj, "extrinsic_r", param.extrinsic_r_);
    ret &= LoadMatrixFromJson(obj, "extrinsic_t", param.extrinsic_t_);
    return ret;
}

static std::string JsonToString(const Json::Value &obj) {
    Json::StyledWriter writer;
    return writer.write(obj);
}

static bool JsonToFile(const Json::Value &obj, const std::string &filename) {
    std::ofstream jsonfile(filename, std::ios::out | std::ios::trunc);
    if (jsonfile.is_open()) {
        Json::StyledWriter writer;
        jsonfile << writer.write(obj);
        jsonfile.close();
        return true;
    }
    std::cerr << "Save Failed!, filename: " << filename << std::endl;
    return false;
}

static bool JsonFromFile(Json::Value &obj, const std::string &filename) {
    Json::Reader reader;
    std::ifstream jsonfile(filename);
    if (jsonfile.is_open()) {
        if (reader.parse(jsonfile, obj, false)) {
            return true;
        }
    }
    std::cerr << "Parse Failed!, filename: " << filename << std::endl;
    return false;
}

static bool check_and_load_float(float *val, const Json::Value &obj,
                                 const std::string &key) {
    if (obj[key].empty()) {
        std::cerr << "Not found key:[" << key << "] in json file" << std::endl;
        return false;
    }
    *val = obj[key].asFloat();
    return true;
};
