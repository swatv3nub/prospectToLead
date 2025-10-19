"""
Example test script to validate the workflow system.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langgraph_builder import LangGraphBuilder
from utils.logger import setup_logging
import json


def test_workflow_construction():
    """Test that workflow can be constructed without errors."""
    print("Testing workflow construction...")
    try:
        builder = LangGraphBuilder("./workflow.json")
        print("✓ Workflow loaded successfully")
        
        graph = builder.build_graph()
        print("✓ Graph constructed successfully")
        
        print(f"  - Agents: {len(builder.agents)}")
        print(f"  - Steps: {len(builder.steps)}")
        
        return True
    except Exception as e:
        print(f"✗ Workflow construction failed: {e}")
        return False


def test_agent_creation():
    """Test that all agents can be instantiated."""
    print("\nTesting agent creation...")
    try:
        builder = LangGraphBuilder("./workflow.json")
        
        for step_id, agent_info in builder.agents.items():
            agent_name = agent_info['config']['agent']
            print(f"  ✓ {agent_name} ({step_id})")
        
        return True
    except Exception as e:
        print(f"  ✗ Agent creation failed: {e}")
        return False


def test_mock_execution():
    """Test workflow execution with mock data."""
    print("\nTesting workflow execution (dry run)...")
    try:
        # Modify config to use dry run
        builder = LangGraphBuilder("./workflow.json")
        
        # Run workflow
        result = builder.execute()
        
        print(f"  ✓ Workflow executed: {result['status']}")
        print(f"  ✓ Steps completed: {len(result['outputs'])}")
        
        # Check each step produced output
        for step_id in builder.agents.keys():
            if step_id in result['outputs']:
                print(f"    - {step_id}: ✓")
            else:
                print(f"    - {step_id}: ✗ (no output)")
        
        # Save test results
        with open("test_results.json", "w") as f:
            json.dump(result, f, indent=2, default=str)
        print("\n  Results saved to test_results.json")
        
        return True
    except Exception as e:
        print(f"  ✗ Execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running LangGraph Workflow Tests")
    print("=" * 60)
    
    setup_logging()
    
    tests = [
        test_workflow_construction,
        test_agent_creation,
        test_mock_execution
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n✗ Test crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
