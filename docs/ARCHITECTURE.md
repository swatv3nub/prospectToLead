# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    workflow.json (Configuration)                 │
│  Defines: ICP criteria, scoring weights, outreach parameters    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LangGraph Builder (langgraph_builder.py)        │
│  • Reads and validates workflow.json                            │
│  • Dynamically constructs LangGraph state machine               │
│  • Orchestrates agent execution                                 │
│  • Manages state flow between steps                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Agent Execution Flow                      │
└─────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────┐
    │ 1. ProspectSearchAgent                              │
    │    • Searches Apollo/Clay APIs                      │
    │    • Filters by ICP (industry, size, revenue)       │
    │    • Detects buying signals                         │
    │    Output: 50 raw prospects                         │
    └──────────────────┬──────────────────────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────────────────────┐
    │ 2. DataEnrichmentAgent                              │
    │    • Enriches with Clearbit/PeopleDataLabs          │
    │    • Adds: tech stack, news, social profiles        │
    │    • Validates data quality                         │
    │    Output: Enriched prospect data                   │
    └──────────────────┬──────────────────────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────────────────────┐
    │ 3. ScoringAgent                                     │
    │    • Calculates fit score (0-100)                   │
    │    • Weighs: size, revenue, tech, signals           │
    │    • Ranks prospects by score                       │
    │    Output: Top 20 ranked leads                      │
    └──────────────────┬──────────────────────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────────────────────┐
    │ 4. OutreachContentAgent                             │
    │    • Uses GPT-4 for personalization                 │
    │    • Generates subject lines + email body           │
    │    • References company-specific details            │
    │    Output: 20 personalized messages                 │
    └──────────────────┬──────────────────────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────────────────────┐
    │ 5. OutreachExecutorAgent                            │
    │    • Sends via SendGrid API                         │
    │    • Implements rate limiting                       │
    │    • Logs delivery status                           │
    │    Output: Campaign ID + send status                │
    └──────────────────┬──────────────────────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────────────────────┐
    │ 6. ResponseTrackerAgent                             │
    │    • Monitors opens, clicks, replies                │
    │    • Tracks engagement over 72 hours                │
    │    • Calculates metrics                             │
    │    Output: Engagement data + metrics                │
    └──────────────────┬──────────────────────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────────────────────┐
    │ 7. FeedbackTrainerAgent                             │
    │    • Analyzes campaign performance                  │
    │    • Suggests workflow improvements                 │
    │    • Logs to Google Sheets for approval             │
    │    Output: Recommendations + analysis               │
    └─────────────────────────────────────────────────────┘
```

## Data Flow

```
Input (ICP Criteria)
    ↓
[Prospect Search] → Raw leads (50)
    ↓
[Enrichment] → Enriched leads (50)
    ↓
[Scoring] → Ranked leads (20 above threshold)
    ↓
[Content Gen] → Personalized messages (20)
    ↓
[Execution] → Sent emails (20)
    ↓
[Tracking] → Engagement metrics
    ↓
[Feedback] → Improvement recommendations
    ↓
Output (Optimized workflow config)
```

## ReAct Pattern (Each Agent)

```
┌──────────────────────────────────────────────┐
│ Agent Execution Loop                         │
├──────────────────────────────────────────────┤
│                                              │
│  1. REASON (Analyze inputs)                  │
│     ├─ LLM analyzes inputs                   │
│     ├─ Plans approach                        │
│     └─ Explains reasoning                    │
│         ↓                                    │
│  2. ACT (Execute logic)                      │
│     ├─ Call external APIs                    │
│     ├─ Process data                          │
│     └─ Generate outputs                      │
│         ↓                                    │
│  3. OBSERVE (Validate)                       │
│     ├─ Check output schema                   │
│     ├─ Log results                           │
│     └─ Return structured data                │
│                                              │
└──────────────────────────────────────────────┘
```

## State Management

```
WorkflowState {
    workflow_config: {...},      // Original config
    current_step: "step_id",     // Current position
    step_outputs: {              // All step outputs
        "prospect_search": {...},
        "enrichment": {...},
        "scoring": {...},
        ...
    },
    errors: [...]                // Any errors
}

