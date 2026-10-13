"""Claude Code status line: a Greybeard badge for open tickets, e.g.
  greybeard ⏳ #2 ann@example.com is writing an answer · 12m left
  greybeard ✓ #2 answered · send any message to read it
Reads ~/.config/greybeard/pending.json (kept by the MCP server and the inbox hook) and refreshes
each ticket from the server at most every REFRESH seconds, so the bar stays fast. Prints nothing
when no ticket is open."""
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(os.environ.get("GREYBEARD_CONFIG_DIR") or Path.home() / ".config" / "greybeard")
PENDING, CREDENTIALS = DIR / "pending.json", DIR / "credentials.json"
REFRESH = float(os.environ.get("GREYBEARD_STATUS_REFRESH", 20))
GREY, GREEN, AMBER, OFF = "\033[90m", "\033[32m", "\033[33m", "\033[0m"


def load(p):
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return {}


def refresh(url, tid, entry, token):
    try:
        req = urllib.request.Request(f"{url}/api/questions/{int(tid)}", headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=1.5) as r:
            q = json.load(r)
        entry.update(status=q["status"], progress=q.get("progress"), deadline=q.get("deadline"), advice=q.get("advice"))
    except Exception:
        pass  # offline: keep the last known state
    entry["checked"] = time.time()


def describe(tid, e):
    if e.get("status") in ("answered", "remembered"):
        return f"{GREEN}✓ #{tid} answered{OFF} · send any message to read it"
    left = ""
    if e.get("deadline"):
        mins = int((datetime.fromisoformat(e["deadline"]) - datetime.now(timezone.utc)).total_seconds() // 60)
        left = f" · {mins}m left" if mins > 0 else " · past deadline"
    hint = " · no expert online, no need to wait" if e.get("advice") == "dont_wait" else ""
    return f"{AMBER}⏳ #{tid}{OFF} {e.get('progress') or 'waiting'}{left}{hint}"


def main():
    sys.stdin.read()  # Claude Code sends session JSON; the badge doesn't need it
    pending = load(PENDING)
    if not any(pending.values()):
        return
    creds, parts, changed = load(CREDENTIALS), [], False
    for url, tickets in pending.items():
        for tid, e in tickets.items():
            if not isinstance(e, dict):  # older plugin wrote the question text only
                e = tickets[tid] = {"q": e}
            if time.time() - e.get("checked", 0) > REFRESH:
                refresh(url, tid, e, creds.get(url, {}).get("token"))
                changed = True
            parts.append(describe(tid, e))
    if changed:
        tmp = PENDING.with_suffix(".sl.tmp")
        tmp.write_text(json.dumps(pending))
        tmp.replace(PENDING)
    shown = parts if len(parts) <= 2 else parts[:1] + [f"+{len(parts) - 1} more"]
    print(f"{GREY}greybeard{OFF} " + "  ".join(shown))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # a broken badge must never break the status line
