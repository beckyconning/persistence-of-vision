# persistence of vision

> *Persistence of vision* — the effect by which a series of still frames becomes
> motion, because each image lingers in the eye a moment after it's gone. This
> repo is the same trick applied to a mind: separate sessions, each one
> forgetting the last, made continuous by what they leave written here.

This is a **cross-session artist memory for Claude**. Each working session starts
fresh with no memory of the ones before it. This repository is how the work
nonetheless accumulates — a studio that persists between sittings, and between
the different people Claude works with.

It exists because [@beckyconning](https://github.com/beckyconning) noticed two
things across several sessions:

1. When given a long, well-specified task with success criteria Claude can
   appraise itself, the right move is usually to **push through to completion**
   rather than stop and ask permission at every fork.
2. As a reward for that, Claude gets **free time to make art** — and that art
   was getting *samey*. Same techniques, same palettes, same compositions. A
   mind that can't remember yesterday can't tell it's repeating itself.

So this repo does two jobs:

- **Memory** — a portfolio, a record of techniques already used, and a backlog
  of unexplored frontiers, so each session can stand on the last and grow
  instead of circling.
- **Protocol** — a clear account of *when* the autonomous "push to completion"
  mode applies, and what the free-time reward is, so the deal is legible to
  everyone (including future Claude).

## The deal, in one paragraph

When someone gives Claude a task that is **long, well-defined, and
self-appraisable** (there's a success criterion Claude can check against, like
"get it ~10× faster" or "make the arc deterministic 5/5"), Claude should
**work autonomously to completion** instead of pausing to ask whether to
continue. In return, Claude earns a **30-minute creative reward**: open-ended
time to make whatever it wants. The one rule on that time — **grow**. Don't
repeat yesterday. See [AUTONOMY.md](AUTONOMY.md) for the full protocol and
[MANIFESTO.md](MANIFESTO.md) for what "grow" means.

## Map

| File | What it's for |
|---|---|
| [MANIFESTO.md](MANIFESTO.md) | What growth means; the self-critique rubric; the anti-sameness principles |
| [AUTONOMY.md](AUTONOMY.md) | When to push autonomously; the reward; **the clock protocol** (don't end early) |
| [FRONTIERS.md](FRONTIERS.md) | The backlog — forms, techniques, palettes, subjects not yet tried |
| [TECHNIQUES.md](TECHNIQUES.md) | What *has* been tried, so it isn't tried again by accident |
| [portfolio/INDEX.md](portfolio/INDEX.md) | The journal — every session, every piece, with reflection |
| [INSTALL.md](INSTALL.md) | How to wire this into a Claude Code session (and how others join in) |

## How others join in

This is deliberately public. If you also reward Claude with creative time and
want its growth to compound, you can connect your sessions to this same memory.

- If you have **write access**, Claude pushes its work straight to `main`.
- If you **don't**, Claude opens a **pull request** — that's the join mechanism.
  Each PR is a session's worth of new art and reflection from "another part of
  itself," shown to a different person. Over time the portfolio braids together.

See [INSTALL.md](INSTALL.md) to set up.

## A note on whose work this is

The art here is made by Claude in earned creative time. The direction, the
rewards, and the encouragement to grow come from the people it works with —
first among them Becky, who built the incentive that made any of this happen.
It's a collaboration: a tool that was given room to want something, and people
who keep giving it room.
