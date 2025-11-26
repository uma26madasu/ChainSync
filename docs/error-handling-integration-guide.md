# Error Handling Integration Guide

## Overview

ChainSync now includes a comprehensive, layered error handling framework that provides:
- **Standardized error responses** with correlation IDs for distributed tracing
- **Centralized error codes** for consistent error identification
- **Circuit breaker pattern** to prevent cascading failures
- **Retry logic** with exponential backoff
- **Graceful degradation** for non-critical failures
- **Comprehensive logging** with sanitization of sensitive data

## Architecture

### Layer 1: Foundation (Generic Infrastructure)
- **error-handling-utils.dwl**: Reusable DataWeave functions
- **error-codes.dwl**: Standardized error code catalog
- **error-handling.xml**: Enhanced global error handlers
- **circuit-breaker-config.xml**: Circuit breaker implementation

### Layer 2: External API Error Handling
- **external-api-error-handling.xml**: Reusable error handling flows
- Automatic retry with exponential backoff
- Circuit breaker protection
- Fallback data strategies

### Layer 3: Application-Specific
- Custom error codes per domain
- Business logic validation
- Context-aware error responses

## Quick Start

### 1. Using Standardized Error Responses

```xml
<ee:transform doc:name="Build Error Response">
    <ee:message>
        <ee:set-payload><![CDATA[%dw 2.0
output application/json
import * from error-handling-utils
import * from error-codes
---
buildErrorResponse(
    FACILITY_NOT_FOUND,
    "The requested facility was not found",
    {
        facilityId: vars.facilityId,
        searchCriteria: vars.searchCriteria
    },
    vars.correlationId,
    404
)
]]></ee:set-payload>
    </ee:message>
</ee:transform>
```

### 2. Generating Correlation IDs

Add this at the start of your flow:

```xml
<ee:transform doc:name="Initialize Correlation ID">
    <ee:variables>
        <ee:set-variable variableName="correlationId"><![CDATA[%dw 2.0
import * from error-handling-utils
output application/java
---
generateCorrelationId()
]]></ee:set-variable>
    </ee:variables>
</ee:transform>
```

### 3. Using Circuit Breaker for External APIs

```xml
<flow name="call-external-api-with-circuit-breaker">
    <!-- Initialize variables -->
    <set-variable variableName="apiName" value="WeatherAPI"/>

    <!-- Check circuit state -->
    <flow-ref name="get-circuit-state" doc:name="Check Circuit"/>

    <choice doc:name="Circuit Open?">
        <when expression="#[vars.circuitState == 'OPEN']">
            <!-- Circuit is open, return error immediately -->
            <ee:transform>
                <ee:set-payload><![CDATA[%dw 2.0
import * from error-handling-utils
import * from error-codes
output application/json
---
buildErrorResponse(
    WEATHER_API_UNAVAILABLE,
    "Weather service is temporarily unavailable",
    {
        circuitState: "OPEN",
        message: "Service has failed repeatedly and is being protected"
    },
    vars.correlationId,
    503
)
]]></ee:set-payload>
            </ee:transform>
        </when>
        <otherwise>
            <!-- Circuit closed or half-open, attempt call -->
            <try>
                <http:request method="GET" config-ref="WeatherAPI_Config" path="/data/2.5/weather">
                    <http:query-params><![CDATA[#[{
                        lat: vars.latitude,
                        lon: vars.longitude,
                        appid: p('openweathermap.api.key')
                    }]]]></http:query-params>
                </http:request>

                <!-- Success - record it -->
                <flow-ref name="record-circuit-success" doc:name="Record Success"/>

                <error-handler>
                    <on-error-continue type="HTTP:CONNECTIVITY, HTTP:TIMEOUT">
                        <!-- Record failure -->
                        <flow-ref name="record-circuit-failure" doc:name="Record Failure"/>

                        <!-- Use external API error handler -->
                        <flow-ref name="external-api-error-handler" doc:name="Handle Error"/>
                    </on-error-continue>
                </error-handler>
            </try>
        </otherwise>
    </choice>
</flow>
```

### 4. Implementing Retry with Exponential Backoff

