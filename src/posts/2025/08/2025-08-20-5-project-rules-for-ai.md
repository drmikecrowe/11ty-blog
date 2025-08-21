---
title: Project Rules for AI - Part 5 of 6
description: How to create effective project rules and memory banks that help AI understand your codebase and architectural decisions
date: 2025-08-20T00:00:00.000Z
preview: ""
draft: false
categories:
  - tech
type: default
excerpt: Creating effective project rules and memory banks for AI assistants is crucial for maintaining code quality and architectural consistency. Learn how to structure your project documentation to help AI understand your decisions and enforce your standards.
tags:
  - tech
  - ai
  - documentation
  - architecture
  - project-management
author: mike-crowe
seo:
  title: "Project Rules for AI: Creating Effective Memory Banks and Architectural Guidelines - Part 5 of 5"
  description: Learn how to create effective project rules and memory banks that help AI understand your codebase and maintain architectural consistency.
  image: 2025/08/project-rules-memory-bank.png
images:
  feature: 2025/08/project-rules-memory-bank.png
  thumb: 2025/08/project-rules-memory-bank.png
  slide:
---

# Project Rules for AI: Creating Effective Memory Banks and Architectural Guidelines

**Part 5 of 6: The AI-Assisted Development Workflow Series**

This is the fifth installment in a six-part series exploring how AI is transforming modern development workflows. In this series, I'll walk through my journey of building an AI-assisted development environment, from basic infrastructure setup to advanced architectural enforcement and task orchestration.

**Series Overview:**

- **Part 1:** MCP Servers, Ports, and Sharing - Setting up the foundation
- **Part 2:** ESLint Configuration Refactoring - Cleaning up tooling with AI
- **Part 3:** Custom Architectural Rules - Teaching AI to enforce design patterns
- **Part 4:** Task Orchestration - Managing complex refactoring workflows
- **Part 5 (This Post):** Project Rules for AI - Creating effective memory banks and guidelines
- **Part 6:** The Ultimate Design Review - Putting it all together

---

In the previous posts, we've taught our AI assistant _how_ to understand and enforce specific architectural rules. We've built a robust system for linting, testing, and managing complex tasks. But how do we ensure the AI behaves consistently and predictably over the long term? How do we give it a "personality" and a "memory" that aligns with our project's philosophy?

The answer lies in creating a comprehensive set of guidelines that the AI can consult before every action. In my setup, this is split into two key parts: the **Agent Protocol** and the **Project Rules**. Together, they form the "brain" of my AI development partner.

## The Agent Protocol: Defining the Personality

The first piece of the puzzle is the `memory-bank/AGENTS.md` file. I think of this as the AI's constitution or its core programming. It doesn't contain project-specific code rules; instead, it defines the AI's high-level behavior, its interaction style, and its core principles.

You can see some of the key sections from my `AGENTS.md` file:

- **Core Philosophy & Attitude**: This sets the tone. I want an "Expert Peer," not a subservient assistant. It should be direct, proactive, and value clean code principles above all else.
- **Interaction Protocol**: This defines how we communicate. No lectures, no fluff. It must clarify ambiguity and warn me if I'm asking it to do something that violates a convention.
- **Code Generation & Modification**: This governs how it writes code. It should edit files directly, respect formatting, and, most importantly, follow a specific code review process.
- **Context & Memory Bank**: This establishes the hierarchy of knowledge. The `memory-bank/` is the single source of truth, more important than the codebase, conversation history, or its own external knowledge.

This file establishes a baseline of behavior. It ensures that no matter what the specific task is, the AI approaches it with the same professional, efficient, and principle-driven mindset.

## The Project Rules: The Letter of the Law

If the `AGENTS.md` is the constitution, the files in `memory-bank/project-rules/` are the specific, legally-binding statutes of the project. These are granular, often file-specific rules that the AI _must_ follow.

These rules cover everything from technology usage to coding patterns:

- `00-pnpm.md`: "Always use pnpm for package management. Period."
- `02-effect-pattern.md`: A detailed, multi-point guide on how to use the Effect library, including import styles, composition patterns, and where `E.runPromise` is allowed to be called (hint: only in XState machines).
- `08-tailwind.md`: A treatise on our Tailwind CSS architecture, enforcing the strict separation of layout and style components.
- `09-state-machine-patterns.md`: Defines the actor-based hierarchy for our XState implementation, ensuring actions are routed correctly.

These rules are not suggestions; they are directives. The `AGENTS.md` file instructs the AI to treat the `memory-bank/` as its authoritative source of truth, and these files are the content of that memory. When I ask the AI to write a new component, it knows it must use CVA, it must not include margins, and it must get its available actions from a state machine actor—not because I told it to in the prompt, but because the rules demand it.

## Putting the Rules into Practice: Prompting with Precision

Having this well-documented set of rules is powerful, but the real leverage comes from how I use them to guide the AI's work. The rules aren't just a passive library; they are an active part of my prompting strategy.

A perfect example is my process for a comprehensive design review, which will be the topic of the next blog post. I don't just ask the AI to "review the code." I give it a highly structured plan that explicitly references the project rules at each step.

Using a task planning tool, I create a master "Design Review" request, which is then broken down into smaller, logical chunks (e.g., "DR Part 1 - Core App Files", "DR Part 2 - Components"). For each of these chunks, I create a series of subtasks, and this is where the magic happens. The description for each subtask points the AI to the exact rule it needs to enforce.

For example, the subtask for analyzing Effect patterns looks like this:

> **Title**: "Effect Pattern Analysis"
> **Description**: "Analyze Effect usage against `memory-bank/project-rules/02-effect-pattern.md`. Identify pattern violations, missing Effect implementations, and improvement opportunities. Generate specific action items."

I do the same for other concerns:

- **Component Styling Analysis**: "Review component styling against `memory-bank/project-rules/08-tailwind.md`..."
- **State Machine Analysis**: "Assess state machine implementations against `memory-bank/project-rules/09-state-machine-patterns.md`..."

This approach transforms the memory bank from a simple knowledge base into a set of precise instruments. I can direct the AI's focus with surgical accuracy, ensuring that each part of the codebase is evaluated against the correct, pre-defined standards. It's a clear, explicit contract: "For this task, these are the rules that matter."

## The Killer Feature: The AI Code Review

This brings me to the single most valuable instruction in the entire system. Buried in the `AGENTS.md` file is a simple-sounding, yet profound, directive:

> **Code Review Process**: After making ANY significant code changes, conduct an internal round table discussion with David Thomas (The Pragmatic Programmer), Andrew Hunt (The Pragmatic Programmer), and Uncle Bob (Clean Code). If they would approve, proceed; if not, iterate until they would approve.

This is where the magic happens.

This instruction forces the AI to pause and reflect. It takes its generated code, which already conforms to the strict **Project Rules** I've pointed it to, and then evaluates it against the higher-level principles of clean, pragmatic, and maintainable code embodied by these three legends of software engineering.

It's a two-layer filter:

1. **Does the code follow the rules?** (e.g., Is the Effect `pipe()` structured correctly? Are the Tailwind classes semantic?)
2. **Is the code _good_?** (e.g., Is it simple? Is it maintainable? Is there a better way to do this?)

This internal dialogue has been a game-changer. The AI doesn't just produce code that works; it produces code that is thought-out, clean, and aligned with the project's deepest architectural and philosophical goals. It catches things I would miss in a manual code review, and it does it instantly. It's like having a senior architect constantly looking over your shoulder, providing expert feedback in real-time.

By combining a high-level "personality" with a set of explicit, enforceable project rules, and then actively using those rules in our daily prompts, we create an AI assistant that is not just a tool, but a true partner in the development process.

In the final post of this series, we'll put all these pieces together and see how this system performs in a full-scale, complex design review.

```

```
