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

/**
 * Determines facility type based on environmental station data
 */
fun determineFacilityType(station: Object): String =
    if (station.airQuality.aqi > 100) "MONITORING_STATION"
    else if (station.weather.visibility < 10) "WEATHER_STATION"
    else "ENVIRONMENTAL_FACILITY"

/**
 * Maps operational status for environmental facilities
 */
fun getOperationalStatus(station: Object): Object = {
    operationMode: if (station.riskAssessment.coordinationRequired) "ALERT" else "NORMAL",
    equipmentStatus: "OPTIMAL",
    processingEfficiency: if (station.airQuality.aqi < 50) 98.5
                         else if (station.airQuality.aqi < 100) 95.0
                         else 90.0,
    backupSystems: ["Emergency Sensors", "Backup Communication"]
}

/**
 * Determines compliance status based on air quality index
 */
fun getComplianceStatus(station: Object): Object = {
    epaCompliant: station.airQuality.aqi < 150,
    stateCompliant: station.airQuality.aqi < 100,
    localCompliant: station.airQuality.aqi < 50,
    lastViolation: if (station.airQuality.aqi > 150) "2024-11-05" else null,
    nextInspection: "2025-08-15"
}

/**
 * Generates standardized error response object
 */
fun generateErrorResponse(code: String, message: String): Object = {
    error: {
        code: code,
        message: message,
        timestamp: now() as String {format: "yyyy-MM-dd'T'HH:mm:ss'Z'"}
    }
}

/**
 * Generates alert ID with timestamp
 */
fun generateAlertId(prefix: String, identifier: String): String =
    prefix ++ "_" ++ identifier ++ "_" ++ now() as String {format: "yyyyMMdd_HHmmss"}

/**
 * Generates workflow ID with timestamp
 */
fun generateWorkflowId(prefix: String): String =
    prefix ++ "_" ++ now() as String {format: "yyyyMMdd_HHmmss"}

/**
 * Generates meeting URL with timestamp
 */
fun generateMeetingUrl(baseUrl: String): String =
    baseUrl ++ now() as String {format: "yyyyMMddHHmmss"}

/**
 * Determines alert level based on risk score
 */
fun determineAlertLevel(riskScore: Number): String =
    if (riskScore >= 8) "CRITICAL"
    else if (riskScore >= 6) "EMERGENCY"
    else if (riskScore >= 4) "WARNING"
    else "ADVISORY"

/**
 * Determines severity level based on risk score
 */
fun determineSeverity(riskScore: Number): String =
    if (riskScore >= 8) "CRITICAL"
    else if (riskScore >= 6) "HIGH"
    else if (riskScore >= 4) "MEDIUM"
    else "LOW"

/**
 * Estimates affected population based on location/city
 */
fun estimateAffectedPopulation(city: String): Number =
    if (city == "New York" or city == "NYC") 125000
    else if (city == "London") 200000
    else if (city == "Beijing") 300000
    else if (city == "Los Angeles" or city == "LA") 150000
    else if (city == "Chicago") 100000
    else if (city == "Atlanta") 75000
    else 50000

/**
 * Generates coordination stakeholders based on alert level
 */
fun getCoordinationStakeholders(alertLevel: String): Array =
    if (alertLevel == "CRITICAL") [
        {name: "EPA Emergency Response", role: "Regulatory Authority"},
        {name: "State Environmental Health", role: "Health Department"},
        {name: "Local Emergency Management", role: "Emergency Coordination"},
        {name: "Water Quality Director", role: "Technical Lead"},
        {name: "Public Information Officer", role: "Communications"}
    ]
    else if (alertLevel == "EMERGENCY") [
        {name: "State Environmental Health", role: "Health Department"},
        {name: "Water Quality Director", role: "Technical Lead"},
        {name: "Operations Manager", role: "Facility Operations"}
    ]
    else [
        {name: "Water Quality Director", role: "Technical Lead"},
        {name: "Operations Manager", role: "Facility Operations"}
    ]

/**
 * Validates environmental reading is within safe thresholds
 */
fun isWithinSafeThreshold(value: Number, min: Number, max: Number): Boolean =
    value >= min and value <= max

/**
 * Calculates environmental risk score based on multiple parameters
 */
fun calculateEnvironmentalRiskScore(aqi: Number, waterQuality: Object, weatherSeverity: Number): Number = do {
    var aqiScore = if (aqi > 200) 4
                   else if (aqi > 150) 3
                   else if (aqi > 100) 2
                   else if (aqi > 50) 1
                   else 0

    var waterScore = if (waterQuality.ph? and not isWithinSafeThreshold(waterQuality.ph, 6.5, 8.5)) 3
                     else if (waterQuality.turbidity? and waterQuality.turbidity > 5.0) 2
                     else if (waterQuality.do? and waterQuality.do < 5.0) 2
                     else 0

    var weatherScore = if (weatherSeverity >= 8) 3
                       else if (weatherSeverity >= 5) 2
                       else if (weatherSeverity >= 3) 1
                       else 0
    ---
    aqiScore + waterScore + weatherScore
}

/**
 * Formats facility ID to standard format
 */
fun formatFacilityId(facilityId: String): String =
    upper(facilityId) replace /[^A-Z0-9_\-]/ with ""

/**
 * Generates incident ID with timestamp and facility
 */
fun generateIncidentId(facilityId: String): String =
    "INC_" ++ formatFacilityId(facilityId) ++ "_" ++ now() as String {format: "yyyyMMddHHmmss"}

/**
 * Determines if coordination is required based on risk score
 */
fun isCoordinationRequired(riskScore: Number): Boolean =
    riskScore >= 6

/**
 * Generates response actions based on alert level
 */
fun generateResponseActions(alertLevel: String, emergencyType: String): Array =
    if (alertLevel == "CRITICAL") [
        "Immediate facility shutdown if necessary",
        "Activate emergency response team",
        "Notify regulatory authorities (EPA/DEQ)",
        "Issue public advisory/boil water notice",
        "Deploy emergency equipment and personnel",
        "Establish incident command center"
    ]
    else if (alertLevel == "EMERGENCY") [
        "Increase monitoring frequency",
        "Activate response protocols",
        "Notify operations management",
        "Prepare contingency resources",
        "Alert nearby facilities"
    ]
    else if (alertLevel == "WARNING") [
        "Enhanced monitoring",
        "Review operational parameters",
        "Prepare response team for standby",
        "Document conditions"
    ]
    else [
        "Continue routine monitoring",
        "Document for trend analysis"
    ]

/**
 * Calculates estimated response time based on severity and distance
 */
fun estimateResponseTime(severity: String, distanceKm: Number): Number =
    if (severity == "CRITICAL") 15 + (distanceKm * 2)
    else if (severity == "HIGH") 30 + (distanceKm * 3)
    else if (severity == "MEDIUM") 60 + (distanceKm * 4)
    else 120 + (distanceKm * 5)