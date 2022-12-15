// Copyright (c) OpenXRLab. All rights reserved.

#include <common/config.h>
#include <common/version.h>
#define FMT_HEADER_ONLY
#include <spdlog/fmt/ostr.h>

std::string get_version_string() {
    return fmt::format("{}.{}.{}", get_version_major(), get_version_minor(),
                       get_version_patch());
}

int get_version_major() { return XRPRIMER_VERSION_MAJOR; }

int get_version_minor() { return XRPRIMER_VERSION_MINOR; }

int get_version_patch() { return XRPRIMER_VERSION_PATCH; }
