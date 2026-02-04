#aura.py

# The initial version of the AURA Framework has been started with 0.0.1.
# The version history will be maintained in seperate approach going forward.
aura_version = "0.0.1"
import argparse
import subprocess
import sys
import os
import traceback
import json
import logging
from typing import Any, Dict, Optional
import openpyxl
import yaml
import subprocess
import re
from core.settings import Constants, framework_logger, set_framework_log_level
from core.utils import run_scrape_mode, run_validate_mode, run_noop_mode
from core.utils import (
    load_locale_data,
    load_printer_profiles,
    get_printer_details_for_country,
    load_address_for_country,
)

WEB_PLATFORMS = ["web_chrome", "web_safari", "web_firefox"]

SIMULATOR_PLATFORM_MAPPING: Dict[str, list] = {
    "windows_app": ["wingotham", "hpxwindows", "wingotham-od", "hpxwindows-od"],
    "mac_app": ["macgotham", "hpxmac", "macgotham-od", "hpxmac-od"],
    "android_app": ["android", "hpxandroid", "android-od", "hpxandroid-od"],
    "ios_app": ["ios", "hpxios", "ios-od", "hpxios-od"],
}

SIMULATOR_CONFIGS: Dict[str, Dict[str, Any]] = {
    "wingotham":        {"simulator_platform": "GothamDesktop"},
    "macgotham":        {"simulator_platform": "GothamMac"},
    "android":          {"simulator_platform": "Android"},
    "ios":              {"simulator_platform": "IOS"},
    "hpxwindows":       {"simulator_platform": "HpxWindows"},
    "hpxmac":           {"simulator_platform": "HpxMac"},
    "hpxandroid":       {"simulator_platform": "HpxAndroid"},
    "hpxios":           {"simulator_platform": "HpxIos"},
    "wingotham-od":     {"simulator_platform": "hpSmartWinOnboardingAgent"},
    "macgotham-od":     {"simulator_platform": "hpSmartMacOsOnboardingAgent"},
    "android-od":       {"simulator_platform": "hpSmartAndroidOnboardingAgent"},
    "ios-od":           {"simulator_platform": "hpSmartIosOnboardingAgent"},
    "hpxwindows-od":    {"simulator_platform": "hpxwindows"},
    "hpxmac-od":        {"simulator_platform": "hpxmac"},
    "hpxandroid-od":    {"simulator_platform": "hpxandroid"},
    "hpxios-od":        {"simulator_platform": "hpxios"},
}

RESOLUTION_CONFIGS: Dict[str, Dict[str, int]] = {
    "web_chrome": {"width": 1920, "height": 1080},
    "web_safari": {"width": 1920, "height": 1080},
    "web_firefox": {"width": 1920, "height": 1080},
    "windows_app": {"width": 1280, "height": 720}, # OOBE
    "mac_app": {"width": 1280, "height": 720}, # OOBE
    "android_app": {"width": 412, "height": 915}, # MOBE
    "ios_app": {"width": 430, "height": 932}, # MOBE
}

class FlowConfigError(Exception):
    pass

