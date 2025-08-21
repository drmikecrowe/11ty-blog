---
title: "The Ultimate Design Review: Orchestrating AI with Task-Based Workflows - Part 6 of 6"
description: "The final part of the series, where we combine AI agents, project rules, and task orchestration to perform a comprehensive, automated codebase design review."
date: 2025-08-21T00:00:00.000Z
preview: ""
draft: false
categories:
  - tech
type: default
excerpt: "Putting it all together: A deep dive into a prompt-driven workflow that uses an AI assistant to perform a full-scale design review, generating an actionable backlog of tasks."
tags:
  - tech
  - ai
  - architecture
  - project-management
  - automation
  - prompting
author: mike-crowe
seo:
  title: "The Ultimate Design Review: Orchestrating AI with Task-Based Workflows - Part 6 of 6"
  description: "A deep dive into a prompt-driven workflow that uses an AI assistant to perform a full-scale design review, generating an actionable backlog of tasks."
  image: 2025/08/ultimate-design-review.png
images: # relative to /src/assets/images/
  feature: 2025/08/ultimate-design-review.png
  thumb: 2025/08/ultimate-design-review.png
  slide:
---

# The Ultimate Design Review: Orchestrating AI with Task-Based Workflows

**Part 6 of 6: The AI-Assisted Development Workflow Series**

This is the final installment in our six-part series on building an AI-assisted development workflow. We've set up our infrastructure, taught the AI our coding standards, and established a robust "memory bank" of project rules. Now, it's time to put it all to the test with the ultimate challenge: a comprehensive, end-to-end design review of the entire codebase.

**Series Overview:**

- **Part 1:** MCP Servers, Ports, and Sharing
- **Part 2:** ESLint Configuration Refactoring
- **Part 3:** Custom Architectural Rules
- **Part 4:** Task Orchestration
- **Part 5:** Project Rules for AI
- **Part 6 (This Post):** The Ultimate Design Review

---

## The Challenge: From "Codebase" to "Action Plan"

How do you review an entire `src/` directory? You can't just feed it to an AI and say, "find problems." The context is too large, the potential feedback is too broad, and the output would be a wall of text, not an actionable plan. To understand the issue, grab a pair of binoculars and use them in your office: Have a coworker toss an index card somewhere in your office and then search for that with the binoculars. If you have a really large code base, have your coworker put it in the office somewhere. That's what your fighting:

- The binoculars symbolize the AI context. It's a fixed width window of information the AI can maintain
- The index card is what you are asking the AI to find

My goal was to create a system that could:

1. Systematically analyze the entire codebase in manageable chunks.
2. Evaluate each chunk against multiple, specific architectural rules.
3. Produce a structured, prioritized, and actionable list of tasks.
4. Be entirely automated and repeatable.

