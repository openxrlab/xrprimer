#pragma once

#include <memory>
#include <stdint.h>
#include <vector>

class Image {

public:
  Image() = default;
  ~Image() = default;

  Image(int width, int height, int channels, int bytes_per_channel, void *data);
  Image(int width, int height, int channels, int bytes_per_channel);
  Image(int width, int height, int channesl);
  Image(int width, int height);

  Image(const Image &other);
  Image(Image &&other);
  Image &operator=(const Image &other);
  Image &operator=(Image &&other);

  int width() const;
  int height() const;
  void set_width(int width);
  void set_height(int height);

  void *Data() const;
  void *MutableData();

private:
  class Impl;
  std::shared_ptr<Impl> impl_;
};