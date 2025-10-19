# Clear Memory Script Documentation

## Overview
The `clear_memory.py` script allows you to selectively or completely clear data from the ChromaDB memory persistence layer.

## Location
`scripts/clear_memory.py`

## Usage

### Show Current Statistics
```powershell
python scripts\clear_memory.py --stats
```

**Output:**
```
============================================================
MEMORY STATISTICS
============================================================
Leads: 54
Campaigns: 0
Interactions: 0
Pending Recommendations: 0
Storage Location: ./data/chroma
============================================================
```

### Clear Specific Data Types

#### Clear Leads/Prospects Only
```powershell
python scripts\clear_memory.py --leads
```
- Prompts for confirmation before deleting
- Removes all discovered prospects from memory
- Useful when you want to start fresh with prospect discovery

#### Clear Campaigns Only
```powershell
python scripts\clear_memory.py --campaigns
```
- Removes all campaign execution history
- Keeps leads, interactions, and recommendations intact

#### Clear Interactions Only
```powershell
python scripts\clear_memory.py --interactions
```
- Removes all email interaction logs (sent, opened, clicked, replied)
- Useful for testing interaction tracking

#### Clear Recommendations Only
```powershell
python scripts\clear_memory.py --recommendations
```
- Removes all AI-generated recommendations
- Useful for clearing old suggestions

### Clear All Data
```powershell
python scripts\clear_memory.py --all
```
- Shows summary of all data before deletion
- Prompts for confirmation
- Clears all collections at once

**Example:**
```
Current memory statistics:
  - Leads: 54
  - Campaigns: 3
  - Interactions: 120
  - Recommendations: 5
  - Total items: 182

Are you sure you want to delete ALL data from memory? (yes/no): yes

[OK] Memory cleared successfully:
  - Leads deleted: 54
  - Campaigns deleted: 3
  - Interactions deleted: 120
  - Recommendations deleted: 5
```

### Force Mode (Skip Confirmation)
```powershell
python scripts\clear_memory.py --all --force
```
- **⚠️ USE WITH CAUTION!**
- Skips all confirmation prompts
- Useful for automated scripts or testing

### Combine Multiple Operations
```powershell
# Clear leads and campaigns together
python scripts\clear_memory.py --leads --campaigns

# Clear everything except recommendations
python scripts\clear_memory.py --leads --campaigns --interactions

# Show stats after clearing
python scripts\clear_memory.py --leads --stats
```

## Safety Features

### 1. Confirmation Prompts
All delete operations require explicit confirmation:
- Type `yes` or `y` to confirm
- Type `no` or `n` to cancel
- Any other input cancels the operation

### 2. Empty Collection Checks
Script detects empty collections and skips deletion:
```
No leads found in memory.
```

### 3. Summary Statistics
After deletion, shows:
- Number of items deleted from each collection
- Final memory statistics

## Use Cases

### 1. Start Fresh with Prospect Discovery
```powershell
# Clear only leads to re-run prospect search
python scripts\clear_memory.py --leads
```

### 2. Reset After Testing
```powershell
# Clear all test data
python scripts\clear_memory.py --all --force
```

### 3. Clean Old Campaigns
```powershell
# Remove old campaign data, keep leads
python scripts\clear_memory.py --campaigns --interactions
```

### 4. Clear Recommendations Before Review
```powershell
# Start fresh with recommendations
python scripts\clear_memory.py --recommendations
```

## API Functions

The script uses these `WorkflowMemory` methods:

### `clear_leads() -> int`
Removes all leads from memory, returns count deleted.

### `clear_campaigns() -> int`
Removes all campaigns from memory, returns count deleted.

### `clear_interactions() -> int`
Removes all interactions from memory, returns count deleted.

### `clear_recommendations() -> int`
Removes all recommendations from memory, returns count deleted.

### `clear_all_data() -> Dict[str, int]`
Removes all data from all collections, returns counts for each.

**Example:**
```python
from utils.memory import get_memory

memory = get_memory()

# Clear only leads
deleted_count = memory.clear_leads()
print(f"Deleted {deleted_count} leads")

# Clear all data
results = memory.clear_all_data()
print(f"Leads: {results['leads_deleted']}")
print(f"Campaigns: {results['campaigns_deleted']}")
print(f"Interactions: {results['interactions_deleted']}")
print(f"Recommendations: {results['recommendations_deleted']}")
```

## Important Notes

### Data is Permanently Deleted
- Cleared data **cannot be recovered**
- Make backups if needed before clearing
- Consider exporting prospects before deletion:
  ```powershell
  # Export before clearing
  python scripts\view_prospects.py --csv --json
  python scripts\clear_memory.py --leads
  ```

### Memory Location
- Default: `./data/chroma/`
- Can be changed via `WorkflowMemory(persist_directory="path")`

### Reset vs Clear
- `clear_*()` methods: Delete specific data, keep collections
- `reset_all()` method: Completely reset ChromaDB client (use with extreme caution)

## Error Handling

The script handles common errors:
- Empty collections (shows message, exits gracefully)
- Invalid confirmation input (treats as 'no')
- ChromaDB connection issues (shows error message)

## Exit Codes
- `0` - Success
- `1` - Error occurred

## Related Scripts
- `view_memory.py` - View memory statistics and contents
- `view_prospects.py` - View and export prospects
- `demo.py` - Run workflow (generates memory data)

---

**Remember:** Always use `--stats` first to see what will be deleted!
