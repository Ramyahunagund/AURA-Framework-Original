import base64
import json
import logging
import os
import pandas as pd
import re
import shutil
import time as time_module
import yaml


from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from selenium import webdriver  
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.action_chains import ActionChains   
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

from openai import AzureOpenAI

from config_loader        import load_config
config = load_config(r"config.yaml")

logger = logging.getLogger(__name__)

class YamlStepExecutor:
    """
    A flexible test step executor that can handle various action types
    and dynamic step configurations from YAML files.
    """
    
    def __init__(self, manager,  driver, metadata_filepath=None, page='instantink/Auth_controls'):
        self.current_page = None
        self.execution_log = []
        self.manager = manager

        self.driver = driver  
        self.control_map = {}
        self.metadatapath = metadata_filepath
        self.variables = {}
        self.metadata = {}

        self.metadata['auth_controls'] = 'auth_controls'
        self.metadata['hpsmart'] = 'hpsmart'
        self.metadata['instantink'] = 'instantink'
        self.metadata['oss'] = 'oss_emulator'
        self.metadata['emulate'] = 'oss_emulator'

        self.iframe_modules = ['billing']        
        
        if metadata_filepath: 
            self.load_json_metadata(page)  
    
    def load_yaml_file(self, file_path: str) -> Dict[str, Any]:
        """Load and parse YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"YAML file not found: {file_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {e}")
    
    def load_yaml_string(self, yaml_string: str) -> Dict[str, Any]:
        """Load and parse YAML from string."""
        try:
            data = yaml.safe_load(yaml_string)
            self.validate_yaml_structure(data)
            return data
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML string: {e}")
        
    def load_json_metadata(self, page):  
        """  
        Load the JSON metadata file into the control map.  
        :param json_file: Path to the JSON file.  
        """ 
        if not page:
            return
        
        base, file = page.split("/", 1)
        folder = self.metadata[base]
        json_file = os.path.join(self.metadatapath, folder, (file + '.json'))
        
        try:
            with open(json_file, 'r') as file:  
                self.control_map = json.load(file)
            logger.info(f"Loaded JSON metadata from {json_file}")  
        except FileNotFoundError:  
            logger.error(f"Error: JSON file '{json_file}' not found.")  
        except json.JSONDecodeError:  
            logger.error(f"Error: Failed to decode JSON file '{json_file}'.")  

    def get_control(self, name):  
        """  
        Get the control ID for the given name from the loaded JSON metadata.  
        :param name: The name or text of the control.  
        :return: Control ID if found, None otherwise.  
        """  
        for control in self.control_map["interactive_elements"]:  
            if control.get("text") == name or control.get("label_text") == name:  
                return control  

    def _click_control(self, control, multiple, timeout: int = 10):
        """
        Attempts to click a button based on metadata.
        Supports id, css, xpath, text, aria-label, name, etc.
        Falls back progressively until click succeeds.
        """
        result = True

        if not control or not isinstance(control, dict):
            return False

        strategies = [
            {"name": "id", "locator": (By.ID, control.get("id")) if control.get("id") else None},
            {"name": "name", "locator": (By.NAME, control.get("name")) if control.get("name") else None},
            {"name": "aria_label", "locator": (By.CSS_SELECTOR, f'[aria-label="{control.get("aria_label")}"]') if control.get("aria_label") else None},
            {"name": "data_testid", "locator": (By.CSS_SELECTOR, f'[data-testid="{control.get("data_testid")}"]') if control.get("data_testid") else None},
            {"name": "class_name", "locator": (By.CLASS_NAME, control.get("classes").split()[0]) if control.get("classes") else None},
            {"name": "partial_link_text", "locator": (By.PARTIAL_LINK_TEXT, control.get("text")) if control.get("tag_name") == "a" and control.get("text") else None}
        ]

        # All CSS selectors
        for css in control.get("css_selectors", []):
            strategies.append({"name": "css_selector", "locator": (By.CSS_SELECTOR, css)})

        # All XPath selectors
        for xp in control.get("xpath_selectors", []):
            strategies.append({"name": "xpath", "locator": (By.XPATH, xp)})

        clicked_any = False
        for strategy in strategies:
            if strategy["locator"] is None:
                continue

            logger.info(f"Trying strategy: {strategy['name']} with locator: {strategy['locator']}")
            try:            
                elements = WebDriverWait(self.driver, timeout).until(
                    # EC.element_to_be_clickable(strategy["locator"])
                    EC.presence_of_all_elements_located(strategy["locator"])                    
                )

                if not elements:
                    logger.debug("elements not found for clicking")

                for element in elements:
                    logger.debug(f"element - is_displayed({element.is_displayed()}), is_enabled({element.is_enabled()}), multiple({multiple})")
                    try:
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            clicked_any = True
                            logger.debug(f"element, {element['text']} is clicked")
                            if not multiple:
                                logger.debug("multiple is false, now breaking element loop")                            
                                break
                            else:
                                logger.debug("multiple is true, introducing delay before next click") 
                                self.do_sleep(0.25)
                    except (ElementClickInterceptedException, NoSuchElementException):
                        logger.warning(f"Error clicking element for {strategy['name']}: {e}")
                        clicked_any = False
                        continue  # skip problematic element
                    except Exception as e:
                        logger.error(f"Unexpected error clicking element for ----- {strategy['name']}: {e}")
                        clicked_any = False
                        continue
                    
                    #break the element loop if element is clicked
                    if clicked_any:
                        logger.debug("Breaking element loop")
                        result = True
                        break
                    
            except TimeoutException as e:
                logger.warning(f"Timeout waiting for elements with strategy {strategy['name']}: {e}")
                result = False
                continue  # try next strategy
            except Exception as e:
                logger.error(f"Unexpected error with strategy {strategy['name']}: {e}")
                result = False
                continue  # try next strategy                                    

            # Break the strategy loop if element is clicked
            if clicked_any:
                logger.debug("selector loop is terminated")
                result = True
                break

        return result

    def _try_click_element(self, element, strategy):  
        """  
        Attempts to click a single element and handles exceptions.  
    
        :param element: The WebElement to click  
        :param strategy: The strategy used to locate the element (for logging purposes)  
        :return: True if the click was successful, False otherwise  
        """  
        try:  
            if element.is_displayed() and element.is_enabled():  
                element.click() 
                return True  
        except StaleElementReferenceException: # (ElementClickInterceptedException, NoSuchElementException) as e:  
            logger.warning(f"Error clicking element for {strategy[0]}")  
        except Exception as e:  
            logger.error(f"Unexpected error clicking element for {strategy[0]}: {e}")  
        return False  

    def do_clicks(self, strategy, multiple, timeout, delay=0.10):
        """  
            Attempts to click one or more elements located by the given strategy.  
            
            :param strategy: Locator strategy (e.g., By.ID, By.CLASS_NAME, etc.)  
            :param multiple: Whether multiple elements should be clicked  
            :param timeout: Maximum time to wait for elements to become clickable  
            :return: True if at least one element was clicked, False otherwise  
            """          
        result = True
        clicked_any = False
        clicked_count = 0

        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located(strategy)                    
            )

            if not elements:
                logger.debug("elements not found for clicking")
                return False

            logger.info(f"Found {len(elements)} elements to click.")

            for element in elements:
                logger.debug(  
                    f"Element: is_displayed({element.is_displayed()}), "  
                    f"is_enabled({element.is_enabled()}), multiple({multiple}) "
                )

                if not self._try_click_element(element, strategy):
                    logger.warning(f"Failed to click element: {element}")  
                    continue  # Skip problematic elements

                clicked_count += 1
                clicked_any = True  
                logger.debug(f"Element clicked successfully, {clicked_count}")

                # If multiple clicks are not allowed, break after the first successful click  
                if not multiple:  
                    logger.debug("Multiple is False, breaking element loop.")  
                    break

                # Delay before clicking the next element (for multiple clicks)  
                logger.debug("Multiple is True, introducing delay before next click.")  
                self.do_sleep(delay)

            logger.info("Finished clicking all elements.")

        except TimeoutException:
            logger.warning(f"Timeout while waiting for elements with strategy {strategy}.")  
            result = False
        except Exception as e:
            logger.error(f"Unexpected error with strategy {strategy['name']}: {e}")  
            result = False  
    
        logger.info(f"Total elements clicked: {clicked_count}")  
        # Final result depends on whether any element was clicked  
        return clicked_any and result 

    def click_control(self, control, multiple, timeout: int = 10):
        """
        Attempts to click a button based on metadata.
        Supports id, css, xpath, text, aria-label, name, etc.
        Falls back progressively until click succeeds.
          
        :param control: Dictionary with element metadata (e.g., id, name, css selectors, etc.).  
        :param multiple: Whether to click multiple matching elements or just the first.  
        :param timeout: Maximum time to wait for elements (default: 10 seconds).  
        :return: True if an element was clicked, False otherwise.  
        """

        if not control or not isinstance(control, dict):
            logger.error("Invalid control metadata. Expected a dictionary, got: %s", type(control))             
            return False
        
        # Prioritize XPath by adding it first  
        strategies = [  
            # Add XPath selectors dynamically first  
            *(  
                {"name": "xpath", "locator": (By.XPATH, xp)}  
                for xp in control.get("xpath_selectors", [])  
            ),
            # Add CSS selectors dynamically  
            *(  
                {"name": "css_selector", "locator": (By.CSS_SELECTOR, css)}  
                for css in control.get("css_selectors", [])  
            ),              
            # Add other strategies  
            {"name": "id", "locator": (By.ID, control.get("id")) if control.get("id") else None},  
            {"name": "name", "locator": (By.NAME, control.get("name")) if control.get("name") else None},  
            {"name": "aria_label", "locator": (By.CSS_SELECTOR, f'[aria-label="{control.get("aria_label")}"]') if control.get("aria_label") else None},  
            {"name": "data_testid", "locator": (By.CSS_SELECTOR, f'[data-testid="{control.get("data_testid")}"]') if control.get("data_testid") else None},  
            {"name": "class_name", "locator": (By.CLASS_NAME, control.get("classes").split()[0]) if control.get("classes") else None},  
            {"name": "partial_link_text", "locator": (By.PARTIAL_LINK_TEXT, control.get("text")) if control.get("tag_name") == "a" and control.get("text") else None},   
        ]  

        for strategy in strategies:
            if (  
                strategy is None or   
                strategy["locator"] is None or   
                not isinstance(strategy["locator"], tuple) or   
                len(strategy["locator"]) != 2  
            ):  
                logger.warning(f"Skipping strategy: {strategy['name']} because the locator is invalid. Locator: {strategy['locator']}")  
                continue  

            logger.info(f"Trying strategy: {strategy['name']} with locator: {strategy['locator']}")
            clicked_any = self.do_clicks(strategy["locator"], multiple, timeout)

            # Break the strategy loop if element is clicked
            if clicked_any:
                logger.info(f"Successfully clicked element using strategy: {strategy['name']}")  
                return True  # Stop after the first successful click     

        # If no elements were clicked, log the failure  
        logger.warning("Failed to click any element using the provided strategies.")  
        return False 

    def navigation_element_expanded(self, text):
        tmp_file = self.variables["TMP_FOLDER"]
        filename = os.path.join(tmp_file, "expand.png")
        test_image = self.take_screenshot(filename=filename)
        prompt = f"""
            STRICT VALIDATION MODE: You are a binary validator, not a helpful assistant.,
            Return {{"status": false}} immediately if ANY condition fails.,
            Do not make excuses or justifications.,

            Focus onto navigation pane of the image.

            Use Chevron to detect the state as well. 
            When expanded, Chevron will be '^' otherwise 'v'.
            
            Tell me if {text} is expanded or collapsed ? 
            Respond with {{"status": true}} or {{"status": false}}

            Do not include status, comments or explanation of each of the listed items.
            If all conditions are met return {{"status": true}}
        """
        result = self.run_ai_task("", test_image, prompt=prompt )
        logger.info(f"{text} expanded - {result}")

        return result["status"] 
    
    def execute_click_action(self, step: Dict[str, Any]) -> None:        
        """Execute click action."""
        element_id = step.get('id', 'unknown')
        label = step.get('label', 'unknown')
        page = step.get('page', 'unknown')                 
        text = step.get('text', 'unknown')
        expand = step.get('expand', 'False')
        parent = step.get('parent', 'unknown')
        multiple = step.get('multiple', 'True')

        result = True

        if page:
            self.load_json_metadata(page)

        # if "hpsmart" in page:
        #     print(f"\nNow in HPSmart context\nBrowser urls - {self.manager.get_all_urls_by_browser()}")
        #     self.manager.switch_to_window_by_url("www.hpsmart", exact_match=False)
        
        # if "emulate" in page:
        #     print(f"\nNow in emulate context - {text}")
        #     self.manager.switch_to_window_by_url("/emulate-actions/", exact_match=False)
        

        multiple = multiple == "True"
        expand = expand == "True"

        to_click = True
        if expand:
            to_click = not self.navigation_element_expanded(text)
            logger.info(f"navigation element - to expand - {to_click}")

        if to_click:
            control = self.get_control(text)  
            if control:  
                logger.debug("Entering click control - text")
                if control and 'iframe' in control and control['iframe']:
                    iframe_element = self.driver.find_element(By.XPATH, control['iframe']["xpath_selectors"][0])
                    print(f"iframe_element - {control['iframe']["xpath_selectors"][0]}")
                    if iframe_element:
                        self.driver.switch_to.frame(iframe_element)

                self.click_control(control, multiple)
                result = True  
            else:
                control = self.get_control(label)
                if control:
                    logger.debug("Entering click control - label")
                    if control and 'iframe' in control and control['iframe']:
                        iframe_element = self.driver.find_element(By.XPATH, control['iframe']["xpath_selectors"][0])
                        print(f"iframe_element - {control['iframe']["xpath_selectors"][0]}")
                        if iframe_element:
                            self.driver.switch_to.frame(iframe_element)
                                               
                    self.click_control(control, multiple)
                    result = True
                else:
                    logger.error(f"Control ID not found for name: text ({text}) or label ({label})")
                    result = False
        else:
            logger.info(f"Element already in expanded state.")
        
        logger.info(f"[CLICK] Page: {page} | Element ID: {element_id} | Text: {text} | Label: {label} | Expand: {expand} | Multiple: {multiple}")
        self.log_action("click", step)

        return result
        
    def set_control_value(self, control, value, timeout=10):  
        """  
        Attempts to set a value in a control based on metadata.  
        Supports id, css, xpath, text, aria-label, name, etc.  
        Falls back progressively until setting value succeeds.  
        :param control: The metadata dictionary for the control.  
        :param value: The value to set in the control.  
        :param timeout: Maximum wait time for locating the control.  
        """  
        if not control or not isinstance(control, dict):  
            logger.info("Empty control metadata")  
            return False  
  
        strategies = []

        basic_strategies = [  
            {"name": "id", "locator": (By.ID, control.get("id")) if control.get("id") else None},  
            {"name": "name", "locator": (By.NAME, control.get("name")) if control.get("name") else None},  
            # {"name": "css_selectors", "locator": (By.CSS_SELECTOR, control["css_selectors"][0]) if control.get("css_selectors") else None},  
            # {"name": "xpath_selectors", "locator": (By.XPATH, control["xpath_selectors"][0]) if control.get("xpath_selectors") else None},  
            {"name": "aria_label", "locator": (By.CSS_SELECTOR, f'[aria-label="{control.get("aria_label")}"]') if control.get("aria_label") else None},  
            {"name": "data_testid", "locator": (By.CSS_SELECTOR, f'[data-testid="{control.get("data_testid")}"]') if control.get("data_testid") else None},  
            {"name": "class_name", "locator": (By.CLASS_NAME, control.get("classes").split()[0]) if control.get("classes") else None},  
            {"name": "partial_link_text", "locator": (By.PARTIAL_LINK_TEXT, control.get("text")) if control.get("tag_name") == "a" and control.get("text") else None},  
        ]

        # All CSS selectors
        for css in control.get("css_selectors", []):
            basic_strategies.append({"name": "css_selector", "locator": (By.CSS_SELECTOR, css)})

        # All XPath selectors
        for xp in control.get("xpath_selectors", []):
            basic_strategies.append({"name": "xpath", "locator": (By.XPATH, xp)})

        strategies.extend([s for s in basic_strategies if s["locator"] is not None])
    
        # # Replace single CSS/XPath with multiple strategies
        # if control.get("css_selectors"):
        #     for i, css_sel in enumerate(control["css_selectors"]):
        #         strategies.append({"name": f"css_selector_{i}", "locator": (By.CSS_SELECTOR, css_sel)})
    
        if control.get("xpath_selectors"):
            for i, xpath_sel in enumerate(control["xpath_selectors"]):
                strategies.append({"name": f"xpath_selector_{i}", "locator": (By.XPATH, xpath_sel)})
  
  
        for strategy in strategies:  
            if strategy["locator"] is None:  
                logger.debug(f"Strategy '{strategy['name']}' locator is null")  
                continue  
  
            try:  
                element = WebDriverWait(self.driver, timeout).until(  
                    EC.presence_of_element_located(strategy["locator"])  
                )
                
                if element.tag_name == "select":  
                    logger.debug(f"Found dropdown element using strategy: {strategy['name']}")  
                    select = Select(element)  
                    # Attempt to select by visible text or value  
                    try:  
                        select.select_by_visible_text(str(value))  
                        logger.info(f"Selected '{value}' from dropdown using visible text.")  
                    except:  
                        select.select_by_value(str(value))  
                        logger.error(f"Selected '{value}' from dropdown using value.")  
                    return True  
  
                element.clear()  # Clear the field before setting the value  
                element.send_keys(str(value))  # Set the value  
                return True  
            except (NoSuchElementException, ElementClickInterceptedException, TimeoutException):  
                logger.error(f"Failed to set value using strategy: {strategy['name']}")  
                continue  
            except Exception as e:  
                logger.error(f"Unexpected error with strategy '{strategy['name']}': {e}")  
                continue  
  
        logger.error("Failed to set value with available metadata.")  
        return False  
  
    def set_variables(self, **kwargs):
        for key, value in kwargs.items():
            logger.info(f"set variables  - {key}: {value}")

        self.variables.update(kwargs)
        return True

    def substitute_variables(self, text):
        """Replace ${variable} with actual values"""
        if not isinstance(text, str):
            logger.debug("substitute variables - returning not isinstance condition")
            return text
        
        logger.info(f"substitute_variables - {self.variables}")
            
        # Replace variables in format ${variable_name}
        def replace_var(match):
            var_name = match.group(1)

            # if var_name in globals():
            #     return str(globals()[var_name])
            # else:
            #     logger.info("variable not found in globals")

            # Handle dot notation: temp_id.status
            if '.' in var_name:
                var_name, key = var_name.split('.', 1)
                var_value = self.variables.get(var_name)
                if isinstance(var_value, dict):
                    return str(var_value.get(key, match.group(0)))
                else:
                    return match.group(0)  # Return original if not a dict
            else:
                logger.debug("substitute variables - else condition")
                return str(self.variables.get(var_name, match.group(0)))
        
        return re.sub(r'\$\{([^}]+)\}', replace_var, text)

    def take_screenshot(self, filename: str = "page.png"):
        self.driver.save_screenshot(filename)
        return filename
    
    def create_message_content(self, prompt_lines, image_base64=None, image_url=None):
        """
        Convert prompt lines array into OpenAI message content array format
        
        Args:
            prompt_lines: List of strings, each representing a line of the prompt
            image_base64: Base64 encoded image string (optional)
            image_url: Image URL (optional, use either this or image_base64)
        
        Returns:
            List of content objects for OpenAI API
        """
        content = []
        
        # Add each prompt line as separate text content
        for line in prompt_lines:
            if line.strip():  # Skip empty lines
                content.append({
                    "type": "text",
                    "text": line.strip()
                })
        
        # Add image if provided
        if image_base64:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_base64}"
                }
            })
        elif image_url:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            })
        
        return content

    def handle_streaming_response(self, response):
        """
        Handle streaming response with try-except for safety
        """

        logger.info(f"handle_streaming_response - {response}")

        result = ""
        
        for chunk in response:
            try:
                if chunk.choices and chunk.choices[0].delta.content:
                    result += chunk.choices[0].delta.content
            except (IndexError, AttributeError):
                # Skip chunks without content (normal in streaming)
                continue
        
        return result

    def debug_streaming_chunks(self, response):
        """Debug what's actually coming through the stream"""
        chunk_count = 0
        full_content = ""
        
        for chunk in response:
            chunk_count += 1
            try:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    logger.info(f"Chunk {chunk_count}: '{content}'")
            except (IndexError, AttributeError):
                logger.info(f"Chunk {chunk_count}: No content")
        
        logger.info(f"\n=== FULL CONCATENATED RESULT ===")
        logger.info(f"'{full_content}'")
        logger.info(f"=== END RESULT ===")
        
        return full_content

    def run_ai_task(self, reference, test, prompt):
        azure_endpoint = config["llm"]["azure_endpoint"]
        deployment = config["llm"]["deployment"]
        api_key = config["llm"]["api_key"]
        api_version = config["llm"]["api_version"]

        result = None

        client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                api_version=api_version
            ) 
        
        if reference:
            with open(reference, "rb") as image_file:
                reference_image = base64.b64encode(image_file.read()).decode('utf-8')
        else:
            reference_image = None

        if test:
            with open(test, "rb") as image_file:
                test_image = base64.b64encode(image_file.read()).decode('utf-8')
        else:
            test_image = None
            # may be an invalid case, should introduce a return statement

        # ChatGPT-4o is sending each line as a text block of the prompt.  Hence adopting similar approach.
        # prompt_lines = prompt.split('\n')
        # content = self.create_message_content(prompt_lines, image_base64=test_image)

        logger.info(f"prompt being used is {prompt}")

        if not reference_image:
            messages = [
                {
                    "role": "system",
                    "content": "You are an vision assistant..."
                },
                {
                    "role": "user",
                    "content": [
                        { "type": "text", "text": prompt },
                        { "type": "image_url", "image_url": { "url": f"data:image/png;base64,{test_image}", "detail": "high" } }
                    ]
                }
            ]
        else:
            messages=[
                {
                    "role": "user",
                    "content": [
                        { "type": "text", "text": prompt },
                        { "type": "image_url", "image_url": { "url": f"data:image/png;base64,{reference_image}", "detail": "high"} },
                        { "type": "image_url", "image_url": { "url": f"data:image/png;base64,{test_image}", "detail": "high" } }
                    ]
                }
            ]

        response = client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_tokens=6000,
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            seed = 12345
            # extra_headers={"Content-Type": "application/json"}
        )
        
        if hasattr(response, '__iter__') and not hasattr(response, 'choices'):
            # logger.info("Streaming content")
            # result = self.debug_streaming_chunks(response)
            result = self.handle_streaming_response(response)
        else:
            # logger.info("Non streaming content")
            result = response.choices[0].message.content    
        
        # logger.info(f"AI model response - {result}")
        cleaned = result.strip('`json\n ')        
        cleaned = cleaned.strip('`')
        # logger.info(f"AI model cleaned response - {cleaned}")        
        data = json.loads(cleaned)
        logger.info(f"AI model return value - {data}")

        return data

    def get_selected_printer(self, config, stack):       
        for item in config["printers"]:
            if stack in item:  # check if the environment key exists
                for printer in item[stack]:
                    if printer.get("selected_printer", False):
                        logger.info(f"get_selected_printer - {printer['serial_number']}")
                        return  printer["serial_number"]
        return None

    def execute_select_action(self, step: Dict[str, Any], timeout=10) -> None:
        element_id = step.get('id', 'unknown')
        text = step.get('text', 'unknown')
        label = step.get('label', 'unknown')
        value = step.get('value', 'unknown')
        page = step.get('page', 'unknown')
        result = True

        try:
            if page:
                self.load_json_metadata(page)

            print(f"select - text({text}) - label({label})")

            control = self.get_control(text)
            if not control:
                control = self.get_control(label)

            #selector loop to be implemented

            if control and 'iframe' in control and control['iframe']:
                iframe_element = self.driver.find_element(By.XPATH, control['iframe']["xpath_selectors"][0])
                print(f"iframe_element - {control['iframe']["xpath_selectors"][0]}")
                if iframe_element:
                    self.driver.switch_to.frame(iframe_element)

            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, control["id"]))
            )
            element.send_keys(str(value)) 

            if iframe_element:
                self.driver.switch_to.default_content()

        except Exception as e:  
            logger.error(f"Error locating CVV {e}")            

        logger.info(f"[SELECT] Page: {page} | Element ID: {element_id} | Text: {text} | Value: {value} ")
        self.log_action("select", step)

        return result

    def execute_select_printer_action(self, step: Dict[str, Any]) -> None:
        """Execute select_printer action."""
        logger.info(f"execute_select_printer - {step}")
        element_id = step.get('id', 'unknown')
        text = step.get('text', 'unknown')
        page = step.get('page', 'unknown')
        result = True
        
        try:
            # Wait for the expand button to be clickable  
            expand_button = WebDriverWait(self.driver, 10).until(  
                EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='selector-collapsed']"))  
            )  
            
            self.driver.execute_script("arguments[0].scrollIntoView(true);", expand_button) 

            # Click the expand button  
            expand_button.click()  

            logger.info("Select printer - dropdown to be clicked")
            # Wait for categories to load  
            categories = WebDriverWait(self.driver, 15).until(  
                EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "selectablePrinters__selectable-printers-container-new-visid")]'))  
            ) 

            # Step 2: Wait for the dropdown options to be visible
            desired_serial_number = self.substitute_variables(text)
            logger.info(f"select logger.infoer - desired_serial_number - {desired_serial_number}")
            found = False 

            for category in categories:
                try: 
                    category_title = category.find_element(By.XPATH, './/p[contains(@class, "selectablelogger.infoers__selectable-printers-submenu-title")]').text  
                    logger.info(f"Searching in category: {category_title}")
                except Exception as e:  
                    logger.error(f"Error extracting category title: {e}")  
                    logger.error(category.get_attribute('outerHTML'))
                    result = False  
                    continue 

                # Step 2b: Get all printers in the current category  
                printers = category.find_elements(By.XPATH, './/div[contains(@class, "selectablePrinters__selectable-printers-item-container")]')  
                if not printers:  
                    logger.info(f"No printers found in category: {category_title}")  
                    continue

                for printer in printers:
                    try:                          
                        printer_info = printer.find_element(By.XPATH, './/div[contains(@class, "option__printer-info")]')

                        printer_name_element = WebDriverWait(printer_info, 10).until(  
                            EC.presence_of_element_located((By.XPATH, './/p[contains(@class, "option__printer-name")]'))  
                        )
                        serial_number_element = WebDriverWait(printer_info, 10).until(  
                                EC.presence_of_element_located((By.XPATH, './/p[contains(@class, "option__printer-serial-number")]'))  
                        )                              

                        # Extract text using JavaScript in case elements are hidden  
                        printer_name = self.driver.execute_script("return arguments[0].textContent;", printer_name_element).strip()  
                        serial_number = self.driver.execute_script("return arguments[0].textContent;", serial_number_element).strip().replace("S/N: ", "") 

                        if not printer_name or not serial_number:  
                            logger.error(f"Invalid printer details: {printer_name}, {serial_number}")
                            result = False
                            continue

                        logger.info(f"Found printer: {printer_name} (Serial Number: {serial_number})") 

                        # Step 2d: Check if the serial number matches  
                        if serial_number == desired_serial_number:  
                            logger.info(f"Selecting printer: {printer_name} (Serial Number: {serial_number})") 

                            # Scroll into view  
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", printer)  

                            # Wait for the element to be clickable  
                            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, './/div[contains(@class, "option__printer-option-new-visid___3VlLa")]')))  
                            
                            # Use ActionChains to click  
                            ActionChains(self.driver).move_to_element(printer).click().perform()  

                            # Click the expand button  
                            expand_button.click()  

                            found = True
                            result = True
                            break 
                    except Exception as e:  
                        logger.error(f"Error extracting printer details: {e}")  
                        logger.error(printer.get_attribute('outerHTML'))  
                        result = False
                        continue 

                if found:
                    result = True  
                    break  

            if not found: 
                logger.error(f"No printer found with serial number: {desired_serial_number}")
                result = False

        except Exception as e:
            logger.error(f"Error locating the printer. {e}")
            logger.error(printer.get_attribute('outerHTML'))
            result = False

        logger.info(f"[SELECT_PRINTER] Page: {page} | Element ID: {element_id} | Text: {text} ")
        self.log_action("select_printer", step)

        return result

    def execute_load_url_action(self, step: Dict[str, Any]) -> None:
        element_id = step.get('id', 'unknown')
        url = step.get('text', 'unknown')
        browser = step.get('browser', "instantink")
        new_tab = step.get('new_tab', 'False')
        page = step.get('page', 'unknown')
        result = True

        url = self.substitute_variables(url)
        result = self.manager.load_url_in_browser(browser, url=url, new_tab=new_tab)

        logger.info(f"[LOAD_URL] Page: {page} | Element ID: {element_id} | Text: {url} | Browser: {browser} | New Tab: {new_tab}")
        self.log_action("load_url", step)

        return result

    def execute_set_action(self, step: Dict[str, Any]) -> None:
        """Execute set/input action."""
        element_id = step.get('id', 'unknown')
        text = step.get('text', 'unknown')
        value = step.get('value', '')
        page = step.get('page', 'unknown')
        result = True

        if page:
            self.load_json_metadata(page)

        if "emulate" in page:
            logger.info(f"\nNow in emulate context - {text}")
            self.manager.switch_to_window_by_url("/emulate-actions/", exact_match=False)  

        value = self.substitute_variables(value)
        control = self.get_control(text)  
        if control:  
            self.set_control_value(control, value)    
        else:  
            logger.error(f"Control ID not found for name: {text}") 
            result = False

        logger.info(f"[SET] Page: {page} | Element ID: {element_id} | Text: {text} | Value: {value}")
        self.log_action("set", step)

        return result
            
    # def execute_wait_action(self, step: Dict[str, Any]) -> None:
    #     """Execute wait action."""
    #     duration = step.get('duration', step.get('sleep', 1))
    #     reason = step.get('reason', 'No reason specified')
        
    #     logger.info(f"[WAIT] Duration: {duration}s | Reason: {reason}")
    #     self.log_action("wait", step)
    
    def execute_navigate_action(self, step: Dict[str, Any]) -> None:
        """Execute navigation action."""
        url = step.get('url', '')
        page = step.get('page', 'unknown')
        
        logger.info(f"[NAVIGATE] Page: {page} | URL: {url}")
        self.log_action("navigate", step)
            
    def execute_verify_action(self, step: Dict[str, Any]) -> None:
        """Execute verification action."""
        element_id = step.get('id', 'unknown')
        prompt = step.get('prompt', '')
        text = step.get('text', '')
        screenshot = step.get('screenshot', '')
        reference_image = step.get('reference_image', None)
        result = True

        reference_image = None if reference_image in [None, "None", ""] else os.path.join(self.variables["REFERENCE_IMAGE_PATH"], reference_image)
        logger.info(f"Reference image - {reference_image}")

        if screenshot:
            tmp_file = self.variables["TMP_FOLDER"]
            filename = os.path.join(tmp_file, "page.png")
            test_image = self.take_screenshot(filename=filename)
            
            dst_filename = os.path.join(self.variables["TRACE_FOLDER"], (element_id.replace(" ", "") + ".png"))
            shutil.copy(filename, dst_filename)
            logger.info(f"screen shot, test_image - {test_image}, trace folder file - {dst_filename}")

            prompt = prompt.format(CURRENT_TIME=self.variables["CURRENT_TIME"].strftime("%H:%M"))
            result = self.run_ai_task(reference_image, test_image, prompt)
        
        logger.info(f"[VERIFY] Element ID: {element_id} | Text: {text} | result: {result}")
        self.log_action("verify", step)

        return result
        
    def execute_vscroll_action(self, step:  Dict[str, Any]) -> None:
        element_id = step.get('id', 'unknown') 
        text = step.get('text', None)
        direction = step.get('direction', None)
        result = True

        # try except block
        body = self.driver.find_element(By.TAG_NAME, "body")
        body.click()

        if text:
            control = self.get_control(text)

            strategies = [
                {"name": "id", "locator": (By.ID, control.get("id")) if control.get("id") else None},
                {"name": "name", "locator": (By.NAME, control.get("name")) if control.get("name") else None},
                {"name": "css_selectors", "locator": (By.CSS_SELECTOR, control["css_selectors"][0]) if control.get("css_selectors") else None},
                {"name": "xpath_selectors", "locator": (By.XPATH, control["xpath_selectors"][0]) if control.get("xpath_selectors") else None},
                {"name": "aria_label", "locator": (By.CSS_SELECTOR, f'[aria-label="{control.get("aria_label")}"]') if control.get("aria_label") else None},
                {"name": "data_testid", "locator": (By.CSS_SELECTOR, f'[data-testid="{control.get("data_testid")}"]') if control.get("data_testid") else None},
                {"name": "class_name", "locator": (By.CLASS_NAME, control.get("classes").split()[0]) if control.get("classes") else None},
                {"name": "partial_link_text", "locator": (By.PARTIAL_LINK_TEXT, control.get("text")) if control.get("tag_name") == "a" and control.get("text") else None}
            ]

            # clicked_any = False
            for strategy in strategies:
                if strategy["locator"] is None:
                    continue
                wait = WebDriverWait(self.driver, 10)
                scroll = wait.until(
                    EC.presence_of_element_located(strategy["locator"])
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", scroll)
                logger.info(f"Vertical scroll to, {text}")
                break 
        else:
            direction = Keys.PAGE_UP if direction else Keys.PAGE_DOWN        
            self.driver.find_element("tag name", "body").send_keys(direction)
            logger.info(f"Vertical scroll by a page") 

        logger.info(f"[VSCROLL] | Element ID: {element_id} | Text: {text} ")
        self.log_action("vscroll", step)

        return result

    def execute_refresh_action(self, step:  Dict[str, Any]) -> None: 
        element_id = step.get('id', 'unknown')
        result = True

        self.driver.refresh()

        logger.info(f"[REFRESH] | element ID: {element_id}")
        self.log_action("refresh", step)

        return result

    def  execute_escape_action(self, step:  Dict[str, Any]) -> None:
        element_id = step.get('id', 'unknown')
        result = True

        self.driver.find_element("tag name", "body").send_keys(Keys.ESCAPE)

        logger.info(f"[ESCAPE] | Element ID: {element_id} ")
        self.log_action("escape", step)

        return result

    def  execute_store_action(self, step:  Dict[str, Any]) -> None:
        element_id = step.get('id', 'unknown')
        text = step.get('text', None)
        result = True

        if text and text != "${}":
            cleaned = text.strip("${}")

            if cleaned.lower() == "current_time":
                self.variables[cleaned] = datetime.now()
            else:
                self.variables[cleaned] = "unknown"

            logger.info(f"store {cleaned} - {self.variables[cleaned]}")
        else:
            logger.error("store text not recognized")

        logger.info(f"[STORE] | Element ID: {element_id} | Text: {text} ")
        self.log_action("store", step)

        return result

    def  execute_locale_action(self, step:  Dict[str, Any]) -> None:
        element_id = step.get('id', 'unknown')
        page = step.get('page', 'unknown')
        country = step.get('country', 'US')
        language = step.get('language', 'English')
        result = True

        # Do a lookup in locales.yaml and then assign the value for country and language.
        self.variables['country'] = country
        self.variables['language'] = language

        logger.info(f"[LOCALE] | Element ID: {element_id} | Page: {page} | Country: {country} | Language: {language}")
        self.log_action("escape", step)

        return result

    def execute_custom_action(self, step: Dict[str, Any]) -> None:
        """Execute custom/unknown actions."""
        action = step.get('action', 'unknown')
        result = True

        logger.info(f"[CUSTOM] Action: {action} | Step data: {step}")
        self.log_action("custom", step)

        return result
    
    def do_sleep(self, duration: int) -> None:
        """Handle sleep/wait with proper timing."""
        if duration > 0:
            logger.info(f"[SLEEP] Waiting for {duration} seconds...")
            time_module.sleep(duration)
    
    def execute_step(self, step: Dict[str, Any]) -> None:
        """Execute a single test step based on its action type."""
        if not isinstance(step, dict):
            raise ValueError("Step must be a dictionary")
        
        result = True

        action = step.get('action', '').lower()
        page = step.get('page')
        
        # Update current page if specified
        if page:
            self.current_page = page
        
        logger.info(f"--- Executing Step ---")
        logger.info(f"Action: {action}")
        logger.info(f"Current Page: {self.current_page}")
        
        # Execute based on action type
        if action == 'click':
            result = self.execute_click_action(step)
        elif action in ['set', 'input']:
            result = self.execute_set_action(step)
        elif action == 'load_url':
            result = self.execute_load_url_action(step)
        elif action == 'select_printer':
            result = self.execute_select_printer_action(step)
        elif action == 'vscroll':
            result = self.execute_vscroll_action(step)
        elif action == 'escape':
            result = self.execute_escape_action(step)                    
        elif action == 'verify':
            result = self.execute_verify_action(step)
        elif action == 'refresh':
            result = self.execute_refresh_action(step)
        elif action == 'store':
            result = self.execute_store_action(step)
        elif action == 'locale':
            result = self.execute_locale_action(step)
        elif action == 'select':
            result = self.execute_select_action(step)                                      
        else:
            result = self.execute_custom_action(step)
        
        # Handle sleep/wait time if specified
        sleep_time = step.get('sleep', 0)
        sleep_time = int(self.substitute_variables(sleep_time))
        logger.debug(f"sleep time {sleep_time} seconds")
        if sleep_time and isinstance(sleep_time, int):
            self.do_sleep(sleep_time)

        return result
    
    def execute_flow(self, yaml_data: Dict[str, Any], flow_result = None) -> None:
        """Execute the complete test flow."""
        if 'flow' not in yaml_data:
            raise ValueError("YAML data must contain 'flow' key")
        
        workflow_results = []

        flow = yaml_data['flow']
        steps = flow.get('steps', [])
        
        if not steps:
            logger.info("No steps found in the flow")
            return
        
        logger.info(f"=== Starting Test Flow Execution ===")
        logger.info(f"Total steps to execute: {len(steps)}")
        
        result = True
        for i, step in enumerate(steps, 1):
            try:                
                logger.info(f"{'='*50}")
                logger.info(f"Step {i}/{len(steps)}")

                start_time = time_module.time()
                result = self.execute_step(step)

            except Exception as e:
                logger.error(f"ERROR in step {i}: {e}")
                self.log_error(i, step, str(e))
                # Continue execution on error
                continue

            end_time = time_module.time()
            duration = end_time - start_time

            # Record structured data
            workflow_results.append({
                'step_name': step['id'],
                'start_time': time_module.ctime(start_time),
                'duration_seconds': round(duration, 4),
                'status': result
            })
        
        if flow_result and workflow_results:
            results_df = pd.DataFrame(workflow_results)
            
            results_df.to_csv(flow_result, index=False)
            logging.info(f"Workflow summary saved to {flow_result}")

        logger.info(f"{'='*50}")
        logger.info("=== Test Flow Execution Completed ===")
        self.print_execution_summary()
    
    def log_action(self, action_type: str, step: Dict[str, Any]) -> None:
        """Log executed action for reporting."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'step_data': dict(step),
            'status': 'success'
        }
        self.execution_log.append(log_entry)
    
    def log_error(self, step_number: int, step: Dict[str, Any], error_message: str) -> None:
        """Log execution error."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'step_number': step_number,
            'step_data': dict(step),
            'status': 'error',
            'error_message': error_message
        }
        self.execution_log.append(log_entry)
    
    def print_execution_summary(self) -> None:
        """Print execution summary."""
        successful_count = 0
        failed_count = 0
        
        for log in self.execution_log:
            if log.get('status') == 'success':
                successful_count += 1
            elif log.get('status') == 'error':
                failed_count += 1
        
        logger.info(f"--- Execution Summary ---")
        logger.info(f"Total steps executed: {len(self.execution_log)}")
        logger.info(f"Successful steps: {successful_count}")
        logger.info(f"Failed steps: {failed_count}")
        
        if failed_count > 0:
            logger.info("Failed steps:")
            for log in self.execution_log:
                if log.get('status') == 'error':
                    step_num = log.get('step_number', 'unknown')
                    error_msg = log.get('error_message', 'unknown error')
                    logger.info(f"  Step {step_num}: {error_msg}")
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Get the complete execution log."""
        return list(self.execution_log)


def run_yaml_test(yaml_content: str) -> YamlStepExecutor:
    """
    Convenience function to run a YAML test and return the executor.
    """
    executor = YamlStepExecutor()
    try:
        yaml_data = executor.load_yaml_string(yaml_content)
        executor.execute_flow(yaml_data)
    except Exception as e:
        logger.error(f"Execution failed: {e}")
    return executor


def run_yaml_test_from_file(file_path: str) -> YamlStepExecutor:
    """
    Convenience function to run a YAML test from file and return the executor.
    """
    executor = YamlStepExecutor()
    try:
        yaml_data = executor.load_yaml_file(file_path)
        executor.execute_flow(yaml_data)
    except Exception as e:
        logger.info(f"Execution failed: {e}")
    return executor
