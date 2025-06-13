%dw 2.0
// Global DataWeave Functions for ChainSync Platform

/**
 * Calculates total emissions from individual components
 */
fun calculateTotalEmissions(emissions: Object): Number = 
    (emissions.co2 default 0) + 
    (emissions.nox default 0) + 
    (emissions.sox default 0) + 
    (emissions.pm default 0)

/**
 * Calculates fuel efficiency based on consumption and distance
 */
fun calculateFuelEfficiency(fuelConsumption: Number, distance: Number): Number = 
    if (distance > 0) fuelConsumption / distance else 0

/**
 * Formats vessel ID to standard format
 */
fun formatVesselId(vesselId: String): String = 
    upper(vesselId) replace /[^A-Z0-9\-]/ with ""

/**
 * Validates emissions data structure
 */
fun validateEmissionsData(emissions: Object): Boolean = 
    emissions.co2? and emissions.nox? and emissions.sox? and
    (emissions.co2 >= 0) and (emissions.nox >= 0) and (emissions.sox >= 0)

/**
 * Generates correlation ID for tracking
 */
fun generateCorrelationId(): String = 
    "CHAIN-" ++ now() as String {format: "yyyyMMddHHmmssSSS"} ++ "-" ++ randomInt(9999)

/**
 * Calculates emissions compliance status
 */
fun checkEmissionsCompliance(emissions: Object, limits: Object): Object = {
    compliant: emissions.co2 <= limits.co2 and 
               emissions.nox <= limits.nox and 
               emissions.sox <= limits.sox,
    violations: [] ++ 
        (if (emissions.co2 > limits.co2) ["CO2_LIMIT_EXCEEDED"] else []) ++
        (if (emissions.nox > limits.nox) ["NOX_LIMIT_EXCEEDED"] else []) ++
        (if (emissions.sox > limits.sox) ["SOX_LIMIT_EXCEEDED"] else [])
}

/**
 * Converts coordinates to decimal degrees
 */
fun convertToDecimalDegrees(degrees: Number, minutes: Number, seconds: Number, direction: String): Number = 
    (degrees + (minutes / 60) + (seconds / 3600)) * (if (direction == "S" or direction == "W") -1 else 1)

/**
 * Calculates distance between two coordinates (Haversine formula)
 */
fun calculateDistance(lat1: Number, lon1: Number, lat2: Number, lon2: Number): Number = do {
    var R = 6371 // Earth's radius in km
    var dLat = (lat2 - lat1) * pi / 180
    var dLon = (lon2 - lon1) * pi / 180
    var a = sin(dLat/2) * sin(dLat/2) + 
            cos(lat1 * pi / 180) * cos(lat2 * pi / 180) * 
            sin(dLon/2) * sin(dLon/2)
    var c = 2 * atan2(sqrt(a), sqrt(1-a))
    ---
    R * c
}

/**
 * Formats timestamp to ISO 8601
 */
fun formatTimestamp(timestamp: DateTime): String = 
    timestamp as String {format: "yyyy-MM-dd'T'HH:mm:ss'Z'"}

/**
 * Masks sensitive data for logging
 */
fun maskSensitiveData(data: String): String = 
    if (sizeOf(data) > 4) 
        data[0 to 3] ++ "*" * (sizeOf(data) - 8) ++ data[-4 to -1]
    else 
        "*" * sizeOf(data)