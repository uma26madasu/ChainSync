# Shared DataWeave Functions - Usage Guide

## Overview

The `global-functions.dwl` file contains reusable DataWeave functions that eliminate code duplication across ChainSync implementation flows. These functions are available to all Mule flows and can significantly reduce repetitive transformation logic.

## Location

**File**: `src/main/resources/global-functions.dwl`

## How to Use Shared Functions

### Import in DataWeave Scripts

To use these functions in your DataWeave transformations, import the module:

```dataweave
%dw 2.0
output application/json
import * from global-functions
---
{
    alertId: generateAlertId("ENV_ALERT", stationId),
    timestamp: formatTimestamp(now()),
    severity: determineSeverity(riskScore)
}
```

### Use in Mule XML Flows

The functions are automatically available when referenced in Transform Message components within XML flows.

## Available Functions Reference

### ID Generation Functions

#### generateAlertId(prefix, identifier)
Generates a standardized alert ID with timestamp.

**Parameters:**
- `prefix: String` - Alert prefix (e.g., "ENV_ALERT")
- `identifier: String` - Unique identifier (e.g., stationId)

**Returns:** `String` - Format: `{prefix}_{identifier}_{timestamp}`

**Example:**
```dataweave
generateAlertId("ENV_ALERT", "STATION_001")
// Returns: "ENV_ALERT_STATION_001_20251115_143025"
```

**Replaces:**
```dataweave
// OLD (duplicated across files):
"ENV_ALERT_" ++ $.stationId ++ "_" ++ now() as String {format: "yyyyMMdd_HHmmss"}

// NEW (using shared function):
generateAlertId("ENV_ALERT", $.stationId)
```

---

#### generateWorkflowId(prefix)
Generates a workflow ID with timestamp.

**Parameters:**
- `prefix: String` - Workflow prefix (e.g., "ENV_WF")

**Returns:** `String` - Format: `{prefix}_{timestamp}`

**Example:**
```dataweave
generateWorkflowId("ENV_WF")
// Returns: "ENV_WF_20251115_143025"
```

---

#### generateIncidentId(facilityId)
Generates an incident ID with formatted facility ID and timestamp.

**Parameters:**
- `facilityId: String` - Facility identifier

**Returns:** `String` - Format: `INC_{FACILITY_ID}_{timestamp}`

**Example:**
```dataweave
generateIncidentId("facility-001")
// Returns: "INC_FACILITY_001_20251115143025"
```

---

#### generateCorrelationId()
Generates a unique correlation ID for request tracking.

**Returns:** `String` - Format: `CHAIN-{timestamp}-{random}`

**Example:**
```dataweave
generateCorrelationId()
// Returns: "CHAIN-20251115143025123-4567"
```

---

### Timestamp Functions

#### formatTimestamp(timestamp)
Formats a DateTime to ISO 8601 format.

**Parameters:**
- `timestamp: DateTime` - DateTime object to format

**Returns:** `String` - ISO 8601 formatted string

**Example:**
```dataweave
formatTimestamp(now())
// Returns: "2025-11-15T14:30:25Z"
```

**Replaces:**
```dataweave
// OLD:
now() as String {format: "yyyy-MM-dd'T'HH:mm:ss'Z'"}

// NEW:
formatTimestamp(now())
```

---

### Risk Assessment Functions

#### determineAlertLevel(riskScore)
Determines alert level based on risk score.

**Parameters:**
- `riskScore: Number` - Risk score (0-10 scale)

**Returns:** `String` - One of: "CRITICAL", "EMERGENCY", "WARNING", "ADVISORY"

**Thresholds:**
- ≥ 8: CRITICAL
- ≥ 6: EMERGENCY
- ≥ 4: WARNING
- < 4: ADVISORY

**Example:**
```dataweave
determineAlertLevel(8.5)
// Returns: "CRITICAL"
```

---

#### determineSeverity(riskScore)
Determines severity level based on risk score.

**Parameters:**
- `riskScore: Number` - Risk score (0-10 scale)

**Returns:** `String` - One of: "CRITICAL", "HIGH", "MEDIUM", "LOW"

