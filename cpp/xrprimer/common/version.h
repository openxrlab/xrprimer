// Copyright (c) OpenXRLab. All rights reserved.

#pragma once

/**
 * @file version.h
 * @brief Functions to get xrprimer version
 */

#include <string>

/** @brief Get major version
 * @return int
 */
int get_version_major();

/** @brief Get minor version
 * @return int
 */
int get_version_minor();

/** @brief Get patch version
 * @return int
 */
int get_version_patch();

/** @brief Get version as a string
 * @return string version string with the format 'major.minor.patch'
 */
std::string get_version_string();
