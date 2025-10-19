# Quick Start Guide

## ⚡ Get Running in 5 Minutes

### Step 1: Setup Environment (1 minute)
```powershell
# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Configure (2 minutes)
```powershell
# Copy example config
copy .env.example .env

# Add minimum required keys to .env:
# - OPENAI_API_KEY=sk-your-key
# - APOLLO_API_KEY=your-key (or leave empty for mock data)
```

### Step 3: Verify (1 minute)
```powershell
# Check configuration
python scripts\check_config.py

# Run tests
python tests\test_workflow.py
```

### Step 4: Execute (1 minute)
```powershell
# Run full workflow
python langgraph_builder.py

# Or run simplified version
python langgraph_builder.py --config workflow_simple.json

# Or run interactive demo
python demo.py
```

## 📊 What Happens When You Run?

1. **ProspectSearch** finds 50 B2B companies matching your ICP
2. **Enrichment** adds technology stack, recent news, social profiles
3. **Scoring** ranks prospects by fit score (0-100)
4. **OutreachContent** generates personalized emails using GPT-4
5. **OutreachExecutor** sends emails (or simulates in dry-run mode)
6. **ResponseTracker** monitors opens, clicks, and replies
7. **FeedbackTrainer** analyzes results and suggests improvements

## 📂 Output Files

After execution, check:
- `workflow_results.json` - Complete execution results
- `logs/workflow.log` - Detailed execution logs
- Google Sheets - Campaign metrics and recommendations (if configured)

## 🎯 Next Steps

1. ✅ Review results in `workflow_results.json`
2. ✅ Check reasoning in `logs/workflow.log`
3. ✅ Modify `workflow.json` to customize behavior
4. ✅ Add real API keys for production use
5. ✅ Record demo video using `DEMO_SCRIPT.md`

## 💡 Tips

- **No API keys?** System uses mock data automatically
- **Want to test?** Use `workflow_simple.json` (3 steps only)
- **Need help?** See `README.md` for detailed docs
- **Email issues?** Set `dry_run: true` in workflow.json

## 🚀 Ready to Deploy

The system is production-ready with:
- Error handling and retries
- Rate limiting for APIs
- Comprehensive logging
- Mock data fallback
- Dry-run testing mode

---

**Need more details?** See:
- `README.md` - Full documentation
- `SETUP.md` - Detailed setup instructions
- `PROJECT_SUMMARY.md` - Complete feature list
- `DEMO_SCRIPT.md` - Video recording guide
