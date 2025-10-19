"""
OutreachContentAgent: Generates personalized outreach messages.
"""
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json


class OutreachContentAgent(BaseAgent):
    """Agent for generating personalized outreach content."""
    
    def _act(self, inputs: Dict[str, Any], reasoning: str) -> Dict[str, Any]:
        """Generate personalized outreach messages."""
        ranked_leads = inputs.get("ranked_leads", [])
        persona = inputs.get("persona", "SDR")
        tone = inputs.get("tone", "friendly")
        value_prop = inputs.get("value_proposition", "AI-powered analytics")
        max_leads = inputs.get("max_leads_to_contact", 20)
        
        # Take top N leads
        leads_to_contact = ranked_leads[:max_leads]
        
        self.logger.info(f"Generating outreach for {len(leads_to_contact)} leads")
        
        messages = []
        
        # Get OpenAI config
        openai_config = self._get_tool_config("OpenAI")
        if not openai_config or not openai_config.get("api_key"):
            self.logger.warning("OpenAI API key not found, using mock messages")
            return {"messages": self._generate_mock_messages(leads_to_contact, value_prop)}
        
        # Initialize LLM
        llm = ChatOpenAI(
            api_key=openai_config["api_key"],
            model=openai_config.get("model", "gpt-4o-mini"),
            temperature=0.7
        )
        
        for ranked_lead in leads_to_contact:
            lead = ranked_lead["lead"]
            try:
                message = self._generate_personalized_message(
                    lead, ranked_lead, persona, tone, value_prop, llm
                )
                messages.append(message)
            except Exception as e:
                self.logger.warning(f"Failed to generate message for {lead.get('email')}: {e}")
        
        self.logger.info(f"Generated {len(messages)} personalized messages")
        
        return {"messages": messages}
    
    def _generate_personalized_message(
        self,
        lead: Dict,
        ranked_lead: Dict,
        persona: str,
        tone: str,
        value_prop: str,
        llm: ChatOpenAI
    ) -> Dict[str, Any]:
        """Generate a single personalized message using LLM."""
        
        # Prepare context
        context = {
            "company": lead.get("company"),
            "contact_name": lead.get("contact").split()[0] if lead.get("contact") else "there",
            "role": lead.get("role"),
            "technologies": lead.get("technologies", []),
            "recent_news": lead.get("recent_news", []),
            "score": ranked_lead.get("score"),
            "reasoning": ranked_lead.get("reasoning")
        }
        
        # Create prompt for subject line
        subject_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are an expert {persona} crafting email subject lines.
            Create a compelling, personalized subject line that:
            - Is under 50 characters
            - Mentions something specific about their company
            - Creates curiosity
            - Sounds {tone} and professional
            
            Do not use generic phrases like "Quick question" or "Following up"."""),
            ("human", f"""Lead context:
            Company: {context['company']}
            Role: {context['role']}
            Technologies: {', '.join(context['technologies'][:3])}
            Recent: {context['recent_news'][0] if context['recent_news'] else 'N/A'}
            
            Generate a subject line:""")
        ])
        
        subject_response = llm.invoke(subject_prompt.format_messages())
        subject_line = subject_response.content.strip().replace('"', '')
        
        # Create prompt for email body
        body_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are an expert {persona} crafting personalized cold emails.
            
            Value Proposition: {value_prop}
            
            Write a brief email (under 150 words) that:
            - Addresses them by first name
            - References something specific about their company or role
            - Explains how we can help (value prop)
            - Has a clear, low-friction call-to-action
            - Sounds {tone} and conversational
            - Does NOT use pushy sales language
            
            Format: Plain text, no HTML."""),
            ("human", f"""Lead context:
            Name: {context['contact_name']}
            Company: {context['company']}
            Role: {context['role']}
            Technologies: {', '.join(context['technologies'][:3])}
            Recent: {context['recent_news'][0] if context['recent_news'] else 'N/A'}
            
            Generate email body:""")
        ])
        
        body_response = llm.invoke(body_prompt.format_messages())
        email_body = body_response.content.strip()
        
        return {
            "lead": lead,
            "subject_line": subject_line,
            "email_body": email_body,
            "personalization_notes": f"Referenced: {', '.join(context['technologies'][:2])}"
        }
    
    def _generate_mock_messages(self, ranked_leads: List[Dict], value_prop: str) -> List[Dict[str, Any]]:
        """Generate mock messages for demonstration."""
        messages = []
        
        for ranked_lead in ranked_leads:
            lead = ranked_lead["lead"]
            first_name = lead.get("contact", "there").split()[0]
            company = lead.get("company", "your company")
            tech = lead.get("technologies", ["your tech stack"])
            
            subject = f"Boosting revenue at {company}"
            
            body = f"""Hi {first_name},

I noticed {company} is using {tech[0] if tech else 'modern technology'} and thought you might be interested in how similar companies have increased revenue by 30% with our AI-powered analytics platform.

{value_prop}

Would you be open to a quick 15-minute chat next week to see if this could help {company}?

Best regards"""
            
            messages.append({
                "lead": lead,
                "subject_line": subject,
                "email_body": body,
                "personalization_notes": f"Referenced {tech[0] if tech else 'company'}"
            })
        
        return messages
