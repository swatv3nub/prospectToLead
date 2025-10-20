# LangGraph Outbound Lead Generation Workflow

A sophisticated, **AI-powered outbound lead generation system** built with **LangGraph 1.0.0** that automates the entire process from prospect discovery to personalized outreach and performance optimization — with **ChromaDB memory persistence** that enables continuous learning and prevents duplicate outreach.

## 🎯 Overview

This project implements an intelligent, self-improving lead generation system that:
- ✅ Discovers and enriches B2B prospects from multiple sources
- ✅ Generates personalized, AI-powered email outreach
- ✅ Tracks engagement (opens, clicks, replies) in real-time
- ✅ Learns from historical performance to improve future campaigns
- ✅ Prevents duplicate outreach using memory persistence
- ✅ Provides human-in-the-loop approval gates for quality control

### 🚀 Key Features

- **🔍 Intelligent Prospect Discovery**: Multi-source lead enrichment using Apollo.io, Clay, and Clearbit
- **✉️ Personalized Email Outreach**: AI-generated, context-aware email campaigns with GPT-4o-mini
- **📊 Response Tracking**: Real-time monitoring of opens, clicks, and replies via SendGrid
- **🧠 Continuous Learning**: FeedbackTrainer analyzes performance and suggests data-driven improvements
- **💾 Memory Persistence**: ChromaDB-based storage prevents duplicate outreach and enables historical learning
- **🔄 Human-in-the-Loop**: Manual approval gates for lead selection and email content
- **📈 Performance Analytics**: Detailed metrics and trend analysis across campaigns
- **📁 Organized Export**: Prospects automatically saved to organized folders (CSV/JSON/Excel) with timestamps

## 🏗️ Architecture

The system uses **LangGraph 1.0.0** to orchestrate a multi-agent workflow with **ChromaDB memory persistence**:

```
ProspectSearchAgent → OutreachExecutorAgent → ResponseTrackerAgent → FeedbackTrainerAgent
        ↓                       ↓                      ↓                      ↓
   [Find Leads]          [Send Emails]          [Track Responses]      [Optimize]
        ↓                       ↓                      ↓                      ↓
  Human Approval         Human Approval         Auto (with memory)    Store Recommendations
        ↓                       ↓                      ↓                      ↓
   Deduplicate           Log Interactions       Track Engagement      Historical Learning
```

### 🧠 Memory Persistence Layer

**ChromaDB-based memory system** with 4 collections:

```
WorkflowMemory (ChromaDB)
├── leads_collection          # All discovered and contacted leads (deduplication)
├── campaigns_collection       # Campaign execution history and metrics
├── interactions_collection    # Email interactions (opened, clicked, replied)
└── recommendations_collection # AI-generated improvement suggestions
```

**Memory enables**:
- ✅ Lead deduplication (never contact the same person twice)
- ✅ Performance tracking (monitor metrics across campaigns)
- ✅ Historical learning (FeedbackTrainer uses past data to improve)
- ✅ Full audit trail (complete interaction history)

**See [docs/MEMORY.md](docs/MEMORY.md) for complete memory documentation.**

### 🤖 Agent Architecture

4 specialized agents working collaboratively:

1. **ProspectSearchAgent**: Discovers prospects using multiple APIs
   - Sources: Apollo.io, Clay, Clearbit
   - **Memory integration**: Automatically deduplicates leads before returning
   - Output: Enriched lead profiles

2. **OutreachExecutorAgent**: Generates and sends personalized emails
   - AI-powered personalization using GPT-4o-mini
   - SendGrid delivery with rate limiting
   - **Memory integration**: Logs "email_sent" interactions

3. **ResponseTrackerAgent**: Monitors email engagement
   - Tracks opens, clicks, replies in real-time
   - Calculates campaign metrics
   - **Memory integration**: Logs all engagement interactions

4. **FeedbackTrainerAgent**: Analyzes performance and optimizes
   - Compares current performance to historical trends
   - Learns from best-performing campaigns
   - **Memory integration**: Retrieves trends, stores recommendations

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

### 4. View Found Prospects

After the workflow runs, prospects are automatically stored in memory and can be viewed/exported:

```powershell
# View prospects in console
python scripts\view_prospects.py

# Export to CSV (saved to prospects/csv/ folder)
python scripts\view_prospects.py --csv

# Export to JSON (saved to prospects/json/ folder)
python scripts\view_prospects.py --json

# Export to Excel (saved to prospects/xlsx/ folder)
python scripts\view_prospects.py --xlsx

# Export all formats at once
python scripts\view_prospects.py --csv --json --xlsx
```

**Exported files are organized by format**:
- `prospects/csv/prospects_20251019_143025.csv` - Spreadsheet format
- `prospects/json/prospects_20251019_143025.json` - Structured data format
- `prospects/xlsx/prospects_20251019_143025.xlsx` - Excel format with formatting

### 5. View Memory Statistics