def parse_args() -> argparse.Namespace:
    if any(arg.startswith('--version') for arg in sys.argv):
        print ("The version of the code is : ",aura_version)
        sys.exit(1)
    print ("************************* AURA Framework - Version:",aura_version,"*************************")

    if any(arg.startswith('--addflow') for arg in sys.argv):
        parser = argparse.ArgumentParser(description="Instant Ink Aura Framework")
        parser.add_argument("--addflow", help="Add a new test flow with the given name", required=True)
        return parser.parse_args()
    parser = argparse.ArgumentParser(description="Instant Ink Aura Framework")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--addflow", help="Add a new test flow with the given name")
    parser.add_argument("--flow", required=False, help="Name of the test flow (folder inside test_flows/)")
    parser.add_argument("--mode", required=True, choices=["scrape", "validate", "noop", "yaml"], help="Execution mode")
    parser.add_argument("--stack", required=False, choices=["stage", "pie", "production"], help="Stack to target")
    parser.add_argument("--locale", required=False, help="Country name (e.g., United States, Germany, Singapore)")
    parser.add_argument("--language", help="Language code (optional, fallback to default for locale)")
    parser.add_argument("--printer_profile", help="Printer profile name (optional)")
    parser.add_argument("--easy_enroll", choices=["yes", "no"], default="no", help="Filter SKU by easy enroll flag (optional, default: no)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--biz_model", choices=["Flex", "E2E"], default="Flex", help="Business model: Flex (default) or E2E")
    parser.add_argument("--target", required=False, choices=["web_chrome", "web_safari", "web_firefox", "windows_app", "mac_app", "android_app", "ios_app"], help="Target platform")
    parser.add_argument("--simulator_platform", choices=SIMULATOR_CONFIGS.keys(), help="Simulator platform (required for app targets)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--payment_method", help="Payment method to use (e.g., credit_card_visa, credit_card_amex, paypal, paypal_2, google_pay, apple_pay, direct_debit, direct_debit_2). Defaults to credit_card_master")
    parser.add_argument("--collect_logs", nargs='?', const='both', choices=['har', 'video', 'both'], help="Collect logs: 'har' for HAR logs only, 'video' for video only, 'both' for both (default when flag is used without value)")
    parser.add_argument("--requirements", help="Dynamic requirements list e.g. --requirements [plan_pages:50,hpplus:activate,flip_shipping:skip]", default=None)
    
    # Command Line argument specific to YAML based tests execution. This is a part of YAML to Aura merge effort.
    parser.add_argument("--base_yaml", required=False, help="Name of the file where the batch run yaml's are provided")
    parser.add_argument("--batch_name", required=False, help="Name of the batch within Batch YAML") 

    args = parser.parse_args()
    
    if args.mode=="yaml": 
        missing = ["--"+arg for arg in ["base_yaml"] if getattr(args, arg) is None]
        if missing:
            parser.error(f"The following arguments are required when mode is 'yaml': {', '.join(missing)}")
    else:
        print ("No Base YAML file provided. Test will be executed from native Aura.")
        missing = ["--"+arg for arg in ["flow", "stack", "locale", "target"] if getattr(args, arg) is None]
        if missing:
            parser.error(f"The following arguments are required when mode is not 'yaml': {', '.join(missing)}")

        if args.target in WEB_PLATFORMS:
            if args.simulator_platform:
                parser.error(f"--simulator_platform cannot be used with web platform '{args.target}'")
        else:
            if not args.simulator_platform:
                parser.error(f"--simulator_platform is required for app platform '{args.target}'")
            allowed_simulators = SIMULATOR_PLATFORM_MAPPING.get(args.target, [])
            if args.simulator_platform not in allowed_simulators:
                parser.error(f"--simulator_platform '{args.simulator_platform}' is not valid for '{args.target}'. Allowed: {', '.join(allowed_simulators)}")
    return args

def build_flow_args(args: argparse.Namespace) -> Dict[str, Any]:
    flow_dir = os.path.join(Constants.TEST_FLOWS_PATH, args.flow)
    if not os.path.isdir(flow_dir):
        raise FlowConfigError(f"Flow folder not found: {flow_dir}")
    locale_map = load_locale_data()
    printer_profiles = load_printer_profiles()
    country = args.locale
    if country not in locale_map:
        raise FlowConfigError(f"Country '{country}' not in locale_map.json")
    region = locale_map[country]["region"]
    languages = locale_map[country]["languages"]
    short_code = locale_map[country]["code"]
    card_payment_gateway = locale_map[country].get("card_payment_gateway")
    language = args.language or languages[0]
    locale_code = f"{language}-{short_code}"
    framework_logger.debug(f"Resolved locale: country={country}, region={region}, lang={language}, code={locale_code}, card_payment_gateway={card_payment_gateway}")
    address = load_address_for_country(country)
    if not address:
        raise FlowConfigError(f"No address found for country: {country}")
    framework_logger.debug(f"Loaded address for {country}: {json.dumps(address)}")
    profile: Optional[str] = None
    derivative_model: Optional[str] = None
    biz_model_param: str = args.biz_model
    supplyvariant: Optional[str] = None
    if args.printer_profile:
        profile, derivative_model, supplyvariant, biz_model_param = get_printer_details_for_country(
            args.printer_profile, region, printer_profiles, args.easy_enroll, args.biz_model
        )
        framework_logger.debug(f"Printer profile resolved: profile={profile}, derivative_model={derivative_model}, supplyvariant={supplyvariant}, biz_model={biz_model_param}")
    
    # Get resolution config
    resolution_config = RESOLUTION_CONFIGS.get(args.target)
    
    # Get simulator platform
    simulator_platform = ""
    if args.simulator_platform:
        simulator_platform = SIMULATOR_CONFIGS[args.simulator_platform]["simulator_platform"]
    
    flow_args = {
        "stack":                           args.stack,
        "locale":                          country,
        "language":                        language,
        "profile":                         profile,
        "derivative_model":                derivative_model,
        "biz_model":                       biz_model_param,
        "supplyvariant":                   supplyvariant,
        "easy_enroll":                     args.easy_enroll,
        "tenant_country":                  country,
        "tenant_country_short":            short_code,
        "tenant_country_language_code":    locale_code,
        "card_payment_gateway":            card_payment_gateway,
        "payment_method":                  args.payment_method,
        "tenant_address":                  address,
        "headless":                        args.headless,
        "target":                          args.target,
        "simulator_platform":              simulator_platform,
        "target_width":                    resolution_config["width"],
        "target_height":                   resolution_config["height"],
        "collect_logs":                    args.collect_logs,
        "requirements":                    parse_requirements(args.requirements) if getattr(args, 'requirements', None) else {},
    }
    framework_logger.debug(f"Flow args JSON: {json.dumps(flow_args)}")
    return flow_args