**Example:**
```dataweave
determineSeverity(7)
// Returns: "HIGH"
```

---

#### calculateEnvironmentalRiskScore(aqi, waterQuality, weatherSeverity)
Calculates comprehensive environmental risk score.

**Parameters:**
- `aqi: Number` - Air Quality Index
- `waterQuality: Object` - Water quality parameters {ph?, turbidity?, do?}
- `weatherSeverity: Number` - Weather severity score (0-10)

**Returns:** `Number` - Calculated risk score

**Example:**
```dataweave
calculateEnvironmentalRiskScore(
    150,
    {ph: 6.0, turbidity: 6.5, do: 4.0},
    7
)
// Returns: 8 (CRITICAL level)
```

---

#### isCoordinationRequired(riskScore)
Determines if multi-agency coordination is needed.

**Parameters:**
- `riskScore: Number` - Risk score

**Returns:** `Boolean` - true if riskScore ≥ 6

**Example:**
```dataweave
isCoordinationRequired(7)
// Returns: true
```

---

### Data Validation Functions

#### isWithinSafeThreshold(value, min, max)
Validates if a value is within safe operational thresholds.

**Parameters:**
- `value: Number` - Value to check
- `min: Number` - Minimum threshold
- `max: Number` - Maximum threshold

**Returns:** `Boolean`

**Example:**
```dataweave
isWithinSafeThreshold(7.2, 6.5, 8.5)  // pH check
// Returns: true
```

**Common Use Cases:**
```dataweave
// Water quality pH
isWithinSafeThreshold(phValue, 6.5, 8.5)

// Dissolved oxygen
isWithinSafeThreshold(doValue, 5.0, 15.0)

// Temperature
isWithinSafeThreshold(temp, 0, 30)
```

---

### Response Generation Functions

#### getCoordinationStakeholders(alertLevel)
Gets list of stakeholders to coordinate based on alert level.

**Parameters:**
- `alertLevel: String` - Alert level ("CRITICAL", "EMERGENCY", "WARNING", "ADVISORY")

**Returns:** `Array<Object>` - Array of stakeholder objects with {name, role}

**Example:**
```dataweave
getCoordinationStakeholders("CRITICAL")
// Returns: [
//   {name: "EPA Emergency Response", role: "Regulatory Authority"},
//   {name: "State Environmental Health", role: "Health Department"},
//   ...
// ]
```

---

#### generateResponseActions(alertLevel, emergencyType)
Generates recommended response actions based on alert level.

**Parameters:**
- `alertLevel: String` - Alert level
- `emergencyType: String` - Type of emergency (for future enhancements)

**Returns:** `Array<String>` - Array of action items

**Example:**
```dataweave
generateResponseActions("EMERGENCY", "WATER_QUALITY")
// Returns: [
//   "Increase monitoring frequency",
//   "Activate response protocols",
//   ...
// ]
```

---

#### estimateResponseTime(severity, distanceKm)
Calculates estimated response time based on severity and distance.

**Parameters:**
- `severity: String` - Severity level ("CRITICAL", "HIGH", "MEDIUM", "LOW")
- `distanceKm: Number` - Distance in kilometers

**Returns:** `Number` - Estimated response time in minutes

**Example:**
```dataweave
estimateResponseTime("CRITICAL", 10)
// Returns: 35 (15 base + 10*2 for distance)
```

---

### Estimation Functions

#### estimateAffectedPopulation(city)
Estimates affected population based on city/location.

**Parameters:**
- `city: String` - City name

**Returns:** `Number` - Estimated population affected

**Supported Cities:**
- New York/NYC: 125,000
- London: 200,000
- Beijing: 300,000
- Los Angeles/LA: 150,000
- Chicago: 100,000
- Atlanta: 75,000
- Default: 50,000

**Example:**
```dataweave
estimateAffectedPopulation("Atlanta")
// Returns: 75000
```

---

### Formatting Functions

#### formatFacilityId(facilityId)
Formats facility ID to standard uppercase alphanumeric format.

**Parameters:**
- `facilityId: String` - Raw facility ID

