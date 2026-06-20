---
layout: post
title: "Code Container: Isolating AI Coding Harnesses Without Losing Your Mind"
description: "A daily-driver for running Claude Code, OpenCode, Codex, and Gemini in isolated environments — with seamless auth, egress firewalls, and zero re-authentication friction."
date: 2026-03-20T10:00:00.000Z
permalink: /posts/2026/2026-03-20-code-container-isolating-ai-harnesses/
draft: false
categories:
    - tech
tags:
    - ai
    - containers
    - security
    - claude-code
    - podman
    - developer-tools
author: Mike Crowe
seo:
    title: "Code Container: Isolating AI Coding Harnesses Without Losing Your Mind"
    description: "A power-user daily-driver for running Claude Code, OpenCode, Codex, and Gemini in rootless Podman containers with seamless auth, egress firewalls, and multi-harness support."
    image: images/featured.png
featured_image: images/featured.png
excerpt: "I let AI harnesses run with full permissions on my host machine for months. Then I found a brilliant container project, forked it, and turned it into something I actually use every day — with seamless auth, an egress firewall, and support for every harness I throw at it."
---

_This post was written with AI assistance (Claude) for structure and formatting. The ideas, paranoia, and late-night container debugging are my own._

---

Let me start with a confession:

> **I've been running AI coding agents with full, unrestricted access to my host machine.**

Claude Code in YOLO mode. OpenCode. Codex. All of them, just loose on my filesystem with `--dangerously-skip-permissions` because — let's be honest — the permission prompts break flow. You're in the zone, the agent is cranking through a refactor, and then it stops to ask "can I read this file?" for the fifteenth time.

So you skip permissions and try not to think about what an LLM with shell access could theoretically do to your `~/.ssh` directory.

I needed isolation. But I also needed it to not suck.

---

## The Landscape: Three Projects, Three Threat Models

Before I get into what I built, some context. This isn't the only container solution for AI coding, and it's not trying to be. There are three projects targeting fundamentally different use cases:

