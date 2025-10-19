# LangGraph-based Autonomous Prospect-to-Lead Workflow

An end-to-end **LangGraph Agent System** that autonomously discovers, enriches, scores, and contacts B2B prospects — and refines its behavior over time through a **FeedbackTrainer** mechanism.

## 🎯 Overview

This project implements an AI-powered outbound lead generation system for **Analytos.ai**, targeting B2B companies in the USA with revenues between $20M–$200M. The system uses LangGraph to orchestrate multiple specialized agents that work collaboratively to automate the entire prospect-to-lead workflow.

### Key Features

- **Dynamic Workflow Construction**: Build entire workflows from a single `workflow.json` configuration
- **Modular Agent Architecture**: 7 specialized agents handling different aspects of the workflow
- **ReAct Pattern**: Agents use Reason → Act → Observe pattern for intelligent decision-making
- **Self-Improving System**: FeedbackTrainer analyzes performance and suggests improvements
- **API Integration**: Supports Clay, Apollo, Clearbit, SendGrid, and Google Sheets
- **Comprehensive Logging**: Detailed execution logs and performance tracking

## 🏗️ Architecture

The system consists of 7 specialized agents:

1. **ProspectSearchAgent**: Discovers prospects using Clay and Apollo APIs
2. **DataEnrichmentAgent**: Enriches lead data with Clearbit/PeopleDataLabs
3. **ScoringAgent**: Scores and ranks leads based on ICP fit
4. **OutreachContentAgent**: Generates personalized email content using GPT-4
5. **OutreachExecutorAgent**: Sends emails via SendGrid/Apollo with rate limiting
6. **ResponseTrackerAgent**: Monitors email engagement (opens, clicks, replies)
7. **FeedbackTrainerAgent**: Analyzes results and suggests workflow improvements

## 📋 Prerequisites

- Python 3.9+
- API Keys for:
  - OpenAI (required for AI agents)
  - Apollo.io (for prospect search - free tier available)
  - Clay (optional - free trial)
  - Clearbit or PeopleDataLabs (optional - for enrichment)
  - SendGrid (for email delivery - free tier available)
  - Google Cloud (optional - for Sheets logging)

## 🚀 Quick Start

### 1. Clone and Setup

```powershell
# Navigate to project directory
cd x:\Project\ProspectToLead

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```powershell
# Copy example environment file
copy .env.example .env

# Edit .env with your API keys
notepad .env
```

**Minimum required configuration**:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
APOLLO_API_KEY=your_apollo_api_key_here
SENDGRID_API_KEY=your_sendgrid_api_key_here
SENDGRID_FROM_EMAIL=your_email@company.com
```

### 3. Run the Workflow

```powershell
# Execute the full workflow
python langgraph_builder.py

# With custom config
python langgraph_builder.py --config ./workflow.json

# Generate workflow visualization
python langgraph_builder.py --visualize
```

## 📁 Project Structure

```
ProspectToLead/
├── agents/
│   ├── __init__.py              # Agent factory
│   ├── base_agent.py            # Base agent with ReAct pattern
│   ├── prospect_search_agent.py # Prospect discovery
│   ├── enrichment_agent.py      # Data enrichment
│   ├── scoring_agent.py         # Lead scoring
│   ├── outreach_content_agent.py # Content generation
│   ├── outreach_executor_agent.py # Email sending
│   ├── response_tracker_agent.py # Response tracking
│   └── feedback_trainer_agent.py # Performance analysis
├── utils/
│   ├── config.py                # Configuration loader
│   ├── logger.py                # Logging utilities
│   └── tools.py                 # API client integrations
├── langgraph_builder.py         # Main workflow builder
├── workflow.json                # Workflow configuration
├── requirements.txt             # Python dependencies
├── .env.example                 # Example environment config
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## ⚙️ Workflow Configuration

The `workflow.json` file defines the entire workflow. Each step includes:

- **id**: Unique identifier
- **agent**: Agent class name
- **inputs**: Input parameters (can reference previous steps)
- **instructions**: Natural language instructions for the agent
- **tools**: API configurations
- **output_schema**: Expected output structure
- **next**: Next step in the workflow (or null for final step)

### Example Step Configuration

```json
{
  "id": "prospect_search",
  "agent": "ProspectSearchAgent",
  "inputs": {
    "icp": {
      "industry": "SaaS",
      "location": "USA",
      "employee_count": { "min": 100, "max": 1000 }
    }
  },
  "instructions": "Search for companies matching ICP criteria",
  "tools": [
    {
      "name": "ApolloAPI",
      "config": { "api_key": "{{APOLLO_API_KEY}}" }
    }
  ],
  "next": "enrichment"
}
```

### Input References

Steps can reference outputs from previous steps:

```json
{
  "inputs": {
    "leads": "{{prospect_search.output.leads}}",
    "workflow_config": "{{workflow}}"
  }
}
```

## 🔧 API Setup Guide

### OpenAI API
1. Sign up at https://platform.openai.com
2. Create an API key
3. Add to `.env`: `OPENAI_API_KEY=sk-...`

### Apollo.io
1. Sign up at https://www.apollo.io (free tier available)
2. Get API key from Settings → Integrations
3. Add to `.env`: `APOLLO_API_KEY=...`

### SendGrid
1. Sign up at https://sendgrid.com (free tier: 100 emails/day)
2. Create API key with Mail Send permissions
3. Verify sender email
4. Add to `.env`:
   ```
   SENDGRID_API_KEY=SG...
   SENDGRID_FROM_EMAIL=verified@yourdomain.com
   ```

### Google Sheets (Optional)
1. Create a Google Cloud project
2. Enable Google Sheets API
3. Create service account and download `credentials.json`
4. Place `credentials.json` in project root
5. Create a Google Sheet and share with service account email
6. Add Sheet ID to `.env`: `GOOGLE_SHEET_ID=...`

## 📊 Output and Results

### Console Output
The workflow provides real-time progress updates:
```
🚀 Starting workflow: OutboundLeadGeneration
✓ Created agent: ProspectSearchAgent
🤔 ProspectSearchAgent reasoning: Analyzing ICP criteria...
✅ Completed step: prospect_search (2.3s)
...
🎉 Workflow completed in 45.2s
```

### Results File
Complete results are saved to `workflow_results.json`:
```json
{
  "status": "completed",
  "outputs": {
    "prospect_search": { "leads": [...] },
    "enrichment": { "enriched_leads": [...] },
    "scoring": { "ranked_leads": [...] },
    ...
  }
}
```

### Feedback and Recommendations
The FeedbackTrainer provides actionable insights:
```
Campaign Performance Summary
===========================
📧 Total Sent: 20
📖 Open Rate: 35.0%
👆 Click Rate: 8.5%
💬 Reply Rate: 4.2%

