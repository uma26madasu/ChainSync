# ChainSync AI Agents - Phase 1

**Intelligent AI agents for environmental service automation and decision support**

## Overview

ChainSync AI Agents is a Python-based microservice that provides intelligent decision support for the ChainSync environmental services platform. Phase 1 implements two foundational agents:

1. **Memory-Enabled Agent** - Stores and recalls historical incidents using vector similarity search
2. **Multi-Step Reasoning Agent** - Performs complex multi-step analysis using LangChain and GPT-4

These agents work together to provide data-driven recommendations for environmental incidents, leveraging historical patterns and real-time reasoning.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ChainSync Platform                       │
│                    (MuleSoft - Port 8081)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  ChainSync AI Agents                         │
│                   (Python - Port 8000)                       │
│  ┌────────────────────┐      ┌────────────────────┐        │
│  │  Memory Agent      │      │  Reasoning Agent   │        │
│  │  (ChromaDB)        │      │  (LangChain)       │        │
│  └────────────────────┘      └────────────────────┘        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                        Slotify                               │
│              (Scheduling Agent - Node.js)                    │
└─────────────────────────────────────────────────────────────┘
```

## Features

### Memory-Enabled Agent
- **Vector Similarity Search**: Semantic search for similar historical incidents
- **Pattern Recognition**: Analyzes success rates, resolution times, and costs
- **ChromaDB Integration**: Persistent vector database for incident storage
- **OpenAI Embeddings**: text-embedding-3-small for high-quality embeddings

### Multi-Step Reasoning Agent
- **LangChain Framework**: ReAct agent for step-by-step reasoning
- **GPT-4 Turbo**: Advanced language model for complex analysis
- **Custom Tools**:
  - Sensor data analysis
  - Population impact calculation
  - Response option evaluation
  - Regulatory risk assessment
- **Structured Output**: JSON responses with confidence scores

## Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- OpenAI API key
- ChainSync MuleSoft API running (default: http://localhost:8081)

## Quick Start

### 1. Clone and Setup

```bash
cd ChainSync/agents
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
CHAINSYNC_API_URL=http://localhost:8081/api
```

### 3. Run with Docker (Recommended)

```bash
docker-compose up -d
```

The agents API will be available at `http://localhost:8000`

### 4. Run Locally (Development)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn src.main:app --reload --port 8000
```

## API Endpoints

### Root & Health

```bash
# API Information
GET http://localhost:8000/

# Health Check
GET http://localhost:8000/health
```

### Memory Agent

#### Store Incident
```bash
POST http://localhost:8000/api/agents/memory/store
Content-Type: application/json

{
  "incident_id": "INC-2024-11-08-001",
  "incident_type": "WATER_CONTAMINATION",
  "facility_id": "Atlanta_WTP",
  "details": {
    "root_cause": "Heavy rain + construction runoff",
    "actions_taken": ["Chlorine boost", "Distribution flushing"],
    "outcome": "SUCCESS",
    "resolution_time": "6 hours",
    "cost": 15000,
    "lessons_learned": "Chlorine boost effective for rain-related contamination"
  },
  "sensor_data": {
    "ecoli": 5,
    "ph": 7.8,
    "turbidity": 1.2
  },
  "timestamp": "2024-11-08T20:30:00Z"
}
```

#### Recall Similar Incidents
```bash
POST http://localhost:8000/api/agents/memory/recall
Content-Type: application/json

{
  "current_incident": {
    "type": "WATER_CONTAMINATION",
    "sensor_data": {
      "ecoli": 5,
      "ph": 7.8,
      "turbidity": 1.2
    },
    "context": "heavy rain yesterday"
  },
  "top_k": 5
}
```

#### Memory Statistics
```bash
GET http://localhost:8000/api/agents/memory/stats
```

### Reasoning Agent

#### Analyze Incident
```bash
POST http://localhost:8000/api/agents/reasoning/analyze
Content-Type: application/json

{
  "incident_id": "INC-2024-11-08-001",
  "incident_type": "WATER_CONTAMINATION",
  "facility_id": "Atlanta_WTP",
  "sensor_data": {
    "ecoli": 5,
    "ph": 7.8,
    "turbidity": 1.2,
    "chlorine": 2.1
  },
  "context": {
    "weather": "heavy_rain_yesterday",
    "recent_events": ["upstream_construction"],
    "population_affected": 125000
  },
  "urgency": "HIGH"
}
```

### Combined Analysis

#### Analyze with Memory
Combines memory recall with multi-step reasoning:

```bash
POST http://localhost:8000/api/agents/analyze-with-memory
Content-Type: application/json

