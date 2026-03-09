---
layout: post
title: "Taming Git Worktrees: From Chaos to a Clean Hub Structure"
description: "I set up git worktrees poorly for months — inconsistent names, folders scattered everywhere. Here's the clean hub structure I wish I'd started with, plus a tool to migrate your existing mess."
date: 2026-03-06T10:00:00.000Z
permalink: /posts/2026-03-06-taming-git-worktrees/
draft: false
categories:
    - tech
tags:
    - tech
    - git
    - linux
    - developer-tools
    - workflow
author: Mike Crowe
seo:
    title: "Taming Git Worktrees: From Chaos to a Clean Hub Structure"
    description: "How to organize git worktrees into a clean .bare/.git hub structure, with a migration script for your existing mess and a git alias for starting fresh."
    image: images/featured.png
featured_image: images/featured.png
excerpt: "I set up git worktrees poorly for months — inconsistent names, folders scattered everywhere. Here's the clean .bare/.git hub structure I wish I'd started with, and a tool to migrate the mess you've already made."
---

_This post was written with AI assistance (Claude) for structure and formatting. The ideas, chaos, and embarrassing folder names are entirely my own._

---

Let me start with a confession:

> **I have been using git worktrees for months and my setup has looked like a disaster the whole time.**

Different repos organized differently. Some had the main checkout named one thing with `-main` and `-feature` suffixes on sibling directories. Others had worktrees scattered to wherever my terminal happened to be open when I ran `git worktree add`. One project had its worktrees split across two different drives because — honestly, I don't even remember why. It seemed like a good idea at 11pm.

If you've ever run `git worktree list` and squinted at the output trying to figure out which of those paths actually still exists on disk, you know the feeling.

Here's what my output actually looked like for one project:

```
/data/mcrowe/Programming/Pinnacle/internal-apps         af0b176b [upgrade-node-22-clean]
/data/mcrowe/Programming/Pinnacle/internal-apps-main    53843e57 [main]
/data/mcrowe/Programming/Pinnacle/internal-apps-upgrade 90fc8834 [upgrade-node-22]
/home/mcrowe/Programming/Pinnacle/fix-middy             1444dfd8 [fix-middy]
```

Note that last one. Different home directory tree. Different drive. Just... there.

This is the post I wish I'd found two years ago.

---

## What Git Worktrees Actually Are

Quick refresher, in case you haven't gone down this rabbit hole yet: git worktrees let you have multiple branches checked out simultaneously as separate directories. Instead of `git stash` → `git checkout` → forget what you were doing → `git stash pop` and hope nothing caught fire, you just `cd ../feature-auth` and your main branch is still exactly where you left it.

The feature is genuinely great. The problem is there's no enforced structure. You can add a worktree anywhere, name it anything, and git won't complain. Which means you end up with whatever you were thinking at the moment you created it — and that's what you're stuck with forever. Or until you write a migration script. Which is what happened here.

---

## The Hub Structure I Wish I'd Started With

Here's the pattern that actually makes sense:

```
my-project/          ← the hub directory
├── .bare/           ← bare git repo (the actual git database)
├── .git             ← plain text file: "gitdir: ./.bare"
├── main/            ← worktree: main branch
├── feature-auth/    ← worktree: whatever you're working on
└── hotfix-payment/  ← worktree: fire drill du jour
```

Two things make this work:

**`.bare/`** holds all the git objects, refs, pack files — the whole database — but has no working tree of its own. It's the hub that all worktrees connect back to.

**`.git`** (a plain text file, _not_ a directory) contains just `gitdir: ./.bare`. This single line is the trick that makes every tool — IDEs, `gh`, git itself — find the repo correctly when you're anywhere inside the hub directory.

Then each branch gets its own subdirectory, named after the branch. Want to review a PR? `git worktree add ./review-pr-42 pr-42`. Done. Want to work on a hotfix while keeping your feature branch untouched? You already have it. The directory names tell you everything you need to know.

### Why `.bare/` + `.git` file, instead of making the directory itself bare?

Bare repos — where the directory _is_ the git database — confuse a lot of tooling. IDEs look for a `.git` _directory_ as a signal that they're inside a repo. GitHub CLI does the same. With the `.git` file redirect, you satisfy everyone: git finds it, your IDE finds it, `gh` finds it, and you find it too.

There's also a fetch config gotcha worth knowing about. Bare clones don't set `remote.origin.fetch` the way a normal `git clone` does, so running `git fetch` afterward won't actually pull remote-tracking branches. You need:

```bash
git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
```

Miss this and you'll wonder why `git branch -r` shows nothing. (Ask me how I know.)

---

## Starting Fresh: A Git Alias

For new repos, I added `clone-worktree` to `~/.config/git/config`:

```ini
[alias]
    clone-worktree = "!f() { \
        url=\"$1\"; \
        name=$(basename \"$url\" .git); \
        dest=$(realpath -m \"${2:-$name}\"); \
        if [ -e \"$dest\" ]; then echo \"Error: '$dest' already exists\"; exit 1; fi; \
        mkdir -p \"$dest\"; \
        git clone --bare \"$url\" \"$dest/.bare\"; \
        printf 'gitdir: ./.bare\\n' > \"$dest/.git\"; \
        git -C \"$dest\" config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'; \
        git -C \"$dest\" fetch; \
        branch=$(git -C \"$dest\" symbolic-ref --short HEAD); \
        git -C \"$dest\" worktree add \"$dest/$branch\" \"$branch\"; \
        printf 'Hub: %s\\nWorktree: %s/%s\\n' \"$dest\" \"$dest\" \"$branch\"; \
    }; f"
```

