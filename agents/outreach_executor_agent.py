"""
OutreachExecutorAgent: Sends emails and tracks delivery.
"""
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from utils.tools import SendGridClient, ApolloAPIClient
from utils.memory import get_memory
import time
import uuid
from datetime import datetime


class OutreachExecutorAgent(BaseAgent):
    """Agent for executing outreach campaigns."""
    
    def _act(self, inputs: Dict[str, Any], reasoning: str) -> Dict[str, Any]:
        """Send outreach emails."""
        messages = inputs.get("messages", [])
        send_delay = inputs.get("send_delay_seconds", 60)
        dry_run = inputs.get("dry_run", False)
        
        self.logger.info(f"Executing outreach for {len(messages)} leads (dry_run={dry_run})")
        
        campaign_id = f"campaign_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d')}"
        sent_status = []
        
        # Try SendGrid first
        sendgrid_config = self._get_tool_config("SendGrid")
        use_sendgrid = sendgrid_config and sendgrid_config.get("api_key")
        
        if use_sendgrid and not dry_run:
            client = SendGridClient(
                sendgrid_config["api_key"],
                sendgrid_config["from_email"]
            )
        else:
            client = None
        
        for i, message in enumerate(messages):
            lead = message["lead"]
            to_email = lead.get("email")
            subject = message["subject_line"]
            body = message["email_body"]
            
            if dry_run:
                # Simulate sending
                status = {
                    "lead_email": to_email,
                    "status": "dry_run_success",
                    "message_id": f"mock_{uuid.uuid4().hex[:8]}",
                    "sent_at": datetime.now().isoformat()
                }
                self.logger.info(f"[DRY RUN] Would send to {to_email}: {subject}")
            else:
                try:
                    if client:
                        result = client.send_email(to_email, subject, body)
                        status = {
                            "lead_email": to_email,
                            "status": result.get("status", "unknown"),
                            "message_id": result.get("message_id", ""),
                            "sent_at": datetime.now().isoformat()
                        }
                    else:
                        # Mock send
                        status = {
                            "lead_email": to_email,
                            "status": "mock_sent",
                            "message_id": f"mock_{uuid.uuid4().hex[:8]}",
                            "sent_at": datetime.now().isoformat()
                        }
                    
                    self.logger.info(f"Sent email to {to_email}")
                    
                    # Log interaction to memory
                    memory = get_memory()
                    memory.add_interaction(
                        lead_email=to_email,
                        interaction_type="email_sent",
                        data={
                            "campaign_id": campaign_id,
                            "subject": subject,
                            "message_id": status.get("message_id"),
                            "sent_at": status.get("sent_at")
                        }
                    )
                    
                    # Rate limiting
                    if i < len(messages) - 1:
                        time.sleep(send_delay)
                        
                except Exception as e:
                    self.logger.error(f"Failed to send to {to_email}: {e}")
                    status = {
                        "lead_email": to_email,
                        "status": "failed",
                        "message_id": "",
                        "sent_at": datetime.now().isoformat(),
                        "error": str(e)
                    }
            
            sent_status.append(status)
        
        success_count = sum(1 for s in sent_status if s["status"] in ["sent", "dry_run_success", "mock_sent"])
        self.logger.info(f"Campaign {campaign_id}: {success_count}/{len(messages)} emails sent successfully")
        
        return {
            "sent_status": sent_status,
            "campaign_id": campaign_id
        }
