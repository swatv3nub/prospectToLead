"""
Agent factory for creating agent instances from configuration.
"""
from typing import Dict, Any
from agents.base_agent import BaseAgent
from agents.prospect_search_agent import ProspectSearchAgent
from agents.enrichment_agent import DataEnrichmentAgent
from agents.scoring_agent import ScoringAgent
from agents.outreach_content_agent import OutreachContentAgent
from agents.outreach_executor_agent import OutreachExecutorAgent
from agents.response_tracker_agent import ResponseTrackerAgent
from agents.feedback_trainer_agent import FeedbackTrainerAgent
from langchain_openai import ChatOpenAI
from utils.config import get_api_config
import os


class AgentFactory:
    """Factory for creating agent instances."""
    
    AGENT_CLASSES = {
        "ProspectSearchAgent": ProspectSearchAgent,
        "DataEnrichmentAgent": DataEnrichmentAgent,
        "ScoringAgent": ScoringAgent,
        "OutreachContentAgent": OutreachContentAgent,
        "OutreachExecutorAgent": OutreachExecutorAgent,
        "ResponseTrackerAgent": ResponseTrackerAgent,
        "FeedbackTrainerAgent": FeedbackTrainerAgent
    }
    
    @classmethod
    def create_agent(cls, agent_config: Dict[str, Any]) -> BaseAgent:
        """Create an agent instance from configuration."""
        agent_name = agent_config.get("agent")
        
        if agent_name not in cls.AGENT_CLASSES:
            raise ValueError(f"Unknown agent type: {agent_name}")
        
        # Create LLM instance for agents that need reasoning
        llm = None
        if agent_name in ["OutreachContentAgent", "FeedbackTrainerAgent"]:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                llm = ChatOpenAI(
                    api_key=openai_key,
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    temperature=0.7
                )
        
        agent_class = cls.AGENT_CLASSES[agent_name]
        return agent_class(agent_config, llm=llm)
