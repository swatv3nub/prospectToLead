"""
Memory persistence layer using ChromaDB for storing campaign data, leads, and interactions.
"""
import chromadb
from chromadb.config import Settings
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import hashlib
from pathlib import Path


class WorkflowMemory:
    """Manages persistent memory for the workflow using ChromaDB."""
    
    def __init__(self, persist_directory: str = "./data/chroma"):
        """Initialize ChromaDB client with persistence."""
        # Create persist directory if it doesn't exist
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize collections
        self._init_collections()
    
    def _init_collections(self):
        """Initialize or get existing collections."""
        # Collection for leads (with deduplication)
        self.leads_collection = self.client.get_or_create_collection(
            name="leads",
            metadata={"description": "All discovered and contacted leads"}
        )
        
        # Collection for campaigns
        self.campaigns_collection = self.client.get_or_create_collection(
            name="campaigns",
            metadata={"description": "Campaign execution history and results"}
        )
        
        # Collection for interactions
        self.interactions_collection = self.client.get_or_create_collection(
            name="interactions",
            metadata={"description": "Email interactions and responses"}
        )
        
        # Collection for recommendations (from FeedbackTrainer)
        self.recommendations_collection = self.client.get_or_create_collection(
            name="recommendations",
            metadata={"description": "AI-generated workflow improvement recommendations"}
        )
    
    def _generate_lead_id(self, email: str) -> str:
        """Generate unique ID for a lead based on email."""
        return hashlib.md5(email.lower().encode()).hexdigest()
    
    def add_lead(self, lead: Dict[str, Any]) -> bool:
        """
        Add a lead to memory. Returns False if lead already exists (duplicate).
        """
        email = lead.get("email")
        if not email:
            return False
        
        lead_id = self._generate_lead_id(email)
        
        # Check if lead already exists
        try:
            existing = self.leads_collection.get(ids=[lead_id])
            if existing['ids']:
                # Lead already exists, update last_seen
                self.leads_collection.update(
                    ids=[lead_id],
                    metadatas=[{
                        **lead,
                        "last_seen": datetime.now().isoformat(),
                        "contact_count": existing['metadatas'][0].get('contact_count', 0) + 1
                    }]
                )
                return False  # Duplicate
        except Exception:
            pass
        
        # Add new lead
        self.leads_collection.add(
            ids=[lead_id],
            documents=[json.dumps(lead)],
            metadatas=[{
                **self._flatten_metadata(lead),
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "contact_count": 1
            }]
        )
        return True
    
    def is_lead_duplicate(self, email: str) -> bool:
        """Check if a lead has been contacted before."""
        lead_id = self._generate_lead_id(email)
        try:
            result = self.leads_collection.get(ids=[lead_id])
            return len(result['ids']) > 0
        except Exception:
            return False
    
    def get_lead_history(self, email: str) -> Optional[Dict[str, Any]]:
        """Get all historical data for a lead."""
        lead_id = self._generate_lead_id(email)
        try:
            result = self.leads_collection.get(ids=[lead_id])
            if result['ids']:
                return {
                    "metadata": result['metadatas'][0],
                    "data": json.loads(result['documents'][0])
                }
        except Exception:
            return None
    
    def add_campaign(self, campaign_id: str, campaign_data: Dict[str, Any]) -> None:
        """Store campaign execution data."""
        self.campaigns_collection.add(
            ids=[campaign_id],
            documents=[json.dumps(campaign_data)],
            metadatas=[{
                "campaign_id": campaign_id,
                "timestamp": datetime.now().isoformat(),
                "workflow_name": campaign_data.get("workflow_name", "unknown"),
                "total_leads": campaign_data.get("total_leads", 0),
                "emails_sent": campaign_data.get("emails_sent", 0),
                "open_rate": campaign_data.get("metrics", {}).get("open_rate", 0),
                "reply_rate": campaign_data.get("metrics", {}).get("reply_rate", 0)
            }]
        )
    
    def get_campaign_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent campaign history."""
        try:
            results = self.campaigns_collection.get(
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            campaigns = []
            for doc, meta in zip(results['documents'], results['metadatas']):
                campaigns.append({
                    "metadata": meta,
                    "data": json.loads(doc)
                })
            
            return campaigns
        except Exception:
            return []
    
    def add_interaction(self, lead_email: str, interaction_type: str, data: Dict[str, Any]) -> None:
        """
        Record an interaction with a lead (email sent, opened, clicked, replied).
        """
        interaction_id = f"{self._generate_lead_id(lead_email)}_{datetime.now().timestamp()}"
        
        self.interactions_collection.add(
            ids=[interaction_id],
            documents=[json.dumps(data)],
            metadatas=[{
                "lead_email": lead_email,
                "interaction_type": interaction_type,
                "timestamp": datetime.now().isoformat(),
                "campaign_id": data.get("campaign_id", "unknown")
            }]
        )
    
    def get_lead_interactions(self, lead_email: str) -> List[Dict[str, Any]]:
        """Get all interactions for a specific lead."""
        try:
            results = self.interactions_collection.get(
                where={"lead_email": lead_email},
                include=["documents", "metadatas"]
            )
            
            interactions = []
            for doc, meta in zip(results['documents'], results['metadatas']):
                interactions.append({
                    "metadata": meta,
                    "data": json.loads(doc)
                })
            
            return interactions
        except Exception:
            return []
    
    def add_recommendation(self, recommendation: Dict[str, Any]) -> None:
        """Store a recommendation from FeedbackTrainer."""
        rec_id = f"rec_{datetime.now().timestamp()}"
        
        self.recommendations_collection.add(
            ids=[rec_id],
            documents=[json.dumps(recommendation)],
            metadatas=[{
                "timestamp": datetime.now().isoformat(),
                "category": recommendation.get("category", "unknown"),
                "status": recommendation.get("approval_status", "pending"),
                "expected_improvement": recommendation.get("expected_improvement", "")
            }]
        )
    
    def get_pending_recommendations(self) -> List[Dict[str, Any]]:
        """Get all pending recommendations awaiting approval."""
        try:
            results = self.recommendations_collection.get(
                where={"status": "pending"},
                include=["documents", "metadatas"]
            )
            
            recommendations = []
            for doc, meta in zip(results['documents'], results['metadatas']):
                recommendations.append({
                    "metadata": meta,
                    "data": json.loads(doc)
                })
            
            return recommendations
        except Exception:
            return []
    
    def approve_recommendation(self, rec_id: str) -> None:
        """Mark a recommendation as approved."""
        try:
            self.recommendations_collection.update(
                ids=[rec_id],
                metadatas=[{"status": "approved"}]
            )
        except Exception as e:
            print(f"Error approving recommendation: {e}")
    
    def get_performance_trends(self, metric: str = "reply_rate", limit: int = 10) -> List[float]:
        """
        Get trend data for a specific metric across recent campaigns.
        """
        campaigns = self.get_campaign_history(limit=limit)
        trends = []
        
        for campaign in campaigns:
            value = campaign['metadata'].get(metric, 0)
            trends.append(value)
        
        return trends
    
    def search_similar_campaigns(self, current_config: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar past campaigns based on configuration similarity.
        This can help the FeedbackTrainer make better recommendations.
        """
        # Convert current config to searchable text
        config_text = json.dumps(current_config)
        
        try:
            results = self.campaigns_collection.query(
                query_texts=[config_text],
                n_results=limit,
                include=["documents", "metadatas", "distances"]
            )
            
            similar_campaigns = []
            for doc, meta, distance in zip(
                results['documents'][0], 
                results['metadatas'][0],
                results['distances'][0]
            ):
                similar_campaigns.append({
                    "metadata": meta,
                    "data": json.loads(doc),
                    "similarity_score": 1 - distance  # Convert distance to similarity
                })
            
            return similar_campaigns
        except Exception:
            return []
    
    def get_best_performing_configs(self, metric: str = "reply_rate", limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve the best-performing campaign configurations based on a metric.
        """
        campaigns = self.get_campaign_history(limit=50)  # Get more to find best
        
        # Sort by metric
        sorted_campaigns = sorted(
            campaigns,
            key=lambda x: x['metadata'].get(metric, 0),
            reverse=True
        )
        
        return sorted_campaigns[:limit]
    
    def _flatten_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Flatten nested dictionaries for ChromaDB metadata (which doesn't support nested dicts).
        """
        flattened = {}
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                # Store complex types as JSON strings
                flattened[key] = json.dumps(value)
            elif isinstance(value, (str, int, float, bool)):
                flattened[key] = value
            else:
                flattened[key] = str(value)
        return flattened
    
    def reset_all(self):
        """Reset all collections (use with caution!)."""
        self.client.reset()
        self._init_collections()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics from memory."""
        settings = self.client.get_settings()
        return {
            "total_leads": self.leads_collection.count(),
            "total_campaigns": self.campaigns_collection.count(),
            "total_interactions": self.interactions_collection.count(),
            "pending_recommendations": len(self.get_pending_recommendations()),
            "memory_location": str(settings.persist_directory) if hasattr(settings, 'persist_directory') else self.persist_dir
        }


# Singleton instance
_memory_instance = None

def get_memory(persist_directory: str = "./data/chroma") -> WorkflowMemory:
    """Get or create the singleton WorkflowMemory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = WorkflowMemory(persist_directory)
    return _memory_instance
