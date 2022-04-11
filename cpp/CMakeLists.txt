#
# library
#
add_subdirectory(xrprimer)

#
# Test case
#
if(ENABLE_TEST)
    add_subdirectory(tests)
endif()
