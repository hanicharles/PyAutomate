"""
FILE: modules/kaggle_finder.py
PURPOSE: Search, recommend, and download Kaggle datasets
"""

import os
import json
import logging
import zipfile
from pathlib import Path
from datetime import datetime

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    KAGGLE_AVAILABLE = True
except ImportError:
    KAGGLE_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

import requests
from config import KAGGLE_DOWNLOAD_DIR, KAGGLE_CACHE_FILE, DATA_DIR

logger = logging.getLogger("KaggleFinder")


CURATED_DATASETS = {
    "image_classification": {
        "display": "🖼️  Image Classification",
        "datasets": [
            {"name": "zalando-research/fashionmnist", "title": "Fashion MNIST",
             "description": "70K grayscale images of 10 clothing categories",
             "size": "30 MB", "usability": 10.0, "priority": 1,
             "tags": ["CNN", "classification", "beginner"]},
            {"name": "gpiosenka/100-bird-species", "title": "100 Bird Species",
             "description": "48,000+ bird images across 525 species",
             "size": "2 GB", "usability": 9.4, "priority": 2,
             "tags": ["CNN", "transfer_learning", "intermediate"]},
            {"name": "paultimothymooney/chest-xray-pneumonia",
             "title": "Chest X-Ray (Pneumonia Detection)",
             "description": "5,863 X-Ray images for medical classification",
             "size": "1.2 GB", "usability": 9.7, "priority": 3,
             "tags": ["medical", "CNN", "binary_classification"]},
            {"name": "moltean/fruits", "title": "Fruits-360",
             "description": "90K images of 131 fruit/vegetable classes",
             "size": "600 MB", "usability": 9.2, "priority": 4,
             "tags": ["CNN", "multiclass", "beginner"]},
        ],
    },
    "nlp_text": {
        "display": "📝 NLP / Text Classification",
        "datasets": [
            {"name": "kazanova/sentiment140", "title": "Sentiment140 (Twitter)",
             "description": "1.6M tweets for sentiment analysis",
             "size": "80 MB", "usability": 8.8, "priority": 1,
             "tags": ["sentiment", "NLP", "beginner"]},
            {"name": "snap/amazon-fine-food-reviews", "title": "Amazon Food Reviews",
             "description": "500K food reviews from Amazon",
             "size": "300 MB", "usability": 9.0, "priority": 2,
             "tags": ["sentiment", "NLP", "intermediate"]},
            {"name": "rmisra/news-category-dataset", "title": "News Category Dataset",
             "description": "200K HuffPost news headlines for classification",
             "size": "60 MB", "usability": 9.5, "priority": 3,
             "tags": ["classification", "NLP", "beginner"]},
            {"name": "lakshmi25npathi/imdb-dataset-of-50k-movie-reviews",
             "title": "IMDB 50K Movie Reviews",
             "description": "50K movie reviews for binary sentiment",
             "size": "66 MB", "usability": 9.8, "priority": 4,
             "tags": ["sentiment", "NLP", "beginner"]},
        ],
    },
    "tabular_regression": {
        "display": "📊 Tabular / Regression",
        "datasets": [
            {"name": "rashikrahmanpritom/heart-attack-analysis-prediction-dataset",
             "title": "Heart Attack Prediction",
             "description": "Heart disease prediction with clinical features",
             "size": "4 KB", "usability": 9.7, "priority": 1,
             "tags": ["classification", "medical", "beginner"]},
            {"name": "fedesoriano/the-boston-houseprice-data",
             "title": "Boston House Prices",
             "description": "Classic regression dataset for house pricing",
             "size": "35 KB", "usability": 9.4, "priority": 2,
             "tags": ["regression", "beginner"]},
            {"name": "shivamb/netflix-shows", "title": "Netflix Shows & Movies",
             "description": "8K+ Netflix titles with metadata",
             "size": "3.5 MB", "usability": 9.6, "priority": 3,
             "tags": ["EDA", "recommendation", "beginner"]},
            {"name": "uciml/iris", "title": "Iris Dataset",
             "description": "Classic ML classification dataset (150 samples)",
             "size": "4 KB", "usability": 10.0, "priority": 4,
             "tags": ["classification", "beginner", "classic"]},
        ],
    },
    "time_series": {
        "display": "📈 Time Series / Forecasting",
        "datasets": [
            {"name": "szrlee/stock-time-series-20050101-to-20171231",
             "title": "Stock Time Series (S&P 500)",
             "description": "Stock prices for all S&P 500 companies",
             "size": "200 MB", "usability": 8.5, "priority": 1,
             "tags": ["stocks", "LSTM", "intermediate"]},
            {"name": "robikscube/hourly-energy-consumption",
             "title": "Hourly Energy Consumption",
             "description": "10+ years of hourly energy data from PJM",
             "size": "8 MB", "usability": 9.1, "priority": 2,
             "tags": ["energy", "forecasting", "intermediate"]},
            {"name": "sumanthvrao/daily-climate-time-series-data",
             "title": "Daily Climate Data",
             "description": "Daily temperature data for Delhi (2013-2017)",
             "size": "100 KB", "usability": 9.3, "priority": 3,
             "tags": ["weather", "forecasting", "beginner"]},
        ],
    },
    "computer_vision": {
        "display": "👁️  Object Detection / Segmentation",
        "datasets": [
            {"name": "andrewmvd/face-mask-detection", "title": "Face Mask Detection",
             "description": "853 images with YOLO annotations",
             "size": "140 MB", "usability": 9.0, "priority": 1,
             "tags": ["YOLO", "detection", "intermediate"]},
            {"name": "sovitrath/road-sign-detection", "title": "Road Sign Detection",
             "description": "Road sign images for autonomous driving",
             "size": "50 MB", "usability": 8.5, "priority": 2,
             "tags": ["YOLO", "detection", "autonomous"]},
        ],
    },
    "recommendation": {
        "display": "🎯 Recommendation Systems",
        "datasets": [
            {"name": "grouplens/movielens-20m-dataset", "title": "MovieLens 20M",
             "description": "20M ratings from 138K users on 27K movies",
             "size": "190 MB", "usability": 9.5, "priority": 1,
             "tags": ["collaborative_filtering", "intermediate"]},
            {"name": "tmdb/tmdb-movie-metadata", "title": "TMDB 5000 Movies",
             "description": "Metadata for 5000 movies from TMDB",
             "size": "6 MB", "usability": 9.2, "priority": 2,
             "tags": ["content_based", "beginner"]},
        ],
    },
    "generative_ai": {
        "display": "🤖 Generative AI / GANs",
        "datasets": [
            {"name": "jessicali9530/celeba-dataset", "title": "CelebA (Celebrity Faces)",
             "description": "200K celebrity face images with attributes",
             "size": "1.4 GB", "usability": 8.8, "priority": 1,
             "tags": ["GAN", "face_generation", "advanced"]},
            {"name": "arnaud58/landscape-pictures", "title": "Landscape Pictures",
             "description": "4,000+ landscape images for generation",
             "size": "500 MB", "usability": 8.0, "priority": 2,
             "tags": ["GAN", "style_transfer", "intermediate"]},
        ],
    },
}


