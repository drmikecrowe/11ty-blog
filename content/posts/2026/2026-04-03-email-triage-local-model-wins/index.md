---
layout: post
title: "I Benchmarked 10 AI Models for Email Triage — A Free Local Model Won"
description: "I ran 275+ emails through Claude, Gemini, and 7 open-source models to find the best classifier for automated email triage. The winner surprised me."
date: 2026-04-03T10:00:00.000Z
permalink: /posts/2026-04-03-email-triage-local-model-wins/
draft: false
categories:
    - tech
tags:
    - ai
    - email
    - llm
    - benchmark
    - local-ai
    - open-source
author: Mike Crowe
seo:
    title: "I Benchmarked 10 AI Models for Email Triage — A Free Local Model Won"
    description: "275+ emails, 10 models, one winner: how a local 7B model beat Claude, Gemini, and open-source heavyweights at email classification."
    image: images/featured.png
featured_image: images/featured.png
excerpt: "I built an email triage system that runs incoming mail through AI classifiers, then benchmarked 10 models head-to-head. The local model running on my home server classified 276 emails with 93% average confidence — for free. Here's what I learned."
---

_This post was written with AI assistance (Claude) for structure and formatting. The analysis, opinions, and surprise at the results are entirely my own._

---

I built an email triage system that reads incoming mail and classifies it into categories: BULK, ACTION, BILLING, MONITOR, JUNK, and PERSONAL. Each email gets a category, a confidence score, and a one-line reason. The system then labels or files the email accordingly.

> **I expected an expensive cloud model to win.**

The architecture is straightforward — an orchestrator fetches unread emails from Gmail and ProtonMail, sends each one to a classifier, and dispatches the result:

```
Orchestrator
    ├── Gmail Adapter        fetch / label / mark-read
    ├── ProtonMail Adapter   fetch / move / mark-read
    ├── Classifier           classify(email) → {category, confidence, reason}
    └── Action Dispatcher    routes → correct adapter action
```

The classifier is swappable — any model that accepts a system prompt and returns JSON works. So naturally, I wondered: **which model is best?**

## The Benchmark Setup

I added a `--profile` flag that runs each email through _every_ configured classifier in parallel, records the results, and produces a comparison report. No inbox changes — pure benchmarking.

The models I tested, grouped by where they run:

**Cloud APIs:**

- **Claude 3 Haiku** (Anthropic) — the original, designed as the production default
- **Gemini 2.5 Flash** (Google) — Anthropic's main competitor in the "fast and cheap" tier

**Local:**

