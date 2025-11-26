/**
 * Error Code Catalog
 *
 * Standardized error codes for ChainSync platform
 * Format: {DOMAIN}_{ERROR_TYPE}
 */
%dw 2.0

// ============================================
// GENERAL / PLATFORM ERROR CODES
// ============================================
var PLATFORM_INTERNAL_ERROR = "PLATFORM_INTERNAL_ERROR"
var PLATFORM_SERVICE_UNAVAILABLE = "PLATFORM_SERVICE_UNAVAILABLE"
var PLATFORM_BAD_REQUEST = "PLATFORM_BAD_REQUEST"
var PLATFORM_UNAUTHORIZED = "PLATFORM_UNAUTHORIZED"
var PLATFORM_FORBIDDEN = "PLATFORM_FORBIDDEN"
var PLATFORM_NOT_FOUND = "PLATFORM_NOT_FOUND"
var PLATFORM_METHOD_NOT_ALLOWED = "PLATFORM_METHOD_NOT_ALLOWED"
var PLATFORM_VALIDATION_FAILED = "PLATFORM_VALIDATION_FAILED"
var PLATFORM_TIMEOUT = "PLATFORM_TIMEOUT"

// ============================================
// ENVIRONMENTAL FACILITIES ERROR CODES
// ============================================
var FACILITY_NOT_FOUND = "FACILITY_NOT_FOUND"
var FACILITY_INVALID_ID = "FACILITY_INVALID_ID"
var FACILITY_QUERY_FAILED = "FACILITY_QUERY_FAILED"
var FACILITY_CREATION_FAILED = "FACILITY_CREATION_FAILED"
var FACILITY_UPDATE_FAILED = "FACILITY_UPDATE_FAILED"
var FACILITY_INACTIVE = "FACILITY_INACTIVE"
var FACILITY_INCIDENT_CREATION_FAILED = "FACILITY_INCIDENT_CREATION_FAILED"

// ============================================
// ENVIRONMENTAL SERVICE VEHICLES ERROR CODES
// ============================================
var VEHICLE_NOT_FOUND = "VEHICLE_NOT_FOUND"
var VEHICLE_INVALID_ID = "VEHICLE_INVALID_ID"
var VEHICLE_NOT_AVAILABLE = "VEHICLE_NOT_AVAILABLE"
var VEHICLE_DISPATCH_FAILED = "VEHICLE_DISPATCH_FAILED"
var VEHICLE_ALREADY_DISPATCHED = "VEHICLE_ALREADY_DISPATCHED"
var VEHICLE_MAINTENANCE_MODE = "VEHICLE_MAINTENANCE_MODE"
var VEHICLE_INVALID_LOCATION = "VEHICLE_INVALID_LOCATION"
var VEHICLE_QUERY_FAILED = "VEHICLE_QUERY_FAILED"

// ============================================
// ENVIRONMENTAL DATA & MONITORING ERROR CODES
// ============================================
var ENV_DATA_STATION_NOT_FOUND = "ENV_DATA_STATION_NOT_FOUND"
var ENV_DATA_INVALID_STATION_ID = "ENV_DATA_INVALID_STATION_ID"
var ENV_DATA_RETRIEVAL_FAILED = "ENV_DATA_RETRIEVAL_FAILED"
var ENV_DATA_INVALID_READINGS = "ENV_DATA_INVALID_READINGS"
var ENV_DATA_SUBMISSION_FAILED = "ENV_DATA_SUBMISSION_FAILED"
var ENV_DATA_MISSING_PARAMETERS = "ENV_DATA_MISSING_PARAMETERS"
var ENV_DATA_OUT_OF_RANGE = "ENV_DATA_OUT_OF_RANGE"

// ============================================
// EMERGENCY ALERT ERROR CODES
// ============================================
var ALERT_CREATION_FAILED = "ALERT_CREATION_FAILED"
var ALERT_INVALID_SEVERITY = "ALERT_INVALID_SEVERITY"
var ALERT_MISSING_REQUIRED_FIELDS = "ALERT_MISSING_REQUIRED_FIELDS"
var ALERT_QUERY_FAILED = "ALERT_QUERY_FAILED"
var ALERT_NOT_FOUND = "ALERT_NOT_FOUND"
var ALERT_UPDATE_FAILED = "ALERT_UPDATE_FAILED"
var ALERT_NOTIFICATION_FAILED = "ALERT_NOTIFICATION_FAILED"

