# ChainSync Platform - Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Deployment Options](#deployment-options)
   - [CloudHub Deployment](#cloudhub-deployment)
   - [On-Premise Deployment](#on-premise-deployment)
   - [Local Development](#local-development)
4. [Database Setup](#database-setup)
5. [External API Configuration](#external-api-configuration)
6. [Security Configuration](#security-configuration)
7. [Testing](#testing)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Software Requirements

- **MuleSoft Runtime**: Mule Enterprise Edition (EE) 4.4.0 or higher
- **Java**: JDK 17
- **Maven**: 3.8.0 or higher
- **PostgreSQL**: 12.0 or higher (for AI insights storage)
- **Git**: For version control

### MuleSoft License

- Valid MuleSoft Enterprise Edition license
- CloudHub account (for CloudHub deployment)
- Anypoint Platform access

### External Services

- OpenWeatherMap API key (free tier available)
- AI Agent service endpoint
- Database access credentials

---

## Environment Configuration

### Secure Properties

The following properties **must** be configured as secure properties (never commit actual values to version control):

#### Database Credentials
```properties
secure::db.username=<your-database-username>
secure::db.password=<your-database-password>
```

#### API Keys and Tokens
```properties
secure::openweathermap.api.key=<your-openweathermap-api-key>
```

### Environment-Specific Properties

Create environment-specific property files or override via CloudHub/Runtime Manager:

#### AI Agent URL
```properties
ai.agent.url.override=<environment-specific-ai-agent-url>
```

**Examples:**
- **Local Development**: `http://localhost:3000`
- **Development Environment**: `https://ai-agent-dev.yourcompany.com`
- **Production**: `https://ai-agent.yourcompany.com`

#### Database Configuration
```properties
db.host=<database-host>
db.port=<database-port>
db.name=<database-name>
```

---

## Deployment Options

### CloudHub Deployment

#### Step 1: Build the Application

```bash
cd /path/to/ChainSync
mvn clean package
```

This creates a deployable JAR file in `target/chainsync-platform-api-1.0.0-SNAPSHOT-mule-application.jar`

#### Step 2: Deploy via Anypoint Runtime Manager

**Option A: Using Runtime Manager UI**

1. Log in to Anypoint Platform
2. Navigate to Runtime Manager
3. Click "Deploy Application"
4. Fill in deployment details:
   - **Application Name**: `chainsync-platform-api`
   - **Runtime Version**: Mule 4.9.0
   - **Worker Size**: Medium (1 vCore) or higher
   - **Workers**: 1 (minimum), 2+ for high availability
   - **Region**: Select closest to your data sources

5. Upload the JAR file from `target/`

6. Configure Properties:
   - Click "Properties" tab
   - Add secure properties:
     ```
     secure::db.username=<value>
     secure::db.password=<value>
     secure::openweathermap.api.key=<value>
     ```
   - Add environment overrides:
     ```
     ai.agent.url.override=https://ai-agent.yourcompany.com
     db.host=your-production-db.amazonaws.com
     db.port=5432
     db.name=chainsync_prod
     ```

7. Click "Deploy Application"

**Option B: Using Anypoint CLI**

```bash
# Install Anypoint CLI
npm install -g anypoint-cli

# Login
anypoint-cli login

# Deploy
anypoint-cli runtime-mgr cloudhub-application deploy \
  --runtime 4.9.0 \
  --workers 1 \
  --workerSize MEDIUM \
  --region us-east-1 \
  chainsync-platform-api \
  target/chainsync-platform-api-1.0.0-SNAPSHOT-mule-application.jar
```

#### Step 3: Configure Secure Properties via CLI

```bash
anypoint-cli runtime-mgr cloudhub-application modify chainsync-platform-api \
  --property "secure::db.username:your_username" \
  --property "secure::db.password:your_password" \
  --property "secure::openweathermap.api.key:your_api_key" \
  --property "ai.agent.url.override:https://ai-agent.yourcompany.com"
```

#### Step 4: Verify Deployment

1. Check application status in Runtime Manager
2. View logs to ensure successful startup
3. Test health endpoint: `https://chainsync-platform-api.cloudhub.io/api/health`

---

### On-Premise Deployment

#### Step 1: Prepare Mule Runtime

1. Download and install Mule Enterprise Edition Runtime 4.9.0
2. Configure `MULE_HOME` environment variable
3. Install PostgreSQL JDBC driver (already included as shared library)

#### Step 2: Configure Secure Properties

Create a secure properties file using Mule Secure Configuration Tool:

```bash
cd $MULE_HOME
./bin/secure-properties-tool.sh encrypt \
  --algorithm AES \
  --mode CBC \
  --key myEncryptionKey \
  db.username "actual_username"
```

Create `config-prod.properties` or set environment variables:

```properties
# Database Configuration
db.host=production-db-server.local
db.port=5432
db.name=chainsync

# AI Agent Configuration
ai.agent.url.override=http://ai-agent-server.local:3000

# External APIs
secure::openweathermap.api.key=${env:OPENWEATHER_API_KEY}
```

#### Step 3: Deploy Application

**Option A: Manual Deployment**

1. Copy JAR to Mule apps directory:
   ```bash
   cp target/chainsync-platform-api-1.0.0-SNAPSHOT-mule-application.jar \
      $MULE_HOME/apps/
   ```

2. Start Mule Runtime:
   ```bash
   $MULE_HOME/bin/mule start
   ```

**Option B: Using Runtime Manager (Hybrid)**

1. Register on-premise server with Anypoint Runtime Manager
2. Deploy via Runtime Manager as you would for CloudHub
3. Manage properties through Runtime Manager console

#### Step 4: Configure Reverse Proxy (Optional but Recommended)

Use NGINX or Apache as a reverse proxy:

**NGINX Configuration Example:**

```nginx
upstream chainsync_backend {
    server localhost:8081;
}

server {
    listen 443 ssl;
    server_name api.chainsync.yourcompany.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location /api/ {
        proxy_pass http://chainsync_backend/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

### Local Development

#### Step 1: Install Prerequisites

- Anypoint Studio 7.x or higher
- Java JDK 17
- PostgreSQL (local instance or Docker)

#### Step 2: Clone Repository

```bash
git clone <repository-url>
cd ChainSync
```

#### Step 3: Configure Local Properties

Create `src/main/resources/config-local.properties` (add to `.gitignore`):

```properties
# Local Development Configuration
db.host=localhost
db.port=5432
db.name=chainsync_dev
db.username=dev_user
db.password=dev_password

# AI Agent (local)
ai.agent.url.override=http://localhost:3000

# External APIs (use your own keys)
openweathermap.api.key=YOUR_LOCAL_API_KEY
```

#### Step 4: Set Up Local Database

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database and user
CREATE DATABASE chainsync_dev;
CREATE USER dev_user WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE chainsync_dev TO dev_user;

-- Create schema
\c chainsync_dev
CREATE SCHEMA environmental;
```

#### Step 5: Run Application

**Using Anypoint Studio:**
1. Import project as Maven project
2. Right-click project → Run As → Mule Application

**Using Maven:**
```bash
mvn clean install
mvn mule:run
```

#### Step 6: Test Locally

```bash
# Health check
curl http://localhost:8081/api/health

# Get facilities (requires auth if enabled)
curl -H "Authorization: Bearer test-token" \
     http://localhost:8081/api/environmental-facilities
```

---

## Database Setup

### PostgreSQL Database Schema

The application requires a PostgreSQL database with the following schema:

```sql
-- Create database
CREATE DATABASE chainsync;

-- Create schema
CREATE SCHEMA environmental;

-- Example table for AI insights (customize based on your needs)
CREATE TABLE environmental.alerts (
    alert_id VARCHAR(50) PRIMARY KEY,
    facility_id VARCHAR(50) NOT NULL,
    emergency_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    affected_population INTEGER,
    trigger_condition TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE environmental.facility_data (
    facility_id VARCHAR(50) PRIMARY KEY,
    facility_name VARCHAR(255) NOT NULL,
    facility_type VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    operational_status VARCHAR(50),
    compliance_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_alerts_facility_id ON environmental.alerts(facility_id);
CREATE INDEX idx_alerts_created_at ON environmental.alerts(created_at);
CREATE INDEX idx_facility_type ON environmental.facility_data(facility_type);
```

### Connection Pool Configuration

For production environments, configure connection pooling in your database connector:

```xml
<db:config name="Database_Config">
    <db:connection>
        <db:pooling-profile maxPoolSize="10" minPoolSize="2" />
    </db:connection>
</db:config>
```

---

## External API Configuration

### OpenWeatherMap API

1. Sign up at https://openweathermap.org/api
2. Get your free API key
3. Configure as secure property:
   ```properties
   secure::openweathermap.api.key=your_actual_api_key
   ```

**Free Tier Limits:**
- 60 calls/minute
- 1,000,000 calls/month

### OpenAQ API

- No API key required
- Free public API
- Rate limit: Reasonable use policy

### USGS Water Services

- No API key required
- Free public API
- Rate limit: Reasonable use policy

### NASA FIRMS Wildfire Alerts

ChainSync integrates NASA's Fire Information for Resource Management System (FIRMS) for real-time wildfire detection.

1. Sign up at https://firms.modaps.eosdis.nasa.gov/api/area/
2. Request your free API key (VIIRS/MODIS satellite data)
3. Configure in `config.properties`:
   ```properties
   nasa.firms.api.key=YOUR_NASA_FIRMS_KEY_HERE
   nasa.firms.enabled=true
   nasa.firms.radius.km=50
   ```

**Free Tier:**
- Unlimited API calls
- Near real-time wildfire detection (VIIRS: 375m resolution)
- Global coverage
- Updates every 3-6 hours

### NASA POWER API

NASA's Prediction Of Worldwide Energy Resources (POWER) provides meteorological and solar data.

**No API key required** ✅

- Free public API
- Documentation: https://power.larc.nasa.gov/docs/
- Rate limit: Reasonable use policy

**Configured Parameters:**
```properties
nasa.power.parameters=T2M,RH2M,WS10M,PRECTOTCORR,ALLSKY_SFC_SW_DWN
```

- `T2M`: Temperature at 2 meters (°C)
- `RH2M`: Relative Humidity at 2 meters (%)
- `WS10M`: Wind Speed at 10 meters (m/s)
- `PRECTOTCORR`: Precipitation Corrected (mm/hour)
- `ALLSKY_SFC_SW_DWN`: Solar Irradiance (kW-hr/m²/day)

### NASA EONET Flood Events

NASA's Earth Observatory Natural Event Tracker (EONET) monitors natural hazard events.

**No API key required** ✅

- Free public API for flood event tracking
- Documentation: https://eonet.gsfc.nasa.gov/docs/v2.1
- Rate limit: Reasonable use policy

**Configuration:**
```properties
nasa.eonet.flood.bbox.size=1
```

Monitors flood events within ±1 degree latitude/longitude of facility locations.

### NASA GIBS Satellite Imagery

NASA's Global Imagery Browse Services (GIBS) provides satellite imagery URLs.

**No API key required for URL generation** ✅

- Imagery URLs generated on-demand (no downloads in Mule)
- Documentation: https://wiki.earthdata.nasa.gov/display/GIBS
- Layer: MODIS Terra Corrected Reflectance True Color
- Resolution: 250m

**Configuration:**
```properties
nasa.gibs.base.url=https://gibs.earthdata.nasa.gov/wmts/epsg4326/best
nasa.gibs.layer=MODIS_Terra_CorrectedReflectance_TrueColor
nasa.gibs.resolution=250m
```

Satellite imagery URLs are only generated for **CRITICAL** alerts (risk score ≥ 8) to provide visual context during emergency coordination meetings.

### AI Agent Integration

Configure your AI agent endpoint:

```properties
ai.agent.url.override=https://your-ai-agent-url.com
ai.agent.enabled=true
ai.agent.timeout=10000
```

---

## Security Configuration

### API Security

The application supports API key-based authentication. Configure in production:

```properties
security.api.key.required=true
security.rate.limiting=true
security.audit.logging=true
security.data.encryption=true
```

### TLS/SSL Configuration

For production deployments, configure TLS:

**CloudHub:** TLS is automatically handled by CloudHub

**On-Premise:** Configure in HTTP listener:

```xml
<http:listener-config name="HTTPS_Listener_config">
    <http:listener-connection host="0.0.0.0" port="8443" protocol="HTTPS">
        <tls:context>
            <tls:key-store
                path="keystore.jks"
                password="${secure::keystore.password}"
                keyPassword="${secure::key.password}" />
        </tls:context>
    </http:listener-connection>
</http:listener-config>
```

### Secure Properties Best Practices

1. **Never commit secure properties to version control**
2. **Use CloudHub secure properties** for cloud deployments
3. **Use Mule Secure Configuration Tool** for on-premise
4. **Rotate credentials regularly**
5. **Use environment variables** where possible

---

## Testing

### Running Unit Tests

```bash
# Run all MUnit tests
mvn clean test

# Run specific test suite
mvn test -Dtest=environmental-facilities-test-suite
```

### Manual API Testing

Use the provided test collection or create your own:

```bash
# Test health endpoint
curl http://localhost:8081/api/health

# Test facilities endpoint
curl -H "Authorization: Bearer test-token" \
     http://localhost:8081/api/environmental-facilities

# Test emergency alert creation
curl -X POST http://localhost:8081/api/environmental-emergency-alerts \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer test-token" \
     -d '{
       "facilityId": "FACILITY_001",
       "emergencyType": "WATER_QUALITY_EXCEEDANCE",
       "severity": "CRITICAL",
       "affectedPopulation": 125000,
       "triggerCondition": "E. coli detected"
     }'
```

### Integration Testing

Test with external APIs in development mode:

```properties
external.apis.enabled=true
mock.data.fallback=true
```

---

## Monitoring and Logging

### CloudHub Monitoring

1. **Application Logs**: Runtime Manager → Logs
2. **Metrics**: Runtime Manager → Dashboard
3. **Alerts**: Configure custom alerts for CPU, memory, errors

### On-Premise Monitoring

Configure log4j2.xml for appropriate log levels:

```xml
<Logger name="com.maritime.sustainability" level="INFO"/>
```

**Production Logging Best Practices:**
- Set root logger to WARN
- Enable INFO for application packages
- Enable DEBUG only for troubleshooting
- Use log aggregation (Splunk, ELK stack)

### Health Checks

Monitor the health endpoint:

```bash
curl http://your-app-url/api/health
```

Expected response:
```json
{
  "status": "UP",
  "timestamp": "2025-11-15T10:30:00Z"
}
```

### Performance Monitoring

Key metrics to monitor:
- **Response time**: Should be < 2000ms (configured threshold)
- **Error rate**: Should be minimal
- **External API response times**: Monitor for timeouts
- **Database connection pool**: Monitor for exhaustion

---

## Troubleshooting

### Common Issues

#### Application Won't Start

**Symptom:** Application fails to deploy or start

**Possible Causes:**
1. Missing secure properties
2. Database connection failure
3. Invalid configuration

**Solutions:**
```bash
# Check logs
tail -f $MULE_HOME/logs/mule.log

# Verify database connectivity
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1"

# Validate configuration
grep -v "^#" config.properties | grep -v "^$"
```

#### External API Timeouts

**Symptom:** Slow response times or errors when calling environmental data endpoints

**Solution:** The application has fallback mechanisms. Verify:
```properties
external.apis.enabled=true
mock.data.fallback=true
timeout.default=30000
```

#### Database Connection Pool Exhaustion

**Symptom:** "No connections available" errors

**Solution:** Increase pool size:
```xml
<db:pooling-profile maxPoolSize="20" minPoolSize="5" />
```

#### Memory Issues

**Symptom:** OutOfMemoryError in logs

**Solution (CloudHub):** Increase worker size to Large (2 vCores)

**Solution (On-Premise):** Increase JVM heap:
```bash
export MULE_OPTS="-Xmx2048m -Xms1024m"
```

### Debug Mode

Enable debug logging temporarily:

```properties
debug.logging=true
```

Or via log4j2.xml:
```xml
<Logger name="com.maritime.sustainability" level="DEBUG"/>
```

### Support Contacts

For deployment issues:
- **MuleSoft Support**: support.mulesoft.com
- **Application Support**: See README.md

---

## Deployment Checklist

### Pre-Deployment

- [ ] Build successful: `mvn clean package`
- [ ] All tests passing: `mvn test`
- [ ] Secure properties configured
- [ ] Database created and accessible
- [ ] External API keys obtained (OpenWeatherMap, NASA FIRMS)
- [ ] AI Agent endpoint configured and reachable

### CloudHub Deployment

- [ ] Application deployed to Runtime Manager
- [ ] Secure properties set
- [ ] Worker size appropriate (Medium or higher)
- [ ] High availability configured (multiple workers)
- [ ] Static IPs configured (if needed)
- [ ] Domain name configured

### On-Premise Deployment

- [ ] Mule Runtime installed and configured
- [ ] Application deployed to apps directory
- [ ] Reverse proxy configured
- [ ] TLS certificates installed
- [ ] Monitoring configured
- [ ] Backup procedures in place

### Post-Deployment

- [ ] Health check endpoint responding
- [ ] API endpoints accessible
- [ ] External API integration working
- [ ] Database connectivity verified
- [ ] Logs being generated correctly
- [ ] Monitoring dashboards configured
- [ ] Documentation updated

---

## Rollback Procedure

### CloudHub

1. In Runtime Manager, select the application
2. Click "Settings" → "Runtime Version"
3. Select previous deployment from history
4. Click "Redeploy"

### On-Premise

1. Stop the application:
   ```bash
   $MULE_HOME/bin/mule stop
   ```

2. Remove current deployment:
   ```bash
   rm $MULE_HOME/apps/chainsync-platform-api-1.0.0-SNAPSHOT-mule-application.jar
   ```

3. Deploy previous version:
   ```bash
   cp backup/chainsync-platform-api-previous-version.jar \
      $MULE_HOME/apps/
   ```

4. Start the application:
   ```bash
   $MULE_HOME/bin/mule start
   ```

---

## Additional Resources

- [MuleSoft Documentation](https://docs.mulesoft.com/)
- [CloudHub Documentation](https://docs.mulesoft.com/runtime-manager/cloudhub)
- [MUnit Testing Framework](https://docs.mulesoft.com/munit/)
- [ChainSync README](README.md)
- [ChainSync Security Guide](SECURITY.md)

---

**Document Version:** 1.0.0
**Last Updated:** 2025-11-15
**Maintained By:** ChainSync Development Team
