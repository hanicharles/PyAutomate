🐍 PyAutomate v2.0
A full-stack Python automation dashboard to manage your desktop workflows, ML datasets, and meeting transcripts.

Python • Flask • Bootstrap • HuggingFace API • Kaggle API

✨ Features
Auto-organize Downloads — categorizes unstructured files automatically based on extensions
Email & Visitor Tracking — bulk emails, custom lists, QR-code based visitor registration flows
Real-time Web Scraper — gather live weather, news, and stock prices
Kaggle Dataset Finder — search, preview, and download ML datasets seamlessly via the Kaggle API
Meeting Summarizer — transcribe, process, and summarize text, audio, and video recordings using Hugging Face LLMs
Study Notes Generator — create actionable, format-friendly, exam-ready notes directly from meeting transcripts
Conversational Transcripts — query and chat dynamically against your active meeting contexts

🗂 Project Structure
PyAutomate/
├── app.py                     # Flask application backend
├── config.py                  # Global path and variables configuration
├── setup_project.py           # Boilerplate installation script
├── sync_google_form.py        # Helper to synchronize visitor tracking lists
├── start_automate.bat         # Windows batch script to start server
├── requirements.txt           # PIP dependencies
├── .env                       # Credential file (Do not commit to version control!)
├── modules/                   # Independent logic modules for each sub-system
│   ├── file_organizer.py
│   ├── email_sender.py
│   ├── web_scraper.py
│   ├── kaggle_finder.py
│   └── meeting_summarizer.py
├── process_transcript.py      # Standalone meeting processor utilizing the HF Inference LLM
├── templates/                 # HTML Dashboard Views (Jinja2)
├── static/
│   ├── css/                   # Front-end styling
│   └── js/                    # Front-end scripting
└── data/                      # Output directory, populated dynamically

🚀 Setup Instructions

Prerequisites
Python 3.8+ → https://www.python.org/downloads/
pip (comes with Python)
ffmpeg (optional, required if processing video/mp3 files)

Step 1 — Clone the project
Place the PyAutomate folder anywhere on your machine.
git clone https://github.com/hanicharles/PyAutomate.git
cd PyAutomate

Step 2 — Configure credentials
Rename `.env.example` or create a `.env` file manually.
Edit `.env`:

FLASK_SECRET_KEY=your-secret-key
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
KAGGLE_USERNAME=your-kaggle-username
KAGGLE_KEY=your-kaggle-api-key
HF_TOKEN=your-huggingface-token

Step 3 — Install dependencies
pip install -r requirements.txt

Step 4 — Start the app
python app.py

(Alternatively on Windows: double-click start_automate.bat)
You should see:

✅ PyAutomate v2.0 starting on port 5000

🚀 PyAutomate Web Dashboard
   Backend: http://localhost:5000
   Logs: logs/activity.log

Step 5 — Start the frontend
The app automatically exposes the dashboard view.
Open your browser to http://localhost:5000 🎉

🔑 Configuration Requirements
Gmail Setup
Enable 2-Step Verification and construct an App Password at myaccount.google.com/apppasswords.

Kaggle API Setup
Go to your Kaggle Account Settings.
Scroll to the API section → Click "Create New Token".
Copy the username and key from the downloaded kaggle.json.

Hugging Face API Setup
Go to your Hugging Face Settings.
Generate an access token (Fine-grained or Classic) and include it as HF_TOKEN.

🗄 Data Tracking
All system metrics and files are securely stored locally inside the `data/` directory:

Table / File        Purpose
visitors.xlsx       History of local visitor registrations natively tracked via Excel
recipients.csv      Email mailing lists and contact logs tracking
scraper_output/     Exported weather, news, and stock dumps in CSV & DOCX
meeting_output/     Meeting transcripts, detailed notes, text files, and summaries
kaggle_downloads/   Storage location of all downloaded ML datasets

🔌 API Endpoints
Method	Path	Description
POST	/api/organizer/scan        Scan files in directory prior to modification
POST	/api/organizer/organize    Sort identified loose files into folders
POST	/api/scraper/weather       Fetch daily weather statistics by region
POST	/api/scraper/stocks        Return latest ticker evaluation
POST	/api/kaggle/search         Find datasets dynamically over API
POST	/api/kaggle/download       Process local download of datasets
POST	/api/meeting/analyze       Process raw text transcripts against intelligent context models
POST	/api/meeting/upload        Send local video/audio files to be chunked, parsed, and logged
POST	/api/meeting/detailed-notes Automatically generate exhaustive exam-ready study outlines
POST	/api/meeting/chat          Run conversational queries against the active meeting context
POST	/api/visitor/submit        Appends visitor to CSV datastores, triggers downstream email workflows

🔧 Troubleshooting
Browser CORS or connection issues:
Ensure the Flask backend is started and you are accessing it via localhost:5000.

Media Processing Errors:
If your video/audio files fail to transcribe, ensure ffmpeg is correctly installed and added to your system PATH.

API Authentication Errors:
Ensure HF_TOKEN, KAGGLE_KEY, and EMAIL_PASSWORD are set correctly in your `.env` file without any extra accidental spaces or quotes.

🔒 Security Notes
API credentials are stored entirely in your local `.env` file — never commit this file to GitHub!
All external API calls (HuggingFace, Kaggle, SMTP) are made server-side (backend), ensuring your API keys are never exposed in the browser.
Local visitors and scraped data remain securely restricted to your own local disk environment.