To achieve this, I created a multi-layered prompting strategy that uses the [TaskFlow MCP server](https://github.com/pinkpixel-dev/taskflow-mcp) to orchestrate the entire workflow. The process is driven by two key prompt files.

## The Master Plan: `new-design-review.md`

The first file, `@memory-bank/prompts/design-review/new-design-review.md`, is the high-level orchestrator. It doesn't perform the analysis itself; it instructs the AI on how to set up the entire project plan within TaskFlow tasks.

Here's the strategy it lays out:

1. **Create Two Buckets:** The first thing it does is create two separate requests in the task server: one for the _analysis process_ and one for the _action items_. This is a critical separation of concerns. The analysis tasks will be marked as "done" once the review is complete, but the action items will form a living backlog of work to be done.

2. **Divide and Conquer:** It then breaks the entire `src/` directory into logical chunks: Core App Files, Components, Services, Machines, Hooks, etc. For each chunk, it creates a parent task in the "analysis" request.

3. **The Mini-Review Subtasks:** This is where the granularity comes in. For each parent task (e.g., `DR Part 3 - Components (Dashboard)`), the prompt instructs the AI to create four specific subtasks:

   - Overall Design Analysis
   - Effect Pattern Analysis
   - Component Styling Analysis
   - State Machine Analysis

   As we saw in the last post, these subtasks explicitly point to the relevant project rules in the memory bank, ensuring the AI evaluates the code against the correct standards. I wanted granular reviews, and the higher level review tends to catch architectural issues, whereas this catches specific implementation issues.

## The Instruction Manual: `request-2-instructions.md`

If the first prompt is the "what," then `@memory-bank/prompts/design-review/request-2-instructions.md` is the "how." This file is a set of instructions for the AI on how to behave _while it is executing_ the analysis subtasks.

Its most critical directive is this: **You MUST create new tasks in the "Action Items" request for every issue you find.**

It strictly forbids the AI from simply summarizing its findings. Instead, it must translate every identified improvement into a well-formed task, complete with a title, description, and severity, and add it to the other request bucket. This is what turns a qualitative review into a quantitative project plan.

## The Results: An Actionable Backlog

After running the AI through this workflow, the `taskflow-mcp` server populates a YAML file with the results. The file from my design review, `@DESIGN-REVIEWS/2025-08-19/tasks.yaml`, is over 800 lines long, but here are a few snippets that show the power of this system.

First, you can see the completed analysis task for the "Core App Files," with its four subtasks all marked as done:

```yaml
- id: task-62
  title: DR Part 1 - Core App Files
  description: |-
    Analyze the following files for design patterns, code quality, and architectural consistency:nn- src/App.tsxn- src/appMachineContext.tsn- src/config.tsn- src/context/DashboardDataContext.tsx
    ...
  done: true
  subtasks:
    - id: subtask-71
      title: Overall Design Analysis
      done: true
    - id: subtask-72
      title: Effect Pattern Analysis
      done: true
    - id: subtask-73
      title: Component Styling Analysis
      done: true
    - id: subtask-74
      title: State Machine Analysis
      done: true
```

More importantly, the _real_ output is the list of actionable tasks generated in the other request. The AI identified dozens of specific, granular improvements, each perfectly formatted according to the instruction prompt.

Here are a few examples of the generated tasks:

A high-priority refactoring task based on our Effect pattern rules:

```yaml
- id: task-98
  title: Add Effect-based validation to ExcelService
  description: ExcelService.ts contains complex validation logic in generateExpenseReport function. Add Effect-based validation using E.succeed().pipe(E.filterOrFail()) pattern for report and expense data validation.
```

A task to fix a clear violation of our Tailwind CSS architecture:

```yaml
- id: task-139
  title: Fix EmptyState.tsx UI component margin violations
  description: Remove margin classes from EmptyState.tsx component. The component contains margin classes mb-4, mb-2, mb-6 that should be handled by parent layout components. Read memory-bank/AGENTS.md and review memory-bank/project-rules/* before starting.
```

A task for a significant architectural improvement to break up a monolithic file:

```yaml
- id: task-99
  title: Extract ExcelService helper functions to separate modules
  description: ExcelService.ts is a 485-line monolith with many helper functions. Extract helper functions into separate modules (excel-formatting.ts, excel-data.ts, excel-styles.ts) to improve maintainability and testability.
```

## Conclusion: The Sum of the Parts

This automated design review is the culmination of our entire AI-assisted workflow. It seamlessly integrates:

- **The Agent Protocol (`AGENTS.md`):** Provides the core principles for the AI's analysis.
- **The Project Rules (`project-rules/`):** Act as the specific, enforceable standards for the review.
- **The Prompting Strategy (`prompts/`):** Orchestrates the complex workflow, breaking it down into manageable steps.
- **The Task Server (`taskflow-mcp`):** Captures the output, transforming a review into an actionable project backlog.

By investing the time to teach the AI _how_ we build software, we've unlocked the ability to automate one of the most time-consuming and critical parts of the development lifecycle. We've moved beyond simple code generation to a world where our AI partner can actively help us manage quality, reduce technical debt, and enforce architectural consistency at scale. It's a powerful glimpse into the future of software development.
