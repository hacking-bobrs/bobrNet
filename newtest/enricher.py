import requests
from database import get_cached_domain, cache_domain

def resolve_true_sovereignty(domain, ip):
    # Skip local lookups or the enrichment API itself to avoid recursion/useless calls
    if ip.startswith("127.") or ip.startswith("192.168.") or ip.startswith("10."):
        return None
    if "ip-api.com" in domain:
        return None

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
        provider_group = "Local / Independent"
        
        us_infrastructure = {
            "AMAZON": "AWS (US)",
            "CLOUDFLARE": "Cloudflare (US)",
            "AKAMAI": "Akamai (US)",
            "FASTLY": "Fastly (US)",
            "GOOGLE": "Google (US)",
            "MICROSOFT": "Azure/MS (US)",
            "META": "Meta (US)",
            "FACEBOOK": "Meta (US)",
            "APPLE": "Apple (US)",
            "DIGITALOCEAN": "DigitalOcean (US)",
            "ORACLE": "Oracle (US)",
            "LINODE": "Linode (US)",
            "TWITTER": "Twitter/X (US)",
        }

        for keyword, provider in us_infrastructure.items():
            if keyword in asn_owner.upper():
                true_sovereignty = "United States (US Cloud Act Jurisdiction)"
                provider_group = provider
                break
        
        telemetry = {
            "domain": domain,
            "ip": ip,
            "country": country,
            "country_code": country_code,
            "lat": r.get("lat", 0.0),
            "lon": r.get("lon", 0.0),
            "asn_owner": asn_owner,
            "true_sovereignty": true_sovereignty,
            "provider_group": provider_group
        }
        
        # Save to database cache
        cache_domain(telemetry)
        return telemetry

    except Exception as e:
        print(f"Failed to enrich {domain}: {e}")
        return None
