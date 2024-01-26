
#include <pybind/calibration/calibrator_api.h>

#ifdef XRPRIMER_BUILD_BASE
void xrprimer_pybind_calibrator(py::module &m) {}
#else

#include <calibration/calibrator_api.h>

void pybind_camera_calibrator(py::module &m) {
    m.def("CalibrateMultiPinholeCamera", &CalibrateMultiPinholeCamera);
}

void xrprimer_pybind_calibrator(py::module &m) {
    py::module m_submodule = m.def_submodule("calibrator");
    pybind_camera_calibrator(m_submodule);
}
#endif
