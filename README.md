<<<<<<< HEAD
# 🐍 PyAutomate v2.0 — AI-Powered Desktop Automation Suite

A full-stack Python automation dashboard with Flask backend and Bootstrap 5 frontend.

## 🚀 Features

| Module | Description |
|--------|-------------|
| 📂 **File Organizer** | Auto-organize Downloads into categories |
| 📧 **Email Sender** | Send bulk personalized emails via SMTP |
| 🌐 **Web Scraper** | Weather, News headlines, Stock prices |
| 📊 **Kaggle Finder** | Search & download ML datasets from Kaggle |
| 🎤 **Meeting Summarizer** | Transcribe & summarize meeting recordings |

## ⚙️ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure credentials
cp .env .env.local   # then edit .env with your credentials

# 3. Run the app
python app.py

# 4. Open browser
# http://localhost:5000
```

## 🔑 Configuration

Edit `.env` with your credentials:

```
FLASK_SECRET_KEY=your-secret-key
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
KAGGLE_USERNAME=your-kaggle-username
KAGGLE_KEY=your-kaggle-api-key
```

### Gmail Setup
Enable 2FA and create an App Password at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

### Kaggle API Setup
1. Go to [kaggle.com/account](https://www.kaggle.com/account)
2. Scroll to API section → Click "Create New Token"
3. Copy `username` and `key` from downloaded `kaggle.json`

## 📁 Project Structure

```
PyAutomate/
├── app.py                     # Flask app entry point
├── config.py                  # Global configuration
├── setup_project.py           # One-click setup script
├── requirements.txt
├── .env                       # Credentials (never commit!)
├── modules/
│   ├── file_organizer.py
│   ├── email_sender.py
│   ├── web_scraper.py
│   ├── kaggle_finder.py
│   └── meeting_summarizer.py
├── templates/                 # Jinja2 HTML templates
├── static/css/style.css
├── static/js/
└── data/                      # Output files
```

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/organizer/scan` | POST | Scan files in directory |
| `/api/organizer/organize` | POST | Organize files into folders |
| `/api/scraper/weather` | POST | Get weather for a city |
| `/api/scraper/news` | POST | Get news headlines |
| `/api/scraper/stocks` | POST | Get stock prices |
| `/api/kaggle/recommend` | POST | Get ML dataset recommendations |
| `/api/kaggle/search` | POST | Search Kaggle datasets |
| `/api/kaggle/download` | POST | Download a Kaggle dataset |
| `/api/meeting/analyze` | POST | Analyze meeting transcript |
=======
# PyAutomate
Desktop Automation Tools
>>>>>>> 783d23198f31eb6514dcc2c435d2355009cb74bb
