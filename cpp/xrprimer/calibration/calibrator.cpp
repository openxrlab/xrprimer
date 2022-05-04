#include "calibrator.h"

#include <ceres/ceres.h>

#include <Eigen/Eigen>

#include <iomanip>
#include <iostream>
#include <iterator>
#include <numeric>
#include <opencv2/calib3d.hpp>
#include <opencv2/core/eigen.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>
#include <thread>
#include <vector>

static void
triangulate_points(const std::vector<Eigen::Vector2f> &points2ds,
                   const std::vector<MathUtil::Matrix34f> &projectionMatrices,
                   Eigen::Vector3d &points3d) {

  if (projectionMatrices.size() < 2) {
    points3d.setZero();
    return;
  }

  Eigen::MatrixXd Jacobian = Eigen::MatrixXd::Zero(2 * points2ds.size(), 4);
  for (int vi = 0; vi < points2ds.size(); ++vi) {
    Jacobian.row(2 * vi) = (points2ds[vi].x() * projectionMatrices[vi].row(2) -
                            projectionMatrices[vi].row(0))
                               .cast<double>();
    Jacobian.row(2 * vi + 1) =
        (points2ds[vi].y() * projectionMatrices[vi].row(2) -
         projectionMatrices[vi].row(1))
            .cast<double>();
  }

  Eigen::Vector4d triangulated_point =
      Jacobian.jacobiSvd(Eigen::ComputeFullV).matrixV().rightCols<1>();

  points3d.x() = (triangulated_point.x() / triangulated_point.w());
  points3d.y() = (triangulated_point.y() / triangulated_point.w());
  points3d.z() = (triangulated_point.z() / triangulated_point.w());
}

static void findChessboardCorners(int &result, const std::string &image,
                                  cv::Size &patternSize,
                                  std::vector<cv::Point2f> &corners) {

  if (image.empty()) {
    result = 0;
    return;
  }

  cv::Mat img_data = cv::imread(image, cv::IMREAD_GRAYSCALE);
  bool res = cv::findChessboardCorners(img_data, patternSize, corners,
                                       cv::CALIB_CB_ADAPTIVE_THRESH |
                                           cv::CALIB_CB_NORMALIZE_IMAGE |
                                           cv::CALIB_CB_FAST_CHECK);

  if (res) {
    cv::cornerSubPix(
        img_data, corners, cv::Size(11, 11), cv::Size(-1, -1),
        cv::TermCriteria(cv::TermCriteria::EPS + cv::TermCriteria::MAX_ITER, 30,
                         0.1));
  }

  result = res ? 1 : 0;
}

bool MultiCalibrator::Push(const std::vector<std::string> &imgs) {
  // cameras/point2ds
  std::vector<std::vector<cv::Point2f>> imageCornersList(imgs.size());
  std::vector<int> foundCorners(imgs.size());
  std::vector<std::thread> findThreads(imgs.size());

  // FIXME: threadpool or async
  // findChessboardCorners
  int camCount = imgs.size();
  for (size_t idx = 0; idx < camCount; idx++) {
    findThreads[idx] = std::thread([&, idx]() {
      findChessboardCorners(foundCorners[idx], imgs[idx], patternSize,
                            imageCornersList[idx]);
    });
  }
  for (size_t i = 0; i < camCount; i++) {
    findThreads[i].join();
  }

  foundCornersList.push_back(foundCorners);

  int valid = 0;
  for (size_t index = 0; index < foundCorners.size(); index++) {
    if (foundCorners[index]) {
      valid++;
    } else {
      std::cout << "Not found pattern on camera idx: " << index << std::endl;
    }
  }

  if (valid >= 2) {
    p2ds.emplace_back(imageCornersList);
    return true;
  }

  return false;
}