class KaggleFinder:
    """Search, recommend, and download Kaggle datasets."""

    def __init__(self):
        self.api = None
        self.cache = self._load_cache()
        self.download_dir = KAGGLE_DOWNLOAD_DIR
        os.makedirs(self.download_dir, exist_ok=True)
        self._init_api()

    def _init_api(self):
        if not KAGGLE_AVAILABLE:
            logger.warning("Kaggle package not installed")
            return
        try:
            self.api = KaggleApi()
            self.api.authenticate()
            logger.info("Kaggle API authenticated")
        except Exception as e:
            logger.warning(f"Kaggle API auth failed: {e}")
            self.api = None

    def _load_cache(self):
        try:
            if KAGGLE_CACHE_FILE.exists():
                with open(KAGGLE_CACHE_FILE) as f:
                    return json.load(f)
        except Exception:
            pass
        return {"searches": [], "downloads": []}

    def _save_cache(self):
        try:
            with open(KAGGLE_CACHE_FILE, "w") as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Cache save failed: {e}")

    def get_ml_categories(self):
        return [
            {"key": k, "display": v["display"], "count": len(v["datasets"])}
            for k, v in CURATED_DATASETS.items()
        ]

    def get_curated_datasets(self, category):
        if category not in CURATED_DATASETS:
            return []
        return sorted(CURATED_DATASETS[category]["datasets"], key=lambda x: x["priority"])

    def recommend_for_topic(self, topic):
        topic_lower = topic.lower()
        keyword_map = {
            "image_classification": ["image", "picture", "photo", "classify", "cnn",
                                      "convolutional", "recognition", "visual"],
            "nlp_text": ["text", "nlp", "sentiment", "language", "tweet",
                         "review", "classification", "spam", "news", "word"],
            "tabular_regression": ["tabular", "regression", "predict", "price",
                                   "house", "salary", "health", "disease", "classic",
                                   "structured", "csv"],
            "time_series": ["time series", "forecast", "stock", "predict",
                            "temporal", "sequential", "energy", "weather", "trend"],
            "computer_vision": ["object detection", "yolo", "segmentation",
                                 "bounding box", "detect", "mask", "autonomous"],
            "recommendation": ["recommendation", "recommend", "collaborative",
                               "movie", "product", "similar", "suggest"],
            "generative_ai": ["generative", "gan", "generate", "create",
                              "deep fake", "style transfer", "creative"],
        }

        scores = {cat: sum(1 for kw in kws if kw in topic_lower)
                  for cat, kws in keyword_map.items()}
        scores = {k: v for k, v in scores.items() if v > 0}

        if not scores:
            return {
                "matched": False,
                "suggestion": "No exact match. Here are all categories:",
                "categories": list(CURATED_DATASETS.keys()),
                "datasets": [],
            }

        best = max(scores, key=scores.get)
        matched_keywords = [kw for kw in keyword_map[best] if kw in topic_lower]
        datasets = self.get_curated_datasets(best)
        for ds in datasets:
            ds["recommendation_reason"] = self._build_curated_reason(ds, topic, matched_keywords)
        return {
            "matched": True,
            "category": best,
            "display": CURATED_DATASETS[best]["display"],
            "datasets": datasets,
        }

    def _build_curated_reason(self, ds, topic, matched_keywords):
        """Generate a reason for curated dataset recommendations."""
        reasons = []

        # Why it matches the topic
        tags = [t.lower() for t in ds.get("tags", [])]
        if "beginner" in tags:
            reasons.append("Great for beginners")
        elif "advanced" in tags:
            reasons.append("Best for advanced projects")
        elif "intermediate" in tags:
            reasons.append("Good for intermediate learners")

        # Usability
        usability = ds.get("usability", 0)
        if usability >= 9.5:
            reasons.append(f"Top-rated usability ({usability}/10)")
        elif usability >= 9.0:
            reasons.append(f"Excellent usability ({usability}/10)")

        # Size context
        size = ds.get("size", "")
        if "KB" in size or (size and int(''.join(filter(str.isdigit, size.split()[0])) or 0) < 10):
            reasons.append("Lightweight, quick to download")
        elif "GB" in size:
            reasons.append("Large-scale real-world data")

        # Keyword match context
        if matched_keywords:
            reasons.append(f"Matches your interest in {matched_keywords[0]}")

        # Priority
        if ds.get("priority") == 1:
            reasons.append("Top pick in this category")

        if not reasons:
            reasons.append(f"Relevant to \"{topic}\"")

        return " · ".join(reasons[:3])

    def _build_recommendation_reason(self, ds, query, rank):
        """Generate a human-readable reason why this dataset is recommended."""
        reasons = []

        # Relevance reason based on rank
        if rank <= 3:
            reasons.append(f"Top match for \"{query}\"")

        # Popularity reason
        downloads = ds.get("downloads", 0)
        if downloads >= 100000:
            reasons.append(f"Very popular ({downloads:,} downloads)")
        elif downloads >= 10000:
            reasons.append(f"Widely used ({downloads:,} downloads)")
        elif downloads >= 1000:
            reasons.append(f"Well-known dataset ({downloads:,} downloads)")

        # Community votes
        votes = ds.get("votes", 0)
        if votes >= 100:
            reasons.append(f"Highly voted by community ({votes:,} votes)")

        # Fallback
        if not reasons:
            reasons.append(f"Relevant to \"{query}\"")

        return " · ".join(reasons)

    def search_datasets(self, query, sort_by="hottest", max_results=10):
        if not self.api:
            return {"success": False,
                    "error": "Kaggle API not available. Configure credentials in .env",
                    "datasets": []}
        try:
            results = self.api.dataset_list(search=query, sort_by=sort_by, file_type="csv")
            datasets = []
            for i, ds in enumerate(results[:max_results]):
                datasets.append({
                    "rank": i + 1,
                    "name": ds.ref,
                    "title": ds.title,
                    "size": str(ds.totalBytes or 0),
                    "size_readable": self._format_bytes(ds.totalBytes or 0),
                    "downloads": ds.downloadCount or 0,
                    "votes": ds.voteCount or 0,
                    "usability": ds.usabilityRating or 0,
                    "last_updated": str(ds.lastUpdated)[:10],
                    "url": f"https://www.kaggle.com/datasets/{ds.ref}",
                    "tags": [],
                })

            datasets.sort(key=lambda x: x["downloads"], reverse=True)
            for i, ds in enumerate(datasets):
                ds["rank"] = i + 1
                ds["priority_score"] = round(ds["downloads"] / 1000, 2)
                ds["recommendation_reason"] = self._build_recommendation_reason(ds, query, ds["rank"])

            self.cache["searches"].append({
                "query": query, "timestamp": datetime.now().isoformat(),
                "results_count": len(datasets),
            })
            self._save_cache()

            return {"success": True, "query": query, "count": len(datasets), "datasets": datasets}

        except Exception as e:
            logger.error(f"Kaggle search failed: {e}")
            return {"success": False, "error": str(e), "datasets": []}

    def download_dataset(self, dataset_name, unzip=True):
        if not self.api:
            return {"success": False, "error": "Kaggle API not available"}
        try:
            safe_name = dataset_name.replace("/", "_")
            dest_dir = self.download_dir / safe_name
            os.makedirs(dest_dir, exist_ok=True)

            self.api.dataset_download_files(dataset_name, path=str(dest_dir), unzip=unzip)

            files = []
            total_size = 0
            for f in dest_dir.rglob("*"):
                if f.is_file():
                    size = f.stat().st_size
                    files.append({"name": f.name, "path": str(f),
                                  "size": self._format_bytes(size), "extension": f.suffix})
                    total_size += size

            self.cache["downloads"].append({
                "dataset": dataset_name, "timestamp": datetime.now().isoformat(),
                "path": str(dest_dir), "files_count": len(files),
            })
            self._save_cache()

            return {"success": True, "dataset": dataset_name, "path": str(dest_dir),
                    "files": files, "total_size": self._format_bytes(total_size),
                    "files_count": len(files)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def preview_dataset(self, file_path, rows=5):
        if not PANDAS_AVAILABLE:
            return {"success": False, "error": "pandas not installed"}
        try:
            path = Path(file_path)
            if not path.exists():
                return {"success": False, "error": "File not found"}
            if path.suffix.lower() != ".csv":
                return {"success": False, "error": "Only CSV files supported"}

            df = pd.read_csv(path, nrows=100)
            return {
                "success": True, "filename": path.name,
                "shape": {"rows": len(df), "columns": len(df.columns)},
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "preview": df.head(rows).to_dict("records"),
                "null_counts": df.isnull().sum().to_dict(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_download_history(self):
        return self.cache.get("downloads", [])

    def get_search_history(self):
        return self.cache.get("searches", [])

    @staticmethod
    def _format_bytes(size):
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def run(self):
        """CLI entry point."""
        print("\n" + "═" * 60)
        print("  📊 KAGGLE DATASET FINDER")
        print("═" * 60)

        while True:
            print("""
  [1] 🎯  Get ML Dataset Recommendations
  [2] 🔍  Search Kaggle Datasets
  [3] ⬇️   Download a Dataset
  [4] 📋  View Download History
  [5] 🔙  Back
            """)
            choice = input("  Choice: ").strip()

            if choice == "1":
                topic = input("  Describe your ML project: ").strip()
                result = self.recommend_for_topic(topic)
                if result["matched"]:
                    print(f"\n  ✅ {result['display']}")
                    for ds in result["datasets"]:
                        print(f"  {ds['priority']}. {ds['title']} ({ds['size']})")
                        print(f"     📦 {ds['name']}")
            elif choice == "2":
                query = input("  Search query: ").strip()
                result = self.search_datasets(query)
                if result["success"]:
                    for ds in result["datasets"][:10]:
                        print(f"  {ds['rank']}. {ds['title']} | {ds['size_readable']}")
                else:
                    print(f"  Error: {result['error']}")
            elif choice == "3":
                name = input("  Dataset (owner/name): ").strip()
                result = self.download_dataset(name)
                if result["success"]:
                    print(f"  ✅ Downloaded {result['files_count']} files")
                else:
                    print(f"  ❌ {result['error']}")
            elif choice == "4":
                history = self.get_download_history()
                for h in history[-10:]:
                    print(f"  • {h['dataset']} ({h['timestamp'][:10]})")
            elif choice == "5":
                break
