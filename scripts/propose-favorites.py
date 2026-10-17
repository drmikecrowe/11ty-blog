#!/usr/bin/env python3
"""
Propose 'watching' entries for things we rewatch, without creating anything.

Sources:
  - NAS directory listings (one name per line, `ls -1` output; `/path:` lines
    set the category for the names that follow)
  - Trakt watch history, if TRAKT_CLIENT_ID is set and --login has been run

Titles that already have a post under content/watching are skipped. Output is
a commented list of create-watching-post.py lines in watching-todo.sh format.

Usage:
    TRAKT_CLIENT_ID=... python scripts/propose-favorites.py --login
    python scripts/propose-favorites.py --movies nas-movies.txt --tv nas-tv.txt
    python scripts/propose-favorites.py --tv nas-tv.txt --out proposals.sh
"""

import argparse
import base64
import hashlib
import json
import os
import re
import secrets
import sys
import time
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

try:
    import requests
except ImportError:
    print("Error: requests not installed. Run: pip install requests")
    sys.exit(1)

TRAKT_API = "https://api.trakt.tv"
TRAKT_AUTHORIZE = "https://auth.trakt.tv/oauth/authorize"
# Must match the app's registered redirect exactly; the page itself can 404
REDIRECT_URI = "https://mikesshinyobjects.tech/trakt-callback"
TOKEN_FILE = Path.home() / ".config" / "trakt" / "token.json"
PENDING_FILE = TOKEN_FILE.with_name("pending-login.json")
YEAR_RE = re.compile(r"\s*\((\d{4})\)\s*$")
# Release-group filenames like "Working Girl 1988 BDMux ITA ENG 1080p ..."
RELEASE_RE = re.compile(r"^(.+?)[ .](19\d{2}|20\d{2})[ .].*$")
# Helper scripts and sidecar files that live alongside the videos
SKIP_RE = re.compile(r"\.(sh|noautosubs|srt|nfo|txt|jpg|png)$", re.IGNORECASE)
VARIANT_RE = re.compile(r"\s+-\s+.*\b(cut|edition|version)\b.*$", re.IGNORECASE)


def norm(title: str) -> str:
    """Comparison key: lowercase alphanumerics, leading article dropped."""
    key = re.sub(r"[^a-z0-9 ]", "", title.lower().replace("&", "and"))
    key = re.sub(r"^(the|a|an) ", "", key)
    return re.sub(r"\s+", "", key)


def parse_name(raw: str) -> tuple[str, str | None, bool]:
    """Return (title, year, clean) for one NAS entry."""
    name = raw.strip()
    m = YEAR_RE.search(name)
    if m:
        return VARIANT_RE.sub("", name[: m.start()]).strip(), m.group(1), True
    m = RELEASE_RE.match(name)
    if m:
        return m.group(1).replace(".", " ").strip(), m.group(2), False
    stripped = re.sub(r"\.[a-z0-9]{2,11}$", "", name).strip()
    return stripped, None, stripped == name


def new_entry(title: str, year: str | None, kind: str, clean: bool = True, raw: str = "") -> dict:
    return {"title": title, "year": year or "", "kind": kind, "nas": set(),
            "clean": clean, "raw": raw, "imdb": "", "plays": 0,
            "rewatched": 0, "distinct": 0, "aired": 0, "last": ""}


def read_nas(path: Path, kind: str) -> dict[tuple[str, str], dict]:
    """Parse an `ls -1` listing into {norm_key: entry}."""
    entries: dict[tuple[str, str], dict] = {}
    category = kind
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.endswith(":") and line.startswith("/"):
            category = line.rstrip(":").rsplit("/", 1)[-1]
            continue
        if SKIP_RE.search(line):
            continue
        title, year, clean = parse_name(line)
        key = (kind, norm(title))
        entry = entries.setdefault(key, new_entry(title, year, kind, clean=clean, raw=line))
        entry["nas"].add(category)
        entry["clean"] = entry["clean"] or clean
    return entries


def existing_titles(content_dir: Path) -> set[str]:
    """Norm keys and IMDB ids of every title already posted under content/watching."""
    keys = set()
    for md in content_dir.rglob("index.md"):
        text = md.read_text()
        m = re.search(r'^title:\s*"?(.+?)"?\s*$', text, re.MULTILINE)
        if m:
            keys.add(norm(m.group(1)))
        m = re.search(r'^imdb_id:\s*"?(tt\d+)"?\s*$', text, re.MULTILINE)
        if m:
            keys.add(m.group(1))
    return keys


def save_token(token: dict) -> None:
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.touch(mode=0o600, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(token, indent=2))


