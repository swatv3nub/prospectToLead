# Interactive Feedback Training

## Overview

The **Interactive Feedback Training** system allows users to provide manual feedback on campaign performance and review AI-generated recommendations through an interactive command-line interface.

This feature enables:
- ✅ Human-in-the-loop approval of AI recommendations
- ✅ Custom feedback and manual observations
- ✅ Campaign performance review with historical comparisons
- ✅ Interactive decision-making for workflow improvements

## Components

### 1. FeedbackTrainerAgent (Interactive Mode)

The `FeedbackTrainerAgent` now supports an `interactive_mode` parameter that enables user prompts during recommendation generation.

**Key Features:**
- Displays campaign performance metrics with historical comparison
- Presents each recommendation with reasoning and expected impact
- Allows users to approve, reject, modify, or skip recommendations
- Collects custom feedback from users
- Tracks approval/rejection with timestamps and attribution

**Usage in Code:**
```python
from agents.feedback_trainer_agent import FeedbackTrainerAgent

# Initialize in interactive mode
agent = FeedbackTrainerAgent(
    agent_name="FeedbackTrainer",
    model="gpt-4o-mini",
    logger=logger,
    interactive_mode=True  # Enable user prompts
)

# Run analysis - will prompt for user input
result = agent.act({
    "responses": responses,
    "campaign_metrics": metrics,
    "workflow_config": config
})
```

### 2. Interactive Feedback Script

The `scripts/interactive_feedback.py` script provides a standalone tool for campaign analysis and recommendation management.

## Usage Guide

### Command-Line Interface

```powershell
# Interactive menu (recommended for first-time users)
python scripts\interactive_feedback.py

# List available campaigns
python scripts\interactive_feedback.py --list-campaigns

# Analyze a specific campaign
python scripts\interactive_feedback.py --analyze campaign_20251019_143025

# View pending recommendations
python scripts\interactive_feedback.py --view-pending

# Review and approve pending recommendations
python scripts\interactive_feedback.py --approve-pending
```

### Interactive Menu Options

When running without arguments, you'll see:

```
INTERACTIVE FEEDBACK TRAINER
======================================================================

Options:
  1. List available campaigns
  2. Analyze a specific campaign (interactive)
  3. View pending recommendations
  4. Review & approve pending recommendations
  5. Exit

Select option [1-5]:
```

### Campaign Analysis Workflow

#### Step 1: List Campaigns

View all campaigns stored in memory:

```powershell
python scripts\interactive_feedback.py --list-campaigns
```

**Output:**
```
AVAILABLE CAMPAIGNS
======================================================================

1. Campaign: campaign_20251019_143025
   Date: 2025-10-19 14:30:25
   Leads: 28
   Sent: 25
   Open Rate: 32.5%
   Click Rate: 8.2%
   Reply Rate: 4.1%

2. Campaign: campaign_20251018_095120
   Date: 2025-10-18 09:51:20
   Leads: 35
   Sent: 35
   Open Rate: 28.0%
   Click Rate: 6.5%
   Reply Rate: 2.8%
```

#### Step 2: Run Interactive Analysis

Analyze a campaign with user interaction:

```powershell
python scripts\interactive_feedback.py --analyze campaign_20251019_143025
```

**Interactive Prompts:**

1. **Performance Summary:**
   ```
   📊 Campaign Performance:
      Open Rate: 32.5%
      Click Rate: 8.2%
      Reply Rate: 4.1%
      Total Sent: 25

   📈 Overall Assessment: HIGH
      [OK] Improving vs historical average
   ```

2. **Review Recommendations:**
   ```
   Would you like to review and approve recommendations? [Y/n]:
   ```

3. **For Each Recommendation:**
   ```
   ----------------------------------------------------------------------
   Recommendation 1/5
   ----------------------------------------------------------------------
   Category: outreach_content
   Parameter: tone
   Current: friendly
   Suggested: curious
   Reasoning: Open rate is 32.5%, above average but could improve with curiosity-driven subject lines.
   Expected Impact: 10-15% increase in open rate

   Options:
     [a] Approve - Accept this recommendation
     [r] Reject - Decline this recommendation
     [m] Modify - Edit the suggested value
     [s] Skip - Leave as pending for later review

   Your choice [a/r/m/s]:
   ```

