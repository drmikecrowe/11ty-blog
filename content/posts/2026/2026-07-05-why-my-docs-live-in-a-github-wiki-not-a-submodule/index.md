---
layout: post
title: "Why My Docs Live in a GitHub Wiki, Not a Submodule"
description: "How cloning a repo's wiki into docs/ sidesteps branch protection and submodule pin hell, plus the @ file-search fix that came with it."
date: 2026-07-05T06:58:14.000Z
draft: true
categories:
    - tech
tags:
    - git
    - github
    - docs
    - claude-code
author: Mike Crowe
seo:
    title: "Why My Docs Live in a GitHub Wiki, Not a Submodule"
    description: "How cloning a repo's wiki into docs/ sidesteps branch protection and submodule pin hell, plus the @ file-search fix that came with it."
    image: images/featured.png
featured_image: images/featured.png
excerpt: "I locked my main branch so nobody (including me) could push straight to it. Then I remembered I still needed to write design docs and roadmaps without opening a PR for every typo fix."
---

_This post was written with AI assistance (Claude) for structure and formatting. The analysis, opinions, and specifics are entirely my own._

Let me start with a confession:

> **I locked down my own main branch and immediately regretted it.**

Not because branch protection was a bad idea. It's the right call for a repo where I don't want a stray `git push` to land something half-baked. But about a day later I went to jot down a design note, a roadmap update, a "here's why we rejected this approach" doc, and ran straight into the wall I'd just built. Every one of those edits now needed a branch, a PR, a review, a merge. For a typo. For a paragraph I'd rewrite three more times before lunch.

## The problem: docs move faster than code review

Here's the scenario: I've got `harnessed`, a CLI that assembles AI-agent containers from a catalog of recipes. `main` is protected — no direct pushes, PRs only. Good for the actual source. Terrible for the pile of markdown that goes with it: architecture notes, per-recipe `PLAN.md` files, a roadmap that changes shape every time I learn something new about how a recipe actually behaves once it's built.

Design docs and roadmaps aren't like source code. They're notes to future-me. I don't want to defend a wording change in a PR review. I want to write it down and move on.

So I needed something that lived with the project instead of some disconnected wiki nobody opens, that still had real version history, and that never made me touch the protected branch just to fix a typo.

## The naive approach: a git submodule

My first instinct was a submodule. Point `docs/` at a separate repo, pin it to a commit, done — right?

Wrong, and here's where I ran afoul of the thing submodules are *for*. A submodule's whole reason to exist is the pin. The parent repo doesn't track "whatever's current in that other repo" — it tracks one specific commit SHA. Update the docs repo, and the parent repo's submodule pointer is now stale until you go bump it.

And bumping that pointer is itself a commit into `main`. Which is exactly the branch I just protected. I'd have traded "PR to edit docs" for "PR to update a pointer that says which commit of the docs to look at." Same bottleneck, with an extra layer of indirection stacked on top.

What a PITA. Submodules solve version-pinning. I didn't have a version-pinning problem. I had a "let me write markdown without a branch protection rule getting in the way" problem.

## The actual fix: docs/ is just a second git repo

Here's the secret: GitHub already ships a second git repo attached to every project, and it's called the wiki. It's got its own remote, its own history, its own permissions model, completely decoupled from `main`'s branch protection. So instead of a submodule, `docs/` in my repo is just a **plain, unpinned clone** of that wiki repo:

```bash
# The wiki's remote is always <repo-url>.wiki.git
git clone https://github.com/<org>/<repo>.wiki.git docs
```

No pin. No pointer to bump. `docs/` isn't tracked by `main` at all. It's `.gitignore`'d there:

```
# docs/ is an unpinned live clone of the project's GitHub wiki (bootstrapped by
# `harnessed build`, see _ensure_docs_wiki_clone in launcher.py). Not a submodule --
# no pinned commit, no pointer-bump PRs. Pull it yourself: git -C docs pull.
/docs/
```

I edit files under `docs/` directly, commit straight to *that* repo's main branch (which I haven't locked down, because it's just docs — the whole point), and `main` never even knows anything changed. No PR. No review queue. Just `git -C docs add . && git -C docs commit -m "..." && git -C docs push`.

I even automated the first clone so I never have to remember the URL pattern by hand:

```python
def _ensure_docs_wiki_clone() -> None:
    """Bootstrap docs/ as an unpinned live clone of the repo's GitHub wiki, when missing."""
    origin_url = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    wiki_url = re.sub(r"\.git$", "", origin_url) + ".wiki.git"
    if not (Path.cwd() / "docs").exists():
        subprocess.run(["git", "clone", wiki_url, "docs"], check=True)
```

This runs once, the first time anyone builds the project on a fresh checkout. After that it's on them (or me) to `git -C docs pull` when they want the latest. It's a real, independent git repo that just happens to live at `docs/` on disk.

## The gotcha nobody warns you about: your tools still think docs/ doesn't exist

I use Claude Code's `@` file-mention autocomplete constantly to pull docs into context. After wiring up the wiki clone, I typed `@recipe-authoring` and got back... nothing.

Turns out `.gitignore`-ing `docs/` has a side effect: any tool that respects `.gitignore` for its own file listing (which is most of them, by default, and for good reason: nobody wants `node_modules/` in their search results) now silently excludes the one directory I actually needed searchable. I'd fixed the branch-protection problem and immediately created an invisible-docs problem.

The fix lives in `.claude/settings.json`, which supports a `fileSuggestion` hook: point it at your own script and Claude Code pipes you the query on stdin instead of using its built-in file finder.

```json
{
  "fileSuggestion": {
    "type": "command",
    "command": ".claude/file-suggestion.sh"
  }
}
```

And the script has to explicitly re-include `docs/` since `ripgrep` (which respects `.gitignore` by default, same as everything else) will otherwise skip it:

```bash
#!/usr/bin/env bash
query=$(cat | jq -r '.query')
root="${CLAUDE_PROJECT_DIR:-.}"
cd "$root" || exit 1
{ rg --files .; rg --files --no-ignore-vcs ./docs; } | sed 's#^\./##' | rg -i -- "$query" | head -15
```

Two bugs I had to shake out of my first pass at this, for anyone copying it: Claude Code sends `{"query": "..."}` as JSON on stdin, not a bare string — skip the `jq -r '.query'` step and you're handing your search tool a raw JSON blob as a regex, which blows up with a parse error instead of just returning nothing. And `cd` into `$CLAUDE_PROJECT_DIR` first, or every result comes back as an ugly absolute path instead of something you'd actually want to `@`-mention.

## What I gave up

This isn't free. Nothing stops me from committing a wrong design decision straight to the wiki — there's no PR gate on it at all. I'm okay with that; it's notes to myself, not shipped behavior. What bugs me more is that a docs commit and the code commit that motivated it aren't linked by anything git understands, so I lean on writing dates into the doc itself and hoping future-me remembers the context. And `git -C docs pull` isn't automatic — I've caught myself reading stale docs more than once because I forgot to run it.

## The results

Docs and roadmaps that actually get written, because writing them doesn't cost a PR. A protected `main` that stays protected. And an `@` search that finally finds the thing I just wrote about it.

_Have your own git-workaround war stories? Hit me up on [GitHub](https://github.com/drmikecrowe) or wherever you found this post._
