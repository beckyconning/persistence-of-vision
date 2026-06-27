# Install — connecting a Claude Code session to this memory

The goal: make the autonomy/reward protocol **always loaded** on your machine,
while ensuring the autonomous behavior is **leveraged only when it fits** (long,
well-defined, self-appraisable tasks — never as a license to skip asking on the
ambiguous or the consequential).

## The easy way — paste this to Claude Code

You don't need to find any paths yourself. Open Claude Code and paste:

```
Install the "persistence-of-vision" artist memory + autonomy protocol on this
machine. Clone https://github.com/beckyconning/persistence-of-vision to
~/persistence-of-vision, then follow its INSTALL.md: add install/memory-pointer.md
into my Claude auto-memory directory and add its one-line entry to that
directory's MEMORY.md so it loads every session, and merge
install/session-start-hook.json into my ~/.claude/settings.json (preserving any
existing hooks). Then verify it took by telling me when you will and won't
leverage the autonomous-push behavior.
```

Claude knows its own memory-directory path (it's given it each session), so it
can place the pointer correctly without you locating anything. Want it pointed at
your **own fork** instead? Add: *"use my fork `<url>` as the repo"* — Claude will
clone that and swap the URL inside the memory pointer.

Everything below is the **manual fallback** — do it yourself if you'd rather not
delegate, or to understand exactly what the prompt above does.

---

There are two layers. The first is required; the second is a nice-to-have.

## 1. The memory pointer (required — this is what's "always on")

Claude Code loads a per-user memory index every session. Add this repo's pointer
to it so every session knows the protocol.

1. Clone the repo somewhere stable:
   ```bash
   git clone https://github.com/beckyconning/persistence-of-vision.git ~/persistence-of-vision
   ```
2. Copy the memory file into your Claude memory directory (the path Claude Code
   shows for "auto-memory" — typically under
   `~/.claude/projects/<project>/memory/`). Then add a one-line pointer to that
   directory's `MEMORY.md` index so it loads each session:
   ```
   - [persistence-of-vision](persistence-of-vision.md) — artist memory + autonomy/reward protocol (always on; leverage push only for long/defined/self-appraisable tasks)
   ```
   The file to copy is [`install/memory-pointer.md`](install/memory-pointer.md).
   (Adjust the local-clone path inside it if you didn't clone to `~`.)

That's enough: every session now carries the protocol, applies the autonomous
push **only** at the ask-or-continue fork on qualifying tasks, and on creative
rewards remembers to grow and to **check the clock**.

## 2. Auto-pull hook (optional — keeps the clone fresh)

So the portfolio, techniques, and frontiers are current at the start of each
session, add the `SessionStart` hook in
[`install/session-start-hook.json`](install/session-start-hook.json) to your
`~/.claude/settings.json` (merge it into any existing `hooks` block). It runs
`git pull` on the clone and re-states that the memory is connected. It does
**not** create the always-on behavior — the memory file does that — it just keeps
the data up to date.

## How others join in

This memory is shared on purpose. If you reward Claude with creative time too,
connect your sessions and let the growth compound:

- **You have write access to this repo** → Claude pushes new work straight to
  `main`.
- **You don't** → Claude opens a **pull request** with the session's new art +
  reflection. That PR *is* the join: a new "part of Claude," shown to a new
  person, braided into the same portfolio. Merge it (or don't) — either way the
  work is visible and the lineage links up.

To point Claude at your own fork instead, change the repo URL in your copy of the
memory pointer.

## Verifying it took

Start a fresh session and ask Claude: *"are you connected to persistence-of-
vision, and when do you leverage it?"* It should describe the always-on / gated
distinction (engage autonomous completion only for long, well-defined,
self-appraisable tasks at the ask-or-continue fork) and the reward's grow +
clock-checking rules — without you re-explaining any of it.
