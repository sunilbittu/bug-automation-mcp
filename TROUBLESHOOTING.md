# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### Issue: `pip install` fails
**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solutions:**
1. Update pip:
   ```bash
   python -m pip install --upgrade pip
   ```

2. Try with Python 3.8+:
   ```bash
   python3 --version  # Check version
   python3 -m pip install -r requirements.txt
   ```

3. Install in a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

#### Issue: Playwright installation fails
**Symptoms:**
```
ERROR: Failed to install browsers
```

**Solutions:**
1. Install browsers manually:
   ```bash
   python -m playwright install chromium
   ```

2. Check system dependencies (Linux):
   ```bash
   python -m playwright install-deps
   ```

3. Try different browser:
   ```bash
   python -m playwright install firefox
   ```

### Google Sheets Issues

#### Issue: "Permission denied" error
**Symptoms:**
```
HttpError 403: The caller does not have permission
```

**Solutions:**
1. Share the Google Sheet with your service account email:
   - Find email in credentials.json: `"client_email": "your-sa@project.iam.gserviceaccount.com"`
   - Open Google Sheet → Share → Add email → Set as Editor

2. Verify API is enabled:
   - Go to https://console.cloud.google.com/
   - APIs & Services → Library
   - Search "Google Sheets API"
   - Click "Enable"

3. Check credentials file path:
   ```bash
   # In .env file
   GOOGLE_CREDENTIALS_PATH=/full/path/to/credentials.json
   ```

#### Issue: "Spreadsheet not found"
**Symptoms:**
```
HttpError 404: Requested entity was not found
```

**Solutions:**
1. Verify Sheet ID in URL:
   ```
   https://docs.google.com/spreadsheets/d/[THIS_IS_THE_SHEET_ID]/edit
   ```

2. Check .env file:
   ```bash
   GOOGLE_SHEET_ID=correct_sheet_id_here
   ```

3. Ensure sheet is not deleted or moved

#### Issue: "Invalid credentials"
**Symptoms:**
```
Error: Could not load credentials from file
```

**Solutions:**
1. Re-download credentials.json from Google Cloud Console
2. Ensure JSON is valid (check with JSON validator)
3. Set correct path in .env:
   ```bash
   GOOGLE_CREDENTIALS_PATH=/absolute/path/to/credentials.json
   ```

### GitLab Issues

#### Issue: "401 Unauthorized"
**Symptoms:**
```
gitlab.exceptions.GitlabAuthenticationError: 401 Unauthorized
```

**Solutions:**
1. Check token validity:
   - Go to GitLab → Settings → Access Tokens
   - Ensure token hasn't expired
   - Create new token if needed

2. Verify token scopes:
   - Required scopes: `api`, `read_repository`, `write_repository`

3. Update .env file:
   ```bash
   GITLAB_TOKEN=your_new_token_here
   ```

#### Issue: "Project not found"
**Symptoms:**
```
GitlabGetError: 404 Project Not Found
```

**Solutions:**
1. Get correct project ID:
   - Go to GitLab project
   - Settings → General
   - Look for "Project ID"

2. Verify you have access:
   - Ensure you're a member of the project
   - Check project visibility (private projects need access)

3. Update .env:
   ```bash
   GITLAB_PROJECT_ID=12345678
   ```

#### Issue: "403 Forbidden"
**Symptoms:**
```
GitlabCreateError: 403 Forbidden
```

**Solutions:**
1. Check your role in the project:
   - Need at least "Developer" role to push code
   - "Reporter" role can only read

2. Verify branch protection:
   - Check if main branch is protected
   - MCP creates feature branches, so this usually isn't an issue

### Playwright Issues

#### Issue: "Browser not found"
**Symptoms:**
```
playwright._impl._api_types.Error: Executable doesn't exist
```

**Solutions:**
1. Install browsers:
   ```bash
   playwright install chromium
   ```

2. Check installation:
   ```bash
   playwright --version
   ```

3. Try system browser:
   ```python
   # In server.py
   browser = await self.playwright.chromium.launch(
       channel="chrome"  # Use system Chrome
   )
   ```

#### Issue: "Element not found"
**Symptoms:**
- Steps fail with "Could not find element"
- Screenshots show element exists

**Solutions:**
1. Add explicit wait:
   ```
   "Wait for login button to appear"
   "Click the login button"
   ```

2. Use better selector:
   ```
   Instead of: "Click button"
   Try: "Click the 'Submit' button"
   Or: "Click #submit-btn"
   ```

3. Check for dynamic content:
   ```
   "Wait 2 seconds"  # Let page load
   "Click the element"
   ```

4. Debug with headed mode:
   ```python
   # In server.py, change:
   self.browser = await self.playwright.chromium.launch(headless=False)
   ```

#### Issue: "Timeout waiting for element"
**Symptoms:**
```
TimeoutError: Timeout 30000ms exceeded
```

**Solutions:**
1. Increase timeout:
   ```python
   # In playwright_parser.py
   await self.page.wait_for_selector(selector, timeout=60000)  # 60 seconds
   ```

2. Check if element is in iframe:
   ```python
   # Look for iframe and switch to it
   frame = page.frame_locator("iframe#myframe")
   await frame.locator("button").click()
   ```

3. Verify element actually appears:
   - Run in headed mode to watch
   - Check network conditions
   - Verify page loads completely

#### Issue: "Navigation failed"
**Symptoms:**
```
Error: net::ERR_CONNECTION_REFUSED
```

