import sqlite3
from datetime import datetime

DB_FILE = "network_traffic.db"

def init_db():
    """
    Initializes the SQLite database and creates the necessary table if it doesn't exist.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create a table to store domain, geo-IP information, and timestamp
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS domain_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT UNIQUE,
            timestamp TEXT,
            status TEXT,
            country TEXT,
            countryCode TEXT,
            region TEXT,
            regionName TEXT,
            city TEXT,
            zip TEXT,
            lat REAL,
            lon REAL,
            timezone TEXT,
            isp TEXT,
            org TEXT,
            "as" TEXT,
            query TEXT
        )
    ''')


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            domain TEXT,
            FOREIGN KEY(domain) REFERENCES domain_cache(domain)
        )
    ''')
    conn.commit()
    conn.close()
    
    conn.commit()
    conn.close()

def save_to_db(domain, geo_info):


    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 2. Prepare the timestamp (ISO 8601 format: YYYY-MM-DD HH:MM:SS)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 3. Insert or Replace the data
    # (INSERT OR REPLACE updates the record if the domain already exists)
    sql_domain = '''
        INSERT OR REPLACE INTO domain_cache (
            domain, timestamp, status, country, countryCode, region, 
            regionName, city, zip, lat, lon, timezone, isp, org, "as", query
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    # Safe data extraction using .get() to prevent KeyErrors if the API skips a field
    values_domain = (
        domain,
        current_time,
        geo_info.get("status"),
        geo_info.get("country"),
        geo_info.get("countryCode"),
        geo_info.get("region"),
        geo_info.get("regionName"),
        geo_info.get("city"),
        geo_info.get("zip"),
        geo_info.get("lat"),
        geo_info.get("lon"),
        geo_info.get("timezone"),
        geo_info.get("isp"),
        geo_info.get("org"),
        geo_info.get("as"),
        geo_info.get("query")  # 'query' contains the IP address returned by ip-api
    )

    sql_log = '''
        INSERT INTO traffic_log (timestamp, domain) VALUES (?, ?)
    '''
        

    try:
        cursor.execute(sql_domain, values_domain)
        cursor.execute(sql_log, (current_time, domain))
        conn.commit()
        print(f"[+] Successfully saved {domain} to SQLite database.")
    except sqlite3.Error as e:
        print(f"[!] SQLite error: {e}")
    finally:
        conn.close()


init_db()