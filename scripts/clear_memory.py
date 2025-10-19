"""
Clear prospects and other data from ChromaDB memory.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.memory import get_memory
import argparse


def confirm_action(message: str) -> bool:
    """Ask for user confirmation."""
    response = input(f"{message} (yes/no): ").strip().lower()
    return response in ['yes', 'y']


def clear_leads():
    """Clear all prospects/leads from memory."""
    memory = get_memory()
    count = memory.leads_collection.count()
    
    if count == 0:
        print("\nNo leads found in memory.")
        return
    
    print(f"\nFound {count} leads in memory.")
    if confirm_action("Are you sure you want to delete all leads?"):
        deleted = memory.clear_leads()
        print(f"\n[OK] Deleted {deleted} leads from memory.")
    else:
        print("\n[CANCELLED] No leads were deleted.")


def clear_campaigns():
    """Clear all campaigns from memory."""
    memory = get_memory()
    count = memory.campaigns_collection.count()
    
    if count == 0:
        print("\nNo campaigns found in memory.")
        return
    
    print(f"\nFound {count} campaigns in memory.")
    if confirm_action("Are you sure you want to delete all campaigns?"):
        deleted = memory.clear_campaigns()
        print(f"\n[OK] Deleted {deleted} campaigns from memory.")
    else:
        print("\n[CANCELLED] No campaigns were deleted.")


def clear_interactions():
    """Clear all interactions from memory."""
    memory = get_memory()
    count = memory.interactions_collection.count()
    
    if count == 0:
        print("\nNo interactions found in memory.")
        return
    
    print(f"\nFound {count} interactions in memory.")
    if confirm_action("Are you sure you want to delete all interactions?"):
        deleted = memory.clear_interactions()
        print(f"\n[OK] Deleted {deleted} interactions from memory.")
    else:
        print("\n[CANCELLED] No interactions were deleted.")


def clear_recommendations():
    """Clear all recommendations from memory."""
    memory = get_memory()
    count = memory.recommendations_collection.count()
    
    if count == 0:
        print("\nNo recommendations found in memory.")
        return
    
    print(f"\nFound {count} recommendations in memory.")
    if confirm_action("Are you sure you want to delete all recommendations?"):
        deleted = memory.clear_recommendations()
        print(f"\n[OK] Deleted {deleted} recommendations from memory.")
    else:
        print("\n[CANCELLED] No recommendations were deleted.")


def clear_all():
    """Clear all data from memory."""
    memory = get_memory()
    stats = memory.get_statistics()
    
    total = stats['total_leads'] + stats['total_campaigns'] + stats['total_interactions'] + stats['pending_recommendations']
    
    if total == 0:
        print("\nMemory is already empty.")
        return
    
    print("\nCurrent memory statistics:")
    print(f"  - Leads: {stats['total_leads']}")
    print(f"  - Campaigns: {stats['total_campaigns']}")
    print(f"  - Interactions: {stats['total_interactions']}")
    print(f"  - Recommendations: {stats['pending_recommendations']}")
    print(f"  - Total items: {total}")
    
    if confirm_action("\nAre you sure you want to delete ALL data from memory?"):
        results = memory.clear_all_data()
        print("\n[OK] Memory cleared successfully:")
        print(f"  - Leads deleted: {results['leads_deleted']}")
        print(f"  - Campaigns deleted: {results['campaigns_deleted']}")
        print(f"  - Interactions deleted: {results['interactions_deleted']}")
        print(f"  - Recommendations deleted: {results['recommendations_deleted']}")
    else:
        print("\n[CANCELLED] No data was deleted.")


def show_stats():
    """Show current memory statistics."""
    memory = get_memory()
    stats = memory.get_statistics()
    
    print("\n" + "="*60)
    print("MEMORY STATISTICS")
    print("="*60)
    print(f"Leads: {stats['total_leads']}")
    print(f"Campaigns: {stats['total_campaigns']}")
    print(f"Interactions: {stats['total_interactions']}")
    print(f"Pending Recommendations: {stats['pending_recommendations']}")
    print(f"Storage Location: {stats['memory_location']}")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Clear prospects and other data from ChromaDB memory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show current statistics
  python scripts/clear_memory.py --stats
  
  # Clear only leads/prospects
  python scripts/clear_memory.py --leads
  
  # Clear only campaigns
  python scripts/clear_memory.py --campaigns
  
  # Clear all data (with confirmation)
  python scripts/clear_memory.py --all
  
  # Force clear without confirmation (use with caution!)
  python scripts/clear_memory.py --all --force
        """
    )
    
    parser.add_argument("--leads", action="store_true", help="Clear all leads/prospects")
    parser.add_argument("--campaigns", action="store_true", help="Clear all campaigns")
    parser.add_argument("--interactions", action="store_true", help="Clear all interactions")
    parser.add_argument("--recommendations", action="store_true", help="Clear all recommendations")
    parser.add_argument("--all", action="store_true", help="Clear all data from memory")
    parser.add_argument("--stats", action="store_true", help="Show memory statistics")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompts")
    
    args = parser.parse_args()
    
    # If force flag is set, override confirm_action globally
    if args.force:
        global confirm_action
        confirm_action = lambda msg: True
    
    # If no arguments provided, show help
    if not any([args.leads, args.campaigns, args.interactions, args.recommendations, args.all, args.stats]):
        parser.print_help()
        return
    
    # Show stats if requested
    if args.stats:
        show_stats()
    
    # Clear specific collections
    if args.leads:
        clear_leads()
    
    if args.campaigns:
        clear_campaigns()
    
    if args.interactions:
        clear_interactions()
    
    if args.recommendations:
        clear_recommendations()
    
    if args.all:
        clear_all()
    
    # Show final stats if anything was cleared
    if any([args.leads, args.campaigns, args.interactions, args.recommendations, args.all]):
        print("\nFinal memory statistics:")
        show_stats()


if __name__ == "__main__":
    main()
