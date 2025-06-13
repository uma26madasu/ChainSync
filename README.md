# ChainSync Universal Coordination Platform API

A comprehensive **environmental monitoring and fleet management platform** built with MuleSoft, providing real-time data integration, intelligent risk assessment, and emergency coordination workflows.

## 🌍 Overview

ChainSync is an enterprise-grade platform that combines environmental monitoring with fleet management to provide:
- **Real-time environmental data** from 6 global monitoring stations
- **Fleet tracking and coordination** with driver safety analytics
- **Intelligent risk assessment** and emergency response workflows
- **Automated alert systems** with coordination scheduling
- **Professional API documentation** with interactive testing

## ✨ Key Features

### 🌡️ Environmental Monitoring
- **Multi-city coverage**: New York, London, Tokyo, Beijing, Mumbai, Sydney
- **Air quality monitoring**: AQI, PM2.5, PM10, NO2, O3, SO2, CO levels
- **Weather integration**: Temperature, humidity, wind, visibility, pressure
- **Risk assessment**: Automated scoring and emergency level classification
- **Real-time alerts**: Automated threshold-based notifications

### 🚛 Fleet Management
- **Real-time vehicle tracking** with GPS coordinates
- **Driver performance analytics** with safety scoring
- **Vehicle health monitoring** including fuel, maintenance, engine status
- **Telematics integration** with speed, braking, and acceleration tracking
- **Hours of service compliance** monitoring

### 🚨 Emergency Coordination
- **Automated alert generation** based on environmental and fleet conditions
- **Risk-based prioritization** with immediate, high, medium, low classifications
- **Coordination workflow triggers** for emergency response
- **Slotify scheduling integration** for resource coordination
- **Multi-stakeholder notifications** with action item tracking

### 🔧 Developer Experience
- **Interactive API Console** with try-it functionality
- **RAML-first design** with comprehensive documentation
- **Request/response validation** based on API specification
- **Professional error handling** with standardized HTTP responses
- **Health monitoring** with dependency status tracking

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   External APIs │    │   MuleSoft API   │    │   Coordination  │
│                 │    │                  │    │                 │
│ • OpenWeatherMap│◄──►│ • Data Transform │◄──►│ • Slotify       │
│ • OpenAQ        │    │ • Risk Assessment│    │ • Emergency     │
│ • Fleet Systems │    │ • Alert Engine   │    │ • Scheduling    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Anypoint Studio 7.x** with Mule Runtime 4.4.0
- **Java 8** or higher
- **Maven 3.6+**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/chainsync-platform-api.git
   cd chainsync-platform-api
   ```

2. **Import into Anypoint Studio**
   - File → Import → Anypoint Studio → Anypoint Studio project from File System
   - Select the project folder

3. **Configure API Keys** (Optional - for real-time data)
   ```properties
   # src/main/resources/config.properties
   openweathermap.api.key=YOUR_API_KEY_HERE
   airvisual.api.key=YOUR_API_KEY_HERE
   ```
   🔑 How to Get API Keys:
 🌤️ OpenWeatherMap (Weather Data)

 Visit: https://openweathermap.org/api
 Sign up for free account
 Verify email
 Get API key from dashboard
 Wait 10 minutes for activation

🌬️ AirVisual (Air Quality Data)

Visit: https://www.iqair.com/air-pollution-data-api
Get free API key
Fill registration form
Verify email
Access key in dashboard

💡 Important Notes:
✅ Free tiers available for both services
✅ App works without keys (uses mock data)
✅ Rate limits: OpenWeatherMap (1K/day), AirVisual (10K/month)

4. **Run the Application**
   - Right-click project → Run As → Mule Application
   - Wait for deployment completion

5. **Access the API**
   - **API Console**: http://localhost:8081/console
   - **Base API**: http://localhost:8081/api
   - **Health Check**: http://localhost:8081/api/health

## 📡 API Endpoints

### Environmental Monitoring
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/environmental-data` | Get all monitoring stations data |
| `GET` | `/environmental-data/{stationId}` | Get specific station data |
| `GET` | `/emergency-alerts` | Get active environmental alerts |
| `POST` | `/emergency-alerts` | Create manual environmental alert |

### Fleet Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/fleet-monitoring` | Get all vehicle data |
| `GET` | `/fleet-monitoring/{vehicleId}` | Get specific vehicle data |
| `GET` | `/fleet-monitoring/enhanced` | Get vehicles with environmental context |
| `GET` | `/driver-performance` | Get driver analytics |

### Fleet Coordination
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/fleet-coordination/recommendations` | Get coordination recommendations |
| `GET` | `/fleet-coordination/driver-safety-alerts` | Get driver safety alerts |
| `GET` | `/fleet-coordination/route-optimization` | Get route optimization suggestions |

### Alerts & Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/fleet-alerts` | Get active fleet alerts |
| `POST` | `/fleet-alerts` | Create fleet alert |
| `GET` | `/health` | Get platform health status |

