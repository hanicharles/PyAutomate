"""
FILE: app.py
PURPOSE: Flask application entry point for PyAutomate v2.0
"""

import os
import logging
from pathlib import Path
from datetime import datetime

from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, flash, send_file,
)
from flask_cors import CORS

from config import (
    FLASK_SECRET, FLASK_DEBUG, FLASK_PORT,
    DOWNLOADS_DIR, SCRAPER_OUTPUT_DIR,
    MEETING_OUTPUT_DIR, KAGGLE_DOWNLOAD_DIR,
    LOG_FILE, LOGS_DIR, LOG_FORMAT, LOG_DATE_FORMAT,
)

# ── Initialize Flask ──
app = Flask(__name__)
app.secret_key = FLASK_SECRET
CORS(app)

# ── Logging ──
os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("PyAutomate")

# ── Import Modules ──
from modules.file_organizer import FileOrganizer
from modules.kaggle_finder import KaggleFinder

try:
    from modules.web_scraper import WebScraper
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False

try:
    from modules.meeting_summarizer import MeetingSummarizer
    MEETING_AVAILABLE = True
except Exception as e:
    logger.error(f"Failed to import MeetingSummarizer: {e}")
    MEETING_AVAILABLE = False


# ══════════════════════════════════════════════════════
# ROUTES — PAGES
# ══════════════════════════════════════════════════════

@app.route("/")
def index():
    stats = {
        "downloads_files": _count_files(DOWNLOADS_DIR),
        "scraped_files": _count_files(SCRAPER_OUTPUT_DIR),
        "meeting_files": _count_files(MEETING_OUTPUT_DIR),
        "kaggle_datasets": _count_files(KAGGLE_DOWNLOAD_DIR),
    }
    return render_template("index.html", stats=stats)


@app.route("/file-organizer")
def file_organizer_page():
    return render_template("file_organizer.html")


@app.route("/email-sender")
def email_sender_page():
    return render_template("email_sender.html")


@app.route("/register")
def registration_page():
    return render_template("registration_page.html")


@app.route("/visitor-form")
def visitor_form_page():
    return render_template("visitor_form.html")


