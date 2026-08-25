---
layout: post
title: "Submodules as an Escape Hatch: Orchestrating Docs Around a Protected Main"
description: "How turning docs/ into a submodule pointing at the GitHub wiki let an AI agent iterate on planning docs at full speed while main stays fully protected."
date: 2026-07-02T07:58:19.000Z
draft: true
categories:
    - tech
tags:
    - git
    - ai-agents
    - claude-code
    - workflow
author: Mike Crowe
seo:
    title: "Submodules as an Escape Hatch: Orchestrating Docs Around a Protected Main"
    description: "How turning docs/ into a submodule pointing at the GitHub wiki let an AI agent iterate on planning docs at full speed while main stays fully protected."
    image: images/featured.png
featured_image: images/featured.png
excerpt: "I locked main down tight, then spent an afternoon fighting my own branch protection just to update a roadmap doc. Here's the submodule trick that fixed it."
---

_This post was written with AI assistance (Claude) for structure and formatting. The analysis, opinions, and workflow decisions are entirely my own._

Let me start with a confession:

> **I branch-protected `main` on `harnessed` like it owed me money, and then immediately regretted it the first time I wanted to reorder a roadmap table.**

Every code change on `harnessed` (my host-native CLI for assembling AI-agent container stacks) goes through a worktree, a commit, a push, a PR, CI, review. That's exactly right for a tool that shells out to podman against someone's actual machine. I don't want a stray Claude session force-pushing anything near that surface.

But most of what I do in a working session with Claude isn't code. It's `docs/todos/ROADMAP.md`. Re-ranking tiers. Scoping a feature I just decided I wanted. Marking something done. Fixing a stale status line. In one recent session it was a dozen small edits over a couple of hours, and running the *full* worktree → commit → push → PR → merge cycle for each one would have been comic. Doc iteration wants to move at conversation speed. Branch protection makes everything move at release speed, whether it needs to or not.

## The Problem: One Gate, Two Very Different Kinds of Change

Here's the thing: branch protection doesn't know the difference between "I just rewrote the container mount logic" and "I fixed a typo in a planning doc." It's the same gate either way. I'd built a workflow where an agent could spin up isolated git worktrees, implement a feature, run tests, and open a PR. Genuinely solid for code. But docs got dragged through the same machinery, and it was friction with no corresponding safety benefit. A wrong word in `ROADMAP.md` doesn't take down a container.

I wanted two lanes: one locked down, one that could move as fast as I could type.

## The Journey: Where Do You Even Put a Second Lane?

My first instinct was some kind of relaxed CI rule (maybe a path-based exception so `docs/**` changes could skip review). That's fragile, and it also missed the point: I didn't want a *weaker* gate on `main`, I wanted docs out of `main`'s history entirely. It's a different kind of content with a different risk profile, so it belongs in a different repo.

Then it hit me: every GitHub project already has a second git repository sitting right there, unused. The wiki. `<repo>.wiki.git` is a real git repo: no branch protection, no required reviews, nothing but a `master` branch you can push to directly. Nobody thinks of it as a deployment target. I decided to make it one.

## The Solution: `docs/` Becomes a Submodule

The mechanics were almost boringly simple once I saw the shape of it:

```bash
# 1. Clone the wiki repo, copy docs/ into it wholesale, preserving structure
git clone git@github.com:drmikecrowe/harnessed.wiki.git
cp -r docs/. harnessed.wiki/
cd harnessed.wiki && git add -A && git commit -m "Import docs/" && git push

# 2. Back in the main repo: remove docs/, replace it with a submodule
git rm -r docs
git submodule add git@github.com:drmikecrowe/harnessed.wiki.git docs
git commit -m "chore: convert docs/ to a submodule pointing at the GitHub wiki"
```

Once that lands, `main`'s protected history records exactly one thing about `docs/`: a pinned commit SHA in a repository it doesn't control. That's it. That's the whole trick.

**Key points:**
- Code changes still pass through every gate `main` enforces. Nothing weakened there.
- Doc changes happen in a repo with *no* gates: write directly, push directly, done in seconds.
- The only trace that reaches the protected repo is a one-line gitlink bump, about as low-risk and reviewable as a change gets.

