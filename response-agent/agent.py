#!/usr/bin/env python3
import hashlib
import hmac
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from ipaddress import ip_address

SECRET = os.getenv("MINISOC_RESPONSE_SECRET", "dev-response-secret")
DRY_RUN = os.getenv("MINISOC_RESPONSE_DRY_RUN", "1") == "1"
PORT = int(os.getenv("MINISOC_RESPONSE_PORT", "9000"))
LOG_PATH = os.getenv("MINISOC_RESPONSE_LOG", "/var/log/minisoc-response.jsonl")
CHAIN = "MINISOC_BLOCK"
ALLOWLIST = {
    value.strip()
    for value in os.getenv(
        "MINISOC_ALLOWLIST",
        "127.0.0.1,192.168.65.10,192.168.65.20",
    ).split(",")
    if value.strip()
}


def run_iptables(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["iptables", "-w", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def ensure_chain() -> None:
    result = run_iptables("-N", CHAIN)
    if result.returncode != 0 and "already exists" not in result.stderr:
        check = run_iptables("-L", CHAIN, "-n")
        if check.returncode != 0:
            raise RuntimeError(check.stderr.strip() or "cannot create chain")

    result = run_iptables("-C", "INPUT", "-j", CHAIN)
    if result.returncode != 0:
        result = run_iptables("-I", "INPUT", "1", "-j", CHAIN)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "cannot attach chain")


def block_ip(ip: str) -> str:
    ensure_chain()
    exists = run_iptables("-C", CHAIN, "-s", ip, "-j", "DROP")
    if exists.returncode == 0:
        return "already_blocked"
    result = run_iptables("-I", CHAIN, "1", "-s", ip, "-j", "DROP")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "iptables block failed")
    return "blocked"


def unblock_ip(ip: str) -> str:
    exists = run_iptables("-C", CHAIN, "-s", ip, "-j", "DROP")
    if exists.returncode != 0:
        return "not_found"
    result = run_iptables("-D", CHAIN, "-s", ip, "-j", "DROP")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "iptables unblock failed")
    return "unblocked"


def snapshot_rules() -> list[str]:
    if DRY_RUN:
        return []
    result = run_iptables("-S", CHAIN)
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def validate_ip(value: str) -> str:
    try:
        ip = ip_address(value)
    except ValueError as exc:
        raise ValueError("invalid IPv4 address") from exc
    if ip.version != 4:
        raise ValueError("only IPv4 is supported")
    if ip.is_loopback or ip.is_unspecified or ip.is_multicast or ip.is_link_local:
        raise ValueError("protected IP address")
    normalized = str(ip)
    if normalized in ALLOWLIST:
        raise ValueError("IP is in the allowlist")
    return normalized


def verify_signature(headers, body: bytes) -> bool:
    timestamp = headers.get("X-MiniSOC-Timestamp")
    signature = headers.get("X-MiniSOC-Signature")
    if not timestamp or not signature:
        return False
    try:
        timestamp_value = int(timestamp)
    except ValueError:
        return False
    if abs(int(time.time()) - timestamp_value) > 60:
        return False
    expected = hmac.new(
        SECRET.encode("utf-8"),
        f"{timestamp}.".encode("utf-8") + body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def write_audit(entry: dict) -> None:
    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    line = json.dumps(entry, ensure_ascii=False)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except OSError:
        print(line, file=sys.stderr)


class Handler(BaseHTTPRequestHandler):
    server_version = "MiniSOCResponse/0.1"

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "ok", "dry_run": DRY_RUN})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path not in ("/block", "/unblock"):
            self._json(404, {"error": "not found"})
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b""
        if not verify_signature(self.headers, body):
            self._json(401, {"error": "invalid signature"})
            return

        try:
            payload = json.loads(body.decode("utf-8"))
            target_ip = validate_ip(str(payload.get("ip", "")))
        except (ValueError, json.JSONDecodeError) as exc:
            self._json(400, {"error": str(exc)})
            return

        action = "block" if self.path == "/block" else "unblock"
        alert_id = payload.get("alert_id")
        reason = str(payload.get("reason", ""))
        try:
            if DRY_RUN:
                result = "would_block" if action == "block" else "would_unblock"
            elif action == "block":
                result = block_ip(target_ip)
            else:
                result = unblock_ip(target_ip)

            response = {
                "ok": True,
                "action": action,
                "ip": target_ip,
                "result": result,
                "dry_run": DRY_RUN,
                "rules": snapshot_rules(),
            }
            write_audit(
                {
                    "remote": self.client_address[0],
                    "action": action,
                    "ip": target_ip,
                    "alert_id": alert_id,
                    "reason": reason,
                    "dry_run": DRY_RUN,
                    "result": result,
                }
            )
            self._json(200, response)
        except Exception as exc:
            write_audit(
                {
                    "remote": self.client_address[0],
                    "action": action,
                    "ip": target_ip,
                    "alert_id": alert_id,
                    "reason": reason,
                    "dry_run": DRY_RUN,
                    "result": "error",
                    "detail": str(exc),
                }
            )
            self._json(500, {"ok": False, "error": str(exc)})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[response-agent] {self.address_string()} {fmt % args}")


def main() -> None:
    print(
        f"[response-agent] listen=0.0.0.0:{PORT} dry_run={DRY_RUN} "
        f"chain={CHAIN} log={LOG_PATH}"
    )
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
