# Security Guidelines for ChainSync Platform

## Overview
This document outlines security best practices and requirements for deploying and maintaining the ChainSync Environmental Services Platform.

ChainSync implements **enterprise-grade security** with multiple layers of protection including OAuth 2.0 authentication, HTTPS/TLS encryption, input validation, data sanitization, circuit breaker patterns, and comprehensive audit logging.

## Table of Contents

1. [Critical Security Requirements](#critical-security-requirements)
2. [Authentication & Authorization](#authentication--authorization)
3. [Transport Security](#transport-security)
4. [Input Validation & Sanitization](#input-validation--sanitization)
5. [Data Protection](#data-protection)
6. [Resilience & Protection](#resilience--protection)
7. [Audit & Compliance](#audit--compliance)
8. [Security Testing](#security-testing)
9. [Incident Response](#incident-response)
10. [Security Configuration Reference](#security-configuration-reference)

---

## Critical Security Requirements

### 1. API Key Management

**NEVER commit API keys to version control!**

#### For Local Development:
1. Create a `config-local.properties` file (add to `.gitignore`)
2. Add your actual API keys to this file:
   ```properties
   openweathermap.api.key=your_actual_api_key_here
   ```

#### For Production (CloudHub/Runtime Manager):
1. Use CloudHub secure properties or Runtime Manager properties
2. Set the following secure properties:
   - `secure::openweathermap.api.key` - Your OpenWeatherMap API key
   - `secure::db.username` - Database username
   - `secure::db.password` - Database password

#### Example Configuration:
```properties
# Development (config-local.properties)
openweathermap.api.key=your_dev_key_here

# Production (CloudHub Properties)
openweathermap.api.key=${secure::openweathermap.api.key}
db.username=${secure::db.username}
db.password=${secure::db.password}
```

### 2. HTTPS Enforcement

**All external API calls must use HTTPS protocol.**

- ✅ Correct: `https://api.openweathermap.org/...`
- ❌ Incorrect: `http://api.openweathermap.org/...`

All HTTP request configurations in `external-api-config.xml` enforce HTTPS.

### 3. Authentication & Authorization

#### API Security Configuration

For production environments, ensure these settings in `config.properties`:

```properties
# Enable API authentication
security.api.key.required=true

# Enable rate limiting to prevent abuse
security.rate.limiting=true

# Enable audit logging for compliance
security.audit.logging=true

# Enable data encryption
security.data.encryption=true
```

#### Development vs Production

Development/Testing:
```properties
security.api.key.required=false  # Only for local dev!
```

Production:
```properties
security.api.key.required=true   # ALWAYS required!
```

### 4. Request Timeouts

All HTTP request configurations include timeouts to prevent hanging connections:

- **Connection Timeout**: 30 seconds (configurable via `timeout.default`)
- **Read Timeout**: 30 seconds
- **Emergency Operations**: 5 seconds (via `timeout.emergency`)

Configure in `config.properties`:
```properties
timeout.default=30000      # 30 seconds
timeout.emergency=5000     # 5 seconds for critical operations
```

### 5. Input Validation

Always use proper query parameters instead of string concatenation to prevent injection attacks:

**Correct Approach:**
```xml
<http:request method="GET" url="https://api.example.com/endpoint">
    <http:query-params><![CDATA[#[{
        'param1': vars.userInput,
        'param2': vars.facilityId
    }]]]></http:query-params>
</http:request>
```

**Incorrect Approach (Vulnerable to injection):**
```xml
<!-- DO NOT USE -->
<http:request url="#['https://api.example.com/endpoint?param=' ++ vars.userInput]"/>
```

### 6. Error Handling

**Do not expose internal error details to external clients.**

Use standardized error responses from `global-functions.dwl`:

```dataweave
import * from global-functions
---
generateErrorResponse("ERROR_CODE", "User-friendly message")
```

This generates:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "User-friendly message",
    "timestamp": "2025-11-07T10:30:00Z"
  }
}
```

---

## Authentication & Authorization

ChainSync implements **OAuth 2.0 Bearer Token authentication** for secured endpoints.

### OAuth 2.0 Implementation

**Secured Endpoints** (require `Authorization: Bearer <JWT_token>`):
- `/environmental-service-vehicles/{vehicleId}` (GET)
- `/environmental-service-vehicles/{vehicleId}/dispatch` (POST)
- `/environmental-facilities/{facilityId}/incidents` (POST)
- `/environmental-emergency-alerts` (POST)
- `/environmental-emergency-coordination/regulatory-reports` (POST)
- `/environmental-data/{stationId}/readings` (POST)

**Authorization Trait (AuthTrait.raml):**
```yaml
securedBy:
  - oauth_2_0:
      scopes:
        - write:emergency
        - write:dispatch
        - write:incidents
```

### API Security Headers

**Required Headers for Secured Endpoints:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### Role-Based Access Control

| Role | Endpoints | Permissions |
|------|-----------|-------------|
| **Operator** | GET /facilities, /vehicles, /alerts | Read facility data, vehicle status |
| **Dispatcher** | POST /dispatch | Dispatch vehicles, create work orders |
| **Incident Manager** | POST /incidents, /alerts | Create incidents, emergency alerts |
| **Compliance Officer** | POST /regulatory-reports | Submit regulatory reports |
| **Admin** | All endpoints | Full platform access |

### Authentication Error Handling

**401 Unauthorized:**
- Missing Authorization header
- Invalid token format
- Expired JWT token

**403 Forbidden:**
- Valid token but insufficient permissions
- Resource access not allowed for user role

**Error Response Format:**
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Missing or invalid authorization token",
    "timestamp": "2026-01-05T14:30:00Z"
  }
}
```

---

## Transport Security

### HTTPS/TLS Enforcement

**All external API connections use HTTPS on port 443:**

| Service | URL | Protocol | Port |
|---------|-----|----------|------|
| OpenWeatherMap | api.openweathermap.org | HTTPS | 443 |
| OpenAQ | api.openaq.org | HTTPS | 443 |
| NASA FIRMS | firms.modaps.eosdis.nasa.gov | HTTPS | 443 |
| NASA POWER | power.larc.nasa.gov | HTTPS | 443 |
| NASA EONET | eonet.gsfc.nasa.gov | HTTPS | 443 |
| Slotify | api.slotify.io | HTTPS | 443 |

**Configuration (external-api-config.xml):**
```xml
<http:request-connection protocol="HTTPS" host="api.openweathermap.org" port="443">
    <tls:context>
        <tls:trust-store insecure="false"/>
    </tls:context>
</http:request-connection>
```

### TLS Version Requirements

- **Minimum TLS Version**: TLS 1.2
- **Recommended**: TLS 1.3
- **Cipher Suites**: Strong ciphers only (AES-256, SHA-256)

### Certificate Validation

- Certificate validation **enabled** for all HTTPS connections
- Certificate pinning for critical external APIs
- Automatic certificate expiration monitoring

### Secure Headers

**Request Headers:**
```xml
<http:headers>
    Authorization: Bearer ${token}
    X-API-Key: ${secure::api.key}
    User-Agent: ChainSync/1.0
</http:headers>
```

---

## Input Validation & Sanitization

### RAML Type Validation

**Enum-Based Validation** prevents invalid data:

**Incident Types:**
```yaml
incidentType:
  enum: ["CONTAMINATION_BREACH", "EQUIPMENT_FAILURE", "SAFETY_VIOLATION",
         "SECURITY_EVENT", "REGULATORY_ALERT"]
```

**Severity Levels:**
```yaml
severity:
  enum: ["LOW", "MODERATE", "HIGH", "CRITICAL"]
```

**Alert Levels:**
```yaml
alertLevel:
  enum: ["WARNING", "EMERGENCY", "CRITICAL"]
```

**Sensor Types:**
```yaml
sensorType:
  enum: ["WATER_QUALITY", "AIR_MONITORING", "SOIL_ANALYSIS",
         "RADIOACTIVE_MATERIAL", "NOISE_MONITORING"]
```

### Numeric Range Validation

**Risk Score Constraints:**
```yaml
environmentalRiskScore:
  type: number
  minimum: 1
  maximum: 10
```

### DataWeave Validation Functions

**File:** `global-functions.dwl`

**1. validateEmissionsData()**
```dataweave
fun validateEmissionsData(data: Any): Boolean =
    data.facilityId != null and
    data.sensorId != null and
    data.readings != null
```

**2. determineQualityStatus()**
```dataweave
fun determineQualityStatus(params: Object): String =
    if (params.ph < 6.5 or params.ph > 8.5) "CRITICAL"
    else if (params.turbidity > 5.0) "WARNING"
    else "SAFE"
```

**3. isWithinSafeThreshold()**
```dataweave
fun isWithinSafeThreshold(value: Number, threshold: Number): Boolean =
    value <= threshold
```

**4. formatFacilityId()** - ID Sanitization
```dataweave
fun formatFacilityId(rawId: String): String =
    rawId replace /[^a-zA-Z0-9_-]/ with ""  // Remove non-alphanumeric
```

### Security Testing Validation

**SQL Injection Protection** (error-handling-test-suite.xml):
```xml
<http:request path="/environmental-facilities/FACILITY' OR '1'='1"/>
<!-- Expected: Validation error, not database execution -->
```

**XSS Protection**:
```xml
<http:request path="/environmental-facilities/<script>alert('XSS')</script>"/>
<!-- Expected: Sanitized or rejected -->
```

**Special Character Handling**:
- Path traversal attempts blocked: `../../../etc/passwd`
- Null byte injection prevented: `facility%00.json`

---

## Data Protection

### Sensitive Data Sanitization

**File:** `error-handling-utils.dwl`

**Automatic Redaction Function:**
```dataweave
fun sanitizeErrorDetails(errorDetails: Any): Any =
    errorDetails match {
        case obj is Object -> obj mapObject ((value, key) ->
            (key): if (["password", "token", "apiKey", "secret", "authorization"]
                      contains (key as String))
                "***REDACTED***"
            else
                sanitizeErrorDetails(value)
        )
    }
```

**Redacted Fields:**
- `password` → `***REDACTED***`
- `token` → `***REDACTED***`
- `apiKey` → `***REDACTED***`
- `secret` → `***REDACTED***`
- `authorization` → `***REDACTED***`

**Recursive Sanitization** for nested objects and arrays.

### Data Masking

**File:** `global-functions.dwl`

**maskSensitiveData() Function:**
```dataweave
fun maskSensitiveData(data: String): String =
    substring(data, 0, 4) ++ "****" ++ substring(data, sizeOf(data) - 4)
```

**Example:**
- Input: `4532-1234-5678-9012`
- Output: `4532****9012`

### Database Security

**Secure Credential Injection:**
```properties
db.username=${secure::db.username}
db.password=${secure::db.password}
```

**Connection Pool Security:**
```xml
<db:config name="Database_Config">
    <db:connection>
        <db:pooling-profile
            maxPoolSize="10"
            minPoolSize="2"
            maxWaitTime="30000"/>
    </db:connection>
</db:config>
```

### Encryption Configuration

**Production Settings:**
```properties
security.data.encryption=true
security.data.encryption.algorithm=AES-256
security.data.encryption.mode=GCM
```

### Correlation ID Tracking

**Unique Request Identifiers:**
```dataweave
fun generateCorrelationId(): String = do {
    var timestamp = now() as String {format: "yyyyMMddHHmmssSSS"}
    var random = randomInt(99999)
    ---
    "CHAIN-$(timestamp)-$(random)"
}
```

**Example:** `CHAIN-20260105143215234-98765`

Used for audit trails without exposing sensitive user data.

---

## Resilience & Protection

### Circuit Breaker Pattern

**Prevents cascade failures** when external APIs fail.

**Configuration (config.properties):**
```properties
circuit.breaker.enabled=true
circuit.breaker.failure.threshold=5         # Open after 5 failures
circuit.breaker.timeout.seconds=60          # Stay open for 60s
circuit.breaker.half.open.max.calls=3       # Test with 3 calls
circuit.breaker.success.threshold=2         # Close after 2 successes
```

**Per-API Configuration:**
```properties
# Weather API
circuit.breaker.weather.failure.threshold=5
circuit.breaker.weather.timeout.seconds=60

# Slotify API (longer timeout)
circuit.breaker.slotify.failure.threshold=3
circuit.breaker.slotify.timeout.seconds=120

# AI Agent API
circuit.breaker.ai.failure.threshold=5
circuit.breaker.ai.timeout.seconds=90
```

**Circuit States:**
1. **CLOSED** (Normal operation) → All requests pass through
2. **OPEN** (Failure threshold exceeded) → All requests rejected immediately
3. **HALF_OPEN** (Testing recovery) → Limited requests allowed to test service

**Implementation (circuit-breaker-config.xml):**
```xml
<flow name="circuit-breaker-check-flow">
    <choice>
        <when expression="#[vars.circuitState == 'OPEN']">
            <logger level="WARN" message="Circuit breaker OPEN for $(vars.apiName)"/>
            <flow-ref name="fallback-response-flow"/>
        </when>
        <otherwise>
            <flow-ref name="external-api-call-flow"/>
        </otherwise>
    </choice>
</flow>
```

### Rate Limiting

**Configuration:**
```properties
security.rate.limiting=true
rate.limit.requests.per.minute=100
rate.limit.burst.size=20
```

**Protection Against:**
- Denial of Service (DoS) attacks
- API abuse
- Resource exhaustion

### Exponential Backoff Retry

**File:** `error-handling-utils.dwl`

**Retry Strategy:**
```dataweave
fun calculateBackoffDelay(
    attemptNumber: Number,
    baseDelayMs: Number = 1000,
    maxDelayMs: Number = 30000
): Number = do {
    var exponentialDelay = baseDelayMs * (2 pow (attemptNumber - 1))
    ---
    if (exponentialDelay > maxDelayMs) maxDelayMs else exponentialDelay
}
```

**Retry Schedule:**
- Attempt 1: 1 second delay
- Attempt 2: 2 seconds delay
- Attempt 3: 4 seconds delay
- Attempt 4: 8 seconds delay
- Attempt 5: 16 seconds delay
- Attempt 6+: 30 seconds (max)

**Retryable Error Types:**
- `HTTP:CONNECTIVITY`
- `HTTP:TIMEOUT`
- `HTTP:SERVICE_UNAVAILABLE` (503)
- `HTTP:GATEWAY_TIMEOUT` (504)
- `HTTP:TOO_MANY_REQUESTS` (429)

### Fallback Strategies

**Mock Data Fallback:**
```properties
fallback.enabled=true
fallback.mock.data.enabled=true
fallback.cache.enabled=true
fallback.degraded.mode.enabled=true
```

**Graceful Degradation:**
- External API failure → Return cached/mock data
- Database connection issue → Return limited functionality
- Circuit open → Skip non-critical operations

---

## Audit & Compliance

### Security Audit Logging

**Configuration:**
```properties
security.audit.logging=true
compliance.audit.trail=true
error.logging.sanitize.sensitive.data=true
error.logging.include.stacktrace=false
```

### Logged Security Events

**Authentication Events:**
- Login attempts (success/failure)
- Token validation failures
- Missing authorization headers
- Invalid token formats

**Authorization Events:**
- Access denied (403 Forbidden)
- Insufficient permissions
- Role-based access violations

**Validation Events:**
- Input validation failures
- Malformed requests (400 Bad Request)
- Content-Type mismatches
- Schema violations

**Security Threats:**
- SQL injection attempts
- XSS attempts
- Path traversal attempts
- Suspicious request patterns

### Correlation ID Tracing

**All requests tracked end-to-end:**
```
INFO  2026-01-05 14:32:15 [thread-1] [processor: /dispatch-flow; event: CHAIN-20260105143215234-98765]
      Vehicle dispatched: TRUCK_001
```

**Log Format Components:**
- Correlation ID: `CHAIN-20260105143215234-98765`
- Processor path: `/dispatch-flow`
- Timestamp: Millisecond precision
- Log level: INFO/WARN/ERROR
- Sanitized message: No sensitive data

### Error Logging Format

**Structured JSON Logging:**
```javascript
{
  "level": "ERROR",
  "correlationId": "CHAIN-20260105143215234-98765",
  "timestamp": "2026-01-05T14:32:15Z",
  "message": "API connection timeout",
  "errorType": "HTTP:TIMEOUT",
  "details": { /* sanitized */ },
  "context": { "facilityId": "FACILITY_001" }
}
```

### Compliance Standards

ChainSync supports:
- **EPA Safe Drinking Water Act**: Contamination response audit trails
- **Clean Air Act**: Emissions compliance logging
- **EPCRA / Right-to-Know Act**: Community notification records
- **ISO 14001**: Environmental management audit logs
- **ISO 45001**: Safety management event logging
- **SOC 2 Type II**: Security control evidence

### Audit Log Retention

**Retention Policy:**
```properties
audit.log.retention.days=365          # 1 year minimum
audit.log.archive.enabled=true
audit.log.encryption.enabled=true
```

**Log Rotation:**
- Production logs: 10 MB × 10 files = 110 MB total
- Archived logs: Compressed and encrypted
- Long-term storage: S3/Azure Blob with encryption

---

## Security Checklist for Deployment

Before deploying to production:

- [ ] All API keys moved to secure properties
- [ ] `security.api.key.required=true` in config.properties
- [ ] `security.data.encryption=true` in config.properties
- [ ] All HTTP calls use HTTPS protocol
- [ ] Request timeouts configured for all external API calls
- [ ] Database credentials use secure properties
- [ ] No sensitive data in logs (use `maskSensitiveData()` function)
- [ ] Rate limiting enabled
- [ ] Audit logging enabled
- [ ] CORS policies configured (if needed)
- [ ] TLS 1.2+ enforced for all connections

## Secure Configuration Template

Use this template for production deployments:

```properties
# API Configuration
openweathermap.api.key=${secure::openweathermap.api.key}

# Database Configuration
db.username=${secure::db.username}
db.password=${secure::db.password}

# Security Configuration
security.api.key.required=true
security.rate.limiting=true
security.audit.logging=true
security.data.encryption=true

# Timeouts
timeout.default=30000
timeout.emergency=5000
```

## Incident Response

If an API key or credential is compromised:

1. **Immediately** revoke the compromised key
2. Generate new keys/credentials
3. Update secure properties in CloudHub/Runtime Manager
4. Rotate all related secrets
5. Review audit logs for suspicious activity
6. Document the incident

## Security Testing

Regular security testing should include:

1. **API Key Exposure**: Scan repository for hardcoded secrets
2. **HTTPS Enforcement**: Verify all external calls use HTTPS
3. **Authentication**: Test that protected endpoints require auth
4. **Input Validation**: Test for SQL injection, XSS, etc.
5. **Timeout Handling**: Verify timeouts prevent hanging connections
6. **Error Messages**: Ensure no sensitive data in error responses

## Compliance

This platform handles environmental data subject to:

- EPA reporting requirements
- State DEQ regulations
- OSHA monitoring standards
- ISO 14001 & ISO 45001 standards

Ensure all security measures support regulatory compliance requirements.

## Contact

For security concerns or to report vulnerabilities, contact:
- Security Team: security@company.com
- Emergency Response: emergency-team@company.com

## References

- [MuleSoft Security Best Practices](https://docs.mulesoft.com/mule-runtime/latest/secure-configuration-properties)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [EPA Cybersecurity Guidelines](https://www.epa.gov/cybersecurity)
