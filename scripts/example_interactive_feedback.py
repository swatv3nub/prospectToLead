"""
Example: Using Interactive Feedback Training

This script demonstrates how to use the interactive feedback features.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.feedback_trainer_agent import FeedbackTrainerAgent
from utils.logger import get_logger
from utils.memory import get_memory


def example_non_interactive():
    """Example: Running FeedbackTrainer without user interaction (default)."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Non-Interactive Mode (Default)")
    print("="*70)
    
    logger = get_logger("example")
    
    # Default mode - no user prompts
    agent = FeedbackTrainerAgent(
        agent_name="FeedbackTrainer",
        model="gpt-4o-mini",
        logger=logger,
        interactive_mode=False  # Default - automatic processing
    )
    
    # Sample campaign data
    inputs = {
        "responses": [
            {"replied": True, "reply_content": "Interested in learning more"},
            {"replied": True, "reply_content": "Not interested"},
        ],
        "campaign_metrics": {
            "total_sent": 25,
            "open_rate": 28.0,
            "click_rate": 5.5,
            "reply_rate": 2.0
        },
        "workflow_config": {}
    }
    
    # This will generate recommendations without prompting user
    result = agent.act(inputs)
    
    print(f"\n[OK] Generated {len(result['recommendations'])} recommendations")
    print("All recommendations marked as 'pending' for later review\n")


def example_interactive():
    """Example: Running FeedbackTrainer with user interaction."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Interactive Mode")
    print("="*70)
    print("User will be prompted to approve/reject each recommendation\n")
    
    logger = get_logger("example")
    
    # Interactive mode - prompts user for decisions
    agent = FeedbackTrainerAgent(
        agent_name="FeedbackTrainer",
        model="gpt-4o-mini",
        logger=logger,
        interactive_mode=True  # Enable user interaction
    )
    
    # Sample campaign data
    inputs = {
        "responses": [
            {"replied": True, "reply_content": "Interested in learning more"},
            {"replied": True, "reply_content": "Not interested"},
        ],
        "campaign_metrics": {
            "total_sent": 25,
            "open_rate": 28.0,
            "click_rate": 5.5,
            "reply_rate": 2.0
        },
        "workflow_config": {}
    }
    
    # This will prompt user for feedback on each recommendation
    result = agent.act(inputs)
    
    print(f"\n[OK] Processed {len(result['recommendations'])} recommendations with user feedback")


def example_review_pending():
    """Example: Review pending recommendations from memory."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Review Pending Recommendations")
    print("="*70)
    
    memory = get_memory()
    pending = memory.get_pending_recommendations()
    
    if not pending:
        print("\nNo pending recommendations in memory.")
        print("Run Example 1 first to generate some recommendations.\n")
        return
    
    print(f"\nFound {len(pending)} pending recommendations:\n")
    
    for i, rec in enumerate(pending, 1):
        data = rec['data']
        print(f"{i}. {data['category']} / {data['parameter']}")
        print(f"   Current: {data['current_value']}")
        print(f"   Suggested: {data['suggested_value']}")
        print(f"   Reasoning: {data['reasoning']}\n")
    
    print("Use 'python scripts/interactive_feedback.py --approve-pending' to review these.\n")


def main():
    """Main menu for examples."""
    print("\n" + "="*70)
    print("INTERACTIVE FEEDBACK TRAINING EXAMPLES")
    print("="*70)
    print("\nChoose an example to run:")
    print("  1. Non-Interactive Mode (automatic, recommendations pending)")
    print("  2. Interactive Mode (user prompts for each recommendation)")
    print("  3. Review Pending Recommendations")
    print("  4. Exit")
    
    choice = input("\nSelect [1-4]: ").strip()
    
    if choice == '1':
        example_non_interactive()
    elif choice == '2':
        example_interactive()
    elif choice == '3':
        example_review_pending()
    elif choice == '4':
        print("\n[OK] Exiting...\n")
        return
    else:
        print("\n[ERROR] Invalid choice\n")


if __name__ == "__main__":
    main()
