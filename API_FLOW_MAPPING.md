# ChainSync Platform API - Flow Mapping

This document shows how the main API (`chainsync-platform-api.xml`) routes requests to implementation flows.

## How APIkit Router Works

The `chainsync-platform-api.xml` uses **APIkit Router** which automatically routes HTTP requests to flows based on naming convention:

- **Flow Naming Pattern**: `{method}:\{resource}:chainsync-platform-api-config`
- **Example**: A `GET /environmental-facilities` request routes to flow `get:\environmental-facilities:chainsync-platform-api-config`

## All Imported Implementation Files

The main API imports **13 implementation files** containing all your flows:

### 1. **environmental-data-impl.xml**
Contains core environmental data flows

### 2. **environmental-facilities-impl.xml**
- `get:\environmental-facilities:chainsync-platform-api-config` - List all facilities
- `get:\environmental-facilities\(facilityId):chainsync-platform-api-config` - Get single facility

### 3. **environmental-station-readings-impl.xml**
- `post:\environmental-data\(stationId)\readings:application\json:chainsync-platform-api-config` - Submit station readings

### 4. **air-pollution-monitoring.xml**
- `get:\esg\air-quality\(facilityId):chainsync-platform-api-config` - Get air quality data for ESG
- `generate-esg-report-flow` - Generate comprehensive ESG report
- `post:\esg\iot-readings:application\json:chainsync-platform-api-config` - Receive IoT sensor data

### 5. **water-quality-monitoring.xml**
- `get:\water-quality\(facilityId):chainsync-platform-api-config` - Get water quality data
- `post:\water-quality\alerts:application\json:chainsync-platform-api-config` - Submit water quality alerts

### 6. **environmental-emergency-alerts-impl.xml**
- `get:\environmental-emergency-alerts:chainsync-platform-api-config` - List emergency alerts
- `post:\environmental-emergency-alerts:application\json:chainsync-platform-api-config` - Create emergency alert

### 7. **facility-incident-impl.xml**
- `post:\environmental-facilities\(facilityId)\incidents:application\json:chainsync-platform-api-config` - Submit facility incident

### 8. **environmental-service-vehicles-impl.xml**
- `get:\environmental-service-vehicles:chainsync-platform-api-config` - List service vehicles
- `get:\environmental-service-vehicles\(vehicleId):chainsync-platform-api-config` - Get single vehicle

### 9. **vehicle-dispatch-impl.xml**
- `post:\environmental-service-vehicles\(vehicleId)\dispatch:application\json:chainsync-platform-api-config` - Dispatch vehicle commands

### 10. **fleet-monitoring-api.xml**
- `get:\fleet-monitoring:chainsync-platform-api-config` - Get fleet monitoring data

### 11. **ai-agent-integration-impl.xml**
- `get-environmental-data-flow` - Get environmental data for AI agent
- `post-alerts-flow` - Receive AI alerts
- `post-emergency-flow` - Receive AI emergency notifications

### 12. **environmental-data-system-api.xml**
- `get:\fleet-coordination\recommendations:chainsync-platform-api-config` - Get fleet coordination recommendations

### 13. **fleet-environmental-coordination.xml**
- `get:\fleet-coordination\driver-safety-alerts:chainsync-platform-api-config` - Get driver safety alerts
- `get:\fleet-coordination\route-optimization:chainsync-platform-api-config` - Get route optimization

## API Request Flow

```
HTTP Request → Main API Listener (chainsync-platform-api.xml)
    ↓
APIkit Router (reads RAML specification)
    ↓
Routes to appropriate flow based on method + path
    ↓
Implementation flow executes (from imported files)
    ↓
Response returned to client
```

## Example: GET /environmental-facilities Request

1. Request arrives at: `http://localhost:8081/api/environmental-facilities`
2. Main flow `chainsync-platform-api-main` receives it
3. APIkit router checks RAML and finds matching endpoint
4. Router calls: `get:\environmental-facilities:chainsync-platform-api-config`
5. This flow exists in: `environmental-facilities-impl.xml` (imported on line 26)
6. Flow executes and returns facility data
7. Response sent back to client

## Testing Your API

### 1. Access API Console
```
http://localhost:8081/console/
```

### 2. Test Endpoints

**Get All Facilities:**
```bash
curl http://localhost:8081/api/environmental-facilities
```

**Get Single Facility:**
```bash
curl http://localhost:8081/api/environmental-facilities/NYC_FAC_001
```

**Get Water Quality:**
```bash
curl http://localhost:8081/api/water-quality/water-treatment-1
```

**Get Air Quality (ESG):**
```bash
curl http://localhost:8081/api/esg/air-quality/waste-processing-1
```

**Get Fleet Recommendations:**
```bash
curl http://localhost:8081/api/fleet-coordination/recommendations
```

**Submit Emergency Alert:**
```bash
curl -X POST http://localhost:8081/api/environmental-emergency-alerts \
  -H "Content-Type: application/json" \
  -d '{
    "facilityId": "VEOLIA_WTP_001",
    "emergencyType": "WATER_QUALITY_EXCEEDANCE",
    "severity": "CRITICAL",
    "affectedPopulation": 125000
  }'
```

## Verifying All Flows Are Connected

To verify all implementation files are properly imported:

1. **Check main API file**: All 13 files should be listed in `<import>` statements
2. **Check flow naming**: Flow names must match RAML endpoints
3. **Check APIkit router**: Should reference `chainsync-platform-api.raml`

## Troubleshooting

### Flow Not Found Error
- **Cause**: Flow name doesn't match APIkit convention
- **Solution**: Check flow name matches `{method}:\{path}:chainsync-platform-api-config`

### Import Error
- **Cause**: Implementation file not imported in main API
- **Solution**: Add `<import file="filename.xml"/>` to chainsync-platform-api.xml

### RAML Mismatch
- **Cause**: Endpoint in RAML but no matching flow
- **Solution**: Create flow with correct naming convention in implementation file

## File Import Order (Current)

1. Global configurations (global.xml, external-api-config.xml, error-handling.xml)
2. Environmental data integration helpers
3. Core environmental data implementations
4. Monitoring & quality implementations
5. Emergency & alert implementations
6. Vehicle & fleet implementations
7. AI integration
8. Fleet coordination

All flows are now accessible through the main API! 🚀
