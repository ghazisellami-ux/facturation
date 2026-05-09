import json, urllib.request

data = json.dumps({"email": "ghazi.sellami@gmail.com", "password": "SicFacture2024!"}).encode()
req = urllib.request.Request("https://facture.sic-tunisia.tn/api/auth/login", data=data, headers={"Content-Type": "application/json"}, method="POST")
try:
    resp = urllib.request.urlopen(req)
    print("HTTPS LOGIN OK:", resp.read().decode()[:80])
except Exception as e:
    print("HTTPS LOGIN FAILED:", e)
    if hasattr(e, "read"): print("Body:", e.read().decode())
