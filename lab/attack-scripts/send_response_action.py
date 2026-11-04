import hashlib
import hmac
import json
import os
import sys
import time
import urllib.request
from pathlib import Path


def load_env() -> None:
    env_path = Path(__file__).resolve().parents[2] / "deploy" / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


load_env()
BASE = os.getenv("MINISOC_RESPONSE_URL", "http://192.168.65.20:9000")
secret = os.getenv("RESPONSE_AGENT_SECRET")
if not secret:
    raise SystemExit("RESPONSE_AGENT_SECRET is missing; set it in deploy/.env")
SECRET = secret.encode("utf-8")

action = sys.argv[1] if len(sys.argv) > 1 else "block"
target_ip = sys.argv[2] if len(sys.argv) > 2 else "192.168.65.99"
body = json.dumps(
    {
        "ip": target_ip,
        "alert_id": 3,
        "reason": "manual response test",
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
