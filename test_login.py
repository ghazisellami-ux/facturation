import json, urllib.request

# Login
data = json.dumps({"email": "ghazi.sellami@gmail.com", "password": "Sic2024"}).encode()
req = urllib.request.Request("http://127.0.0.1:8002/api/auth/login", data=data, headers={"Content-Type": "application/json"}, method="POST")
resp = urllib.request.urlopen(req)
token = json.loads(resp.read())["access_token"]

# Test PDF
url = f"http://127.0.0.1:8002/api/invoices/ac247759-00af-454e-b5ca-e8cf9fdfa6f0/pdf?token={token}"
try:
    req2 = urllib.request.Request(url)
    resp2 = urllib.request.urlopen(req2)
    pdf_data = resp2.read()
    with open("/tmp/test_facture.pdf", "wb") as f:
        f.write(pdf_data)
    print(f"PDF OK! Size: {len(pdf_data)} bytes")
    print(f"Starts with: {pdf_data[:20]}")
except Exception as e:
    print(f"FAILED: {e}")
    if hasattr(e, "read"):
        print(e.read().decode()[:500])