|                  | Code Container (this project)   | [Anthropic's devcontainer](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo) | [Trail of Bits](https://github.com/trailofbits/claude-code-devcontainer) |
| ---------------- | ------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **Use case**     | Power-user daily driver         | VS Code team environments                                                                                   | Security auditing untrusted code                                         |
| **Threat model** | Contain the AI, not the repo    | Consistent team setup                                                                                       | Malicious repos / adversarial input                                      |
| **Harnesses**    | Claude, OpenCode, Codex, Gemini | Claude                                                                                                      | Claude                                                                   |

**Anthropic's official devcontainer** is the "corporate IT" answer — a VS Code-first reference implementation for teams wanting consistent dev environments.

**[Trail of Bits](https://github.com/trailofbits/claude-code-devcontainer)** built theirs specifically for security auditors reviewing untrusted code. Their threat model explicitly includes malicious repos trying to escape the container. If you're doing security work on code you don't trust, use theirs.

**This project** is for someone who wants YOLO mode across multiple AI harnesses without the friction of re-authentication or tool switching. You trust your own code. You don't fully trust what the AI might do with network access.

---

## The Starting Point: kevinMEH/code-container

Here's the thing: I didn't build this from scratch, and I want to be very clear about that. [Kevin](https://github.com/kevinMEH) built [code-container](https://github.com/kevinMEH/code-container) — a clean, well-thought-out project that solves the core problem elegantly. Mount your project into a container, run your AI harness inside it, and your host stays clean. The fundamentals were already there:

- Container-per-project isolation
- Shared caches for npm/pip so you're not re-downloading the internet every session
- A simple CLI interface (`container` to enter, `exit` to leave)
- Session persistence — stop a container, come back later, everything's still there

This is genuinely great work. The architecture is sound, the script is readable, and the project solves a real problem that a lot of people doing AI-assisted development are just ignoring.

Kevin has since migrated the upstream project to JavaScript, distributed via npm (`npx code-container`). That's a perfectly valid distribution strategy, but I chose to stay in bash. Everything this tool does is orchestrate `podman`/`docker` CLI commands, manage mounts, and set up iptables rules — that's shell scripting's home turf. A ~560-line bash script with zero runtime dependencies felt right for a tool whose entire job is wrangling containers. No build step, no `node_modules`, just a script and a symlink.

I had some specific needs that the upstream project didn't cover, and rather than try to shoehorn them in as PRs that might not fit Kevin's vision, I forked.

---

## What I Needed That Didn't Exist

### 1. Rootless Podman (Not Docker-as-Root)

The upstream project uses Docker. That's fine for most people, but I run Podman rootless on Manjaro and I really didn't want to go back to giving a container runtime root access to my system. The whole point of isolation is, you know, _isolation_.

Podman's `--userns=keep-id` maps your host UID into the container so file ownership just works — no more files owned by `root` scattered through your project directory after the container touches them.

### 2. Seamless Claude Code Authentication

This was the one that almost made me give up.

Claude Code uses your machine ID (`/etc/machine-id`) as part of its device fingerprint. Inside a container, that's a different machine ID. Which means Claude Code thinks you're on a new machine. Which means it wants you to re-authenticate. Every. Single. Time.

And it wasn't just the machine ID. The container's username was `ubuntu` while my host username is `mcrowe` — another fingerprint mismatch. And the credentials live in `~/.claude/` which wasn't being shared.

The fix was a combination of three things:

```bash
# Mount host machine ID so Claude sees the same device
-v /etc/machine-id:/etc/machine-id:ro

# Share the entire Claude config directory (not piecemeal)
-v "$HOME/.claude:$CONTAINER_HOME/.claude:rw"
-v "$HOME/.claude.json:$CONTAINER_HOME/.claude.json:rw"

# Match the host username inside the container (build-time ARG)
--build-arg USERNAME="$USER"
```

Once all three pieces were in place: zero re-authentication. The container looks like the same machine to Claude Code. (Through much weeping and gnashing of teeth, I arrived at this combination.)

### 3. Hardware Auth Passthrough

I use a YubiKey for SSH via GPG agent, and 1Password's SSH agent for some repos. Both of those need socket passthrough into the container:

```bash
# 1Password SSH agent
-v "$HOME/.1password/agent.sock:$CONTAINER_HOME/.1password/agent.sock"

# GPG agent SSH socket (YubiKey)
-v "/run/user/$(id -u)/gnupg/S.gpg-agent.ssh:$CONTAINER_HOME/.gnupg-sockets/S.gpg-agent.ssh"
```

These are conditionally mounted — if the socket doesn't exist on your host, it's skipped. No errors, no broken containers.

### 4. Multiple AI Harnesses

I don't just use Claude Code. I bounce between OpenCode, Codex, and Gemini CLI depending on the task. The container image uses [mise](https://mise.jdx.dev/) instead of NVM, which manages Node, Python, pnpm, and all the CLI tools from a single config. One image, all the harnesses.

And there's an `extra-tools.txt` file (gitignored, personal to you) where you pick additional tools from a menu of mise-compatible options — `bat`, `lazygit`, `yazi`, `ruff`, whatever. Your picks get baked into the image at build time.

---

## The Egress Firewall: Containing the AI, Not Just the Files

Here's where it gets interesting.

File isolation is good. But the bigger exfiltration vector isn't the filesystem — it's the network. An AI agent with shell access can `curl` your secrets anywhere. The research on this is clear: the primary risk with agentic AI in development environments is data exfiltration over the network.

So every container session now starts with an iptables egress firewall:

```bash
iptables -P OUTPUT DROP   # Block everything by default

# Then whitelist only what's needed:
# - api.anthropic.com (Claude API)
# - github.com and friends (git, gh CLI, releases)
# - registry.npmjs.org (npm)
# - pypi.org (pip)
# - mise.jdx.dev (tool manager)
# - Host gateway (local services)
```

The default policy is DROP. If it's not on the whitelist, it doesn't leave the container. DNS is allowed (so resolution works), but TCP connections to non-whitelisted IPs are silently dropped.

Here's what that looks like in practice. I asked the AI harness inside the container to fetch reddit.com:

**Via the harness's MCP web tool:** Works fine — because MCP tools run server-side, outside the container's network namespace.

**Via direct `curl`:** Connection timed out on all 4 Reddit IPs. DNS resolved (allowed), but the actual connection was dropped by the firewall.

| Method                              | Network Access             |
| ----------------------------------- | -------------------------- |
| Direct (curl, bash, any shell tool) | Blocked by iptables        |
| MCP server tools (webReader, etc.)  | Runs outside the container |

The harness can't phone home, can't exfiltrate your code, can't hit unauthorized APIs. But its legitimate tool integrations that run outside the container still work perfectly. That's the right security boundary.

If you need unrestricted network access for a session:

```bash
container --no-firewall
```

---

## Getting Started

Install is a one-liner:

```bash
curl -fsSL https://raw.githubusercontent.com/drmikecrowe/code-container/main/install.sh | bash
```

Then build the image and go:

```bash
container --build        # One-time image build
cd /path/to/project
container                # Enter container shell
container --claude       # Jump straight into Claude Code (YOLO mode)
```

Session state persists. Packages you install stick around. Stop a container, come back tomorrow, pick up where you left off.

---

## Is It Worth It?

Absolutely — but with caveats. This is still very much a work-in-progress. The field of agentic AI security is young, and what constitutes "good enough" isolation is a moving target. The egress firewall is IP-based (resolved at session start), so long-running sessions could see CDN IPs rotate out from under the rules. Docker support for the networking features is untested. There are rough edges.

But here's what I can tell you: I run this every day. Multiple projects, multiple harnesses, hardware auth working seamlessly, no re-authentication, and I sleep a little better knowing that my AI agents can't `curl` my SSH keys to an arbitrary endpoint.

Check out the project on GitHub: [drmikecrowe/code-container](https://github.com/drmikecrowe/code-container)

And seriously — go give [kevinMEH/code-container](https://github.com/kevinMEH/code-container) a star. The foundation they built is what made all of this possible.

_Running AI coding agents without isolation? Tried that. Don't recommend it. Found a different approach? I'd love to hear about it — hit me up on [GitHub](https://github.com/drmikecrowe) or wherever you found this post._
