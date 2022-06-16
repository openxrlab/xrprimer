#include "logging.h"
#include <memory>
#include <spdlog/sinks/stdout_color_sinks.h>
#include <spdlog/spdlog.h>

#define LOG_MSGBUF_INIT 512

namespace roam {

static spdlog::logger *logger() {
    static std::unique_ptr<spdlog::logger> s_logger;
    if (!s_logger) {
        auto console_sink =
            std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
        console_sink->set_level(spdlog::level::trace);
        console_sink->set_pattern("%Y-%m-%d %T.%e - [ROAM][%^%l%$] %v");
        s_logger = std::make_unique<spdlog::logger>(
            "roam", spdlog::sinks_init_list{console_sink});
        s_logger->set_level(spdlog::level::trace);
    }
    return s_logger.get();
}

void log_message(XRLogLevel level, const char *format, ...) {
    static std::vector<char> msgbuf(LOG_MSGBUF_INIT);
    va_list vargs1, vargs2;
    va_start(vargs1, format);
    va_copy(vargs2, vargs1);
    int len = vsnprintf(nullptr, 0, format, vargs1);
    va_end(vargs1);
    if (msgbuf.size() < len + 1) {
        msgbuf.resize(len + 1);
    }
    vsnprintf(msgbuf.data(), msgbuf.size(), format, vargs2);
    va_end(vargs2);
    spdlog::level::level_enum lvl;
    switch (level) {
    case XR_LOG_DEBUG:
        lvl = spdlog::level::debug;
        break;
    case XR_LOG_INFO:
        lvl = spdlog::level::info;
        break;
    case XR_LOG_NOTICE:
        lvl = spdlog::level::info;
        break;
    case XR_LOG_WARNING:
        lvl = spdlog::level::warn;
        break;
    case XR_LOG_ERR:
        lvl = spdlog::level::err;
        break;
    case XR_LOG_CRIT:
        lvl = spdlog::level::critical;
        break;
    case XR_LOG_ALERT:
        lvl = spdlog::level::critical;
        break;
    case XR_LOG_EMERG:
        lvl = spdlog::level::critical;
        break;
    }
    logger()->log(lvl, msgbuf.data());
}

} // namespace roam
