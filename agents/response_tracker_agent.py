"""
ResponseTrackerAgent: Monitors email engagement and responses.
"""
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
import random
from datetime import datetime, timedelta


class ResponseTrackerAgent(BaseAgent):
    """Agent for tracking email responses and engagement."""
    
    def _act(self, inputs: Dict[str, Any], reasoning: str) -> Dict[str, Any]:
        """Track email responses and engagement."""
        campaign_id = inputs.get("campaign_id")
        tracking_duration = inputs.get("tracking_duration_hours", 72)
        
        self.logger.info(f"Tracking responses for campaign {campaign_id}")
        
        # In a real implementation, this would poll Apollo API or email service
        # For demonstration, we'll simulate tracking data
        
        # Get sent emails from previous step
        # In practice, we'd query the email service API
        responses = self._simulate_tracking_data(campaign_id)
        
        # Calculate metrics
        campaign_metrics = self._calculate_metrics(responses)
        
        self.logger.info(f"Campaign metrics: {campaign_metrics}")
        
        return {
            "responses": responses,
            "campaign_metrics": campaign_metrics
        }
    
    def _simulate_tracking_data(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Simulate email tracking data for demonstration."""
        # In production, this would call Apollo API or email service webhooks
        
        mock_emails = [
            "john.smith@acmesaas.com",
            "sarah.johnson@techvision.com",
            "michael.williams@cloudsync.com",
            "emily.brown@dataflow.com",
            "david.jones@nextgen.com"
        ]
        
        responses = []
        
        for email in mock_emails:
            # Simulate realistic engagement rates
            opened = random.random() < 0.35  # 35% open rate
            clicked = opened and random.random() < 0.15  # 15% of opens click
            replied = opened and random.random() < 0.05  # 5% reply rate
            
            engagement_score = 0
            if opened:
                engagement_score += 30
            if clicked:
                engagement_score += 40
            if replied:
                engagement_score += 30
            
            reply_content = ""
            if replied:
                replies = [
                    "This looks interesting. Can we schedule a call?",
                    "Thanks for reaching out. I'd like to learn more.",
                    "Could you send me more information about your solution?",
                    "Let's chat next week. What's your availability?",
                    "Not interested at this time, but keep me posted."
                ]
                reply_content = random.choice(replies)
            
            responses.append({
                "lead_email": email,
                "opened": opened,
                "clicked": clicked,
                "replied": replied,
                "reply_content": reply_content,
                "engagement_score": engagement_score,
                "last_activity": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat()
            })
        
        return responses
    
    def _calculate_metrics(self, responses: List[Dict]) -> Dict[str, Any]:
        """Calculate campaign performance metrics."""
        total = len(responses)
        
        if total == 0:
            return {
                "total_sent": 0,
                "open_rate": 0,
                "click_rate": 0,
                "reply_rate": 0
            }
        
        opens = sum(1 for r in responses if r["opened"])
        clicks = sum(1 for r in responses if r["clicked"])
        replies = sum(1 for r in responses if r["replied"])
        
        return {
            "total_sent": total,
            "open_rate": round((opens / total) * 100, 2),
            "click_rate": round((clicks / total) * 100, 2),
            "reply_rate": round((replies / total) * 100, 2),
            "total_opens": opens,
            "total_clicks": clicks,
            "total_replies": replies
        }
