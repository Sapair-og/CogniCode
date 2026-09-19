import sqlite3

def authenticate_user(username: str, password_hash: str) -> dict:
    """
    Authenticates a user against an SQLite database.
    VULNERABILITY: Direct string formatting into raw SQL enables SQL Injection (CWE-89).
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # Intentionally vulnerable raw query
    query = f"SELECT id, username, role FROM users WHERE username = '{username}' AND password = '{password_hash}'"
    cursor.execute(query)
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {"id": row[0], "username": row[1], "role": row[2]}
    return None
