---
layout: post
title: People Approve, Agents Check
description: "Where AI actually belongs in the software delivery lifecycle: at the two boundaries where projects fail, as a checker and never an approver."
date: 2026-08-24T09:00:00.000Z
draft: false
categories:
  - pinnacle
  - tech
tags:
  - ai
  - engineering-leadership
  - sdlc
  - code-review
author: Mike Crowe
seo:
  title: People Approve, Agents Check
  description: "Where AI actually belongs in the software delivery lifecycle: at the two boundaries where projects fail, as a checker and never an approver."
  image: images/featured.png
featured_image: images/featured.png
excerpt: Everyone is racing to find out how much of the work the AI can do. We asked where delivery actually breaks instead, put an agent at each of those two places, and came out convinced you need better engineers than before, not fewer.
---
_This post was written with AI assistance (Claude) for structure and formatting. The design, opinions, and specifics are entirely my own._

**I think the industry is measuring the wrong thing, and I think the leaderboard is making software worse.**

Every vendor pitch I've sat through in the last year answers the same question: how much of the work can the AI do? Percentage of code generated. Tickets closed without a human. Autonomy tiers, like a self-driving car. That's a fine question if you're selling a model, but it's the wrong question if you're responsible for an engineering organization, because it smuggles in two assumptions. The first is that the bottleneck is typing. The second, which nobody says out loud in the meeting but everybody hears, is that a successful AI rollout ends with fewer engineers.

Both are wrong, and the second one is expensively wrong.

## Where this came from

This started with adversarial code review. I began having an independent reviewer, one carrying none of my assumptions, try to break my finished work instead of blessing it. Its entire brief was to find the input that makes the code fail. That alone was worth the tokens.

I'll admit why I needed it. I had drifted into trusting the high-end models. When Opus hands you code, it hands it to you with total confidence: no hedging, no "you may want to check this," just a clean explanation of why it did what it did. I got comfortable, and you can probably see where this is going. When I started pointing a second model at that output with instructions to break it, I was genuinely shocked at the gap between how certain the first model sounded and how well the code actually held up. The confidence is a constant. The quality is not. Nothing has made me more careful than watching a model I trust get taken apart by a second model with no stake in being right.

Then I moved the whole thing upstream. I was already writing specs first, so before any code existed I pointed the same adversarial treatment at the spec itself: find the requirement that can't be tested, find the two bullets that contradict each other, find the thing I assumed and never wrote down.

That turned out to be even more valuable. My specs were full of holes I could not see, because I was the one who put them there, and every hole caught at spec time was a hole that never became code. Reviewing the output catches mistakes; reviewing the intent prevents them. The tokens I spent arguing with a machine about what I actually meant were the cheapest tokens I spent all year.

That's the part I couldn't stop thinking about. If an adversarial loop does that for one engineer working alone, what does it do for a team? So we started building it into a real process at Pinnacle Solutions Group, the consulting firm I'm part of, and we're genuinely excited about where it's going. This is us thinking out loud about where AI belongs in software delivery, and I'd rather share it while it's still being shaped than wait until it's a polished case study.

Two disclaimers. Helping engineering orgs put this in place is work Pinnacle Solutions Group sells, so read the whole thing with that in mind. And it's running on a live client engagement right now, being developed with them and fitted to how they already work. I'm describing a process I believe in and am actively proving, not results I can hand you. When I get to what it costs, I'll be specific about what I don't yet know.

## Delivery breaks at the edges, not in the middle

Think back through the projects that went badly for stupid reasons, not the ones with genuinely hard technical problems. Anecdotally, across the ones I've watched up close, nearly all of them broke at one of two boundaries.

The first is the handoff from product to engineering. Somebody writes down what they want, and what they write down is incomplete: acceptance criteria you can't actually test, an assumption nobody stated, two requirements that quietly contradict each other. Nobody notices at write time. Somebody notices on day four of the sprint, in a meeting, after the money is already spent.

