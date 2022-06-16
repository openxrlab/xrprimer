#ifndef XR_LOGGINHT_H_
#define XR_LOGGINHT_H_

enum XRLogLevel {
    XR_LOG_DEBUG = -1,  /**< debug message                      **/
    XR_LOG_INFO = 0,    /**< informational message              **/
    XR_LOG_NOTICE = 1,  /**< normal, but significant, condition **/
    XR_LOG_WARNING = 2, /**< warning conditions                 **/
    XR_LOG_ERR = 3,     /**< error conditions                   **/
    XR_LOG_CRIT = 4,    /**< critical conditions                **/
    XR_LOG_ALERT = 5,   /**< action must be taken immediately   **/
    XR_LOG_EMERG = 6    /**< system is unusable                 **/
};

void log_message(XRLogLevel level, const char *format, ...);

#define xr_log_emergency(...) log_message(XR_LOG_EMERG, __VA_ARGS__)
#define xr_log_alert(...) log_message(XR_LOG_ALERT, __VA_ARGS__)
#define xr_log_critical(...) log_message(XR_LOG_CRIT, __VA_ARGS__)
#define xr_log_error(...) log_message(XR_LOG_ERR, __VA_ARGS__)
#define xr_log_warning(...) log_message(XR_LOG_WARNING, __VA_ARGS__)
#define xr_log_notice(...) log_message(XR_LOG_NOTICE, __VA_ARGS__)
#define xr_log_info(...) log_message(XR_LOG_INFO, __VA_ARGS__)
#define xr_log_debug(...) log_message(XR_LOG_DEBUG, __VA_ARGS__)

#define xr_runtime_assert(condition, message)                                  \
    do {                                                                       \
        if (!(condition)) {                                                    \
            log_error("Assertion failed at " __FILE__                          \
                      ":%d : %s\nWhen testing condition:\n    %s",             \
                      __LINE__, message, #condition);                          \
            abort();                                                           \
        }                                                                      \
    } while (0)

#endif // XR_LOGGINHT_H_
