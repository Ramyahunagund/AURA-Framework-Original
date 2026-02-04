from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from typing import Optional
from core.settings import GlobalState, framework_logger
import test_flows_common.test_flows_common as common
import os

class PlaywrightManager:
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.logs_path: Optional[str] = None

    def setup(self) -> Page:
        """Setup playwright, browser, context and page"""
        self.playwright = sync_playwright().start()
        target = getattr(GlobalState, 'target')
        if target in ['web_safari', 'mac_app', 'ios_app']:
            browser_type = 'webkit'
        elif target == 'web_firefox':
            browser_type = 'firefox'
        else:
            browser_type = 'chromium'
        
        launch_args = {"headless": GlobalState.headless}
        context_args = {
            "locale": GlobalState.language_code,
            "viewport": {"width": GlobalState.target_width, "height": GlobalState.target_height},
            "device_scale_factor": 2.0
        }

        collect_har = GlobalState.collect_logs in ['har', 'both']
        capture_video = GlobalState.collect_logs in ['video', 'both']

        if GlobalState.run_dir:
            self.logs_path = os.path.join(GlobalState.run_dir, "logs")
            os.makedirs(self.logs_path, exist_ok=True)

        if collect_har and self.logs_path:
            har_path = os.path.join(self.logs_path, f"{GlobalState.flow_name}_{GlobalState.timestamp}.har")
            context_args["record_har_path"] = har_path
            framework_logger.info(f"HAR logs collection enabled and will be saved to: {har_path}")

        if capture_video and self.logs_path:
            context_args["record_video_dir"] = self.logs_path
            context_args["record_video_size"] = {
                "width": GlobalState.target_width,
                "height": GlobalState.target_height
            }
            framework_logger.info(f"Video captures enabled and will be saved to: {self.logs_path}/*.webm")

        if hasattr(common, 'PROXY_URL') and common.PROXY_URL:
            launch_args["proxy"] = {"server": common.PROXY_URL}
            context_args["proxy"] = {"server": common.PROXY_URL}
            framework_logger.info(f"Proxy enabled: {common.PROXY_URL}")

        if browser_type == 'firefox':
            self.browser = self.playwright.firefox.launch(**launch_args)
        elif browser_type == 'webkit':
            self.browser = self.playwright.webkit.launch(**launch_args)
        else:
            self.browser = self.playwright.chromium.launch(**launch_args)
            
        self.context = self.browser.new_context(**context_args)
        self.page = self.context.new_page()
        
        return self.page
    
    def close(self):
        collect_logs = GlobalState.collect_logs
        collect_har = GlobalState.collect_logs in ['har', 'both']
        capture_video = GlobalState.collect_logs in ['video', 'both']

        if self.page:
            try:
                self.page.close()
            except Exception as e:
                framework_logger.warning(f"Error closing page: {e}")
            
        if self.context:
            try:
                self.context.close()      
                if collect_logs and self.logs_path and os.path.exists(self.logs_path):
                    if collect_har:
                        har_files = [f for f in os.listdir(self.logs_path) if f.endswith('.har')]
                        if har_files:
                            framework_logger.info(f"HAR logs successfully saved: {har_files}")
                        else:
                            framework_logger.warning(f"No HAR logs found in: {self.logs_path}")
                    if capture_video:
                        video_files = [f for f in os.listdir(self.logs_path) if f.endswith('.webm')]
                        if video_files:
                            framework_logger.info(f"Video captures successfully saved: {video_files}")
                        else:
                            framework_logger.warning(f"No video captures found in: {self.logs_path}")

            except Exception as e:
                framework_logger.warning(f"Error closing context: {e}")
                
        if self.browser:
            try:
                self.browser.close()
            except Exception as e:
                framework_logger.warning(f"Error closing browser: {e}")
                
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception as e:
                framework_logger.warning(f"Error stopping playwright: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self.setup()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()