The second is the handoff from "the work is done" to "the work is proven." A change gets reviewed by looking at code. Looking at code answers a question (is this reasonable code?) that nobody actually needed answered. The question is whether this change does what product asked for, and how we know.

The middle, where the typing happens, is mostly fine. That's where every vendor is aiming.

So we aimed somewhere else, and not out of contrarianism. The speedup in the middle is real, but it's a commodity: every tool on the market delivers it, and your team collects it no matter whose logo is on the invoice. The failures at the edges cost sprints, not minutes, and nobody was selling anything there.

We put an AI agent at each of those two boundaries, and we gave it a job description with a hard limit on it: **people approve, agents check.** An agent in this design never approves anything, never merges anything, and never decides what gets built. It reads, it tests, and it reports, and the verdict belongs to a person every time.

Underneath, there's nothing exotic here. It's spec-driven development feeding test-driven development, wrapped in a workflow that makes both of them non-optional.

None of the individual pieces is new. Planting a deliberate fault to prove the tests would catch it is mutation testing, an idea from the 1970s. Coverage on changed lines is standard CI configuration. Requirements reviews, design reviews, spec-first, test-first: all decades old. What I'd defend as new is where they sit. When AI writes most of the code, plausible work arrives faster than anyone can judge it, and these old disciplines are how judgment keeps up.

## Gate 1: AI that protects human judgment

The first gate sits between product and engineering. It runs on a story that's headed into refinement, and it answers one question: is this specified well enough to *be* refined?

An agent reads the story and puts it to this test: could an engineer prove, from what is written here, that the intent was met? That question does a lot of work. It forces every acceptance criterion to be verifiable rather than aspirational. It surfaces the assumption sitting under the third bullet that nobody wrote down. It catches the place where criterion two and criterion five can't both be true.

This is aimed squarely at helping the people who write those stories. Product and marketing are often not technical, and they are being asked to express intent precisely enough for engineers to manifest it. That's a hard thing to do with no feedback loop. Today the feedback arrives four days into the sprint, in a meeting, in front of people. This gate gives them the same feedback in writing, in minutes, from a machine that doesn't sigh.

A story that passes moves on to refinement. That's not an agent approving the work; it's an agent confirming that product has finished product's job, so engineering can start engineering's job. Nobody's clear, well-specified ticket sits in a queue waiting for a human to rubber-stamp what an agent already confirmed. What gets built is still decided by people in refinement, downstream of this gate, exactly as it was before.

A story that fails bounces back to whoever wrote it, with written findings. And not vague ones like "this needs work," but specific ones: *criterion three has no observable outcome, here is what's missing; criteria one and four conflict under this condition; this assumes the user is already authenticated and the story never says so.* Bad tickets bounce before they cost a sprint, and they bounce with a document instead of a meeting.

The part that matters most: the gate does not fill in the gaps. It finds them and hands them back.

The industry instinct is the opposite. Vague requirement? Let the model guess. It'll produce something plausible, and plausible is very close to correct, and the demo will go great. But deciding what the business actually wants is not a gap-filling exercise. It's the highest-judgment work in the building, done by the people with the context and the scars. Automating a plausible guess over the top of that doesn't remove the work, it just hides it until it's expensive.

So we deliberately preserve the human conversation at exactly the point where the human is the value. What we change is the price and the timing: earlier, cheaper, in writing, before anyone has spent a sprint on the wrong thing.

## Between the gates: building a specification worth implementing

This is where spec-driven development actually lives, and it's the part I had wrong in my own head until recently. I'd lumped it all into "refinement," which is one word doing two jobs.

Refinement answers *is this item ready*: is it clear, is it testable, roughly how big, in what order. That's product's item, and Gate 1 is what protects it. Building the **Implementation Plan** answers a different question, *how will we build this*, and it belongs to the team. Those are two artifacts with two owners, and collapsing them is how you end up with a product owner refereeing a design argument.

