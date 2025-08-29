#!/usr/bin/env python3
import os, sys, re, time, html
from datetime import datetime, timezone

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "public")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SOURCE_URL = os.environ.get("SOURCE_URL", "").strip()
UDXPY_HOST = os.environ.get("UDXPY_HOST", "192.168.50.1").strip()
UDXPY_PORT = int(os.environ.get("UDXPY_PORT", "8889"))
OUTPUT_FILENAME = os.environ.get("OUTPUT_FILENAME", "playlist.m3u").strip()

def fetch_source() -> str:
    if SOURCE_URL:
        try:
            import requests
            resp = requests.get(SOURCE_URL, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            raise RuntimeError(f"Failed to fetch SOURCE_URL: {SOURCE_URL}\n{e}")
    # fallback: local file
    local_path = os.path.join(os.path.dirname(__file__), "..", "source.m3u")
    if not os.path.exists(local_path):
        raise FileNotFoundError("No SOURCE_URL provided and ./source.m3u not found")
    with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def transform_to_udpxy(m3u: str, host: str, port: int) -> str:
    if not m3u or not m3u.strip():
        return "#EXTM3U\n"

    lines = m3u.replace("\r", "").split("\n")
    out = []
    # Ensure header
    if not lines[0].strip().startswith("#EXTM3U"):
        out.append("#EXTM3U")

    for line in lines:
        t = line.strip()
        if not t or t.startswith("#"):
            out.append(line)
            continue

        lower = t.lower()
        if lower.startswith("rtp://@") or lower.startswith("udp://@"):
            after_at = t.split("@", 1)[1]
            out.append(f"http://{host}:{port}/rtp/{after_at}")
            continue
        if lower.startswith("rtp://") or lower.startswith("udp://"):
            target = t.split("://", 1)[1]
            if target.startswith("@"):
                target = target[1:]
            out.append(f"http://{host}:{port}/rtp/{target}")
            continue

        out.append(line)
    return "\n".join(out) + "\n"

def write_outputs(body: str):
    playlist_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
    with open(playlist_path, "w", encoding="utf-8") as f:
        f.write(body)

    # Simple index page
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    index = f'''<!doctype html>
<html>
<head><meta charset="utf-8"><title>MyTV Playlist</title></head>
<body>
  <h1>MyTV Playlist</h1>
  <p>Last updated: {html.escape(now)}</p>
  <p><a href="{html.escape(OUTPUT_FILENAME)}">{html.escape(OUTPUT_FILENAME)}</a></p>
</body>
</html>
'''
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index)

def main():
    src = fetch_source()
    body = transform_to_udpxy(src, UDXPY_HOST, UDXPY_PORT)
    write_outputs(body)
    print(f"Wrote to ./public/{OUTPUT_FILENAME}")

if __name__ == "__main__":
    main()
