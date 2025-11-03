#!/usr/bin/env python3
"""
Setup script for Bug Automation MCP
Guides user through initial configuration
"""

import os
import sys
import json
import subprocess
from pathlib import Path


class SetupWizard:
    def __init__(self):
        self.config = {}
        self.project_root = Path(__file__).parent
    
    def print_header(self, text):
        """Print a formatted header"""
        print("\n" + "="*60)
        print(f"  {text}")
        print("="*60 + "\n")
    
    def print_step(self, step_num, total_steps, description):
        """Print a step indicator"""
        print(f"\n[Step {step_num}/{total_steps}] {description}")
        print("-" * 60)
    
    def prompt(self, question, default=None, required=True):
        """Prompt user for input"""
        if default:
            question = f"{question} [{default}]"
        question += ": "
        
        while True:
            response = input(question).strip()
            
            if not response and default:
                return default
            elif not response and required:
                print("This field is required. Please enter a value.")
                continue
            else:
                return response
    
    def confirm(self, question):
        """Ask for yes/no confirmation"""
        response = input(f"{question} (y/n): ").strip().lower()
        return response in ['y', 'yes']
    
    def install_dependencies(self):
        """Install Python dependencies"""
        self.print_step(1, 7, "Installing Dependencies")
        
        print("Installing Python packages...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                check=True,
                cwd=self.project_root
            )
            print("✓ Python packages installed successfully")
        except subprocess.CalledProcessError:
            print("✗ Failed to install Python packages")
            if not self.confirm("Continue anyway?"):
                sys.exit(1)
        
        print("\nInstalling Playwright browsers...")
        try:
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                check=True,
                cwd=self.project_root
            )
            print("✓ Playwright browser installed successfully")
        except subprocess.CalledProcessError:
            print("✗ Failed to install Playwright browser")
            if not self.confirm("Continue anyway?"):
                sys.exit(1)
    
    def setup_google_sheets(self):
        """Configure Google Sheets integration"""
        self.print_step(2, 7, "Google Sheets Configuration")
        
        print("To use Google Sheets, you need:")
        print("1. A Google Cloud Project with Sheets API enabled")
        print("2. A Service Account with credentials JSON file")
        print("3. The service account email added to your spreadsheet\n")
        
        if not self.confirm("Have you completed these steps?"):
            print("\nPlease complete these steps:")
            print("1. Go to https://console.cloud.google.com/")
            print("2. Create a project")
            print("3. Enable Google Sheets API")
            print("4. Create a Service Account")
            print("5. Download credentials JSON")
            print("\nRun this setup again when ready.")
            sys.exit(0)
        
        creds_path = self.prompt(
            "Path to Google credentials JSON file",
            default="credentials.json"
        )
        
        # Check if file exists
        if not os.path.exists(creds_path):
            print(f"✗ File not found: {creds_path}")
            if not self.confirm("Continue anyway?"):
                sys.exit(1)
        else:
            print(f"✓ Found credentials file: {creds_path}")
        
        sheet_id = self.prompt("Google Sheet ID")
        
        print("\nGoogle Sheets setup information:")
        print(f"Your service account email should have access to the sheet.")
        print(f"Sheet URL: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
        
        self.config['GOOGLE_CREDENTIALS_PATH'] = creds_path
        self.config['GOOGLE_SHEET_ID'] = sheet_id
    
    def setup_gitlab(self):
        """Configure GitLab integration"""
        self.print_step(3, 7, "GitLab Configuration")
        
        print("To use GitLab, you need:")
        print("1. A GitLab account (gitlab.com or self-hosted)")
        print("2. A personal access token with 'api' scope")
        print("3. Your project ID\n")
        
        gitlab_url = self.prompt(
            "GitLab URL",
            default="https://gitlab.com"
        )
        
        print("\nTo create a personal access token:")
        print(f"1. Go to {gitlab_url}/-/profile/personal_access_tokens")
        print("2. Create a token with 'api' scope")
        print("3. Copy the token (you won't see it again!)\n")
        
        gitlab_token = self.prompt("GitLab Personal Access Token")
        
        print("\nTo find your project ID:")
        print("1. Go to your GitLab project")
        print("2. Look in the project settings or overview")
        print("3. It's a numeric ID like '12345678'\n")
        
        project_id = self.prompt("GitLab Project ID")
        
        self.config['GITLAB_URL'] = gitlab_url
        self.config['GITLAB_TOKEN'] = gitlab_token
        self.config['GITLAB_PROJECT_ID'] = project_id
        
        print("✓ GitLab configured")
    
    def setup_spreadsheet_template(self):
        """Guide user to set up spreadsheet"""
        self.print_step(4, 7, "Spreadsheet Template Setup")
        
        print("Your Google Sheet should have these columns:")
        print("\nColumn | Field")
        print("-------|------------------")
        print("A      | Bug ID")
        print("B      | Title")
        print("C      | Description")
        print("D      | Reproduction Steps")
        print("E      | Expected Result")
        print("F      | Actual Result")
        print("G      | Status")
        print("H      | Priority")
        print("I      | Notes (optional)")
        
        print("\nExample row:")
        print("BUG-001 | Login fails | Cannot login | 1. Go to /login... | Success | Error 500 | Open | High")
        
        if self.confirm("\nCreate a sample sheet template?"):
            self.create_sample_sheet_data()
    
    def create_sample_sheet_data(self):
        """Create sample data file"""
        sample_data = """Bug ID,Title,Description,Reproduction Steps,Expected Result,Actual Result,Status,Priority
BUG-001,Login button not working,Users cannot log in,"1. Navigate to https://example.com/login
2. Enter username
3. Enter password
4. Click Login button",User should be logged in,Error message appears,Open,High
BUG-002,Search returns no results,Search functionality broken,"1. Go to homepage
2. Click search bar
3. Type 'test query'
4. Click search button",Search results displayed,No results found message,Open,Medium
BUG-003,Profile image not uploading,Cannot upload profile picture,"1. Go to profile settings
2. Click upload image
3. Select image file
4. Click save",Image should be saved,Error: File too large,Open,Low"""
        
        with open(self.project_root / 'sample_bugs.csv', 'w') as f:
            f.write(sample_data)
        
        print("✓ Created sample_bugs.csv")
        print("  Import this into your Google Sheet to get started")
    
    def configure_playwright(self):
        """Configure Playwright options"""
        self.print_step(5, 7, "Playwright Configuration")
        
        headless = self.confirm("Run Playwright in headless mode? (no browser window)")
        browser = self.prompt("Browser to use", default="chromium")
        
        self.config['PLAYWRIGHT_HEADLESS'] = 'true' if headless else 'false'
        self.config['PLAYWRIGHT_BROWSER'] = browser
        
        print("✓ Playwright configured")
    
    def create_env_file(self):
        """Create .env file with configuration"""
        self.print_step(6, 7, "Creating Environment File")
        
        env_path = self.project_root / '.env'
        
        if env_path.exists():
            if not self.confirm(".env file already exists. Overwrite?"):
                print("Skipping .env creation")
                return
        
        with open(env_path, 'w') as f:
            f.write("# Bug Automation MCP Configuration\n")
            f.write("# Generated by setup.py\n\n")
            
            for key, value in self.config.items():
                f.write(f"{key}={value}\n")
        
        print(f"✓ Created .env file at {env_path}")
        print("\n⚠️  IMPORTANT: Never commit .env file to version control!")
    
    def create_claude_config(self):
        """Create Claude Desktop configuration"""
        self.print_step(7, 7, "Claude Desktop Integration")
        
        if not self.confirm("Add to Claude Desktop config?"):
            print("Skipping Claude Desktop configuration")
            return
        
        # Determine Claude config path based on OS
        if sys.platform == "darwin":  # macOS
            config_dir = Path.home() / "Library" / "Application Support" / "Claude"
        elif sys.platform == "win32":  # Windows
            config_dir = Path.home() / "AppData" / "Roaming" / "Claude"
        else:  # Linux
            config_dir = Path.home() / ".config" / "claude"
        
        config_file = config_dir / "claude_desktop_config.json"
        
        mcp_config = {
            "bug-automation": {
                "command": sys.executable,
                "args": [str(self.project_root / "server.py")],
                "env": dict(self.config)
            }
        }
        
        if config_file.exists():
            print(f"Found existing config at: {config_file}")
            print("\nAdd this to your mcpServers section:")
        else:
            print(f"Create this file: {config_file}")
            print("\nWith this content:")
        
        print(json.dumps({"mcpServers": mcp_config}, indent=2))
        
        if self.confirm("\nSave configuration snippet to mcp_config.json?"):
            with open(self.project_root / 'mcp_config.json', 'w') as f:
                json.dump({"mcpServers": mcp_config}, f, indent=2)
            print("✓ Saved to mcp_config.json")
    
    def run(self):
        """Run the setup wizard"""
        self.print_header("Bug Automation MCP - Setup Wizard")
        
        print("This wizard will help you set up the Bug Automation MCP server.")
        print("You'll need to configure:")
        print("  • Python dependencies")
        print("  • Google Sheets API")
        print("  • GitLab integration")
        print("  • Playwright browser automation")
        print("  • Claude Desktop (optional)")
        
        if not self.confirm("\nReady to begin?"):
            print("Setup cancelled.")
            return
        
        try:
            self.install_dependencies()
            self.setup_google_sheets()
            self.setup_gitlab()
            self.setup_spreadsheet_template()
            self.configure_playwright()
            self.create_env_file()
            self.create_claude_config()
            
            self.print_header("Setup Complete!")
            
            print("✓ All configuration steps completed\n")
            print("Next steps:")
            print("1. Import sample_bugs.csv to your Google Sheet (if created)")
            print("2. Share the Google Sheet with your service account email")
            print("3. Add the MCP config to Claude Desktop (if desired)")
            print("4. Run: python server.py")
            print("\nFor usage examples, run: python example.py")
            print("\nFor detailed documentation, see:")
            print("  • README.md - Basic usage")
            print("  • WORKFLOW.md - Complete workflows")
            
        except KeyboardInterrupt:
            print("\n\nSetup interrupted by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n✗ Setup failed with error: {e}")
            if self.confirm("Show detailed error?"):
                import traceback
                traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    wizard = SetupWizard()
    wizard.run()