### Pre-assembling the context

The moment a story clears Gate 1, an agent goes and reads the codebase against it and assembles a context pack: which subsystems this touches, the patterns already in use there, the tests that cover that ground today, the prior art from the last time somebody did something similar.

This is small and it's cheap and I think it's one of the highest-leverage pieces in the whole process, because it gets produced while nobody is waiting on it. In grooming, the team walks in already knowing what the story touches instead of speculating out loud, which is most of what sizing actually needs, without paying for a full design on every item in the backlog. Later, it's the input the planning agent needs, already gathered.

### Then the plan, when someone picks up the work

An engineer takes the story. An agent drafts the Implementation Plan from the approved Requirements and the context pack: approach, the tests that will prove each acceptance criterion, risks, and how we back it out. A second agent, with none of the first one's context, attacks that draft. The engineer resolves the findings, owns the result, and signs it. Then code gets written.

That agent draft is not a shortcut around the engineer. It's a better starting point than the engineer would produce alone under sprint pressure, because it actually read forty files instead of pattern-matching off four. What it cannot do is decide whether this approach is right for where the system is going, whether the rollback is real, or whether the risk list is honest. That's the signature.

And when the plan reveals the estimate was wrong, that's the process working. You find out on day one, in writing, with a reason. A plan can bounce a story back the same way Gate 1 does.

### Why the agent may fill this gap and not the other one

Gate 1 refuses to fill gaps in the Requirements. Here an agent drafts a whole specification. That looks inconsistent. The difference is the cost of a wrong guess.

A wrong guess about product intent is unrecoverable. Nothing downstream can detect it. Every test passes, the evidence is clean, and you shipped the wrong thing correctly. A wrong guess about technical approach is checkable. The Requirements check it, an adversarial reviewer checks it, and so does what we call **the gauntlet**: an automated review that holds the implementation to a standard while it's built, with every changed line tested, the tests proven able to catch a deliberately planted fault, and every check the merge gate will run passing before the work is called done. So does the engineer who has to put their name on it. The blast radius is different, so the rule is different.

## Gate 2: AI that forces human understanding

The gauntlet ends with output: check results, coverage of the changed lines, planted faults caught. That output says the code was built to standard. It does not say the right thing was built, and treating those as the same claim is exactly the conflation this gate exists to prevent.

That's what the **Evidence** document is for. Its shape is simple: each acceptance criterion from the Requirements, how the change satisfies it, and how that was verified. Tests mapped to specific criteria. The gauntlet's results. Screenshots where the change touches something a person looks at. It isn't written at the end as paperwork; it accumulates as the work is built. Evidence is the proof that the acceptance criteria were met, assembled from what the gauntlet produced.

Gate 2 is the formal check on that proof. An agent validates the Evidence against the Requirements before the change is ever put up for review: does what the gauntlet proved actually prove what product asked for? Then the engineer must read the Evidence against the Requirements and personally decide whether the work meets the intent. The question isn't whether the tests are green; it's whether the thing does what was wanted. The AI assembles the proof, and the engineer renders the verdict and signs their name to it.

So a piece of work carries three named documents by the time it ships. **Requirements** says what and how we'll know. **Implementation Plan** says how, before the build. **Evidence** proves it. Each one carries a human approval, and each one was checked by an agent first.

But a signature is cheap. Nothing about signing a document stops an engineer from skimming it and signing anyway. If all this gate did was swap "skim a green build and merge" for "skim an Evidence doc and sign," I'd have added ceremony and called it rigor. A process that only asks for a signature gets signatures.

That's why the signature isn't the mechanism. The next section is.

## The forcing function: every change becomes knowledge transfer

The engineer who signed the verdict then uses that same Evidence to walk reviewers and QA through the change, out loud, in front of colleagues. It's not a diff review, it's a narrative: here's what product asked for, here's how this satisfies it, here's how we know.

