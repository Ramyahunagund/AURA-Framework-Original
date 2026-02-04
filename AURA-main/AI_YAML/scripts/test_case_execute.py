import logging
import os
import pytest
import sys
import yaml

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config_loader        import load_config, get_printers_by_description
from teststep_processor   import YamlStepExecutor
from multibrowsermanager  import MultiBrowserManager  
from conftest             import yaml_data

config = load_config(r"config.yaml")
METADATA_FILEPATH = config["metadata"]["controls"]
REFERENCE_IMAGES = config["metadata"]["reference_images"]
URL = config["login"]["url"]
USERNAME = config["login"]["username"]
PASSWORD = config["login"]["password"]
COUNTRY = config["locale"]["country"]
LANGUAGE = config["locale"]["language"]
LARGE_WAIT = int(config["large_wait"]) * 60     # seconds


manager = MultiBrowserManager()

@pytest.fixture(scope="module")  
def driver():

    browser = "instantink"
    driver = manager.create_normal_browser(browser, user_data_dir=None)
    if not driver:
        logging.error("Browser error - Check if Chrome profile folder exists")
        return
        
    yield driver  
    # Quit the WebDriver at the end of the test session  
    driver.quit()  
  
def test_case_execute(yaml_data, yaml_file_path, driver):  
    """  
    Test the execution of the flow using the FlowController class.  
    """
    logging.info("hp-ai-instant-services")
    # logging.info(config)

    printer_description = "out_of_trial_period"
    printer_to_select = get_printers_by_description(config, printer_description)[0]["serial_number"]
    logging.info(f"demo - printer - {printer_to_select}")

    logging.info(f"test_verify_cancellation_pause_plan execution")
    logging.info(f"Select printer {printer_to_select}, {printer_description}")
    
    executor = YamlStepExecutor(manager, driver, METADATA_FILEPATH, 'instantink/Home')

    trace_folder = os.path.join(os.path.dirname(config["log_file"]),(os.path.splitext(os.path.basename(yaml_file_path))[0] + "_" + datetime.now().strftime("%d_%m_%Y_%H_%M_%S")))
    os.makedirs(trace_folder, exist_ok=True)

    # Set global variables where referenced in YAML files.
    executor.set_variables(
        URL=URL,
        COUNTRY=COUNTRY,
        LANGUAGE=LANGUAGE,
        USERNAME=USERNAME,
        PASSWORD=PASSWORD,
        REFERENCE_IMAGE_PATH=REFERENCE_IMAGES,
        SELECTED_PRINTER=executor.get_selected_printer(config, "stage"),
        TMP_FOLDER=config["tmp_folder"],
        TRACE_FOLDER=trace_folder,
        CURRENT_TIME=datetime.now(),
        LARGE_WAIT=LARGE_WAIT
    )

    try:
        logging.info(f"Test execution begin")
        flow = yaml_data
        print(f"yaml file contents - {yaml.dump(yaml_data, indent=2)}")
        flow_result = os.path.join(trace_folder, os.path.splitext(os.path.basename(yaml_file_path))[0] + ".csv")
        executor.execute_flow(flow, flow_result)

    except Exception as e:
        logging.error(f"Test execution failed: {e}")
