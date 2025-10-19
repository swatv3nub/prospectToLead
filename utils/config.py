"""
Configuration loader and validator for the LangGraph workflow system.
"""
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
import jsonschema

# Load environment variables
load_dotenv()


class ConfigLoader:
    """Loads and validates workflow configuration."""
    
    WORKFLOW_SCHEMA = {
        "type": "object",
        "required": ["workflow_name", "steps"],
        "properties": {
            "workflow_name": {"type": "string"},
            "description": {"type": "string"},
            "version": {"type": "string"},
            "steps": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["id", "agent", "instructions"],
                    "properties": {
                        "id": {"type": "string"},
                        "agent": {"type": "string"},
                        "inputs": {"type": "object"},
                        "instructions": {"type": "string"},
                        "tools": {"type": "array"},
                        "output_schema": {"type": "object"},
                        "next": {"type": ["string", "null"]}
                    }
                }
            }
        }
    }
    
    @staticmethod
    def load_workflow(config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load and validate workflow configuration from JSON file."""
        if config_path is None:
            config_path = os.getenv("WORKFLOW_CONFIG_PATH", "./workflow.json")
        
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Workflow config not found: {config_path}")
        
        with open(config_file, 'r') as f:
            workflow_config = json.load(f)
        
        # Validate schema
        try:
            jsonschema.validate(instance=workflow_config, schema=ConfigLoader.WORKFLOW_SCHEMA)
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError(f"Invalid workflow configuration: {e.message}")
        
        return workflow_config
    
    @staticmethod
    def substitute_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
        """Replace {{ENV_VAR}} placeholders with actual environment variables."""
        config_str = json.dumps(config)
        
        # Find all {{VAR}} patterns and replace
        import re
        pattern = r'\{\{([A-Z_]+)\}\}'
        
        def replacer(match):
            var_name = match.group(1)
            value = os.getenv(var_name, '')
            if not value:
                print(f"Warning: Environment variable {var_name} not set")
            return value
        
        config_str = re.sub(pattern, replacer, config_str)
        return json.loads(config_str)
    
    @staticmethod
    def get_env(key: str, default: Optional[str] = None) -> str:
        """Get environment variable with optional default."""
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Required environment variable {key} not set")
        return value


def get_api_config(tool_name: str) -> Dict[str, Any]:
    """Get API configuration for a specific tool."""
    configs = {
        "OpenAI": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        },
        "ClayAPI": {
            "api_key": os.getenv("CLAY_API_KEY"),
            "endpoint": "https://api.clay.com/search"
        },
        "ApolloAPI": {
            "api_key": os.getenv("APOLLO_API_KEY"),
            "endpoint": "https://api.apollo.io/v1"
        },
        "Clearbit": {
            "api_key": os.getenv("CLEARBIT_API_KEY"),
            "endpoint": "https://person.clearbit.com/v2"
        },
        "PeopleDataLabs": {
            "api_key": os.getenv("PEOPLEDATALABS_API_KEY"),
            "endpoint": "https://api.peopledatalabs.com/v5"
        },
        "SendGrid": {
            "api_key": os.getenv("SENDGRID_API_KEY"),
            "from_email": os.getenv("SENDGRID_FROM_EMAIL")
        },
        "GoogleSheets": {
            "credentials_file": os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials.json"),
            "sheet_id": os.getenv("GOOGLE_SHEET_ID")
        }
    }
    
    return configs.get(tool_name, {})
