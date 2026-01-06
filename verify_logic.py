import sys
import os
import time
from datetime import datetime, timedelta

# Add current dir to path
sys.path.insert(0, os.getcwd())

from src.database import DatabaseManager

def test_database():
    print("Testing DatabaseManager...")
    db = DatabaseManager()
    
    # Test Add
    sid = db.add_snippet("Test content")
    print(f"Added snippet {sid}")
    
    # Test Get
    inbox = db.get_snippets(False)
    assert any(s['id'] == sid for s in inbox), "Snippet not found in inbox"
    print("Snippet found in inbox")
    
    # Test Delete
    db.delete_snippet(sid)
    inbox = db.get_snippets(False)
    assert not any(s['id'] == sid for s in inbox), "Snippet not deleted"
    print("Snippet deleted")
    
    # Test Expiration
    print("Testing Expiration Logic...")
    # Manually insert an old record
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    old_date = (datetime.now() - timedelta(hours=25)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO snippets (content, created_at) VALUES (?, ?)", ("Expired content", old_date))
    conn.commit()
    conn.close()
    
    before_count = len(db.get_snippets(False))
    deleted = db.cleanup_expired()
    print(f"Cleaned up {deleted} snippets")
    assert deleted >= 1, "Did not clean up expired snippet"
    
    print("Database tests passed!")

if __name__ == "__main__":
    try:
        test_database()
    except Exception as e:
        print(f"FAILED: {e}")
        sys.exit(1)