bool MultiCalibrator::Init() {
  std::vector<size_t> unInitCamIndexList;
  std::vector<int> validCarmersCountList;
  // First Step: solve pnp
  // Calibrate each camera individually
  int32_t maxIdx = -1, maxSize = -1;

  {
    printf("Init cameras.\n");

    validCarmersCountList.reserve(p2ds.size());

    // frames/camera/points
    for (int i = 0; i < p2ds.size(); i++) {
      int32_t validCams = 0;
      for (size_t cidx = 0; cidx < p2ds[i].size(); cidx++) {
        if (!p2ds[i][cidx].empty()) {
          validCams++;
        }
      }

      validCarmersCountList.push_back(validCams);

      if (maxSize < validCams) {
        maxSize = validCams;
        maxIdx = i;
      }
    }

    // print valid value
    for (int i = 0; i < foundCornersList.size(); i++) {
      std::cout << "frameID: " << std::setw(2) << i << " | "
                << "valid:" << validCarmersCountList[i] << " | ";
      std::copy(foundCornersList[i].begin(), foundCornersList[i].end(),
                std::ostream_iterator<int>(std::cout, " "));
      std::cout << std::endl;
    }

    std::vector<cv::Point3f> p3ds;
    for (int row = 0; row < patternSize.height; row++)
      for (int col = 0; col < patternSize.width; col++)
        p3ds.emplace_back(
            cv::Point3f(col * squareSize.width, row * squareSize.height, 0.f));

    int camId = 0;
    // camera/points

    cv::Matx33f cvNewK;
    cv::Mat rvec, rmat, tvec;
    for (const auto &iter : p2ds[maxIdx]) {
      PinholeCameraParameter &cam = cams[camId++];
      if (iter.empty()) {
        unInitCamIndexList.push_back(camId);
        continue;
      }
      cv::eigen2cv(cam.intrinsic33(), cvNewK);
      cv::solvePnP(p3ds, iter, cvNewK, cv::Mat(), rvec, tvec);

      cv::Rodrigues(rvec, rmat);
      cv::cv2eigen(rmat, cam.extrinsic_r_);
      cv::cv2eigen(tvec, cam.extrinsic_t_);
    }
  }

  // FIXME: may be need a Max iter count, else while(1)
  // second step: using solvePnP to init other cameras
  while (!unInitCamIndexList.empty()) {
    printf("Init other cameras.\n");
    // find next camera to solve pnp
    std::vector<std::pair<int, int>> candidateFrames;

    // cameras
    for (int i = 0; i < p2ds.size(); i++) {
      int initCnt = 0;
      int camId = 0;

      // points
      for (const auto &iter : p2ds[i]) {
        camId++;
        if (iter.empty()) {
          continue;
        }

        if (std::find(unInitCamIndexList.begin(), unInitCamIndexList.end(),
                      camId) == unInitCamIndexList.end()) {
          initCnt++;
        }
      }

      if (initCnt >= 1 && initCnt != validCarmersCountList[i]) {
        candidateFrames.emplace_back(std::make_pair(initCnt, i));
      }
    }

    if (candidateFrames.empty()) {
      std::cout << "Cannot find enough frames to init all the cameras!!!"
                << std::endl;
      return false; // cannot init camera
    }

    std::cout << "unInitCamera: ";
    std::copy(unInitCamIndexList.begin(), unInitCamIndexList.end(),
              std::ostream_iterator<int>(std::cout, " "));
    std::cout << std::endl;

    std::cout << "candidate frame indices: \n";

    for (auto c : candidateFrames)
      std::cout << "FrameIdx: " << std::setw(2) << c.second
                << " InitCnt: " << c.first
                << " valid: " << validCarmersCountList[c.second] << std::endl;

    const int maxIdx =
        std::max_element(candidateFrames.begin(), candidateFrames.end())
            ->second;

    std::vector<cv::Point3f> p3ds;
    for (int row = 0; row < patternSize.height; row++)
      for (int col = 0; col < patternSize.width; col++)
        p3ds.emplace_back(
            cv::Point3f(col * squareSize.width, row * squareSize.height, 0.f));

    // get deltaT from current coordinate to world coordinate
    Eigen::Matrix4f deltaT = Eigen::Matrix4f::Identity();
    int camId = 0;
    cv::Matx33f cvNewK;
    for (const auto &iter : p2ds[maxIdx]) {
      PinholeCameraParameter &cam = cams[camId++];
      if (iter.empty()) {
        continue;
      }
      if (std::find(unInitCamIndexList.begin(), unInitCamIndexList.end(),
                    camId) == unInitCamIndexList.end()) {
        Eigen::Matrix3f R = cam.extrinsic_r_;
        Eigen::Vector3f t = cam.extrinsic_t_;
        Eigen::Matrix4f Tworld;
        Tworld.setIdentity();
        Tworld.topLeftCorner(3, 3) = R;
        Tworld.topRightCorner(3, 1) = t;

        cv::Mat rvec, rmat, tvec;
        cv::eigen2cv(cam.intrinsic33(), cvNewK);
        cv::solvePnP(p3ds, iter, cvNewK, cv::Mat(), rvec, tvec);
        cv::Rodrigues(rvec, rmat);

        Eigen::Matrix3f Rnew;
        Eigen::Vector3f tnew;
        cv2eigen(rmat, Rnew);
        cv2eigen(tvec, tnew);
        Eigen::Matrix4f Tnew = Eigen::Matrix4f::Identity();
        Tnew.topLeftCorner(3, 3) = Rnew;
        Tnew.topRightCorner(3, 1) = tnew;

        Eigen::Matrix4f Tnew_inv = Tnew.inverse();

        deltaT = Tnew_inv * Tworld;

        break;
      }
    }

    Eigen::Matrix4f Tref = Eigen::Matrix4f::Identity();
    camId = 0;

    for (const auto &iter : p2ds[maxIdx]) {
      PinholeCameraParameter &cam = cams[camId++];
      if (iter.empty()) {
        continue;
      }
      if (std::find(unInitCamIndexList.begin(), unInitCamIndexList.end(),
                    camId) == unInitCamIndexList.end())
        continue;

      cv::Mat rvec, rmat, tvec;
      cv::eigen2cv(cam.intrinsic33(), cvNewK);
      cv::solvePnP(p3ds, iter, cvNewK, cv::Mat(), rvec, tvec);
      cv::Rodrigues(rvec, rmat);

      Eigen::Matrix3f Rnew;
      Eigen::Vector3f tnew;
      cv2eigen(rmat, Rnew);
      cv2eigen(tvec, tnew);
      Eigen::Matrix4f Tnew = Eigen::Matrix4f::Identity();
      Tnew.topLeftCorner(3, 3) = Rnew;
      Tnew.topRightCorner(3, 1) = tnew;

      Eigen::Matrix4f Tworld = Tnew * deltaT;

      std::cout << "Tworld: \n" << Tworld << std::endl;

      cam.extrinsic_r_ = Tworld.topLeftCorner(3, 3);
      cam.extrinsic_t_ = Tworld.topRightCorner(3, 1);

      unInitCamIndexList.erase(std::find(unInitCamIndexList.begin(),
                                         unInitCamIndexList.end(), camId));
    }
  }

  return true;
}

