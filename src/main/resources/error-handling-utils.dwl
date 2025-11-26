/**
 * Error Handling Utilities
 *
 * Provides standardized error handling functions for ChainSync platform
 * Including correlation IDs, error response formatting, and error code management
 */
%dw 2.0

import * from dw::core::Strings

/**
 * Generates a unique correlation ID for request tracing
 * Format: timestamp-random
 */
fun generateCorrelationId(): String = do {
    var timestamp = now() as String {format: "yyyyMMddHHmmssSSS"}
    var random = randomInt(99999)
    ---
    "$(timestamp)-$(random)"
}

/**
 * Builds a standardized error response
 *
 * @param errorCode - Standardized error code (e.g., "ENV_FACILITY_NOT_FOUND")
 * @param message - Human-readable error message
 * @param details - Additional error details (optional)
 * @param correlationId - Request correlation ID (optional, will be generated if not provided)
 * @param httpStatus - HTTP status code (optional, default: 500)
 * @return Standardized error response object
 */
fun buildErrorResponse(
    errorCode: String,
    message: String,
    details: Any = null,
    correlationId: String = generateCorrelationId(),
    httpStatus: Number = 500
): Object = {
    error: {
        code: errorCode,
        message: message,
        (details: details) if (details != null),
        correlationId: correlationId,
        timestamp: now() as String {format: "yyyy-MM-dd'T'HH:mm:ss'Z'"},
        httpStatus: httpStatus
    }
}

/**
 * Builds error response from exception
 *
 * @param exception - Exception object from error handler
 * @param errorCode - Standardized error code
 * @param correlationId - Request correlation ID (optional)
 * @return Standardized error response object
 */
fun buildErrorResponseFromException(
    exception: Any,
    errorCode: String,
    correlationId: String = generateCorrelationId()
): Object = do {
    var errorMessage = exception.description default exception.detailedDescription default "An unexpected error occurred"
    var httpStatus = if (exception.errorType.namespace == "HTTP")
        (exception.errorType.identifier replace /\D/ with "") as Number default 500
    else 500
    ---
    buildErrorResponse(
        errorCode,
        errorMessage,
        {
            errorType: exception.errorType.identifier default "UNKNOWN",
            (causeMessage: exception.cause.description) if (exception.cause != null)
        },
        correlationId,
        httpStatus
    )
}

/**
 * Maps HTTP status code to standardized error code
 *
 * @param statusCode - HTTP status code
 * @param context - Context string (e.g., "WEATHER_API", "FACILITY")
 * @return Standardized error code
 */
fun mapHttpStatusToErrorCode(statusCode: Number, context: String): String =
    context ++ "_" ++ (statusCode match {
        case 400 -> "BAD_REQUEST"
        case 401 -> "UNAUTHORIZED"
        case 403 -> "FORBIDDEN"
        case 404 -> "NOT_FOUND"
        case 405 -> "METHOD_NOT_ALLOWED"
        case 408 -> "TIMEOUT"
        case 409 -> "CONFLICT"
        case 422 -> "VALIDATION_FAILED"
        case 429 -> "RATE_LIMIT_EXCEEDED"
        case 500 -> "INTERNAL_ERROR"
        case 502 -> "BAD_GATEWAY"
        case 503 -> "SERVICE_UNAVAILABLE"
        case 504 -> "GATEWAY_TIMEOUT"
        else -> "ERROR"
    })

/**
 * Determines if an error is retryable based on error type
 *
 * @param errorType - Error type string (e.g., "HTTP:CONNECTIVITY")
 * @return true if error is retryable, false otherwise
 */
fun isRetryableError(errorType: String): Boolean =
    errorType contains "CONNECTIVITY" or
    errorType contains "TIMEOUT" or
    errorType contains "503" or
    errorType contains "504" or
    errorType contains "429"

/**
 * Determines if an error is critical (should propagate)
 *
 * @param errorType - Error type string
 * @param criticalFlows - Array of critical flow names
 * @param currentFlow - Current flow name
 * @return true if error is critical, false otherwise
 */
fun isCriticalError(
    errorType: String,
    criticalFlows: Array = ["emergency", "alert", "incident", "dispatch"],
    currentFlow: String = ""
): Boolean = do {
    var isAuthError = errorType contains "UNAUTHORIZED" or errorType contains "FORBIDDEN"
    var isInCriticalFlow = criticalFlows some ((flow) -> currentFlow contains flow)
    ---
    isAuthError or isInCriticalFlow
}

/**
 * Builds a fallback response for graceful degradation
 *
 * @param originalRequest - Original request context
 * @param errorMessage - Error message
 * @param fallbackData - Fallback data to return
 * @param correlationId - Request correlation ID
 * @return Fallback response with warning
 */
fun buildFallbackResponse(
    originalRequest: String,
    errorMessage: String,
    fallbackData: Any,
    correlationId: String = generateCorrelationId()
): Object = {
    status: "degraded",
    warning: "Primary service unavailable, returning fallback data",
    message: errorMessage,
    correlationId: correlationId,
    timestamp: now() as String {format: "yyyy-MM-dd'T'HH:mm:ss'Z'"},
    data: fallbackData
}

/**
 * Calculates exponential backoff delay
 *
 * @param attemptNumber - Current retry attempt (1-based)
 * @param baseDelayMs - Base delay in milliseconds (default: 1000)
 * @param maxDelayMs - Maximum delay in milliseconds (default: 30000)
 * @return Delay in milliseconds
 */
fun calculateBackoffDelay(
    attemptNumber: Number,
    baseDelayMs: Number = 1000,
    maxDelayMs: Number = 30000
): Number = do {
    var exponentialDelay = baseDelayMs * (2 pow (attemptNumber - 1))
    ---
    if (exponentialDelay > maxDelayMs) maxDelayMs else exponentialDelay
}

/**
 * Sanitizes error details for logging (removes sensitive data)
 *
 * @param errorDetails - Error details object
 * @return Sanitized error details
 */
fun sanitizeErrorDetails(errorDetails: Any): Any =
    errorDetails match {
        case obj is Object -> obj mapObject ((value, key) ->
            (key): if (["password", "token", "apiKey", "secret", "authorization"] contains (key as String))
                "***REDACTED***"
            else
                sanitizeErrorDetails(value)
        )
        case arr is Array -> arr map sanitizeErrorDetails($)
        else -> errorDetails
    }

/**
 * Formats error for structured logging
 *
 * @param error - Error object or exception
 * @param correlationId - Request correlation ID
 * @param additionalContext - Additional context (optional)
 * @return Formatted log entry
 */
fun formatErrorLog(
    error: Any,
    correlationId: String,
    additionalContext: Object = {}
): Object = {
    level: "ERROR",
    correlationId: correlationId,
    timestamp: now() as String {format: "yyyy-MM-dd'T'HH:mm:ss'Z'"},
    message: error.description default error.message default "Unknown error",
    errorType: error.errorType.identifier default error.code default "UNKNOWN",
    (details: sanitizeErrorDetails(error.details)) if (error.details != null),
    (context: additionalContext) if (!isEmpty(additionalContext))
}
