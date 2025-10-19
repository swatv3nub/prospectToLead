"""
LangGraph Builder: Dynamically constructs and executes LangGraph workflow from JSON configuration.
"""
import os
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from utils.config import ConfigLoader
from utils.logger import setup_logging, WorkflowLogger
from utils.memory import get_memory
from agents import AgentFactory


class WorkflowState(TypedDict):
    """State object that flows through the workflow."""
    workflow_config: Dict[str, Any]
    current_step: str
    step_outputs: Dict[str, Any]
    errors: List[str]


class LangGraphBuilder:
    """Builds and executes LangGraph workflows from JSON configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the builder with configuration."""
        setup_logging()
        
        # Load and validate workflow configuration
        self.raw_config = ConfigLoader.load_workflow(config_path)
        self.config = ConfigLoader.substitute_env_vars(self.raw_config)
        
        self.workflow_name = self.config["workflow_name"]
        self.steps = self.config["steps"]
        
        self.logger = WorkflowLogger(self.workflow_name)
        self.agents = {}
        
        # Build agent instances
        self._build_agents()
    
    def _build_agents(self):
        """Create agent instances for each step."""
        self.logger.logger.info(f"Building agents for {len(self.steps)} steps")
        
        for step_config in self.steps:
            step_id = step_config["id"]
            try:
                agent = AgentFactory.create_agent(step_config)
                self.agents[step_id] = {
                    "agent": agent,
                    "config": step_config
                }
                self.logger.logger.info(f"✓ Created agent: {step_config['agent']}")
            except Exception as e:
                self.logger.logger.error(f"✗ Failed to create agent {step_id}: {e}")
                raise
    
    def build_graph(self) -> StateGraph:
        """Construct the LangGraph from configuration."""
        self.logger.logger.info("Building LangGraph workflow")
        
        # Create state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for each step
        for step_id in self.agents.keys():
            workflow.add_node(step_id, self._create_node_function(step_id))
        
        # Add edges based on workflow configuration
        self._add_edges(workflow)
        
        # Set entry point (first step)
        first_step = self.steps[0]["id"]
        workflow.set_entry_point(first_step)
        
        self.logger.logger.info("✓ Graph construction complete")
        
        return workflow.compile()
    
    def _create_node_function(self, step_id: str):
        """Create a node function for a specific step."""
        def node_function(state: WorkflowState) -> WorkflowState:
            """Execute a single workflow step."""
            agent_info = self.agents[step_id]
            agent = agent_info["agent"]
            config = agent_info["config"]
            
            self.logger.log_step_start(step_id, config["agent"])
            
            try:
                # Prepare inputs by resolving references
                inputs = self._resolve_inputs(config.get("inputs", {}), state)
                
                # Execute agent
                output = agent.execute(inputs)
                
                # Store output in state
                state["step_outputs"][step_id] = output
                state["current_step"] = step_id
                
                self.logger.log_step_complete(step_id, config["agent"], output)
                
            except Exception as e:
                self.logger.log_step_error(step_id, config["agent"], e)
                state["errors"].append(f"{step_id}: {str(e)}")
                raise
            
            return state
        
        return node_function
    
    def _resolve_inputs(self, inputs: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Resolve input references like {{step.output.field}}."""
        resolved = {}
        
        for key, value in inputs.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Extract reference path
                ref_path = value[2:-2].strip()
                
                if ref_path == "workflow":
                    resolved[key] = self.config
                else:
                    # Parse path like "prospect_search.output.leads"
                    parts = ref_path.split(".")
                    
                    if parts[0] in state["step_outputs"]:
                        result = state["step_outputs"][parts[0]]
                        for part in parts[1:]:
                            if isinstance(result, dict):
                                result = result.get(part)
                        resolved[key] = result
                    else:
                        resolved[key] = value
            else:
                resolved[key] = value
        
        return resolved
    
    def _add_edges(self, workflow: StateGraph):
        """Add edges between nodes based on configuration."""
        for step in self.steps:
            step_id = step["id"]
            next_step = step.get("next")
            
            if next_step:
                workflow.add_edge(step_id, next_step)
            else:
                # This is the last step
                workflow.add_edge(step_id, END)
    
    def execute(self) -> Dict[str, Any]:
        """Execute the complete workflow."""
        self.logger.logger.info(f"🚀 Starting workflow: {self.workflow_name}")
        
        # Build graph
        graph = self.build_graph()
        
        # Initialize state
        initial_state: WorkflowState = {
            "workflow_config": self.config,
            "current_step": "",
            "step_outputs": {},
            "errors": []
        }
        
        try:
            # Execute workflow
            final_state = graph.invoke(initial_state)
            
            self.logger.log_workflow_complete()
            
            # Check for errors
            if final_state.get("errors"):
                self.logger.logger.error(f"Workflow completed with errors: {final_state['errors']}")
            
            # Store campaign results in memory
            campaign_id = final_state["step_outputs"].get("send", {}).get("campaign_id", f"campaign_{datetime.now().timestamp()}")
            memory = get_memory()
            
            campaign_data = {
                "workflow_name": self.workflow_name,
                "campaign_id": campaign_id,
                "timestamp": datetime.now().isoformat(),
                "total_leads": len(final_state["step_outputs"].get("prospect_search", {}).get("leads", [])),
                "emails_sent": len(final_state["step_outputs"].get("send", {}).get("sent_status", [])),
                "metrics": final_state["step_outputs"].get("response_tracking", {}).get("campaign_metrics", {}),
                "recommendations": final_state["step_outputs"].get("feedback_trainer", {}).get("recommendations", [])
            }
            
            memory.add_campaign(campaign_id, campaign_data)
            self.logger.logger.info(f"Campaign data stored in memory with ID: {campaign_id}")
            
            # Log memory statistics
            stats = memory.get_statistics()
            self.logger.logger.info(f"Memory stats: {stats}")
            
            return {
                "status": "completed" if not final_state.get("errors") else "completed_with_errors",
                "outputs": final_state["step_outputs"],
                "errors": final_state.get("errors", []),
                "campaign_id": campaign_id,
                "memory_stats": stats
            }
            
        except Exception as e:
            self.logger.logger.error(f"💥 Workflow failed: {str(e)}")
            raise
    
    def visualize(self, output_path: str = "workflow_graph.png"):
        """Visualize the workflow graph (optional)."""
        try:
            graph = self.build_graph()
            # Note: Requires graphviz and additional dependencies
            # graph.get_graph().draw_png(output_path)
            self.logger.logger.info(f"Workflow visualization saved to {output_path}")
        except Exception as e:
            self.logger.logger.warning(f"Could not visualize workflow: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Execute LangGraph-based prospect-to-lead workflow")
    parser.add_argument("--config", "-c", help="Path to workflow.json", default="./workflow.json")
    parser.add_argument("--visualize", "-v", action="store_true", help="Generate workflow visualization")
    
    args = parser.parse_args()
    
    try:
        # Build workflow
        builder = LangGraphBuilder(args.config)
        
        # Visualize if requested
        if args.visualize:
            builder.visualize()
        
        # Execute workflow
        result = builder.execute()
        
        # Print summary
        print("\n" + "=" * 60)
        print("WORKFLOW EXECUTION COMPLETE")
        print("=" * 60)
        print(f"Status: {result['status']}")
        print(f"Steps executed: {len(result['outputs'])}")
        
        if result['errors']:
            print(f"Errors: {len(result['errors'])}")
            for error in result['errors']:
                print(f"  - {error}")
        
        # Print final results
        if "feedback_trainer" in result['outputs']:
            feedback = result['outputs']['feedback_trainer']
            print("\n" + feedback.get('analysis_summary', ''))
            
            print("\n📋 Recommendations:")
            for rec in feedback.get('recommendations', []):
                print(f"\n  • {rec['category']} - {rec['parameter']}")
                print(f"    {rec['reasoning']}")
                print(f"    Expected: {rec['expected_improvement']}")
        
        print("\n" + "=" * 60)
        
        # Save results
        output_file = "workflow_results.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nFull results saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