Usage:

```bash
# Clones into ./my-repo hub, checks out main branch into ./my-repo/main/
git clone-worktree git@github.com:drmikecrowe/my-repo

# Or put it wherever you want
git clone-worktree git@github.com:drmikecrowe/my-repo ~/Projects/CustomerA/my-repo
```

You get this immediately:

```
my-repo/
├── .bare/
├── .git        ← "gitdir: ./.bare"
└── main/       ← ready to work in
```

Then add branches as worktrees when you need them:

```bash
git -C ~/Projects/my-repo worktree add feature-auth
```

### The gotcha I hit immediately

I ran `git clone-worktree` targeting a directory that already existed on disk (I'd already created the project folder by hand). The alias tries to write `gitdir: ./.bare` to `.git`, but `.git` was already a directory. Here's the actual error:

```
f(): line 1: /data/mcrowe/Programming/Personal/git-worktree-organize/.git: Is a directory
fatal: 'main' is already used by worktree at '...'
```

The `if [ -e "$dest" ]` guard at the top handles this now — it bails with a clear error before touching anything. It wasn't there on the first run. What a PITA.

---

## Migrating Your Existing Mess

Starting fresh is the easy part. What about the repos you've had for two years with worktrees named whatever you were thinking when you created them?

That's what [git-worktree-organize](https://github.com/drmikecrowe/git-worktree-organize) is for. It takes your existing git repo plus all its linked worktrees and reorganizes everything into the hub structure — wherever you want it.

```bash
# Convert in place (renames original to .old, creates hub at the original path)
npx git-worktree-organize ~/Projects/Pinnacle/internal-apps

# Or move the whole thing somewhere completely different
npx git-worktree-organize ~/Projects/CustomerA/old-project ~/Projects/CustomerB/new-location
```

Here's the thing about that second form: **this is also just a general worktree relocation tool**. If you want to move a repo with all its worktrees to a completely different folder — or a completely different filesystem — this handles it. It detects cross-filesystem moves (comparing device numbers) and falls back from `mv` to `cp -a` + `rm -rf` automatically.

Under the hood, it:

1. Reads `git worktree list --porcelain` to enumerate everything
2. Copies `.git/` contents → `DEST/.bare/`, sets `core.bare = true`
3. Fixes `remote.origin.fetch`
4. Writes the `DEST/.git` redirect file
5. Strips `.git/` from your main repo's directory, moves it to `DEST/<branch>/`, and wires it up as a proper linked worktree (with a new `worktrees/<name>/` admin entry in `.bare/`)
6. Moves each linked worktree to `DEST/<branch>/` and updates the pointer files in both directions

The pointer files are the fiddly part. Each linked worktree has a `.git` _file_ containing `gitdir: /path/to/.bare/worktrees/<name>`. And inside `.bare/worktrees/<name>/gitdir` is the reverse pointer back to the worktree. Both sides need updating every time something moves. Get one wrong and git thinks the worktree is gone.

Before running, it shows you exactly what it's going to do and asks for confirmation:

```
Worktrees to migrate:
  [upgrade-node-22-clean]  (labeled [main])  →  /new/location/upgrade-node-22-clean
  [main]                                     →  /new/location/main
  [upgrade-node-22]                          →  /new/location/upgrade-node-22
  [fix-middy]                                →  /new/location/fix-middy

Hub destination: /new/location  (bare repo at /new/location/.bare)

Proceed? [y/N]
```

---

## After

Running it on `internal-apps`:

```
/data/mcrowe/Programming/Pinnacle/internal-apps/
├── .bare/
├── .git
├── main/
├── upgrade-node-22/
├── upgrade-node-22-clean/
└── fix-middy/
```

Branch names as directory names. Everything in one place. `git worktree list` makes sense for the first time in years.

---

## The Proper Tool: git-worktree-organize on npm

The git alias handles fresh clones well, but migrating existing repos is a different beast. There are actually several ways a git repo-with-worktrees can look in the wild:

| What you have          | How to detect it                                      |
| ---------------------- | ----------------------------------------------------- |
| Standard non-bare repo | `.git/` directory, `core.bare=false`                  |
| Already a hub          | `.bare/` + `.git` file                                |
| Bare root              | The directory itself is the bare repo                 |
| Bare in `.git/`        | `.git/` directory, `core.bare=true`                   |
| Bare external          | `.git` file pointing to a gitdir stored elsewhere     |

So I built it as a proper TypeScript/Node CLI that detects which configuration type you have and handles all of them. It's on npm now — no install required:

```bash
npx git-worktree-organize <source> [destination]
```

---

## The Short Version

Git worktrees are great. The problem was never the feature — it was the absence of an obvious convention. The `.bare/.git` hub structure is that convention. Branch names become directory names, everything has a predictable home, and you can move the whole thing anywhere without breaking anything.

Starting fresh? Use the alias. Already have a mess? Use `npx git-worktree-organize`.

Source, issues, and contributions: [github.com/drmikecrowe/git-worktree-organize](https://github.com/drmikecrowe/git-worktree-organize)

_Have your own creative git worktree disaster story? Hit me up on [GitHub](https://github.com/drmikecrowe) or wherever you found this post._
