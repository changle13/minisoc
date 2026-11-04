#!/usr/bin/env python3
import argparse
import json
import os
import re
import socket
import time
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_URL = os.getenv("MINISOC_API_URL", "http://192.168.65.10:8000")
API_KEY = os.getenv("MINISOC_API_KEY", "dev-ingest-key")
LOG_FILE = Path(os.getenv("MINISOC_LOG_FILE", "/var/log/auth.log"))
STATE_FILE = Path(os.getenv("MINISOC_STATE_FILE", "agent_state.json"))
BATCH_SIZE = int(os.getenv("MINISOC_BATCH_SIZE", "100"))
POLL_INTERVAL = float(os.getenv("MINISOC_POLL_INTERVAL", "2"))
HOSTNAME = socket.gethostname()

FAILED_RE = re.compile(
    r"Failed password for (?:invalid user )?(?P<user>\S+) from "
    r"(?P<ip>\d+\.\d+\.\d+\.\d+) port \d+ ssh2"
)
ACCEPTED_RE = re.compile(
    r"Accepted password for (?P<user>\S+) from "
    r"(?P<ip>\d+\.\d+\.\d+\.\d+) port \d+ ssh2"
)


def parse_timestamp(line: str) -> datetime:
    year = datetime.now().year
    dt = datetime.strptime(f"{year} {line[:15]}", "%Y %b %d %H:%M:%S")
    return dt.replace(tzinfo=datetime.now().astimezone().tzinfo)


def build_event(line: str) -> dict | None:
    failed = FAILED_RE.search(line)
    accepted = ACCEPTED_RE.search(line)
    match = failed or accepted
    if match is None:
        return None

    event_type = "ssh_failed" if failed else "ssh_success"
    return {
        "timestamp": parse_timestamp(line).isoformat(),
        "source_type": "auth",
        "host": HOSTNAME,
        "username": match.group("user"),
        "src_ip": match.group("ip"),
        "process": "sshd",
        "command_line": line.strip(),
        "raw": {
            "line": line.strip(),
            "event_type": event_type,
        },
    }


def load_offset() -> int:
    if not STATE_FILE.exists():
        return 0
    try:
        return int(json.loads(STATE_FILE.read_text())["offset"])
    except (ValueError, KeyError, json.JSONDecodeError):
        return 0


def save_offset(offset: int) -> None:
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps({"offset": offset}))
    tmp.replace(STATE_FILE)


def send_batch(events: list[dict]) -> bool:
    if not events:
        return True

    payload = json.dumps({"events": events}).encode("utf-8")
    request = Request(
        f"{API_URL}/api/v1/ingest/events",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY,
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=20) as response:
            return response.status == 202
    except HTTPError as exc:
        print(f"[agent] HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')}")
    except URLError as exc:
        print(f"[agent] send failed: {exc.reason}")
    return False


def process_once() -> None:
    if not LOG_FILE.exists():
        print(f"[agent] log file not found: {LOG_FILE}")
        return

    offset = load_offset()
    if LOG_FILE.stat().st_size < offset:
        offset = 0

    with LOG_FILE.open("rb") as handle:
        handle.seek(offset)
        lines = []
        for _ in range(BATCH_SIZE):
            raw_line = handle.readline()
            if not raw_line:
                break
            lines.append(raw_line.decode("utf-8", "replace"))

        new_offset = handle.tell()

    events = [event for line in lines if (event := build_event(line)) is not None]
    if send_batch(events):
        save_offset(new_offset)
        print(f"[agent] sent {len(events)} events, offset={new_offset}")
    else:
        print("[agent] send failed, offset not advanced")


def main() -> None:
    parser = argparse.ArgumentParser(description="MiniSOC auth.log agent")
    parser.add_argument("--once", action="store_true", help="process one batch and exit")
    args = parser.parse_args()

    if args.once:
        process_once()
        return

    print(f"[agent] watching {LOG_FILE}, api={API_URL}")
    while True:
        process_once()
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