4. **Approval Actions:**

   - **Approve (a):**
     - Marks recommendation as "approved"
     - Records your username and timestamp
     - Will be used in future campaigns

   - **Reject (r):**
     - Prompts for rejection reason
     - Marks recommendation as "rejected"
     - Won't be applied to workflow

   - **Modify (m):**
     - Allows editing the suggested value
     - Example: Change "curious" to "authoritative"
     - Automatically approves after modification

   - **Skip (s):**
     - Leaves as "pending" for later review
     - Can be reviewed using `--approve-pending`

5. **Custom Feedback:**
   ```
   Would you like to add custom feedback/notes? [y/N]: y

   Enter your feedback: The subject lines need more personalization based on industry

   [OK] Custom feedback added
   ```

6. **Summary:**
   ```
   FEEDBACK SUMMARY
   ======================================================================

   ✓ Approved: 3
   ✗ Rejected: 1
   ⊙ Pending: 1

   [OK] User feedback collection complete

   [OK] Analysis saved to: logs/feedback_campaign_20251019_143025_20251020_155430.json
   ```

### Review Pending Recommendations

View all recommendations that haven't been approved/rejected yet:

```powershell
python scripts\interactive_feedback.py --view-pending
```

**Output:**
```
PENDING RECOMMENDATIONS
======================================================================

1. scoring: min_score_threshold
   Current: 60
   Suggested: 70
   Reasoning: Low reply rate suggests we should focus on higher-quality leads only.
   Expected: Better response rates from more qualified prospects

2. outreach_content: email_length
   Current: 150 words
   Suggested: 100 words
   Reasoning: Click rate is 6.5%. Shorter, punchier emails tend to perform better.
   Expected: 20% increase in click-through rate
```

### Approve Pending Recommendations

Review and make decisions on pending recommendations:

```powershell
python scripts\interactive_feedback.py --approve-pending
```

**Interactive Flow:**
```
REVIEW PENDING RECOMMENDATIONS
======================================================================

----------------------------------------------------------------------
Recommendation 1/2
----------------------------------------------------------------------
Category: scoring
Parameter: min_score_threshold
Current: 60
Suggested: 70
Reasoning: Low reply rate suggests we should focus on higher-quality leads only.
Expected Impact: Better response rates from more qualified prospects

Options:
  [a] Approve
  [r] Reject
  [s] Skip

Your choice [a/r/s]: a
[OK] Approved
```

## Data Storage

### Recommendations in Memory

All recommendations (pending, approved, rejected) are stored in ChromaDB's `recommendations_collection` with metadata:

```python
{
    "category": "outreach_content",
    "parameter": "tone",
    "current_value": "friendly",
    "suggested_value": "curious",
    "reasoning": "...",
    "expected_improvement": "...",
    "approval_status": "approved",  # or "rejected", "pending"
    "approved_by": "john_doe",
    "approval_timestamp": "2025-10-20T15:54:30",
    "modified": True  # If user modified the suggestion
}
```

### Analysis Logs

Each interactive analysis session is saved to `logs/feedback_<campaign_id>_<timestamp>.json`:

```json
{
  "recommendations": [...],
  "analysis_summary": "...",
  "performance_analysis": {
    "open_rate_status": "good",
    "engagement_quality": "high",
    "vs_historical": {
      "improving": true
    }
  },
  "historical_trends": {
    "open_rate_trend": [28.0, 30.5, 32.5],
    "reply_rate_trend": [2.8, 3.5, 4.1]
  }
}
```

## Integration with Workflow

### Using Interactive Mode in LangGraph

To enable interactive feedback in your workflow:

1. **Modify Agent Initialization:**
   ```python
   # In langgraph_builder.py
   feedback_agent = FeedbackTrainerAgent(
       agent_name="FeedbackTrainer",
       model="gpt-4o-mini",
       logger=logger,
       interactive_mode=True  # Enable user interaction
   )
   ```

