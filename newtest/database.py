import sqlite3
from datetime import datetime

DB_NAME = "sovereignty.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Cache table to store domain intelligence permanently
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS domain_cache (
            domain TEXT PRIMARY KEY,
            ip TEXT,
            country TEXT,
            country_code TEXT,
            latitude REAL,
            longitude REAL,
            asn_owner TEXT,       -- e.g., "AMAZON-02" or "GOOGLE"
            true_sovereignty TEXT -- The actual corporate jurisdiction (e.g., "United States")
        )
    ''')
    
    # Live log table of every single request your phone makes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            client_ip TEXT,
            domain TEXT,
            FOREIGN KEY(domain) REFERENCES domain_cache(domain)
        )
    ''')
    conn.commit()
    conn.close()

def log_request(client_ip, domain):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO traffic_log (timestamp, client_ip, domain) VALUES (?, ?, ?)",
        (datetime.now().isoformat(), client_ip, domain)
    )
    conn.commit()
    conn.close()

def get_cached_domain(domain):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM domain_cache WHERE domain = ? LIMIT 1", (domain,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "domain": row[0], "ip": row[1], "country": row[2], "country_code": row[3],
            "lat": row[4], "lon": row[5], "asn_owner": row[6], "true_sovereignty": row[7]
        }
    return None

def cache_domain(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO domain_cache 
        (domain, ip, country, country_code, latitude, longitude, asn_owner, true_sovereignty)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['domain'], data['ip'], data['country'], data['country_code'], 
          data['lat'], data['lon'], data['asn_owner'], data['true_sovereignty']))
    conn.commit()
    conn.close()
