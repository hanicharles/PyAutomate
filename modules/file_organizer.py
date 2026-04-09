"""
FILE: modules/file_organizer.py
PURPOSE: Organize files into categorized subfolders
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime

from config import FILE_CATEGORIES, SKIP_FILES, DOWNLOADS_DIR

logger = logging.getLogger("FileOrganizer")


class FileOrganizer:
    """Organizes files in a directory into categorized subfolders."""

    def __init__(self, source_dir=None):
        self.source_dir = Path(source_dir) if source_dir else DOWNLOADS_DIR
        self.organized = 0
        self.skipped = 0
        self.errors = 0
        self.log_entries = []

    def get_category(self, extension):
        """Return category name for a given file extension."""
        ext = extension.lower()
        for category, extensions in FILE_CATEGORIES.items():
            if ext in extensions:
                return category
        return "Others"

    def scan_files(self):
        """Scan source directory for files (non-recursive)."""
        try:
            files = [
                f for f in self.source_dir.iterdir()
                if f.is_file() and f.name not in SKIP_FILES
            ]
            logger.info(f"Scanned {len(files)} files in {self.source_dir}")
            return files
        except Exception as e:
            logger.error(f"Scan failed: {e}")
            return []

    def organize_files(self, files):
        """Move files into category subfolders."""
        for f in files:
            try:
                category = self.get_category(f.suffix)
                dest_dir = self.source_dir / category
                dest_dir.mkdir(exist_ok=True)

                dest = dest_dir / f.name
                # Avoid overwriting — append timestamp if needed
                if dest.exists():
                    stem = f.stem
                    suffix = f.suffix
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dest = dest_dir / f"{stem}_{ts}{suffix}"

                shutil.move(str(f), str(dest))
                self.organized += 1
                self.log_entries.append({
                    "file": f.name,
                    "category": category,
                    "status": "moved",
                })
                logger.info(f"Moved '{f.name}' → {category}/")

            except Exception as e:
                self.errors += 1
                self.log_entries.append({
                    "file": f.name,
                    "category": "error",
                    "status": str(e),
                })
                logger.error(f"Error moving '{f.name}': {e}")

    def run(self):
        """CLI entry point."""
        print("\n" + "═" * 55)
        print("  📂 FILE ORGANIZER")
        print("═" * 55)
        print(f"  Source: {self.source_dir}")

        files = self.scan_files()
        if not files:
            print("  ℹ️  No files to organize.")
            return

        print(f"\n  Found {len(files)} files.")
        confirm = input("  Organize now? (y/n): ").strip().lower()
        if confirm == "y":
            self.organize_files(files)
            print(f"\n  ✅ Organized: {self.organized}")
            print(f"  ⚠️  Errors: {self.errors}")
        else:
            print("  Cancelled.")
