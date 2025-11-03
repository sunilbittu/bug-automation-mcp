# Bug Automation MCP - Quick Start Guide

## What This Does

This MCP (Model Context Protocol) server connects **Google Sheets**, **GitLab**, and **Playwright** to automate your bug workflow:

1. **Read bugs** from Google Sheets
2. **Reproduce bugs** automatically using Playwright
3. **Verify fixes** with automated testing
4. **Commit fixes** to GitLab with merge requests
5. **Update status** back in Google Sheets

## 5-Minute Setup

### Prerequisites
- Python 3.8+
- Google Cloud account (free)
- GitLab account (free)
- Claude Desktop (to use with Claude)

### Quick Install

```bash
# 1. Navigate to the project
cd bug-automation-mcp

# 2. Run the setup wizard
python setup.py

# 3. Follow the prompts to configure everything
```

The setup wizard will:
- ✓ Install all dependencies
- ✓ Help you configure Google Sheets API
- ✓ Set up GitLab integration
- ✓ Create your .env file
- ✓ Generate Claude Desktop config

### Manual Setup (Alternative)

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Copy and edit environment file
cp env.example .env
nano .env  # Add your credentials

# Test the setup
python example.py
```

## Configuration Files

### 1. Google Sheets (`credentials.json`)
- Go to https://console.cloud.google.com/
- Create project → Enable Sheets API → Create Service Account
- Download credentials → Save as `credentials.json`

### 2. Environment Variables (`.env`)
```bash
GOOGLE_SHEET_ID=your_spreadsheet_id
GOOGLE_CREDENTIALS_PATH=credentials.json
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=your_token
GITLAB_PROJECT_ID=your_project_id
```

### 3. Google Sheet Format
Create a sheet named "Bugs" with these columns:

| Column | Field | Example |
|--------|-------|---------|
| A | Bug ID | BUG-001 |
| B | Title | Login fails |
| C | Description | Cannot login with valid credentials |
| D | Steps | 1. Go to /login\n2. Enter credentials\n3. Click Login |
| E | Expected | User should be logged in |
| F | Actual | Error 500 appears |
| G | Status | Open |
| H | Priority | High |

## Using with Claude

### Add to Claude Desktop

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bug-automation": {
      "command": "python",
      "args": ["/full/path/to/bug-automation-mcp/server.py"],
      "env": {
        "GOOGLE_SHEET_ID": "your_sheet_id",
        "GOOGLE_CREDENTIALS_PATH": "/full/path/to/credentials.json",
        "GITLAB_URL": "https://gitlab.com",
        "GITLAB_TOKEN": "your_token",
        "GITLAB_PROJECT_ID": "your_project"
      }
    }
  }
}
```

### Example Usage

**Reproduce a Bug:**
```
You: "Read bug BUG-001 from my sheet and try to reproduce it"

Claude: [Uses MCP tools to read and reproduce]
"I've reproduced BUG-001. The login button is indeed not responding. 
Screenshots attached showing the issue."
```

**Fix and Verify:**
```
You: "I've fixed the bug. Please verify it works now."

Claude: [Uses verify_fix tool]
"Fix verified! The login button now works correctly. 
Should I commit this to GitLab?"
```

**Commit Fix:**
```
You: "Yes, commit to a new branch and create an MR"

Claude: [Uses commit_fix tool]
"Committed to branch 'fix/bug-001'. 
Created MR #123: https://gitlab.com/your/project/-/merge_requests/123
Updated bug status to 'Fixed' in your Google Sheet."
```

## Common Workflows

### Workflow 1: Daily Bug Triage
```
You: "Show me all open bugs from my sheet"
Claude: [Lists bugs with priorities]

You: "Let's reproduce the high-priority ones"
Claude: [Reproduces each bug, provides screenshots]
```

### Workflow 2: Fix Verification
```
You: "I just pushed a fix for BUG-042. Verify it on staging"
Claude: [Runs verification tests]
"Verification passed! All steps completed successfully."
```

### Workflow 3: Automated Testing
```
You: "For each fixed bug in my sheet, verify the fix still works"
Claude: [Iterates through fixed bugs, verifies each]
"Verified 5 bugs, all still working correctly."
```

## File Structure

```
bug-automation-mcp/
├── server.py              # Main MCP server
├── playwright_parser.py   # Natural language step parser
├── example.py            # Usage examples
├── setup.py              # Setup wizard
├── requirements.txt      # Python dependencies
├── env.example          # Environment template
├── README.md            # Full documentation
├── WORKFLOW.md          # Detailed workflows
└── package.json         # NPM metadata
```

## Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "Playwright browser not found"
```bash
playwright install chromium
```

### "Permission denied" for Google Sheets
- Ensure service account email has access to your sheet
- Share sheet with: your-service-account@project.iam.gserviceaccount.com

### "GitLab authentication failed"
- Check your token has 'api' scope
- Verify GITLAB_URL and GITLAB_PROJECT_ID

## Advanced Features

### Natural Language Steps
Write reproduction steps in plain English:
- "Navigate to https://example.com"
- "Click the Login button"
- "Type 'admin' into username field"
- "Verify welcome message is displayed"

### Custom Step Syntax
Support for complex interactions:
- "Wait for spinner to disappear"
- "Hover over the menu"
- "Select 'United States' from country dropdown"
- "Scroll to the footer"

### Parallel Execution
Process multiple bugs simultaneously for faster triage.

### Screenshots & Evidence
Automatic screenshot capture at key steps for documentation.

## Next Steps

1. ✅ Complete setup using `python setup.py`
2. ✅ Create your bug tracking sheet
3. ✅ Add a sample bug
4. ✅ Test reproduction with `python example.py`
5. ✅ Add to Claude Desktop config
6. ✅ Start automating your bug workflow!

## Resources

- **Full Documentation**: See README.md
- **Workflow Guide**: See WORKFLOW.md
- **Support**: Open an issue on GitLab/GitHub
- **MCP Docs**: https://modelcontextprotocol.io

## Tips for Success

1. **Write Clear Steps**: Be specific in reproduction steps
2. **Use Selectors**: Include element IDs/classes when possible
3. **Test Incrementally**: Start with simple bugs
4. **Monitor Results**: Check screenshots to verify automation
5. **Keep Sheet Updated**: Always reflect current bug status
6. **Branch Per Bug**: Create separate branches for each fix
7. **Document Fixes**: Add notes about what was changed

---

**Ready to automate your bug workflow?**

Run `python setup.py` to get started! 🚀
