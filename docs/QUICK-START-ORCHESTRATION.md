# Quick Start: API Orchestration with Error Handling

## 🎯 Overview

This guide shows you how to use **flow-ref** to orchestrate 15+ APIs in your ChainSync platform with comprehensive error handling.

## 📋 Pattern Summary

```
Main API Flow → Implementation Flow → Sub-Flows → External APIs
     ↓               ↓                    ↓            ↓
  Routing      Business Logic      Reusable     Circuit Breaker
  Context      Orchestration       Components   Error Handling
```

## ⚡ Quick Example

### 1. Main API Flow (Routing)

```xml
<flow name="post:\alerts:application\json:chainsync-platform-api-config">
    <!-- Initialize correlation ID -->
    <set-variable variableName="correlationId" value="#[uuid()]"/>

    <!-- Call implementation -->
    <flow-ref name="create-alert-implementation"/>
</flow>
```

### 2. Implementation Flow (Business Logic)

```xml
<flow name="create-alert-implementation">
    <!-- Validate -->
    <flow-ref name="validate-input"/>

    <!-- Get data -->
    <flow-ref name="get-environmental-data"/>

    <!-- Parallel actions -->
    <scatter-gather>
        <route><flow-ref name="notify-slotify"/></route>
        <route><flow-ref name="notify-ai"/></route>
        <route><flow-ref name="dispatch-vehicle"/></route>
    </scatter-gather>

    <!-- Build response -->
    <ee:transform>
        <ee:set-payload><!-- merge results --></ee:set-payload>
    </ee:transform>
</flow>
```

### 3. Sub-Flow (External API with Circuit Breaker)

```xml
<sub-flow name="notify-slotify">
    <!-- Set API context -->
    <set-variable variableName="apiName" value="Slotify"/>

    <!-- Check circuit -->
    <flow-ref name="get-circuit-state"/>

    <!-- Only call if circuit not OPEN -->
    <choice>
        <when expression="#[vars.circuitState != 'OPEN']">
            <try>
                <http:request config-ref="Slotify"/>
                <flow-ref name="record-circuit-success"/>

                <error-handler>
                    <on-error-continue type="HTTP:CONNECTIVITY">
                        <flow-ref name="record-circuit-failure"/>
                        <flow-ref name="external-api-error-handler"/>
                    </on-error-continue>
                </error-handler>
            </try>
        </when>
        <otherwise>
            <!-- Return fallback -->
            <set-payload value="#[{status: 'fallback'}]"/>
        </otherwise>
    </choice>
</sub-flow>
```

## 🔧 Your Current Structure

```
chainsync-platform-api.xml (Main)
├── Import: error-handling.xml
├── Import: external-api-error-handling.xml
├── Import: circuit-breaker-config.xml
├── Import: orchestration-example.xml ← NEW REFERENCE
│
├── Implementation Files (9+)
│   ├── environmental-facilities-impl.xml
│   ├── environmental-service-vehicles-impl.xml
│   ├── environmental-emergency-alerts-impl.xml
│   ├── environmental-data-impl.xml
│   ├── facility-incident-impl.xml
│   ├── vehicle-dispatch-impl.xml
│   ├── ai-agent-integration-impl.xml
│   ├── slotify-integration-impl.xml
│   └── ... more
│
└── Integration Files (6+)
    ├── environmental-data-integration.xml
    ├── air-pollution-monitoring.xml
    ├── water-quality-monitoring.xml
    └── ... more
```

## 📝 3-Step Implementation Checklist

### Step 1: Main API Flow
```xml
<flow name="get:\your-endpoint:chainsync-platform-api-config">
    <!-- ✅ Initialize correlation ID -->
    <ee:transform>
        <ee:variables>
            <ee:set-variable variableName="correlationId"><![CDATA[%dw 2.0
import * from error-handling-utils
output application/java
---
generateCorrelationId()
]]></ee:set-variable>
        </ee:variables>
    </ee:transform>

    <!-- ✅ Log request -->
    <logger level="INFO" message='#["[$(vars.correlationId)] GET /your-endpoint - Started"]'/>

    <!-- ✅ Call implementation -->
    <flow-ref name="your-endpoint-implementation"/>

    <!-- ✅ Set response headers -->
    <ee:transform>
        <ee:variables>
            <ee:set-variable variableName="outboundHeaders"><![CDATA[%dw 2.0
output application/java
---
{ "X-Correlation-ID": vars.correlationId }
]]></ee:set-variable>
        </ee:variables>
    </ee:transform>
</flow>
```

