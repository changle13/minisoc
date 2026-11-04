import json
import urllib.request
from datetime import datetime, timedelta, timezone

BASE = "http://192.168.65.10:8000"
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
        "X-API-Key": "dev-ingest-key",
    },
    method="POST",
)
with urllib.request.urlopen(request) as response:
    print(response.status, response.read().decode("utf-8"))
