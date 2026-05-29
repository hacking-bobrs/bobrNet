# 🛡️ Sovereignty Sentinel: AI Agents & Architecture

Welcome to the **Sovereignty Sentinel** technical blueprint. This document defines the operational layer of our autonomous network auditing agents built for the hackathon demo.

---

## 🤖 The Sovereignty Agent Fleet

Sovereignty Sentinel utilizes a decentralized architecture of specialized micro-agents that intercept, analyze, and enforce data sovereignty in real-time.

```
       [ Client Device ]
               │
               ▼  (DNS Intercept)
     ┌───────────────────┐
     │  Intercept Agent  │ ───► Logs to Traffic Ledger
     └───────────────────┘
               │
               ▼  (Raw IP & Domain)
     ┌───────────────────┐
     │ Enrichment Agent  │ ───► IP Geolocation & ASN Lookup
     └───────────────────┘
               │
               ▼  (Network Telemetry)
     ┌───────────────────┐
     │ Jurisdictional    │ ───► Corporate Parent Tracing
     │ Overlord Agent    │      (Detects Cloud Act, CDN Overrides)
     └───────────────────┘
               │
               ▼  (True Sovereignty Verdict)
     ┌───────────────────┐
     │ Operational UI    │ ───► Real-Time Map, Neon Telemetry
     │ Telemetry Stream  │      & Geopolitical Risk Matrix
     └───────────────────┘
```

### 1. 📡 The Intercept Agent (`dns_server.py`)
* **Role**: Inline Network Interception.
* **Mechanism**: Spasms a lightweight UDP socket on Port 53, captures upstream DNS requests, safely mirrors the package to the upstream recursive resolver (`8.8.8.8`), and instantly forks the resolved IP payload to the intelligence pipeline without blocking the client.
* **Metrics Tracked**: Transaction throughput, unique domain count, client source tracking.

### 2. 🧠 The Enrichment Agent (`enricher.py`)
* **Role**: Geopolitical & Physical Mapping.
* **Mechanism**: Interrogates distributed BGP/ASN mapping registries to convert transient IP addresses into physical lat/long coordinates, registered country boundaries, and Autonomous System Numbers (ASN).
* **Database Cache**: Integrates a SQLite-backed permanent cache to prevent lookup throttling and ensure sub-millisecond response loops for recurring targets.

### 3. ⚖️ The Jurisdictional Overlord Agent (`enricher.py` / Override Engine)
* **Role**: Corporate & Legal Sovereignty Decoupling.
* **The Problem**: A local server might sit in Germany or Poland, but if it's hosted on **AWS, Cloudflare, Akamai, or Google**, it is legally bound by the **US Cloud Act**. It is *not* sovereign.
* **Mechanism**: Performs string token analysis on the ASN ownership structure. If a match occurs against known systemic monopolies, it overrides local geolocation to flag the connection under **US Cloud Act Jurisdiction**.

---

## 📊 Presentation Pitch Deck Integration

### Why This Wins Hackathons:
1. **Real-time Shock Factor**: When judges connect their phones to this DNS server, they immediately see that 70%+ of their "local" apps are instantly pinging Virginia, USA or US-controlled CDNs.
2. **True Sovereignty Mapping**: Unlike generic IP trackers, we expose the *legal* jurisdiction, not just the physical wire.
3. **Cyberpunk UI**: Designed with glassmorphic overlay widgets, high-contrast neon risk indicators, and real-time canvas-based pulsing nodes.

---

## 🛠️ Developer Setup for Demo Mode

To ignite the Sovereignty Sentinel platform for presentation:

```bash
# 1. Install dependencies
pip install dnspython flask flask-socketio requests

# 2. Run with root privileges (Required to bind to DNS Port 53)
sudo python dns_server.py
```

*Change your device's DNS settings to the host's IP address, open `http://localhost:8081`, and watch the dependency map materialize live.*
