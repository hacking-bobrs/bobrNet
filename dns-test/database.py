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
            true_sovereignty TEXT, -- The actual corporate jurisdiction (e.g., "United States")
            provider_group TEXT,   -- The cloud provider/CDN name
            city TEXT DEFAULT ''
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

def get_recent_traffic(limit=1000):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.timestamp, t.domain, c.ip, c.country, c.country_code, c.city,
               c.latitude, c.longitude, c.asn_owner, c.true_sovereignty, c.provider_group
        FROM traffic_log t
        LEFT JOIN domain_cache c ON t.domain = c.domain
        ORDER BY t.id DESC
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for row in rows:
        results.append({
            "timestamp": row[0],
            "domain": row[1],
            "ip": row[2] or "",
            "country": row[3] or "unknown",
            "country_code": row[4] or "UN",
            "city": row[5] or "",
            "lat": row[6] or 0,
            "lon": row[7] or 0,
            "asn_owner": row[8] or "unknown",
            "true_sovereignty": row[9] or "unknown",
            "provider_group": row[10] or "Local / Independent"
        })
    return list(reversed(results))

def get_cached_domain(domain):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM domain_cache WHERE domain = ? LIMIT 1", (domain,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "domain": row[0], "ip": row[1], "country": row[2], "country_code": row[3],
            "lat": row[4], "lon": row[5], "asn_owner": row[6], "true_sovereignty": row[7],
            "provider_group": row[8] if len(row) > 8 else "Unknown",
            "city": row[9] if len(row) > 9 else ""
        }
    return None

def cache_domain(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO domain_cache 
        (domain, ip, country, country_code, latitude, longitude, asn_owner, true_sovereignty, provider_group, city)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['domain'], data['ip'], data['country'], data['country_code'], 
          data['lat'], data['lon'], data['asn_owner'], data['true_sovereignty'], data['provider_group'], data.get('city', '')))
    conn.commit()
    conn.close()
