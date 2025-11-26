# ChainSync Error Handling Framework

## Overview

The ChainSync platform now includes a comprehensive, production-ready error handling framework designed to provide:

- ✅ **Consistent error responses** across all APIs
- ✅ **Distributed tracing** with correlation IDs
- ✅ **Resilience patterns** (circuit breakers, retries, fallbacks)
- ✅ **Standardized error codes** for easy identification
- ✅ **Comprehensive logging** with sensitive data sanitization
- ✅ **Graceful degradation** for external API failures

## Architecture Layers

### 🏗️ **Layer 1: Foundation (Generic)**
Shared utilities and infrastructure used by all APIs:

| Component | Purpose | Location |
|-----------|---------|----------|
| **Error Utilities** | Reusable DataWeave functions | `src/main/resources/error-handling-utils.dwl` |
| **Error Codes** | Standardized error code catalog | `src/main/resources/error-codes.dwl` |
| **Global Error Handlers** | APIkit error handling | `src/main/mule/error-handling.xml` |

### 🔌 **Layer 2: External API Handling**
Specialized handling for external API integrations:

| Component | Purpose | Location |
|-----------|---------|----------|
| **External API Errors** | Reusable error flows | `src/main/mule/external-api-error-handling.xml` |
| **Circuit Breaker** | Failure protection | `src/main/mule/circuit-breaker-config.xml` |
| **Retry Logic** | Exponential backoff | Built into external API flows |

### 🎯 **Layer 3: Application-Specific**
Custom error handling per business domain:

- Facility management errors
- Vehicle dispatch errors
- Environmental data validation
- Alert processing errors
- Compliance reporting errors

## Quick Start

### 1. Generate Correlation ID
```dataweave
%dw 2.0
import * from error-handling-utils
output application/java
---
generateCorrelationId()
```

### 2. Build Error Response
```dataweave
%dw 2.0
import * from error-handling-utils
import * from error-codes
output application/json
---
buildErrorResponse(
    FACILITY_NOT_FOUND,
    "The requested facility was not found",
    { facilityId: vars.facilityId },
    vars.correlationId,
    404
)
```

### 3. Use Circuit Breaker
```xml
<flow-ref name="get-circuit-state"/>
<choice>
    <when expression="#[vars.circuitState != 'OPEN']">
        <!-- Make API call -->
    </when>
</choice>
```

## Key Features

### 📊 **Standardized Error Response Format**
```json
{
  "error": {
    "code": "FACILITY_NOT_FOUND",
    "message": "The requested environmental facility was not found",
    "details": {
      "facilityId": "FAC-12345"
    },
    "correlationId": "20251126143022789-54321",
    "timestamp": "2025-11-26T14:30:22Z",
    "httpStatus": 404
  }
}
```

### 🔄 **Circuit Breaker States**

```
CLOSED ──(5 failures)──> OPEN ──(60s timeout)──> HALF_OPEN ──(2 successes)──> CLOSED
   │                        │                         │
   └──(success)──┘         └──(all fail fast)      └──(1 failure)──> OPEN
```

### ♻️ **Retry with Exponential Backoff**
- Attempt 1: Immediate
- Attempt 2: Wait 1s
- Attempt 3: Wait 2s
- Attempt 4: Wait 4s
- Max delay: 30s

### 🎯 **Error Code Categories**

| Prefix | Category | HTTP Range | Example |
|--------|----------|------------|---------|
| `PLATFORM_*` | Platform errors | 400-500 | `PLATFORM_BAD_REQUEST` |
| `FACILITY_*` | Facility errors | 400-500 | `FACILITY_NOT_FOUND` |
| `VEHICLE_*` | Vehicle errors | 400-500 | `VEHICLE_NOT_AVAILABLE` |
| `ENV_DATA_*` | Environmental data | 400-422 | `ENV_DATA_OUT_OF_RANGE` |
| `ALERT_*` | Alert errors | 400-500 | `ALERT_CREATION_FAILED` |
| `WEATHER_API_*` | Weather API | 400-503 | `WEATHER_API_UNAVAILABLE` |
| `AIR_QUALITY_API_*` | Air quality | 400-503 | `AIR_QUALITY_API_TIMEOUT` |
| `SLOTIFY_*` | Slotify API | 400-503 | `SLOTIFY_API_RATE_LIMIT` |

## Configuration

