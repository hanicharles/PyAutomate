"""
FILE: setup_project.py
PURPOSE: One-click project setup for PyAutomate v2.0
"""

import os
import sys
import json
import subprocess


def create_all_directories():
    dirs = [
        "modules",
        "templates", "templates/components",
        "static", "static/css", "static/js", "static/images",
        "data", "data/scraper_output",
        "data/scraper_output/weather", "data/scraper_output/news",
        "data/scraper_output/cricket", "data/scraper_output/stocks",
        "data/meeting_output", "data/kaggle_downloads",
        "logs", "tests",
    ]
    print("\n📁 Creating directories...")
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"  ✅ {d}/")


def create_env_file():
    env_content = """FLASK_SECRET_KEY=your-secret-key-change-this
FLASK_DEBUG=True
FLASK_PORT=5000
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
KAGGLE_USERNAME=your-kaggle-username
KAGGLE_KEY=your-kaggle-api-key
"""
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(env_content)
        print("  ✅ .env")
    else:
        print("  ℹ️  .env already exists")


def create_sample_data():
    if not os.path.exists("data/recipients.csv"):
        with open("data/recipients.csv", "w") as f:
            f.write("name,email,subject,message\n")
            f.write("John,john@example.com,Report,Hi {name} your report is ready.\n")
            f.write("Jane,jane@example.com,Meeting,Hi {name} meeting at 3PM.\n")
        print("  ✅ data/recipients.csv")

    if not os.path.exists("data/preferences.json"):
        with open("data/preferences.json", "w") as f:
            json.dump({}, f)
        print("  ✅ data/preferences.json")

    if not os.path.exists("data/kaggle_cache.json"):
        with open("data/kaggle_cache.json", "w") as f:
            json.dump({"searches": [], "downloads": []}, f, indent=2)
        print("  ✅ data/kaggle_cache.json")


def install_packages():
    print("\n📦 Installing packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("  ✅ All packages installed!")
    except subprocess.CalledProcessError:
        print("  ⚠️  Some packages failed. Install manually.")
    except FileNotFoundError:
        print("  ⚠️  requirements.txt not found.")


def main():
    print("╔══════════════════════════════════════════════════╗")
    print("║     🐍 PyAutomate v2.0 — Project Setup          ║")
    print("╚══════════════════════════════════════════════════╝")

    create_all_directories()
    create_env_file()
    create_sample_data()

    install_choice = input("\n📦 Install Python packages? (y/n): ").strip().lower()
    if install_choice == "y":
        install_packages()

    print("\n" + "═" * 55)
    print("  🎉 Setup complete!")
    print("  📝 Configure .env with your credentials")
    print("  🚀 Run: python app.py")
    print("═" * 55)


if __name__ == "__main__":
    main()
