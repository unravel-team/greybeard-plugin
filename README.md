# Greybeard plugin for Claude Code

Phone a greybeard: lets your AI agent ask a real engineer when it's stuck or about to make a call you can't judge (going live, payments, your users' data). The answer comes back into your chat.

Greybeard is invite-only for now. Join the waitlist at https://greybeard.unravel.tech.

## Install

In Claude Code:

    /plugin marketplace add unravel-team/greybeard-plugin
    /plugin install greybeard@greybeard

Restart Claude Code, then ask: *"Ask a greybeard how to put my app online safely."* The first call shows a link; sign in with Google once. Needs [uv](https://docs.astral.sh/uv/) and Python 3.10+.

## Optional: status line badge

Shows open questions and replies in the status bar. Add to `~/.claude/settings.json`:

    "statusLine": { "type": "command", "refreshInterval": 15,
      "command": "python3 ~/.claude/plugins/marketplaces/greybeard/hooks/greybeard_statusline.py" }

## Sign out

Ask your agent to "log out of greybeard".

## What's in here

- `mcp/greybeard_mcp.py`: the tools your agent calls (ask, check, rate, log out).
- `hooks/`: shows replies in the chat on your next message, and the status line badge.
- `skills/ask-a-greybeard/`: tells the agent when asking is worth it.

Your question and the context your agent writes are sent to greybeard.unravel.tech and shown to experts. The agent is told to leave out secrets and customer data. Your sign-in token is kept in `~/.config/greybeard/credentials.json`, readable only by you.
