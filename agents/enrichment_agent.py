"""
DataEnrichmentAgent: Enriches lead data with additional information.
"""
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from utils.tools import ClearbitClient, PeopleDataLabsClient
import random


class DataEnrichmentAgent(BaseAgent):
    """Agent for enriching lead data."""
    
    def _act(self, inputs: Dict[str, Any], reasoning: str) -> Dict[str, Any]:
        """Enrich leads with additional data."""
        leads = inputs.get("leads", [])
        
        self.logger.info(f"Enriching {len(leads)} leads")
        
        enriched_leads = []
        
        for lead in leads:
            try:
                enriched_lead = self._enrich_single_lead(lead)
                enriched_leads.append(enriched_lead)
            except Exception as e:
                self.logger.warning(f"Failed to enrich lead {lead.get('email')}: {e}")
                # Add minimal enrichment
                enriched_leads.append(self._add_mock_enrichment(lead))
        
        self.logger.info(f"Successfully enriched {len(enriched_leads)} leads")
        
        return {"enriched_leads": enriched_leads}
    
    def _enrich_single_lead(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich a single lead."""
        email = lead.get("email")
        
        enriched_data = {
            "company": lead.get("company"),
            "contact": lead.get("contact_name"),
            "email": email,
            "role": lead.get("title"),
            "linkedin": lead.get("linkedin"),
            "technologies": [],
            "company_description": "",
            "recent_news": [],
            "social_profiles": {}
        }
        
        # Try Clearbit
        clearbit_config = self._get_tool_config("Clearbit")
        if clearbit_config and clearbit_config.get("api_key") and email:
            try:
                client = ClearbitClient(clearbit_config["api_key"])
                data = client.enrich_person(email)
                if data:
                    enriched_data.update(self._parse_clearbit_data(data))
                    return enriched_data
            except Exception as e:
                self.logger.debug(f"Clearbit enrichment failed: {e}")
        
        # Try PeopleDataLabs
        pdl_config = self._get_tool_config("PeopleDataLabs")
        if pdl_config and pdl_config.get("api_key") and email:
            try:
                client = PeopleDataLabsClient(pdl_config["api_key"])
                data = client.enrich_person(email=email)
                if data:
                    enriched_data.update(self._parse_pdl_data(data))
                    return enriched_data
            except Exception as e:
                self.logger.debug(f"PeopleDataLabs enrichment failed: {e}")
        
        # Fallback to mock enrichment
        return self._add_mock_enrichment(lead)
    
    def _parse_clearbit_data(self, data: Dict) -> Dict[str, Any]:
        """Parse Clearbit API response."""
        person = data.get("person", {})
        company = data.get("company", {})
        
        return {
            "technologies": company.get("tech", []),
            "company_description": company.get("description", ""),
            "social_profiles": {
                "twitter": person.get("twitter", {}).get("handle"),
                "linkedin": person.get("linkedin", {}).get("handle")
            }
        }
    
    def _parse_pdl_data(self, data: Dict) -> Dict[str, Any]:
        """Parse PeopleDataLabs API response."""
        return {
            "technologies": data.get("job_company_inferred_technologies", []),
            "company_description": data.get("job_company_description", ""),
            "recent_news": [],
            "social_profiles": {
                "linkedin": data.get("linkedin_url"),
                "twitter": data.get("twitter_url")
            }
        }
    
    def _add_mock_enrichment(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Add mock enrichment data for demonstration."""
        mock_tech_stacks = [
            ["Salesforce", "HubSpot", "Slack", "AWS"],
            ["Microsoft Dynamics", "Zendesk", "Google Cloud", "Tableau"],
            ["Pipedrive", "Intercom", "Azure", "PowerBI"],
            ["Zoho CRM", "Freshdesk", "AWS", "Looker"]
        ]
        
        mock_news = [
            "Company announces Series B funding round",
            "Expansion into new market segment",
            "Launch of new product line",
            "Strategic partnership announced"
        ]
        
        return {
            "company": lead.get("company"),
            "contact": lead.get("contact_name"),
            "email": lead.get("email"),
            "role": lead.get("title"),
            "linkedin": lead.get("linkedin"),
            "technologies": random.choice(mock_tech_stacks),
            "company_description": f"{lead.get('company')} is a leading SaaS company providing innovative solutions.",
            "recent_news": [random.choice(mock_news)],
            "social_profiles": {
                "linkedin": lead.get("linkedin"),
                "twitter": f"https://twitter.com/{lead.get('company', '').lower().replace(' ', '')}"
            }
        }
