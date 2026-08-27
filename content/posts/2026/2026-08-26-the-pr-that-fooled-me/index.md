---
layout: post
title: The PR That Fooled Me
description: How an immaculate AI-generated pull request, a second model with different training, and one concurrency bug convinced me to never ship AI code without adversarial review.
date: 2026-08-26T09:00:00.000Z
draft: false
categories:
  - tech
tags:
  - ai
  - code-review
  - testing
  - claude
author: Mike Crowe
seo:
  title: The PR That Fooled Me
  description: How an immaculate AI-generated pull request, a second model with different training, and one concurrency bug convinced me to never ship AI code without adversarial review.
  image: images/featured.png
featured_image: images/featured.png
excerpt: The best-looking PR in my repo had a data-loss race in it, and the model that wrote it reviewed itself and found nothing. Here's the three-week paper trail that changed how I ship code.
---
_This post was written with AI assistance (Claude) for structure and formatting. The PRs, the bug, and the opinions are entirely my own._

**The best-looking PR in my repo had a data-loss race in it, and the model that wrote it reviewed its own work and found nothing.**

I've written before about [where AI belongs in software delivery](/posts/2026/2026-08-24-people-approve-agents-check/), and the short version of that post is: people approve, agents check. This post is the origin story. It's three weeks of commit history in one public repo, and I'm going to walk you through it in order, because the order is the argument.

## Act one: the PR that looked perfect

