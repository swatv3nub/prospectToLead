"""
ScoringAgent: Scores and ranks leads based on ICP fit.
"""
from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class ScoringAgent(BaseAgent):
    """Agent for scoring and ranking leads."""
    
    def _act(self, inputs: Dict[str, Any], reasoning: str) -> Dict[str, Any]:
        """Score leads based on criteria."""
        enriched_leads = inputs.get("enriched_leads", [])
        scoring_criteria = inputs.get("scoring_criteria", {})
        
        self.logger.info(f"Scoring {len(enriched_leads)} leads")
        
        # Extract weights
        company_size_weight = scoring_criteria.get("company_size_weight", 0.2)
        revenue_weight = scoring_criteria.get("revenue_weight", 0.3)
        tech_match_weight = scoring_criteria.get("technology_match_weight", 0.25)
        signal_weight = scoring_criteria.get("signal_strength_weight", 0.25)
        min_threshold = scoring_criteria.get("min_score_threshold", 60)
        
        ranked_leads = []
        
        for lead in enriched_leads:
            score_breakdown = self._calculate_score(
                lead,
                company_size_weight,
                revenue_weight,
                tech_match_weight,
                signal_weight
            )
            
            total_score = score_breakdown["total"]
            
            if total_score >= min_threshold:
                ranked_leads.append({
                    "lead": lead,
                    "score": total_score,
                    "score_breakdown": score_breakdown,
                    "reasoning": self._generate_reasoning(lead, score_breakdown)
                })
        
        # Sort by score descending
        ranked_leads.sort(key=lambda x: x["score"], reverse=True)
        
        self.logger.info(f"Ranked {len(ranked_leads)} leads above threshold {min_threshold}")
        
        return {"ranked_leads": ranked_leads}
    
    def _calculate_score(self, lead: Dict, size_w: float, rev_w: float, tech_w: float, sig_w: float) -> Dict[str, Any]:
        """Calculate detailed score for a lead."""
        # Company size score (0-100)
        company_size = lead.get("company_size", 0)
        size_score = self._score_company_size(company_size)
        
        # Revenue score (0-100)
        revenue = lead.get("revenue", 0)
        revenue_score = self._score_revenue(revenue)
        
        # Technology match score (0-100)
        technologies = lead.get("technologies", [])
        tech_score = self._score_technology_match(technologies)
        
        # Signal strength score (0-100)
        signal = lead.get("signal", "general")
        signal_score = self._score_signal(signal)
        
        # Weighted total
        total = (
            size_score * size_w +
            revenue_score * rev_w +
            tech_score * tech_w +
            signal_score * sig_w
        ) * 100
        
        return {
            "company_size_score": round(size_score * 100, 2),
            "revenue_score": round(revenue_score * 100, 2),
            "technology_score": round(tech_score * 100, 2),
            "signal_score": round(signal_score * 100, 2),
            "total": round(total, 2)
        }
    
    def _score_company_size(self, size: int) -> float:
        """Score based on company size (100-1000 is ideal)."""
        if 100 <= size <= 1000:
            return 1.0
        elif 50 <= size < 100 or 1000 < size <= 2000:
            return 0.7
        elif size > 2000:
            return 0.5
        else:
            return 0.3
    
    def _score_revenue(self, revenue: int) -> float:
        """Score based on revenue ($20M-$200M is ideal)."""
        if 20_000_000 <= revenue <= 200_000_000:
            return 1.0
        elif 10_000_000 <= revenue < 20_000_000:
            return 0.7
        elif revenue > 200_000_000:
            return 0.6
        else:
            return 0.3
    
    def _score_technology_match(self, technologies: List[str]) -> float:
        """Score based on technology stack alignment."""
        target_tech = {"salesforce", "hubspot", "aws", "google cloud", "azure", "slack", "tableau"}
        
        if not technologies:
            return 0.5
        
        tech_lower = {t.lower() for t in technologies}
        matches = len(tech_lower & target_tech)
        
        if matches >= 3:
            return 1.0
        elif matches == 2:
            return 0.8
        elif matches == 1:
            return 0.6
        else:
            return 0.4
    
    def _score_signal(self, signal: str) -> float:
        """Score based on buying signal strength."""
        signal_scores = {
            "recent_funding": 1.0,
            "hiring_for_sales": 0.9,
            "tech_stack_match": 0.8,
            "expansion": 0.85,
            "general": 0.5
        }
        return signal_scores.get(signal, 0.5)
    
    def _generate_reasoning(self, lead: Dict, score_breakdown: Dict) -> str:
        """Generate human-readable reasoning for the score."""
        reasons = []
        
        company = lead.get("company", "Company")
        
        if score_breakdown["company_size_score"] >= 80:
            reasons.append(f"{company} has an ideal company size")
        
        if score_breakdown["revenue_score"] >= 80:
            reasons.append("revenue fits our ICP perfectly")
        
        if score_breakdown["technology_score"] >= 80:
            reasons.append("strong technology stack alignment")
        
        if score_breakdown["signal_score"] >= 80:
            reasons.append("showing strong buying signals")
        
        if not reasons:
            return f"{company} meets basic qualification criteria"
        
        return f"{company}: " + ", ".join(reasons)
