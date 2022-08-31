#pragma once

#include <memory>
#include <stdint.h>
#include <vector>

enum PixelFormat {
    NONE,
    RGB24,
    BGR24,
    RGBA,
    GRAY8,
    GRAY16BE,
    GRAY16LE,
    FORMAT_NUM,
};

class Image {

  public:
    Image();
    ~Image();

    /**
     * @brief Construct a new Image object
     *
     * @param width
     * @param height
     * @param format
     */
    Image(int width, int height, PixelFormat format);

    /**
     * @brief Construct a new Image object
     *
     * @param width
     * @param height
     * @param widthStep
     * @param format
     */
    Image(int width, int height, int widthStep, PixelFormat format);

    /**
     * @brief Construct a new Image object
     *
     * @param width
     * @param height
     * @param widthStep
     * @param format
     * @param data Pointer to the user data. constructors that take data
     * and step parameters do not allocate data. Instead, they just
     * initialize the header that points to the specified data, which means
     * that no data is copied. This operation is very efficient and can be used
     * to process external data using `Image` class. The external data is not
     * automatically deallocated, so you should take care of it.
     */
    Image(int width, int height, int widthStep, PixelFormat format, void *data);

    Image(const Image &other);
    Image(Image &&other);
    Image &operator=(const Image &other);
    Image &operator=(Image &&other);

    /**
     * @brief Image timestamp
     *
     * @return int64_t
     */
    int64_t timestamp() const;

    /**
     * @brief Set the timestamp object
     *
     * @param timestamp
     */
    void set_timestamp(int64_t timestamp);

    /**
     * @brief Image stream index
     *
     * @return int64_t
     */
    int64_t stream_id() const;

    /**
     * @brief Set the stream id object
     *
     * @param stream_id
     */
    void set_stream_id(int64_t stream_id);

    /**
     * @brief Image width in pixels.
     *
     * @return int
     */
    int width() const;

    /**
     * @brief Image height in pixels.
     *
     * @return int
     */
    int height() const;

    /**
     * @brief Image format @see PixelFormat
     *
     * @return PixelFormat
     */
    PixelFormat format() const;

    /**
     * @brief the size of each pixel in bytes
     *
     * @return int  same as channels() * depth()
     */
    int elemSize() const;

    /**
     * @brief Image channels, supporet 1,2,3 or 4
     *
     * @return int
     */
    int channels() const;

    /**
     * @brief Image per channel bytes
     *
     * @return int, supported 1,2,3,4
     */
    int depth() const;

    /**
     * @brief Size of aligned image row in bytes.
     *
     * @return int
     */
    int step() const;

    /**
     * @brief Pointer to aligned image data
     *
     * @return void*
     */
    const void *data() const;

    /**
     * @brief Pointer to aligned image data
     *
     * @return void*
     */
    void *mutable_data();

    /**
     * @brief
     *
     * @return Image
     */
    Image clone() const;

    /**
     * @brief
     *
     * @param image
     * @return true
     * @return false
     */
    bool copyTo(Image *image);

    /**
     * @brief
     *
     * @return true
     * @return false
     */
    bool empty();

  private:
    class Impl;
    std::shared_ptr<Impl> impl_ = nullptr;
};
