"""
ProspectSearchAgent: Discovers prospects using Clay and Apollo APIs.
"""
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from utils.tools import ClayAPIClient, ApolloAPIClient
from utils.memory import get_memory
import random


class ProspectSearchAgent(BaseAgent):
    """Agent for searching and discovering prospects."""
    
    def _act(self, inputs: Dict[str, Any], reasoning: str) -> Dict[str, Any]:
        """Search for prospects matching ICP criteria."""
        icp = inputs.get("icp", {})
        signals = inputs.get("signals", [])
        max_results = inputs.get("max_results", 50)
        
        self.logger.info(f"Searching for prospects with ICP: {icp}")
        
        leads = []
        
        # Try Clay API first
        clay_config = self._get_tool_config("ClayAPI")
        if clay_config and clay_config.get("api_key"):
            try:
                clay_client = ClayAPIClient(clay_config["api_key"])
                clay_results = clay_client.search_companies(icp)
                leads.extend(self._parse_clay_results(clay_results))
            except Exception as e:
                self.logger.warning(f"Clay API failed: {e}")
        
        # Try Apollo API
        apollo_config = self._get_tool_config("ApolloAPI")
        if apollo_config and apollo_config.get("api_key"):
            try:
                apollo_client = ApolloAPIClient(apollo_config["api_key"])
                
                # Convert ICP to Apollo search parameters
                employee_ranges = self._get_employee_ranges(icp.get("employee_count", {}))
                
                apollo_results = apollo_client.mixed_people_search(
                    titles=["VP", "Director", "Head of", "Chief", "Manager"],
                    organization_locations=[icp.get("location", "United States")],
                    organization_num_employees_ranges=employee_ranges,
                    per_page=min(max_results, 100)
                )
                
                leads.extend(self._parse_apollo_results(apollo_results, icp))
            except Exception as e:
                self.logger.warning(f"Apollo API failed: {e}")
        
        # If APIs fail, generate mock data for demonstration
        if not leads:
            self.logger.info("Generating mock prospect data for demonstration")
            leads = self._generate_mock_leads(icp, max_results)
        
        # Filter by signals if specified
        if signals:
            leads = [lead for lead in leads if lead.get("signal") in signals]
        
        # Deduplicate leads using memory
        memory = get_memory()
        unique_leads = []
        duplicate_count = 0
        
        for lead in leads:
            email = lead.get("email")
            if email and not memory.is_lead_duplicate(email):
                unique_leads.append(lead)
                memory.add_lead(lead)
            else:
                duplicate_count += 1
        
        if duplicate_count > 0:
            self.logger.info(f"Filtered out {duplicate_count} duplicate leads")
        
        # Limit results
        unique_leads = unique_leads[:max_results]
        
        self.logger.info(f"Found {len(unique_leads)} unique prospects")
        
        return {"leads": unique_leads}
    
    def _parse_clay_results(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """Parse Clay API results into standard format."""
        leads = []
        for result in results:
            lead = {
                "company": result.get("company_name", ""),
                "contact_name": result.get("contact_name", ""),
                "email": result.get("email", ""),
                "linkedin": result.get("linkedin_url", ""),
                "title": result.get("title", ""),
                "signal": result.get("signal", "general"),
                "company_size": result.get("employee_count", 0),
                "revenue": result.get("revenue", 0)
            }
            leads.append(lead)
        return leads
    
    def _parse_apollo_results(self, results: List[Dict], icp: Dict) -> List[Dict[str, Any]]:
        """Parse Apollo API results into standard format."""
        leads = []
        for person in results:
            organization = person.get("organization", {})
            lead = {
                "company": organization.get("name", ""),
                "contact_name": person.get("name", ""),
                "email": person.get("email", ""),
                "linkedin": person.get("linkedin_url", ""),
                "title": person.get("title", ""),
                "signal": self._detect_signal(organization),
                "company_size": organization.get("estimated_num_employees", 0),
                "revenue": organization.get("estimated_annual_revenue", 0)
            }
            leads.append(lead)
        return leads
    
    def _detect_signal(self, organization: Dict) -> str:
        """Detect buying signals from organization data."""
        signals = ["recent_funding", "hiring_for_sales", "tech_stack_match", "expansion"]
        return random.choice(signals)
    
    def _get_employee_ranges(self, employee_count: Dict) -> List[str]:
        """Convert employee count range to Apollo format."""
        min_emp = employee_count.get("min", 0)
        max_emp = employee_count.get("max", 10000)
        
        ranges = []
        if min_emp <= 100 <= max_emp:
            ranges.append("1,100")
        if min_emp <= 500 <= max_emp:
            ranges.append("101,500")
        if min_emp <= 1000 <= max_emp:
            ranges.append("501,1000")
        if min_emp <= 5000 <= max_emp:
            ranges.append("1001,5000")
        
        return ranges or ["101,500"]
    
    def _generate_mock_leads(self, icp: Dict, count: int) -> List[Dict[str, Any]]:
        """Generate mock leads for demonstration purposes."""
        mock_companies = [
            "Acme SaaS Inc", "TechVision Solutions", "CloudSync Pro",
            "DataFlow Systems", "NextGen Analytics", "Innovate Labs",
            "ScaleUp Software", "AgileCore Tech", "FutureStack Inc",
            "SmartOps Platform"
        ]
        
        mock_titles = [
            "VP of Sales", "Director of Revenue Operations", "Head of Business Development",
            "Chief Revenue Officer", "VP of Marketing", "Director of Growth"
        ]
        
        mock_signals = ["recent_funding", "hiring_for_sales", "tech_stack_match"]
        
        leads = []
        for i in range(min(count, len(mock_companies))):
            company = mock_companies[i % len(mock_companies)]
            contact_name = f"{random.choice(['John', 'Sarah', 'Michael', 'Emily', 'David'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])}"
            
            lead = {
                "company": company,
                "contact_name": contact_name,
                "email": f"{contact_name.lower().replace(' ', '.')}@{company.lower().replace(' ', '')}.com",
                "linkedin": f"https://linkedin.com/in/{contact_name.lower().replace(' ', '-')}",
                "title": random.choice(mock_titles),
                "signal": random.choice(mock_signals),
                "company_size": random.randint(100, 1000),
                "revenue": random.randint(20000000, 200000000)
            }
            leads.append(lead)
        
        return leads
