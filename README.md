# Graph API Data Fetcher

## Overview
The **Graph API Data Fetcher** is a Python-based ETL tool designed to extract data from the **Facebook and Instagram Graph API (v22.0)**. It automates data fetching for:

- **Facebook Page Insights & Posts**
- **Instagram Business Insights & Reels**
- **Facebook Ads & Campaign Performance**
- **Multi-threaded Ads Insights Processing**

This tool supports **long-lived token management**, **rate-limit handling**, and **secure storage**.

---

## Features
✅ **Fetch Facebook Page & Post Insights**  
✅ **Retrieve Instagram Account & Media Metrics**  
✅ **Fetch Facebook Ads Campaigns, Ad Sets, and Insights**  
✅ **Automated Long-Lived Token Refresh with Encryption**  
✅ **Handles API Rate Limits & Retries on Errors**  
✅ **Multi-Threaded Execution for Faster Data Processing**

---

## Installation
### 1️⃣ Clone the Repository
```sh
git clone https://github.com/luisfreitas213/graph-api-data-fetcher
cd graph-api-data-fetcher
```

### 2️⃣ Create a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # On Mac/Linux
venv\Scripts\activate    # On Windows
```

### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

---

## Configuration
This application requires **environment variables** to be set. You can do this by creating a `.env` file or setting them manually.

### **Required Environment Variables**
```ini
PAGE_ID=your_facebook_page_id
PAGE_NAME=your_page_name
ADS_ACCOUNT=your_ads_account_id
ACCESS_TOKEN=your_facebook_access_token
FB_APP_ID=your_facebook_app_id
FB_APP_SECRET=your_facebook_app_secret
NUM_MONTHS_DATA=3
ETL_MODE=social  # Options: "social" (for pages & posts) or "ads" (for ads data)
```

### **Setting Environment Variables Manually**
For Linux/macOS:
```sh
export PAGE_ID="your_facebook_page_id"
export PAGE_NAME="your_page_name"
export ADS_ACCOUNT="your_ads_account_id"
export ACCESS_TOKEN="your_facebook_access_token"
export FB_APP_ID="your_facebook_app_id"
export FB_APP_SECRET="your_facebook_app_secret"
export NUM_MONTHS_DATA=3
export ETL_MODE="social"
```
For Windows:
```sh
set PAGE_ID="your_facebook_page_id"
set PAGE_NAME="your_page_name"
set ADS_ACCOUNT="your_ads_account_id"
set ACCESS_TOKEN="your_facebook_access_token"
set FB_APP_ID="your_facebook_app_id"
set FB_APP_SECRET="your_facebook_app_secret"
set NUM_MONTHS_DATA=3
set ETL_MODE="social"
```

### **Configurable Storage Locations**
The **output folder structure** for raw data storage is defined in `config/config.py`:
```python
OUTPUT_PATH = Path(f"/datalake/raw/graph/{PAGE_NAME}")
```

---
## External Libraries in `requirements.txt`
This project relies on the following external dependencies:

| Package | Version | Description |
|---------|---------|-------------|
| **requests** | 2.32.3 | Handles HTTP requests to interact with the Facebook Graph API. |
| **python-dateutil** | 2.9.0 | Provides powerful extensions to work with date/time handling. |
| **cryptography** | 44.0.1 | Encrypts and securely stores tokens for authentication. |

Ensure all dependencies are installed using:
```sh
pip install -r requirements.txt
```
To manually install a specific package, use:
```sh
pip install package_name
```

---

## Usage
Run the ETL process with:
```sh
python src/main.py
```

The script automatically detects the `ETL_MODE`:
- `social` → Fetches **Facebook & Instagram Page Insights**
- `ads` → Fetches **Facebook Ads & Campaign Performance**

---

## Data Extraction Process
### 🔹 **Facebook Page & Posts**
- Fetch **Page Metrics** (likes, engagement, impressions, etc.)
- Retrieve **Posts & Attachments**
- Collect **Post-Level Metrics**

### 🔹 **Instagram Data**
- Fetch **Instagram Business Account Details**
- Retrieve **Instagram Media (Posts & Reels)**
- Collect **Insights for Posts & Reels**

### 🔹 **Facebook Ads & Campaigns**
- Retrieve **Campaigns, Ad Sets, and Ads**
- Fetch **Ad Creatives (Thumbnails, Titles, etc.)**
- Collect **Ad Insights (Clicks, CTR, CPC, Reach, etc.)**
- Store **Monthly Insights for historical analysis**

---

## Folder Structure
```
graph-api-data-fetcher/
│── src/
│   ├── auth/                # Token Management & Authentication
│   ├── config/              # Configuration & Environment Variables
│   ├── extract/             # API Client for Fetching Data
│   ├── utils/               # Utility Functions
│   ├── graph_etl/           # ETL Pipeline
│   ├── main.py              # Main Entry Point
│── requirements.txt         # Python Dependencies
│── README.md                # Documentation
```

---

## Error Handling & Logging
- **If API errors occur**, the script logs them and continues execution.
- **Rate limits** are handled with **exponential backoff retries**.
- **If token issues arise**, the script refreshes or prompts for a new one.

---

## Token Management
This tool manages **long-lived tokens** securely:
- If a **token file exists**, it refreshes the **long-lived token** and updates it.
- If **no token is found**, it generates a **new long-lived token** using a short-lived token.
- Tokens are **stored with encryption** for security.

---

## Running with Docker
You can deploy this tool using **Docker**:

### **1️⃣ Build the Docker Image**
```sh
docker build -t graph-api-data-fetcher .
```

### **2️⃣ Run the Docker Container**
```sh
docker run --env-file .env graph-api-data-fetcher
```

---

## License
📜 **MIT License** - Free to use and modify! 🚀

---

**Maintainer:** Luís Freitas
