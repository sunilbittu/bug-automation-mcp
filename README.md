# Bug Automation MCP Server

An MCP (Model Context Protocol) server that integrates Google Sheets, GitLab, and Playwright to automate bug reproduction, fixing, and verification workflows.

## Features

- **Google Sheets Integration**: Read and update bug information from spreadsheets
- **Playwright Automation**: Reproduce bugs and verify fixes automatically
- **GitLab Integration**: Commit fixes and create merge requests
- **End-to-end Workflow**: From bug reading to fix verification and code commit

## Architecture

```
Bug Tracking (Google Sheets)
        ↓
Read Bug Details
        ↓
Reproduce with Playwright
        ↓
Fix Code
        ↓
Verify Fix with Playwright
        ↓
Commit to GitLab
        ↓
Update Status in Google Sheets
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Google Sheets API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API
4. Create a Service Account
5. Download the credentials JSON file and save as `credentials.json`
6. Share your Google Sheet with the service account email

### 3. Configure GitLab

1. Create a GitLab personal access token with `api`, `read_repository`, and `write_repository` scopes
2. Note your project ID from your GitLab project settings

### 4. Set Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp env.example .env
# Edit .env with your actual values
```

### 5. Prepare Google Sheet Format

Your Google Sheet should have these columns:
- **Column A**: Bug ID
- **Column B**: Title
- **Column C**: Description
- **Column D**: Reproduction Steps
- **Column E**: Expected Result
- **Column F**: Actual Result
- **Column G**: Status
- **Column H**: Priority
- **Column I**: Notes (optional)

Example:
```
| ID   | Title              | Description        | Steps                | Expected    | Actual      | Status | Priority |
|------|--------------------|--------------------|----------------------|-------------|-------------|--------|----------|
| BUG-001 | Login fails     | Cannot login       | 1. Go to /login...   | Success     | Error 500   | Open   | High     |
```

## Running the Server

```bash
python server.py
```

## Usage with Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "bug-automation": {
      "command": "python",
      "args": ["/path/to/bug-automation-mcp/server.py"],
      "env": {
        "GOOGLE_SHEET_ID": "your_sheet_id",
        "GOOGLE_CREDENTIALS_PATH": "/path/to/credentials.json",
        "GITLAB_URL": "https://gitlab.com",
        "GITLAB_TOKEN": "your_token",
        "GITLAB_PROJECT_ID": "your_project_id"
      }
    }
  }
}
```

## Available Tools

### 1. read_bug
Read a specific bug from Google Sheets by ID.

```python
read_bug(bug_id="BUG-001")
```

### 2. reproduce_bug
Use Playwright to reproduce a bug based on steps.

```python
reproduce_bug(
    bug_id="BUG-001",
    url="https://yourapp.com",
    steps=[
        "Navigate to login page",
        "Enter username",
        "Click submit",
        "Observe error"
    ]
)
```

### 3. verify_fix
Verify that a bug fix works using Playwright.

```python
verify_fix(
    bug_id="BUG-001",
    url="https://yourapp.com",
    verification_steps=[
        "Navigate to login page",
        "Enter credentials",
        "Verify successful login"
    ]
)
```

### 4. commit_fix
Commit bug fix to GitLab repository.

```python
commit_fix(
    bug_id="BUG-001",
    branch_name="fix/bug-001",
    files=[
        {
            "path": "src/login.js",
            "content": "// fixed code here"
        }
    ],
    commit_message="Fix: Login authentication error"
)
```

### 5. update_bug_status
Update bug status in Google Sheets.

```python
update_bug_status(
    bug_id="BUG-001",
    status="Fixed",
    notes="Fixed authentication logic"
)
```

## Available Resources

- `sheets://bugs/active` - List of active bugs
- `sheets://bugs/pending` - List of pending bugs

## Example Workflow

Using Claude with this MCP server:

```
User: "Read bug BUG-001 and try to reproduce it"

Claude will:
1. Call read_bug("BUG-001") to get bug details
2. Parse the reproduction steps
3. Call reproduce_bug() with the URL and steps
4. Return screenshots and results

User: "The bug is confirmed. Let me fix it and commit."

Claude will:
1. Help you write the fix
2. Call commit_fix() to push to GitLab
3. Call verify_fix() to test the fix
4. Call update_bug_status() to mark as fixed
```

## Advanced Playwright Step Parsing

For more sophisticated bug reproduction, you can extend the step parsing logic to understand:

- **Navigation**: "Go to URL", "Click on X"
- **Input**: "Type X into Y", "Enter text"
- **Assertions**: "Verify X is visible", "Check error message"
- **Wait conditions**: "Wait for X to load"

Example enhancement:

```python
async def parse_and_execute_step(page: Page, step: str):
    step_lower = step.lower()
    
    if "navigate to" in step_lower or "go to" in step_lower:
        # Extract URL and navigate
        pass
    elif "click" in step_lower:
        # Extract selector and click
        selector = extract_selector(step)
        await page.click(selector)
    elif "type" in step_lower or "enter" in step_lower:
        # Extract text and selector
        pass
    elif "verify" in step_lower or "check" in step_lower:
        # Add assertion
        pass
```

## Security Notes

- Keep your `credentials.json` and `.env` files secure
- Never commit sensitive credentials to version control
- Use environment variables for production deployments
- Limit Google Sheet and GitLab access to necessary permissions only

## Troubleshooting

### Google Sheets Permission Error
- Ensure the service account email has been granted access to the sheet
- Verify the Sheet ID is correct

### GitLab Authentication Error
- Check your personal access token has required scopes
- Verify the GitLab URL and project ID

### Playwright Errors
- Run `playwright install` to ensure browsers are installed
- Check if the target website is accessible

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
