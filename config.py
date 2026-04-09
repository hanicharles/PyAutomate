import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = Path.home() / "Downloads"
DATA_DIR = BASE_DIR / "data"
SCRAPER_OUTPUT_DIR = DATA_DIR / "scraper_output"
MEETING_OUTPUT_DIR = DATA_DIR / "meeting_output"
KAGGLE_DOWNLOAD_DIR = DATA_DIR / "kaggle_downloads"
LOGS_DIR = BASE_DIR / "logs"

FLASK_SECRET = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-me")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
RECIPIENTS_CSV = DATA_DIR / "recipients.csv"

KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME", "")
KAGGLE_KEY = os.getenv("KAGGLE_KEY", "")
KAGGLE_CACHE_FILE = DATA_DIR / "kaggle_cache.json"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

WEATHER_API_URL = "https://wttr.in/{}?format=j1"
NEWS_RSS_URL = "https://news.google.com/rss?hl=en&gl=US&ceid=US:en"
NEWS_SEARCH_URL = "https://news.google.com/rss/search?q={}&hl=en&gl=US&ceid=US:en"
YAHOO_FINANCE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}"
PREFERENCES_FILE = DATA_DIR / "preferences.json"
NOTIFICATION_TIMEOUT = 10

CHUNK_DURATION = 30
MAX_SUMMARY_SENTENCES = 10
MIN_SUMMARY_SENTENCES = 3
KEYWORDS_COUNT = 10
MAX_ACTION_ITEMS = 15

FILE_CATEGORIES = {
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".xls",
                  ".pptx", ".csv", ".rtf", ".md", ".epub"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg",
               ".webp", ".ico", ".tiff", ".psd"],
    "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv",
               ".webm", ".m4v"],
    "Music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".iso"],
    "Code": [".py", ".js", ".ts", ".html", ".css", ".java", ".cpp",
             ".c", ".go", ".rs", ".json", ".xml", ".yaml", ".sql"],
    "Datasets": [".csv", ".tsv", ".parquet", ".h5", ".hdf5",
                 ".feather", ".pkl", ".npy"],
    "Executables": [".exe", ".msi", ".app", ".deb", ".dmg", ".apk"],
}

SKIP_FILES = [".DS_Store", "Thumbs.db", "desktop.ini"]

LOG_FILE = LOGS_DIR / "activity.log"
LOG_FORMAT = "%(asctime)s | %(name)-18s | %(levelname)-7s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