### Circuit Breaker (`config.properties`)
```properties
circuit.breaker.enabled=true
circuit.breaker.failure.threshold=5
circuit.breaker.timeout.seconds=60
circuit.breaker.success.threshold=2

# Per-API settings
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

### Error Response
```properties
error.response.include.correlation.id=true
error.response.include.timestamp=true
error.response.include.error.code=true
error.response.include.details=true
```

## Available Functions

### Error Handling Utilities (`error-handling-utils.dwl`)

| Function | Purpose |
|----------|---------|
| `generateCorrelationId()` | Create unique request ID |
| `buildErrorResponse()` | Build standard error response |
| `buildErrorResponseFromException()` | Build from exception |
| `buildFallbackResponse()` | Build degraded response |
| `mapHttpStatusToErrorCode()` | Map status to code |
| `isRetryableError()` | Check if error is retryable |
| `isCriticalError()` | Check if error is critical |
| `calculateBackoffDelay()` | Calculate retry delay |
| `sanitizeErrorDetails()` | Remove sensitive data |
| `formatErrorLog()` | Format for logging |

### Error Codes (`error-codes.dwl`)

| Function | Purpose |
|----------|---------|
| `getHttpStatus(errorCode)` | Get HTTP status for code |
| `getErrorMessage(errorCode)` | Get user message for code |
| `isRetryable(errorCode)` | Check if code is retryable |
| `isCritical(errorCode)` | Check if code is critical |

## Reusable Flows

### Circuit Breaker Flows

| Flow | Purpose |
|------|---------|
| `get-circuit-state` | Get current circuit state |
| `record-circuit-failure` | Record API failure |
| `record-circuit-success` | Record API success |
| `reset-circuit-subflow` | Reset circuit to CLOSED |

### External API Error Handlers

| Handler | Handles |
|---------|---------|
| Connectivity/Timeout | `HTTP:CONNECTIVITY`, `HTTP:TIMEOUT` |
| Rate Limit | `HTTP:TOO_MANY_REQUESTS` |
| Authentication | `HTTP:UNAUTHORIZED`, `HTTP:FORBIDDEN` |
| Bad Request | `HTTP:BAD_REQUEST` |
| Not Found | `HTTP:NOT_FOUND` |
| Server Errors | `HTTP:INTERNAL_SERVER_ERROR`, `HTTP:SERVICE_UNAVAILABLE` |

## Error Handling Strategies

### 🎯 **Internal APIs**
- Validate early, fail fast
- Return detailed error messages
- No retries (application logic errors)
- Use specific error codes

### 🌐 **External APIs**
- Circuit breaker protection
- Retry with exponential backoff
- Graceful degradation with fallback
- Log all failures
- Sanitize sensitive data

### 🚨 **Critical Operations**
- Emergency alerts
- Incident reporting
- Vehicle dispatch
- Regulatory reports

**Strategy:**
- Propagate errors (don't suppress)
- Immediate alerting
- Detailed logging
- No silent failures

### 📊 **Non-Critical Operations**
- Health checks
- Data queries
- Analytics

**Strategy:**
- Continue on error
- Return cached/fallback data
- Log warnings
- Degraded mode acceptable

## Integration Checklist

When integrating error handling into a flow:

- [ ] Generate/propagate correlation ID at flow start
- [ ] Set `vars.apiName` for external API calls
- [ ] Check circuit state before external API calls
- [ ] Record circuit success/failure
- [ ] Use standardized error response format
- [ ] Choose appropriate error codes
- [ ] Log with correlation ID
- [ ] Sanitize sensitive data in logs
- [ ] Add retry for retryable errors only
- [ ] Define fallback behavior
- [ ] Test error scenarios
- [ ] Document error codes used

## Monitoring & Debugging

### Log Search
```bash
# Find all errors for a request
grep "20251126143022789-54321" application.log

# Find circuit breaker events
grep "Circuit breaker" application.log

# Find retry attempts
grep "Retrying" application.log
```

### Circuit Breaker State
Check Object Store:
- **State**: `circuit:{apiName}:state`
- **Metrics**: `circuit:{apiName}:metrics`

### Common Patterns

**Correlation ID in logs:**
```
[20251126143022789-54321] FACILITY_NOT_FOUND - Facility FAC-123 not found
```

**Circuit breaker logs:**
```
[20251126143022789-54321] Circuit breaker OPENING for WeatherAPI - Threshold exceeded
[20251126143022789-54321] Circuit breaker for WeatherAPI - Failure 5 of 5
```

## Best Practices

### ✅ DO
- Always use correlation IDs
- Use specific error codes
- Provide helpful error details
- Sanitize sensitive data
- Log at appropriate levels
- Test error scenarios
- Use circuit breakers for external APIs
- Implement graceful degradation

### ❌ DON'T
- Return generic error messages
- Include passwords/tokens in errors
- Retry non-retryable errors
- Suppress critical errors
- Use placeholders in error messages
- Log sensitive data
- Make external calls when circuit is OPEN

## Testing

### Unit Tests (MUnit)
```xml
<munit:test name="test-error-response-format">
    <!-- Verify error response structure -->
    <munit:assert-that expression="#[payload.error.code]"
                       is="#[MunitTools::notNullValue()]"/>
    <munit:assert-that expression="#[payload.error.correlationId]"
                       is="#[MunitTools::notNullValue()]"/>
</munit:test>
```

### Integration Tests
- Test circuit breaker state transitions
- Verify retry behavior
- Check fallback responses
- Validate error codes
- Test correlation ID propagation

## Documentation

- **[Integration Guide](error-handling-integration-guide.md)** - Detailed implementation guide
- **[Error Codes Reference](../src/main/resources/error-codes.dwl)** - Complete error code catalog
- **[Utilities Reference](../src/main/resources/error-handling-utils.dwl)** - Function documentation

## Performance Impact

| Feature | Overhead | Mitigation |
|---------|----------|------------|
| Correlation ID | Minimal | Generated once per request |
| Error logging | Low | Async logging |
| Circuit breaker | Low | Object Store lookup |
| Retry logic | Variable | Configurable attempts/delays |
| Error transformation | Minimal | DataWeave optimization |

## Roadmap

### ✅ Implemented
- Standardized error responses
- Error code catalog
- Circuit breaker pattern
- Retry with exponential backoff
- Global error handlers
- Correlation IDs
- Sensitive data sanitization

### 🔄 Future Enhancements
- Distributed circuit breaker (Redis/Hazelcast)
- Advanced metrics (Prometheus/Grafana)
- Error rate alerting (PagerDuty/Slack)
- API response caching
- Request throttling
- Health check endpoints
- Circuit breaker dashboard

## Support

**Questions or issues?**
1. Check the [Integration Guide](error-handling-integration-guide.md)
2. Review error code in `error-codes.dwl`
3. Search logs with correlation ID
4. Check circuit breaker state
5. Contact platform team

## Version

**Current Version:** 1.0.0
**Last Updated:** 2025-11-26
**MuleSoft Runtime:** 4.9.0+