// ============================================
// REGULATORY COMPLIANCE ERROR CODES
// ============================================
var COMPLIANCE_REPORT_CREATION_FAILED = "COMPLIANCE_REPORT_CREATION_FAILED"
var COMPLIANCE_INVALID_REPORT_TYPE = "COMPLIANCE_INVALID_REPORT_TYPE"
var COMPLIANCE_QUERY_FAILED = "COMPLIANCE_QUERY_FAILED"
var COMPLIANCE_MISSING_DATA = "COMPLIANCE_MISSING_DATA"
var COMPLIANCE_VALIDATION_FAILED = "COMPLIANCE_VALIDATION_FAILED"

// ============================================
// EXTERNAL API ERROR CODES - WEATHER
// ============================================
var WEATHER_API_UNAVAILABLE = "WEATHER_API_UNAVAILABLE"
var WEATHER_API_TIMEOUT = "WEATHER_API_TIMEOUT"
var WEATHER_API_INVALID_RESPONSE = "WEATHER_API_INVALID_RESPONSE"
var WEATHER_API_UNAUTHORIZED = "WEATHER_API_UNAUTHORIZED"
var WEATHER_API_RATE_LIMIT = "WEATHER_API_RATE_LIMIT"
var WEATHER_API_BAD_REQUEST = "WEATHER_API_BAD_REQUEST"
var WEATHER_API_NOT_FOUND = "WEATHER_API_NOT_FOUND"
var WEATHER_API_INTERNAL_ERROR = "WEATHER_API_INTERNAL_ERROR"

// ============================================
// EXTERNAL API ERROR CODES - AIR QUALITY
// ============================================
var AIR_QUALITY_API_UNAVAILABLE = "AIR_QUALITY_API_UNAVAILABLE"
var AIR_QUALITY_API_TIMEOUT = "AIR_QUALITY_API_TIMEOUT"
var AIR_QUALITY_API_INVALID_RESPONSE = "AIR_QUALITY_API_INVALID_RESPONSE"
var AIR_QUALITY_API_RATE_LIMIT = "AIR_QUALITY_API_RATE_LIMIT"
var AIR_QUALITY_API_NOT_FOUND = "AIR_QUALITY_API_NOT_FOUND"
var AIR_QUALITY_API_INTERNAL_ERROR = "AIR_QUALITY_API_INTERNAL_ERROR"

// ============================================
// EXTERNAL API ERROR CODES - SLOTIFY
// ============================================
var SLOTIFY_API_UNAVAILABLE = "SLOTIFY_API_UNAVAILABLE"
var SLOTIFY_API_TIMEOUT = "SLOTIFY_API_TIMEOUT"
var SLOTIFY_API_UNAUTHORIZED = "SLOTIFY_API_UNAUTHORIZED"
var SLOTIFY_API_FORBIDDEN = "SLOTIFY_API_FORBIDDEN"
var SLOTIFY_API_RATE_LIMIT = "SLOTIFY_API_RATE_LIMIT"
var SLOTIFY_API_BAD_REQUEST = "SLOTIFY_API_BAD_REQUEST"
var SLOTIFY_API_NOT_FOUND = "SLOTIFY_API_NOT_FOUND"
var SLOTIFY_API_INVALID_RESPONSE = "SLOTIFY_API_INVALID_RESPONSE"
var SLOTIFY_API_INTERNAL_ERROR = "SLOTIFY_API_INTERNAL_ERROR"
var SLOTIFY_MEETING_CREATION_FAILED = "SLOTIFY_MEETING_CREATION_FAILED"
var SLOTIFY_MEETING_UPDATE_FAILED = "SLOTIFY_MEETING_UPDATE_FAILED"
var SLOTIFY_MEETING_CANCELLATION_FAILED = "SLOTIFY_MEETING_CANCELLATION_FAILED"
var SLOTIFY_AVAILABILITY_CHECK_FAILED = "SLOTIFY_AVAILABILITY_CHECK_FAILED"

// ============================================
// AI AGENT INTEGRATION ERROR CODES
// ============================================
var AI_AGENT_MISSING_FACILITY_ID = "AI_AGENT_MISSING_FACILITY_ID"
var AI_AGENT_DATA_RETRIEVAL_FAILED = "AI_AGENT_DATA_RETRIEVAL_FAILED"
var AI_AGENT_ALERT_PROCESSING_FAILED = "AI_AGENT_ALERT_PROCESSING_FAILED"
var AI_AGENT_EMERGENCY_PROCESSING_FAILED = "AI_AGENT_EMERGENCY_PROCESSING_FAILED"
var AI_AGENT_INVALID_PAYLOAD = "AI_AGENT_INVALID_PAYLOAD"