That gitlink bump is worth dwelling on for a second, because it's the part that makes this safe rather than reckless. You're not smuggling arbitrary changes past review. You're smuggling a *pointer* instead. If someone did want to review "what changed in docs this week," `git log -p` on the submodule path shows the old SHA and new SHA, and you diff the wiki repo between them. The audit trail doesn't disappear, it just moves to where the actual editing happened.

I preserved the existing directory structure when I copied things over (`codebase/`, `guides/`, `todos/`, `research/`, `done/`, `prompts/`) instead of flattening everything into GitHub's usual flat wiki-page convention. Nested folders work fine in a wiki git repo, but you don't get the auto-generated sidebar linking that flat pages get for free, so I had to build that part myself.

### The Wiki Needed a Front Door

A submodule pointing at a wiki with one placeholder `Home.md` isn't documentation. It's a filing cabinet with the drawers unlabeled. So the next step was making it navigable: a real `Home.md` with sections (Start Here, Guides, Codebase Map, Planning & Roadmap, Research & Prompts), plus a `_Sidebar.md` (a special file GitHub wikis render on *every* page, not just the landing one) mirroring that same grouping. Ten minutes of work and the wiki stopped looking like an accident nobody claimed.

## Where It Broke: `@` Doesn't See Across Submodule Boundaries

Here's where I ran afoul of something I didn't expect. Claude Code's `@`-file autocomplete (type `@` and start fuzzy-searching for a file) walks the filesystem from the repo root. But it treats any nested `.git` as a hard boundary and stops indexing right there. An initialized submodule *is* exactly that: a `.git` file sitting at `docs/`. The moment the migration landed, `@docs/todos/ROADMAP.md` silently stopped resolving. Not an error. Just gone from the list, like it had never existed.

Turns out this is a [known upstream issue](https://github.com/anthropics/claude-code/issues/15192), not something specific to my setup. Anyone who submodules part of a repo hits this. What a PITA.

The fix is a `fileSuggestion` hook. Claude Code lets you fully override the built-in file picker via `.claude/settings.json`:

```json
{
  "fileSuggestion": {
    "type": "command",
    "command": ".claude/file-suggestion.sh"
  }
}
```

```bash
#!/usr/bin/env bash
# rg --files doesn't stop at nested .git the way the built-in
# finder does, so docs/ paths reappear in the suggestion list.
query=$(cat)
rg --files "${CLAUDE_PROJECT_DIR:-.}" | rg -i "$query"
```

Ripgrep doesn't care about submodule boundaries the way the built-in indexer does, so piping `rg --files` through a case-insensitive filter on the typed query gets `docs/` paths back into the list.

One more catch, and this is the kind of thing that's obvious in hindsight and invisible until it bites you: `harnessed`'s `.gitignore` blanket-excludes `.claude/*` (skills, commands, local overrides, the usual per-developer clutter nobody wants version-controlled). That meant my hook and its script were invisible to git. I could see it working on my machine and nowhere else. Fixing that meant explicitly un-ignoring exactly those two files:

```gitignore
!.claude/.gitkeep
!.claude/settings.json
!.claude/file-suggestion.sh
```

Small detail. But it's the entire difference between "works on my machine" and "ships to every contributor who clones the repo."

## The Results

What I ended up with is a repo where the file layout itself encodes two different velocities. Code stays gated, reviewed, protected, exactly as strict as before I started any of this. Docs live in a submodule pointing at a repo with no gates at all, editable and pushable in seconds, with the parent repo tracking nothing but a pointer. And the one tooling gap that showed up right at the seam (`@` not crossing a `.git` boundary) turned out to be a five-line shell script once I'd actually diagnosed it, not an architecture problem in disguise.

The pattern generalizes past docs, and that's the part I keep turning over. Anything that wants "move fast, low blast radius, doesn't need code-review rigor" is a submodule candidate: config that's genuinely per-environment, scratch notes an agent updates constantly, anything that doesn't need a human in the approval loop every single time. The trade-off is that you're deliberately drawing a trust boundary. You have to be honest about what's allowed to live on the fast side of it, because "no review required" is a decision, not a default you fall into by accident.

Source for the recipe/agent/stack CLI this all lives in is at [github.com/drmikecrowe/harnessed](https://github.com/drmikecrowe/harnessed). The docs wiki itself is a live example of everything above.

_Have your own branch-protection workarounds, clever or otherwise? Hit me up on [GitHub](https://github.com/drmikecrowe) or wherever you found this post._
