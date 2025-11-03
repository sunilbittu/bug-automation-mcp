"""
Playwright Step Parser
Converts natural language steps into Playwright actions
"""

import re
from playwright.async_api import Page, expect


class PlaywrightStepParser:
    """Parse and execute natural language test steps"""
    
    def __init__(self, page: Page):
        self.page = page
    
    async def execute_step(self, step: str) -> dict:
        """
        Execute a natural language step and return results
        
        Returns:
            dict: {'success': bool, 'message': str, 'screenshot': bytes}
        """
        step_lower = step.lower().strip()
        
        try:
            # Navigation steps
            if any(keyword in step_lower for keyword in ['navigate to', 'go to', 'visit', 'open']):
                return await self._handle_navigation(step)
            
            # Click actions
            elif any(keyword in step_lower for keyword in ['click', 'press', 'tap']):
                return await self._handle_click(step)
            
            # Input/Type actions
            elif any(keyword in step_lower for keyword in ['type', 'enter', 'fill', 'input']):
                return await self._handle_input(step)
            
            # Select dropdown
            elif 'select' in step_lower and ('dropdown' in step_lower or 'from' in step_lower):
                return await self._handle_select(step)
            
            # Wait actions
            elif any(keyword in step_lower for keyword in ['wait for', 'wait until']):
                return await self._handle_wait(step)
            
            # Verification/Assertion steps
            elif any(keyword in step_lower for keyword in ['verify', 'check', 'assert', 'ensure', 'confirm']):
                return await self._handle_verification(step)
            
            # Scroll actions
            elif 'scroll' in step_lower:
                return await self._handle_scroll(step)
            
            # Hover actions
            elif 'hover' in step_lower:
                return await self._handle_hover(step)
            
            else:
                return {
                    'success': False,
                    'message': f'Unable to parse step: {step}',
                    'screenshot': None
                }
        
        except Exception as e:
            screenshot = await self.page.screenshot()
            return {
                'success': False,
                'message': f'Error executing step "{step}": {str(e)}',
                'screenshot': screenshot
            }
    
    async def _handle_navigation(self, step: str) -> dict:
        """Handle navigation steps"""
        # Extract URL from step
        url_pattern = r'https?://[^\s]+'
        match = re.search(url_pattern, step)
        
        if match:
            url = match.group(0)
        else:
            # Try to find URL after common keywords
            for keyword in ['to', 'visit', 'open']:
                if keyword in step.lower():
                    parts = step.lower().split(keyword)
                    if len(parts) > 1:
                        url = parts[1].strip()
                        if not url.startswith('http'):
                            url = 'https://' + url
                        break
            else:
                return {
                    'success': False,
                    'message': f'Could not extract URL from: {step}',
                    'screenshot': None
                }
        
        await self.page.goto(url)
        screenshot = await self.page.screenshot()
        
        return {
            'success': True,
            'message': f'Navigated to {url}',
            'screenshot': screenshot
        }
    
    async def _handle_click(self, step: str) -> dict:
        """Handle click actions"""
        selector = self._extract_selector(step)
        
        if not selector:
            return {
                'success': False,
                'message': f'Could not extract selector from: {step}',
                'screenshot': None
            }
        
        # Try different selector strategies
        element = await self._find_element(selector)
        
        if element:
            await element.click()
            screenshot = await self.page.screenshot()
            return {
                'success': True,
                'message': f'Clicked on {selector}',
                'screenshot': screenshot
            }
        else:
            screenshot = await self.page.screenshot()
            return {
                'success': False,
                'message': f'Could not find element: {selector}',
                'screenshot': screenshot
            }
    
    async def _handle_input(self, step: str) -> dict:
        """Handle input/typing actions"""
        # Extract text to type (usually in quotes)
        text_match = re.search(r'["\']([^"\']+)["\']', step)
        text = text_match.group(1) if text_match else ""
        
        # Extract selector
        selector = self._extract_selector(step)
        
        if not selector:
            return {
                'success': False,
                'message': f'Could not extract selector from: {step}',
                'screenshot': None
            }
        
        element = await self._find_element(selector)
        
        if element:
            await element.fill(text)
            screenshot = await self.page.screenshot()
            return {
                'success': True,
                'message': f'Entered "{text}" into {selector}',
                'screenshot': screenshot
            }
        else:
            screenshot = await self.page.screenshot()
            return {
                'success': False,
                'message': f'Could not find input element: {selector}',
                'screenshot': screenshot
            }
    
    async def _handle_select(self, step: str) -> dict:
        """Handle dropdown selection"""
        # Extract option value
        option_match = re.search(r'["\']([^"\']+)["\']', step)
        option = option_match.group(1) if option_match else ""
        
        selector = self._extract_selector(step)
        
        if not selector:
            return {
                'success': False,
                'message': f'Could not extract selector from: {step}',
                'screenshot': None
            }
        
        try:
            await self.page.select_option(selector, option)
            screenshot = await self.page.screenshot()
            return {
                'success': True,
                'message': f'Selected "{option}" from {selector}',
                'screenshot': screenshot
            }
        except Exception as e:
            screenshot = await self.page.screenshot()
            return {
                'success': False,
                'message': f'Could not select option: {str(e)}',
                'screenshot': screenshot
            }
    
    async def _handle_wait(self, step: str) -> dict:
        """Handle wait conditions"""
        selector = self._extract_selector(step)
        
        if not selector:
            # Wait for time
            time_match = re.search(r'(\d+)\s*(second|seconds|ms|millisecond)', step.lower())
            if time_match:
                duration = int(time_match.group(1))
                unit = time_match.group(2)
                
                if 'ms' in unit or 'millisecond' in unit:
                    await self.page.wait_for_timeout(duration)
                else:
                    await self.page.wait_for_timeout(duration * 1000)
                
                return {
                    'success': True,
                    'message': f'Waited for {duration} {unit}',
                    'screenshot': None
                }
        else:
            # Wait for element
            try:
                await self.page.wait_for_selector(selector, timeout=10000)
                return {
                    'success': True,
                    'message': f'Element {selector} appeared',
                    'screenshot': None
                }
            except Exception:
                return {
                    'success': False,
                    'message': f'Element {selector} did not appear',
                    'screenshot': await self.page.screenshot()
                }
    
    async def _handle_verification(self, step: str) -> dict:
        """Handle verification/assertion steps"""
        step_lower = step.lower()
        
        # Check if verifying visibility
        if 'visible' in step_lower or 'displayed' in step_lower or 'shown' in step_lower:
            selector = self._extract_selector(step)
            if selector:
                element = await self._find_element(selector)
                is_visible = await element.is_visible() if element else False
                
                screenshot = await self.page.screenshot()
                
                # Check if expecting NOT visible
                expecting_not_visible = any(word in step_lower for word in ['not', 'hidden', 'invisible'])
                
                if (is_visible and not expecting_not_visible) or (not is_visible and expecting_not_visible):
                    return {
                        'success': True,
                        'message': f'Verified {selector} visibility',
                        'screenshot': screenshot
                    }
                else:
                    return {
                        'success': False,
                        'message': f'Verification failed for {selector} visibility',
                        'screenshot': screenshot
                    }
        
        # Check if verifying text content
        elif 'contains' in step_lower or 'text' in step_lower or 'says' in step_lower:
            text_match = re.search(r'["\']([^"\']+)["\']', step)
            expected_text = text_match.group(1) if text_match else ""
            
            selector = self._extract_selector(step)
            
            if selector and expected_text:
                element = await self._find_element(selector)
                if element:
                    actual_text = await element.text_content()
                    screenshot = await self.page.screenshot()
                    
                    if expected_text.lower() in (actual_text or "").lower():
                        return {
                            'success': True,
                            'message': f'Verified text "{expected_text}" in {selector}',
                            'screenshot': screenshot
                        }
                    else:
                        return {
                            'success': False,
                            'message': f'Text verification failed. Expected "{expected_text}", got "{actual_text}"',
                            'screenshot': screenshot
                        }
        
        # Generic verification
        selector = self._extract_selector(step)
        if selector:
            element = await self._find_element(selector)
            screenshot = await self.page.screenshot()
            
            if element:
                return {
                    'success': True,
                    'message': f'Verified element {selector} exists',
                    'screenshot': screenshot
                }
            else:
                return {
                    'success': False,
                    'message': f'Element {selector} not found',
                    'screenshot': screenshot
                }
        
        return {
            'success': False,
            'message': f'Could not parse verification: {step}',
            'screenshot': await self.page.screenshot()
        }
    
    async def _handle_scroll(self, step: str) -> dict:
        """Handle scroll actions"""
        if 'bottom' in step.lower():
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            message = 'Scrolled to bottom'
        elif 'top' in step.lower():
            await self.page.evaluate('window.scrollTo(0, 0)')
            message = 'Scrolled to top'
        else:
            selector = self._extract_selector(step)
            if selector:
                element = await self._find_element(selector)
                if element:
                    await element.scroll_into_view_if_needed()
                    message = f'Scrolled to {selector}'
                else:
                    return {
                        'success': False,
                        'message': f'Element {selector} not found for scrolling',
                        'screenshot': await self.page.screenshot()
                    }
            else:
                await self.page.evaluate('window.scrollBy(0, 300)')
                message = 'Scrolled down'
        
        screenshot = await self.page.screenshot()
        return {
            'success': True,
            'message': message,
            'screenshot': screenshot
        }
    
    async def _handle_hover(self, step: str) -> dict:
        """Handle hover actions"""
        selector = self._extract_selector(step)
        
        if not selector:
            return {
                'success': False,
                'message': f'Could not extract selector from: {step}',
                'screenshot': None
            }
        
        element = await self._find_element(selector)
        
        if element:
            await element.hover()
            screenshot = await self.page.screenshot()
            return {
                'success': True,
                'message': f'Hovered over {selector}',
                'screenshot': screenshot
            }
        else:
            return {
                'success': False,
                'message': f'Could not find element: {selector}',
                'screenshot': await self.page.screenshot()
            }
    
    def _extract_selector(self, step: str) -> str:
        """Extract a CSS selector or text from a step"""
        # Try to find quoted text (likely a button label or element text)
        quote_match = re.search(r'["\']([^"\']+)["\']', step)
        if quote_match:
            text = quote_match.group(1)
            # Return text-based selector
            return f'text={text}'
        
        # Look for common UI elements
        for element_type in ['button', 'link', 'input', 'field', 'checkbox', 'radio']:
            if element_type in step.lower():
                # Extract the identifier after the element type
                pattern = f'{element_type}[\\s]+(called|labeled|named|with)[\\s]+["\']?([^"\'\\s]+)["\']?'
                match = re.search(pattern, step.lower())
                if match:
                    identifier = match.group(2)
                    return f'{element_type}:has-text("{identifier}")'
        
        # Look for IDs
        id_match = re.search(r'#([a-zA-Z0-9_-]+)', step)
        if id_match:
            return f'#{id_match.group(1)}'
        
        # Look for class names
        class_match = re.search(r'\.([a-zA-Z0-9_-]+)', step)
        if class_match:
            return f'.{class_match.group(1)}'
        
        # Try to find text after common prepositions
        for prep in ['on the', 'on', 'into the', 'into', 'with', 'at']:
            if f' {prep} ' in step.lower():
                parts = step.lower().split(f' {prep} ')
                if len(parts) > 1:
                    potential_selector = parts[1].strip().strip('"\'')
                    if potential_selector:
                        return f'text={potential_selector}'
        
        return ""
    
    async def _find_element(self, selector: str):
        """Find an element using various strategies"""
        try:
            # Try direct selector first
            element = self.page.locator(selector).first
            if await element.count() > 0:
                return element
        except Exception:
            pass
        
        # If selector is just text, try various text-based selectors
        if not any(char in selector for char in ['#', '.', '[', '>', ' ']):
            selectors_to_try = [
                f'button:has-text("{selector}")',
                f'a:has-text("{selector}")',
                f'text={selector}',
                f'[aria-label*="{selector}" i]',
                f'[placeholder*="{selector}" i]',
                f'[title*="{selector}" i]',
            ]
            
            for sel in selectors_to_try:
                try:
                    element = self.page.locator(sel).first
                    if await element.count() > 0:
                        return element
                except Exception:
                    continue
        
        return None
