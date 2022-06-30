
#include <common/version.h>
#include <pybind/common/version.h>

void pybind_get_version(py::module &m) {
    m.def("get_version_major", get_version_major);
    m.def("get_version_minor", get_version_minor);
    m.def("get_version_patch", get_version_patch);
    m.def("get_version_string", get_version_string);
}

void xrprimer_pybind_version(py::module &m) {
    py::module m_submodule = m.def_submodule("common");
    pybind_get_version(m_submodule);
}