2. **Run Workflow:**
   ```powershell
   python langgraph_builder.py --interactive-feedback
   ```

   The workflow will pause at the FeedbackTrainer node and prompt for user input.

### Applying Approved Recommendations

Approved recommendations can be applied to future campaigns:

```python
from utils.memory import get_memory

memory = get_memory()

# Get all approved recommendations
approved_recs = [
    r for r in memory.recommendations.get()['metadatas']
    if r.get('approval_status') == 'approved'
]

# Apply to workflow config
for rec in approved_recs:
    if rec['category'] == 'outreach_content':
        workflow_config['outreach_content'][rec['parameter']] = rec['suggested_value']
```

## Benefits

### 1. Human Expertise Integration
- Combines AI insights with human judgment
- Domain experts can override or modify AI suggestions
- Captures tribal knowledge as custom feedback

### 2. Continuous Improvement
- Approved recommendations improve future campaigns
- Rejection reasons help refine AI suggestion quality
- Historical tracking shows improvement over time

### 3. Accountability & Traceability
- Every decision is attributed to a user
- Timestamps track when decisions were made
- Audit trail for compliance and review

### 4. Learning Loop
- AI learns from approval/rejection patterns
- Future recommendations become more aligned with user preferences
- Reduces manual review burden over time

## Best Practices

### 1. Regular Review Cadence
- Review recommendations after each campaign (weekly/monthly)
- Don't let pending recommendations accumulate
- Set aside dedicated time for feedback sessions

### 2. Provide Detailed Rejection Reasons
- Helps improve future AI recommendations
- Creates knowledge base of what works/doesn't work
- Useful for team training

### 3. Use Custom Feedback Liberally
- Add observations not captured by metrics
- Note external factors (seasonality, market changes)
- Document successful tactics for replication

### 4. Test Modified Recommendations
- When modifying suggestions, test with small sample first
- Compare results against AI's original suggestion
- Document which modifications work best

### 5. Review Historical Trends
- Look at performance trends before making decisions
- Consider whether metrics are improving or declining
- Account for statistical significance in small campaigns

## Troubleshooting

### Issue: No Campaigns Found
```
[ERROR] No campaigns found in memory
```
**Solution:** Run at least one campaign first using `python langgraph_builder.py`

### Issue: Campaign Not Found
```
[ERROR] Campaign 'campaign_xyz' not found
```
**Solution:** Use `--list-campaigns` to see available campaign IDs

### Issue: No Pending Recommendations
```
No pending recommendations to review.
```
**Solution:** Run a campaign analysis first or check if all recommendations were already reviewed

### Issue: Permission Denied on Log Files
```
PermissionError: [Errno 13] Permission denied: 'logs/...'
```
**Solution:** Ensure `logs/` directory exists and you have write permissions

## Future Enhancements

Potential improvements for the interactive feedback system:

1. **Web UI**: Browser-based interface for easier interaction
2. **Batch Approval**: Approve multiple similar recommendations at once
3. **A/B Testing**: Test competing recommendations automatically
4. **Team Collaboration**: Multiple users can review and vote on recommendations
5. **Slack Integration**: Approve recommendations directly from Slack
6. **Mobile App**: Review recommendations on the go
7. **Auto-Approval Rules**: Define rules for automatic approval based on criteria
8. **Recommendation Scoring**: Track which recommendations perform best

## Related Documentation

- **[MEMORY.md](MEMORY.md)** - Memory persistence system architecture
- **[CLEAR_MEMORY.md](CLEAR_MEMORY.md)** - Memory management and clearing
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Overall system architecture
- **[DEMO_SCRIPT.md](DEMO_SCRIPT.md)** - Demonstration walkthrough

## Summary

The Interactive Feedback Training system bridges the gap between AI automation and human expertise, ensuring that workflow optimizations are:
- ✅ Data-driven (from AI analysis)
- ✅ Validated (by human experts)
- ✅ Traceable (with audit trails)
- ✅ Continuously improving (through learning loops)

Use this system to maintain quality control while scaling your outbound lead generation campaigns.
