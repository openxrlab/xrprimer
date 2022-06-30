#include <common/version.h>
#include <gtest/gtest.h>

TEST(test_version, get_version) {

    int major = get_version_major();
    int minor = get_version_minor();
    int patch = get_version_patch();

    std::string version = get_version_string();

    std::cout << "Major: " << major << std::endl;
    std::cout << "Minor: " << minor << std::endl;
    std::cout << "Patch: " << patch << std::endl;
    std::cout << "Version: " << version << std::endl;
}
