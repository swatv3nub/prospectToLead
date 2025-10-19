"""
Script to view and manage ChromaDB memory statistics.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.memory import get_memory
import json


def display_statistics():
    """Display overall memory statistics."""
    memory = get_memory()
    stats = memory.get_statistics()
    
    print("\n" + "=" * 60)
    print("WORKFLOW MEMORY STATISTICS")
    print("=" * 60)
    
    print(f"\n📊 Overview:")
    print(f"  • Total Leads: {stats['total_leads']}")
    print(f"  • Total Campaigns: {stats['total_campaigns']}")
    print(f"  • Total Interactions: {stats['total_interactions']}")
    print(f"  • Pending Recommendations: {stats['pending_recommendations']}")
    print(f"  • Storage Location: {stats['memory_location']}")


def display_recent_campaigns():
    """Display recent campaign history."""
    memory = get_memory()
    campaigns = memory.get_campaign_history(limit=5)
    
    print("\n" + "=" * 60)
    print("RECENT CAMPAIGNS")
    print("=" * 60)
    
    if not campaigns:
        print("\n  No campaigns found in memory.")
        return
    
    for i, campaign in enumerate(campaigns, 1):
        meta = campaign['metadata']
        print(f"\n{i}. Campaign: {meta.get('campaign_id', 'Unknown')}")
        print(f"   Date: {meta.get('timestamp', 'Unknown')}")
        print(f"   Leads: {meta.get('total_leads', 0)}")
        print(f"   Sent: {meta.get('emails_sent', 0)}")
        print(f"   Metrics: Open:{meta.get('open_rate', 0)}% Reply:{meta.get('reply_rate', 0)}%")


def display_performance_trends():
    """Display performance trends over time."""
    memory = get_memory()
    
    print("\n" + "=" * 60)
    print("PERFORMANCE TRENDS (Last 10 Campaigns)")
    print("=" * 60)
    
    open_rates = memory.get_performance_trends("open_rate", limit=10)
    reply_rates = memory.get_performance_trends("reply_rate", limit=10)
    click_rates = memory.get_performance_trends("click_rate", limit=10)
    
    if open_rates:
        print(f"\n📖 Open Rate Trend: {' → '.join([f'{x:.1f}%' for x in open_rates])}")
        print(f"   Average: {sum(open_rates)/len(open_rates):.1f}%")
    
    if reply_rates:
        print(f"\n💬 Reply Rate Trend: {' → '.join([f'{x:.1f}%' for x in reply_rates])}")
        print(f"   Average: {sum(reply_rates)/len(reply_rates):.1f}%")
    
    if click_rates:
        print(f"\n👆 Click Rate Trend: {' → '.join([f'{x:.1f}%' for x in click_rates])}")
        print(f"   Average: {sum(click_rates)/len(click_rates):.1f}%")


def display_pending_recommendations():
    """Display pending recommendations."""
    memory = get_memory()
    recommendations = memory.get_pending_recommendations()
    
    print("\n" + "=" * 60)
    print("PENDING RECOMMENDATIONS")
    print("=" * 60)
    
    if not recommendations:
        print("\n  No pending recommendations.")
        return
    
    for i, rec in enumerate(recommendations, 1):
        data = rec['data']
        print(f"\n{i}. {data.get('category', 'Unknown')}: {data.get('parameter', 'Unknown')}")
        print(f"   Current: {data.get('current_value')}")
        print(f"   Suggested: {data.get('suggested_value')}")
        print(f"   Reason: {data.get('reasoning')}")
        print(f"   Expected: {data.get('expected_improvement')}")
        print(f"   Status: {data.get('approval_status')}")


def check_lead(email: str):
    """Check if a lead exists in memory."""
    memory = get_memory()
    
    is_duplicate = memory.is_lead_duplicate(email)
    history = memory.get_lead_history(email)
    
    print(f"\n{'=' * 60}")
    print(f"LEAD: {email}")
    print(f"{'=' * 60}")
    
    if is_duplicate and history:
        print(f"\n✅ Lead found in memory")
        print(f"   First Seen: {history['metadata'].get('first_seen')}")
        print(f"   Last Seen: {history['metadata'].get('last_seen')}")
        print(f"   Contact Count: {history['metadata'].get('contact_count')}")
        
        # Get interactions
        interactions = memory.get_lead_interactions(email)
        if interactions:
            print(f"\n   Interactions ({len(interactions)}):")
            for interaction in interactions[:5]:  # Show last 5
                meta = interaction['metadata']
                print(f"     • {meta['interaction_type']} - {meta['timestamp']}")
    else:
        print(f"\n❌ Lead not found in memory")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="View and manage workflow memory")
    parser.add_argument("--stats", action="store_true", help="Show overall statistics")
    parser.add_argument("--campaigns", action="store_true", help="Show recent campaigns")
    parser.add_argument("--trends", action="store_true", help="Show performance trends")
    parser.add_argument("--recommendations", action="store_true", help="Show pending recommendations")
    parser.add_argument("--check-lead", type=str, help="Check if a lead exists")
    parser.add_argument("--all", action="store_true", help="Show all information")
    
    args = parser.parse_args()
    
    # If no arguments, show all
    if not any(vars(args).values()) or args.all:
        display_statistics()
        display_recent_campaigns()
        display_performance_trends()
        display_pending_recommendations()
    else:
        if args.stats:
            display_statistics()
        if args.campaigns:
            display_recent_campaigns()
        if args.trends:
            display_performance_trends()
        if args.recommendations:
            display_pending_recommendations()
        if args.check_lead:
            check_lead(args.check_lead)
    
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
