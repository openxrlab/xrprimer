#include <common/version.h>
#include <iostream>

#define CATCH_CONFIG_MAIN
#include "catch.hpp"

TEST_CASE("Meta", "Get Version") {

    int major = get_version_major();
    int minor = get_version_minor();
    int patch = get_version_patch();

    std::string version = get_version_string();

    std::cout << "Major: " << major << std::endl;
    std::cout << "Minor: " << minor << std::endl;
    std::cout << "Patch: " << patch << std::endl;
    std::cout << "Version: " << version << std::endl;
}
