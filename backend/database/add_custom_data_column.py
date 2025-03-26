"""
One-time script to add custom_data column to messages table.
"""

import sqlite3
import os

def add_custom_data_column():
    """Add custom_data column to messages table."""
    try:
        # Get the database path
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mosaic.db")
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Add the custom_data column
        cursor.execute('ALTER TABLE messages ADD COLUMN custom_data JSON')
        
        # Commit and close
        conn.commit()
        conn.close()
        
        print("Successfully added custom_data column to messages table")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column already exists")
        else:
            print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    add_custom_data_column()
