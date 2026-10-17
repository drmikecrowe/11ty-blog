---
layout: post
title: First Drafts All the Way Down
description: I measured 83 stories built with a frontier model. 80% of the plans and 48% of the passing implementations needed rework before anyone should have trusted them.
date: 2026-10-17T09:00:00.000Z
draft: false
categories:
  - pinnacle
  - tech
tags:
  - ai
  - sdlc
  - testing
  - code-review
  - evidence
author: Mike Crowe
seo:
  title: First Drafts All the Way Down
  description: I measured 83 stories built with a frontier model. 80% of the plans and 48% of the passing implementations needed rework before anyone should have trusted them.
  image: images/featured.png
featured_image: images/featured.png
excerpt: "If your AI workflow is plan, build, tests pass, ship, you are shipping first drafts. I have the numbers: 80% of my plans and half of my green builds needed rework."
---
_This post was written with AI assistance (Claude) for structure, formatting, and pulling the numbers out of my logs. The process, the opinions, and the voice are my own._

<style>
.se-tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:1.5em 0}
.se-tile{border:1px solid rgba(127,127,127,.35);border-left:4px solid #b3261e;border-radius:10px;padding:14px 16px}
.se-tile.se-time{border-left-color:#2a78d6}
.se-n{font-size:2.2em;font-weight:700;line-height:1.1;font-variant-numeric:tabular-nums}
.se-of{font-size:.45em;font-weight:500;opacity:.7;margin-left:6px}
.se-l{font-size:.95em;margin-top:4px}
.se-cap{font-size:.85em;opacity:.75;margin:-.5em 0 1.5em}
.se-table{width:100%;border-collapse:collapse;font-size:.92em;margin:1em 0 1.5em}
.se-table th,.se-table td{padding:6px 10px;border-bottom:1px solid rgba(127,127,127,.3);text-align:right}
.se-table th:first-child,.se-table td:first-child{text-align:left}
.se-bars{display:grid;grid-template-columns:auto 1fr auto;gap:6px 10px;align-items:center;margin:1em 0 1.5em;font-size:.92em}
.se-bar{height:12px;border-radius:0 4px 4px 0;background:#2a78d6;min-width:2px}
</style>

**If your AI workflow is plan, build, tests pass, ship, you are shipping first drafts.**

I don't mean that as a dig at the models. I mean it literally. The model hands you a plan with total confidence, then hands you code with a green test run and the same total confidence, and both of them are first drafts. Nobody would ship a junior engineer's first draft without a review. We've somehow decided the frontier model gets a pass.

I didn't want to argue that from vibes, so I measured it. Over the last month I ran 83 stories through my AI SDLC process across three repositories. Opus 5.5 wrote almost every plan and implementation, which is the best model I can reasonably afford to run all day. Separate review agents, mostly on Sonnet, checked the work at every step. Here's what they found:

<div class="se-tiles">
  <div class="se-tile"><div class="se-n">80%<span class="se-of">53 / 66</span></div><div class="se-l">of plans needed rework before the build started</div></div>
  <div class="se-tile"><div class="se-n">48%<span class="se-of">31 / 64</span></div><div class="se-l">of implementations, every test passing, needed rework before the PR</div></div>
  <div class="se-tile"><div class="se-n">25%<span class="se-of">14 / 56</span></div><div class="se-l">of plans pointed the wrong way until a person overruled the model on a Decide call</div></div>
</div>

Four out of five plans. Half of the green builds. One plan in four heading in the wrong direction. That's the latest model I can afford, working inside a process built to make it succeed.

## Where this came from

I read Itamar Gilad's [Evidence-Guided](https://itamargilad.com/book-evidence-guided/), and it changed how I think about delivering software. The book is about product management, but the core move applies everywhere: stop deciding on opinion and confidence, and combine human judgement with evidence. Your confidence in an idea should match the evidence you have for it, not how good it sounds in the meeting.

Here's the thing: a frontier model is the most confident colleague you will ever work with. It never says "I think." It says "Done." Gilad's book taught me to be suspicious of confidence without evidence, and it turns out that's exactly the right instinct for AI-written software.

## We can't read our way out of this

This week Anthropic published how they [redesigned source control](https://www.anthropic.com/engineering/redesigning-source-control). They went from about 2,500 merged changes a day in May 2026 to over 30,000 a day in September, and Git couldn't keep up, so they built their own system (Scion). Their line that stuck with me: "the latent demand for merging code is practically infinite, and every bottleneck we remove immediately leads to a further increase in the amount of code we produce."

Think about what that means for code review. If the company that makes the model can't keep its version control on top of the volume, nobody is reading all those diffs. I'm certainly not reading all of mine. For most of my career, reading the PR *was* the quality process. That doesn't scale to this.

So the standard has to change. **The new standard is evidence that we met the plan and the story**, assembled by the process and checked by something other than the thing that wrote the code. I read the evidence. I don't read every line.

## Step 0: you need real tests first

I want to be blunt about this one: **you won't get acceleration from AI without thorough testing.** Tests are the only thing that steers the model. Without them, every one of the checks below has nothing to stand on, and "it compiles" becomes your definition of done.

And "we have tests" isn't the bar either. I wrote about this in [The Tests That Would Not Notice](/posts/2026/2026-10-10-the-tests-that-would-not-notice/). In this data set, 46 implementations ran mutation testing (1,055 mutants), and 8 of them had passing tests that wouldn't notice a broken line until new tests were written. Testing is step 0. Good testing is step 0 done right. Nothing in the AI SDLC works until it's there.

## The process, briefly

Every story goes through the same steps. The model writes, and a separate agent checks:

- **Story.** The author answers questions until the acceptance criteria are testable. A story check grades whether it's ready to plan.
- **Plan.** The model writes the plan. An adversarial plan review hunts for places a builder would build something the story didn't mean. A plan check grades whether an engineer who never saw the conversation could build it. A person rules on the Decide calls, the choices that belong to a person and not the model.
- **Build.** Tests first, then code, until the gauntlet (tests, lint, types, and whatever else the repo declares) is green. Then an adversarial code review tries to prove the diff wrong.
- **Evidence.** The model writes the evidence. An evidence-vs-plan check holds it against the plan's scenarios, and an evidence-vs-story check holds it against the story's acceptance criteria.
- **PR.** Only then does it go up for review.

The checks are cheap and fast. The median judge run takes under a minute.

## Using /plan without a review is a first draft

The plan is where I expected the model to shine. It reads the story, reads the code, and writes a clean, numbered plan. It looks done. It almost never is.

<div class="se-tiles">
  <div class="se-tile"><div class="se-n">80%<span class="se-of">53 / 66</span></div><div class="se-l">of plans needed rework before the build started</div></div>
  <div class="se-tile"><div class="se-n">69%<span class="se-of">45 / 65</span></div><div class="se-l">of plans the plan check sent back at least once</div></div>
  <div class="se-tile se-time"><div class="se-n">+9m<span class="se-of">of 18m in all</span></div><div class="se-l">added to planning, on average, to review the plan and fix the gaps it found</div></div>
</div>

The adversarial plan review raised gaps on nearly every plan it read. In the 31 plans that logged what happened to them, 124 gaps were fixed in the plan and 66 were declined with a written reason. That second number matters to me. The review is advice, not law, and the model pushes back when the review is wrong. But 124 real fixes across 31 plans is about four holes per plan that would otherwise have become code.

Planning roughly doubled in agent time. Nine extra minutes per plan is the cheapest fix in this whole process, because every hole caught in the plan is one that never gets built, tested, reviewed, and thrown away.

So when someone tells me they run `/plan` and go straight to build, my answer is that they're building from a first draft.

## The plan pointed the wrong way

If I could put one number from this whole exercise on a slide, it would come from this section.

The review agents check whether a plan is complete and buildable. They can't check whether it's heading in the right direction, because the direction lives in someone's head: the customer, the business, how the product is actually used. So the process makes the model stop and ask. Every choice that belongs to a person becomes a **Decide call**: the question, the options, and the model's recommended default. A person rules on each one before the plan is approved.

<div class="se-tiles">
  <div class="se-tile"><div class="se-n">181</div><div class="se-l">Decide calls across 56 plans, about three per plan</div></div>
  <div class="se-tile"><div class="se-n">10%<span class="se-of">17 / 165</span></div><div class="se-l">of rulings went against the model's recommended default</div></div>
  <div class="se-tile"><div class="se-n">25%<span class="se-of">14 / 56</span></div><div class="se-l">of plans with Decide calls changed direction because a person overruled the model</div></div>
</div>

Read that last tile again. One plan in four was confidently pointed somewhere it shouldn't go. The problem wasn't missing detail. The plan was wrong about what we needed. The review agents grade whether a plan is complete and buildable, and a plan can be perfectly buildable in the wrong direction.

The model's default was right 90% of the time, which is good. But the 10% it got wrong are the expensive ones. A missed edge case costs you a fix. A plan pointed the wrong way costs you the whole build, built correctly, tested, reviewed, and thrown away. If your process lets the model make those calls silently, you won't find out until the demo.

## Testing doesn't mean it's ready

Now the build. By the time the adversarial code review runs, the gauntlet is green. Every test the model wrote passes. By the usual definition, the work is done.

<div class="se-tiles">
  <div class="se-tile"><div class="se-n">48%<span class="se-of">31 / 64</span></div><div class="se-l">of implementations, every test passing, needed rework before the PR</div></div>
  <div class="se-tile"><div class="se-n">35</div><div class="se-l">blocking defects found in code whose tests all passed</div></div>
  <div class="se-tile"><div class="se-n">54%<span class="se-of">19 / 35</span></div><div class="se-l">of those defects a user would have seen</div></div>
  <div class="se-tile se-time"><div class="se-n">+12m<span class="se-of">of 38m in all</span></div><div class="se-l">added to the build, on average, to review the code and fix the defects it found</div></div>
</div>

Here's what kind of defects they were:

<div class="se-bars">
  <div>Missed edge case</div><div><div class="se-bar" style="width:100%"></div></div><div>10</div>
  <div>Wrong behavior</div><div><div class="se-bar" style="width:80%"></div></div><div>8</div>
  <div>False evidence</div><div><div class="se-bar" style="width:50%"></div></div><div>5</div>
  <div>Drift from the plan</div><div><div class="se-bar" style="width:40%"></div></div><div>4</div>
  <div>Security</div><div><div class="se-bar" style="width:30%"></div></div><div>3</div>
  <div>Test gap</div><div><div class="se-bar" style="width:20%"></div></div><div>2</div>
  <div>Other</div><div><div class="se-bar" style="width:10%"></div></div><div>3</div>
</div>

A few of them, in plain words:

- **Security (GH-120):** extra request fields could overwrite checked values like parent, project or summary, because the guards ran before the fields were merged in. Tests passed.
- **Error handling (GH-566):** if launching a child process failed in an unexpected way, the worker died silently and the child sat there waiting forever. Tests passed.
- **Test gap (GH-159):** a new test file was never wired into any test layer, so it never ran and proved nothing. Every test that *did* run passed, which is exactly the problem.

That last one is my favorite, in the way a scary movie is your favorite. Green was a lie, and nothing in the test run could have told me.

## Matching the plan isn't matching the story

This is the control I'm proudest of, and the one I'd push hardest on any team doing AI-driven delivery.

At sign-off the model writes the evidence: here's each requirement, here's the test or run that proves it. The evidence-vs-plan check holds that evidence against the plan. The evidence-vs-story check holds the same evidence against the story's acceptance criteria. Most AI workflows stop at the first one, if they have it at all. The plan is the model's own document, so of course the code matches it.

<div class="se-tiles">
  <div class="se-tile"><div class="se-n">31%<span class="se-of">14 / 45</span></div><div class="se-l">of implementations held at sign-off by the evidence-vs-story check: a story requirement had no proof</div></div>
  <div class="se-tile"><div class="se-n">25%<span class="se-of">4 / 16</span></div><div class="se-l">of implementations passed the evidence-vs-plan check and failed the evidence-vs-story check in the same round</div></div>
</div>

That second tile is the scary one. The plan was built. The build succeeded. Every test passed. The evidence-vs-plan check said ready. And the evidence-vs-story check said no, because the plan never covered everything the story asked for.

My clearest example is GH-566. The story asked for something to work while a pod was running. The tests proved it worked while an agent was running *in the same process*. Plan matched, tests green, evidence complete, and we'd built the wrong thing. Only the gate that went back to the original story caught it.

(16 is a small base. I added the evidence-vs-plan check to the process later, so only 16 implementations went through both.)

## What it costs

None of this is free, so here's the bill:

<div class="se-tiles">
  <div class="se-tile se-time"><div class="se-n">$98</div><div class="se-l">for every review check across all 83 stories, about $0.40 per blocking issue sent back</div></div>
  <div class="se-tile se-time"><div class="se-n">6%</div><div class="se-l">of the total cost of the work went to review</div></div>
</div>

<table class="se-table">
<thead><tr><th>Check</th><th>Median run</th><th>Cost</th><th>Needed rework</th></tr></thead>
<tbody>
<tr><td>Story check</td><td>0.8 min</td><td>$18.12</td><td>15 of 55 stories (27%)</td></tr>
<tr><td>Adversarial plan review</td><td>0.2 min</td><td>$10.18</td><td>30 of 31 plans (97%)</td></tr>
<tr><td>Plan check</td><td>0.3 min</td><td>$18.08</td><td>45 of 65 plans (69%)</td></tr>
<tr><td>Adversarial code review</td><td>0.7 min</td><td>$30.94</td><td>18 of 60 implementations (30%)</td></tr>
<tr><td>Evidence vs plan</td><td>0.4 min</td><td>$7.22</td><td>9 of 32 implementations (28%)</td></tr>
<tr><td>Evidence vs story</td><td>0.4 min</td><td>$13.73</td><td>14 of 45 implementations (31%)</td></tr>
</tbody>
</table>

The judges run on Sonnet, which is about half the per-token price of the Opus model doing the building. Review took about 10% of the agent's working time and 6% of the cost. Forty cents to catch a defect before a PR is the best deal in my whole workflow.

## What still got through

After all of that, I went back through every issue and pull request filed after these stories merged, looking for bugs that traced back to one of them.

<div class="se-tiles">
  <div class="se-tile"><div class="se-n">2%<span class="se-of">2 / 83</span></div><div class="se-l">of stories had a defect reported after merge</div></div>
</div>

One was a merge that duplicated an import another story had already added. The other (GH-120) had two bugs in a Jira adapter that a later issue reported without naming the story, so I had to trace them back through git. Not zero. But I'll take 2 out of 83.

## People still matter

The machines found most of the volume. They checked every plan, every diff, and every piece of evidence, and they're cheap and fast enough to do it on every story. But the 17 Decide calls where a person overruled the model are the ones no agent could have caught, because the right answer wasn't in the code or the story. It was in someone's head. Those are the calls about what we're building and why, and I don't want a model making them. People approve, agents check.

## What this doesn't prove

- **It's still a small (but significant) sample.** 83 stories is enough to see a pattern, not enough to call it a law.
- **Escapes only count what someone reported.** A bug nobody filed an issue for isn't in my 2%.
- **Some reviews never block.** The adversarial plan review is advice, and 66 of its gaps were declined. I counted only the ones that changed the plan.
- **Timing is the agent's working time,** with time spent waiting on me left out. It's an estimate built from the logs, not a stopwatch.

## The new definition of done

Here's where I've landed. The model isn't the problem. It's very good, and it gets better every few months. The problem is treating its first output as its final output because it arrived confident and green.

Done used to mean "the tests pass and someone read the diff." With this much code coming at us, done now means **the evidence shows we built what the plan said, and the plan covers what the story asked**, checked by something other than the thing that wrote it. And none of it works unless the tests underneath are real.

If you want help building this kind of process for your team, that's what we do at [Pinnacle Solutions Group](https://pinnsg.com/).

_Have your own numbers on how often AI output is right the first time? I'd love to compare notes. Hit me up on [GitHub](https://github.com/drmikecrowe) or wherever you found this post._