def token_request(payload: dict) -> dict:
    """POST /oauth/token (PKCE app: no client_secret) and save the result."""
    payload = {"client_id": os.environ["TRAKT_CLIENT_ID"], "redirect_uri": REDIRECT_URI, **payload}
    response = requests.post(f"{TRAKT_API}/oauth/token", json=payload, timeout=30)
    if not response.ok:
        sys.exit(f"Trakt token request failed ({response.status_code}): {response.text}")
    token = response.json()
    token.setdefault("created_at", int(time.time()))
    save_token(token)
    return token


def login() -> None:
    """Authorization Code + PKCE, step 1: print the URL, stash the verifier."""
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)
    url = TRAKT_AUTHORIZE + "?" + urlencode({
        "response_type": "code",
        "client_id": os.environ["TRAKT_CLIENT_ID"],
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    })
    PENDING_FILE.parent.mkdir(parents=True, exist_ok=True)
    PENDING_FILE.touch(mode=0o600, exist_ok=True)
    PENDING_FILE.write_text(json.dumps({"verifier": verifier, "state": state}))
    webbrowser.open(url)
    print(f"Approve access in your browser:\n\n  {url}\n")
    print("Then run again with: --code '<URL you land on>'")


def finish_login(pasted: str) -> None:
    """Step 2: exchange the pasted code (or callback URL) for tokens."""
    if not PENDING_FILE.exists():
        sys.exit("No pending login; run --login first.")
    pending = json.loads(PENDING_FILE.read_text())
    # zsh url-quote-magic escapes ?, = and & even inside single quotes
    pasted = pasted.replace("\\", "")
    params = parse_qs(urlparse(pasted).query)
    if params:
        if params.get("state", [""])[0] != pending["state"]:
            sys.exit("State mismatch; run --login again.")
        code = params["code"][0]
    else:
        code = pasted
    token_request({"grant_type": "authorization_code", "code": code, "code_verifier": pending["verifier"]})
    PENDING_FILE.unlink()
    print(f"Saved token to {TOKEN_FILE}")


def access_token() -> str:
    """Stored access token, refreshed when it is within a day of expiring."""
    token = json.loads(TOKEN_FILE.read_text())
    if time.time() > token["created_at"] + token["expires_in"] - 86400:
        # Refresh tokens are single-use; token_request saves the new pair
        token = token_request({"grant_type": "refresh_token", "refresh_token": token["refresh_token"]})
    return token["access_token"]




def trakt_pages(path: str) -> list:
    """GET every page of a paginated Trakt list (max 250 items per page)."""
    headers = {
        "content-type": "application/json",
        "trakt-api-version": "2",
        "trakt-api-key": os.environ["TRAKT_CLIENT_ID"],
        "authorization": f"Bearer {access_token()}",
    }
    items, page = [], 1
    while True:
        response = requests.get(f"{TRAKT_API}{path}?page={page}&limit=250", headers=headers, timeout=60)
        response.raise_for_status()
        items += response.json()
        if page >= int(response.headers.get("x-pagination-page-count", 1)):
            return items
        page += 1


def trakt_entry(entries: dict[tuple[str, str], dict], media: dict, kind: str) -> dict:
    entry = entries.setdefault((kind, norm(media["title"])), new_entry(media["title"], "", kind))
    entry["year"] = entry["year"] or str(media.get("year") or "")
    entry["imdb"] = media["ids"].get("imdb") or entry["imdb"]
    return entry


def merge_trakt(entries: dict[tuple[str, str], dict]) -> None:
    """Add movie plays and per-show episode stats from Trakt."""
    for item in trakt_pages("/sync/watched/movies"):
        entry = trakt_entry(entries, item["movie"], "movie")
        entry["plays"] += item.get("plays", 0)
        entry["last"] = max(entry["last"], (item.get("last_watched_at") or "")[:10])

    # /sync/watched/shows no longer carries episodes, so rebuild from history
    shows: dict[str, tuple[dict, dict]] = {}
    for item in trakt_pages("/sync/history/episodes"):
        episode = item["episode"]
        if episode["season"] == 0:
            continue
        entry = trakt_entry(entries, item["show"], "tv")
        entry["aired"] = item["show"].get("aired_episodes") or 0
        entry["last"] = max(entry["last"], item["watched_at"][:10])
        _, days = shows.setdefault(entry["title"], (entry, {}))
        days.setdefault((episode["season"], episode["number"]), set()).add(item["watched_at"][:10])
    for entry, days in shows.values():
        entry["distinct"] = len(days)
        entry["plays"] = sum(len(d) for d in days.values())
        # Played on 2+ different days; same-day duplicates are scrobble noise
        entry["rewatched"] = sum(len(d) > 1 for d in days.values())


def complete(entry: dict) -> float:
    return entry["distinct"] / entry["aired"] if entry["aired"] else 0.0