- **Qwen 2.5 Coder 7B** — running on my home server via [Ollama](https://ollama.com/)

**Open-source via [Synthetic](https://synthetic.new):**

- **GLM-4.7-Flash** (Zhipu/Z.ai) — I use Z.ai regularly, expected this to be a contender
- **Kimi-K2-Instruct** (Moonshot)
- **MiniMax-M2.1** (MiniMax)
- **Llama-3.3-70B** (Meta)
- **DeepSeek-V3.2** (DeepSeek)
- **Qwen-3.5-397B** (Qwen)
- **GLM-5** (Zhipu/Z.ai)

Each model received the same system prompt (built from my `config.yaml` category definitions) and the same email content. The only variable was the model.

## The Results

After running 275+ emails through the top three models and ~100 through each Synthetic model, here's what the data looked like:

| Model                         | Emails | Avg Conf | Min Conf | Avg Latency | Est. Cost |
| ----------------------------- | ------ | -------- | -------- | ----------- | --------- |
| **Qwen 2.5 Coder 7B** (local) | 276    | 0.93     | 0.80     | 1,096ms     | **Free**  |
| Gemini 2.5 Flash              | 275    | 0.92     | 0.80     | 882ms       | $0.048    |
| Claude 3 Haiku                | 275    | 0.90     | 0.80     | 892ms       | $0.085    |
| Kimi-K2-Instruct              | 101    | 0.93     | 0.90     | 2,138ms     | $0.121    |
| MiniMax-M2.1                  | 100    | 0.94     | 0.75     | 2,465ms     | $0.075    |
| Llama-3.3-70B                 | 99     | 0.88     | 0.80     | 2,071ms     | $0.089    |
| GLM-4.7-Flash                 | 98     | 0.96     | 0.90     | 5,427ms     | $0.055    |
| DeepSeek-V3.2                 | 56     | 0.86     | 0.70     | 10,659ms    | $0.109    |
| GLM-5                         | 53     | 0.93     | 0.85     | 7,676ms     | $0.174    |
| Qwen-3.5-397B                 | 51     | 0.93     | 0.85     | 27,994ms    | $0.360    |

### The Winner: A Free Local Model

Yeah, I was surprised too.

**Qwen 2.5 Coder 7B** — a 7-billion parameter model running on my home server — classified 276 emails with **93% average confidence** and never dropped below 80%. That's higher than Claude Haiku (0.90) and essentially tied with Gemini (0.92).

At 1.1 seconds average latency, it's only 200ms slower than the cloud APIs. And the cost? Zero. It's running on hardware I already own.

This isn't some beefy server, either. It's an **NVIDIA GeForce RTX 3060** — a mid-range GPU from 2021 with 12GB of GDDR6 VRAM, 3,584 CUDA cores, and a 192-bit memory bus. You can pick one up used for under $250. It's the kind of card a gamer upgrades _from_, not _to_. And it's running a 7B model at inference speeds that compete with cloud APIs.

Here's why this matters for email triage specifically: this is a **structured output task**. The model doesn't need to reason deeply — it needs to read an email, match it against clear category definitions, and output JSON. A focused 7B model can do this just as well as (or better than) a general-purpose 200B+ model.

### What About Gemini?

Gemini 2.5 Flash was the best cloud option — fastest (882ms), cheapest ($0.048 for 275 emails), and solid confidence (0.92). If I didn't have a local server, Gemini would be my pick without hesitation.

Claude 3 Haiku was fine but offered no advantage. Same speed as Gemini, lower confidence, nearly twice the cost. For this specific task, there's no reason to choose Haiku over Gemini.

### Synthetic: Open-Source Models Without the Infrastructure

[Synthetic](https://synthetic.new) deserves a shoutout here. They're a US-based company that provides hosted open-source models with security guarantees — no sending your data to unknown endpoints. Their OpenAI-compatible API meant I just changed the `base_url` in my config and had instant access to models from DeepSeek, Qwen, Meta, Moonshot, MiniMax, and Zhipu. No spinning up GPUs, no managing infrastructure, no worrying about where my data goes.

I did hit rate limits during the benchmark, which is honestly a sign of their popularity — there are a lot of us eager to test these models. The team has been responsive and the service is clearly scaling to meet demand. For anyone who wants to benchmark open-source models against each other without building their own inference pipeline, Synthetic is the easiest on-ramp I've found.

### The GLM-4.7-Flash Disappointment

This one stung. I use [Z.ai](https://z.ai) regularly and their GLM models are solid for general chat. I expected GLM-4.7-Flash to be a strong contender.

It wasn't terrible — 0.96 average confidence is the highest of any model. But it **burned 91,568 output tokens** across 98 emails. For comparison, Gemini used 12,803 output tokens for 275 emails. GLM-4.7-Flash used **7x more tokens per email** than Gemini.

Why? It's reasoning before answering. Despite the system prompt explicitly saying "Respond ONLY with a valid JSON object — no thinking, no analysis, no explanation," the model would spend hundreds of tokens analyzing the email before producing the classification. More tokens means more cost and more latency (5.4 seconds average vs Gemini's 882ms).

That high confidence might also be **overconfidence** — when a model reasons extensively, it tends to become more certain regardless of whether the reasoning is correct. I'd want to verify accuracy before trusting that 0.96 number.

### The Models I Dropped

Three models didn't make the cut and I disabled them mid-benchmark:

- **Qwen-3.5-397B**: 28 seconds average latency. One email took 107 seconds. It's a reasoning model that thinks before it answers, and for structured output tasks, that's pure waste. At $0.36 for 51 emails, it was the most expensive model tested.
- **DeepSeek-V3.2**: 10.6 seconds average and returned 0-confidence classifications twice. Slow and unreliable — a bad combination.
- **GLM-5**: 7.7 seconds, expensive ($0.17 for 53 emails), and no better at the actual task than models that cost 1/3 the price.

## What I Learned

Here are the things that surprised me:

- **Task fit matters more than model size.** Email classification is pattern matching against clear definitions. A focused 7B model can match or beat a 397B model at this task because the extra reasoning capacity goes unused.
- **Confidence isn't accuracy.** GLM-4.7-Flash reported 0.96 average confidence but burned 7x the tokens of Gemini at 0.92. More tokens ≠ more correct. I need to manually verify a sample to know which model is actually right.
- **Local models are viable for production.** I went into this expecting to pay for a cloud API. I came out running a free local model with better confidence than Haiku and latency that's perfectly acceptable for email (this isn't real-time chat — an extra 200ms per email is nothing).
- **"Thinking" models are wrong for structured output.** Qwen-3.5, DeepSeek, and GLM-5 all burned tokens on reasoning before producing JSON. For tasks with clear definitions and a constrained output format, you want a model that answers directly — not one that thinks out loud.

## What I'm Running Now

My `config.yaml` currently looks like this:

```yaml
classifier:
    backend: ollama
    ollama:
        host: http://192.168.4.5:11434
        model: qwen2.5-coder:7b
```

Free, fast, accurate enough, and running on hardware I already have. I keep Gemini configured as a fallback and Synthetic for occasional benchmarking, but day-to-day the local model handles everything.

The full source code for the email triage system can be available if there is interest. Seems specific to me tho, so reach out if you want a copy.

_Have your own experience benchmarking LLMs for specific tasks? Found a local model that punches above its weight? Hit me up on [GitHub](https://github.com/drmikecrowe) or wherever you found this post._
