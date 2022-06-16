#pragma once
#include <Eigen/Core>
#include <cfloat>
#include <cmath>
#include <fstream>
#include <type_traits>

namespace MathUtil {
typedef Eigen::Matrix<unsigned char, Eigen::Dynamic, Eigen::Dynamic> MatrixXb;
typedef Eigen::Matrix<unsigned char, 3, 3> Matrix3b;
typedef Eigen::Matrix<unsigned char, 3, Eigen::Dynamic> Matrix3Xb;
typedef Eigen::Matrix<unsigned char, 4, Eigen::Dynamic> Matrix4Xb;
typedef Eigen::Matrix<unsigned char, 2, 1> Vector2b;
typedef Eigen::Matrix<unsigned char, 3, 1> Vector3b;
typedef Eigen::Matrix<unsigned char, 4, 1> Vector4b;
typedef Eigen::Matrix<unsigned int, Eigen::Dynamic, Eigen::Dynamic> MatrixXu;
typedef Eigen::Matrix<unsigned int, 3, 3> Matrix3u;
typedef Eigen::Matrix<unsigned int, 3, Eigen::Dynamic> Matrix3Xu;
typedef Eigen::Matrix<unsigned int, 4, Eigen::Dynamic> Matrix4Xu;
typedef Eigen::Matrix<unsigned int, 2, 1> Vector2u;
typedef Eigen::Matrix<unsigned int, 3, 1> Vector3u;
typedef Eigen::Matrix<unsigned int, 4, 1> Vector4u;
typedef Eigen::Matrix<float, 6, 1> Vector6f;
typedef Eigen::Matrix<float, 3, 4> Matrix34f;
typedef Eigen::Matrix<float, 3, 2> Matrix32f;
typedef Eigen::Matrix<double, 6, 1> Vector6d;
typedef Eigen::Matrix<double, 3, 4> Matrix34d;
typedef Eigen::Matrix<double, 3, 2> Matrix32d;

// basic
template <typename T> inline bool Equal(const T &a, const T &b) {
    if (std::is_same<float, std::decay<T>>::value)
        return (a - b <= FLT_EPSILON && a - b >= -FLT_EPSILON);
    else if (std::is_same<double, std::decay<T>>::value)
        return (a - b <= DBL_EPSILON && a - b >= -DBL_EPSILON);
    else
        return a == b;
}

template <typename T> inline bool EqualZero(const T &a) { return Equal(a, 0); }

template <typename T>
inline bool Approx(const T &a, const T &b, const T &rate = 10) {
    if (std::is_same<float, T>::value)
        return (a - b <= rate * FLT_EPSILON && a - b >= -rate * FLT_EPSILON);
    else if (std::is_same<double, T>::value)
        return (a - b <= rate * DBL_EPSILON && a - b >= -rate * DBL_EPSILON);
    else
        return a == b;
}

template <typename T> inline bool ApproxZero(const T &a, const T &rate = 10) {
    return Approx(a, T(0), rate);
}

// Linear Algebra
template <typename T>
inline Eigen::Matrix<T, 3, 3> Skew(const Eigen::Matrix<T, 3, 1> &vec) {
    Eigen::Matrix<T, 3, 3> skew;
    skew << 0, -vec.z(), vec.y(), vec.z(), 0, -vec.x(), -vec.y(), vec.x(), 0;
    return skew;
}

template <typename T>
inline Eigen::Matrix<T, 3, 3> Rodrigues(const Eigen::Matrix<T, 3, 1> &vec) {
    const T theta = vec.norm();
    const Eigen::Matrix<T, 3, 3> I = Eigen::Matrix<T, 3, 3>::Identity();

    if (ApproxZero(theta))
        return I;
    else {
        const T c = std::cos(theta);
        const T s = std::sin(theta);
        const T itheta = 1 / theta;
        const Eigen::Matrix<T, 3, 1> r = vec / theta;
        return c * I + (1 - c) * r * r.transpose() + s * Skew(r);
    }
}

template <typename T>
inline Eigen::Matrix<T, 3, 9>
RodriguesJacobi(const Eigen::Matrix<T, 3, 1> &vec) {
    const T theta = vec.norm();
    Eigen::Matrix<T, 3, 9> dSkew;
    dSkew.setZero();
    dSkew(0, 5) = dSkew(1, 6) = dSkew(2, 1) = -1;
    dSkew(0, 7) = dSkew(1, 2) = dSkew(2, 3) = 1;
    if (ApproxZero(theta)) {
        return -dSkew;
    } else {
        const T c = std::cos(theta);
        const T s = std::sin(theta);
        const T c1 = 1 - c;
        const T itheta = 1 / theta;
        const Eigen::Matrix<T, 3, 1> r = vec / theta;
        const Eigen::Matrix<T, 3, 3> rrt = r * r.transpose();
        const Eigen::Matrix<T, 3, 3> skew = Skew(r);
        const Eigen::Matrix<T, 3, 3> I = Eigen::Matrix3f::Identity();
        Eigen::Matrix<T, 3, 9> drrt;
        drrt << r.x() + r.x(), r.y(), r.z(), r.y(), 0, 0, r.z(), 0, 0, 0, r.x(),
            0, r.x(), r.y() + r.y(), r.z(), 0, r.z(), 0, 0, 0, r.x(), 0, 0,
            r.y(), r.x(), r.y(), r.z() + r.z();
        Eigen::Matrix<T, 3, 9> jaocbi;
        Eigen::Matrix<T, 5, 1> a;
        for (int i = 0; i < 3; i++) {
            a << -s * r[i], (s - 2 * c1 * itheta) * r[i], c1 * itheta,
                (c - s * itheta) * r[i], s * itheta;
            for (int j = 0; j < 3; j++)
                for (int k = 0; k < 3; k++)
                    jaocbi(i, k + k + k + j) =
                        (a[0] * I(j, k) + a[1] * rrt(j, k) +
                         a[2] * drrt(i, j + j + j + k) + a[3] * skew(j, k) +
                         a[4] * dSkew(i, j + j + j + k));
        }
        return jaocbi;
    }
}

// robust function
template <typename T> inline T Welsch(const T &c, const T &_x) {
    const T x = _x / c;
    return 1 - exp(-x * x / 2);
}

// 3D measure
template <typename T>
inline T Point2LineDist(const Eigen::Matrix<T, 3, 1> &pA,
                        const Eigen::Matrix<T, 3, 1> &pB,
                        const Eigen::Matrix<T, 3, 1> &ray) {
    return ((pA - pB).cross(ray)).norm();
}

template <typename T>
inline T Line2LineDist(const Eigen::Matrix<T, 3, 1> &pA,
                       const Eigen::Matrix<T, 3, 1> &rayA,
                       const Eigen::Matrix<T, 3, 1> &pB,
                       const Eigen::Matrix<T, 3, 1> &rayB) {
    if (Approx<T>(rayA.dot(rayB), 1))
        return Point2LineDist(pA, pB, rayA);
    else
        return std::abs((pA - pB).dot((rayA.cross(rayB)).normalized()));
}

// others
inline int LayGrid(const int &x, const int &dim) { return (x + dim - 1) / dim; }
} // namespace MathUtil
