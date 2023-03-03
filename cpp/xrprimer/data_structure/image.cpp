// Copyright (c) OpenXRLab. All rights reserved.

#include <algorithm>
#include <data_structure/image.h>
#include <map>
#include <memory>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <vector>

/**
 * PixelFormatDesc
 */
struct PixelFormatDesc {
    int depth;    //< bytes every channel
    int channels; //< format channels
};

static std::map<PixelFormat, PixelFormatDesc> kPixelDesc = {
    {NONE, {0, 0}},  {RGB24, {1, 3}},    {BGR24, {1, 3}},   {RGBA, {1, 4}},
    {GRAY8, {1, 1}}, {GRAY16BE, {2, 1}}, {GRAY16BE, {2, 1}}};

static int FormatDepth(PixelFormat format) {
    if (format < FORMAT_NUM) {
        return kPixelDesc[format].depth;
    }
    return 0;
}

static int FormatChannels(PixelFormat format) {
    if (format < FORMAT_NUM) {
        return kPixelDesc[format].channels;
    }
    return 0;
}

/**
 * Class Image::Impl
 */
class Image::Impl {

    friend class Image;

  public:
    Impl() {}
    ~Impl() { data_ = nullptr; }

    Impl(int width, int height, int step, PixelFormat format)
        : allocated_(true), width_(width), height_(height), step_(step),
          format_(format) {
        storage_data_.reset(new uint8_t[height * step],
                            [](uint8_t *data) { delete[] data; });
        data_ = storage_data_.get();
    }

    Impl(int width, int height, int step, PixelFormat format, void *data)
        : allocated_(false), width_(width), height_(height), step_(step),
          format_(format) {
        data_ = data;
        // proxy
        storage_data_.reset(static_cast<uint8_t *>(data), [](uint8_t *data) {});
    }

    Impl(int width, int height, PixelFormat format)
        : Impl(width, height,
               width * FormatChannels(format) * FormatDepth(format), format) {}

    std::shared_ptr<Impl> Clone() const {
        std::shared_ptr<Impl> newVal = std::make_shared<Impl>();
        copyTo(newVal.get());
        return newVal;
    }

    bool copyTo(Impl *impl) const {

        if (impl == nullptr) {
            return false;
        }

        if (this == impl) {
            return true;
        }

        if (empty()) {
            *impl = Impl();
            return true;
        }

        if (impl->empty()) {
            *impl = Impl(width_, height_, format_);
        }

        if (impl->format_ == format_ && impl->width_ == width_ &&
            impl->height_ == height_) {

            std::memcpy(impl->data_, this->data_, this->height_ * this->step_);

        } else {
            // TODO: mismatch format, maybe data is external
            fprintf(stderr, "Image::Impl::copyTo: mismatch format\n");
            return false;
        }

        return true;
    }

    bool empty() const {
        return (storage_data_ == nullptr) || (data_ == nullptr);
    }

  private:
    int width_ = 0;
    int height_ = 0;
    int step_ = 0;
    PixelFormat format_;
    std::shared_ptr<uint8_t> storage_data_;
    void *data_ = nullptr;
    int64_t ts_ = -1;        //< timestamp
    int64_t stream_id_ = -1; //< stream_id
    bool allocated_ = false;
};

/**
 * Class Image
 */
Image::Image() {}

Image::~Image() {}

Image::Image(int width, int height, PixelFormat format) {
    impl_ = std::make_shared<Impl>(width, height, format);
}

Image::Image(int width, int height, int step, PixelFormat format) {
    impl_ = std::make_shared<Impl>(width, height, step, format);
}

Image::Image(int width, int height, int step, PixelFormat format, void *data) {
    impl_ = std::make_shared<Impl>(width, height, step, format, data);
}

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

int64_t Image::timestamp() const {
    if (this->impl_) {
        return this->impl_->ts_;
    }
    return -1;
}

void Image::set_timestamp(int64_t timestamp) {
    if (this->impl_) {
        this->impl_->ts_ = timestamp;
    }
}

int64_t Image::stream_id() const {
    if (this->impl_) {
        return this->impl_->stream_id_;
    }
    return -1;
}

void Image::set_stream_id(int64_t stream_id) {
    if (this->impl_) {
        this->impl_->stream_id_ = stream_id;
    }
}

int Image::width() const {
    if (this->impl_) {
        return this->impl_->width_;
    }
    return 0;
}

int Image::height() const {
    if (this->impl_) {
        return this->impl_->height_;
    }
    return 0;
}

PixelFormat Image::format() const {
    if (this->impl_) {
        return this->impl_->format_;
    }
    return NONE;
}

int Image::elemSize() const { return channels() * depth(); }

int Image::channels() const {
    if (this->impl_) {
        return FormatChannels(this->impl_->format_);
    }
    return 0;
}

int Image::depth() const {
    if (this->impl_) {
        return FormatDepth(this->impl_->format_);
    }
    return 0;
}

int Image::step() const {
    if (this->impl_) {
        return this->impl_->step_;
    }
    return 0;
}

const void *Image::data() const {
    if (this->impl_) {
        return this->impl_->data_;
    }
    return nullptr;
}

void *Image::mutable_data() { return const_cast<void *>(data()); }

Image Image::clone() const {
    Image newVal;
    if (this->impl_) {
        newVal.impl_ = this->impl_->Clone();
    }
    return newVal;
}

bool Image::copyTo(Image *image) {

    if (image == nullptr) {
        return false;
    }

    if (this == image) {
        return true;
    }

    if (!image->impl_) {
        image->impl_ = std::make_shared<Impl>();
    }

    return impl_->copyTo(image->impl_.get());
}

bool Image::empty() {
    if (this->impl_) {
        return this->impl_->empty();
    }
    return true;
}