struct ReprojCostFunctor {
  ReprojCostFunctor(const Eigen::Matrix3d &_K, const Eigen::Vector2d &_p2d) {
    m_K = _K;
    m_p2d = _p2d;
  }

  template <typename T>
  bool operator()(const T *const _r, const T *const _t, const T *_p3d,
                  T *residuals) const {
    const Eigen::Map<const Eigen::Matrix<T, 3, 1>> r(_r);
    const Eigen::Map<const Eigen::Matrix<T, 3, 1>> t(_t);
    const Eigen::Map<const Eigen::Matrix<T, 3, 1>> p3d(_p3d);

    const T theta = r.norm();
    Eigen::Matrix<T, 3, 3> R;
    if (theta < T(DBL_EPSILON))
      R = Eigen::Matrix3d::Identity().cast<T>();
    else
      R = Eigen::AngleAxis<T>(theta, r / theta).matrix();

    Eigen::Matrix<T, 3, 1> p = m_K.cast<T>() * (R * p3d + t);
    Eigen::Matrix<T, 2, 1> uv(p[0] / p[2], p[1] / p[2]);
    residuals[0] = (uv - m_p2d.cast<T>()).norm();
    return true;
  }

private:
  Eigen::Matrix3d m_K;
  Eigen::Vector2d m_p2d;
};

