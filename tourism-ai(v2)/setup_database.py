import sqlite3

def create_database():
    # Connect to SQLite database (creates the file if it doesn’t exist)
    conn = sqlite3.connect('project.db')
    cursor = conn.cursor()
    
    # Create the search_history table if it doesn’t already exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database and table created successfully.")

# Run this function when executing the script
if __name__ == "__main__":
    create_database()