@app.route("/api/email/qr")
def api_email_qr():
    import qrcode
    from io import BytesIO
    
    # Get server address (fallback to localhost if not found)
    # In a real scenario, you'd want the external IP here
    server_url = "https://forms.gle/4yCwNX8NLdaboAR76"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(server_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    
    return send_file(buf, mimetype="image/png")


@app.route("/web-scraper")
def web_scraper_page():
    return render_template("web_scraper.html")


@app.route("/kaggle")
def kaggle_page():
    kaggle = KaggleFinder()
    categories = kaggle.get_ml_categories()
    history = kaggle.get_download_history()
    return render_template("kaggle_finder.html", categories=categories, history=history)


@app.route("/meeting")
def meeting_page():
    return render_template("meeting_summarizer.html")


@app.route("/settings")
def settings_page():
    return render_template("settings.html")


# ══════════════════════════════════════════════════════
# API ROUTES — FILE ORGANIZER
# ══════════════════════════════════════════════════════

@app.route("/api/organizer/scan", methods=["POST"])
def api_scan_files():
    data = request.json or {}
    source = data.get("source_dir", str(DOWNLOADS_DIR))

    organizer = FileOrganizer(source_dir=source)
    files = organizer.scan_files()

    file_list = []
    categories = {}
    for f in files:
        cat = organizer.get_category(f.suffix)
        categories.setdefault(cat, []).append(f.name)
        file_list.append({
            "name": f.name,
            "size": f"{f.stat().st_size / 1024:.1f} KB",
            "extension": f.suffix,
            "category": cat,
        })

    return jsonify({
        "success": True,
        "total_files": len(files),
        "files": file_list,
        "categories": {k: len(v) for k, v in categories.items()},
        "source_dir": source,
    })


@app.route("/api/organizer/organize", methods=["POST"])
def api_organize_files():
    data = request.json or {}
    source = data.get("source_dir", str(DOWNLOADS_DIR))

    organizer = FileOrganizer(source_dir=source)
    files = organizer.scan_files()
    organizer.organize_files(files)

    return jsonify({
        "success": True,
        "organized": organizer.organized,
        "skipped": organizer.skipped,
        "errors": organizer.errors,
        "log": organizer.log_entries,
    })


# ══════════════════════════════════════════════════════
# API ROUTES — EMAIL SENDER
# ══════════════════════════════════════════════════════

@app.route("/api/email/preview", methods=["GET"])
def api_email_preview():
    from modules.email_sender import EmailSender
    sender = EmailSender()
    recipients = sender.preview_recipients()
    return jsonify({"success": True, "recipients": recipients, "count": len(recipients)})


@app.route("/api/email/send-single", methods=["POST"])
def api_email_send_single():
    data = request.json or {}
    from modules.email_sender import EmailSender
    sender = EmailSender()
    result = sender.send_single(
        to_email=data.get("email", ""),
        subject=data.get("subject", ""),
        body=data.get("body", ""),
        name=data.get("name", ""),
    )
    return jsonify(result)


@app.route("/api/email/send-bulk", methods=["POST"])
def api_email_send_bulk():
    from modules.email_sender import EmailSender
    sender = EmailSender()
    result = sender.send_bulk()
    return jsonify(result)


@app.route("/api/visitor/submit", methods=["POST"])
def api_visitor_submit():
    data = request.json or {}
    name = data.get("name")
    email = data.get("email")
    reason = data.get("reason")
    
    if not all([name, email, reason]):
        return jsonify({"success": False, "error": "Missing required fields"})
    
    # 1. Save to Excel
    import pandas as pd
    excel_path = Path("data/visitors.xlsx")
    os.makedirs("data", exist_ok=True)
    
    new_data = {
        "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "Name": [name],
        "Email": [email],
        "Reason": [reason]
    }
    df_new = pd.DataFrame(new_data)
    
    try:
        if excel_path.exists():
            df_old = pd.read_excel(excel_path)
            df_final = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_final = df_new
        df_final.to_excel(excel_path, index=False)
    except Exception as e:
        logger.error(f"Failed to save to Excel: {e}")
        # Continue anyway, email is more important
        
    # 1.5 Save to recipients.csv
    csv_path = Path("data/recipients.csv")
    try:
        if not csv_path.exists():
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write("Name,Email,Subject,Message,\n")
        
        with open(csv_path, 'a', encoding='utf-8') as f:
            clean_name = str(name).replace(',', '')
            clean_email = str(email).replace(',', '')
            clean_reason = str(reason).replace(',', '')
            f.write(f"{clean_name},{clean_email},Visitor Alert,Hi {clean_name} thanks for visiting. Reason: {clean_reason},\n")
    except Exception as e:
        logger.error(f"Failed to save to recipients CSV: {e}")
    
    # 2. Send immediate email
    from modules.email_sender import EmailSender
    sender = EmailSender()
    subject = f"Visitor Registration: {name}"
    body = f"Hi {name},\n\nThank you for visiting us today.\n\nYour stated reason for visit: {reason}\n\nWe have registered your details successfully.\n\nBest regards,\nPyAutomate System"
    
    email_result = sender.send_single(email, subject, body, name)
    
    return jsonify({"success": True, "email_sent": email_result.get("success", False)})


@app.route("/api/visitor/list", methods=["GET"])
def api_visitor_list():
    import pandas as pd
    excel_path = Path("data/visitors.xlsx")
    if not excel_path.exists():
        return jsonify({"success": True, "visitors": []})
    
    try:
        df = pd.read_excel(excel_path)
        # Get last 10 visitors, most recent first
        visitors = df.tail(10).to_dict('records')
        visitors.reverse()
        return jsonify({"success": True, "visitors": visitors})
    except Exception as e:
        logger.error(f"Failed to read visitors: {e}")
        return jsonify({"success": False, "error": str(e)})


# ══════════════════════════════════════════════════════
# API ROUTES — WEB SCRAPER
# ══════════════════════════════════════════════════════

@app.route("/api/scraper/weather", methods=["POST"])
def api_scrape_weather():
    data = request.json or {}
    city = data.get("city", "London")

    scraper = WebScraper()
    result = scraper.scrape_weather(city)

    if result:
        scraper.save_to_csv("weather", result)
        scraper.save_to_docx("weather", result)

    return jsonify({"success": bool(result), "data": result})


@app.route("/api/scraper/news", methods=["POST"])
def api_scrape_news():
    data = request.json or {}
    topic = data.get("topic", "general")

    scraper = WebScraper()
    result = scraper.scrape_news(topic)

    if result:
        scraper.save_to_csv("news", result)

    return jsonify({"success": bool(result), "data": result})


@app.route("/api/scraper/stocks", methods=["POST"])
def api_scrape_stocks():
    data = request.json or {}
    symbols = data.get("symbols", ["AAPL"])

    scraper = WebScraper()
    result = scraper.scrape_stocks(symbols)

    if result:
        scraper.save_to_csv("stocks", result)

    return jsonify({"success": bool(result), "data": result})


# ══════════════════════════════════════════════════════
# API ROUTES — KAGGLE
# ══════════════════════════════════════════════════════

@app.route("/api/kaggle/recommend", methods=["POST"])
def api_kaggle_recommend():
    data = request.json or {}
    topic = data.get("topic", "")
    kaggle = KaggleFinder()
    result = kaggle.recommend_for_topic(topic)
    return jsonify(result)


@app.route("/api/kaggle/search", methods=["POST"])
def api_kaggle_search():
    data = request.json or {}
    query = data.get("query", "")
    sort_by = data.get("sort_by", "hottest")
    kaggle = KaggleFinder()
    result = kaggle.search_datasets(query, sort_by=sort_by)
    return jsonify(result)


@app.route("/api/kaggle/download", methods=["POST"])
def api_kaggle_download():
    data = request.json or {}
    dataset_name = data.get("dataset", "")
    if not dataset_name:
        return jsonify({"success": False, "error": "No dataset specified"})
    kaggle = KaggleFinder()
    result = kaggle.download_dataset(dataset_name)
    return jsonify(result)


@app.route("/api/kaggle/preview", methods=["POST"])
def api_kaggle_preview():
    data = request.json or {}
    file_path = data.get("file_path", "")
    kaggle = KaggleFinder()
    result = kaggle.preview_dataset(file_path)
    return jsonify(result)


@app.route("/api/kaggle/categories")
def api_kaggle_categories():
    kaggle = KaggleFinder()
    return jsonify(kaggle.get_ml_categories())


@app.route("/api/kaggle/history")
def api_kaggle_history():
    kaggle = KaggleFinder()
    return jsonify({
        "downloads": kaggle.get_download_history(),
        "searches": kaggle.get_search_history(),
    })


# ══════════════════════════════════════════════════════
# API ROUTES — MEETING SUMMARIZER
# ══════════════════════════════════════════════════════

@app.route("/api/meeting/analyze", methods=["POST"])
def api_analyze_meeting():
    data = request.json or {}
    transcript = data.get("transcript", "")

    if not transcript:
        return jsonify({"success": False, "error": "No transcript provided"})

    summarizer = MeetingSummarizer()
    summarizer.set_transcript(transcript)
    result = summarizer.analyze_transcript()

    if result:
        summarizer.save_docx()
        summarizer.save_txt()
        summarizer.save_csv()

    return jsonify({"success": bool(result), "data": result})


@app.route("/api/meeting/detailed-notes", methods=["POST"])
def api_detailed_notes():
    data = request.json or {}
    transcript = data.get("transcript", "")
    summary = data.get("summary", "")

    if not transcript:
        return jsonify({"success": False, "error": "No transcript provided"})

    summarizer = MeetingSummarizer()
    summarizer.set_transcript(transcript)
    summarizer.summary = summary
    notes = summarizer.generate_detailed_notes()
    
    if notes:
        summarizer.save_detailed_notes()
        return jsonify({"success": True, "notes": notes})
    return jsonify({"success": False, "error": "Failed to generate detailed notes"})


@app.route("/api/meeting/chat", methods=["POST"])
def api_meeting_chat():
    data = request.json or {}
    transcript = data.get("transcript", "")
    summary = data.get("summary", "")
    question = data.get("question", "")

    if not question:
        return jsonify({"success": False, "error": "No question provided"})
    if not transcript:
        return jsonify({"success": False, "error": "No transcript context available"})

    summarizer = MeetingSummarizer()
    summarizer.set_transcript(transcript)
    summarizer.summary = summary
    answer = summarizer.chat(question)

    return jsonify({"success": True, "answer": answer})


@app.route("/api/meeting/upload", methods=["POST"])
def api_upload_meeting():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"})

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename"})

    upload_dir = MEETING_OUTPUT_DIR / "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    filepath = upload_dir / file.filename
    file.save(str(filepath))

    summarizer = MeetingSummarizer()
    ext = filepath.suffix.lower()
    if ext == ".txt":
        summarizer.load_text_file(filepath)
    elif ext in [".wav", ".mp3", ".flac", ".ogg", ".m4a"]:
        summarizer.load_audio_file(filepath)
    else:
        return jsonify({"success": False, "error": f"Unsupported format: {ext}. Use .mp3, .wav, .flac, .ogg, or .m4a"})

    if summarizer.transcript:
        result = summarizer.analyze_transcript()
        if result:
            summarizer.save_docx()
            summarizer.save_txt()
            summarizer.save_csv()
        return jsonify({"success": bool(result), "data": result})

    return jsonify({"success": False, "error": "Could not process file"})


@app.route("/api/meeting/upload-video", methods=["POST"])
def api_upload_video():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"})
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename"})
    upload_dir = MEETING_OUTPUT_DIR / "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    filepath = upload_dir / file.filename
    file.save(str(filepath))
    ext = filepath.suffix.lower()
    if ext not in [".mp4", ".avi", ".mkv", ".mov", ".webm"]:
        return jsonify({"success": False, "error": f"Unsupported video format: {ext}. Use .mp4, .avi, .mkv, .mov, or .webm"})

    summarizer = MeetingSummarizer()
    if not summarizer.load_video_file(filepath):
        return jsonify({"success": False, "error": "Could not extract/transcribe audio from video. Make sure ffmpeg is installed."})

    if summarizer.transcript:
        result = summarizer.analyze_transcript()
        if result:
            summarizer.save_docx()
            summarizer.save_txt()
            summarizer.save_csv()
        return jsonify({"success": bool(result), "data": result})
    return jsonify({"success": False, "error": "Could not transcribe audio from video"})


# ══════════════════════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════════════════════

def _count_files(directory):
    try:
        return sum(1 for f in Path(directory).rglob("*") if f.is_file())
    except Exception:
        return 0


# ══════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    logger.info(f"PyAutomate v2.0 starting on port {FLASK_PORT}")
    print(f"""
╔══════════════════════════════════════════════════════╗
║                                                      ║
║   🐍 PyAutomate v2.0 — Web Dashboard                ║
║                                                      ║
║   🌐 Open: http://localhost:{FLASK_PORT}                 ║
║   📝 Logs: logs/activity.log                        ║
║   🛑 Stop: Ctrl + C                                 ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
    """)
    app.run(debug=False, port=FLASK_PORT, host="0.0.0.0")
