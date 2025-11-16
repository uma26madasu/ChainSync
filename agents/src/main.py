"""
ChainSync AI Agents - Main FastAPI Application
Exposes REST APIs for Memory and Reasoning agents
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional, List
import os
from datetime import datetime
import logging

from agents.memory_agent import MemoryEnabledAgent
from agents.reasoning_agent import MultiStepReasoningAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ChainSync AI Agents API",
    description="Phase 1: Memory-Enabled and Multi-Step Reasoning Agents",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
CHAINSYNC_API_URL = os.getenv("CHAINSYNC_API_URL", "http://localhost:8081/api")

# Initialize agents (lazy loading)
memory_agent_instance = None
reasoning_agent_instance = None


def get_memory_agent() -> MemoryEnabledAgent:
    """Dependency to get Memory Agent instance"""
    global memory_agent_instance
    if memory_agent_instance is None:
        if not OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY environment variable not set"
            )
        memory_agent_instance = MemoryEnabledAgent(
            persist_directory=CHROMA_PERSIST_DIR,
            openai_api_key=OPENAI_API_KEY
        )
    return memory_agent_instance


def get_reasoning_agent() -> MultiStepReasoningAgent:
    """Dependency to get Reasoning Agent instance"""
    global reasoning_agent_instance
    if reasoning_agent_instance is None:
        if not OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY environment variable not set"
            )
        reasoning_agent_instance = MultiStepReasoningAgent(
            llm_api_key=OPENAI_API_KEY,
            chainsync_api_url=CHAINSYNC_API_URL
        )
    return reasoning_agent_instance


# Pydantic models for request/response validation
class IncidentStoreRequest(BaseModel):
    incident_id: str
    incident_type: str
    facility_id: str
    details: Dict
    sensor_data: Optional[Dict] = None
    timestamp: str

    class Config:
        json_schema_extra = {
            "example": {
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
                "sensor_data": {"ecoli": 5, "ph": 7.8, "turbidity": 1.2},
                "timestamp": "2024-11-08T20:30:00Z"
            }
        }


class IncidentRecallRequest(BaseModel):
    current_incident: Dict
    top_k: int = 5

    class Config:
        json_schema_extra = {
            "example": {
                "current_incident": {
                    "type": "WATER_CONTAMINATION",
                    "sensor_data": {"ecoli": 5, "ph": 7.8, "turbidity": 1.2},
                    "context": "heavy rain yesterday"
                },
                "top_k": 5
            }
        }


class ReasoningAnalysisRequest(BaseModel):
    incident_id: str
    incident_type: str
    facility_id: str
    sensor_data: Dict
    context: Dict
    urgency: str = "MEDIUM"

    class Config:
        json_schema_extra = {
            "example": {
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
        }


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "ChainSync AI Agents",
        "version": "1.0.0",
        "phase": "Phase 1",
        "agents": [
            "Memory-Enabled Agent",
            "Multi-Step Reasoning Agent"
        ],
        "status": "active",
        "endpoints": {
            "memory": {
                "store": "POST /api/agents/memory/store",
                "recall": "POST /api/agents/memory/recall",
                "stats": "GET /api/agents/memory/stats"
            },
            "reasoning": {
                "analyze": "POST /api/agents/reasoning/analyze"
            }
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agents_initialized": {
            "memory": memory_agent_instance is not None,
            "reasoning": reasoning_agent_instance is not None
        }
    }


# Memory Agent Endpoints

@app.post("/api/agents/memory/store")
async def store_incident(
    request: IncidentStoreRequest,
    agent: MemoryEnabledAgent = Depends(get_memory_agent)
):
    """
    Store an incident in memory for future recall

    This endpoint stores historical incident data in the vector database
    for similarity search and pattern recognition.
    """
    try:
        result = agent.store_incident(request.dict())
        return result
    except Exception as e:
        logger.error(f"Error storing incident: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/memory/recall")
async def recall_incidents(
    request: IncidentRecallRequest,
    agent: MemoryEnabledAgent = Depends(get_memory_agent)
):
    """
    Recall similar incidents from memory

    Uses vector similarity search to find historical incidents
    similar to the current situation.
    """
    try:
        result = agent.recall_similar_incidents(
            current_incident=request.current_incident,
            top_k=request.top_k
        )
        return result
    except Exception as e:
        logger.error(f"Error recalling incidents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/memory/stats")
async def get_memory_stats(
    agent: MemoryEnabledAgent = Depends(get_memory_agent)
):
    """Get memory statistics"""
    try:
        stats = agent.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Reasoning Agent Endpoints

@app.post("/api/agents/reasoning/analyze")
async def analyze_incident(
    request: ReasoningAnalysisRequest,
    agent: MultiStepReasoningAgent = Depends(get_reasoning_agent)
):
    """
    Analyze an incident using multi-step reasoning

    Performs comprehensive analysis including:
    - Sensor data analysis
    - Population impact calculation
    - Response option evaluation
    - Regulatory risk assessment
    - Final recommendation with confidence score
    """
    try:
        result = agent.analyze_incident(request.dict())

        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message"))

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing incident: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Combined workflow endpoint
@app.post("/api/agents/analyze-with-memory")
async def analyze_with_memory(
    request: ReasoningAnalysisRequest,
    memory_agent: MemoryEnabledAgent = Depends(get_memory_agent),
    reasoning_agent: MultiStepReasoningAgent = Depends(get_reasoning_agent)
):
    """
    Combined analysis: Recall similar incidents + Multi-step reasoning

    This endpoint:
    1. Recalls similar historical incidents
    2. Performs multi-step reasoning analysis
    3. Combines both for comprehensive recommendation
    """
    try:
        # Step 1: Recall similar incidents
        recall_request = {
            "current_incident": {
                "type": request.incident_type,
                "facility_id": request.facility_id,
                "sensor_data": request.sensor_data,
                "context": request.context
            },
            "top_k": 5
        }

        memory_result = memory_agent.recall_similar_incidents(
            current_incident=recall_request['current_incident'],
            top_k=5
        )

        # Step 2: Perform reasoning analysis
        reasoning_result = reasoning_agent.analyze_incident(request.dict())

        # Step 3: Combine results
        combined_result = {
            "incident_id": request.incident_id,
            "timestamp": datetime.utcnow().isoformat(),
            "memory_insights": {
                "similar_incidents": memory_result.get('similar_incidents', []),
                "patterns": memory_result.get('patterns', {}),
                "historical_recommendation": memory_result.get('recommendation', '')
            },
            "reasoning_analysis": {
                "steps": reasoning_result.get('reasoning_steps', []),
                "recommendation": reasoning_result.get('final_recommendation', {}),
                "analysis": reasoning_result.get('raw_analysis', '')
            },
            "combined_recommendation": self._combine_recommendations(
                memory_result,
                reasoning_result
            ),
            "slotify_briefing": self._generate_combined_briefing(
                memory_result,
                reasoning_result
            )
        }

        return combined_result

    except Exception as e:
        logger.error(f"Error in combined analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _combine_recommendations(memory_result: Dict, reasoning_result: Dict) -> Dict:
    """Combine memory and reasoning recommendations"""

    memory_patterns = memory_result.get('patterns', {})
    reasoning_rec = reasoning_result.get('final_recommendation', {})

    return {
        "primary_action": reasoning_rec.get('action', 'REVIEW_REQUIRED'),
        "confidence": reasoning_rec.get('confidence', 0.5),
        "historical_success_rate": memory_patterns.get('success_rate', 0),
        "historical_validation": memory_patterns.get('total_similar_incidents', 0) > 0,
        "reasoning": reasoning_rec.get('reasoning', ''),
        "fallback_plan": reasoning_rec.get('fallback_plan', 'Escalate to authorities')
    }


def _generate_combined_briefing(memory_result: Dict, reasoning_result: Dict) -> str:
    """Generate combined briefing for Slotify"""

    memory_patterns = memory_result.get('patterns', {})
    reasoning_rec = reasoning_result.get('final_recommendation', {})

    briefing = f"""COMPREHENSIVE INCIDENT ANALYSIS

RECOMMENDATION: {reasoning_rec.get('action', 'N/A')}
Confidence: {int(reasoning_rec.get('confidence', 0) * 100)}%

HISTORICAL VALIDATION:
• {memory_patterns.get('total_similar_incidents', 0)} similar past incidents
• {int(memory_patterns.get('success_rate', 0) * 100)}% historical success rate
• Average resolution: {memory_patterns.get('average_resolution_time', 'N/A')}

CURRENT ANALYSIS:
{reasoning_rec.get('reasoning', 'See detailed analysis')[:200]}

Full analysis and historical data available in attached reports.
"""
    return briefing.strip()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
