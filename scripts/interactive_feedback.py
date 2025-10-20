"""
Interactive Feedback Training Script
Allows users to provide feedback on campaign performance and approve/modify recommendations.
"""
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.memory import get_memory
from agents.feedback_trainer_agent import FeedbackTrainerAgent
from utils.logger import get_logger
from datetime import datetime
import json


def display_campaign_summary(campaign_id: Optional[str] = None):
    """Display summary of campaign(s) from memory."""
    memory = get_memory()
    
    if campaign_id:
        # Show specific campaign
        campaigns = [c for c in memory.get_campaign_history(limit=100) 
                    if c['metadata'].get('campaign_id') == campaign_id]
        if not campaigns:
            print(f"\n[ERROR] Campaign '{campaign_id}' not found in memory")
            return None
    else:
        # Show recent campaigns
        campaigns = memory.get_campaign_history(limit=10)
    
    if not campaigns:
        print("\n[ERROR] No campaigns found in memory")
        return None
    
    print("\n" + "="*70)
    print("AVAILABLE CAMPAIGNS")
    print("="*70)
    
    for i, campaign in enumerate(campaigns, 1):
        meta = campaign['metadata']
        print(f"\n{i}. Campaign: {meta.get('campaign_id', 'Unknown')}")
        print(f"   Date: {meta.get('timestamp', 'Unknown')}")
        print(f"   Leads: {meta.get('total_leads', 0)}")
        print(f"   Sent: {meta.get('emails_sent', 0)}")
        print(f"   Open Rate: {meta.get('open_rate', 0)}%")
        print(f"   Click Rate: {meta.get('click_rate', 0)}%")
        print(f"   Reply Rate: {meta.get('reply_rate', 0)}%")
    
    return campaigns


def get_campaign_metrics(campaign_id: str) -> Dict[str, Any]:
    """Retrieve campaign metrics from memory."""
    memory = get_memory()
    campaigns = memory.get_campaign_history(limit=100)
    
    for campaign in campaigns:
        if campaign['metadata'].get('campaign_id') == campaign_id:
            return campaign['metadata']
    
    return {}


def get_campaign_responses(campaign_id: str) -> List[Dict[str, Any]]:
    """Get responses/interactions for a campaign."""
    memory = get_memory()
    
    # Get all interactions and filter by campaign
    all_interactions = memory.interactions.get()
    
    responses = []
    if all_interactions and all_interactions.get('metadatas'):
        for i, meta in enumerate(all_interactions['metadatas']):
            if meta.get('campaign_id') == campaign_id:
                responses.append({
                    'email': meta.get('lead_email'),
                    'interaction_type': meta.get('interaction_type'),
                    'timestamp': meta.get('timestamp'),
                    'replied': meta.get('interaction_type') == 'replied',
                    'reply_content': meta.get('reply_content', '')
                })
    
    return responses


def view_pending_recommendations():
    """View all pending recommendations."""
    memory = get_memory()
    pending = memory.get_pending_recommendations()
    
    print("\n" + "="*70)
    print("PENDING RECOMMENDATIONS")
    print("="*70)
    
    if not pending:
        print("\nNo pending recommendations.")
        return []
    
    for i, rec in enumerate(pending, 1):
        data = rec['data']
        print(f"\n{i}. {data.get('category', 'Unknown')}: {data.get('parameter', 'Unknown')}")
        print(f"   Current: {data.get('current_value')}")
        print(f"   Suggested: {data.get('suggested_value')}")
        print(f"   Reasoning: {data.get('reasoning')}")
        print(f"   Expected: {data.get('expected_improvement')}")
    
    return pending