**Returns:** `String` - Formatted facility ID (uppercase, alphanumeric, dashes, underscores only)

**Example:**
```dataweave
formatFacilityId("facility@#001")
// Returns: "FACILITY001"
```

---

#### formatVesselId(vesselId)
Formats vessel ID to standard format.

**Parameters:**
- `vesselId: String` - Raw vessel ID

**Returns:** `String` - Formatted vessel ID

---

#### maskSensitiveData(data)
Masks sensitive data for logging.

**Parameters:**
- `data: String` - Sensitive string to mask

**Returns:** `String` - Masked string showing first 4 and last 4 characters

**Example:**
```dataweave
maskSensitiveData("1234567890123456")
// Returns: "1234********3456"
```

---

### Geospatial Functions

#### calculateDistance(lat1, lon1, lat2, lon2)
Calculates distance between two coordinates using Haversine formula.

**Parameters:**
- `lat1: Number` - Latitude of point 1
- `lon1: Number` - Longitude of point 1
- `lat2: Number` - Latitude of point 2
- `lon2: Number` - Longitude of point 2

**Returns:** `Number` - Distance in kilometers

**Example:**
```dataweave
calculateDistance(33.7490, -84.3880, 33.7590, -84.3780)
// Returns: 1.38 (km)
```

---

#### convertToDecimalDegrees(degrees, minutes, seconds, direction)
Converts DMS (Degrees, Minutes, Seconds) to decimal degrees.

**Parameters:**
- `degrees: Number`
- `minutes: Number`
- `seconds: Number`
- `direction: String` - "N", "S", "E", or "W"

**Returns:** `Number` - Decimal degrees

---

### Error Handling Functions

#### generateErrorResponse(code, message)
Generates standardized error response object.

**Parameters:**
- `code: String` - Error code
- `message: String` - Error message

**Returns:** `Object` - Error response with timestamp

**Example:**
```dataweave
generateErrorResponse("ENV_001", "Water quality threshold exceeded")
// Returns: {
//   error: {
//     code: "ENV_001",
//     message: "Water quality threshold exceeded",
//     timestamp: "2025-11-15T14:30:25Z"
//   }
// }
```

---

### Emissions & Compliance Functions

#### calculateTotalEmissions(emissions)
Calculates total emissions from components.

**Parameters:**
- `emissions: Object` - Emissions object with {co2?, nox?, sox?, pm?}

**Returns:** `Number` - Total emissions

---

#### checkEmissionsCompliance(emissions, limits)
Checks emissions compliance against limits.

**Parameters:**
- `emissions: Object` - Current emissions
- `limits: Object` - Emission limits

**Returns:** `Object` - {compliant: Boolean, violations: Array<String>}

---

#### calculateFuelEfficiency(fuelConsumption, distance)
Calculates fuel efficiency.

**Parameters:**
- `fuelConsumption: Number` - Fuel consumed
- `distance: Number` - Distance traveled

**Returns:** `Number` - Efficiency ratio

---

### Facility Assessment Functions

#### determineFacilityType(station)
Determines facility type based on environmental data.

**Parameters:**
- `station: Object` - Station data with airQuality and weather

**Returns:** `String` - Facility type

---

#### getOperationalStatus(station)
Gets operational status for environmental facility.

**Parameters:**
- `station: Object` - Station data

**Returns:** `Object` - Operational status details

---

#### getComplianceStatus(station)
Determines compliance status.

**Parameters:**
- `station: Object` - Station data

**Returns:** `Object` - Compliance details

---

## Migration Examples

### Example 1: Alert Generation

**Before (duplicated code):**
```dataweave
%dw 2.0
output application/json
---
{
    alerts: payload.data filter ($.riskAssessment.riskScore >= 5) map {
        alertId: "ENV_ALERT_" ++ $.stationId ++ "_" ++ now() as String {format: "yyyyMMdd_HHmmss"},
        alertLevel: if ($.riskAssessment.riskScore >= 8) "CRITICAL"
                    else if ($.riskAssessment.riskScore >= 6) "EMERGENCY"
                    else "WARNING",
        timestamp: now() as String {format: "yyyy-MM-dd'T'HH:mm:ss'Z'"}
    }
}
```

