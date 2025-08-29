# MyTV Playlist (GitHub Pages + Actions)

This repository auto-generates an **M3U** playlist that rewrites multicast URLs (`rtp://@…`, `udp://@…`) to **udpxy** format and **publishes it to GitHub Pages** — no server needed.

**Public URL after setup:**  
```
https://<your-username>.github.io/<your-repo>/playlist.m3u
```

## How it works
- A GitHub Actions workflow runs on a schedule (hourly by default) and on manual dispatch.
- It runs a small Python script to:
  1. Download your source M3U (or read `source.m3u` in the repo if no URL is provided)
  2. Transform multicast links to udpxy: `http://<UDXPY_HOST>:<UDXPY_PORT>/rtp/<ip:port>`
  3. Publish `playlist.m3u` + `index.html` via **GitHub Pages**

## Quick Start
1. **Create a new repo** on GitHub, then upload this project.
2. In GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. (Option A) Edit workflow env to set your source and udpxy:
   - Open `.github/workflows/publish.yml` and change `SOURCE_URL`, `UDXPY_HOST`, `UDXPY_PORT`.
   - Commit.
   
   **OR**
   
   (Option B) Put a local `source.m3u` in the repo root (kept private if you need). The workflow will use it if `SOURCE_URL` is blank.
4. Go to **Actions** tab → run **“Build & Deploy Pages”** (workflow_dispatch) once, or wait for the next schedule.
5. Your playlist will appear at `https://<user>.github.io/<repo>/playlist.m3u`.

> Note: GitHub Action cron uses **UTC**. The provided schedule runs **hourly**.

## Local testing
```
python3 scripts/generate_m3u.py
# outputs to ./public/playlist.m3u (and ./public/index.html)
```

## Config options (environment variables)
- `SOURCE_URL`: Remote M3U URL (e.g. raw GitHub file). If empty, the script will try `./source.m3u` instead.
- `UDXPY_HOST`: Default `192.168.50.1`
- `UDXPY_PORT`: Default `8889`
- `OUTPUT_FILENAME`: Default `playlist.m3u`

## Security
If your source URL requires tokens/cookies or is on a private network, GitHub’s runners **cannot** reach it. In that case, use `source.m3u` committed to the repo instead.
