import yaml

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)
  
# Function to filter printers based on description  
def get_printers_by_description(config, description):  
    # Get the 'printers' list from the config  
    printers = config.get("printers", [])

    # Find the dictionary in the list that contains the 'pie' key  
    pie_printers = next((item.get("pie", []) for item in printers if "pie" in item), [])  

    if not pie_printers:
        return []

    # Case 1: pie is a single dict
    if isinstance(pie_printers, dict):
        if pie_printers.get("description") == description:
            return [{
                "model": pie_printers.get("model"),
                "serial_number": pie_printers.get("serial_number")
            }]
        return []

    # Case 2: pie is a list of dicts
    elif isinstance(pie_printers, list):
        return [
            {"model": printer.get("model"), "serial_number": printer.get("serial_number")}
            for printer in pie_printers
            if isinstance(printer, dict) and printer.get("description") == description
        ]

    return []
