
#include <data_structure/camera/pinhole_camera.h>
#include <iostream>
#include <json/json.h>

template <typename T>
static void SaveMatrix(Json::Value &obj, const std::string &key, T mat) {
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
static void LoadMatrix(Json::Value &obj, const std::string &key, T &mat) {
  int rows = mat.rows();
  int cols = mat.cols();

  Json::Value array = obj[key];
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
}

void PinholeCameraParameter::SaveFile(const std::string &filename) {
  Json::Value obj;
  obj["name"] = name_;
  obj["height"] = height_;
  obj["width"] = width_;
  SaveMatrix(obj, "intrinsic", intrinsic_);
  SaveMatrix(obj, "extrinsic_r", extrinsic_r_);
  SaveMatrix(obj, "extrinsic_t", extrinsic_t_);
  obj["k1"] = k1_;
  obj["k2"] = k2_;
  obj["k3"] = k3_;
  obj["k4"] = k4_;
  obj["k5"] = k5_;
  obj["k6"] = k6_;
  obj["p1"] = p1_;
  obj["p2"] = p2_;
  std::ofstream jsonfile(filename, std::ios::out | std::ios::trunc);
  {
    Json::StyledWriter writer;
    jsonfile << writer.write(obj);
  }
  jsonfile.close();
}
void PinholeCameraParameter::LoadFile(const std::string &filename) {
  Json::Value obj;
  Json::Reader reader;
  std::ifstream jsonfile(filename);

  if (reader.parse(jsonfile, obj, false)) {
    name_ = obj["name"].asString();
    height_ = obj["height"].asInt();
    width_ = obj["width"].asInt();
    LoadMatrix(obj, "intrinsic", intrinsic_);
    LoadMatrix(obj, "extrinsic_r", extrinsic_r_);
    LoadMatrix(obj, "extrinsic_t", extrinsic_t_);
    k1_ = obj["k1"].asFloat();
    k2_ = obj["k2"].asFloat();
    k3_ = obj["k3"].asFloat();
    k4_ = obj["k4"].asFloat();
    k5_ = obj["k5"].asFloat();
    k6_ = obj["k6"].asFloat();
    p1_ = obj["p1"].asFloat();
    p2_ = obj["p2"].asFloat();
  } else {
    std::cerr << "Invalid json file: " << filename << std::endl;
  }
}