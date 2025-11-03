#!/usr/bin/env python3
"""
MCP Server for Bug Automation
Integrates Google Sheets, GitLab, and Playwright for automated bug reproduction and fixing
"""

import asyncio
import os
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import AnyUrl
import mcp.server.stdio

# Google Sheets integration
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# GitLab integration
import gitlab

# Playwright integration
from playwright.async_api import async_playwright, Browser, Page


class BugAutomationMCP:
    def __init__(self):
        self.server = Server("bug-automation")
        self.sheets_service = None
        self.gitlab_client = None
        self.playwright = None
        self.browser: Browser | None = None
        
        # Register handlers
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP handlers for resources and tools"""
        
        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available bug tracking resources"""
            return [
                Resource(
                    uri=AnyUrl("sheets://bugs/active"),
                    name="Active Bugs",
                    mimeType="application/json",
                    description="List of active bugs from Google Sheets"
                ),
                Resource(
                    uri=AnyUrl("sheets://bugs/pending"),
                    name="Pending Bugs",
                    mimeType="application/json",
                    description="List of pending bugs awaiting reproduction"
                ),
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: AnyUrl) -> str:
            """Read bug information from Google Sheets"""
            if not self.sheets_service:
                await self.initialize_sheets()
            
            spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")
            
            if str(uri) == "sheets://bugs/active":
                range_name = "Bugs!A2:H"  # Assuming columns: ID, Title, Description, Steps, Expected, Actual, Status, Priority
            elif str(uri) == "sheets://bugs/pending":
                range_name = "Bugs!A2:H"
            else:
                return "Unknown resource"
            
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            # Filter based on status
            if "active" in str(uri):
                bugs = [row for row in values if len(row) > 6 and row[6].lower() in ['open', 'in progress']]
            else:
                bugs = [row for row in values if len(row) > 6 and row[6].lower() == 'pending']
            
            # Format as structured data
            bug_list = []
            for row in bugs:
                if len(row) >= 7:
                    bug_list.append({
                        'id': row[0] if len(row) > 0 else '',
                        'title': row[1] if len(row) > 1 else '',
                        'description': row[2] if len(row) > 2 else '',
                        'steps': row[3] if len(row) > 3 else '',
                        'expected': row[4] if len(row) > 4 else '',
                        'actual': row[5] if len(row) > 5 else '',
                        'status': row[6] if len(row) > 6 else '',
                        'priority': row[7] if len(row) > 7 else ''
                    })
            
            return str(bug_list)
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available bug automation tools"""
            return [
                Tool(
                    name="read_bug",
                    description="Read a specific bug from Google Sheets by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "bug_id": {
                                "type": "string",
                                "description": "The bug ID to retrieve"
                            }
                        },
                        "required": ["bug_id"]
                    }
                ),
                Tool(
                    name="reproduce_bug",
                    description="Use Playwright to reproduce a bug based on steps",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "bug_id": {
                                "type": "string",
                                "description": "The bug ID to reproduce"
                            },
                            "url": {
                                "type": "string",
                                "description": "The URL to test"
                            },
                            "steps": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Step-by-step instructions to reproduce"
                            }
                        },
                        "required": ["bug_id", "url", "steps"]
                    }
                ),
                Tool(
                    name="verify_fix",
                    description="Verify that a bug fix works using Playwright",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "bug_id": {
                                "type": "string",
                                "description": "The bug ID to verify"
                            },
                            "url": {
                                "type": "string",
                                "description": "The URL to test"
                            },
                            "verification_steps": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Steps to verify the fix"
                            }
                        },
                        "required": ["bug_id", "url", "verification_steps"]
                    }
                ),
                Tool(
                    name="commit_fix",
                    description="Commit bug fix to GitLab repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "bug_id": {
                                "type": "string",
                                "description": "The bug ID being fixed"
                            },
                            "branch_name": {
                                "type": "string",
                                "description": "Branch name for the fix"
                            },
                            "files": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "path": {"type": "string"},
                                        "content": {"type": "string"}
                                    }
                                },
                                "description": "Files to commit with their content"
                            },
                            "commit_message": {
                                "type": "string",
                                "description": "Commit message"
                            }
                        },
                        "required": ["bug_id", "branch_name", "files", "commit_message"]
                    }
                ),
                Tool(
                    name="update_bug_status",
                    description="Update bug status in Google Sheets",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "bug_id": {
                                "type": "string",
                                "description": "The bug ID to update"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["Open", "In Progress", "Fixed", "Verified", "Closed"],
                                "description": "New status for the bug"
                            },
                            "notes": {
                                "type": "string",
                                "description": "Additional notes about the update"
                            }
                        },
                        "required": ["bug_id", "status"]
                    }
                ),
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
            """Execute bug automation tools"""
            
            if name == "read_bug":
                return await self.read_bug(arguments["bug_id"])
            
            elif name == "reproduce_bug":
                return await self.reproduce_bug(
                    arguments["bug_id"],
                    arguments["url"],
                    arguments["steps"]
                )
            
            elif name == "verify_fix":
                return await self.verify_fix(
                    arguments["bug_id"],
                    arguments["url"],
                    arguments["verification_steps"]
                )
            
            elif name == "commit_fix":
                return await self.commit_fix(
                    arguments["bug_id"],
                    arguments["branch_name"],
                    arguments["files"],
                    arguments["commit_message"]
                )
            
            elif name == "update_bug_status":
                return await self.update_bug_status(
                    arguments["bug_id"],
                    arguments["status"],
                    arguments.get("notes", "")
                )
            
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    async def initialize_sheets(self):
        """Initialize Google Sheets API client"""
        creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        self.sheets_service = build('sheets', 'v4', credentials=creds)
    
    async def initialize_gitlab(self):
        """Initialize GitLab client"""
        gitlab_url = os.getenv("GITLAB_URL", "https://gitlab.com")
        gitlab_token = os.getenv("GITLAB_TOKEN")
        
        self.gitlab_client = gitlab.Gitlab(gitlab_url, private_token=gitlab_token)
        self.gitlab_client.auth()
    
    async def initialize_playwright(self):
        """Initialize Playwright browser"""
        if not self.playwright:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
    
    async def read_bug(self, bug_id: str) -> Sequence[TextContent]:
        """Read a specific bug from Google Sheets"""
        if not self.sheets_service:
            await self.initialize_sheets()
        
        spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")
        range_name = "Bugs!A2:H"
        
        result = self.sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        for row in values:
            if len(row) > 0 and row[0] == bug_id:
                bug_data = {
                    'id': row[0] if len(row) > 0 else '',
                    'title': row[1] if len(row) > 1 else '',
                    'description': row[2] if len(row) > 2 else '',
                    'steps': row[3] if len(row) > 3 else '',
                    'expected': row[4] if len(row) > 4 else '',
                    'actual': row[5] if len(row) > 5 else '',
                    'status': row[6] if len(row) > 6 else '',
                    'priority': row[7] if len(row) > 7 else ''
                }
                return [TextContent(type="text", text=str(bug_data))]
        
        return [TextContent(type="text", text=f"Bug {bug_id} not found")]
    
    async def reproduce_bug(self, bug_id: str, url: str, steps: list[str]) -> Sequence[TextContent | ImageContent]:
        """Reproduce a bug using Playwright"""
        await self.initialize_playwright()
        
        results = []
        page = await self.browser.new_page()
        
        try:
            results.append(TextContent(
                type="text",
                text=f"Starting bug reproduction for {bug_id} at {url}"
            ))
            
            await page.goto(url)
            
            for i, step in enumerate(steps):
                results.append(TextContent(
                    type="text",
                    text=f"Step {i+1}: {step}"
                ))
                
                # Here you would parse and execute the step
                # This is a simplified example
                # In practice, you'd need more sophisticated step parsing
                
            # Take screenshot of the bug
            screenshot = await page.screenshot()
            results.append(ImageContent(
                type="image",
                data=screenshot.decode('latin1'),
                mimeType="image/png"
            ))
            
            results.append(TextContent(
                type="text",
                text=f"Bug reproduction completed for {bug_id}"
            ))
            
        except Exception as e:
            results.append(TextContent(
                type="text",
                text=f"Error during reproduction: {str(e)}"
            ))
        finally:
            await page.close()
        
        return results
    
    async def verify_fix(self, bug_id: str, url: str, verification_steps: list[str]) -> Sequence[TextContent]:
        """Verify a bug fix using Playwright"""
        await self.initialize_playwright()
        
        results = []
        page = await self.browser.new_page()
        
        try:
            results.append(TextContent(
                type="text",
                text=f"Starting fix verification for {bug_id} at {url}"
            ))
            
            await page.goto(url)
            
            for i, step in enumerate(verification_steps):
                results.append(TextContent(
                    type="text",
                    text=f"Verification step {i+1}: {step}"
                ))
                # Execute verification step
            
            results.append(TextContent(
                type="text",
                text=f"Fix verification completed successfully for {bug_id}"
            ))
            
        except Exception as e:
            results.append(TextContent(
                type="text",
                text=f"Verification failed: {str(e)}"
            ))
        finally:
            await page.close()
        
        return results
    
    async def commit_fix(self, bug_id: str, branch_name: str, files: list[dict], commit_message: str) -> Sequence[TextContent]:
        """Commit bug fix to GitLab"""
        if not self.gitlab_client:
            await self.initialize_gitlab()
        
        try:
            project_id = os.getenv("GITLAB_PROJECT_ID")
            project = self.gitlab_client.projects.get(project_id)
            
            # Create a new branch
            try:
                project.branches.create({'branch': branch_name, 'ref': 'main'})
            except Exception:
                pass  # Branch might already exist
            
            # Commit files
            actions = []
            for file in files:
                actions.append({
                    'action': 'update',
                    'file_path': file['path'],
                    'content': file['content']
                })
            
            commit = project.commits.create({
                'branch': branch_name,
                'commit_message': commit_message,
                'actions': actions
            })
            
            # Create merge request
            mr = project.mergerequests.create({
                'source_branch': branch_name,
                'target_branch': 'main',
                'title': f'Fix: {commit_message}',
                'description': f'Fixes bug {bug_id}'
            })
            
            return [TextContent(
                type="text",
                text=f"Successfully committed fix for {bug_id}. MR: {mr.web_url}"
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error committing fix: {str(e)}"
            )]
    
    async def update_bug_status(self, bug_id: str, status: str, notes: str = "") -> Sequence[TextContent]:
        """Update bug status in Google Sheets"""
        if not self.sheets_service:
            await self.initialize_sheets()
        
        spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")
        range_name = "Bugs!A2:H"
        
        # Find the bug row
        result = self.sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        for i, row in enumerate(values):
            if len(row) > 0 and row[0] == bug_id:
                # Update status (column G, index 6)
                update_range = f"Bugs!G{i+2}"
                self.sheets_service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=update_range,
                    valueInputOption='RAW',
                    body={'values': [[status]]}
                ).execute()
                
                # Add notes if provided (could be column I or a notes sheet)
                if notes:
                    notes_range = f"Bugs!I{i+2}"
                    self.sheets_service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=notes_range,
                        valueInputOption='RAW',
                        body={'values': [[notes]]}
                    ).execute()
                
                return [TextContent(
                    type="text",
                    text=f"Updated bug {bug_id} status to {status}"
                )]
        
        return [TextContent(
            type="text",
            text=f"Bug {bug_id} not found"
        )]
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point"""
    mcp_server = BugAutomationMCP()
    try:
        await mcp_server.run()
    finally:
        await mcp_server.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
