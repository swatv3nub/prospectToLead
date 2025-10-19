"""
Base agent class with ReAct reasoning pattern.
"""
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from utils.logger import get_logger
import json


class BaseAgent(ABC):
    """Base class for all workflow agents implementing ReAct pattern."""
    
    def __init__(self, agent_config: Dict[str, Any], llm: Optional[ChatOpenAI] = None):
        self.agent_id = agent_config.get("id")
        self.agent_name = agent_config.get("agent")
        self.instructions = agent_config.get("instructions")
        self.tools_config = agent_config.get("tools", [])
        self.output_schema = agent_config.get("output_schema", {})
        self.logger = get_logger(f"agent.{self.agent_name}")
        self.llm = llm
        
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with ReAct pattern: Reason -> Act -> Observe."""
        self.logger.info(f"Executing {self.agent_name} with inputs")
        
        try:
            # Reason: Analyze inputs and plan actions
            reasoning = self._reason(inputs)
            self.logger.info(f"Reasoning: {reasoning}")
            
            # Act: Execute the core agent logic
            result = self._act(inputs, reasoning)
            
            # Observe: Validate and structure output
            output = self._observe(result)
            
            self.logger.info(f"{self.agent_name} completed successfully")
            return output
            
        except Exception as e:
            self.logger.error(f"Error in {self.agent_name}: {str(e)}")
            raise
    
    def _reason(self, inputs: Dict[str, Any]) -> str:
        """Reasoning step: Analyze inputs and plan approach."""
        if self.llm:
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"""You are a reasoning agent for {self.agent_name}.
                Task: {self.instructions}
                
                Analyze the inputs and explain your approach in 2-3 sentences.
                Be specific about what you'll do and why."""),
                ("human", f"Inputs: {json.dumps(inputs, indent=2)}")
            ])
            
            response = self.llm.invoke(prompt.format_messages())
            return response.content
        else:
            return f"Processing {self.agent_name} with provided inputs"
    
    @abstractmethod
    def _act(self, inputs: Dict[str, Any], reasoning: str) -> Dict[str, Any]:
        """Action step: Execute core agent logic. Must be implemented by subclasses."""
        pass
    
    def _observe(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Observation step: Validate and structure output."""
        # Basic validation - ensure result matches expected schema structure
        if self.output_schema:
            # Simple validation: check if keys exist
            for key in self.output_schema.keys():
                if key not in result:
                    self.logger.warning(f"Missing expected output key: {key}")
        
        return result
    
    def _get_tool_config(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific tool."""
        for tool in self.tools_config:
            if tool.get("name") == tool_name:
                return tool.get("config", {})
        return None