## 💻 Usage Examples

### Get Environmental Data
```bash
curl -X GET "http://localhost:8081/api/environmental-data" \
     -H "Accept: application/json"
```

### Get Fleet Recommendations
```bash
curl -X GET "http://localhost:8081/api/fleet-coordination/recommendations" \
     -H "Accept: application/json"
```

### Create Emergency Alert
```bash
curl -X POST "http://localhost:8081/api/fleet-alerts" \
     -H "Content-Type: application/json" \
     -d '{
       "vehicleId": "TRUCK_001",
       "alertType": "EMERGENCY",
       "alertLevel": "CRITICAL",
       "triggerCondition": "Vehicle breakdown"
     }'
```

## 📊 Sample Response

```json
{
  "data": [
    {
      "stationId": "NYC_CENTRAL_001",
      "city": "New York",
      "coordinates": {
        "latitude": 40.7128,
        "longitude": -74.0060
      },
      "airQuality": {
        "aqi": 85,
        "level": "Moderate",
        "pollutants": {
          "pm25": 25.4,
          "pm10": 32.1
        }
      },
      "weather": {
        "temperature": 22.5,
        "condition": "Partly Cloudy",
        "visibility": 15
      },
      "riskAssessment": {
        "riskScore": 4,
        "emergencyLevel": "LOW",
        "coordinationRequired": false
      }
    }
  ]
}
```

## 🛠️ Technical Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Runtime** | MuleSoft Mule | 4.4.0 |
| **Design** | RAML | 1.0 |
| **Transformation** | DataWeave | 2.0 |
| **API Framework** | APIkit | Latest |
| **Build Tool** | Maven | 3.6+ |
| **Java** | OpenJDK | 8+ |

## ⚙️ Configuration

### Environment Variables
```bash
# HTTP Configuration
HTTP_HOST=0.0.0.0
HTTP_PORT=8081

# External API Keys (Optional)
OPENWEATHERMAP_API_KEY=your_key_here
AIRVISUAL_API_KEY=your_key_here
```

### Monitoring Stations
- **NYC_CENTRAL_001**: New York, US (40.7128, -74.0060)
- **LON_CENTRAL_001**: London, UK (51.5074, -0.1278)
- **TOK_CENTRAL_001**: Tokyo, JP (35.6762, 139.6503)
- **BEI_CENTRAL_001**: Beijing, CN (39.9042, 116.4074)
- **MUM_CENTRAL_001**: Mumbai, IN (19.0760, 72.8777)
- **SYD_CENTRAL_001**: Sydney, AU (-33.8688, 151.2093)

## 🧪 Testing

### Interactive Testing
1. Open **API Console**: http://localhost:8081/console
2. Browse available endpoints
3. Click **"Try it"** on any endpoint
4. Enter parameters and execute requests
5. View real-time responses

### Health Check
```bash
curl http://localhost:8081/api/health
```

Expected response: `200 OK` with service status details.

## 📈 Monitoring & Observability

### Health Endpoints
- **Application Health**: `/api/health`
- **Individual Services**: Included in health response
- **Dependencies**: External API status monitoring

### Metrics Tracked
- Response times for all endpoints
- External API availability
- Alert generation rates
- Risk score distributions
- Fleet coordination events

## 🚀 Deployment

### Local Development
```bash
mvn clean install
# Import into Anypoint Studio and run
```

### CloudHub Deployment
```bash
# Configure deployment properties
mvn clean deploy -DmuleDeploy \
  -Dcloudhub.application.name=chainsync-platform-api \
  -Dcloudhub.environment=Production \
  -Dcloudhub.region=us-east-1
```

## 🔐 Security Considerations

- **API Keys**: Store in secure configuration management
- **HTTPS**: Enable in production deployments  
- **Rate Limiting**: Configure appropriate limits
- **Authentication**: Implement as needed for production
- **Input Validation**: Automatic via RAML specification

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-capability`)
3. Commit changes (`git commit -am 'Add new capability'`)
4. Push to branch (`git push origin feature/new-capability`)
5. Create Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Developer**: Uma Madasu
- **Architecture**: MuleSoft Integration Platform
- **Project Type**: Environmental Monitoring & Fleet Coordination

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/chainsync-platform-api/issues)
- **Documentation**: API Console at `/console`
- **Email**: support@chainsync.com

## 🎯 Roadmap

- [ ] **Phase 1**: ✅ Core environmental monitoring
- [ ] **Phase 2**: ✅ Fleet management integration  
- [ ] **Phase 3**: ✅ Emergency coordination workflows
- [ ] **Phase 4**: 🔄 Advanced analytics and ML integration
- [ ] **Phase 5**: 📋 Mobile application support
- [ ] **Phase 6**: 📋 Enterprise security implementation

---

**Built with ❤️ using MuleSoft Anypoint Platform**

*Demonstrating enterprise-grade API development with environmental monitoring, fleet coordination, and emergency response capabilities.*