### Step 2: Implementation Flow
```xml
<flow name="your-endpoint-implementation">
    <!-- ✅ Business logic -->
    <flow-ref name="validate-input"/>
    <flow-ref name="get-data"/>
    <flow-ref name="transform-data"/>

    <!-- ✅ Error handling -->
    <error-handler>
        <on-error-propagate type="APP:VALIDATION_ERROR">
            <ee:transform>
                <ee:set-payload><![CDATA[%dw 2.0
import * from error-handling-utils
import * from error-codes
output application/json
---
buildErrorResponse(
    YOUR_ERROR_CODE,
    error.description,
    null,
    vars.correlationId,
    400
)
]]></ee:set-payload>
            </ee:transform>
        </on-error-propagate>
    </error-handler>
</flow>
```

### Step 3: External API Sub-Flow
```xml
<sub-flow name="call-external-api">
    <!-- ✅ Circuit breaker -->
    <set-variable variableName="apiName" value="ExternalAPI"/>
    <flow-ref name="get-circuit-state"/>

    <!-- ✅ Conditional call -->
    <choice>
        <when expression="#[vars.circuitState != 'OPEN']">
            <try>
                <http:request config-ref="ExternalAPI"/>
                <flow-ref name="record-circuit-success"/>

                <error-handler>
                    <on-error-continue type="HTTP:CONNECTIVITY, HTTP:TIMEOUT">
                        <flow-ref name="record-circuit-failure"/>
                        <flow-ref name="external-api-error-handler"/>
                    </on-error-continue>
                </error-handler>
            </try>
        </when>
        <otherwise>
            <set-payload value="#[vars.fallbackData]"/>
        </otherwise>
    </choice>
</sub-flow>
```

## 🎬 Complete Working Example

See `orchestration-example.xml` for a fully working reference implementation with:

- ✅ **Correlation ID** initialization
- ✅ **Scatter-gather** for parallel execution
- ✅ **Circuit breaker** integration
- ✅ **Error handling** at all layers
- ✅ **Standardized responses**
- ✅ **Logging** with context
- ✅ **Fallback** strategies

## 🔍 Key Patterns

### Pattern 1: Simple Flow-Ref
```xml
<flow-ref name="target-flow-name"/>
```

### Pattern 2: Flow-Ref with Context
```xml
<!-- Variables automatically passed to called flow -->
<set-variable variableName="correlationId" value="#[uuid()]"/>
<set-variable variableName="userId" value="#[payload.userId]"/>
<flow-ref name="process-user-data"/>
<!-- Called flow can access vars.correlationId and vars.userId -->
```

### Pattern 3: Parallel Orchestration
```xml
<scatter-gather>
    <route><flow-ref name="flow1"/></route>
    <route><flow-ref name="flow2"/></route>
    <route><flow-ref name="flow3"/></route>
</scatter-gather>
<!-- Results in payload array: [payload1, payload2, payload3] -->
```

### Pattern 4: Sequential with Error Handling
```xml
<flow name="sequential-processing">
    <try>
        <flow-ref name="step1"/>
        <flow-ref name="step2"/>
        <flow-ref name="step3"/>

        <error-handler>
            <on-error-continue type="ANY">
                <logger message="Step failed: $(error.description)"/>
                <!-- Recover or fallback -->
            </on-error-continue>
        </error-handler>
    </try>
</flow>
```

## 📊 Error Response Format

All errors return this structure:
```json
{
  "error": {
    "code": "FACILITY_NOT_FOUND",
    "message": "Facility not found",
    "details": { "facilityId": "FAC-123" },
    "correlationId": "20251126123456789-12345",
    "timestamp": "2025-11-26T12:34:56Z",
    "httpStatus": 404
  }
}
```

