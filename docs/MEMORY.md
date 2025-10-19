# Memory Persistence System

## Overview

The workflow system includes a **ChromaDB-based memory persistence layer** that stores historical data about leads, campaigns, interactions, and recommendations. This enables:

- **Lead deduplication** - Avoid contacting the same leads multiple times
- **Performance tracking** - Monitor metrics across campaigns over time
- **Historical learning** - FeedbackTrainer uses past campaign data to improve recommendations
- **Interaction history** - Track all email opens, clicks, and replies for each lead

## Architecture

```
WorkflowMemory (ChromaDB)
├── leads_collection          # All discovered and contacted leads
├── campaigns_collection       # Campaign execution history and metrics
├── interactions_collection    # Email interactions (opened, clicked, replied)
└── recommendations_collection # AI-generated improvement suggestions
```

## Features

### 1. Lead Deduplication

**ProspectSearchAgent** automatically filters out leads that have been contacted before:

```python
# Automatically checks memory before adding leads
unique_leads = []
for lead in leads:
    if not memory.is_lead_duplicate(lead['email']):
        unique_leads.append(lead)
        memory.add_lead(lead)
```

### 2. Interaction Tracking

**OutreachExecutorAgent** and **ResponseTrackerAgent** log all interactions:

```python
# Log email sent
memory.add_interaction(email, "email_sent", {
    "campaign_id": campaign_id,
    "subject": subject,
    "sent_at": timestamp
})

# Log email opened
memory.add_interaction(email, "email_opened", {
    "campaign_id": campaign_id
})

# Log email replied
memory.add_interaction(email, "email_replied", {
    "campaign_id": campaign_id,
    "reply_content": content
})
```

### 3. Campaign History

**LangGraphBuilder** stores complete campaign data after each execution:

```python
campaign_data = {
    "workflow_name": "OutboundLeadGeneration",
    "campaign_id": "campaign_abc123",
    "total_leads": 50,
    "emails_sent": 20,
    "metrics": {
        "open_rate": 35.0,
        "click_rate": 8.5,
        "reply_rate": 3.2
    }
}
memory.add_campaign(campaign_id, campaign_data)
```

### 4. Historical Learning

**FeedbackTrainerAgent** uses past campaign data to make better recommendations:

```python
# Get performance trends
trends = memory.get_performance_trends("reply_rate", limit=10)

# Find best performing configurations
best_configs = memory.get_best_performing_configs("reply_rate", limit=3)

# Compare current campaign to historical average
if current_reply_rate > avg_historical_reply_rate:
    # Performance is improving!
```

### 5. Recommendation Tracking

**FeedbackTrainerAgent** stores all recommendations with approval status:

```python
memory.add_recommendation({
    "category": "outreach_content",
    "parameter": "tone",
    "current_value": "friendly",
    "suggested_value": "curious",
    "reasoning": "Open rate is 20%, below average...",
    "approval_status": "pending"
})

# Later, after human review:
memory.approve_recommendation(rec_id)
```

## Using the Memory System

### View Statistics

```powershell
# View all memory statistics
python scripts\view_memory.py --all

# View specific information
python scripts\view_memory.py --stats
python scripts\view_memory.py --campaigns
python scripts\view_memory.py --trends
python scripts\view_memory.py --recommendations

# Check if a lead exists
python scripts\view_memory.py --check-lead john.doe@company.com
```

### Example Output

```
============================================================
WORKFLOW MEMORY STATISTICS
============================================================

📊 Overview:
  • Total Leads: 150
  • Total Campaigns: 3
  • Total Interactions: 245
  • Pending Recommendations: 5
  • Storage Location: ./data/chroma

============================================================
RECENT CAMPAIGNS
============================================================

1. Campaign: campaign_20251019
   Date: 2025-10-19T14:30:00
   Leads: 50
   Sent: 20
   Metrics: Open:35.0% Reply:3.2%

2. Campaign: campaign_20251018
   Date: 2025-10-18T10:15:00
   Leads: 50
   Sent: 20
   Metrics: Open:28.5% Reply:2.1%

============================================================
PERFORMANCE TRENDS (Last 10 Campaigns)
============================================================

📖 Open Rate Trend: 28.5% → 31.2% → 35.0%
   Average: 31.6%

💬 Reply Rate Trend: 2.1% → 2.8% → 3.2%
   Average: 2.7%
```