**After (using shared functions):**
```dataweave
%dw 2.0
output application/json
import * from global-functions
---
{
    alerts: payload.data filter ($.riskAssessment.riskScore >= 5) map {
        alertId: generateAlertId("ENV_ALERT", $.stationId),
        alertLevel: determineAlertLevel($.riskAssessment.riskScore),
        timestamp: formatTimestamp(now())
    }
}
```

### Example 2: Coordination Workflow

**Before:**
```dataweave
%dw 2.0
output application/json
---
{
    workflowId: "ENV_WF_" ++ now() as String {format: "yyyyMMdd_HHmmss"},
    stakeholders: if (payload.alertLevel == "CRITICAL") [
        {name: "EPA Emergency Response", role: "Regulatory Authority"},
        {name: "State Environmental Health", role: "Health Department"}
    ] else [
        {name: "Water Quality Director", role: "Technical Lead"}
    ],
    estimatedResponseTime: if (payload.severity == "CRITICAL") 15 + (payload.distance * 2)
                           else 30 + (payload.distance * 3)
}
```

**After:**
```dataweave
%dw 2.0
output application/json
import * from global-functions
---
{
    workflowId: generateWorkflowId("ENV_WF"),
    stakeholders: getCoordinationStakeholders(payload.alertLevel),
    estimatedResponseTime: estimateResponseTime(payload.severity, payload.distance)
}
```

### Example 3: Risk Assessment

**Before:**
```dataweave
%dw 2.0
output application/json
---
{
    riskScore: (if (payload.aqi > 200) 4 else if (payload.aqi > 150) 3 else 0) +
               (if (payload.ph < 6.5 or payload.ph > 8.5) 3 else 0) +
               (if (payload.weatherSeverity >= 8) 3 else 0),
    severity: if (riskScore >= 8) "CRITICAL"
              else if (riskScore >= 6) "HIGH"
              else "MEDIUM"
}
```

**After:**
```dataweave
%dw 2.0
output application/json
import * from global-functions
---
{
    riskScore: calculateEnvironmentalRiskScore(
        payload.aqi,
        {ph: payload.ph, turbidity: payload.turbidity, do: payload.do},
        payload.weatherSeverity
    ),
    severity: determineSeverity(riskScore)
}
```

## Best Practices

1. **Always import the module** at the top of your DataWeave scripts:
   ```dataweave
   import * from global-functions
   ```

2. **Use shared functions instead of duplicating logic** - Check `global-functions.dwl` before writing new transformation logic

3. **Add new shared functions** when you notice patterns repeating across 3+ files

4. **Document new functions** with clear parameter descriptions and examples

5. **Test functions** in isolation before using in production flows

6. **Keep functions pure** - Avoid side effects, always return values

7. **Use descriptive parameter names** for clarity

## Testing Shared Functions

Test shared functions in DataWeave playground or in MUnit tests:

```dataweave
%dw 2.0
output application/json
import * from global-functions
---
{
    test_alertId: generateAlertId("TEST", "001"),
    test_severity: determineSeverity(7),
    test_distance: calculateDistance(33.75, -84.39, 33.76, -84.38),
    test_population: estimateAffectedPopulation("Atlanta")
}
```

## Benefits

- **Reduced Code Duplication**: Single source of truth for common logic
- **Easier Maintenance**: Update logic in one place
- **Improved Consistency**: Standardized formatting and calculations
- **Better Testability**: Test functions in isolation
- **Faster Development**: Reuse proven logic
- **Enhanced Readability**: Descriptive function names replace complex inline logic

## Contributing

When adding new shared functions:

1. Add the function to `src/main/resources/global-functions.dwl`
2. Document it in this guide with:
   - Function signature
   - Parameter descriptions
   - Return type
   - Usage examples
   - Migration example (before/after)
3. Add unit tests for the function
4. Update relevant implementation files to use the new function

---

**Last Updated**: 2025-11-15
**Version**: 2.0.0
