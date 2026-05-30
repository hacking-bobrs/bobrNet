import sqlite3
from datetime import datetime

DB_FILE = "network_traffic.db"

def init_db():
    """
    Initializes the SQLite database and creates the necessary table if it doesn't exist.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
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

def save_to_db(domain, geo_info):


    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    log_only = is_domain_cached(domain)

    if not log_only:
        sql_domain = '''
            INSERT OR REPLACE INTO domain_cache (
                domain, timestamp, status, country, countryCode, region, 
                regionName, city, zip, lat, lon, timezone, isp, org, "as", query
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''

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
        if not log_only:
            cursor.execute(sql_domain, values_domain)
        cursor.execute(sql_log, (current_time, domain))
        conn.commit()
        print(f"[+] Successfully saved {domain} to SQLite database.")
    except sqlite3.Error as e:
        print(f"[!] SQLite error: {e}")
    finally:
        conn.close()


def get_chronological_traffic_log():
    """
    Holt alle Traffic-Logs chronologisch sortiert aus der Datenbank.
    Gibt eine Liste von (domain, geo_info) Tupeln zurück.
    Taucht eine Domain mehrfach im Log auf, erscheint sie auch mehrfach in der Liste.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql_join = '''
        SELECT 
            tl.domain,
            dc.status, dc.country, dc.countryCode, dc.region, dc.regionName,
            dc.city, dc.zip, dc.lat, dc.lon, dc.timezone, dc.isp, dc.org, 
            dc."as", dc.query
        FROM traffic_log tl
        INNER JOIN domain_cache dc ON tl.domain = dc.domain
        ORDER BY tl.timestamp ASC
    '''
    
    traffic_data = []

    try:
        cursor.execute(sql_join)
        rows = cursor.fetchall()

        for row in rows:
            domain = row["domain"]
            
            geo_info = {
                "status": row["status"],
                "country": row["country"],
                "countryCode": row["countryCode"],
                "region": row["region"],
                "regionName": row["regionName"],
                "city": row["city"],
                "zip": row["zip"],
                "lat": row["lat"],
                "lon": row["lon"],
                "timezone": row["timezone"],
                "isp": row["isp"],
                "org": row["org"],
                "as": row["as"],
                "query": row["query"]
            }
            
            traffic_data.append((domain, geo_info))
            
    except sqlite3.Error as e:
        print(f"[!] SQLite-Fehler bei der Log-Abfrage: {e}")
    finally:
        conn.close()

    return traffic_data

def is_domain_cached(domain):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM domain_cache WHERE domain = ? LIMIT 1", (domain,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def print_cached_domains():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM domain_cache")
    domains = cursor.fetchall()

    print("Cached Domains:")
    for d in domains:
        print(f" - {d[1]}")

    conn.close()

def print_traffic_log():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM traffic_log")
    domains = cursor.fetchall()

    print("Traffic Log:")
    for d in domains:
        print(f" - {d[2]}")

    conn.close()


def get_all_cached_domains():
    """Returns all cached domains with their geo info as a list of dicts."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM domain_cache')
    rows = cursor.fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result

def get_traffic_summary():
    """Returns summary statistics for the PDF report."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Total requests
    cursor.execute('SELECT COUNT(*) as total FROM traffic_log')
    total_requests = cursor.fetchone()['total']

    # Unique domains
    cursor.execute('SELECT COUNT(DISTINCT domain) as total FROM traffic_log')
    unique_domains = cursor.fetchone()['total']

    # Country distribution
    cursor.execute('''
        SELECT dc.country, dc.countryCode, COUNT(*) as cnt
        FROM traffic_log tl
        INNER JOIN domain_cache dc ON tl.domain = dc.domain
        GROUP BY dc.country
        ORDER BY cnt DESC
    ''')
    country_dist = [dict(r) for r in cursor.fetchall()]

    # Provider distribution
    cursor.execute('''
        SELECT dc.isp, COUNT(*) as cnt
        FROM traffic_log tl
        INNER JOIN domain_cache dc ON tl.domain = dc.domain
        GROUP BY dc.isp
        ORDER BY cnt DESC
    ''')
    provider_dist = [dict(r) for r in cursor.fetchall()]

    # Top domains by request count
    cursor.execute('''
        SELECT domain, COUNT(*) as cnt
        FROM traffic_log
        GROUP BY domain
        ORDER BY cnt DESC
        LIMIT 20
    ''')
    top_domains = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        'total_requests': total_requests,
        'unique_domains': unique_domains,
        'country_dist': country_dist,
        'provider_dist': provider_dist,
        'top_domains': top_domains
    }


#print_cached_domains()
#print_traffic_log()

#print(f"Is 'example.com' cached? {is_domain_cached('rb.de')}")