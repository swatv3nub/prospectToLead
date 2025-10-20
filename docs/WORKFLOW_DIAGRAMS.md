# Workflow Visual Diagram

## Simple Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH WORKFLOW ORCHESTRATION                 │
└─────────────────────────────────────────────────────────────────────┘

                            ┌──────────────┐
                            │    START     │
                            └──────┬───────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │  ProspectSearchAgent │
                        │  • Query Apollo.io   │
                        │  • Deduplicate       │
                        │  • Store in memory   │
                        └──────────┬───────────┘
                                   │
                                   ▼
                          ┌────────────────┐
                          │ Human Approval │  ◄── Quality Gate
                          │   Review ICP   │
                          └────────┬───────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │    ScoringAgent      │
                        │  • AI evaluation     │
                        │  • 0-100 scores      │
                        │  • Filter threshold  │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ OutreachContentAgent │
                        │  • Generate emails   │
                        │  • Personalize       │
                        │  • GPT-4 powered     │
                        └──────────┬───────────┘
                                   │
                                   ▼
                          ┌────────────────┐
                          │ Human Approval │  ◄── Quality Gate
                          │   Review Copy  │
                          └────────┬───────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ OutreachExecutorAgent│
                        │  • Send via SendGrid │
                        │  • Log interactions  │
                        │  • Track delivery    │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ ResponseTrackerAgent │
                        │  • Monitor opens     │
                        │  • Track clicks      │
                        │  • Detect replies    │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ FeedbackTrainerAgent │
                        │  • Analyze metrics   │
                        │  • Compare history   │
                        │  • Generate recs     │
                        └──────────┬───────────┘
                                   │
                                   ▼
                            ┌──────────┐
                            │   END    │
                            └──────────┘

                    ┌────────────────────────┐
                    │   ChromaDB Memory      │
                    │  • Leads (28)          │
                    │  • Campaigns (1)       │
                    │  • Interactions (10)   │
                    │  • Recommendations (3) │
                    └────────────────────────┘
                              ▲
                              │
                    All Agents Read/Write Memory
```

---

## Data Flow Diagram 

```
┌──────────────────────────────────────────────────────────────────────┐
│                      CHROMADB MEMORY ARCHITECTURE                    │
└──────────────────────────────────────────────────────────────────────┘

INPUT                      MEMORY LAYER                     OUTPUT
─────                      ────────────                     ──────

Apollo.io      ──────►  ┌─────────────────┐
Clay API       ──────►  │     LEADS       │  ──────►  Deduplication
Clearbit       ──────►  │   Collection    │  ──────►  History Tracking
                        │ • email (unique)│
                        │ • company       │
                        │ • score         │
                        │ • first_seen    │
                        │ • contact_count │
                        └─────────────────┘

Campaign       ──────►  ┌─────────────────┐
Execution      ──────►  │   CAMPAIGNS     │  ──────►  Performance
Metrics        ──────►  │   Collection    │  ──────►  Trends
                        │ • campaign_id   │
                        │ • open_rate     │
                        │ • reply_rate    │
                        │ • timestamp     │
                        └─────────────────┘

Email Sent     ──────►  ┌─────────────────┐
Email Opened   ──────►  │  INTERACTIONS   │  ──────►  Engagement
Link Clicked   ──────►  │   Collection    │  ──────►  Tracking
Reply Received ──────►  │ • lead_email    │
                        │ • type          │
                        │ • campaign_id   │
                        │ • timestamp     │
                        └─────────────────┘

AI Analysis    ──────►  ┌─────────────────┐
Performance    ──────►  │ RECOMMENDATIONS │  ──────►  Continuous
Comparison     ──────►  │   Collection    │  ──────►  Learning
                        │ • category      │
                        │ • parameter     │
                        │ • suggested     │
                        │ • reasoning     │
                        │ • status        │
                        └─────────────────┘
```

---

## Component Architecture 

```
┌──────────────────────────────────────────────────────────────────────┐
│                       SYSTEM ARCHITECTURE                            │
└──────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATION LAYER                          │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │           LangGraph 1.0.0 StateGraph Builder              │    │
│  │  • Node management  • State transitions  • Flow control   │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐        ┌───────────────┐        ┌───────────────┐
│  AGENT LAYER  │        │  MEMORY LAYER │        │   API LAYER   │
├───────────────┤        ├───────────────┤        ├───────────────┤
│ • Prospect    │        │ • ChromaDB    │        │ • Apollo.io   │
│   Search      │◄──────►│ • Vector DB   │◄──────►│ • OpenAI      │
│ • Scoring     │        │ • Persistence │        │ • SendGrid    │
│ • Outreach    │        │ • 4 Collections│       │ • Clearbit    │
│ • Feedback    │        │               │        │               │
└───────────────┘        └───────────────┘        └───────────────┘
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  ▼
                        ┌─────────────────┐
                        │  HUMAN LAYER    │
                        ├─────────────────┤
                        │ • Approval Gates│
                        │ • Interactive   │
                        │   Feedback      │
                        │ • Custom Input  │
                        └─────────────────┘
```

---

## Feedback Loop Diagram 

```
┌──────────────────────────────────────────────────────────────────────┐
│                      CONTINUOUS LEARNING LOOP                        │
└──────────────────────────────────────────────────────────────────────┘

                    Campaign N
                         │
                         ▼
            ┌────────────────────────┐
            │   Execute Campaign     │
            │  • Find prospects      │
            │  • Send emails         │
            │  • Track responses     │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │   Store in Memory      │
            │  • Lead data           │
            │  • Interactions        │
            │  • Performance metrics │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │   Analyze Results      │
            │  • Compare to history  │
            │  • Identify patterns   │
            │  • Generate insights   │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  Create Recommendations│
            │  • Subject line tips   │
            │  • Content changes     │
            │  • ICP adjustments     │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │   Human Review         │
            │  • Approve/Reject      │
            │  • Modify suggestions  │
            │  • Add custom feedback │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │   Apply Changes        │
            │  • Update workflow     │
            │  • Refine parameters   │
            │  • Test improvements   │
            └────────────┬───────────┘
                         │
                         ▼
                    Campaign N+1
                    (Improved!)
                         │
                         │
                    [Loop continues...]
```

---

## Key Metrics Dashboard 

```
┌──────────────────────────────────────────────────────────────────────┐
│                      CAMPAIGN PERFORMANCE                            │
└──────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   PROSPECTS FOUND   │  │    EMAILS SENT      │  │     OPEN RATE       │
│                     │  │                     │  │                     │
│        28           │  │         25          │  │      32.5%          │
│   ████████████████  │  │   ████████████████  │  │   ████████████████  │
│                     │  │                     │  │   ↑ vs avg (28%)    │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘

┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│    CLICK RATE       │  │    REPLY RATE       │  │   RECOMMENDATIONS   │
│                     │  │                     │  │                     │
│        8.2%         │  │        4.1%         │  │         3           │
│   ████████████████  │  │   ████████████████  │  │   ████████████████  │
│   ↑ vs avg (6.5%)   │  │   ↑ vs avg (2.8%)   │  │   pending review    │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘

MEMORY STATUS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Leads:          28  ████████████████████████████ 
Campaigns:       1  ██
Interactions:   10  ██████████
Recommendations: 3  ██████

HISTORICAL TREND:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reply Rate:  [2.8%] → [3.5%] → [4.1%]  📈 IMPROVING
Open Rate:   [28.0%] → [30.5%] → [32.5%]  📈 IMPROVING
```

---