That's the part you cannot fake. You can sign a document you didn't read, but you cannot stand in front of two colleagues and explain a change you don't understand, and everyone in the room knows it within about ninety seconds. The Evidence document isn't the enforcement. It's the script for a conversation that *is* the enforcement.

"Out loud" flexes with the team. For a distributed group that means a live call or a recorded walkthrough rather than a conference room, and the rule holds either way: the engineer explains the change to people who can ask questions.

This is the thing every engineering leader is quietly afraid of: an engineer generating a change they don't understand, skimming a green build, and shipping it. I can't make that structurally impossible; anyone who tells you they can is selling. What I can do is put the moment of "explain this to your peers" between the AI's output and production, and make it the normal cost of shipping. Not understanding your own change stops being invisible.

And then think about what that does over a quarter. Every single change becomes a teaching moment, delivered by someone who is required to understand it well enough to defend it. The team learns how the system is changing, update by update, from a person rather than from a diff nobody reads. Institutional knowledge stops being a thing that lives in three people's heads and starts being a thing the process produces as a byproduct.

This is the same set of models everyone else is using, aimed at a different problem. The difference isn't the tooling; it's where the human sits, and what the process makes them do when they get there.

## Your engineers matter more now, not less

Nothing in this design is aimed at needing fewer engineers. It's aimed at raising the quality of what your engineers ship when they work with AI. Those are different goals, and they lead to opposite decisions at nearly every fork.

A model will produce something plausible for almost any request. Plausible is the dangerous part: it compiles, reads well in review, passes the tests it was written alongside, and quietly does the wrong thing. The only reliable defense is a person who knows the system, knows what was actually asked for, and is equipped to tell the difference. No model removes that need, because judging whether the AI did what was intended is itself a judgment about intent.

So the volume of code goes up and the value of engineering judgment goes up with it. Every gate exists to put a competent engineer in front of the right question at the right moment, with the evidence in hand to answer it. Gate 1 hands them a request worth building. Gate 2 hands them the proof and makes them rule on it. The walkthrough keeps the whole team sharp enough to keep doing that as the system grows.

An org that cuts engineers to pay for AI ends up with more code and less capacity to judge it. That is the worst version of this. If your team gets faster, the win is that they take on work they couldn't before, not that there are fewer of them.

## What this costs

This is the part vendors skip, so here it is up front: this process is slower than what the market currently expects from AI. Gate 1 adds a loop before refinement. The Implementation Plan adds a draft and an adversarial pass before code. Tests written from acceptance criteria are slower to write than tests written from finished code. Evidence takes real effort to produce, and the walkthrough takes real time from more than one person.

The walkthrough is the line I expect the most pushback on, and the pushback is fair: multiple colleagues per change, out loud, does not scale like a CI job. I'm not going to argue it away, because it's the deliberate purchase. Quality of what ships and a team that understands what shipped are the two things this whole design exists to buy, and the walkthrough is where both get paid for. How deep it goes, and for which changes, is one of the things the current engagement is calibrating.

It costs more tokens, too. Every adversarial pass is a second model reading work the first model already did. The context pack is a full codebase read before anyone has picked up the story. Attacking a spec, then attacking an implementation plan, then validating Evidence against the Requirements: none of that is free, and it is spend you would not have if you simply asked a model for the code and merged what came back.

I think it's the best money in the budget. I called those the cheapest tokens I spent all year and I meant it literally: you are buying rework you never have to do, at a price you can see up front. But it's a real line item, it's larger than a single-agent workflow, and a client should agree to it going in rather than discover it on the first invoice. Spend ceilings and usage alerts go in on day one for exactly that reason. Adoption shouldn't come with an open tab.

The middle is genuinely faster. An engineer with AI leverage and a clear spec outruns the same engineer without it, and it isn't close. But that gain is smaller than the number on the slide, because we are deliberately spending part of it on tests and proof.

