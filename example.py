#!/usr/bin/env python3
"""
Example test script demonstrating the bug automation workflow
"""

import asyncio
import os
from dotenv import load_dotenv

# This would normally be done through MCP, but here's a direct example
from playwright.async_api import async_playwright
from playwright_parser import PlaywrightStepParser


async def example_bug_reproduction():
    """
    Example: Reproduce a login bug
    """
    print("=== Bug Reproduction Example ===\n")
    
    # Sample bug from Google Sheets
    bug = {
        'id': 'BUG-001',
        'title': 'Login button not working',
        'description': 'Users cannot log in when clicking the login button',
        'steps': [
            'Navigate to https://example.com/login',
            'Enter "testuser" into username field',
            'Enter "password123" into password field',
            'Click on "Login" button',
            'Verify error message is displayed'
        ],
        'expected': 'User should be logged in',
        'actual': 'Error message appears',
        'status': 'Open',
        'priority': 'High'
    }
    
    print(f"Bug ID: {bug['id']}")
    print(f"Title: {bug['title']}")
    print(f"Description: {bug['description']}")
    print(f"\nReproduction Steps:")
    for i, step in enumerate(bug['steps'], 1):
        print(f"  {i}. {step}")
    print()
    
    # Initialize Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set to True for headless
        page = await browser.new_page()
        
        # Initialize step parser
        parser = PlaywrightStepParser(page)
        
        # Execute reproduction steps
        print("Executing reproduction steps...\n")
        results = []
        
        for i, step in enumerate(bug['steps'], 1):
            print(f"Step {i}: {step}")
            result = await parser.execute_step(step)
            results.append(result)
            
            if result['success']:
                print(f"  ✓ {result['message']}")
            else:
                print(f"  ✗ {result['message']}")
            
            # Small delay between steps
            await asyncio.sleep(1)
        
        print("\n=== Reproduction Complete ===")
        print(f"Total steps: {len(results)}")
        print(f"Successful: {sum(1 for r in results if r['success'])}")
        print(f"Failed: {sum(1 for r in results if not r['success'])}")
        
        # Keep browser open for inspection
        print("\nBrowser will close in 5 seconds...")
        await asyncio.sleep(5)
        
        await browser.close()


async def example_fix_verification():
    """
    Example: Verify a bug fix
    """
    print("\n=== Fix Verification Example ===\n")
    
    verification_steps = [
        'Navigate to https://example.com/login',
        'Enter "testuser" into username field',
        'Enter "password123" into password field',
        'Click on "Login" button',
        'Wait for dashboard to load',
        'Verify "Welcome" is visible',
        'Verify no error message is displayed'
    ]
    
    print("Verification Steps:")
    for i, step in enumerate(verification_steps, 1):
        print(f"  {i}. {step}")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        parser = PlaywrightStepParser(page)
        
        print("Executing verification steps...\n")
        all_passed = True
        
        for i, step in enumerate(verification_steps, 1):
            print(f"Step {i}: {step}")
            result = await parser.execute_step(step)
            
            if result['success']:
                print(f"  ✓ {result['message']}")
            else:
                print(f"  ✗ {result['message']}")
                all_passed = False
            
            await asyncio.sleep(1)
        
        print("\n=== Verification Complete ===")
        if all_passed:
            print("✓ All verification steps passed! Fix is working.")
        else:
            print("✗ Some verification steps failed. Fix needs more work.")
        
        print("\nBrowser will close in 5 seconds...")
        await asyncio.sleep(5)
        
        await browser.close()


async def example_natural_language_steps():
    """
    Example: Various natural language step formats
    """
    print("\n=== Natural Language Step Examples ===\n")
    
    example_steps = [
        # Navigation
        'Go to https://example.com',
        'Navigate to the homepage',
        'Visit https://google.com',
        
        # Clicking
        'Click on the "Submit" button',
        'Click the login link',
        'Press the #search-button',
        'Tap on "Next"',
        
        # Typing/Input
        'Type "hello world" into the search field',
        'Enter "user@example.com" into email',
        'Fill "John Doe" into the name input',
        
        # Selection
        'Select "United States" from the country dropdown',
        
        # Verification
        'Verify "Welcome" is visible',
        'Check that error message contains "Invalid"',
        'Ensure the submit button is displayed',
        'Confirm "Success" text appears',
        
        # Waiting
        'Wait for the modal to load',
        'Wait 2 seconds',
        'Wait for #spinner to disappear',
        
        # Scrolling
        'Scroll to the bottom',
        'Scroll to the footer',
        'Scroll to the "Contact Us" section',
        
        # Hovering
        'Hover over the menu button',
        'Hover on the profile icon',
    ]
    
    print("Supported step formats:\n")
    for step in example_steps:
        print(f"  • {step}")
    
    print("\nThese steps can be used in your Google Sheets to describe bug reproduction!")


async def main():
    """Run examples"""
    load_dotenv()
    
    print("Bug Automation MCP - Examples\n")
    print("Choose an example to run:")
    print("1. Bug Reproduction")
    print("2. Fix Verification")
    print("3. Natural Language Steps Reference")
    print("0. Run all examples")
    
    choice = input("\nEnter choice (0-3): ").strip()
    
    if choice == "1":
        await example_bug_reproduction()
    elif choice == "2":
        await example_fix_verification()
    elif choice == "3":
        await example_natural_language_steps()
    elif choice == "0":
        await example_natural_language_steps()
        print("\n" + "="*60 + "\n")
        # Note: The other examples would need a real website to test against
        print("Other examples require a real website to test.")
        print("Update the URLs in the example functions to test against your site.")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
