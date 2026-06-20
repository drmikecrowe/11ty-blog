---
layout: post
title: "Secrets Management with 1Password - Part 2 of 3"
description: "How I use 1Password CLI integration in Dorothy to safely manage secrets in environment variables"
date: 2026-01-05T16:10:51.000Z
permalink: /posts/2026/2026-01-05-dorothy-series-part-2/
preview: ""
draft: false
categories:
    - tech
type: default
excerpt: "Stop hardcoding API keys in your shell config. Here's how I use 1Password CLI to load secrets on-demand in any shell."
tags:
    - tech
    - dorothy
    - 1password
    - shell
    - devops
author: Mike Crowe
seo:
    title: "Secrets Management with 1Password - Part 2 of 3"
    description: "How I use 1Password CLI integration in Dorothy to safely manage secrets in environment variables"
    image: images/featured.png
featured_image: images/featured.png
---

**Part 2 of 3: The Dorothy Configuration Series**

This is the second installment in a three-part series exploring how I use [Dorothy](https://github.com/bevry/dorothy) to manage my shell configuration across multiple shells and operating systems. In this post, I'll show you how to securely manage API keys and secrets without ever committing them to your dotfiles.

**Series Overview:**

- **Part 1:** [Taming the Dotfile Chaos with Dorothy](/posts/2026/2026-01-05-dorothy-series-part-1-taming-dotfile-chaos-with-dorothy/) - Introduction and core concepts
- **Part 2:** [Secrets Management with 1Password](/posts/2026/2026-01-05-dorothy-series-part-2-secrets-management-with-1password/) - Safe environment variable handling (this post)
- **Part 3:** [AI-Powered Shell Commands with Shell-GPT](/posts/2026/2026-01-05-dorothy-series-part-3-ai-powered-shell-commands-with-shell-gpt/) - Natural language shell integration

---

_This post was written with AI assistance (Claude) for structure, formatting, and information gathering. The ideas, direction, and voice are my own._

## The Problem with Secrets

Let me start with a confession:

> **I've committed API keys to git repos more times than I'd like to admit.**

We've all been there. You're setting up a new project, you need an API key, and you think "I'll just put it in my `.bashrc` for now and fix it later." Spoiler: you never fix it later. And then one day you're grepping through your dotfiles and there's your OpenAI key, in plain text, staring back at you.

The usual solutions all have problems. Environment variables in your shell config? Plain text. A `.env` file? Still plain text, just in a different location. Secret managers with their own CLIs? Now you're copying and pasting tokens around.

What I really wanted was a way to reference secrets in my environment that wouldn't actually expose them until I explicitly needed them.

## Enter 1Password CLI

If you're already using 1Password, you probably know about their CLI tool (`op`). What you might not know is that it supports a special URL scheme for referencing secrets:

```
op://vault-name/item-name/field-name
```

This is just a string. It's not your actual secret—it's a _reference_ to your secret. The `op` CLI can resolve these references, but only after you've authenticated.

This is a pretty standard development flow that [1Password recommends](https://developer.1password.com/docs/cli/secrets-environment-variables) which I use frequently. However, what about when you need the secret value and you don't want to prefix your command with `op run`? That's how these scripts came into my daily usage.

## The Setup

### Step 1: Define Your Secret References

In Dorothy, I have a `config.local` folder for machine-specific configuration that doesn't get synced. Inside that, I have a `1password.env` file:

```bash
# ~/.config/dorothy/config.local/1password.env
OPENAI_API_KEY=op://Private/OpenAI-API-Key/api-key
ANTHROPIC_API_KEY=op://Private/Claude-API-Key/credential
HUGGINGFACE_API_KEY=op://Private/HuggingFace-token/credential
GEMINI_API_KEY=op://Private/Gemini-API-key/credential
BRAVE_SEARCH_API_KEY=op://Private/BraveSearchApiKey/credential
```

These get sourced into my environment on shell startup. At this point, if I run `echo $OPENAI_API_KEY`, I just get:

```
op://Private/OpenAI-API-Key/api-key
```

Not very useful for actually calling APIs, but also not a secret sitting in plain text.

### Step 2: The Helper Scripts

Here's where it gets interesting. In Dorothy I have shell-specific scripts that provide three functions:

- `load-1password` — Authenticate and resolve all `op://` references to actual secrets
- `unload-1password` — Restore the original `op://` references
- `op-status` — Show what's currently loaded

I've written implementations for Zsh, Fish, and Nushell. Let's walk through how they work.

### The Zsh Implementation

```zsh
load-1password() {
    # Find all exported env vars containing op://
    local -a op_names
    local -a op_values
    local name value

    while IFS='=' read -r name value; do
        [[ "$value" == *'op://'* ]] || continue
        op_names+=("$name")
        op_values+=("$value")
    done < <(env)

    if (( ${#op_names} == 0 )); then
        echo "No op:// references found in environment"
        return
    fi

    # Store originals for unload (name|value pairs)
    local -a originals
    local i
    for ((i=1; i<=${#op_names}; i++)); do
        originals+=("${op_names[$i]}|${op_values[$i]}")
    done
    export __OP_ORIGINAL__="${(j:\n:)originals}"

    # Build template and inject
    local template=""
    for ((i=1; i<=${#op_names}; i++)); do
        template+="${op_names[$i]}=${op_values[$i]}"$'\n'
    done

    local decoded
    decoded=$(printf '%s' "$template" | op inject)

    # Update environment with decoded values
    local line
    while IFS= read -r line; do
        [[ -n "$line" ]] || continue
        local vname="${line%%=*}"
        local vvalue="${line#*=}"
        typeset -gx "$vname"="$vvalue"
    done <<< "$decoded"

    local count=${#op_names}
    echo "Loaded $count secrets from 1Password"
}
```

The key insight here is `op inject`. This command takes a template with `op://` references and outputs the same template with secrets resolved. By piping our environment variable definitions through it, we get the actual values back. We also stash the original `op://` references in `__OP_ORIGINAL__` so we can restore them later.

So what does this do? _It activates these secrets in my current shell environment_. This is fantastic — gives me ad-hoc, secure access to my secrets without jumping through the `op run` hoops.

The `unload-1password` function just reverses the process:

```zsh
unload-1password() {
    if [[ -z "${__OP_ORIGINAL__:-}" ]]; then
        echo "No 1Password secrets currently loaded"
        return
    fi

    # Restore original op:// references
    local -a originals
    originals=("${(@s:\n:)__OP_ORIGINAL__}")

    local entry name value
    for entry in "${originals[@]}"; do
        name="${entry%%|*}"
        value="${entry#*|}"
        typeset -gx "$name"="$value"
    done

    unset __OP_ORIGINAL__
    echo "Restored ${#originals} op:// references"
}
```

### The Fish Implementation

Fish has its own syntax, but the logic is identical:

```fish
function load-1password
    # Find all env vars containing op://
    set -l op_names
    set -l op_values

    for name in (set -nx)
        if string match -qr 'op://' -- $$name
            set -a op_names $name
            set -a op_values $$name
        end
    end

    if test -z "$op_names"
        echo "No op:// references found in environment"
        return
    end

    # Store originals for unload
    set -l originals
    for i in (seq (count $op_names))
        set -a originals "$op_names[$i]|$op_values[$i]"
    end
    set -gx __OP_ORIGINAL__ (string join '\n' $originals)

    # Build template and inject
    set -l template
    for i in (seq (count $op_names))
        set -a template "$op_names[$i]=$op_values[$i]"
    end
    set -l decoded (string join '\n' $template | op inject)

    # Update environment with decoded values
    for line in (string split '\n' $decoded)
        if test -n "$line"
            set -l parts (string split -m 1 '=' $line)
            if test (count $parts) -eq 2
                set -gx $parts[1] $parts[2]
            end
        end
    end

    echo "Loaded "(count $op_names)" secrets from 1Password"
end
```

### The Nushell Implementation

And here's where Nushell shines. The same logic, but much more readable:

```nu
def --env load-1password [] {
    # Find all env vars containing op://
    let op_vars = ($env
        | transpose name value
        | where { ($in.value | describe) == "string" and ($in.value | str contains "op://") }
    )

    if ($op_vars | is-empty) {
        print "No op:// references found in environment"
        return
    }

    # Store originals for unload
    $env.__OP_ORIGINAL__ = ($op_vars | to nuon)

    # Build template and inject
    let template = ($op_vars | each { $"($in.name)=($in.value)" } | str join "\n")
    let decoded = ($template | ^op inject | lines | parse "{name}={value}")

    # Update environment with decoded values
    for row in $decoded {
        load-env { ($row.name): $row.value }
    }

    print $"Loaded ($decoded | length) secrets from 1Password"
}
```

That `$env | transpose name value | where ...` pipeline is just _chef's kiss_. Nushell treats the environment as structured data, making this kind of manipulation elegant.

## Using It in Practice

The workflow is simple:

```bash
# Check what's available
$ op-status
1Password secrets not loaded: 17 op:// references found
  OPENAI_API_KEY
  ANTHROPIC_API_KEY
  HUGGINGFACE_API_KEY
  ...

# Load the secrets (triggers biometric/password auth)
$ load-1password
Loaded 17 secrets from 1Password

# Now your API calls work
$ echo $OPENAI_API_KEY
sk-proj-abc123...

# When you're done, clean up
$ unload-1password
Restored 17 op:// references

# Back to references
$ echo $OPENAI_API_KEY
op://Private/OpenAI-API-Key/api-key
```

Here's what that looks like in practice:

<video controls width="100%" style="max-width: 800px;">
  <source src="images/Screencast_20260106_044849.webm" type="video/webm">
  Your browser does not support the video tag.
</video>

The beauty of this approach:

1. **Secrets are never in plain text in config files** — Only `op://` references get committed or stored
2. **Explicit authentication** — You consciously decide when to load secrets
3. **Easy cleanup** — One command restores the safe state

## Beyond Dorothy

While I use this within Dorothy's `custom` folder structure, these scripts work anywhere. You could drop them in your own dotfiles and source them directly. The only requirements are:

1. The 1Password CLI (`op`) installed and configured
2. Your secrets stored as `op://` references in environment variables

You can grab the scripts from my [Dorothy config repo](https://github.com/drmikecrowe/dorothy-config.git) and adapt them for your setup.