{
  "incident_id": "INC-2024-11-08-001",
  "incident_type": "WATER_CONTAMINATION",
  "facility_id": "Atlanta_WTP",
  "sensor_data": {
    "ecoli": 5,
    "ph": 7.8,
    "turbidity": 1.2,
    "chlorine": 2.1
  },
  "context": {
    "weather": "heavy_rain_yesterday",
    "recent_events": ["upstream_construction"],
    "population_affected": 125000
  },
  "urgency": "HIGH"
}
```

**Response includes:**
- Similar historical incidents
- Pattern analysis
- Multi-step reasoning breakdown
- Combined recommendation
- Slotify briefing (for meeting scheduling)

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | ✅ |
| `CHAINSYNC_API_URL` | ChainSync MuleSoft API URL | `http://localhost:8081/api` | ✅ |
| `CHROMA_PERSIST_DIR` | ChromaDB persistence directory | `./data/chroma_db` | ❌ |
| `AGENTS_PORT` | Server port | `8000` | ❌ |
| `AGENTS_HOST` | Server host | `0.0.0.0` | ❌ |
| `LOG_LEVEL` | Logging level | `INFO` | ❌ |
| `ENVIRONMENT` | Environment (dev/staging/prod) | `development` | ❌ |

### Agent-Specific Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `MEMORY_AGENT_TOP_K` | Number of similar incidents to recall | `5` |
| `MEMORY_AGENT_SIMILARITY_THRESHOLD` | Minimum similarity score (0-1) | `0.7` |
| `REASONING_AGENT_MODEL` | OpenAI model for reasoning | `gpt-4-turbo` |
| `REASONING_AGENT_TEMPERATURE` | Temperature for GPT-4 | `0.2` |
| `REASONING_AGENT_MAX_ITERATIONS` | Max reasoning iterations | `10` |

## Development

### Project Structure

```
agents/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── memory_agent.py        # Memory-Enabled Agent
│   │   └── reasoning_agent.py     # Multi-Step Reasoning Agent
│   ├── __init__.py
│   └── main.py                    # FastAPI application
├── data/
│   └── chroma_db/                 # ChromaDB persistence (auto-created)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (coming in Phase 2)
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black src/

# Sort imports
isort src/

# Lint
flake8 src/

# Type checking
mypy src/
```

## Docker Deployment

### Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f agents

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Docker Services

| Service | Port | Description |
|---------|------|-------------|
| `agents` | 8000 | ChainSync AI Agents API |
| `chromadb` | 8001 | ChromaDB vector database |

### Data Persistence

ChromaDB data is persisted in a Docker volume (`chainsync-chroma-data`). This ensures incident history is preserved across container restarts.

## Integration with ChainSync Platform

### Workflow

1. **ChainSync MuleSoft** detects an incident (water contamination, air pollution, etc.)
2. **Calls Agents API** with incident details
3. **Memory Agent** recalls similar historical incidents
4. **Reasoning Agent** performs multi-step analysis
5. **Combined Response** returned to ChainSync
6. **ChainSync** notifies **Slotify** to schedule authority meetings
7. **Slotify** uses agent briefing for meeting context

### Example Integration (from MuleSoft)

```xml
<http:request method="POST"
              url="${agents.api.url}/api/agents/analyze-with-memory"
              doc:name="AI Agent Analysis">
    <http:body><![CDATA[#[
        {
            incident_id: vars.incidentId,
            incident_type: "WATER_CONTAMINATION",
            facility_id: vars.facilityId,
            sensor_data: payload.sensorData,
            context: payload.context,
            urgency: "HIGH"
        }
    ]]]></http:body>
</http:request>
```

## Monitoring

### Health Checks

```bash
# Check agent health
curl http://localhost:8000/health

# Check ChromaDB health
curl http://localhost:8001/api/v1/heartbeat
```

### Logs

```bash
# Docker logs
docker-compose logs -f agents

# ChromaDB logs
docker-compose logs -f chromadb
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   ```
   Error: OPENAI_API_KEY environment variable not set
   ```
   **Solution**: Ensure `.env` file has valid OpenAI API key

2. **ChromaDB Connection Failed**
   ```
   Error: Could not connect to ChromaDB
   ```
   **Solution**: Ensure ChromaDB service is running: `docker-compose up chromadb -d`

3. **Port Already in Use**
   ```
   Error: Port 8000 is already allocated
   ```
   **Solution**: Change `AGENTS_PORT` in `.env` or stop conflicting service

4. **ChainSync API Not Reachable**
   ```
   Error: Cannot connect to ChainSync API
   ```
   **Solution**: Update `CHAINSYNC_API_URL` in `.env` and ensure MuleSoft is running

## Roadmap

### Phase 1 ✅ (Current)
- Memory-Enabled Agent
- Multi-Step Reasoning Agent
- FastAPI REST API
- Docker deployment

### Phase 2 (Planned)
- Compliance Autopilot Agent
- Natural Language Query Agent
- Root Cause Analysis Agent
- PostgreSQL for compliance tracking
- Enhanced testing suite

### Phase 3 (Planned)
- Continuous Learning Agent
- Model fine-tuning pipeline
- Advanced analytics dashboard
- Multi-tenant support

## Support

For issues, questions, or contributions:
- **ChainSync Platform**: See main repository README
- **Agent Issues**: Check logs and troubleshooting section
- **API Documentation**: Visit http://localhost:8000/docs (FastAPI Swagger UI)

## License

Part of the ChainSync Environmental Services Platform.

---

**ChainSync AI Agents - Phase 1**
*Intelligent decision support for environmental services* 🌍🤖