Check campaign history and memory statistics:

```powershell
# View all memory statistics
python scripts\view_memory.py --all

# View specific information
python scripts\view_memory.py --stats       # Overall statistics
python scripts\view_memory.py --campaigns   # Recent campaigns
python scripts\view_memory.py --trends      # Performance trends

# Check if a lead exists
python scripts\view_memory.py --check-lead john.doe@company.com
```

### 6. Clear Memory (Optional)

Remove data from memory when needed:

```powershell
# Show current memory statistics
python scripts\clear_memory.py --stats

# Clear only prospects/leads
python scripts\clear_memory.py --leads

# Clear all data (with confirmation)
python scripts\clear_memory.py --all
```

### 7. Interactive Feedback & Recommendation Review

Provide feedback on campaign performance and approve AI-generated recommendations:

```powershell
# Interactive menu
python scripts\interactive_feedback.py

# List all campaigns
python scripts\interactive_feedback.py --list-campaigns

# Analyze a specific campaign with interactive prompts
python scripts\interactive_feedback.py --analyze campaign_20251019_143025

# View pending recommendations
python scripts\interactive_feedback.py --view-pending

# Review and approve/reject pending recommendations
python scripts\interactive_feedback.py --approve-pending

# Force clear without confirmation (use with caution!)
python scripts\clear_memory.py --all --force
```

**⚠️ Note:** Cleared data cannot be recovered. Export prospects first if needed:
```powershell
python scripts\view_prospects.py --csv --json
python scripts\clear_memory.py --leads
```

See [docs/CLEAR_MEMORY.md](docs/CLEAR_MEMORY.md) for detailed documentation.

## 📁 Project Structure

```
ProspectToLead/
├── agents/
│   ├── __init__.py              # Agent factory
│   ├── base_agent.py            # Base agent with ReAct pattern
│   ├── prospect_search_agent.py # Prospect discovery with memory deduplication
│   ├── enrichment_agent.py      # Data enrichment
│   ├── scoring_agent.py         # Lead scoring
│   ├── outreach_content_agent.py # Content generation
│   ├── outreach_executor_agent.py # Email sending with interaction logging
│   ├── response_tracker_agent.py # Response tracking with memory
│   └── feedback_trainer_agent.py # Performance analysis with historical learning
├── utils/
│   ├── config.py                # Configuration loader
│   ├── logger.py                # Logging utilities
│   ├── llm.py                   # OpenAI GPT-4o-mini integration
│   ├── memory.py                # ChromaDB memory persistence layer
│   └── tools.py                 # API client integrations
├── scripts/
│   ├── check_config.py          # Configuration validation
│   ├── view_memory.py           # Memory statistics and querying
│   ├── view_prospects.py        # View and export prospects
│   └── clear_memory.py          # Clear data from memory
├── docs/
│   ├── MEMORY.md                # Memory system documentation
│   ├── CLEAR_MEMORY.md          # Clear memory documentation
│   ├── BUGFIX_UNICODE.md        # Unicode encoding fix documentation
│   ├── PROJECT_SUMMARY.md       # Project overview
│   ├── QUICKSTART.md            # Quick start guide
│   └── SETUP.md                 # Detailed setup instructions
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── test_agents.py           # Agent unit tests
│   └── test_workflow.py         # End-to-end workflow tests
├── data/
│   └── chroma/                  # ChromaDB memory storage (auto-created)
├── logs/
│   └── workflow.log             # Workflow execution logs
├── prospects/                   # Exported prospect data (organized by format)
│   ├── README.md                # Prospects folder documentation
│   ├── csv/                     # CSV exports with timestamps
│   ├── json/                    # JSON exports with timestamps
│   └── xlsx/                    # Excel exports with timestamps
├── langgraph_builder.py         # Main workflow builder
├── workflow.json                # Workflow configuration
├── workflow_simple.json         # Simplified workflow config
├── demo.py                      # Example workflow execution
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
- **[Memory System](./docs/MEMORY.md)** - Complete guide to ChromaDB memory persistence
- **[System Architecture](./docs/ARCHITECTURE.md)** - In-depth architecture diagrams and explanations
- **[Project Summary](./docs/PROJECT_SUMMARY.md)** - Complete feature list and deliverables
- **[Demo Script](./docs/DEMO_SCRIPT.md)** - Guide for recording demo video
- **[Bug Fixes](./docs/BUGFIX_UNICODE.md)** - Unicode encoding fix for Windows compatibility

### 📁 Prospects Export

The `prospects/` folder contains exported lead data organized by format:
- **`prospects/csv/`** - CSV files with timestamp (e.g., `prospects_20251019_143025.csv`)
- **`prospects/json/`** - JSON files with timestamp (e.g., `prospects_20251019_143025.json`)
- **`prospects/xlsx/`** - Excel files with timestamp (e.g., `prospects_20251019_143025.xlsx`)

Use `python scripts\view_prospects.py --help` for export options.

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
