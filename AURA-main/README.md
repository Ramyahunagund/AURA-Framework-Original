# Instant Ink AURA Framework

UI scraping and validation framework for HP Instant Ink flows.

---

## 🔧 Features

- 📊 Excel-based test data and reporting
- 🌍 Locale- and language-aware execution
- 🖨  Virtual Printer support with SKU filtering
- 📸 Screenshot capture and visual diffing
- 🧪 Scrape, Validate and NOOP modes
- 📂 Structured flow and result directories
- 🖥 Device/OS simulation (web, Android, iOS, etc.) using OSS simulator
- 🪵 Centralized logging
- 🧩 Extensible flows and modular codebase

---

## Directory Structure

```
AURA/
│
├── core/
│   ├── scraper.py
│   ├── settings.py
│   ├── utils.py
│   └── validator.py
│
├── test_flows/
│   ├── CreateV3Account/
│   │   ├── create_v3_account.py
│   │   └── test_data/
│   │       ├── en-US/
│   │       │   ├── create_v3_account_testdata.xlsx
│   │       │   └── screenshots/
│   │       │       ├── plan_selection_en-US_full_page.png
│   │       │       └── ...
│   │       └── ... (other locales)
│   ├── CreateIISubscription/
│   │   ├── create_ii_subscription.py
│   │   └── test_data/
│   │       └── ...
│   └── ... (other flows)
│
├── test_flows_exec_results/
│   ├── CreateV3Account_en-US_<timestamp>/
│   │   ├── validation_screenshots/
│   │   │   ├── plan_selection_en-US_full_page.png
│   │   ├── validation_failure_screenshots/
│   │   │   ├── fail_0000_plan_selection_en-US_full_page.png
│   │   ├── validation_results.xlsx
│   │   └── validation_results.html
│   └── ...
│
├── z_scraped_data/
│   ├── CreateV3Account/
│   │   ├── en-US/
│   │   │   ├── <timestamp>/
│   │   │   │   ├── screenshots/
│   │   │   │   │   ├── ...
│   │   │   │   └── scrape_data.xlsx
│   │   └── ... (older runs)
│   └── ...
│
├── test_flows_common/
│   ├── test_flows_common.py
│   ├── .env
│   ├── address_data.json
│   ├── locale_map.json
│   ├── printer_profiles.json
│   ├── credentials.json
│   └── token.json
│
├── logs/
│   └── ...
│
├── aura.py
├── help.html
├── README.md
└── requirements.txt
```

---

## 🚀 Quick Start

### 1. Install dependencies

```powershell
pip install -r requirements.txt
python -m playwright install
```

### 2. Run a flow (example)

**Scrape Mode:**
```powershell
python aura.py --flow CreateV3Account --mode scrape --stack stage --locale "United States" --headless
```

**Validate Mode:**
```powershell
python aura.py --flow CreateIISubscription --mode validate --stack pie --locale Australia --printer_profile novelli --easy_enroll yes
```

See all options:
```powershell
python aura.py --help
```

### 3. Results
- Scraped data and screenshots: `z_scraped_data/`
- Validation results: `test_flows_exec_results/<flow>_<locale>_<timestamp>/`
- Logs: `logs/framework.log`

---

## Arguments

- `--flow`: Name of the test flow (folder inside `test_flows/`)
- `--mode`: `scrape`, `validate`, or `noop`
- `--stack`: `stage` or `pie`
- `--locale`: Country name (e.g., United States)
- `--language`: Language code (optional)
- `--printer_profile`: Printer profile name (optional)
- `--easy_enroll`: `yes` or `no` (optional)
- `--headless`: Run browser in headless mode
- `--biz_model`: `Flex` (default) or `E2E`
- `--target`: OSS Platforms
- `--addflow`: "FlowName" to create all the directories and sample files in test_flows

---

## 📝 Requirements

- Python 3.8+
- Playwright
- openpyxl
- Pillow