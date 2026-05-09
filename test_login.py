import json, urllib.request

# Login
data = json.dumps({"email": "ghazi.sellami@gmail.com", "password": "Sic2024"}).encode()
req = urllib.request.Request("http://127.0.0.1:8002/api/auth/login", data=data, headers={"Content-Type": "application/json"}, method="POST")
resp = urllib.request.urlopen(req)
token = json.loads(resp.read())["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test all 3 endpoints used by factures page
for url in ["http://127.0.0.1:8002/api/invoices/?invoice_type=facture", "http://127.0.0.1:8002/api/clients/", "http://127.0.0.1:8002/api/products/"]:
    try:
        req2 = urllib.request.Request(url, headers=headers)
        resp2 = urllib.request.urlopen(req2)
        result = json.loads(resp2.read())
        print(f"OK {url.split('/')[-2]}: {len(result) if isinstance(result, list) else result}")
    except Exception as e:
        print(f"FAIL {url}: {e}")
        if hasattr(e, "read"): print("  Body:", e.read().decode()[:200])