📋 Recommendations:
• outreach_content - tone
  Open rate is 35%, above average. Continue with current approach.
• scoring - min_score_threshold
  High engagement suggests we can expand targeting.
```

## 🧪 Testing and Development

### Dry Run Mode
Test without sending actual emails:
```python
# In workflow.json, set dry_run: true
{
  "id": "send",
  "inputs": {
    "dry_run": true
  }
}
```

### Mock Data
Agents automatically use mock data when APIs are unavailable, allowing development without all API keys.

### Logging
Logs are written to `./logs/workflow.log` with detailed execution traces.

## 🔄 Extending the System

### Adding a New Agent

1. **Create agent class** in `agents/`:
```python
from agents.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def _act(self, inputs, reasoning):
        # Your logic here
        return {"result": "success"}
```

2. **Register in factory** (`agents/__init__.py`):
```python
AGENT_CLASSES = {
    ...
    "MyCustomAgent": MyCustomAgent
}
```

3. **Add to workflow.json**:
```json
{
  "id": "my_step",
  "agent": "MyCustomAgent",
  "inputs": {...},
  "instructions": "...",
  "next": "next_step"
}
```

### Modifying Workflow Logic

Edit `workflow.json` to:
- Change ICP criteria
- Adjust scoring weights
- Modify outreach tone
- Add/remove workflow steps
- Change step sequencing

No code changes required!

## 📈 Performance Optimization

### Rate Limiting
Configure delays between API calls:
```json
{
  "inputs": {
    "send_delay_seconds": 60
  }
}
```

### Batch Processing
Limit prospects per run:
```json
{
  "inputs": {
    "max_results": 50,
    "max_leads_to_contact": 20
  }
}
```

### Caching
The system automatically caches enrichment data in the state object.

## 🐛 Troubleshooting

### Common Issues

**Import errors for langgraph/langchain:**
```powershell
pip install --upgrade langgraph langchain langchain-openai
```

**API authentication failures:**
- Verify API keys in `.env`
- Check API key permissions/scopes
- Ensure API quotas not exceeded

**Google Sheets errors:**
- Verify `credentials.json` exists
- Check service account email has edit access to sheet
- Confirm Sheet ID is correct

**Email sending failures:**
- Verify sender email in SendGrid
- Check SendGrid API key permissions
- Ensure not exceeding rate limits

## 📝 Best Practices

1. **Start with dry run** to test workflow without sending emails
2. **Use mock data** during development to avoid API costs
3. **Monitor API quotas** to avoid service interruptions
4. **Review feedback** regularly to optimize performance
5. **Version control** your `workflow.json` configurations
6. **Rotate API keys** periodically for security

## 🤝 Contributing

This is a demonstration project. To extend or customize:

1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Test thoroughly
5. Submit pull request with clear description

## 📄 License

This project is provided as-is for demonstration purposes.

## 📧 Contact

For questions about this implementation:
- **Email**: santosh.thota@analytos.ai
- **CC**: gaurav.gupta@analytos.ai

## 📚 Additional Documentation

For more detailed information, see the [docs](./docs/) folder:

- **[Quick Start Guide](./docs/QUICKSTART.md)** - Get running in 5 minutes
- **[Setup Instructions](./docs/SETUP.md)** - Detailed setup and API configuration
- **[System Architecture](./docs/ARCHITECTURE.md)** - In-depth architecture diagrams and explanations
- **[Project Summary](./docs/PROJECT_SUMMARY.md)** - Complete feature list and deliverables
- **[Demo Script](./docs/DEMO_SCRIPT.md)** - Guide for recording demo video

## 🎥 Demo Video

A demo video walkthrough is available showing:
- Complete workflow execution
- Agent reasoning and decision-making
- Performance analysis and recommendations
- Architecture and design choices

---

**Built with**: LangGraph, LangChain, OpenAI GPT-4, Python 3.9+

**Targets**: B2B SaaS companies, $20M-$200M revenue, 100-1000 employees, USA

**Approach**: AI-assisted development using Cursor and Claude (vibe coding encouraged!)