### Access Memory Programmatically

```python
from utils.memory import get_memory

# Get memory instance
memory = get_memory()

# Check for duplicates
if memory.is_lead_duplicate("john@example.com"):
    print("Lead already contacted!")

# Get lead history
history = memory.get_lead_history("john@example.com")
print(f"Contacted {history['metadata']['contact_count']} times")

# Get all interactions
interactions = memory.get_lead_interactions("john@example.com")
for interaction in interactions:
    print(f"{interaction['metadata']['interaction_type']} - {interaction['metadata']['timestamp']}")

# Get performance trends
reply_rates = memory.get_performance_trends("reply_rate", limit=10)
avg_reply_rate = sum(reply_rates) / len(reply_rates)
print(f"Average reply rate: {avg_reply_rate}%")

# Find similar campaigns
similar = memory.search_similar_campaigns(current_config, limit=5)
for campaign in similar:
    print(f"Similar campaign: {campaign['metadata']['campaign_id']}")
    print(f"Similarity: {campaign['similarity_score']:.2f}")
```

## Data Persistence

- **Storage Location**: `./data/chroma/` (configurable)
- **Format**: ChromaDB vector database
- **Persistence**: Automatic - data survives restarts
- **Reset**: Use `memory.reset_all()` to clear (use with caution!)

## Memory Statistics

```python
stats = memory.get_statistics()
# {
#     "total_leads": 150,
#     "total_campaigns": 3,
#     "total_interactions": 245,
#     "pending_recommendations": 5,
#     "memory_location": "./data/chroma"
# }
```

## Integration Points

### Agent Integration

All agents automatically use memory when appropriate:

| Agent | Memory Usage |
|-------|-------------|
| ProspectSearchAgent | Deduplicates leads, stores new leads |
| OutreachExecutorAgent | Logs email sent interactions |
| ResponseTrackerAgent | Logs opens, clicks, replies |
| FeedbackTrainerAgent | Retrieves trends, stores recommendations |
| LangGraphBuilder | Stores campaign results |

### Workflow Output

After each workflow execution, results include memory stats:

```json
{
  "status": "completed",
  "outputs": { ... },
  "campaign_id": "campaign_abc123",
  "memory_stats": {
    "total_leads": 150,
    "total_campaigns": 3,
    "total_interactions": 245,
    "pending_recommendations": 5
  }
}
```

## Benefits

1. **No Duplicate Outreach**: Automatically prevents contacting the same leads
2. **Continuous Learning**: System improves based on historical performance
3. **Full Audit Trail**: Complete history of all interactions
4. **Data-Driven Recommendations**: FeedbackTrainer uses real historical data
5. **Performance Tracking**: Monitor improvement over time

## Advanced Features

### Search Similar Campaigns

Find campaigns with similar configurations to learn from past successes:

```python
similar_campaigns = memory.search_similar_campaigns(
    current_config, 
    limit=5
)
```

### Get Best Performers

Retrieve top-performing campaigns for any metric:

```python
best_campaigns = memory.get_best_performing_configs(
    metric="reply_rate", 
    limit=5
)
```

### Trend Analysis

Track how metrics change over time:

```python
open_rate_trend = memory.get_performance_trends("open_rate", limit=20)
# [25.0, 27.5, 30.2, 32.1, ...]
```

## Storage Considerations

- **ChromaDB** uses SQLite backend for persistence
- Data is stored locally in `./data/chroma/`
- Storage grows with usage (~1-10 MB per campaign)
- No external database required
- Can be backed up by copying the `./data/chroma/` directory

## Future Enhancements

Potential future additions:
- Export memory to JSON/CSV
- Import historical campaign data
- Advanced similarity search with embeddings
- Automated A/B test tracking
- Multi-workspace memory isolation

---

**Memory persistence is enabled by default** and requires no configuration. The system automatically creates the storage directory on first use.