def proposal_line(entry: dict) -> str:
    flag = "--tv" if entry["kind"] == "tv" else "--movie"
    title = entry["title"].replace('"', '\\"')
    date = f"--date {entry['last'][:7]} " if entry["last"] else ""
    notes = [entry["year"]] if entry["year"] else []
    if entry["kind"] == "tv" and entry["distinct"]:
        notes.append(f"rewatched {entry['rewatched']}/{entry['distinct']} eps")
        notes.append(f"{complete(entry):.0%} of {entry['aired']} aired")
    elif entry["plays"]:
        notes.append(f"{entry['plays']} plays")
    if entry["nas"]:
        notes.append("NAS: " + ", ".join(sorted(entry["nas"])))
    if not entry["clean"]:
        notes.append(f"CHECK NAME: {entry['raw']}")
    return f'run "{title}" {flag} {date}--rank TBD   # ' + " | ".join(notes)


HEADER = """#!/usr/bin/env bash
#
# Proposed favorites from propose-favorites.py. Nothing has been created yet.
#
#   1. Delete the lines you don't want.
#   2. Replace each TBD with a rank (1=top .. 5=good), or drop "--rank TBD".
#      Add --highly for top picks. --date is the month you last watched it.
#   3. Run it. An unfilled TBD fails argparse and stops the script there.
#
set -euo pipefail
cd "$(dirname "$0")/.."

run() { mise exec -- uv run python scripts/create-watching-post.py "$@"; }
"""


def main():
    parser = argparse.ArgumentParser(
        description="Propose watching entries for titles we rewatch"
    )
    parser.add_argument("--movies", type=Path, help="NAS movie listing (ls -1 output)")
    parser.add_argument("--tv", type=Path, help="NAS TV listing (ls -1 output)")
    parser.add_argument("--min-plays", type=int, default=2, help="Movies: Trakt plays needed (default: 2)")
    parser.add_argument("--min-rewatched", type=int, default=10, help="TV: episodes rewatched (default: 10)")
    parser.add_argument("--min-complete", type=float, default=0.9, help="TV: share of aired episodes watched (default: 0.9)")
    parser.add_argument("--min-episodes", type=int, default=10, help="TV: aired episodes for the completion rule (default: 10)")
    parser.add_argument("--out", type=Path, help="Write proposals here (default: stdout)")
    parser.add_argument("--login", action="store_true", help=f"Sign in to Trakt and save a token to {TOKEN_FILE}")
    parser.add_argument("--code", help="Finish --login with the callback URL (or bare code)")
    args = parser.parse_args()

    if args.login or args.code:
        if "TRAKT_CLIENT_ID" not in os.environ:
            sys.exit("Set TRAKT_CLIENT_ID first.")
        login() if args.login else finish_login(args.code)
        return

    content_dir = Path(__file__).parent.parent / "content" / "watching"
    entries: dict[tuple[str, str], dict] = {}
    if args.movies:
        entries.update(read_nas(args.movies, "movie"))
    if args.tv:
        entries.update(read_nas(args.tv, "tv"))

    use_trakt = "TRAKT_CLIENT_ID" in os.environ and TOKEN_FILE.exists()
    if use_trakt:
        merge_trakt(entries)
    else:
        print("Note: TRAKT_CLIENT_ID unset or no --login token; NAS only.", file=sys.stderr)

    def rewatched(e: dict) -> bool:
        return e["rewatched"] >= args.min_rewatched

    def finished(e: dict) -> bool:
        return e["aired"] >= args.min_episodes and complete(e) >= args.min_complete

    def qualifies(e: dict) -> bool:
        if not use_trakt:
            return bool(e["nas"])
        if e["kind"] == "tv":
            return rewatched(e) or finished(e)
        return e["plays"] >= args.min_plays or bool(e["nas"] - {"movie"})

    posted = existing_titles(content_dir)
    candidates = [e for (_, k), e in entries.items() if qualifies(e) and k not in posted and e["imdb"] not in posted]
    skipped = sum(1 for k, e in entries.items() if qualifies(e)) - len(candidates)

    groups = [
        (f"TV: rewatched {args.min_rewatched}+ episodes", lambda e: e["kind"] == "tv" and rewatched(e),
         lambda e: -e["rewatched"]),
        (f"TV: watched {args.min_complete:.0%}+ of {args.min_episodes}+ episodes", lambda e: e["kind"] == "tv" and not rewatched(e),
         lambda e: (-complete(e), -e["distinct"])),
        (f"Movies: {args.min_plays}+ plays or NAS favorites", lambda e: e["kind"] == "movie",
         lambda e: (-e["plays"], e["title"].lower())),
    ]
    lines = [HEADER, f"# Sources: NAS{' + Trakt' if use_trakt else ''}. Skipped {skipped} already posted."]
    for heading, keep, order in groups:
        group = sorted((e for e in candidates if keep(e)), key=order)
        lines += ["", f"# ── {heading} ({len(group)}) " + "─" * 20]
        lines += [proposal_line(e) for e in group]

    text = "\n".join(lines) + "\n"
    if args.out:
        args.out.write_text(text)
        print(f"Wrote {len(candidates)} proposals to {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
