
#include "pybind/xrprimer_pybind.h"

#include <pybind/calibration/calibrator_api.h>
#include <pybind/data_structure/camera.h>

PYBIND11_MODULE(xrprimer_cpp, m) {

    // later in binding code:
    py::bind_vector<std::vector<int>>(m, "VectorInt");
    py::bind_vector<std::vector<int64_t>>(m, "VectorInt64");
    py::bind_vector<std::vector<uint8_t>>(m, "VectorUint8");
    py::bind_vector<std::vector<float>>(m, "VectorFloat");
    py::bind_vector<std::vector<double>>(m, "VectorDouble");

    py::bind_vector<std::vector<PinholeCameraParameter>>(
        m, "VectorPinholeCameraParameter")
        .def(py::init(
            [](int i) { return std::vector<PinholeCameraParameter>(i); }));
    py::implicitly_convertible<py::tuple,
                               std::vector<PinholeCameraParameter>>();
    py::implicitly_convertible<py::list, std::vector<PinholeCameraParameter>>();

    xrprimer_pybind_camera(m);
    xrprimer_pybind_calibrator(m);
}
