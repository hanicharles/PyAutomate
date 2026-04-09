# 🐍 PyAutomate v2.0 — AI-Powered Desktop Automation Suite

A full-stack Python automation dashboard with Flask backend and Bootstrap 5 frontend. PyAutomate acts as a comprehensive productivity hub for common desktop tasks. 

## 🚀 Features

| Module | Description |
|--------|-------------|
| 📂 **File Organizer** | Automatically organize unstructured Downloads directories into neatly categorized folders. |
| 📧 **Email Sender & Visitor Tracking** | Send bulk personalized emails from custom lists. Includes QR-code based registration flows and tracking. |
| 🌐 **Web Scraper** | Gather and query real-time data including weather, news headlines, and stock prices. |
| 📊 **Kaggle Finder** | Search, preview, and download Machine Learning datasets seamlessly via the Kaggle API. |
| 🎤 **Meeting Summarizer** | Transcribe and summarize meeting recordings (text, audio, video). Backed by Llama 3 via Hugging Face Inference API. Query your transcript and generate actionable/exam-ready study notes directly in the brower! |

## ⚙️ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure credentials
# Copy .env configuration variables
cp .env .env.local   # or simply rename '.env' and populate your keys

# 3. Start the application
python app.py

# Alternatively, run via batch script on Windows:
start_automate.bat

# 4. Open in Browser
# http://localhost:5000
```

## 🔑 Configuration (.env setup)

Make sure you create an `.env` file in the root directory based on the following pattern before running:

```ini
FLASK_SECRET_KEY=your-secret-key
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
KAGGLE_USERNAME=your-kaggle-username
KAGGLE_KEY=your-kaggle-api-key
HF_TOKEN=your-huggingface-token
```

### Gmail Configuration
Enable 2-Step Verification and construct an App Password at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).

### Kaggle API Setup
1. Go to your [Kaggle Account Settings](https://www.kaggle.com/account).
2. Scroll to the API section → Click **"Create New Token"**.
3. Copy the `username` and `key` from the downloaded `kaggle.json`.

### Hugging Face API Setup
1. Go to your [Hugging Face Settings](https://huggingface.co/settings/tokens).
2. Generate an access token (Fine-grained or Classic) and include it as `HF_TOKEN`.

## 📁 Project Structure

```
PyAutomate/
├── app.py                     # Flask application backend
├── config.py                  # Global path and variables configuration
├── setup_project.py           # Boilerplate installation script
├── sync_google_form.py        # Helper to synchronize visitor tracking lists
├── start_automate.bat         # Batch script to boot dependencies / the server
├── requirements.txt           # PIP dependencies
├── .env                       # Credential file (Do not commit to version control!)
├── modules/                   # Independent modules for each sub-system
│   ├── file_organizer.py
│   ├── email_sender.py
│   ├── web_scraper.py
│   ├── kaggle_finder.py
│   └── meeting_summarizer.py
├── process_transcript.py      # Standalone meeting processor utilizing the HF Inference LLM
├── templates/                 # Jinja2 HTML Dashboard Views
├── static/css/                # Front-end styling
├── static/js/                 # Front-end scripting
└── data/                      # Output directory, populated iteratively
```

## 🌐 API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/organizer/scan` | POST | Scan files in directory prior to modification |
| `/api/organizer/organize` | POST | Sort identified loose files into folders |
| `/api/scraper/weather` | POST | Fetch daily weather statistics by region |
| `/api/scraper/stocks` | POST | Return latest ticker evaluation |
| `/api/kaggle/search` | POST | Find datasets dynamically over API |
| `/api/kaggle/download` | POST | Process local download of datasets |
| `/api/meeting/analyze` | POST | Process raw text transcripts against intelligent context models |
| `/api/meeting/upload` | POST | Send local video/audio files to be chunked, parsed, and logged |
| `/api/meeting/detailed-notes`| POST | Automatically generate exhaustive, exam-ready study outlines |
| `/api/meeting/chat` | POST | Run conversational queries against the active meeting context |
| `/api/visitor/submit` | POST | Appends visitor to CSV datastores, triggers downstream email workflows |
