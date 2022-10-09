#pragma once

/**
 * @file version.h
 * @brief Functions to get xrprimer version
 */

#include <string>

/** @brief get_version_major
 * @return major version number
 */
int get_version_major();

int get_version_minor();

int get_version_patch();

std::string get_version_string();