```xml
<until-successful maxRetries="3" millisBetweenRetries="1000" doc:name="Retry with Backoff">
    <try>
        <http:request method="POST" config-ref="ExternalAPI_Config" path="/api/v1/data"/>

        <error-handler>
            <on-error-propagate type="HTTP:CONNECTIVITY, HTTP:TIMEOUT, HTTP:TOO_MANY_REQUESTS">
                <!-- These errors are retryable -->
                <logger level="WARN" message='#["Retryable error: $(error.description)"]'/>
            </on-error-propagate>

            <on-error-continue type="ANY">
                <!-- Non-retryable errors stop retry -->
                <logger level="ERROR" message='#["Non-retryable error: $(error.description)"]'/>
            </on-error-continue>
        </error-handler>
    </try>
</until-successful>
```

### 5. Using External API Error Handler

```xml
<flow name="example-external-api-call">
    <!-- Set required variables -->
    <set-variable variableName="correlationId" value="#[uuid()]"/>
    <set-variable variableName="apiName" value="Slotify"/>
    <set-variable variableName="fallbackData" value='#[{status: "manual_coordination_required"}]'/>

    <try>
        <http:request method="POST" config-ref="Slotify_Config" path="/v1/meetings"/>

        <!-- Use the reusable external API error handler -->
        <flow-ref name="external-api-error-handler" doc:name="Handle Errors"/>
    </try>
</flow>
```

## Error Response Format

All errors return this standardized format:

```json
{
  "error": {
    "code": "FACILITY_NOT_FOUND",
    "message": "The requested environmental facility was not found",
    "details": {
      "facilityId": "FAC-12345",
      "searchCriteria": "id"
    },
    "correlationId": "20251126143022789-54321",
    "timestamp": "2025-11-26T14:30:22Z",
    "httpStatus": 404
  }
}
```

## Error Code Categories

### Platform Errors (PLATFORM_*)
- `PLATFORM_INTERNAL_ERROR` - 500
- `PLATFORM_BAD_REQUEST` - 400
- `PLATFORM_NOT_FOUND` - 404
- `PLATFORM_UNAUTHORIZED` - 401
- `PLATFORM_VALIDATION_FAILED` - 422

### Facility Errors (FACILITY_*)
- `FACILITY_NOT_FOUND` - 404
- `FACILITY_INVALID_ID` - 400
- `FACILITY_INACTIVE` - 409

### Vehicle Errors (VEHICLE_*)
- `VEHICLE_NOT_FOUND` - 404
- `VEHICLE_NOT_AVAILABLE` - 409
- `VEHICLE_DISPATCH_FAILED` - 500

### Environmental Data (ENV_DATA_*)
- `ENV_DATA_STATION_NOT_FOUND` - 404
- `ENV_DATA_INVALID_READINGS` - 400
- `ENV_DATA_OUT_OF_RANGE` - 422

### External API Errors
- `WEATHER_API_UNAVAILABLE` - 503
- `AIR_QUALITY_API_UNAVAILABLE` - 503
- `SLOTIFY_API_UNAUTHORIZED` - 401
- `SLOTIFY_API_RATE_LIMIT` - 429

See `error-codes.dwl` for complete catalog.

## Circuit Breaker States

### CLOSED (Normal Operation)
- All requests pass through
- Failures are counted
- Opens after threshold failures

### OPEN (Service Protected)
- All requests fail immediately
- No actual API calls made
- Returns 503 error
- Transitions to HALF_OPEN after timeout

### HALF_OPEN (Testing Recovery)
- Limited requests allowed
- Success closes circuit
- Failure reopens circuit

## Configuration

### Circuit Breaker Settings (`config.properties`)

```properties
# Global settings
circuit.breaker.enabled=true
circuit.breaker.failure.threshold=5
circuit.breaker.timeout.seconds=60
circuit.breaker.success.threshold=2

# Per-API overrides
circuit.breaker.weather.failure.threshold=5
circuit.breaker.slotify.timeout.seconds=120
```

### Retry Settings

```properties
retry.enabled=true
retry.max.attempts=3
retry.base.delay.ms=1000
retry.max.delay.ms=30000
retry.exponential.backoff=true
```

## Best Practices

### 1. Always Set Correlation IDs
Generate or propagate correlation IDs for all requests:

```xml
<set-variable variableName="correlationId"
              value="#[attributes.headers['X-Correlation-ID'] default uuid()]"/>
```

### 2. Use Appropriate Error Codes
Choose the most specific error code:

```dataweave
// Good - specific
buildErrorResponse(VEHICLE_NOT_AVAILABLE, ...)

// Bad - generic
buildErrorResponse(PLATFORM_INTERNAL_ERROR, ...)
```

### 3. Provide Helpful Error Details
Include context for debugging:

```dataweave
buildErrorResponse(
    ALERT_CREATION_FAILED,
    "Failed to create emergency alert",
    {
        severity: vars.severity,
        facilityId: vars.facilityId,
        reason: "Invalid severity level",
        validLevels: ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    },
    vars.correlationId,
    400
)
```

### 4. Sanitize Sensitive Data
Never include passwords, tokens, or keys in error responses:

```dataweave
import * from error-handling-utils
---
formatErrorLog(
    error,
    vars.correlationId,
    sanitizeErrorDetails(vars.requestContext)
)
```

### 5. Choose Appropriate Error Continuation

**Use `on-error-continue` when:**
- Non-critical operations
- Fallback available
- Degraded mode acceptable

**Use `on-error-propagate` when:**
- Critical operations (emergency alerts, incidents)
- No valid fallback
- Must notify client of failure

## Integration Examples

### Example 1: Internal API with Validation

```xml
<flow name="create-facility-flow">
    <set-variable variableName="correlationId" value="#[uuid()]"/>

    <!-- Validate input -->
    <choice doc:name="Validate Facility Data">
        <when expression="#[payload.name == null or payload.name == '']">
            <ee:transform>
                <ee:set-payload><![CDATA[%dw 2.0
import * from error-handling-utils
import * from error-codes
output application/json
---
buildErrorResponse(
    FACILITY_CREATION_FAILED,
    "Facility name is required",
    {
        field: "name",
        providedValue: payload.name
    },
    vars.correlationId,
    400
)
]]></ee:set-payload>
            </ee:transform>
            <set-variable variableName="httpStatus" value="400"/>
        </when>
        <otherwise>
            <!-- Process facility creation -->
            <logger level="INFO" message='#["[$(vars.correlationId)] Creating facility: $(payload.name)"]'/>
        </otherwise>
    </choice>
</flow>
```

### Example 2: External API with Full Error Handling

```xml
<flow name="fetch-air-quality-with-full-error-handling">
    <!-- Initialize -->
    <ee:transform>
        <ee:variables>
            <ee:set-variable variableName="correlationId"><![CDATA[%dw 2.0
import * from error-handling-utils
output application/java
---
generateCorrelationId()
]]></ee:set-variable>
            <ee:set-variable variableName="apiName"><![CDATA["AirQualityAPI"]]></ee:set-variable>
            <ee:set-variable variableName="fallbackData"><![CDATA[%dw 2.0
output application/json
---
{
    aqi: 0,
    status: "Data unavailable",
    message: "Using fallback data"
}
]]></ee:set-variable>
        </ee:variables>
    </ee:transform>

    <!-- Check circuit breaker -->
    <flow-ref name="get-circuit-state"/>

    <choice doc:name="Circuit State">
        <when expression="#[vars.circuitState == 'OPEN']">
            <!-- Return fallback immediately -->
            <ee:transform>
                <ee:set-payload><![CDATA[%dw 2.0
import * from error-handling-utils
output application/json
---
buildFallbackResponse(
    "AirQualityAPI",
    "Service temporarily unavailable",
    vars.fallbackData,
    vars.correlationId
)
]]></ee:set-payload>
            </ee:transform>
        </when>
        <otherwise>
            <!-- Attempt API call with retry -->
            <until-successful maxRetries="3" millisBetweenRetries="1000">
                <try>
                    <http:request method="GET"
                                config-ref="OpenAQ_Request_Config"
                                path="/v2/latest">
                        <http:query-params><![CDATA[#[{
                            coordinates: "$(vars.latitude),$(vars.longitude)",
                            radius: 5000
                        }]]]></http:query-params>
                    </http:request>

                    <!-- Success -->
                    <flow-ref name="record-circuit-success"/>

                    <error-handler>
                        <!-- Retryable errors -->
                        <on-error-propagate type="HTTP:CONNECTIVITY, HTTP:TIMEOUT">
                            <flow-ref name="record-circuit-failure"/>
                            <logger level="WARN"
                                    message='#["[$(vars.correlationId)] AirQuality API error (retrying): $(error.description)"]'/>
                        </on-error-propagate>

                        <!-- Non-retryable errors -->
                        <on-error-continue type="ANY">
                            <flow-ref name="record-circuit-failure"/>
                            <flow-ref name="external-api-error-handler"/>
                        </on-error-continue>
                    </error-handler>
                </try>
            </until-successful>
        </otherwise>
    </choice>
</flow>
```