void MultiCalibrator::optimizeExtrinsics() {
  printf("Start bundle.\n");
  std::vector<Eigen::Vector3d> rs;
  std::vector<Eigen::Vector3d> ts;
  for (const auto &cam : cams) {
    Eigen::AngleAxisf angleAxis(cam.extrinsic_r_);
    rs.push_back(
        Eigen::Vector3f(angleAxis.axis() * angleAxis.angle()).cast<double>());
    ts.push_back(cam.extrinsic_t_.cast<double>());
  }

  size_t pointCount = patternSize.height * patternSize.width;
  // frame/[3 * points]
  std::vector<Eigen::Matrix3Xd> p3ds(p2ds.size(),
                                     Eigen::Matrix3Xd(3, pointCount));

  Eigen::Vector3d point3d;

  ceres::Problem problem;
  for (int imgIdx = 0; imgIdx < p2ds.size(); imgIdx++) {
    std::vector<std::vector<Eigen::Vector2f>> point2ds;
    std::vector<std::vector<MathUtil::Matrix34f>> projs;
    point2ds.resize(pointCount);
    projs.resize(pointCount);
    // triangulate
    int camIdx = 0;
    for (const auto &iter : p2ds[imgIdx]) {
      auto cam = cams[camIdx++];
      if (iter.empty()) {
        continue;
      }

      for (size_t i = 0; i < pointCount; i++) {
        point2ds[i].push_back(Eigen::Vector2f(iter[i].x, iter[i].y));

        MathUtil::Matrix34f proj;
        proj.leftCols<3>() = cam.extrinsic_r_;
        proj.col(3) = cam.extrinsic_t_;
        proj = cam.intrinsic33() * proj;
        projs[i].push_back(std::move(proj));
      }
    }

    for (int i = 0; i < pointCount; i++) {
      triangulate_points(point2ds[i], projs[i], point3d);
      p3ds[imgIdx].col(i) = point3d;
    }

    camIdx = 0;
    for (auto &&iter : p2ds[imgIdx]) {
      auto cam = cams[camIdx++];
      const Eigen::Matrix3d K = cam.intrinsic33().cast<double>();
      double *_r = rs[camIdx - 1].data();
      double *_t = ts[camIdx - 1].data();
      for (int pIdx = 0; pIdx < iter.size(); pIdx++) {
        const Eigen::Vector2d p2d(iter[pIdx].x, iter[pIdx].y);
        ceres::CostFunction *func =
            new ceres::AutoDiffCostFunction<ReprojCostFunctor, 1, 3, 3, 3>(
                new ReprojCostFunctor(K, p2d));
        problem.AddResidualBlock(func, NULL, _r, _t,
                                 p3ds[imgIdx].col(pIdx).data());
      }
    }
  }

  ceres::Solver::Options options;
  options.linear_solver_type = ceres::ITERATIVE_SCHUR;
  options.minimizer_type = ceres::LINE_SEARCH;
  options.max_num_iterations = 5000;
  options.minimizer_progress_to_stdout = true;
  ceres::Solver::Summary summary;
  ceres::Solve(options, &problem, &summary);

  // update
  for (size_t i = 0; i < cams.size(); i++) {
    cams[i].extrinsic_r_ =
        MathUtil::Rodrigues(Eigen::Vector3f(rs[i].cast<float>()));
    cams[i].extrinsic_t_ = Eigen::Vector3f(ts[i].cast<float>());
  }

  if (/*verbose*/ 0) {
    std::cout << summary.BriefReport() << std::endl;
  }
}

void MultiCalibrator::NormalizeCamExtrinsics() {
  // transform camera extrinsics (use cam0 as world coordinate)
  Eigen::Matrix4f RT0 = Eigen::Matrix4f::Identity();
  RT0.topLeftCorner(3, 3) = cams[0].extrinsic_r_;
  RT0.topRightCorner(3, 1) = cams[0].extrinsic_t_;

  std::cout << "RT0:\n" << RT0 << std::endl;

  for (auto &cam : cams) {
    Eigen::Matrix4f RT = Eigen::Matrix4f::Identity();
    RT.topLeftCorner(3, 3) = cam.extrinsic_r_;
    RT.topRightCorner(3, 1) = cam.extrinsic_t_;
    Eigen::Matrix4f RT_inv = RT.inverse();

    Eigen::Matrix4f RT_ = RT0 * RT_inv;
    cam.extrinsic_r_ = RT_.topLeftCorner(3, 3);
    cam.extrinsic_t_ = RT_.topRightCorner(3, 1);
  }
}
