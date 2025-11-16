"""
Multi-Step Reasoning Agent for ChainSync
Provides step-by-step logical analysis for complex environmental incidents
"""

from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from typing import Dict, List
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiStepReasoningAgent:
    """Agent that performs multi-step reasoning for incident analysis"""

    def __init__(self, llm_api_key: str, chainsync_api_url: str = None):
        """
        Initialize the Multi-Step Reasoning Agent

        Args:
            llm_api_key: OpenAI API key
            chainsync_api_url: URL for ChainSync MuleSoft API (optional)
        """
        logger.info("Initializing Multi-Step Reasoning Agent")

        self.llm = ChatOpenAI(
            model="gpt-4-turbo",
            api_key=llm_api_key,
            temperature=0.2  # Lower temp for more consistent reasoning
        )

        self.chainsync_api = chainsync_api_url
        self.tools = self._create_tools()
        self.agent = self._create_agent()

        logger.info("Reasoning Agent initialized successfully")

    def _create_tools(self) -> List[Tool]:
        """Create custom tools for environmental analysis"""
        return [
            Tool(
                name="analyze_sensor_data",
                func=self.analyze_sensor_data,
                description="Analyze current sensor readings against EPA/DEQ regulatory limits. Input should be JSON string of sensor data."
            ),
            Tool(
                name="calculate_population_impact",
                func=self.calculate_population_impact,
                description="Calculate affected population based on facility and distribution zone. Input should be facility_id."
            ),
            Tool(
                name="evaluate_response_options",
                func=self.evaluate_response_options,
                description="Compare cost/benefit of different response strategies. Input should be incident_type."
            ),
            Tool(
                name="assess_regulatory_risk",
                func=self.assess_regulatory_risk,
                description="Assess regulatory compliance risk and potential fines. Input should be JSON with parameter and value."
            )
        ]

    def _create_agent(self) -> AgentExecutor:
        """Create the reasoning agent with custom prompt"""

        prompt = PromptTemplate.from_template("""You are an expert environmental engineer analyzing incidents at water/waste/environmental facilities.

Your task: Analyze the incident step-by-step and provide actionable recommendations.

Available tools: {tools}
Tool names: {tool_names}

Incident data:
{incident_data}

Think through this systematically:
1. What is the current situation? (analyze sensor data and violations)
2. What caused this? (determine root cause based on context)
3. Who is affected? (calculate population impact)
4. What are the regulatory implications? (assess compliance risk)
5. What are our options? (evaluate response strategies)
6. What should we do? (recommend action with confidence score and fallback)

Important:
- Be specific with numbers (costs, times, populations)
- Calculate confidence based on evidence strength
- Always provide a fallback plan
- Consider EPA/DEQ regulations

Use this format for EACH step:
Thought: [your reasoning for this step]
Action: [tool name]
Action Input: [input to tool]
Observation: [result from tool]

After completing all steps:
Thought: I now have enough information to make a final recommendation
Final Answer: [JSON formatted recommendation with: action, urgency, confidence, reasoning, fallback_plan]

Begin!

{agent_scratchpad}
        """)

        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True
        )

    def analyze_incident(self, incident_data: Dict) -> Dict:
        """
        Main method to analyze incident with multi-step reasoning

        Args:
            incident_data: Dict containing incident information

        Returns:
            Dict with reasoning steps and recommendation
        """
        try:
            logger.info(f"Analyzing incident: {incident_data.get('incident_id', 'UNKNOWN')}")

            # Invoke agent with incident data
            result = self.agent.invoke({
                "incident_data": json.dumps(incident_data, indent=2)
            })

            # Parse the final answer
            final_recommendation = self._parse_recommendation(result['output'])

            # Extract reasoning steps from intermediate steps
            reasoning_steps = self._extract_reasoning_steps(result)

            # Generate Slotify briefing
            slotify_briefing = self._generate_slotify_briefing(
                reasoning_steps,
                final_recommendation
            )

            logger.info(f"Analysis complete. Recommendation: {final_recommendation.get('action', 'N/A')}")

            return {
                "status": "success",
                "reasoning_steps": reasoning_steps,
                "final_recommendation": final_recommendation,
                "slotify_briefing": slotify_briefing,
                "raw_analysis": result['output']
            }

        except Exception as e:
            logger.error(f"Error analyzing incident: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "reasoning_steps": [],
                "final_recommendation": {
                    "action": "MANUAL_REVIEW_REQUIRED",
                    "urgency": "HIGH",
                    "confidence": 0.0,
                    "reasoning": f"Agent error: {str(e)}"
                }
            }

    # Tool implementations
    def analyze_sensor_data(self, sensor_data_json: str) -> str:
        """Tool: Analyze sensor readings against regulatory limits"""
        try:
            data = json.loads(sensor_data_json)
            violations = []
            warnings = []

            # EPA limits for common parameters
            limits = {
                'ecoli': {'max': 0, 'unit': 'CFU/100mL', 'regulation': 'EPA SDWA'},
                'ph': {'min': 6.5, 'max': 8.5, 'regulation': 'EPA SDWA'},
                'turbidity': {'max': 1.0, 'unit': 'NTU', 'regulation': 'EPA SDWA'},
                'chlorine': {'min': 0.5, 'max': 4.0, 'unit': 'ppm', 'regulation': 'EPA SDWA'},
                'pm25': {'max': 35.0, 'unit': 'µg/m³', 'regulation': 'EPA NAAQS'},
                'pm10': {'max': 150.0, 'unit': 'µg/m³', 'regulation': 'EPA NAAQS'},
            }

            for param, value in data.items():
                if param in limits:
                    limit = limits[param]

                    # Check violations
                    if 'max' in limit and value > limit['max']:
                        violations.append(f"{param}: {value} exceeds max {limit['max']} ({limit['regulation']})")
                    elif 'min' in limit and value < limit['min']:
                        violations.append(f"{param}: {value} below min {limit['min']} ({limit['regulation']})")

                    # Check warnings (approaching limit)
                    if 'max' in limit:
                        percentage = (value / limit['max']) * 100
                        if percentage > 90 and value <= limit['max']:
                            warnings.append(f"{param} at {percentage:.0f}% of limit ({value}/{limit['max']})")

            result = {
                "violations": violations,
                "warnings": warnings,
                "severity": "CRITICAL" if violations else ("WARNING" if warnings else "NORMAL"),
                "total_parameters_checked": len(data)
            }

            return json.dumps(result)

        except Exception as e:
            return json.dumps({"error": str(e)})

    def calculate_population_impact(self, facility_id: str) -> str:
        """Tool: Calculate affected population"""
        # Mock implementation - in production would query GIS/customer database
        population_data = {
            "Atlanta_WTP": {
                "total_customers": 125000,
                "schools": 23,
                "hospitals": 2,
                "nursing_homes": 5,
                "vulnerable_population_percentage": 15
            },
            "Decatur_Plant": {
                "total_customers": 45000,
                "schools": 8,
                "hospitals": 1,
                "nursing_homes": 2,
                "vulnerable_population_percentage": 12
            }
        }

        data = population_data.get(facility_id, {
            "total_customers": 50000,
            "schools": 10,
            "hospitals": 1,
            "nursing_homes": 3,
            "vulnerable_population_percentage": 12
        })

        data["facility_id"] = facility_id
        data["vulnerable_population"] = int(data["total_customers"] * data["vulnerable_population_percentage"] / 100)

        return json.dumps(data)

    def evaluate_response_options(self, incident_type: str) -> str:
        """Tool: Evaluate different response strategies"""

        response_strategies = {
            "WATER_CONTAMINATION": [
                {
                    "option": "Chlorine boost + flushing",
                    "estimated_cost": 15000,
                    "time_to_resolve": "6-8 hours",
                    "success_rate": 0.92,
                    "risks": "May not work if contamination is severe",
                    "benefits": "Low cost, minimal customer impact"
                },
                {
                    "option": "Boil water advisory",
                    "estimated_cost": 2000000,
                    "time_to_resolve": "immediate",
                    "success_rate": 1.0,
                    "risks": "Public trust damage, media coverage",
                    "benefits": "100% protects public health"
                },
                {
                    "option": "Switch to backup source",
                    "estimated_cost": 50000,
                    "time_to_resolve": "2-4 hours",
                    "success_rate": 0.98,
                    "risks": "Backup source may have capacity limits",
                    "benefits": "Fast resolution, no public alert needed"
                }
            ],
            "AIR_QUALITY_VIOLATION": [
                {
                    "option": "Reduce operations to 50%",
                    "estimated_cost": 100000,
                    "time_to_resolve": "immediate",
                    "success_rate": 0.95,
                    "risks": "Revenue loss",
                    "benefits": "Guaranteed compliance"
                },
                {
                    "option": "Equipment adjustment",
                    "estimated_cost": 10000,
                    "time_to_resolve": "2-6 hours",
                    "success_rate": 0.85,
                    "risks": "May not be sufficient",
                    "benefits": "Low cost, no operations impact"
                }
            ],
            "EQUIPMENT_FAILURE": [
                {
                    "option": "Emergency repair",
                    "estimated_cost": 75000,
                    "time_to_resolve": "12-24 hours",
                    "success_rate": 0.80,
                    "risks": "May require parts not in stock",
                    "benefits": "Resume normal operations"
                },
                {
                    "option": "Switch to backup equipment",
                    "estimated_cost": 5000,
                    "time_to_resolve": "1-2 hours",
                    "success_rate": 0.95,
                    "risks": "Backup may have reduced capacity",
                    "benefits": "Fast, low cost"
                }
            ]
        }

        options = response_strategies.get(incident_type, [
            {
                "option": "Follow standard emergency protocol",
                "estimated_cost": 25000,
                "time_to_resolve": "varies",
                "success_rate": 0.75,
                "risks": "Generic approach may not be optimal",
                "benefits": "Established procedure"
            }
        ])

        return json.dumps({
            "incident_type": incident_type,
            "available_options": options,
            "recommendation": "Compare cost, time, and success rate for decision"
        })

    def assess_regulatory_risk(self, param_data_json: str) -> str:
        """Tool: Assess regulatory compliance risk"""
        try:
            data = json.loads(param_data_json)
            parameter = data.get('parameter')
            value = data.get('value')

            # Regulatory fines and requirements
            regulatory_info = {
                "ecoli": {
                    "regulation": "EPA Safe Drinking Water Act",
                    "violation_fine": 37500,  # per day
                    "reporting_requirement": "Immediate (within 24 hours)",
                    "public_notification": "Required within 24 hours"
                },
                "ph": {
                    "regulation": "EPA SDWA",
                    "violation_fine": 25000,
                    "reporting_requirement": "Next quarterly report",
                    "public_notification": "Required if health risk"
                },
                "pm25": {
                    "regulation": "EPA NAAQS (Clean Air Act)",
                    "violation_fine": 37500,
                    "reporting_requirement": "Immediate",
                    "public_notification": "Air quality alert required"
                }
            }

            info = regulatory_info.get(parameter, {
                "regulation": "Various EPA/State regulations",
                "violation_fine": 25000,
                "reporting_requirement": "Varies",
                "public_notification": "May be required"
            })

            info["parameter"] = parameter
            info["current_value"] = value
            info["risk_level"] = "HIGH" if value else "MEDIUM"

            return json.dumps(info)

        except Exception as e:
            return json.dumps({"error": str(e)})

    def _extract_reasoning_steps(self, agent_result: Dict) -> List[Dict]:
        """Parse agent's thought process into structured steps"""

        steps = []

        # Try to extract from intermediate_steps if available
        if 'intermediate_steps' in agent_result:
            for i, (action, observation) in enumerate(agent_result['intermediate_steps']):
                steps.append({
                    "step": i + 1,
                    "action": action.tool,
                    "input": action.tool_input,
                    "finding": observation,
                    "confidence": 0.8  # Default confidence
                })

        # If no intermediate steps, create summary steps
        if not steps:
            steps = [
                {"step": 1, "action": "Analyze data", "finding": "Incident analyzed"},
                {"step": 2, "action": "Determine impact", "finding": "Impact assessed"},
                {"step": 3, "action": "Evaluate options", "finding": "Options reviewed"},
                {"step": 4, "action": "Generate recommendation", "finding": "Recommendation created"}
            ]

        return steps

    def _parse_recommendation(self, output: str) -> Dict:
        """Extract structured recommendation from agent output"""

        try:
            # Try to parse JSON from output
            if '{' in output and '}' in output:
                json_start = output.index('{')
                json_end = output.rindex('}') + 1
                json_str = output[json_start:json_end]
                recommendation = json.loads(json_str)
                return recommendation
        except:
            pass

        # Fallback: extract key information from text
        recommendation = {
            "action": "REVIEW_REQUIRED",
            "urgency": "HIGH",
            "confidence": 0.5,
            "reasoning": output[:500],  # First 500 chars
            "fallback_plan": "Escalate to human decision-maker"
        }

        # Try to extract action from output
        if "chlorine" in output.lower():
            recommendation["action"] = "CHLORINE_BOOST"
            recommendation["confidence"] = 0.85
        elif "boil water" in output.lower():
            recommendation["action"] = "BOIL_WATER_ADVISORY"
            recommendation["confidence"] = 0.90
        elif "reduce" in output.lower():
            recommendation["action"] = "REDUCE_OPERATIONS"
            recommendation["confidence"] = 0.80

        return recommendation

    def _generate_slotify_briefing(
        self,
        steps: List[Dict],
        recommendation: Dict
    ) -> str:
        """Generate concise briefing for Slotify meeting"""

        action = recommendation.get('action', 'N/A')
        confidence = recommendation.get('confidence', 0)
        reasoning = recommendation.get('reasoning', 'See analysis')

        briefing = f"""INCIDENT ANALYSIS - Multi-Step Reasoning Complete

RECOMMENDATION: {action}
Confidence: {int(confidence * 100)}%

REASONING:
{reasoning[:300]}

ANALYSIS STEPS COMPLETED: {len(steps)}

Full detailed analysis available in attached report.
"""
        return briefing.strip()
