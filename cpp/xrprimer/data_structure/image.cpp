#include <algorithm>
#include <data_structure/image.h>
#include <stdint.h>
#include <string.h>
#include <vector>

// Class Image::Impl
class Image::Impl {

  friend class Image;

public:
  Impl() {}
  ~Impl() {}

  Impl(int width, int height, int channels, int bytes_per_channel, void *data)
      : width_(width), height_(height), num_of_channels_(channels),
        bytes_per_channel_(bytes_per_channel) {
    if (data) {
      data_.resize(width_ * height_ * num_of_channels_ * bytes_per_channel_);
      memcpy(data_.data(), data, data_.size());
    }
  }

  Impl(int width, int height, int channels, int bytes_per_channel)
      : Impl(width, height, channels, bytes_per_channel, nullptr) {}

  Impl(int width, int height, int channesl)
      : Impl(width, height, channesl, 1, nullptr) {}

  Impl(int width, int height) : Impl(width, height, 3, 1, nullptr) {}

private:
  /// Width of the image.
  int width_ = 0;
  /// Height of the image.
  int height_ = 0;
  /// Number of chanels in the image.
  int num_of_channels_ = 0;
  /// Number of bytes per channel.
  int bytes_per_channel_ = 0;
  /// Image storage buffer.
  std::vector<uint8_t> data_;
};

// Class Image
Image::Image(int width, int height, int channels, int bytes_per_channel,
             void *data) {
  impl_ =
      std::make_shared<Impl>(width, height, channels, bytes_per_channel, data);
}

Image::Image(int width, int height, int channels, int bytes_per_channel)
    : Image(width, height, channels, bytes_per_channel, nullptr) {}

Image::Image(int width, int height, int channesl)
    : Image(width, height, channesl, 1, nullptr) {}

Image::Image(int width, int height) : Image(width, height, 3, 1, nullptr) {}

Image::Image(const Image &other) { this->impl_ = other.impl_; }

Image::Image(Image &&other) { this->impl_ = other.impl_; }

Image &Image::operator=(const Image &other) {
  this->impl_ = other.impl_;
  return *this;
}

Image &Image::operator=(Image &&other) {
  this->impl_ = other.impl_;
  return *this;
}

void Image::set_width(int width) {
  if (this->impl_) {
    this->impl_->width_ = width;
  }
}
int Image::width() const {
  if (this->impl_) {
    return this->impl_->width_;
  }
  return 0;
}
void Image::set_height(int height) {
  if (this->impl_) {
    this->impl_->height_ = height;
  }
}

int Image::height() const {
  if (this->impl_) {
    return this->impl_->height_;
  }
  return 0;
}

void *Image::Data() const {
  if (this->impl_) {
    return this->impl_->data_.data();
  }
  return nullptr;
}

void *Image::MutableData() { return Data(); }