## 🎯 Best Practices

### ✅ DO
- Initialize correlation ID in main API flow
- Use flow-ref for all business logic
- Add circuit breakers for external APIs
- Log with correlation ID
- Handle errors at appropriate layers
- Use scatter-gather for parallel operations
- Provide fallback data when possible

### ❌ DON'T
- Put business logic in main API flow
- Call external APIs without circuit breaker
- Ignore correlation ID
- Suppress critical errors
- Make external calls when circuit is OPEN
- Forget to log important events

## 🚀 Testing Your Implementation

### Test 1: Basic Flow
```bash
curl -X GET http://localhost:8081/api/facilities \
  -H "X-Correlation-ID: test-123"
```

### Test 2: Check Correlation ID
```bash
# Response should include X-Correlation-ID header
curl -i -X GET http://localhost:8081/api/facilities
```

### Test 3: Error Handling
```bash
# Should return standardized error
curl -X GET http://localhost:8081/api/facilities/INVALID
```

### Test 4: Circuit Breaker
```bash
# Simulate multiple failures to open circuit
# Check logs for "Circuit breaker OPENING" message
```

## 📚 Additional Resources

- **Detailed Guide**: `docs/API-ORCHESTRATION-PATTERN.md`
- **Error Handling**: `docs/ERROR-HANDLING-README.md`
- **Integration Guide**: `docs/error-handling-integration-guide.md`
- **Example Code**: `src/main/mule/orchestration-example.xml`

## 💡 Quick Tips

1. **Correlation IDs**: Generate once in main flow, propagate automatically
2. **Circuit Breakers**: Check state before external API calls
3. **Error Handling**: Layer appropriately (global → implementation → integration)
4. **Logging**: Always include correlation ID in logs
5. **Parallel Execution**: Use scatter-gather for independent operations
6. **Fallbacks**: Provide degraded functionality when APIs fail

## 🎓 Example Scenarios

### Scenario 1: Create Alert (Orchestration)
```
Main API Flow
    ↓
Implementation Flow
    ├─→ Validate Input
    ├─→ Get Environmental Data
    ├─→ Calculate Risk
    ├─→ Create Alert Record
    └─→ Parallel Notifications
        ├─→ Schedule Meeting (Slotify) [Circuit Breaker]
        ├─→ Notify AI Agent [Error Continue]
        └─→ Dispatch Vehicle [Error Continue]
```

### Scenario 2: Get Complete Data (Aggregation)
```
Main API Flow
    ↓
Implementation Flow
    └─→ Scatter-Gather
        ├─→ Get Basic Info
        ├─→ Get Weather [Circuit Breaker]
        ├─→ Get Air Quality [Circuit Breaker]
        ├─→ Get Alerts
        └─→ Get Vehicles
    ↓
Merge Results
```

### Scenario 3: External API Call (Circuit Breaker)
```
Sub-Flow
    ├─→ Check Circuit State
    ├─→ If OPEN → Return Fallback
    └─→ If CLOSED/HALF_OPEN
        ├─→ Try API Call
        ├─→ Success → Record Success
        └─→ Failure → Record Failure → Use Fallback
```

## 🔧 Configuration

All settings in `config.properties`:

```properties
# Circuit Breaker
circuit.breaker.enabled=true
circuit.breaker.failure.threshold=5
circuit.breaker.timeout.seconds=60

# Retry Logic
retry.enabled=true
retry.max.attempts=3
retry.exponential.backoff=true

# Error Handling
error.response.include.correlation.id=true
fallback.enabled=true
```

## ✅ Summary

You're already using the **best practice pattern**! This guide shows you how to enhance it with:

1. **Correlation IDs** for tracing
2. **Circuit breakers** for resilience
3. **Standardized errors** for consistency
4. **Comprehensive logging** for debugging
5. **Graceful degradation** for reliability

**Your 15+ APIs** are perfectly structured for maintainability and scalability! 🎉
