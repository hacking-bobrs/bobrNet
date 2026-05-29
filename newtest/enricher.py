import requests
from database import get_cached_domain, cache_domain

def resolve_true_sovereignty(domain, ip):
    # 1. Check if we already looked this up before
    cached = get_cached_domain(domain)
    if cached:
        return cached

    # 2. If not cached, fetch deep network telemetry
    try:
        # 'fields=66842623' requests status, country, countryCode, lat, lon, org, as, and query
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=66842623", timeout=2.0).json()
        
        asn_owner = r.get("as", "Unknown Infrastructure")
        country = r.get("country", "Unknown")
        country_code = r.get("countryCode", "UN")
        
        # --- SOPHISTICATED SOVEREIGNTY OVERRIDE ENGINE ---
        # If it's a known global CDN or Cloud Provider, we look at corporate parent origins
        true_sovereignty = country # default
        
        cdn_keywords = ["CLOUDFLARE", "AKAMAI", "AMAZON", "FASTLY", "GOOGLE", "MICROSOFT"]
        if any(keyword in asn_owner.upper() for keyword in cdn_keywords):
            # For a pure tech demo, you can flag these as structurally US-controlled
            # due to Cloud Act jurisdictions, regardless of where the local node lives.
            true_sovereignty = "United States (US Cloud Act Jurisdiction)"

        telemetry = {
            "domain": domain,
            "ip": ip,
            "country": country,
            "country_code": country_code,
            "lat": r.get("lat", 0.0),
            "lon": r.get("lon", 0.0),
            "asn_owner": asn_owner,
            "true_sovereignty": true_sovereignty
        }
        
        # Save to database cache
        cache_domain(telemetry)
        return telemetry

    except Exception as e:
        print(f"Failed to enrich {domain}: {e}")
        return None
