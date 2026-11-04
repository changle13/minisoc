import hashlib
import hmac
import json
import sys
import time
import urllib.request

BASE = "http://192.168.65.20:9000"
SECRET = b"dev-response-secret"

action = sys.argv[1] if len(sys.argv) > 1 else "block"
target_ip = sys.argv[2] if len(sys.argv) > 2 else "192.168.65.99"
body = json.dumps(
    {
        "ip": target_ip,
        "alert_id": 3,
        "reason": "manual dry-run test",
    }
).encode("utf-8")
timestamp = str(int(time.time()))
signature = hmac.new(
    SECRET,
    f"{timestamp}.".encode("utf-8") + body,
    hashlib.sha256,
).hexdigest()

request = urllib.request.Request(
    f"{BASE}/{action}",
    data=body,
    headers={
        "Content-Type": "application/json",
        "X-MiniSOC-Timestamp": timestamp,
        "X-MiniSOC-Signature": signature,
    },
    method="POST",
)

with urllib.request.urlopen(request) as response:
    print(response.status, response.read().decode("utf-8"))
