import subprocess
import time
import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from typing import Dict, Optional, Tuple, Set

class MultiBrowserManager:
    def __init__(self):
        self.browsers = {}
        self.current_browser = None
        self.os_system = platform.system()
        
    def create_remote_browser(self, profile_name: str = "remote", remote_port: int = 9222):
        """Create browser with debugger address (existing Chrome instance)"""
        try:
            options = Options()
            options.debugger_address = f"localhost:{remote_port}"
            options.add_argument("--disable-logging")
            options.add_argument("--log-level=3")  # Suppress INFO, WARNING, ERROR
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=options)
            
            self.browsers[profile_name] = {
                'driver': driver,
                'type': 'debug',
                'profile': profile_name,
                'remote_port': remote_port,
                'original_tabs': driver.window_handles.copy(),
                'current_tab_index': 0
            }
            
            print(f"Connected to Debug browser on port {remote_port}")
            return driver
            
        except Exception as e:
            print(f"Failed to connect to debug browser: {e}")
            return None
    
    def create_incognito_browser(self, profile_name: str, user_data_dir: str = None):
        """Create new incognito browser instance"""
        try:
            options = Options()
            options.add_argument("--incognito")
            
            if user_data_dir:
                options.add_argument(f"--user-data-dir={user_data_dir}")
            
            # Add other useful options
            options.add_argument("--no-default-browser-check")
            options.add_argument("--no-first-run")
            
            driver = webdriver.Chrome(options=options)
            
            self.browsers[profile_name] = {
                'driver': driver,
                'type': 'incognito',
                'profile': profile_name,
                'user_data_dir': user_data_dir,
                'original_tabs': driver.window_handles.copy(),
                'current_tab_index': 0
            }
            
            print(f"✅ Created incognito browser: {profile_name}")
            return driver
            
        except Exception as e:
            print(f"❌ Failed to create incognito browser {profile_name}: {e}")
            return None
    
    def create_normal_browser(self, profile_name: str, user_data_dir: str = None):
        """Create new incognito browser instance"""
        try:
            options = Options()
            
            if user_data_dir:
                options.add_argument(f"--user-data-dir={user_data_dir}")
            
            # Add other useful options
            options.add_argument("--no-default-browser-check")
            options.add_argument("--no-first-run")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-first-run --no-service-autorun --password-store=basic")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-notifications")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            prefs = {
                "credentials_enable_service": False,   # disable Chrome credential service
                "profile.password_manager_enabled": False,  # disable password manager
                "profile.default_content_setting_values.notifications": 2                
            }
            options.add_experimental_option("prefs", prefs)            
            
            driver = webdriver.Chrome(options=options)
            
            self.browsers[profile_name] = {
                'driver': driver,
                'type': 'incognito',
                'profile': profile_name,
                'user_data_dir': user_data_dir,
                'original_tabs': driver.window_handles.copy(),
                'current_tab_index': 0
            }
            
            print(f"✅ Created normal browser: {profile_name}")
            return driver
            
        except Exception as e:
            print(f"❌ Failed to create incognito browser {profile_name}: {e}")
            return None    

    def bring_to_foreground(self, browser_name: str, force_restore: bool = True):
        """Bring specific browser window to foreground"""
        if browser_name not in self.browsers:
            print(f"❌ Browser {browser_name} not found")
            return False
        
        try:
            driver = self.browsers[browser_name]['driver']
            
            # Method 1: Try Selenium window operations (skip if already maximized)
            if force_restore:
                try:
                    # Check current window state first
                    current_size = driver.get_window_size()
                    if current_size['width'] <= 10 or current_size['height'] <= 10:
                        # Window appears minimized, try to restore
                        print("🔧 Window appears minimized, attempting Selenium restore...")
                        driver.maximize_window()
                        time.sleep(0.5)
                    else:
                        # Window is already visible, just ensure it's maximized
                        print("🔧 Window appears visible, ensuring maximized...")
                        try:
                            driver.maximize_window()
                        except Exception as max_error:
                            print(f"⚠️ Maximize skipped (already maximized)")
                        time.sleep(0.3)
                except Exception as e:
                    print(f"⚠️ Selenium window operations failed: {e}")
            
            # Method 2: OS-specific commands
            if self.os_system == "Windows":
                # Bring Chrome to foreground
                subprocess.run([
                    'powershell', '-Command',
                    'Add-Type -AssemblyName Microsoft.VisualBasic; '
                    '[Microsoft.VisualBasic.Interaction]::AppActivate("Chrome")'
                ], capture_output=True)
                
            elif self.os_system == "Darwin":  # macOS
                subprocess.run([
                    'osascript', '-e',
                    'tell application "Google Chrome" to activate'
                ], capture_output=True)
                
            elif self.os_system == "Linux":
                subprocess.run(['wmctrl', '-a', 'Chrome'], capture_output=True)

            # Method 3: Additional Selenium actions to ensure visibility
            try:
                # Get current window size to check if minimized
                size = driver.get_window_size()
                if size['width'] == 0 or size['height'] == 0:
                    print("⚠️ Window appears minimized, attempting to restore...")
                    driver.set_window_size(1920, 1080)
                    driver.set_window_position(0, 0)
                
                # Try to interact with the page to ensure it's active
                driver.execute_script("window.focus();")
                
                # Final maximize to ensure visibility
                driver.maximize_window()
                
            except Exception as e:
                print(f"⚠️ Additional restoration attempts failed: {e}")
            
            # Longer delay for minimized windows
            time.sleep(1.0)

            # # Small delay to ensure focus
            # time.sleep(0.5)
            
            self.current_browser = browser_name
            print(f"🔥 Brought {browser_name} to foreground")
            return True
            
        except Exception as e:
            print(f"❌ Failed to bring {browser_name} to foreground: {e}")
            return False
    
    def check_window_state(self, browser_name: str):
        """Check if browser window is minimized or hidden"""
        if browser_name not in self.browsers:
            return "not_found"
        
        try:
            driver = self.browsers[browser_name]['driver']
            
            # Get window size and position
            size = driver.get_window_size()
            position = driver.get_window_position()
            
            # Check if window appears minimized (size is 0 or very small)
            if size['width'] <= 10 or size['height'] <= 10:
                return "minimized"
            
            # Check if window is off-screen
            if position['x'] < -1000 or position['y'] < -1000:
                return "off_screen"
            
            # Try to get window state via JavaScript
            try:
                visibility = driver.execute_script("return document.visibilityState;")
                if visibility == "hidden":
                    return "hidden"
            except:
                pass
            
            return "visible"
            
        except Exception as e:
            print(f"⚠️ Could not check window state for {browser_name}: {e}")
            return "unknown"
    
    def ensure_window_visible(self, browser_name: str):
        """Ensure window is visible before bringing to foreground"""
        state = self.check_window_state(browser_name)
        print(f"Window state for {browser_name}: {state}")
        
        if state in ["minimized", "hidden", "off_screen"]:
            print(f"🔧 Restoring {browser_name} from {state} state...")
            return self.bring_to_foreground(browser_name, force_restore=True)
        elif state == "visible":
            return self.bring_to_foreground(browser_name, force_restore=False)
        else:
            # Unknown state, try force restore
            return self.bring_to_foreground(browser_name, force_restore=True)

    def switch_to_browser(self, browser_name: str, bring_to_focus: bool = True):
        """Switch context to specific browser"""
        if browser_name not in self.browsers:
            print(f"❌ Browser {browser_name} not found")
            return None
        
        if bring_to_focus:
            self.bring_to_foreground(browser_name)
        
        self.current_browser = browser_name
        return self.browsers[browser_name]['driver']
    
    def load_url_in_browser(self, browser_name: str, url: str, new_tab: bool = False):
        """Load URL in specific browser"""
        if browser_name not in self.browsers:
            print(f"❌ Browser {browser_name} not found")
            return False
        
        driver = self.browsers[browser_name]['driver']
        
        try:
            if new_tab:
                # Open in new tab
                driver.execute_script(f"window.open('{url}', '_blank');")
                # Switch to new tab
                driver.switch_to.window(driver.window_handles[-1])
                self.browsers[browser_name]['current_tab_index'] = len(driver.window_handles) - 1
            else:
                # Load in current tab
                driver.get(url)
            
            driver.maximize_window()
            driver.refresh()
            print(f"✅ Loaded {url} in {browser_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load {url} in {browser_name}: {e}")
            return False
    
    def get_current_driver(self):
        """Get currently active browser driver"""
        if self.current_browser:
            return self.browsers[self.current_browser]['driver']
        return None
    
    def list_browsers(self):
        """List all managed browsers"""
        print("\n=== Managed Browsers ===")
        for name, info in self.browsers.items():
            driver = info['driver']
            current_url = driver.current_url
            tab_count = len(driver.window_handles)
            status = "🔥 ACTIVE" if name == self.current_browser else "💤 INACTIVE"
            
            print(f"{status} {name} ({info['type']})")
            print(f"   URL: {current_url}")
            print(f"   Tabs: {tab_count}")

    def get_top_windows_with_urls(self, count: int = 2):
        """Get top N windows across all browsers with their URLs"""
        all_windows = []
        
        for browser_name, browser_info in self.browsers.items():
            driver = browser_info['driver']
            current_window = driver.current_window_handle
            
            try:
                # Get all window handles for this browser
                window_handles = driver.window_handles
                
                for i, window_handle in enumerate(window_handles):
                    try:
                        # Switch to each window to get its URL
                        driver.switch_to.window(window_handle)
                        url = driver.current_url
                        title = driver.title
                        
                        window_info = {
                            'browser_name': browser_name,
                            'browser_type': browser_info['type'],
                            'window_handle': window_handle,
                            'window_index': i,
                            'url': url,
                            'title': title,
                            'is_active': window_handle == current_window
                        }
                        all_windows.append(window_info)
                        
                    except Exception as e:
                        print(f"⚠️ Could not get info for window {window_handle} in {browser_name}: {e}")
                
                # Restore original window
                driver.switch_to.window(current_window)
                
            except Exception as e:
                print(f"⚠️ Could not process browser {browser_name}: {e}")
        
        # Sort by browser order and window index (top windows first)
        all_windows.sort(key=lambda x: (x['browser_name'], x['window_index']))
        
        # Return top N windows
        top_windows = all_windows[:count]
        
        print(f"\n=== Top {count} Windows ===")
        for i, window in enumerate(top_windows, 1):
            status = "🔥 ACTIVE" if window['is_active'] else "💤 INACTIVE"
            print(f"{i}. {status} {window['browser_name']} ({window['browser_type']}) - Tab {window['window_index']}")
            print(f"   URL: {window['url']}")
            print(f"   Title: {window['title'][:60]}...")
            print()
        
        return top_windows
    
    def get_all_urls_by_browser(self):
        """Get all URLs organized by browser"""
        browser_urls = {}
        
        for browser_name, browser_info in self.browsers.items():
            driver = browser_info['driver']
            current_window = driver.current_window_handle
            
            browser_urls[browser_name] = {
                'type': browser_info['type'],
                'windows': []
            }
            
            try:
                window_handles = driver.window_handles
                
                for i, window_handle in enumerate(window_handles):
                    try:
                        driver.switch_to.window(window_handle)
                        url = driver.current_url
                        title = driver.title
                        
                        browser_urls[browser_name]['windows'].append({
                            'index': i,
                            'handle': window_handle,
                            'url': url,
                            'title': title,
                            'is_current': window_handle == current_window
                        })
                    except Exception as e:
                        browser_urls[browser_name]['windows'].append({
                            'index': i,
                            'handle': window_handle,
                            'url': f"ERROR: {e}",
                            'title': "Could not access",
                            'is_current': False
                        })
                
                # Restore original window
                driver.switch_to.window(current_window)
                
            except Exception as e:
                print(f"⚠️ Could not process browser {browser_name}: {e}")
        
        return browser_urls
    
    def switch_to_window_by_url(self, url_part: str, exact_match: bool = False):
        """Switch to first window containing specific URL"""
        for browser_name, browser_info in self.browsers.items():
            driver = browser_info['driver']
            current_window = driver.current_window_handle
            
            try:
                for window_handle in driver.window_handles:
                    driver.switch_to.window(window_handle)
                    current_url = driver.current_url
                    
                    match_found = False
                    if exact_match:
                        match_found = current_url == url_part
                    else:
                        match_found = url_part.lower() in current_url.lower()
                    
                    if match_found:
                        print(f"✅ Switched to {browser_name} window with URL: {current_url}")
                        self.current_browser = browser_name
                        return {
                            'browser_name': browser_name,
                            'window_handle': window_handle,
                            'url': current_url,
                            'driver': driver
                        }
                
                # Restore original window if no match
                driver.switch_to.window(current_window)
                
            except Exception as e:
                print(f"⚠️ Error searching in {browser_name}: {e}")
        
        print(f"❌ No window found with URL containing: {url_part}")
        return None

    def wait_for_new_window(self, timeout: int = 10, check_interval: float = 0.5) -> Tuple[Optional[str], Optional[webdriver.Chrome], Optional[str]]:
        """
        Wait for and return details of any new window that appears across all browsers
        
        Args:
            timeout: Maximum time to wait in seconds
            check_interval: How often to check for new windows in seconds
            
        Returns:
            Tuple of (profile_name, driver, window_handle) or (None, None, None) if timeout
        """
        print(f"🔍 Waiting for new window (timeout: {timeout}s)...")
        
        # Capture initial window state for all browsers
        initial_windows = {}
        for profile_name, browser_info in self.browsers.items():
            try:
                driver = browser_info['driver']
                initial_windows[profile_name] = set(driver.window_handles)
                print(f"   📋 {profile_name}: {len(initial_windows[profile_name])} initial windows")
            except Exception as e:
                print(f"⚠️ Could not get initial windows for {profile_name}: {e}")
                initial_windows[profile_name] = set()
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check each browser for new windows
            for profile_name, browser_info in self.browsers.items():
                try:
                    driver = browser_info['driver']
                    current_windows = set(driver.window_handles)
                    new_windows = current_windows - initial_windows[profile_name]
                    
                    if new_windows:
                        new_handle = list(new_windows)[0]  # Get first new window
                        
                        # Switch to the new window to get its details
                        original_window = driver.current_window_handle
                        driver.switch_to.window(new_handle)
                        
                        try:
                            new_url = driver.current_url
                            new_title = driver.title
                            print(f"🎉 New window detected in {profile_name}!")
                            print(f"   🔗 URL: {new_url}")
                            print(f"   📄 Title: {new_title}")
                        except Exception as e:
                            print(f"🎉 New window detected in {profile_name}! (could not get details: {e})")
                        
                        # Set this browser as current
                        self.current_browser = profile_name
                        
                        return profile_name, driver, new_handle
                        
                except Exception as e:
                    print(f"⚠️ Error checking {profile_name} for new windows: {e}")
            
            time.sleep(check_interval)
        
        print(f"⏰ Timeout: No new window detected within {timeout} seconds")
        return None, None, None

    def find_window_by_url(self, target_url: str, partial_match: bool = True) -> Tuple[Optional[str], Optional[webdriver.Chrome], Optional[str]]:
        """
        Find window containing specific URL across all browsers
        
        Args:
            target_url: URL or URL part to search for
            partial_match: If True, match partial URLs; if False, exact match only
            
        Returns:
            Tuple of (profile_name, driver, window_handle) or (None, None, None) if not found
        """
        print(f"🔍 Searching for window with URL {'containing' if partial_match else 'matching'}: {target_url}")
        
        for profile_name, browser_info in self.browsers.items():
            driver = browser_info['driver']
            original_window = driver.current_window_handle
            
            try:
                for window_handle in driver.window_handles:
                    driver.switch_to.window(window_handle)
                    current_url = driver.current_url
                    
                    match_found = False
                    if partial_match:
                        match_found = target_url.lower() in current_url.lower()
                    else:
                        match_found = target_url.lower() == current_url.lower()
                    
                    if match_found:
                        print(f"✅ Found window in {profile_name}: {current_url}")
                        self.current_browser = profile_name
                        return profile_name, driver, window_handle
                
                # Restore original window if no match in this browser
                driver.switch_to.window(original_window)
                
            except Exception as e:
                print(f"⚠️ Error searching {profile_name}: {e}")
                try:
                    driver.switch_to.window(original_window)
                except:
                    pass
        
        print(f"❌ No window found with URL {'containing' if partial_match else 'matching'}: {target_url}")
        return None, None, None

    def wait_for_window_with_url(self, target_url: str, timeout: int = 10, partial_match: bool = True, check_interval: float = 0.5) -> Tuple[Optional[str], Optional[webdriver.Chrome], Optional[str]]:
        """
        Wait for a window with specific URL to appear
        
        Args:
            target_url: URL or URL part to wait for
            timeout: Maximum time to wait in seconds
            partial_match: If True, match partial URLs; if False, exact match only
            check_interval: How often to check in seconds
            
        Returns:
            Tuple of (profile_name, driver, window_handle) or (None, None, None) if timeout
        """
        print(f"🔍 Waiting for window with URL {'containing' if partial_match else 'matching'}: {target_url}")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self.find_window_by_url(target_url, partial_match)
            if result[0] is not None:  # Found a match
                return result
            
            time.sleep(check_interval)
        
        print(f"⏰ Timeout: No window with URL {'containing' if partial_match else 'matching'} '{target_url}' found within {timeout} seconds")
        return None, None, None

    def close_browser(self, browser_name: str):
        """Close specific browser"""
        if browser_name in self.browsers:
            try:
                self.browsers[browser_name]['driver'].quit()
                del self.browsers[browser_name]
                if self.current_browser == browser_name:
                    self.current_browser = None
                print(f"✅ Closed {browser_name}")
            except Exception as e:
                print(f"❌ Error closing {browser_name}: {e}")
    
    def close_all(self):
        """Close all browsers"""
        for browser_name in list(self.browsers.keys()):
            self.close_browser(browser_name)