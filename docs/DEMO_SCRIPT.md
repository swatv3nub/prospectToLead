# Demo Video Script

## Introduction (30 seconds)
- "Hi, I'm demonstrating a LangGraph-based autonomous prospect-to-lead workflow system"
- "This system automates B2B lead generation from discovery to outreach"
- "It's built with LangGraph, LangChain, and integrates with Apollo, Clearbit, and SendGrid"

## Architecture Overview (60 seconds)
- Show project structure
- "The system has 7 specialized agents working together"
- Open workflow.json
- "Everything is configured declaratively in this JSON file"
- "Each step defines an agent, its inputs, tools, and next step"
- "Agents use ReAct pattern: Reason, Act, Observe"

## Live Execution (90 seconds)
- Run: `python langgraph_builder.py`
- "Watch as it executes each step:"
  - ProspectSearchAgent finds companies matching ICP
  - DataEnrichmentAgent adds context
  - ScoringAgent ranks by fit
  - OutreachContentAgent generates personalized emails
  - OutreachExecutorAgent sends (or simulates)
  - ResponseTrackerAgent monitors engagement
  - FeedbackTrainerAgent suggests improvements
- Show console output with reasoning

## Results (45 seconds)
- Open workflow_results.json
- "Here are the discovered prospects"
- "Their scores and reasoning"
- "Generated personalized messages"
- "And AI-generated recommendations for improvement"

## Key Features (30 seconds)
- "The system is self-improving"
- "FeedbackTrainer analyzes metrics and suggests config changes"
- "Everything is extensible - just add to workflow.json"
- "Works with or without API keys using mock data"

## Design Choices (45 seconds)
- "Why LangGraph? Stateful workflows with conditional logic"
- "Why ReAct pattern? Agents explain their reasoning"
- "Why JSON config? No code changes to modify workflow"
- "Why modular agents? Easy to test and extend"
- "Built with vibe coding using AI assistants"

## Conclusion (20 seconds)
- "The system is production-ready and fully documented"
- "See README for setup instructions"
- "GitHub link in description"
- "Thanks for watching!"

---

## Recording Tips

1. **Screen Setup**: 
   - VS Code on left showing code
   - Terminal on right showing execution
   - 1080p resolution minimum

2. **What to Show**:
   - Project structure in file explorer
   - workflow.json configuration
   - langgraph_builder.py main script
   - Live execution with output
   - Results file
   - Logs showing reasoning

3. **Narration Tips**:
   - Speak clearly and confidently
   - Explain WHY not just WHAT
   - Highlight unique features
   - Keep energy high

4. **Editing**:
   - Add timestamps for each section
   - Zoom in on important code
   - Speed up slow parts (2x)
   - Add captions for key points

5. **Length**: Aim for 3-5 minutes total

## Upload Checklist

- [ ] Video title: "LangGraph Autonomous Prospect-to-Lead Workflow - AI Agent System"
- [ ] Description includes GitHub link
- [ ] Tags: langgraph, langchain, ai agents, lead generation, b2b
- [ ] Set to Public or Unlisted
- [ ] Share link via email