That said, the paragraphs above make this sound slower than it is. Most of what this process standardizes should already be standard operating procedure in most organizations: tests tied to the requirements, review that checks intent, proof that the work does what was asked. I'm not piling new work on top of delivery. What I'm mostly doing is refusing to let AI's speed become the excuse to skip work that was always owed. The velocity this trims is the false kind: the perceived gains of merging plausible code fast and paying it back later as rework.

So what I'm claiming is confidence. Fewer sprints spent building the wrong thing, fewer changes that pass review and fail intent, and a team that understands what it shipped. If the number you're optimizing is lines per day, I'm the wrong call. If it's the ratio of shipped work that actually did what was asked, this is the trade I'd make.

## What holds it up

The gates only work if what they're checking is real. Two supporting pieces do that work.

- **The gauntlet.** Tests come from the acceptance criteria, not from the finished code, so they verify what was asked for instead of confirming whatever got built. The gauntlet's job is to prove that testing is real: every changed line covered, and planted faults confirming the suite would catch a genuine mistake. A suite that can't catch a deliberate mistake wasn't going to catch an accidental one.
- **Adversarial review.** An independent AI reviewer, carrying none of the author's assumptions, is briefed to break the work: find the input that makes it fail. Confirmed findings get fixed and re-checked. This is where the whole thing started for me, and it's still the piece I trust most. Self-review doesn't work. The author always finds a reason the work is right. One caveat: two frontier models share training data and failure modes, so this independence is a design goal with limits. The reviewer has none of the author's context, and that catches a lot, but it can still share the author's blind spots.

## Where this doesn't fit

This process assumes you know what you're building. Exploratory work, spikes, R&D where the spec is the thing you're trying to discover: gating that behind Requirements is backwards, and we don't try. The honest artifact there is a timebox and a writeup, and the process starts after.

It also assumes changes worth the ceremony. A dependency bump or a typo fix doesn't need an Implementation Plan and a walkthrough, and a process that pretends it does will get routed around within a month. Part of what we're calibrating with the current client is exactly that tiering: which changes get the full treatment, which get the gauntlet alone, and who decides.

And a three-person team probably shouldn't run this as written. The walkthrough is priced for teams big enough that knowledge silos are a real risk. Below that size everyone already knows every change, and the gates worth keeping are the two adversarial reviews.

## How it lands in your org

We customize the gates to your workflow rather than the other way around. The gates hook onto the states your team already has. No new methodology, nothing replaced, no migration.

And it's built to end. We lead the first run, coach the second, and step back to review only for the third. If your team still needs us on run four, we designed it wrong.

## What to ask the next vendor, including us

If you're evaluating AI in your delivery process, the autonomy percentage on the slide tells you almost nothing about whether your delivery will improve. Three better questions, and I'd expect to answer all of them myself:

**Where does the human judgment live, and what protects it?** If the answer is that the AI fills in whatever product left vague, you're buying a machine that converts unclear thinking into shipped code at high speed.

**How do you prove the work meets the intent?** If the answer is "code review," ask what question code review actually answers. Then ask who on the team will be able to explain the change six months from now.

**What does this slow down?** Any honest process has a cost. A vendor who reports only acceleration is either not measuring or not telling you.

And ask what the vendor thinks happens to your engineers. If the pitch is a headcount line, walk. We didn't get here by asking how much of the job the AI could take. We asked where delivery breaks, and the answer was the same two places it's always broken. The machines are genuinely useful there. They just aren't in charge there, and they need better engineers around them than they did before, not fewer.

_This is what I think about most days right now. We're building it with a client as I write this, shaping it to their process rather than handing them ours, and the parts that survive contact with a real team are the parts worth keeping. If you're wrestling with the same question of where AI belongs in your delivery process, and how you'd prove it worked, I'd genuinely like to hear how you're approaching it, whether or not you ever talk to us. Find me on [GitHub](https://github.com/drmikecrowe) or wherever you found this post._