**Solutions:**
1. Check URL is correct:
   - Verify protocol (https:// not http://)
   - Check domain spelling

2. Test URL manually in browser

3. Check if site requires authentication:
   - Add login steps first
   - Handle cookies/sessions

### MCP Server Issues

#### Issue: "Module not found"
**Symptoms:**
```
ModuleNotFoundError: No module named 'mcp'
```

**Solutions:**
1. Install all requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Check Python version:
   ```bash
   python --version  # Should be 3.8+
   ```

#### Issue: "Server not responding"
**Symptoms:**
- Claude says "Tool not available"
- No response from MCP server

**Solutions:**
1. Check server is running:
   ```bash
   ps aux | grep server.py
   ```

2. Restart server:
   ```bash
   pkill -f server.py
   python server.py
   ```

3. Check Claude Desktop config:
   ```json
   {
     "mcpServers": {
       "bug-automation": {
         "command": "python",
         "args": ["/full/path/to/server.py"],
         "env": { /* ... */ }
       }
     }
   }
   ```

4. View server logs:
   - Check terminal where server is running
   - Look for error messages

### Step Parsing Issues

#### Issue: Steps not executing correctly
**Symptoms:**
- Parser says "Could not parse step"
- Wrong action performed

**Solutions:**
1. Use clearer language:
   ```
   ❌ "Hit the thing"
   ✓ "Click the 'Submit' button"
   ```

2. Add quotes for text:
   ```
   ✓ "Type 'username' into email field"
   ✓ "Click on 'Login' button"
   ```

3. Be specific about selectors:
   ```
   ✓ "Click #submit-button"
   ✓ "Click .login-btn"
   ```

4. Test step-by-step:
   ```python
   # In example.py
   result = await parser.execute_step("Your step here")
   print(result)
   ```

### Environment Issues

#### Issue: ".env file not found"
**Symptoms:**
```
Environment variable not set: GOOGLE_SHEET_ID
```

**Solutions:**
1. Create .env file:
   ```bash
   cp env.example .env
   ```

2. Edit with your values:
   ```bash
   nano .env  # or use any text editor
   ```

3. Verify file location:
   ```bash
   ls -la .env  # Should be in project root
   ```

4. Load environment manually:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

### Performance Issues

#### Issue: Bug reproduction is slow
**Symptoms:**
- Takes minutes per bug
- Tests timeout

**Solutions:**
1. Use headless mode:
   ```python
   browser = await playwright.chromium.launch(headless=True)
   ```

2. Reduce wait times:
   - Remove unnecessary "Wait X seconds" steps
   - Use specific element waits

3. Optimize selectors:
   - Use IDs instead of text when possible
   - Avoid complex CSS selectors

4. Run in parallel:
   ```python
   # For multiple bugs
   tasks = [reproduce_bug(bug_id) for bug_id in bug_ids]
   results = await asyncio.gather(*tasks)
   ```

### Data Issues

#### Issue: Bug data not updating
**Symptoms:**
- Changes don't appear in Sheet
- Old data returned

**Solutions:**
1. Check Sheet range:
   ```python
   # In server.py, verify range is correct
   range_name = "Bugs!A2:H"  # Adjust as needed
   ```

2. Clear cache:
   - Google Sheets API caches data
   - Wait a few seconds and retry

3. Verify write permissions:
   - Service account needs Editor role
   - Not just Viewer

4. Check for locked cells:
   - Ensure cells aren't protected
   - Check Sheet permissions

## Debugging Tips

### Enable Verbose Logging

```python
# Add to server.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Capture More Screenshots

```python
# In playwright_parser.py, after each action:
await self.page.screenshot(path=f'debug_{step_num}.png')
```

### Test Components Individually

```python
# Test Google Sheets only
python -c "from server import BugAutomationMCP; import asyncio; mcp = BugAutomationMCP(); asyncio.run(mcp.initialize_sheets())"

# Test GitLab only
python -c "from server import BugAutomationMCP; import asyncio; mcp = BugAutomationMCP(); asyncio.run(mcp.initialize_gitlab())"

# Test Playwright only
python -c "from playwright.async_api import async_playwright; import asyncio; asyncio.run(async_playwright().start())"
```

### Use Example Script

```bash
# Run examples to test each component
python example.py
```

### Check Dependencies

```bash
pip list | grep mcp
pip list | grep playwright
pip list | grep google
pip list | grep gitlab
```

## Getting Help

### Information to Provide

When asking for help, include:
1. Error message (full traceback)
2. Python version: `python --version`
3. OS: Windows/Mac/Linux
4. Steps to reproduce
5. Relevant .env variables (redact secrets!)
6. Screenshots if UI-related

### Useful Commands

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Check Playwright
playwright --version

# Test Google Sheets connection
python -c "from googleapiclient.discovery import build; print('Google API client works')"

# Test GitLab connection
python -c "import gitlab; print('GitLab library works')"
```

### Reset Everything

If all else fails:
```bash
# 1. Remove virtual environment
rm -rf venv/

# 2. Reinstall
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 3. Reconfigure
python setup.py
```

## Still Having Issues?

1. **Check documentation**: Review README.md and WORKFLOW.md
2. **Run examples**: `python example.py` to test components
3. **Review logs**: Check server output for clues
4. **Test manually**: Try actions manually first
5. **Simplify**: Start with simplest case and build up

---

**Remember**: Most issues are configuration-related. Double-check your credentials and environment variables first!
