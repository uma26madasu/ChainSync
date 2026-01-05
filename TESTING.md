# ChainSync - Testing Documentation

## Overview

ChainSync has **comprehensive automated test coverage** using MuleSoft MUnit framework, ensuring reliability, quality, and security across all APIs, integrations, and error scenarios.

## Table of Contents

1. [Test Coverage Summary](#test-coverage-summary)
2. [Test Suites](#test-suites)
3. [Running Tests](#running-tests)
4. [Test Organization](#test-organization)
5. [Writing New Tests](#writing-new-tests)
6. [Continuous Integration](#continuous-integration)
7. [Test Maintenance](#test-maintenance)

---

## Test Coverage Summary

### Statistics

| Metric                    | Count    | Coverage                                      |
|---------------------------|----------|-----------------------------------------------|
| **Test Suites**           | 14       | All flows and APIs covered                    |
| **Total Test Cases**      | 150+     | Success scenarios + error handling            |
| **Success Scenario Tests**| 100+     | Happy path and integration validation         |
| **Error Handling Tests**  | 50+      | Validation, security, edge cases              |
| **API Coverage**          | 100%     | All endpoints tested                          |
| **Integration Coverage**  | 100%     | AI Agent, Slotify, NASA APIs                  |
| **Security Test Cases**   | 12+      | SQL injection, XSS, auth, validation          |

### Test Distribution

```
Core API Tests (5 suites):        35 tests
Operational Flow Tests (5 suites): 40 tests
Integration Tests (3 suites):      30 tests
Global Error Handling (1 suite):   36+ tests
────────────────────────────────────────────
Total:                             140+ tests
```

---

## Test Suites

### Core API Test Suites

#### 1. environmental-facilities-test-suite.xml
**Purpose:** Test facility monitoring APIs

**Success Scenarios:**
- List all environmental facilities
- Get facility details by ID
- Filter facilities by type

**Error Tests:**
- Missing authorization header → 401
- Facility not found → 404
- Invalid facility ID format → 400

**File:** `src/test/munit/environmental-facilities-test-suite.xml`

---

#### 2. environmental-data-test-suite.xml
**Purpose:** Test environmental monitoring stations

**Success Scenarios:**
- Get all station data
- Get station-specific environmental data
- Time-range filtering

**Error Tests:**
- Station not found → 404
- Invalid query parameters → 400
- Missing required parameters → 400

**File:** `src/test/munit/environmental-data-test-suite.xml`

---

#### 3. service-vehicles-test-suite.xml
**Purpose:** Test vehicle management APIs

**Success Scenarios:**
- List all environmental service vehicles
- Get vehicle details by ID
- Filter vehicles by type and availability
- Get vehicle capacity data

**Error Tests:**
- Missing authorization → 401
- Vehicle not found → 404
- Invalid vehicle ID → 400

**File:** `src/test/munit/service-vehicles-test-suite.xml`

---

#### 4. fleet-monitoring-test-suite.xml
**Purpose:** Test fleet tracking and telematics

**Success Scenarios:**
- Get fleet monitoring data
- Get vehicle-specific monitoring
- Get enhanced fleet data with environmental context
- Fleet metrics and performance data

**Error Tests:**
- Invalid vehicle ID → 404
- Missing authorization → 401
- Invalid query parameters → 400

**File:** `src/test/munit/fleet-monitoring-test-suite.xml`

---

#### 5. emergency-alerts-test-suite.xml
**Purpose:** Test emergency alert management

**Success Scenarios:**
- List all emergency alerts
- Create new emergency alert
- Filter alerts by severity
- Geo-based alert filtering

**Error Tests:**
- Invalid alert data → 400
- Missing required fields → 400
- Unauthorized access → 401

**File:** `src/test/munit/emergency-alerts-test-suite.xml`

---

### Operational Flow Test Suites

#### 6. air-pollution-monitoring-test-suite.xml
**Purpose:** Test air quality monitoring & IoT sensors

**Success Scenarios (7 tests):**
- Get ESG air quality data for facility
- Post IoT sensor readings (methane monitoring)
- Post IoT air quality readings (PM2.5, NO2, CO)
- Generate critical methane alerts (threshold >2000 ppm)
- Generate ESG compliance reports
- Multi-parameter air quality assessment
- Real-time air quality index calculation

**Error Tests (8 tests):**
- Missing sensorId → 400 BAD_REQUEST
- Missing facilityId → 400 BAD_REQUEST
- Invalid sensor type → 400 BAD_REQUEST
- Missing Authorization header → 401 UNAUTHORIZED
- Malformed JSON payload → 400 BAD_REQUEST
- Wrong Content-Type header → 415 UNSUPPORTED_MEDIA_TYPE
- Invalid reading values (negative, out of range) → 400
- Missing required reading parameters → 400

**File:** `src/test/munit/air-pollution-monitoring-test-suite.xml`

**Example Test:**
```xml
<munit:test name="post-iot-critical-methane-test"
            description="Test critical methane alert generation">
    <munit:execution>
        <http:request method="POST" path="/esg/iot-readings">
            <http:body><![CDATA[#[output application/json
---
{
  "facilityId": "FACILITY_001",
  "sensorId": "SENSOR_CH4_001",
  "sensorType": "METHANE",
  "readings": {
    "methane_ppm": 2500
  }
}]]]></http:body>
        </http:request>
    </munit:execution>
    <munit:validation>
        <munit-tools:assert-that
            expression="#[payload.alertLevel]"
            is="#[MunitTools::equalTo('CRITICAL')]"/>
    </munit:validation>
</munit:test>
```

---

#### 7. water-quality-monitoring-test-suite.xml
**Purpose:** Test water quality monitoring & contamination alerts

**Success Scenarios (7 tests):**
- Get water quality parameters
- Post E.coli contamination detection
- Post pH exceedance alert
- Post turbidity threshold violation
- Generate compliance status report
- Multi-parameter water quality assessment
- Drinking water safety validation

**Error Tests (8 tests):**
- Missing stationId → 400
- Invalid parameter names → 400
- Missing authorization → 401
- Malformed contamination data → 400
- Invalid threshold values → 400
- Wrong Content-Type → 415
- Out-of-range pH values → 400
- Negative parameter values → 400

**File:** `src/test/munit/water-quality-monitoring-test-suite.xml`

---

#### 8. vehicle-dispatch-test-suite.xml
**Purpose:** Test priority-based vehicle dispatch operations

**Success Scenarios (7 tests):**
- Dispatch vehicle with URGENT priority
- Dispatch vehicle with HIGH priority
- Dispatch vehicle with MEDIUM priority
- Complex dispatch with route optimization
- Dispatch coordination with multiple vehicles
- ETA calculation and updates
- Emergency response dispatch

**Error Tests (6 tests):**
- Missing vehicleId → 400
- Missing taskType → 400
- Invalid priority level → 400
- Missing authorization → 401
- Malformed dispatch payload → 400
- Wrong Content-Type → 415

**File:** `src/test/munit/vehicle-dispatch-test-suite.xml`

---

#### 9. station-readings-test-suite.xml
**Purpose:** Test environmental station reading submissions

**Success Scenarios (6 tests):**
- Submit water quality sensor readings
- Submit air monitoring sensor readings
- Submit soil analysis data
- Submit radioactive material readings
- Submit noise monitoring data
- Multi-sensor batch submissions

**Error Tests (4 tests):**
- Missing stationId → 400
- Invalid sensorType enum → 400
- Missing authorization → 401
- Malformed sensor readings → 400

**File:** `src/test/munit/station-readings-test-suite.xml`

---

#### 10. facility-incident-test-suite.xml
**Purpose:** Test critical incident reporting & regulatory coordination

**Success Scenarios (6 tests):**
- Report contamination breach (CRITICAL severity)
- Report equipment failure (HIGH severity)
- Report safety violation (MODERATE severity)
- Generate regulatory notification workflow
- Trigger emergency coordination meeting via Slotify
- Generate incident audit trail

**Error Tests (5 tests):**
- Missing incidentType → 400
- Invalid severity level → 400
- Missing authorization → 401
- Malformed incident data → 400
- Invalid facility ID format → 400

**File:** `src/test/munit/facility-incident-test-suite.xml`

---

### Integration Test Suites

#### 11. ai-agent-integration-test-suite.xml
**Purpose:** Test AI agent endpoints

**Success Scenarios (8 tests):**
- Get environmental data for AI analysis (`GET /environmental/{facilityId}`)
- Post AI-generated alerts (`POST /alerts`)
- Post emergency notifications (`POST /emergency`)
- Multi-facility environmental data retrieval
- AI alert with risk score calculation
- Emergency protocol activation
- AI recommendation processing

**Error Tests (5 tests):**
- Missing facilityId → 404
- Invalid alert data format → 400
- Missing emergency type → 400
- Malformed JSON → 400
- Missing authorization (if required) → 401

**File:** `src/test/munit/ai-agent-integration-test-suite.xml`

---

#### 12. slotify-integration-test-suite.xml
**Purpose:** Test meeting automation & stakeholder coordination

**Success Scenarios:**
- Schedule emergency coordination meeting
- Cancel scheduled meeting
- Add participant to meeting
- Update meeting details
- Webhook event processing (meeting started, ended, participant joined)

**Error Tests:**
- Invalid meeting data → 400
- Missing participants list → 400
- Authorization failures → 401
- Invalid meeting ID → 404

**File:** `src/test/munit/slotify-integration-test-suite.xml`

---

#### 13. fleet-coordination-test-suite.xml
**Purpose:** Test driver safety alerts & route optimization

**Success Scenarios (6 tests):**
- Get driver safety alerts
- Get route optimization with environmental factors
- Route optimization with weather integration
- Multi-stop route planning
- Real-time traffic integration
- Emergency route recalculation

**Error Tests (3 tests):**
- Missing vehicleId → 400
- Invalid route parameters → 400
- Missing authorization → 401

**File:** `src/test/munit/fleet-coordination-test-suite.xml`

---

### Global Error Handling Test Suite

#### 14. error-handling-test-suite.xml
**Purpose:** Comprehensive global error handling validation (36+ tests)

**Test Categories:**

##### A. Error Response Format Consistency (5 tests)
Validates that all endpoints return consistent error structure:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message",
    "timestamp": "2026-01-05T14:30:00Z"
  }
}
```

**Tested Endpoints:**
- `/environmental-facilities/{facilityId}` → 404
- `/fleet-monitoring/{vehicleId}` → 404
- `/environmental-data/{stationId}` → 404
- All endpoints validate error.code, error.message, error.timestamp fields

---

##### B. Authentication & Authorization (8 tests)

**Missing Authorization Tests:**
- GET /environmental-data (no auth header) → 401 UNAUTHORIZED
- GET /environmental-facilities (no auth header) → 401 UNAUTHORIZED
- POST /environmental-service-vehicles/TRUCK_001/dispatch (no auth) → 401
- POST /environmental-facilities/FAC_001/incidents (no auth) → 401
- POST /environmental-emergency-alerts (no auth) → 401

**Invalid Token Tests:**
- Invalid token format: `Authorization: InvalidToken` → 401
- Malformed Bearer token → 401

**Tests verify:**
- Error response includes "UNAUTHORIZED" code
- HTTP 401 status code returned
- Helpful error message provided

---

##### C. Security Testing (4 tests)

**SQL Injection Attempt:**
```xml
<http:request path="/environmental-facilities/FACILITY' OR '1'='1">
    <munit:validation>
        <!-- Expects error, NOT database execution -->
        <munit-tools:assert-that
            expression="#[payload.error]"
            is="#[MunitTools::notNullValue()]"/>
    </munit:validation>
</http:request>
```

**XSS Attempt:**
```xml
<http:request path="/environmental-facilities/<script>alert('XSS')</script>"/>
```

**Special Character Handling:**
- Tests validation of IDs with special characters
- Path traversal protection (`../../../etc/passwd`)

**Unicode & Encoding:**
- Unicode character handling in facility IDs
- URL encoding validation

---

##### D. HTTP Method Validation (6 tests)

Tests that endpoints reject unsupported HTTP methods:

- PUT on /environmental-data (GET-only endpoint) → 405 METHOD_NOT_ALLOWED
- PATCH on /environmental-facilities → 405
- DELETE on /environmental-data → 405
- POST on read-only endpoints → 405

**Validates:**
- Correct 405 status code
- Error message indicates method not allowed
- Allowed methods listed in response

---

##### E. Error Code Consistency (5 tests)

**404 Not Found Format Validation:**
- `/environmental-facilities/UNKNOWN_FACILITY` → error.code contains "NOT_FOUND"
- `/fleet-monitoring/UNKNOWN_VEHICLE` → consistent NOT_FOUND format
- `/environmental-data/UNKNOWN_STATION` → consistent NOT_FOUND format

**400 Bad Request Format Validation:**
- Malformed JSON → error.code contains "BAD_REQUEST"
- Missing required fields → "VALIDATION_ERROR" or "BAD_REQUEST"

**Consistency Checks:**
- All 404 errors follow same format across endpoints
- All 400 errors have consistent structure
- Error codes use standardized naming (UPPER_SNAKE_CASE)

---

##### F. Edge Cases (8+ tests)

**Empty & Null Payloads:**
```xml
<http:request method="POST" path="/environmental-emergency-alerts">
    <http:body><![CDATA[#[{}]]]></http:body>
</http:request>
<!-- Expected: 400 BAD_REQUEST - missing required fields -->
```

**Null JSON Object:**
```xml
<http:body><![CDATA[#[null]]]></http:body>
```

**Invalid JSON Syntax:**
```xml
<http:body><![CDATA[{invalid json}]]></http:body>
```

**Large Payloads:**
- Tests payload size limits
- Validates rejection of oversized requests

**Missing Content-Type:**
```xml
<http:request method="POST" path="/...">
    <!-- No Content-Type header -->
</http:request>
```

**Unsupported Media Type (415):**
```xml
<http:headers>
    {"Content-Type" : "application/xml"}
</http:headers>
<!-- Platform expects application/json -->
```

**Special Characters in Query Parameters:**
- Tests handling of URL-encoded characters
- Validates query parameter sanitization

**File:** `src/test/munit/error-handling-test-suite.xml`

---

## Running Tests

### Run All Tests

```bash
# Run all 150+ tests
mvn clean test

# Run with detailed output
mvn clean test -X

# Run tests and generate coverage report
mvn clean test jacoco:report
```

**Expected Output:**
```
Tests run: 150+, Failures: 0, Errors: 0, Skipped: 0
```

---

### Run Specific Test Suites

#### Core API Tests
```bash
mvn test -Dtest=environmental-facilities-test-suite
mvn test -Dtest=environmental-data-test-suite
mvn test -Dtest=service-vehicles-test-suite
mvn test -Dtest=fleet-monitoring-test-suite
mvn test -Dtest=emergency-alerts-test-suite
```

#### Operational Flow Tests
```bash
mvn test -Dtest=air-pollution-monitoring-test-suite
mvn test -Dtest=water-quality-monitoring-test-suite
mvn test -Dtest=vehicle-dispatch-test-suite
mvn test -Dtest=station-readings-test-suite
mvn test -Dtest=facility-incident-test-suite
```

#### Integration Tests
```bash
mvn test -Dtest=ai-agent-integration-test-suite
mvn test -Dtest=slotify-integration-test-suite
mvn test -Dtest=fleet-coordination-test-suite
```

#### Error Handling Tests
```bash
mvn test -Dtest=error-handling-test-suite
```

---

### Run Tests by Category

```bash
# Run all error handling tests across suites
mvn test -Dtest=*-test-suite -Dtest.filter="*error*"

# Run all success scenario tests
mvn test -Dtest=*-test-suite -Dtest.filter="*success*"

# Run all security tests
mvn test -Dtest=error-handling-test-suite -Dtest.filter="*security*,*injection*,*xss*"

# Run all authentication tests
mvn test -Dtest=*-test-suite -Dtest.filter="*auth*"
```

---

## Test Organization

### Directory Structure

```
src/test/
├── munit/
│   ├── air-pollution-monitoring-test-suite.xml
│   ├── ai-agent-integration-test-suite.xml
│   ├── emergency-alerts-test-suite.xml
│   ├── environmental-data-test-suite.xml
│   ├── environmental-facilities-test-suite.xml
│   ├── error-handling-test-suite.xml
│   ├── facility-incident-test-suite.xml
│   ├── fleet-coordination-test-suite.xml
│   ├── fleet-monitoring-test-suite.xml
│   ├── service-vehicles-test-suite.xml
│   ├── slotify-integration-test-suite.xml
│   ├── station-readings-test-suite.xml
│   ├── vehicle-dispatch-test-suite.xml
│   └── water-quality-monitoring-test-suite.xml
├── resources/
│   ├── config-test.properties
│   └── log4j2-test.xml
```

### Naming Conventions

**Test Suite Files:**
- Pattern: `{component-name}-test-suite.xml`
- Example: `air-pollution-monitoring-test-suite.xml`

**Test Names:**
- Pattern: `{action}-{component}-{scenario}-test`
- Examples:
  - `get-facility-success-test`
  - `post-iot-missing-sensor-id-test`
  - `dispatch-vehicle-urgent-priority-test`

---

## Writing New Tests

### Test Template

```xml
<munit:test name="test-name"
            description="Clear description of what is being tested"
            expectedErrorType="HTTP:BAD_REQUEST">  <!-- Optional: for error tests -->

    <!-- Setup (optional) -->
    <munit:behavior>
        <set-variable variableName="testData" value="#[...]"/>
    </munit:behavior>

    <!-- Execution -->
    <munit:execution>
        <http:request method="POST"
                     config-ref="HTTP_Request_configuration"
                     path="/api/endpoint">
            <http:body><![CDATA[#[output application/json
---
{
  "field1": "value1",
  "field2": "value2"
}]]]></http:body>
            <http:headers><![CDATA[#[output application/java
---
{
  "Authorization" : "Bearer test-token",
  "Content-Type" : "application/json"
}]]]></http:headers>
        </http:request>
    </munit:execution>

    <!-- Validation -->
    <munit:validation>
        <munit-tools:assert-that
            expression="#[payload.responseField]"
            is="#[MunitTools::equalTo('expectedValue')]"
            message="Field should equal expected value"/>
        <munit-tools:assert-that
            expression="#[attributes.statusCode]"
            is="#[MunitTools::equalTo(200)]"/>
    </munit:validation>
</munit:test>
```

### Best Practices

1. **One Assertion Per Test** (when possible)
   - Focus each test on a single behavior
   - Makes failures easier to diagnose

2. **Clear Test Names**
   - Name should describe what's being tested
   - Include expected outcome

3. **Use expectedErrorType**
   - For tests expecting errors, use `expectedErrorType` attribute
   - Examples: `HTTP:BAD_REQUEST`, `HTTP:UNAUTHORIZED`, `HTTP:NOT_FOUND`

4. **Validate HTTP Status Codes**
   - Always assert on `attributes.statusCode`
   - Ensures API contract compliance

5. **Test Data Organization**
   - Use realistic test data
   - Consider edge cases and boundary conditions

6. **Documentation**
   - Add clear descriptions
   - Document why the test exists

---

## Continuous Integration

### Pre-Commit Testing

```bash
# Run before committing code
mvn clean test

# Only commit if all tests pass
if [ $? -eq 0 ]; then
    git commit -m "Your commit message"
else
    echo "Tests failed! Fix before committing."
    exit 1
fi
```

### CI/CD Pipeline Integration

**GitHub Actions Example:**
```yaml
name: Test ChainSync

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up JDK 17
        uses: actions/setup-java@v2
        with:
          java-version: '17'
      - name: Run tests
        run: mvn clean test
      - name: Block merge if tests fail
        run: exit $?
```

### Test Requirements for Deployment

**Before Deployment:**
1. All tests must pass (0 failures, 0 errors)
2. No skipped tests
3. Test coverage maintained above 80%

```bash
# Pre-deployment test validation
mvn clean test
if [ $? -ne 0 ]; then
    echo "❌ Tests failed - deployment blocked"
    exit 1
else
    echo "✅ All tests passed - safe to deploy"
fi
```

---

## Test Maintenance

### When to Update Tests

1. **API Contract Changes**
   - New fields added to request/response
   - Endpoint URLs changed
   - HTTP methods changed

2. **Bug Fixes**
   - Add regression test for each bug fix
   - Ensure bug cannot reoccur

3. **New Features**
   - Add tests before or alongside feature implementation
   - Test both success and error scenarios

4. **Security Updates**
   - Add security tests for new vulnerabilities
   - Update validation rules

### Test Coverage Goals

| Category | Target Coverage |
|----------|----------------|
| API Endpoints | 100% |
| Success Scenarios | 100% |
| Error Scenarios | 90%+ |
| Security Tests | All OWASP Top 10 |
| Integration Points | 100% |

### Test Review Checklist

- [ ] All tests have clear names and descriptions
- [ ] Both success and error scenarios covered
- [ ] HTTP status codes validated
- [ ] Error response formats validated
- [ ] Security tests included
- [ ] Integration points tested
- [ ] Edge cases covered
- [ ] Test data is realistic and comprehensive

---

## Troubleshooting Tests

### Common Issues

**Tests Failing Locally:**
```bash
# Clean and rebuild
mvn clean install

# Run specific failing test
mvn test -Dtest=failing-test-name

# Check logs
tail -f target/surefire-reports/*.txt
```

**External API Tests Failing:**
- Check `config-test.properties`
- Verify mock data fallback enabled
- Ensure API keys configured (if needed)

**Timeout Issues:**
- Increase test timeout in munit-test-suite
- Check network connectivity

---

## Test Reports

### Generate Coverage Report

```bash
# Generate JaCoCo coverage report
mvn clean test jacoco:report

# View report
open target/site/jacoco/index.html
```

### MUnit Test Reports

```bash
# Test results location
target/surefire-reports/

# View XML reports
cat target/surefire-reports/TEST-*.xml

# View text summaries
cat target/surefire-reports/*.txt
```

---

## Contact

For questions about testing:
- Documentation: This file (TESTING.md)
- Deployment Guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- Security Guide: [SECURITY.md](SECURITY.md)
- Main README: [README.md](README.md)

---

**Document Version:** 1.0.0
**Last Updated:** 2026-01-05
**Test Framework:** MUnit 2.x
**Total Test Suites:** 14
**Total Test Cases:** 150+