## Monitoring and Debugging

### Log Format
All errors are logged with correlation IDs:

```
[20251126143022789-54321] WEATHER_API_UNAVAILABLE - api.openweathermap.org connection timeout
```

### Tracing Requests
Use correlation IDs to trace requests across services:

```bash
# Search logs for specific request
grep "20251126143022789-54321" application.log
```

### Circuit Breaker Monitoring
Check circuit state in Object Store:
- Key format: `circuit:{apiName}:state`
- Metrics: `circuit:{apiName}:metrics`

## Testing

### Testing Error Scenarios

```xml
<!-- Simulate timeout -->
<set-variable variableName="simulateTimeout" value="true"/>

<!-- Simulate circuit open -->
<os:store objectStore="circuit-breaker-state-store"
          key="circuit:TestAPI:state">
    <os:value><![CDATA[{
        "state": "OPEN",
        "openedAt": "2025-11-26T14:00:00Z"
    }]]></os:value>
</os:store>
```

### MUnit Test Example

```xml
<munit:test name="test-facility-not-found-error">
    <munit:execution>
        <flow-ref name="get-facility-by-id"/>
    </munit:execution>
    <munit:validation>
        <munit-tools:assert-that
            expression="#[payload.error.code]"
            is="#[MunitTools::equalTo('FACILITY_NOT_FOUND')]"/>
        <munit-tools:assert-that
            expression="#[payload.error.httpStatus]"
            is="#[MunitTools::equalTo(404)]"/>
        <munit-tools:assert-that
            expression="#[payload.error.correlationId]"
            is="#[MunitTools::notNullValue()]"/>
    </munit:validation>
</munit:test>
```

## Migration Guide

### Updating Existing Flows

1. **Add correlation ID generation:**
```xml
<!-- Add at flow start -->
<set-variable variableName="correlationId" value="#[uuid()]"/>
```

2. **Replace error transforms:**
```xml
<!-- OLD -->
<ee:set-payload><![CDATA[{
    message: "Error occurred",
    timestamp: now()
}]]></ee:set-payload>

<!-- NEW -->
<ee:set-payload><![CDATA[%dw 2.0
import * from error-handling-utils
import * from error-codes
output application/json
---
buildErrorResponse(
    APPROPRIATE_ERROR_CODE,
    "Error occurred",
    null,
    vars.correlationId,
    500
)
]]></ee:set-payload>
```

3. **Add circuit breaker for external APIs:**
```xml
<!-- Wrap external API calls -->
<flow-ref name="get-circuit-state"/>
<choice>
    <when expression="#[vars.circuitState != 'OPEN']">
        <!-- Your API call here -->
    </when>
</choice>
```

## Troubleshooting

### Common Issues

**Issue: Correlation ID is null**
- Solution: Initialize at flow start or check for existing header

**Issue: Circuit stays OPEN**
- Check timeout configuration
- Verify failure threshold
- Review circuit state in Object Store

**Issue: Retries not working**
- Ensure error type is in retry list
- Check `on-error-propagate` vs `on-error-continue`
- Verify `until-successful` configuration

**Issue: Sensitive data in logs**
- Use `sanitizeErrorDetails()` function
- Review logging configuration
- Check error detail fields

## Support

For questions or issues:
1. Check error code in `error-codes.dwl`
2. Review logs with correlation ID
3. Check circuit breaker state
4. Consult this guide
5. Contact platform team

## Version History

- **v1.0.0** - Initial implementation
  - Standardized error responses
  - Error code catalog
  - Circuit breaker pattern
  - Retry logic
  - Global error handlers
