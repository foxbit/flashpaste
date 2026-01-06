import sqlite3
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from gi.repository import GLib

class DatabaseManager:
    def __init__(self):
        # Setup path
        data_dir = GLib.get_user_data_dir()
        app_dir = os.path.join(data_dir, "flashpaste")
        os.makedirs(app_dir, exist_ok=True)
        self.db_path = os.path.join(app_dir, "snippets.db")
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_published BOOLEAN DEFAULT 0,
                pastebin_url TEXT,
                pastebin_key TEXT
            )
        """)
        conn.commit()
        conn.close()

    def add_snippet(self, content: str) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO snippets (content) VALUES (?)", (content,))
        snippet_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return snippet_id

    def get_snippets(self, is_published: bool = False) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM snippets WHERE is_published = ? ORDER BY created_at DESC", 
            (1 if is_published else 0,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def delete_snippet(self, snippet_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))
        conn.commit()
        conn.close()

    def mark_published(self, snippet_id: int, url: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE snippets SET is_published = 1, pastebin_url = ? WHERE id = ?",
            (url, snippet_id)
        )
        conn.commit()
        conn.close()

    def cleanup_expired(self) -> int:
        """
        Deletes unpublished snippets older than 24 hours.
        Returns the number of deleted rows.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # SQLite's DATETIME('now', '-1 day') is roughly equivalent, but let's be safe and use python time
        cutoff = datetime.now() - timedelta(hours=24)
        cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "DELETE FROM snippets WHERE is_published = 0 AND created_at < ?",
            (cutoff_str,)
        )
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_count
