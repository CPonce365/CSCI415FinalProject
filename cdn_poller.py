import time, json, requests, os

CDN_IPS = {
    "100.75.52.97": (33.7490, -84.3880),     # Atlanta
    "100.77.84.84": (32.7767, -96.7970),     # Dallas
    "100.65.100.91": (34.052235, -118.243683) # Los Angeles
}

OUTPUT_PATH = "/tmp/cdn_routing.json"

cache = {}

def fetch_metrics(ip):
    try:
        r = requests.get(f"http://{ip}:8000/metrics", timeout=2)
        return r.json()
    except:
        return None

while True:
    routing_info = {}

    for ip, coords in CDN_IPS.items():
        entry = {"location": coords, "metrics": []}
        result = fetch_metrics(ip)
        if result:
            result["timestamp"] = int(time.time())
            entry["metrics"].append(result)
        routing_info[ip] = entry

    with open(OUTPUT_PATH, "w") as f:
        json.dump(routing_info, f, indent=2)

    time.sleep(15)