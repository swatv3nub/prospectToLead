"""
Demo script showing how to use the LangGraph workflow system.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from langgraph_builder import LangGraphBuilder
from utils.logger import setup_logging
import json


def demo_basic_execution():
    """Demonstrate basic workflow execution."""
    print("\n" + "=" * 60)
    print("DEMO: Basic Workflow Execution")
    print("=" * 60 + "\n")
    
    # Setup logging
    setup_logging()
    
    # Build workflow
    print("Building workflow from configuration...")
    builder = LangGraphBuilder("./workflow.json")
    
    print(f"Loaded workflow: {builder.workflow_name}")
    print(f"Number of steps: {len(builder.steps)}")
    print(f"Agents: {', '.join(builder.agents.keys())}")
    
    # Execute
    print("\nExecuting workflow...\n")
    result = builder.execute()
    
    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    print(f"\nStatus: {result['status']}")
    print(f"Steps completed: {len(result['outputs'])}")
    
    # Show prospect search results
    if 'prospect_search' in result['outputs']:
        leads = result['outputs']['prospect_search'].get('leads', [])
        print(f"\n📊 Found {len(leads)} prospects")
        if leads:
            print("\nSample prospect:")
            print(f"  Company: {leads[0].get('company')}")
            print(f"  Contact: {leads[0].get('contact_name')}")
            print(f"  Title: {leads[0].get('title')}")
    
    # Show scoring results
    if 'scoring' in result['outputs']:
        ranked = result['outputs']['scoring'].get('ranked_leads', [])
        print(f"\n⭐ Scored {len(ranked)} leads")
        if ranked:
            top_lead = ranked[0]
            print(f"\nTop lead (score: {top_lead['score']}):")
            print(f"  {top_lead['lead'].get('company')}")
            print(f"  {top_lead['reasoning']}")
    
    # Show outreach results
    if 'outreach_content' in result['outputs']:
        messages = result['outputs']['outreach_content'].get('messages', [])
        print(f"\n✉️  Generated {len(messages)} personalized messages")
        if messages:
            msg = messages[0]
            print(f"\nSample message:")
            print(f"  To: {msg['lead'].get('email')}")
            print(f"  Subject: {msg['subject_line']}")
            print(f"  Preview: {msg['email_body'][:100]}...")
    
    # Show feedback
    if 'feedback_trainer' in result['outputs']:
        feedback = result['outputs']['feedback_trainer']
        print("\n" + feedback.get('analysis_summary', ''))
        
        recs = feedback.get('recommendations', [])
        if recs:
            print(f"\n💡 {len(recs)} recommendations for improvement:")
            for rec in recs[:3]:  # Show first 3
                print(f"\n  • {rec['category']}: {rec['parameter']}")
                print(f"    {rec['reasoning']}")
    
    print("\n" + "=" * 60)


def demo_custom_workflow():
    """Demonstrate using a custom workflow configuration."""
    print("\n" + "=" * 60)
    print("DEMO: Custom Workflow Configuration")
    print("=" * 60 + "\n")
    
    # Create custom workflow
    custom_config = {
        "workflow_name": "QuickTest",
        "description": "Quick test workflow",
        "steps": [
            {
                "id": "search",
                "agent": "ProspectSearchAgent",
                "inputs": {
                    "icp": {
                        "industry": "Technology",
                        "location": "USA",
                        "employee_count": {"min": 50, "max": 200}
                    },
                    "max_results": 5
                },
                "instructions": "Find 5 prospects",
                "tools": [],
                "next": None
            }
        ]
    }
    
    # Save custom config
    with open("custom_workflow.json", "w") as f:
        json.dump(custom_config, f, indent=2)
    
    print("Created custom workflow with 1 step")
    print("Configuration saved to: custom_workflow.json")
    
    # Execute custom workflow
    builder = LangGraphBuilder("custom_workflow.json")
    result = builder.execute()
    
    print(f"\nStatus: {result['status']}")
    leads = result['outputs']['search'].get('leads', [])
    print(f"Found {len(leads)} prospects\n")


def demo_step_by_step():
    """Show detailed step-by-step execution."""
    print("\n" + "=" * 60)
    print("DEMO: Step-by-Step Workflow Details")
    print("=" * 60 + "\n")
    
    builder = LangGraphBuilder("./workflow_simple.json")
    
    print("Workflow steps:\n")
    for i, step in enumerate(builder.steps, 1):
        print(f"{i}. {step['agent']} ({step['id']})")
        print(f"   Purpose: {step['instructions']}")
        print(f"   Next: {step.get('next', 'END')}\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LangGraph Prospect-to-Lead Workflow - Demo")
    print("=" * 60)
    
    try:
        # Run demos
        demo_step_by_step()
        demo_basic_execution()
        
        print("\n✅ Demo completed successfully!")
        print("\nNext steps:")
        print("  1. Review workflow_results.json for full output")
        print("  2. Check logs/workflow.log for detailed logs")
        print("  3. Modify workflow.json to customize behavior")
        print("  4. Add your API keys to .env for real data")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