// ============================================
// DATABASE ERROR CODES
// ============================================
var DB_CONNECTION_FAILED = "DB_CONNECTION_FAILED"
var DB_QUERY_FAILED = "DB_QUERY_FAILED"
var DB_TIMEOUT = "DB_TIMEOUT"
var DB_CONSTRAINT_VIOLATION = "DB_CONSTRAINT_VIOLATION"
var DB_DUPLICATE_ENTRY = "DB_DUPLICATE_ENTRY"

// ============================================
// ERROR CODE METADATA
// ============================================

/**
 * Gets HTTP status code for a given error code
 */
fun getHttpStatus(errorCode: String): Number =
    errorCode match {
        // 400 Bad Request
        case s if (s contains "BAD_REQUEST" or s contains "INVALID" or s contains "MISSING") -> 400

        // 401 Unauthorized
        case s if (s contains "UNAUTHORIZED") -> 401

        // 403 Forbidden
        case s if (s contains "FORBIDDEN") -> 403

        // 404 Not Found
        case s if (s contains "NOT_FOUND") -> 404

        // 405 Method Not Allowed
        case s if (s contains "METHOD_NOT_ALLOWED") -> 405

        // 408 Request Timeout
        case s if (s contains "TIMEOUT") -> 408

        // 409 Conflict
        case s if (s contains "ALREADY_" or s contains "DUPLICATE") -> 409

        // 422 Unprocessable Entity
        case s if (s contains "VALIDATION_FAILED" or s contains "OUT_OF_RANGE") -> 422

        // 429 Too Many Requests
        case s if (s contains "RATE_LIMIT") -> 429

        // 503 Service Unavailable
        case s if (s contains "UNAVAILABLE" or s contains "MAINTENANCE") -> 503

        // 500 Internal Server Error (default)
        else -> 500
    }

/**
 * Gets user-friendly message for error code
 */
fun getErrorMessage(errorCode: String): String =
    errorCode match {
        // Facilities
        case "FACILITY_NOT_FOUND" -> "The requested environmental facility was not found"
        case "FACILITY_INVALID_ID" -> "Invalid facility ID format"
        case "FACILITY_INACTIVE" -> "The facility is currently inactive"

        // Vehicles
        case "VEHICLE_NOT_FOUND" -> "The requested service vehicle was not found"
        case "VEHICLE_NOT_AVAILABLE" -> "The vehicle is not available for dispatch"
        case "VEHICLE_ALREADY_DISPATCHED" -> "The vehicle is already dispatched to another location"
        case "VEHICLE_MAINTENANCE_MODE" -> "The vehicle is currently in maintenance mode"

        // Environmental Data
        case "ENV_DATA_STATION_NOT_FOUND" -> "Monitoring station not found"
        case "ENV_DATA_INVALID_READINGS" -> "Invalid sensor readings provided"
        case "ENV_DATA_OUT_OF_RANGE" -> "Sensor readings are outside acceptable range"

        // Alerts
        case "ALERT_INVALID_SEVERITY" -> "Invalid alert severity level"
        case "ALERT_MISSING_REQUIRED_FIELDS" -> "Required alert fields are missing"

        // External APIs
        case "WEATHER_API_UNAVAILABLE" -> "Weather service is temporarily unavailable"
        case "AIR_QUALITY_API_UNAVAILABLE" -> "Air quality service is temporarily unavailable"
        case "SLOTIFY_API_UNAVAILABLE" -> "Scheduling service is temporarily unavailable"
        case "SLOTIFY_API_UNAUTHORIZED" -> "Invalid Slotify API credentials"

        // AI Agent
        case "AI_AGENT_MISSING_FACILITY_ID" -> "Facility ID is required for AI analysis"

        // Database
        case "DB_CONNECTION_FAILED" -> "Database connection failed"
        case "DB_DUPLICATE_ENTRY" -> "A record with this information already exists"

        // Default
        else -> "An error occurred processing your request"
    }

/**
 * Determines if error should be retried
 */
fun isRetryable(errorCode: String): Boolean =
    errorCode contains "TIMEOUT" or
    errorCode contains "UNAVAILABLE" or
    errorCode contains "RATE_LIMIT" or
    errorCode contains "CONNECTION_FAILED"

/**
 * Determines if error requires immediate attention
 */
fun isCritical(errorCode: String): Boolean =
    errorCode contains "EMERGENCY" or
    errorCode contains "ALERT_CREATION_FAILED" or
    errorCode contains "INCIDENT" or
    errorCode contains "DISPATCH_FAILED"
