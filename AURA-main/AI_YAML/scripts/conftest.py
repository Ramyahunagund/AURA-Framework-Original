# conftest.py

import logging
import os
import pytest
import sys
import yaml

from typing import Dict, Any
from config_loader import load_config

config = load_config(r"config.yaml")

@pytest.fixture(autouse=True, scope="session")
def configure_logging():
    # Remove handlers pytest already attached
    for h in logging.root.handlers[:]:
        logging.root.removeHandler(h)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(config["log_file"]),
            logging.StreamHandler(sys.stdout)
        ]
    )

def pytest_addoption(parser):
    """
    This hook adds a new command-line option for specifying the YAML file.
    """
    parser.addoption(
        "--yaml-file",
        action="store",
        default=None,
        help="Path to the YAML file for test input."
    )

def load_yaml_file(file_path: str) -> Dict[str, Any]:
        """Load and parse YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"YAML file not found: {file_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {e}")
    
def extract_flow_steps(data):
    """
    If the YAML contains flow/steps, return that value.
    Otherwise return the whole document.
    """
    try:
        return data["flow"]["steps"]
    except (KeyError, TypeError):
        return data

def expand_imports(base_path, node):
    """
    Recursively expand any list items containing a 'file' key
    by loading the referenced YAML file.
    """
    if isinstance(node, list):
        expanded = []
        for item in node:
            if isinstance(item, dict) and 'file' in item:
                # file_path = os.path.join(base_path, item['file'])
                file_path = os.path.join(config['common_test_components'], item['file'])                
                print(f"file_path - {file_path}")
                loaded = load_yaml_file(file_path)
                expanded.extend(extract_flow_steps(loaded))
            else:
                expanded.append(expand_imports(base_path, item))
        return expanded
    elif isinstance(node, dict):
        return {k: expand_imports(base_path, v) for k, v in node.items()}
    else:
        return node  # scalar value

def parse_flow(config_path):
    base_dir = os.path.dirname(os.path.abspath(config_path))
    root = load_yaml_file(config_path)
    phases = root.get("flow", {}).get("phases", {})

    # flatten all phases into a single list
    all_steps = []
    for steps in phases.values():
        if steps:
            all_steps.extend(expand_imports(base_dir, steps))

    return {"flow": {"steps": all_steps}}    

@pytest.fixture
def yaml_data(request):
    """
    This fixture reads the YAML file specified by the --yaml-file option
    and returns its content as a Python dictionary.
    """
    yaml_file_path = request.config.getoption("--yaml-file")
    
    if not yaml_file_path:
        pytest.skip("YAML file not provided. Use --yaml-file to specify one.")
    
    try:
        return parse_flow(yaml_file_path)
    except FileNotFoundError:
        pytest.fail(f"YAML file not found at: {yaml_file_path}")
    except yaml.YAMLError as e:
        pytest.fail(f"Error parsing YAML file: {e}")

@pytest.fixture(scope="session")
def yaml_file_path(pytestconfig):
    """
    Session-scoped fixture that returns the file path
    passed with --yaml-file.
    """
    path = pytestconfig.getoption("yaml_file")
    if not path:
        pytest.skip("--yaml-file was not provided")
    return path        