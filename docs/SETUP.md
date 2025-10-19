# Setup Instructions

## Quick Setup (5 minutes)

### 1. Install Python Dependencies

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install all requirements
pip install -r requirements.txt
```

### 2. Configure API Keys

```powershell
# Copy example environment file
copy .env.example .env

# Edit with your API keys
notepad .env
```

**Minimum configuration** (to get started):
```env
OPENAI_API_KEY=sk-your-key-here
APOLLO_API_KEY=your-apollo-key
```

### 3. Verify Configuration

```powershell
python scripts\check_config.py
```

### 4. Run Tests

```powershell
python tests\test_workflow.py
```

### 5. Execute Workflow

```powershell
# Full workflow
python langgraph_builder.py

# Simplified test workflow
python langgraph_builder.py --config workflow_simple.json
```

## Obtaining API Keys

### OpenAI (Required)
1. Go to https://platform.openai.com
2. Sign up or log in
3. Navigate to API Keys
4. Create new key
5. Copy and add to `.env`

### Apollo.io (Required for real data)
1. Go to https://www.apollo.io
2. Sign up (free tier available)
3. Go to Settings → Integrations → API
4. Copy API key
5. Add to `.env`

### SendGrid (Required for sending emails)
1. Go to https://sendgrid.com
2. Sign up (free tier: 100 emails/day)
3. Settings → API Keys → Create API Key
4. Give "Mail Send" permission
5. Copy key and add to `.env`
6. **Important**: Verify your sender email in SendGrid

### Optional APIs

**Clearbit** (enrichment):
- https://clearbit.com
- Free trial available
- Add to `.env` if using

**Clay** (prospecting):
- https://clay.com
- Free trial available
- Add to `.env` if using

**Google Sheets** (feedback logging):
1. Create Google Cloud project
2. Enable Google Sheets API
3. Create service account
4. Download `credentials.json`
5. Place in project root
6. Share your Google Sheet with service account email

## Running in Mock Mode

You can test the system without all API keys - it will use mock data:

```powershell
# Will use mock data where APIs are not configured
python langgraph_builder.py
```

The system automatically falls back to mock data when:
- API keys are missing
- APIs return errors
- Rate limits are hit

## Troubleshooting

### "Module not found" errors
```powershell
pip install --upgrade -r requirements.txt
```

### Virtual environment issues
```powershell
# Recreate virtual environment
Remove-Item -Recurse -Force .\venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### API authentication errors
- Double-check API keys in `.env`
- Ensure no extra spaces or quotes
- Verify API key permissions

### Google Sheets errors
- Confirm `credentials.json` exists
- Check service account has edit access
- Verify Sheet ID is correct

## Next Steps

1. ✅ Complete setup steps above
2. ✅ Run configuration check
3. ✅ Run tests
4. ✅ Execute simplified workflow
5. ✅ Execute full workflow
6. ✅ Review results in `workflow_results.json`
7. ✅ Check logs in `logs/workflow.log`

## Need Help?

- Check README.md for detailed documentation
- Review example configurations in `workflow_simple.json`
- Check logs for detailed error messages
