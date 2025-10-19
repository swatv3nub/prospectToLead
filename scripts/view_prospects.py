"""
View all prospects/leads stored in memory.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.memory import get_memory
import json

def view_all_prospects():
    """Display all prospects stored in memory."""
    memory = get_memory()
    
    # Get all leads
    try:
        results = memory.leads_collection.get()
        
        if not results['documents']:
            print("\nNo prospects found in memory.")
            return
        
        print("\n" + "="*80)
        print(f"PROSPECTS FOUND: {len(results['documents'])} total")
        print("="*80)
        
        for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas']), 1):
            lead_data = json.loads(doc)
            
            print(f"\n{i}. {metadata.get('name', 'N/A')}")
            print(f"   Email: {metadata.get('email', 'N/A')}")
            print(f"   Company: {metadata.get('company', 'N/A')}")
            print(f"   Title: {metadata.get('title', 'N/A')}")
            print(f"   LinkedIn: {lead_data.get('linkedin', 'N/A')}")
            print(f"   Phone: {lead_data.get('phone', 'N/A')}")
            print(f"   Location: {lead_data.get('location', 'N/A')}")
            print(f"   Company Size: {lead_data.get('company_size', 'N/A')}")
            print(f"   Industry: {lead_data.get('industry', 'N/A')}")
            print(f"   Revenue: ${lead_data.get('revenue', 'N/A'):,}" if lead_data.get('revenue') else "   Revenue: N/A")
            print(f"   Signal: {lead_data.get('signal', 'N/A')}")
            print(f"   First Contacted: {metadata.get('first_contacted', 'N/A')}")
            print(f"   Contact Count: {metadata.get('contact_count', 0)}")
            print("-" * 80)
    
    except Exception as e:
        print(f"\nError retrieving prospects: {e}")

def export_prospects_to_json(filename="prospects.json"):
    """Export all prospects to a JSON file."""
    memory = get_memory()
    
    try:
        results = memory.leads_collection.get()
        
        if not results['documents']:
            print("\nNo prospects found to export.")
            return
        
        prospects = []
        for doc, metadata in zip(results['documents'], results['metadatas']):
            lead_data = json.loads(doc)
            prospect = {
                **lead_data,
                "first_contacted": metadata.get('first_contacted'),
                "contact_count": metadata.get('contact_count', 0)
            }
            prospects.append(prospect)
        
        # Create prospects/json directory
        output_dir = os.path.join("prospects", "json")
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to prospects/json/ folder
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(prospects, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Exported {len(prospects)} prospects to {output_path}")
        print(f"Full path: {os.path.abspath(output_path)}")
    
    except Exception as e:
        print(f"\nError exporting prospects: {e}")

def export_prospects_to_csv(filename="prospects.csv"):
    """Export all prospects to a CSV file."""
    memory = get_memory()
    
    try:
        results = memory.leads_collection.get()
        
        if not results['documents']:
            print("\nNo prospects found to export.")
            return
        
        import csv
        
        prospects = []
        for doc, metadata in zip(results['documents'], results['metadatas']):
            lead_data = json.loads(doc)
            prospect = {
                "name": metadata.get('name', ''),
                "email": metadata.get('email', ''),
                "company": metadata.get('company', ''),
                "title": metadata.get('title', ''),
                "linkedin": lead_data.get('linkedin', ''),
                "phone": lead_data.get('phone', ''),
                "location": lead_data.get('location', ''),
                "company_size": lead_data.get('company_size', ''),
                "industry": lead_data.get('industry', ''),
                "revenue": lead_data.get('revenue', ''),
                "signal": lead_data.get('signal', ''),
                "first_contacted": metadata.get('first_contacted', ''),
                "contact_count": metadata.get('contact_count', 0)
            }
            prospects.append(prospect)
        
        if prospects:
            # Create prospects/csv directory
            output_dir = os.path.join("prospects", "csv")
            os.makedirs(output_dir, exist_ok=True)
            
            # Save to prospects/csv/ folder
            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=prospects[0].keys())
                writer.writeheader()
                writer.writerows(prospects)
            
            print(f"\n✓ Exported {len(prospects)} prospects to {output_path}")
            print(f"Full path: {os.path.abspath(output_path)}")
    
    except Exception as e:
        print(f"\nError exporting prospects: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="View and export prospects from memory")
    parser.add_argument("--view", action="store_true", help="View all prospects in console")
    parser.add_argument("--json", metavar="FILE", help="Export prospects to JSON file")
    parser.add_argument("--csv", metavar="FILE", help="Export prospects to CSV file")
    
    args = parser.parse_args()
    
    if not any([args.view, args.json, args.csv]):
        # Default: view prospects
        view_all_prospects()
    else:
        if args.view:
            view_all_prospects()
        if args.json:
            export_prospects_to_json(args.json)
        if args.csv:
            export_prospects_to_csv(args.csv)
