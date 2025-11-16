"""
Memory-Enabled Agent for ChainSync
Stores and retrieves historical incidents for learning and pattern recognition
"""

import chromadb
from chromadb.utils import embedding_functions
from typing import Dict, List, Optional
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryEnabledAgent:
    """Agent that stores and recalls historical incidents using vector similarity search"""

    def __init__(self, persist_directory: str = "./chroma_db", openai_api_key: str = None):
        """
        Initialize the Memory-Enabled Agent

        Args:
            persist_directory: Directory to persist ChromaDB data
            openai_api_key: OpenAI API key for embeddings
        """
        logger.info(f"Initializing Memory Agent with persist directory: {persist_directory}")

        # Initialize ChromaDB client
        self.client = chromadb.Client(chromadb.Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))

        # Use OpenAI embeddings for semantic search
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            model_name="text-embedding-3-small"
        )

        # Create or get collection for environmental incidents
        self.collection = self.client.get_or_create_collection(
            name="environmental_incidents",
            embedding_function=self.embedding_function,
            metadata={"description": "Historical environmental incidents for learning"}
        )

        logger.info(f"Memory collection initialized with {self.collection.count()} incidents")

    def store_incident(self, incident_data: Dict) -> Dict:
        """
        Store an incident in memory for future recall

        Args:
            incident_data: Dict containing incident details

        Returns:
            Dict with storage confirmation
        """
        try:
            incident_id = incident_data['incident_id']
            logger.info(f"Storing incident: {incident_id}")

            # Create searchable text representation
            incident_text = self._create_incident_text(incident_data)

            # Prepare metadata
            metadata = {
                "incident_id": incident_id,
                "incident_type": incident_data['incident_type'],
                "facility_id": incident_data['facility_id'],
                "outcome": incident_data['details']['outcome'],
                "resolution_time": incident_data['details']['resolution_time'],
                "cost": str(incident_data['details']['cost']),
                "timestamp": incident_data['timestamp']
            }

            # Store in vector database
            self.collection.add(
                documents=[incident_text],
                metadatas=[metadata],
                ids=[incident_id]
            )

            logger.info(f"Successfully stored incident {incident_id}")

            return {
                "status": "success",
                "message": f"Incident {incident_id} stored in memory",
                "total_incidents": self.collection.count()
            }

        except Exception as e:
            logger.error(f"Error storing incident: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    def recall_similar_incidents(
        self,
        current_incident: Dict,
        top_k: int = 5
    ) -> Dict:
        """
        Retrieve similar incidents from memory

        Args:
            current_incident: Dict with current incident details
            top_k: Number of similar incidents to retrieve

        Returns:
            Dict with similar incidents and patterns
        """
        try:
            logger.info(f"Recalling similar incidents (top {top_k})")

            # Create query text from current incident
            query_text = self._create_incident_text(current_incident)

            # Perform semantic search
            results = self.collection.query(
                query_texts=[query_text],
                n_results=top_k,
                include=['metadatas', 'documents', 'distances']
            )

            # Parse results
            similar_incidents = []
            for i, metadata in enumerate(results['metadatas'][0]):
                similar_incidents.append({
                    "incident_id": metadata['incident_id'],
                    "incident_type": metadata['incident_type'],
                    "facility_id": metadata['facility_id'],
                    "similarity_score": round(1 - results['distances'][0][i], 3),
                    "outcome": metadata['outcome'],
                    "resolution_time": metadata['resolution_time'],
                    "cost": int(metadata['cost']),
                    "timestamp": metadata['timestamp'],
                    "details": results['documents'][0][i]
                })

            # Analyze patterns
            patterns = self._analyze_patterns(similar_incidents)

            # Generate recommendation
            recommendation = self._generate_recommendation(similar_incidents, patterns)

            logger.info(f"Found {len(similar_incidents)} similar incidents")

            return {
                "status": "success",
                "similar_incidents": similar_incidents,
                "patterns": patterns,
                "recommendation": recommendation,
                "query_used": query_text
            }

        except Exception as e:
            logger.error(f"Error recalling incidents: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "similar_incidents": []
            }

    def _create_incident_text(self, incident: Dict) -> str:
        """
        Convert incident data to searchable text

        Args:
            incident: Incident dictionary

        Returns:
            Formatted text string
        """
        text_parts = []

        # Add type and facility
        incident_type = incident.get('incident_type', incident.get('type', 'UNKNOWN'))
        text_parts.append(f"Type: {incident_type}")

        facility_id = incident.get('facility_id', 'UNKNOWN')
        text_parts.append(f"Facility: {facility_id}")

        # Add sensor data if available
        if 'sensor_data' in incident:
            sensors = incident['sensor_data']
            sensor_str = ", ".join([f"{k}={v}" for k, v in sensors.items()])
            text_parts.append(f"Sensors: {sensor_str}")

        # Add symptoms if available
        if 'symptoms' in incident:
            symptoms = incident['symptoms']
            symptom_str = ", ".join([f"{k}={v}" for k, v in symptoms.items()])
            text_parts.append(f"Symptoms: {symptom_str}")

        # Add context if available
        if 'context' in incident:
            context = incident['context']
            if isinstance(context, dict):
                context_str = ", ".join([f"{k}={v}" for k, v in context.items()])
                text_parts.append(f"Context: {context_str}")
            elif isinstance(context, str):
                text_parts.append(f"Context: {context}")

        # Add details if available (for stored incidents)
        if 'details' in incident:
            details = incident['details']
            if 'actions_taken' in details:
                actions = details['actions_taken']
                if isinstance(actions, list):
                    text_parts.append(f"Actions: {', '.join(actions)}")
            if 'outcome' in details:
                text_parts.append(f"Outcome: {details['outcome']}")
            if 'lessons_learned' in details:
                text_parts.append(f"Lessons: {details['lessons_learned']}")

        return " | ".join(text_parts)

    def _analyze_patterns(self, incidents: List[Dict]) -> Dict:
        """
        Find patterns in similar incidents

        Args:
            incidents: List of similar incidents

        Returns:
            Dict with pattern analysis
        """
        if not incidents:
            return {
                "total_similar_incidents": 0,
                "success_rate": 0,
                "average_resolution_time": "N/A",
                "average_cost": 0
            }

        # Calculate success rate
        successful = sum(1 for i in incidents if i.get('outcome') == 'SUCCESS')
        success_rate = successful / len(incidents) if incidents else 0

        # Parse resolution times (assumes format like "6 hours", "2 days")
        resolution_times = []
        for incident in incidents:
            time_str = incident.get('resolution_time', '0 hours')
            try:
                parts = time_str.split()
                if len(parts) >= 2:
                    value = float(parts[0])
                    unit = parts[1].lower()
                    # Convert to hours
                    if 'day' in unit:
                        value *= 24
                    resolution_times.append(value)
            except:
                pass

        avg_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0

        # Calculate average cost
        avg_cost = sum(i.get('cost', 0) for i in incidents) / len(incidents) if incidents else 0

        return {
            "total_similar_incidents": len(incidents),
            "success_rate": round(success_rate, 2),
            "average_resolution_time": f"{int(avg_time)} hours" if avg_time > 0 else "N/A",
            "average_cost": int(avg_cost),
            "most_similar_score": incidents[0].get('similarity_score', 0) if incidents else 0
        }

    def _generate_recommendation(
        self,
        incidents: List[Dict],
        patterns: Dict
    ) -> str:
        """
        Generate recommendation based on memory

        Args:
            incidents: List of similar incidents
            patterns: Pattern analysis

        Returns:
            Recommendation string
        """
        if not incidents:
            return "No similar historical incidents found. Proceed with standard protocols."

        success_rate = patterns.get('success_rate', 0)
        avg_time = patterns.get('average_resolution_time', 'unknown')
        most_similar = incidents[0]

        recommendation = f"""Based on {len(incidents)} similar past incidents:
• Most similar case: {most_similar.get('incident_id', 'N/A')} (similarity: {most_similar.get('similarity_score', 0):.0%})
• Historical success rate: {int(success_rate * 100)}%
• Average resolution time: {avg_time}
• Average cost: ${patterns.get('average_cost', 0):,}

Recommended approach: {most_similar.get('details', 'Review most similar incident for guidance')}
"""

        return recommendation.strip()

    def get_statistics(self) -> Dict:
        """
        Get memory statistics

        Returns:
            Dict with statistics
        """
        total_count = self.collection.count()

        return {
            "total_incidents_stored": total_count,
            "collection_name": self.collection.name,
            "embedding_model": "text-embedding-3-small",
            "status": "active"
        }
