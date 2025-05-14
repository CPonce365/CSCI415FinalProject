from flask import Flask, request, jsonify
import geoip2.database
from geopy.distance import geodesic
import requests
from ipaddress import ip_address, ip_network

TAILSCALE_CGNAT = ip_network("100.64.0.0/10")
DEFAULT_CLIENT_COORDS = (40.730610, -73.935242)  # Example: NYC

app = Flask(__name__)
geoip_db = geoip2.database.Reader('/usr/share/GeoIP/GeoLite2-City.mmdb')

CDN_NODES = {
    "100.75.52.97": (33.7490, -84.3880),     # Atlanta
    "100.77.84.84": (32.7767, -96.7970),     # Dallas
    "100.65.100.91": (34.052235, -118.243683) # Los Angeles
}

def get_client_coords(ip):
    try:
        if ip_address(ip) in TAILSCALE_CGNAT:
            raise ValueError("Tailscale IP detected")

        record = geoip_db.city(ip)
        return (record.location.latitude, record.location.longitude)
    except Exception as e:
        print(f"[WARN] Falling back to default location for IP: {ip} — {e}")
        return DEFAULT_CLIENT_COORDS

def fetch_metrics(ip):
    try:
        r = requests.get(f"http://{ip}:8000/metrics", timeout=2)
        return r.json()
    except:
        return None

@app.route("/get_cdn")
def get_cdn():
    client_ip = (
        request.headers.get("X-Client-IP") or
        request.args.get("client_ip") or
        request.remote_addr
    )

    client_coords = get_client_coords(client_ip)
    if not client_coords:
        return jsonify({"error": "Could not locate client"}), 503

    MAX_CONN = 1000
    MAX_DIST_KM = 20000

    # Weights
    alpha = 0.4
    beta = 0.8
    gamma = 0.2
    delta = 0.2
    epsilon = 0.4

    best_ip = None
    best_weight = float("inf")

    for cdn_ip, cdn_coords in CDN_NODES.items():
        metrics = fetch_metrics(cdn_ip)
        if not metrics:
            continue

        m1 = metrics.get("cpu_percent", 100)
        m2 = metrics.get("memory_percent", 100)
        m3 = min(metrics.get("connections", 1000), MAX_CONN) / MAX_CONN
        m4_km = geodesic(client_coords, cdn_coords).km
        m4 = min(m4_km, MAX_DIST_KM) / MAX_DIST_KM

        weight = alpha * (beta * m1 + gamma * m2) + delta * m3 + epsilon * m4

        if weight < best_weight:
            best_weight = weight
            best_ip = cdn_ip

    if not best_ip:
        return jsonify({"error": "No CDN available"}), 503

    return jsonify({"best_cdn": best_ip})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