On July 28 I merged [PR #169](https://github.com/drmikecrowe/harnessed/pull/169) in [harnessed](https://github.com/drmikecrowe/harnessed). Opus wrote most of it. Go look at the PR body, because the body is the point.

(A word about the repo, since I'm about to link into it four times and I haven't formally announced it. `harnessed` is a tool for people who want different configurations of their agentic harness in container isolation: you compose recipes of skills, MCP servers, and services into a named stack, and it launches in a pod with nothing leaking in from your host config. Toolchains come from mise, every dependency is pinned, updates respect a seven-day minimum release age so a poisoned package gets caught before it reaches a build, and images get Snyk and Socket scans at build time. It's my daily driver and I'm dogfooding it hard, but it's alpha: today it supports Claude Code and omp, with more harnesses planned. If that's a tool you've been wanting and you'd like to help shape it, come on in. Otherwise, the announcement post is coming when it's ready for you.)

It has a measured-cost table justifying the design (a one-line edit to an install script cost 307 seconds through the container build and 4.3 seconds natively, so the installs moved to runtime volumes). It lists two premises that were tested and disproved along the way, with links to where each was recorded instead of quietly dropped. It documents four bugs found during the work, each fixed with a test that fails without the fix.

That is a better PR writeup than most humans produce. I know because I'm one of the humans. When your AI hands you work at that level of polish, with benchmarks and disproved hypotheses and regression tests, skepticism starts to feel rude. I got comfortable. The polish was doing exactly what polish does.

## Act two: a second opinion I didn't ask nicely for

Four days later I put up [PR #185](https://github.com/drmikecrowe/harnessed/pull/185), a rework of the CLI verbs. Same workflow, same model, same confident writeup: 1,766 tests passing, every removed test accounted for in a table, docs updated.

This was also the first PR I ran through CodeRabbit, mostly out of curiosity. I had already asked Opus to review its own work. It found nothing worth stopping for.

CodeRabbit found this:

> Two concurrent `--recipe` invocations with the same recipe set derive the same name. Both can observe `preexisting=False` before either mints, so both return a non-`None` `minted_dir`. [...] If one of the two concurrent launches fails `_build_stack` while the other is still using or building the same stack, the failing process deletes a manifest the other process depends on.

A classic check-then-act race, in the one code path where concurrent same-name launches aren't exotic (sharing one stack across repos is the design goal, so two repos starting together is the expected case). A failed build could delete a manifest another live launch was using. Data loss, sitting inside a PR whose test table I had just admired.

Here's the part that actually rattled me. The race wasn't even introduced by #185. It was pre-existing code that the refactor made visible. The model that wrote it, the model that refactored it, and the model that reviewed both had walked past it every time. A differently-trained model looked at it once and stopped.

That's when the lesson landed. The author always finds a reason the work is right. That's true of me, and it turns out to be true of a frontier model reviewing its own output. Self-review isn't review.

## Act three: moving the fight upstream

I didn't fix the race in #185. I scoped it out deliberately (that PR was about CLI grammar, and mixing a concurrency fix into it is how you get neither reviewed well) and recorded it as [issue #287](https://github.com/drmikecrowe/harnessed/issues/287).

By the time that issue got picked up in mid-August, my process had changed shape. Read the issue comments in order and you can see the new machinery:

1. A **DECISION** comment recording the fix approach, with current line numbers, so the implementer doesn't re-derive the research.
2. A full **SPEC** posted as a comment, before any code existed, with a line I now consider load-bearing: *"Approval of this spec is the gate that authorizes implementation."*
3. The spec itself went through adversarial review before I approved it, and the review changed it. Poking holes in a document costs minutes. Poking the same holes in an implementation costs a rewrite.
4. A human (me) applying the `spec-approved` label, timestamped.

That third point deserves a beat. When I started running adversarial reviews against code, the payoff was catching bugs. When I pointed the same treatment at specs, the payoff was bigger: every hole caught at spec time is a hole that never becomes code. The mint-race spec that got implemented was not the spec I first wrote.

## Act four: what "done" looks like now

The fix landed as [PR #414](https://github.com/drmikecrowe/harnessed/pull/414), and its body is an EVIDENCE document. Not a description of the change. Proof, organized so a reviewer can attack it:

- A **spec-to-test mapping**: eight scenarios from the approved spec, each mapped to a named test.
- A concurrency test that **deterministically fails against the old code** (two threads claim ownership) and passes with the fix (one does). Not "we added tests." A reproduction first.
- **Five hand-planted mutants**, all killed, because if your test suite can't catch a deliberate mistake it wasn't going to catch an accidental one.
- Two rounds of **adversarial review**, findings fixed and re-checked.
- And a section titled **"Not proven"**: the container build path the suite never executes, the NFS caveat on advisory locks, the mutation tool that wouldn't run in a worktree, the fact that the final SHA's adversarial pass was substituted rather than re-run.

That last section is the one I'd defend hardest. Evidence that can't tell you what it doesn't cover isn't evidence, it's marketing. The "Not proven" list is what makes the rest of the document worth believing.

## What I actually learned

**The confidence is a constant. The quality is not.** Every PR in this story arrived with the same certainty. One of them carried a data-loss race. Nothing in the presentation distinguishes them, which means the presentation carries no information. You have to attack the work.

**Self-review doesn't work, for silicon or for me.** The reviewer needs to carry none of the author's assumptions. A fresh session helps. A different model with different training helps more (with one caveat: frontier models share training data and failure modes, so even two-model review has correlated blind spots; it's a design goal, not a guarantee).

**Upstream beats downstream.** Adversarial review of code catches mistakes. Adversarial review of the spec prevents them, at a fraction of the cost. 

**This costs tokens, and it's the cheapest spend in the budget.** Every adversarial pass is a second model re-reading finished work. I meant it when I called them the cheapest tokens I spent all year: the alternative was shipping the race and paying for it during someone's demo.

If you want the team-scale version of this, with gates and human sign-off and the process we're building around it at Pinnacle Solutions Group, that's the [People Approve, Agents Check](/posts/2026/2026-08-24-people-approve-agents-check/) post. This one is just the receipt trail: one repo, three weeks, and the PR that taught me to stop trusting a clean explanation.

_Have your own "the AI sounded so sure" stories? Hit me up on [GitHub](https://github.com/drmikecrowe) or wherever you found this post._