def approve_pending_recommendations():
    """Interactively approve or reject pending recommendations."""
    memory = get_memory()
    pending = memory.get_pending_recommendations()
    
    if not pending:
        print("\nNo pending recommendations to review.")
        return
    
    print("\n" + "="*70)
    print("REVIEW PENDING RECOMMENDATIONS")
    print("="*70)
    
    for i, rec in enumerate(pending, 1):
        data = rec['data']
        rec_id = rec['id']
        
        print(f"\n{'-'*70}")
        print(f"Recommendation {i}/{len(pending)}")
        print(f"{'-'*70}")
        print(f"Category: {data.get('category')}")
        print(f"Parameter: {data.get('parameter')}")
        print(f"Current: {data.get('current_value')}")
        print(f"Suggested: {data.get('suggested_value')}")
        print(f"Reasoning: {data.get('reasoning')}")
        print(f"Expected Impact: {data.get('expected_improvement')}")
        
        print("\nOptions:")
        print("  [a] Approve")
        print("  [r] Reject")
        print("  [s] Skip")
        
        choice = input("\nYour choice [a/r/s]: ").strip().lower()
        
        if choice == 'a':
            data['approval_status'] = 'approved'
            data['approved_timestamp'] = datetime.now().isoformat()
            # Update in memory (re-add with same ID)
            memory.recommendations.update(
                ids=[rec_id],
                metadatas=[data]
            )
            print("[OK] Approved")
            
        elif choice == 'r':
            reason = input("Rejection reason (optional): ").strip()
            data['approval_status'] = 'rejected'
            data['rejection_reason'] = reason or "Not specified"
            data['rejected_timestamp'] = datetime.now().isoformat()
            memory.recommendations.update(
                ids=[rec_id],
                metadatas=[data]
            )
            print("[OK] Rejected")
        else:
            print("[OK] Skipped")


def run_interactive_analysis(campaign_id: str):
    """Run interactive feedback analysis on a specific campaign."""
    print("\n" + "="*70)
    print("INTERACTIVE FEEDBACK ANALYSIS")
    print("="*70)
    print(f"Campaign: {campaign_id}\n")
    
    # Get campaign data
    metrics = get_campaign_metrics(campaign_id)
    if not metrics:
        print(f"[ERROR] Campaign '{campaign_id}' not found")
        return
    
    responses = get_campaign_responses(campaign_id)
    
    print(f"Found {len(responses)} interactions for this campaign")
    
    # Initialize agent in interactive mode
    logger = get_logger("interactive_feedback")
    agent = FeedbackTrainerAgent(
        agent_name="FeedbackTrainer",
        model="gpt-4o-mini",
        logger=logger,
        interactive_mode=True
    )
    
    # Prepare inputs
    inputs = {
        "responses": responses,
        "campaign_metrics": metrics,
        "workflow_config": {}
    }
    
    # Run analysis with user interaction
    result = agent.act(inputs)
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nTotal recommendations: {len(result['recommendations'])}")
    
    approved = sum(1 for r in result['recommendations'] if r.get('approval_status') == 'approved')
    rejected = sum(1 for r in result['recommendations'] if r.get('approval_status') == 'rejected')
    pending = sum(1 for r in result['recommendations'] if r.get('approval_status') == 'pending')
    
    print(f"Approved: {approved}")
    print(f"Rejected: {rejected}")
    print(f"Pending: {pending}")
    
    # Save to file
    output_file = Path(__file__).parent.parent / "logs" / f"feedback_{campaign_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n[OK] Analysis saved to: {output_file}")


def main():
    """Main interactive menu."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Interactive feedback training")
    parser.add_argument("--list-campaigns", action="store_true", help="List available campaigns")
    parser.add_argument("--analyze", type=str, help="Run interactive analysis on campaign ID")
    parser.add_argument("--view-pending", action="store_true", help="View pending recommendations")
    parser.add_argument("--approve-pending", action="store_true", help="Review and approve pending recommendations")
    
    args = parser.parse_args()
    
    if args.list_campaigns:
        display_campaign_summary()
    
    elif args.analyze:
        run_interactive_analysis(args.analyze)
    
    elif args.view_pending:
        view_pending_recommendations()
    
    elif args.approve_pending:
        approve_pending_recommendations()
    
    else:
        # Interactive menu
        print("\n" + "="*70)
        print("INTERACTIVE FEEDBACK TRAINER")
        print("="*70)
        print("\nOptions:")
        print("  1. List available campaigns")
        print("  2. Analyze a specific campaign (interactive)")
        print("  3. View pending recommendations")
        print("  4. Review & approve pending recommendations")
        print("  5. Exit")
        
        while True:
            choice = input("\nSelect option [1-5]: ").strip()
            
            if choice == '1':
                display_campaign_summary()
            
            elif choice == '2':
                campaigns = display_campaign_summary()
                if campaigns:
                    campaign_id = input("\nEnter campaign ID to analyze: ").strip()
                    if campaign_id:
                        run_interactive_analysis(campaign_id)
            
            elif choice == '3':
                view_pending_recommendations()
            
            elif choice == '4':
                approve_pending_recommendations()
            
            elif choice == '5':
                print("\n[OK] Exiting...")
                break
            
            else:
                print("\n[ERROR] Invalid choice. Please select 1-5.")


if __name__ == "__main__":
    main()
