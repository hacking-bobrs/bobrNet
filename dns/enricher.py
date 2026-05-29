import requests

def resolve_true_sovereignty(domain, ip, database):
    # Skip local lookups or the enrichment API itself to avoid recursion/useless calls
    if ip.startswith("127.") or ip.startswith("192.168.") or ip.startswith("10."):
        return None
    if "ip-api.com" in domain:
        return None

    # 1. Check if we already looked this up before
    cached = database.get_cached_domain(domain)
    if cached:
        return cached

    # 2. If not cached, fetch deep network telemetry
    try:
        # 'fields=66842623' requests status, country, countryCode, lat, lon, org, as, and query
        location_data_reply = requests.get(f"http://ip-api.com/json/{ip}?fields=66842623", timeout=2.0).json()
        
        asn_owner = location_data_reply.get("as", "Unknown Infrastructure")
        country = location_data_reply.get("country", "Unknown")
        country_code = location_data_reply.get("countryCode", "UN")
        city = location_data_reply.get("city", "")

        # --- INFRASTRUCTURE ENRICHMENT ---
        # Detect global CDN or Cloud Provider
        true_sovereignty = country # default
        provider_group = "Local / Independent"
        
        infrastructure_map = {
            "AMAZON": "AWS",
            "CLOUDFLARE": "Cloudflare",
            "AKAMAI": "Akamai",
            "FASTLY": "Fastly",
            "GOOGLE": "Google",
            "MICROSOFT": "Azure/MS",
            "META": "Meta",
            "FACEBOOK": "Meta",
            "APPLE": "Apple",
            "DIGITALOCEAN": "DigitalOcean",
            "ORACLE": "Oracle",
            "LINODE": "Linode",
            "TWITTER": "Twitter/X",
        }

        for keyword, provider in infrastructure_map.items():
            if keyword in asn_owner.upper():
                provider_group = provider
                break
        
        telemetry = {
            "domain": domain,
            "ip": ip,
            "country": country,
            "country_code": country_code,
            "city": city,
            "lat": location_data_reply.get("lat", 0.0),
            "lon": location_data_reply.get("lon", 0.0),
            "asn_owner": asn_owner,
            "true_sovereignty": true_sovereignty,
            "provider_group": provider_group
        }
        
        # Save to database cache
        database.cache_domain(telemetry)
        return telemetry

    except Exception as e:
        print(f"Failed to enrich {domain}: {e}")
        return None
