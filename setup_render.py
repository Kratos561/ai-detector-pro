import urllib.request
import urllib.error
import json

RENDER_TOKEN = "rnd_0AVpP3lyehVuNqlW35BugO5p3I1F"
OWNER_ID = "tea-d6pvvlsr85hc73d272l0"
HEADERS = {
    "Authorization": f"Bearer {RENDER_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def render_request(method, path, data=None):
    url = f"https://api.render.com/v1{path}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, method=method)
    for k, v in HEADERS.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode()), r.getcode()
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode()), e.code

# List existing services
print("=== Existing Services on Render ===")
result, code = render_request("GET", f"/services?ownerId={OWNER_ID}&limit=20")
print(f"Status: {code}")
if code == 200:
    for item in result:
        svc = item.get("service", item)
        print(f"  - {svc.get('name')}: {svc.get('type')} | {svc.get('serviceDetails', {}).get('url', 'N/A')}")
else:
    print(json.dumps(result, indent=2)[:500])

print("\n=== Trying Backend with correct schema ===")
backend_payload = {
    "type": "web_service",
    "name": "ai-detector-pro-backend",
    "ownerId": OWNER_ID,
    "repo": "https://github.com/Kratos561/ai-detector-pro",
    "autoDeploy": "yes",
    "branch": "main",
    "rootDir": "backend",
    "serviceDetails": {
        "runtime": "python",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
        "plan": "free",
        "region": "oregon",
        "envVars": [],
        "envSpecificDetails": {
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT"
        }
    }
}
b_result, b_code = render_request("POST", "/services", backend_payload)
print(f"Status: {b_code}")
print(json.dumps(b_result, indent=2)[:800])
