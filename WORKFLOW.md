# Bug Automation Workflow Guide

## Complete End-to-End Workflow

### Phase 1: Bug Discovery & Documentation (Google Sheets)

```
QA Team → Discovers Bug → Documents in Google Sheets
                            ↓
                    Bug Details Include:
                    - ID (BUG-XXX)
                    - Title
                    - Description
                    - Reproduction Steps
                    - Expected vs Actual Results
                    - Status (Open)
                    - Priority
```

### Phase 2: Automated Bug Reproduction (Playwright)

```
Claude (via MCP) → Reads Bug from Sheets
                   ↓
            Parses Reproduction Steps
                   ↓
            Launches Playwright Browser
                   ↓
            Executes Steps One-by-One
                   ↓
            Captures Screenshots & Logs
                   ↓
            Confirms Bug Exists
                   ↓
            Updates Status → "Confirmed"
```

### Phase 3: Bug Analysis & Fix Development

```
Developer/Claude → Analyzes Bug Report
                   ↓
            Reviews Error Logs
                   ↓
            Identifies Root Cause
                   ↓
            Develops Fix
                   ↓
            Local Testing
```

### Phase 4: Automated Fix Verification (Playwright)

```
Fix Ready → Claude Verifies with Playwright
            ↓
     Executes Verification Steps
            ↓
     Compares with Expected Behavior
            ↓
     Captures Success Screenshots
            ↓
     Verification Passes? 
     ├─ Yes → Proceed to Commit
     └─ No → Back to Development
```

### Phase 5: Code Commit & MR Creation (GitLab)

```
Verified Fix → Create Feature Branch
               ↓
        Commit Changes
               ↓
        Push to GitLab
               ↓
        Create Merge Request
               ↓
        Link MR to Bug ID
               ↓
        Request Code Review
```

### Phase 6: Status Update (Google Sheets)

```
Commit Success → Update Bug Status
                 ↓
          Status → "Fixed"
                 ↓
          Add Notes (MR Link)
                 ↓
          Update Timestamp
                 ↓
          Notify Stakeholders
```

## Integration Examples

### Example 1: Simple Bug Flow

**Google Sheet Entry:**
```
ID: BUG-042
Title: Search returns no results
Steps: 
1. Navigate to https://myapp.com
2. Click on search bar
3. Type "test query"
4. Click search button
5. Verify results are displayed
Expected: Search results appear
Actual: "No results found" message
Status: Open
```

**Claude Conversation:**
```
User: "Check if BUG-042 can be reproduced"

Claude: I'll read the bug details and attempt to reproduce it.
[Calls read_bug("BUG-042")]
[Calls reproduce_bug(...)]

Claude: "I've successfully reproduced BUG-042. The search 
        functionality is indeed returning no results for valid 
        queries. Screenshots attached. Would you like me to 
        analyze the issue?"

User: "Yes, what could be causing it?"

Claude: "Based on the reproduction, this appears to be a 
        frontend issue with the search query not being properly 
        sent to the backend. Let me check the search component code."

User: "I've fixed the search handler. Can you verify the fix?"

Claude: [Calls verify_fix(...)]
        "Fix verified successfully! The search now returns results 
        as expected. Should I commit this to GitLab?"

User: "Yes, create a branch and commit"

Claude: [Calls commit_fix(...)]
        "Committed fix to branch 'fix/bug-042' and created MR #123.
        Updated bug status to 'Fixed' in Google Sheets."
```

### Example 2: Complex Multi-Step Bug

**Scenario:** Login flow with OAuth fails

**Steps:**
```
1. Navigate to https://myapp.com/login
2. Click "Login with Google"
3. Wait for OAuth popup
4. Enter credentials in popup
5. Click "Allow" button
6. Wait for redirect
7. Verify user is logged in
8. Check that profile picture is displayed
```

**Playwright Parser Handles:**
- Window/tab switching for OAuth popup
- Waiting for redirects
- Handling async authentication
- Verifying final logged-in state

### Example 3: Visual Regression Testing

**Bug:** Button appears in wrong color

**Reproduction Steps:**
```
1. Navigate to dashboard
2. Verify submit button is green
3. Hover over submit button
4. Verify button turns dark green
5. Take screenshot for comparison
```

**Parser Capabilities:**
- Color verification
- Hover state testing
- Screenshot comparison
- Visual diff reporting

## Advanced Configuration

### Custom Step Syntax in Google Sheets

You can use these formats in your reproduction steps:

```
Navigation:
- "Go to {URL}"
- "Navigate to {URL}"
- "Visit {URL}"
- "Open {URL}"

Clicking:
- "Click on '{element}'"
- "Click the {element}"
- "Press '{button}'"
- "Tap on {element}"

Input:
- "Type '{text}' into {field}"
- "Enter '{text}' into {field}"
- "Fill '{text}' into {field}"

Selection:
- "Select '{option}' from {dropdown}"
- "Choose '{option}' from {dropdown}"

Verification:
- "Verify '{text}' is visible"
- "Check that {element} is displayed"
- "Ensure {element} contains '{text}'"
- "Confirm {condition}"

Waiting:
- "Wait for {element} to appear"
- "Wait {N} seconds"
- "Wait until {element} is visible"

Scrolling:
- "Scroll to {element}"
- "Scroll to the bottom"
- "Scroll to the top"
```

