"""
FeedbackTrainerAgent: Analyzes campaign performance and suggests improvements.
"""
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from utils.tools import GoogleSheetsClient
from utils.memory import get_memory
from datetime import datetime
import json


class FeedbackTrainerAgent(BaseAgent):
    """Agent for analyzing performance and suggesting workflow improvements."""
    
    def _act(self, inputs: Dict[str, Any], reasoning: str) -> Dict[str, Any]:
        """Analyze campaign results and suggest improvements."""
        responses = inputs.get("responses", [])
        campaign_metrics = inputs.get("campaign_metrics", {})
        workflow_config = inputs.get("workflow_config", {})
        
        self.logger.info("Analyzing campaign performance and generating recommendations")
        
        # Get memory for historical analysis
        memory = get_memory()
        
        # Get performance trends from past campaigns
        historical_trends = {
            "open_rate_trend": memory.get_performance_trends("open_rate", limit=10),
            "reply_rate_trend": memory.get_performance_trends("reply_rate", limit=10),
            "click_rate_trend": memory.get_performance_trends("click_rate", limit=10)
        }
        
        # Get best performing configurations for comparison
        best_configs = memory.get_best_performing_configs("reply_rate", limit=3)
        
        # Analyze results
        analysis = self._analyze_performance(responses, campaign_metrics, historical_trends)
        
        # Generate recommendations using historical data
        recommendations = self._generate_recommendations(
            analysis, campaign_metrics, workflow_config, best_configs
        )
        
        # Store recommendations in memory
        for rec in recommendations:
            memory.add_recommendation(rec)
        
        # Generate summary
        analysis_summary = self._create_summary(campaign_metrics, recommendations, historical_trends)
        
        # Log to Google Sheets if configured
        self._log_to_sheets(campaign_metrics, recommendations, analysis)
        
        self.logger.info(f"Generated {len(recommendations)} recommendations")
        
        return {
            "recommendations": recommendations,
            "analysis_summary": analysis_summary,
            "performance_analysis": analysis,
            "historical_trends": historical_trends
        }
    
    def _analyze_performance(self, responses: List[Dict], metrics: Dict, 
                            historical_trends: Dict = None) -> Dict[str, Any]:
        """Analyze campaign performance in detail."""
        open_rate = metrics.get("open_rate", 0)
        click_rate = metrics.get("click_rate", 0)
        reply_rate = metrics.get("reply_rate", 0)
        
        # Analyze response patterns
        positive_replies = []
        negative_replies = []
        
        for response in responses:
            if response.get("replied") and response.get("reply_content"):
                content = response["reply_content"].lower()
                if any(word in content for word in ["interested", "schedule", "learn more", "yes"]):
                    positive_replies.append(response)
                elif any(word in content for word in ["not interested", "no", "unsubscribe"]):
                    negative_replies.append(response)
        
        analysis = {
            "open_rate_status": "good" if open_rate > 25 else "needs_improvement",
            "click_rate_status": "good" if click_rate > 5 else "needs_improvement",
            "reply_rate_status": "excellent" if reply_rate > 3 else "good" if reply_rate > 1 else "needs_improvement",
            "positive_responses": len(positive_replies),
            "negative_responses": len(negative_replies),
            "engagement_quality": "high" if reply_rate > 2 and click_rate > 5 else "medium",
            "areas_for_improvement": []
        }
        
        if open_rate < 25:
            analysis["areas_for_improvement"].append("subject_lines")
        if click_rate < 5:
            analysis["areas_for_improvement"].append("email_content")
        if reply_rate < 2:
            analysis["areas_for_improvement"].append("call_to_action")
        
        # Add historical comparison if available
        if historical_trends:
            avg_open_rate = sum(historical_trends.get("open_rate_trend", [0])) / max(len(historical_trends.get("open_rate_trend", [1])), 1)
            avg_reply_rate = sum(historical_trends.get("reply_rate_trend", [0])) / max(len(historical_trends.get("reply_rate_trend", [1])), 1)
            
            analysis["vs_historical"] = {
                "open_rate_vs_avg": open_rate - avg_open_rate,
                "reply_rate_vs_avg": reply_rate - avg_reply_rate,
                "improving": reply_rate > avg_reply_rate
            }
        
        return analysis
    
    def _generate_recommendations(
        self, 
        analysis: Dict, 
        metrics: Dict,
        workflow_config: Dict,
        best_configs: List[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations using historical data."""
        recommendations = []
        
        # Subject line recommendations
        if "subject_lines" in analysis["areas_for_improvement"]:
            recommendations.append({
                "category": "outreach_content",
                "parameter": "tone",
                "current_value": "friendly",
                "suggested_value": "curious",
                "reasoning": f"Open rate is {metrics['open_rate']}%, below industry average. Try a more curiosity-driven tone in subject lines.",
                "expected_improvement": "10-15% increase in open rate",
                "approval_status": "pending"
            })
        
        # Email content recommendations
        if "email_content" in analysis["areas_for_improvement"]:
            recommendations.append({
                "category": "outreach_content",
                "parameter": "email_length",
                "current_value": "150 words",
                "suggested_value": "100 words",
                "reasoning": f"Click rate is {metrics['click_rate']}%. Shorter, punchier emails tend to perform better.",
                "expected_improvement": "20% increase in click-through rate",
                "approval_status": "pending"
            })
        
        # CTA recommendations
        if "call_to_action" in analysis["areas_for_improvement"]:
            recommendations.append({
                "category": "outreach_content",
                "parameter": "call_to_action",
                "current_value": "schedule a call",
                "suggested_value": "quick 10-minute chat",
                "reasoning": f"Reply rate is {metrics['reply_rate']}%. Lower-friction CTAs typically get better response.",
                "expected_improvement": "30% increase in reply rate",
                "approval_status": "pending"
            })
        
        # ICP refinement based on engagement
        if analysis["engagement_quality"] == "high":
            recommendations.append({
                "category": "prospect_search",
                "parameter": "expand_icp",
                "current_value": "100-1000 employees",
                "suggested_value": "50-1500 employees",
                "reasoning": "High engagement suggests we can expand our ICP range while maintaining quality.",
                "expected_improvement": "50% more qualified leads",
                "approval_status": "pending"
            })
        
        # Scoring adjustments
        if metrics.get("reply_rate", 0) < 2:
            recommendations.append({
                "category": "scoring",
                "parameter": "min_score_threshold",
                "current_value": 60,
                "suggested_value": 70,
                "reasoning": "Low reply rate suggests we should focus on higher-quality leads only.",
                "expected_improvement": "Better response rates from more qualified prospects",
                "approval_status": "pending"
            })
        
        # Learn from best performing configs
        if best_configs:
            best_config = best_configs[0]
            best_reply_rate = best_config['metadata'].get('reply_rate', 0)
            
            if best_reply_rate > metrics.get('reply_rate', 0) * 1.5:
                recommendations.append({
                    "category": "historical_learning",
                    "parameter": "apply_best_config",
                    "current_value": "current_config",
                    "suggested_value": f"config_from_{best_config['metadata'].get('campaign_id')}",
                    "reasoning": f"Historical campaign achieved {best_reply_rate}% reply rate vs current {metrics.get('reply_rate', 0)}%",
                    "expected_improvement": f"Increase reply rate to ~{best_reply_rate}%",
                    "approval_status": "pending"
                })
        
        return recommendations
    
    def _create_summary(self, metrics: Dict, recommendations: List[Dict], 
                       historical_trends: Dict = None) -> str:
        """Create human-readable analysis summary."""
        summary = f"""
Campaign Performance Summary
===========================
📧 Total Sent: {metrics.get('total_sent', 0)}
📖 Open Rate: {metrics.get('open_rate', 0)}%
👆 Click Rate: {metrics.get('click_rate', 0)}%
💬 Reply Rate: {metrics.get('reply_rate', 0)}%
"""
        
        # Add historical comparison if available
        if historical_trends and historical_trends.get("reply_rate_trend"):
            avg_reply = sum(historical_trends["reply_rate_trend"]) / len(historical_trends["reply_rate_trend"])
            current_reply = metrics.get('reply_rate', 0)
            
            if current_reply > avg_reply:
                summary += f"\n📈 Improvement: {current_reply - avg_reply:.1f}% above historical average\n"
            else:
                summary += f"\n📉 Below average: {avg_reply - current_reply:.1f}% below historical average\n"
        
        summary += "\nAnalysis:\n"
        
        if metrics.get('open_rate', 0) > 25:
            summary += "✅ Open rate is above average - subject lines are working well\n"
        else:
            summary += "⚠️  Open rate needs improvement - consider testing new subject line approaches\n"
        
        if metrics.get('reply_rate', 0) > 2:
            summary += "✅ Reply rate is excellent - messaging resonates with prospects\n"
        else:
            summary += "⚠️  Reply rate could be better - consider refining value proposition\n"
        
        summary += f"\n📋 Generated {len(recommendations)} recommendations for improvement\n"
        summary += "\nRecommendations require human approval before implementation."
        
        return summary
    
    def _log_to_sheets(self, metrics: Dict, recommendations: List[Dict], analysis: Dict):
        """Log results to Google Sheets."""
        sheets_config = self._get_tool_config("GoogleSheets")
        
        if not sheets_config or not sheets_config.get("sheet_id"):
            self.logger.info("Google Sheets not configured, skipping logging")
            return
        
        try:
            client = GoogleSheetsClient(
                sheets_config.get("credentials_file", "credentials.json"),
                sheets_config["sheet_id"]
            )
            
            # Prepare rows for logging
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Log metrics
            metrics_row = [
                timestamp,
                metrics.get("total_sent", 0),
                metrics.get("open_rate", 0),
                metrics.get("click_rate", 0),
                metrics.get("reply_rate", 0)
            ]
            
            client.append_rows("Campaign Metrics", [metrics_row])
            
            # Log recommendations
            for rec in recommendations:
                rec_row = [
                    timestamp,
                    rec["category"],
                    rec["parameter"],
                    str(rec["current_value"]),
                    str(rec["suggested_value"]),
                    rec["reasoning"],
                    rec["approval_status"]
                ]
                client.append_rows("Recommendations", [rec_row])
            
            self.logger.info("Successfully logged to Google Sheets")
            
        except Exception as e:
            self.logger.warning(f"Failed to log to Google Sheets: {e}")
