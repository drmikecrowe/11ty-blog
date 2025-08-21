---
title: How I Taught My AI Pair Programmer to Be Our Team's Tailwind CSS Cop - Part 3 of 6
description: Creating custom ESLint rules to enforce architectural discipline in Tailwind CSS projects with AI assistance
date: 2025-08-20T00:00:00.000Z
preview: ""
draft: false
categories:
  - tech
type: default
excerpt: When Tailwind CSS projects grow, architectural discipline becomes crucial. Learn how I created custom ESLint rules with AI to enforce a three-tier component system that keeps layout and styling concerns properly separated.
tags:
  - tech
  - javascript
  - typescript
  - eslint
  - tailwind
  - ai
  - architecture
author: mike-crowe
seo:
  title: How I Taught My AI Pair Programmer to Be Our Team's Tailwind CSS Cop - Part 3 of 5
  description: Learn how to create custom ESLint rules with AI to enforce architectural discipline in Tailwind CSS projects.
  image: 2025/08/tailwind-architectural-rules.png
images:
  feature: 2025/08/tailwind-architectural-rules.png
  thumb: 2025/08/tailwind-architectural-rules.png
  slide:
---

# How I Taught My AI Pair Programmer to Be Our Team's Tailwind CSS Cop

**Part 3 of 6: The AI-Assisted Development Workflow Series**

This is the third installment in a five-part series exploring how AI is transforming modern development workflows. In this series, I'll walk through my journey of building an AI-assisted development environment, from basic infrastructure setup to advanced architectural enforcement and task orchestration.

**Series Overview:**

- **Part 1:** MCP Servers, Ports, and Sharing - Setting up the foundation
- **Part 2:** ESLint Configuration Refactoring - Cleaning up tooling with AI
- **Part 3 (This Post):** Custom Architectural Rules - Teaching AI to enforce design patterns
- **Part 4:** Task Orchestration - Managing complex refactoring workflows
- **Part 5:** Project Rules for AI - Creating effective memory banks and guidelines
- **Part 6:** The Ultimate Design Review - Putting it all together

---

We've all been there. You start a new project with Tailwind CSS, and everything is beautiful. The utility-first approach is fast, flexible, and keeps you right in your HTML. But as the project grows and the team expands, the CSS landscape can start to feel like the Wild West. Utility classes get sprinkled everywhere, components start to blur the lines between structure and style, and soon you're overriding margins and fighting for specificity.

I love Tailwind, but I knew we needed to introduce some architectural discipline before things got out of hand. The problem is, architectural rules are only as good as their enforcement. Documentation gets stale, and nagging in code reviews doesn't scale.

So, I had a thought. What if I could teach our team's AI pair programmer to be our automated style cop? What if it could not only understand our rules but actively enforce them?

## The Convention: A Three-Tier System for Sanity

First, we needed a clear, simple convention. We decided on a three-tier component architecture designed to enforce a strict separation of concerns:

1. **Layout Components (`src/components/layout/`)**

   - **Job**: To arrange things on a page. They are the masters of `flex`, `grid`, and `gap`.
   - **The Rule**: They know nothing about style. No colors, no fonts, no borders. They are structurally pure.

2. **UI Components (`src/components/ui/`)**

   - **Job**: To be the beautiful, reusable building blocks. Buttons, Cards, Inputs, etc. They define their own appearance, including colors, fonts, and padding.
   - **The Rule**: They must be completely ignorant of their position on the page. This means **they are forbidden from having margins**. Spacing is the responsibility of the parent Layout Component, which uses `gap` or `space-*` to arrange them.

3. **Feature & Page Components (`src/pages/`, etc.)**
   - **Job**: To be the glue. These are the smart components that know about the business logic. They compose Layout and UI components to build actual features.
   - **The Rule**: The rules are relaxed here. This is the layer where we bring everything together. They can use layout and styling utilities to compose the other two component types.

This system ensures that our UI components are truly reusable and that our layout logic is centralized and predictable.

## The Solution: Hiring an AI for Architectural Enforcement

With the convention defined, I turned to my AI assistant. I described the three-tier system and asked, "Can you build a custom ESLint rule to enforce this?"

Working with the AI was like having a hyper-competent junior developer who knew the ESLint AST (Abstract Syntax Tree) better than I ever will. I provided the high-level architectural goals, and it handled the implementation details.

### How the Custom Plugin Works

The resulting ESLint rule is a simple but powerful detective. For every component file, it performs three steps:

1. **Location Check**: First, it looks at the component's file path. Does it live in `src/components/layout/`, `src/components/ui/`, or somewhere else? This determines which rulebook to apply.
2. **Class Inspection**: Next, it parses the JSX and extracts all the Tailwind classes from the `className` prop. It's smart enough to handle string literals and basic template literals.
3. **Rule Application**: Finally, it applies the logic:
   - If it's a **UI Component**, it scans the class list for any margin patterns (`m-*`, `mx-*`, `mt-*`, etc.) and flags them as errors.
   - If it's a **Layout Component**, it checks for any non-layout classes (like `bg-red-500`, `font-bold`, etc.) and flags those.
   - If it's a **Feature/Page Component**, it does nothing. They are free to compose as they see fit.

The AI generated the rule file, a utility file to hold the class definitions, and even modified our main `eslint.config.js` to wire it all up.

## The Results: The Moment of Truth

I ran the linter across our codebase, and it worked perfectly. It immediately flagged several components that were violating our new convention. Here’s a summary of what it caught:

- **AppLayout.tsx & Sidebar.tsx**: These core layout components were caught using styling classes like `bg-gray-100`, `text-purple-700`, and `font-bold`. The linter correctly identified these as style concerns that should not be in a layout component.
- **EmptyState.tsx & ErrorState.tsx**: These UI components had `mb-4` and `mt-2` margins, violating our "marginless UI" rule. The parent component should be responsible for this spacing.
- **FileDropzone.tsx & MainContent.tsx**: These UI components were using `mx-auto`, another margin-related property that is the responsibility of a layout container.
- **StatCard.tsx**: This UI component was using `mt-1` and `ml-1`, which are small but important violations of the architectural pattern.

Each of these warnings was a clear, actionable task for us to clean up the codebase and align it with our new, more maintainable architecture.

## Conclusion: More Than Just Code Generation

This experience was a powerful demonstration of how to use LLMs for more than just generating boilerplate or fixing simple bugs. By teaching the AI our team's specific architectural patterns, we were able to turn it into a partner for enforcing code quality and consistency at scale. It automated the tedious work of code validation, freeing us up to focus on building features.
