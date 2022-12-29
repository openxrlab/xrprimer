#
# library
#
add_subdirectory(xrprimer)

#
# python bindding
#
if(PYTHON_BINDING AND NOT IOS)
  add_subdirectory(pybind)
endif()

#
# Test case
#
if(ENABLE_TEST)
  add_subdirectory(tests)
endif()