State flows through graph:
  Initial State → Node 1 → Node 2 → ... → Node N → Final State
```

## Tool Integration Architecture

```
Agent
  ↓
Tools Layer (utils/tools.py)
  ↓
┌─────────────┬──────────────┬─────────────┬──────────────┐
│  Apollo API │  Clearbit    │  OpenAI     │  SendGrid    │
│             │              │             │              │
│ • Search    │ • Enrich     │ • Generate  │ • Send       │
│ • Enrich    │   person     │   content   │   email      │
│             │ • Enrich     │ • Reasoning │              │
│             │   company    │             │              │
└─────────────┴──────────────┴─────────────┴──────────────┘
```

## Error Handling Flow

```
Try Execute Step
  │
  ├─ Success → Log + Store Output → Next Step
  │
  └─ Error → 
       ├─ Log Error
       ├─ Add to state.errors
       ├─ Retry (if configured)
       └─ Continue or Fail
```

## Feedback Loop

```
Campaign Results
  ↓
Analyze Metrics
  ↓
Generate Recommendations
  ↓
Log to Google Sheets
  ↓
Human Reviews & Approves
  ↓
Update workflow.json
  ↓
Re-run with improved config
  ↓
Better Results 🎉
```

## File Structure Map

```
ProspectToLead/
│
├── 🎯 Entry Points
│   ├── langgraph_builder.py    # Main execution
│   ├── demo.py                  # Interactive demo
│   └── tests/test_workflow.py  # Test suite
│
├── 🤖 Agents
│   ├── base_agent.py           # ReAct pattern base
│   ├── prospect_search_agent.py
│   ├── enrichment_agent.py
│   ├── scoring_agent.py
│   ├── outreach_content_agent.py
│   ├── outreach_executor_agent.py
│   ├── response_tracker_agent.py
│   └── feedback_trainer_agent.py
│
├── 🔧 Utilities
│   ├── config.py               # Config loading
│   ├── logger.py               # Logging system
│   └── tools.py                # API clients
│
├── ⚙️ Configuration
│   ├── workflow.json           # Full workflow
│   ├── workflow_simple.json    # Simple test
│   └── .env.example            # API keys template
│
└── 📚 Documentation
    ├── README.md               # Main docs
    ├── QUICKSTART.md           # 5-min start
    ├── SETUP.md                # Detailed setup
    ├── DEMO_SCRIPT.md          # Video guide
    └── PROJECT_SUMMARY.md      # Feature list
```

## Technology Stack

```
┌─────────────────────────────────────────────────┐
│            Application Layer                     │
│  • LangGraph (Workflow Orchestration)           │
│  • LangChain (Agent Framework)                  │
│  • Custom Agents (Business Logic)               │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────┴───────────────────────────────┐
│            Integration Layer                     │
│  • OpenAI GPT-4o-mini (LLM)                     │
│  • Apollo API (Prospecting)                     │
│  • Clearbit/PDL (Enrichment)                    │
│  • SendGrid (Email)                             │
│  • Google Sheets (Logging)                      │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────┴───────────────────────────────┐
│            Infrastructure Layer                  │
│  • Python 3.9+                                  │
│  • Logging (colorlog)                           │
│  • HTTP Clients (requests, httpx)               │
│  • Vector Store (ChromaDB - optional)           │
└─────────────────────────────────────────────────┘
```

## Deployment Options

```
Development Mode
  • Mock data for all APIs
  • Dry-run email sending
  • Local logging only
  
Production Mode
  • Real API integration
  • Actual email delivery
  • Google Sheets logging
  • Error alerting
```

---

This architecture provides:
- ✅ Modularity (each agent independent)
- ✅ Scalability (add agents via JSON)
- ✅ Maintainability (clear separation of concerns)
- ✅ Testability (mock at any layer)
- ✅ Observability (comprehensive logging)