### Environment-Specific Configuration

Create multiple environment configs:

**.env.development:**
```bash
GOOGLE_SHEET_ID=dev_sheet_id
GITLAB_PROJECT_ID=dev_project_id
TEST_BASE_URL=https://dev.myapp.com
```

**.env.staging:**
```bash
GOOGLE_SHEET_ID=staging_sheet_id
GITLAB_PROJECT_ID=staging_project_id
TEST_BASE_URL=https://staging.myapp.com
```

**.env.production:**
```bash
GOOGLE_SHEET_ID=prod_sheet_id
GITLAB_PROJECT_ID=prod_project_id
TEST_BASE_URL=https://myapp.com
```

### GitLab CI/CD Integration

Add to `.gitlab-ci.yml`:

```yaml
test:bug-verification:
  stage: test
  script:
    - pip install -r requirements.txt
    - playwright install chromium
    - python -c "
      import asyncio
      from server import BugAutomationMCP
      
      async def verify_all_fixed_bugs():
          mcp = BugAutomationMCP()
          await mcp.initialize_sheets()
          await mcp.initialize_playwright()
          
          # Get all bugs with status 'Fixed'
          # Run verification for each
          # Report results
      
      asyncio.run(verify_all_fixed_bugs())
      "
  only:
    - merge_requests
```

## Monitoring & Reporting

### Daily Bug Report

Generate automated reports:

```python
async def generate_daily_report():
    """Generate daily bug status report"""
    # Get all bugs from sheets
    # Categorize by status
    # Generate summary
    # Send to team via email/slack
    
    report = {
        'date': today,
        'new_bugs': count_new,
        'fixed_bugs': count_fixed,
        'in_progress': count_in_progress,
        'verified': count_verified,
        'critical': count_critical
    }
    
    return report
```

### Success Metrics

Track these KPIs:
- Time to reproduce bug (automated)
- Time to verify fix (automated)
- Bug fix turnaround time
- Automation success rate
- Manual intervention required

## Troubleshooting Common Issues

### Issue: Playwright can't find elements

**Solution:** 
- Add explicit waits: `Wait for {element} to appear`
- Use more specific selectors
- Check if element is in iframe
- Verify element timing (appears after JS load)

### Issue: OAuth/SSO fails in headless mode

**Solution:**
```python
# In server.py, modify browser launch:
self.browser = await self.playwright.chromium.launch(
    headless=False,  # Use headed mode for OAuth
    args=['--disable-blink-features=AutomationControlled']
)
```

### Issue: GitLab rate limiting

**Solution:**
- Implement request throttling
- Use GitLab webhook triggers instead of polling
- Cache common queries

### Issue: Google Sheets API quota exceeded

**Solution:**
- Implement caching layer
- Batch read operations
- Use exponential backoff
- Request quota increase

## Best Practices

1. **Clear Bug Documentation**: Write detailed reproduction steps
2. **Atomic Steps**: Each step should be a single action
3. **Deterministic Tests**: Avoid flaky tests with proper waits
4. **Screenshots**: Always capture state at key moments
5. **Idempotent Fixes**: Ensure fixes can be reapplied safely
6. **Branch Naming**: Use consistent naming (fix/BUG-XXX)
7. **Commit Messages**: Reference bug ID in commits
8. **Status Updates**: Keep Google Sheets current
9. **Regular Cleanup**: Archive old/closed bugs
10. **Team Communication**: Share automation results

## Security Considerations

1. **Credentials**: Store in environment variables, never commit
2. **Service Account**: Use minimal required permissions
3. **GitLab Token**: Use project-specific tokens
4. **Network**: Run Playwright in isolated environment
5. **Logs**: Sanitize sensitive data from logs
6. **Access Control**: Limit who can trigger automation
7. **Audit Trail**: Log all automation actions
8. **Secrets Rotation**: Regularly rotate credentials

## Scaling Considerations

### Parallel Execution

Run multiple reproductions in parallel:

```python
async def reproduce_multiple_bugs(bug_ids: list):
    tasks = []
    for bug_id in bug_ids:
        tasks.append(reproduce_bug(bug_id))
    
    results = await asyncio.gather(*tasks)
    return results
```

### Distributed Testing

Use Playwright Grid for distributed execution:

```yaml
# docker-compose.yml
version: '3'
services:
  playwright-1:
    image: mcr.microsoft.com/playwright:latest
  playwright-2:
    image: mcr.microsoft.com/playwright:latest
  playwright-3:
    image: mcr.microsoft.com/playwright:latest
```

## Future Enhancements

- [ ] AI-powered step generation from bug descriptions
- [ ] Automatic root cause analysis
- [ ] Suggested fix generation
- [ ] Visual regression testing integration
- [ ] Performance metrics collection
- [ ] Mobile device emulation
- [ ] Cross-browser testing
- [ ] Slack/Teams integration for notifications
- [ ] Dashboard for bug metrics visualization
- [ ] ML-based flaky test detection
