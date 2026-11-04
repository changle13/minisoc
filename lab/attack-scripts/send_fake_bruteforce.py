import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone
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
BASE = os.getenv("MINISOC_API_URL", "http://192.168.65.10:8000")
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise SystemExit("API_KEY is missing; set it in deploy/.env")

now = datetime.now(timezone.utc)
events = []
for index in range(6):
    timestamp = now - timedelta(seconds=index)
    events.append(
        {
            "timestamp": timestamp.isoformat(),
            "source_type": "auth",
            "host": "victim",
            "username": "victim",
            "src_ip": "192.168.65.99",
            "process": "sshd",
            "command_line": "Failed password for victim from 192.168.65.99 port 2222 ssh2",
            "raw": {
                "event_type": "ssh_failed",
                "line": "synthetic ssh brute-force test",
            },
        }
    )

body = json.dumps({"events": events}).encode("utf-8")
request = urllib.request.Request(
    f"{BASE}/api/v1/ingest/events",
    data=body,
    headers={
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
    },
    method="POST",
)
with urllib.request.urlopen(request) as response:
    print(response.status, response.read().decode("utf-8"))