def parse_requirements(req_str: Optional[str]) -> Dict[str, Any]:
    """Parse the --requirements into a dict.
    Accepted input examples:
      "[plan_pages:50, hpplus:activate, flip_shipping:skip]"
      "plan_pages:50,hpplus:activate"
      "plan_pages:50" (single)
    Rules:
      - Outer brackets [] optional.
      - Items separated by comma.
      - Each item key:value (first ':' splits key and value only).
      - Keys normalized to snake_case; values kept as string except numeric digits -> int.
      - Empty / malformed entries ignored.
    """
    if not req_str:
        return {}
    text = req_str.strip()
    if text.startswith('[') and text.endswith(']'):
        text = text[1:-1]
    parts = [p.strip() for p in text.split(',') if p.strip()]
    result: Dict[str, Any] = {}
    for part in parts:
        if ':' not in part:
            framework_logger.debug(f"Ignoring requirement entry without colon: {part}")
            continue
        key, value = part.split(':', 1)
        key = to_snake_case(key.strip())
        value = value.strip()
        if re.fullmatch(r"-?\d+", value):
            try:
                num = int(value)
                value = num
            except ValueError:
                pass
        if key:
            result[key] = value
    framework_logger.debug(f"Parsed requirements: {result}")
    return result

def to_snake_case(name: str) -> str:
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()

def add_flow(flow_name: str) -> None:
    base_dir = os.path.join(Constants.TEST_FLOWS_PATH, flow_name)
    test_data_dir = os.path.join(base_dir, "test_data")
    sample_dir = os.path.join(test_data_dir, "zSample")
    os.makedirs(sample_dir, exist_ok=True)
    snake_file = to_snake_case(flow_name)
    flow_file = os.path.join(base_dir, f"{snake_file}.py")
    rel_path = f"test_flows/{flow_name}/{snake_file}.py"
    if not os.path.exists(flow_file):
        with open(flow_file, "w", encoding="utf-8") as f:
            f.write(f"# {rel_path}\n\n")
    init_file = os.path.join(base_dir, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w", encoding="utf-8") as f:
            f.write("")
    spreadsheet_name = f"{snake_file}_testdata.xlsx"
    spreadsheet_path = os.path.join(sample_dir, spreadsheet_name)
    if not os.path.exists(spreadsheet_path):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sheet1"
        wb.save(spreadsheet_path)

    print(f"Created flow structure for '{flow_name}' at {base_dir} (main file: {snake_file}.py, sample spreadsheet: {spreadsheet_name} in test_data/zSample)")

def process_yaml(base_yaml, selected_batches=None):  
    """  
    Process the YAML file and execute commands for the specified batches.  
     
    :param base_yaml: Path to the YAML file.  
    :param selected_batches: List of batch names to execute (None means execute all).  
    """  
    with open(base_yaml, 'r') as yaml_file:  
        data = yaml.safe_load(yaml_file)  
     
    batches = data.get('batches', [])  
     
    for batch in batches:  
        name = batch.get('name')  
        files = batch.get('files', [])  
         
        # Skip batches not in the selected list (if specified)  
        if selected_batches and name not in selected_batches:
            print(f"Batch name - {name} not found")  
            continue  
         
        print(f"Processing Batch: {name}")  
         
        # Execute the Python command for each file in the batch  
        for file in files:  
            print(f"\tExecuting file: {file}")  
             
            try:  
                # subprocess.run(['pytest', '-s -v test_case_execute.py', file], check=True)  
                print("\t", "-" * 75)
            except subprocess.CalledProcessError as e:  
                print(f"Error occurred while processing {file}: {e}")

def aura() -> None:
    
    args = parse_args()

    if args.base_yaml:
        print ("Test will be executed from YAML based approach.") 
        base_yaml = args.base_yaml
        selected_batch = args.batch_name if args.batch_name else None
        process_yaml(base_yaml, selected_batch)

    else:
        if hasattr(args, "debug") and args.debug:
            set_framework_log_level(logging.DEBUG)
            framework_logger.debug("Debug logging enabled via --debug")
        if hasattr(args, "addflow") and args.addflow:
            add_flow(args.addflow)
            return
        try:
            flow_args = build_flow_args(args)
            framework_logger.info(f"Flow arguments: {json.dumps(flow_args, indent=2)}")
            if args.mode == "scrape":
                run_scrape_mode(args.flow, flow_args)
            elif args.mode == "validate":
                run_validate_mode(args.flow, flow_args)
            elif args.mode == "noop":
                run_noop_mode(args.flow, flow_args)
            else:
                framework_logger.error(f"Invalid mode: {args.mode}")
                sys.exit(1)
        except FlowConfigError as e:
            framework_logger.error(str(e))
            sys.exit(1)
        except Exception:
            framework_logger.error(f"Unhandled exception:\n{traceback.format_exc()}")
            sys.exit(1)

if __name__ == "__main__":
    aura()