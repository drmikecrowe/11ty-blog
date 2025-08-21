---
title: My ESLint Config Was a Mess. I Asked an AI to Fix It. - Part 2 of 6
description: How I used AI to clean up and refactor my ESLint configuration for a modern TypeScript and Tailwind CSS v4 project
date: 2025-08-20T00:00:00.000Z
preview: ""
draft: false
categories:
  - tech
type: default
excerpt: When my ESLint configuration became a house of cards, I turned to AI for help. The result was a clean, refactored config that automatically enforces code quality and consistency across our TypeScript and Tailwind CSS v4 project.
tags:
  - tech
  - javascript
  - typescript
  - eslint
  - tailwind
  - ai
author: mike-crowe
seo:
  title: My ESLint Config Was a Mess. I Asked an AI to Fix It. - Part 2 of 5
  description: Learn how to use AI to refactor and improve your ESLint configuration for modern TypeScript and Tailwind CSS projects.
  image: 2025/08/eslint-config-refactor.png
images:
  feature: 2025/08/eslint-config-refactor.png
  thumb: 2025/08/eslint-config-refactor.png
  slide:
---

# My ESLint Config Was a Mess. I Asked an AI to Fix It.

**Part 2 of 6: The AI-Assisted Development Workflow Series**

This is the second installment in a five-part series exploring how AI is transforming modern development workflows. In this series, I'll walk through my journey of building an AI-assisted development environment, from basic infrastructure setup to advanced architectural enforcement and task orchestration.

**Series Overview:**

- **Part 1:** MCP Servers, Ports, and Sharing - Setting up the foundation
- **Part 2 (This Post):** ESLint Configuration Refactoring - Cleaning up tooling with AI
- **Part 3:** Custom Architectural Rules - Teaching AI to enforce design patterns
- **Part 4:** Task Orchestration - Managing complex refactoring workflows
- **Part 5:** Project Rules for AI - Creating effective memory banks and guidelines
- **Part 6:** The Ultimate Design Review - Putting it all together

---

If you're a frontend developer, you know the love-hate relationship we have with ESLint. We love that it keeps our code clean and consistent. We hate spending hours wrestling with config files, trying to get plugins to play nicely with each other, especially in a modern TypeScript and Tailwind CSS v4 world.

My `eslint.config.js` was starting to feel like a house of cards. I wanted to add better Tailwind CSS linting, but my first attempt with a popular plugin led to a cascade of peer dependency warnings and configuration errors. After a few failed attempts, I realized I was spending more time configuring the linter than writing code. This is not the way.

So, I turned to my AI pair programmer with a simple plea: "Help me fix this mess."

## Why is eslint locking up?

The first issue I needed help with was that ESLint was trying to use type-aware rules with multiple TypeScript config files, which can cause it to hang when processing large codebases. Type-aware rules like `@typescript-eslint/no-unused-vars` and `@typescript-eslint/no-floating-promises` require ESLint to perform complex type checking across your entire project, and when you have multiple `tsconfig.json` files or conflicting TypeScript configurations, this can lead to infinite loops or excessive memory usage.

The solution was to create a **dual-config approach** that separates type-aware and non-type-aware rules:

- **App files** use the fast, non-type-aware config for quick feedback during development
- **Test files** use the comprehensive type-aware config for thorough validation
- **Shared configuration** provides common rules and plugins across both configs

This separation allows ESLint to run quickly during development while still providing comprehensive type checking where it matters most.

## The Mission: Clean, Refactored ESLint Config

My goal was to not just get a new Tailwind plugin working, but to clean up the entire ESLint configuration. The process, guided by the AI, was a masterclass in untangling complexity.

Here’s what the AI did, based on the final git commit that fixed everything:

### 1. Refactoring for Readability and DRYness

The first thing it did was apply the Don't Repeat Yourself (DRY) principle to my config. Instead of having separate, nearly identical objects for different TypeScript configurations, it created common, reusable building blocks:

- `COMMON_PLUGINS`: A single object defining all the ESLint plugins we use, like `@typescript-eslint`, `prettier`, `react-hooks`, and the new Tailwind plugins.
- `COMMON_SETTINGS`: A shared object for settings, like the import resolver paths.
- `COMMON_RULES`: A comprehensive object containing all the rules that apply across the entire project.

This immediately made the config file shorter, cleaner, and much easier to understand. If we need to add a new rule everywhere, we now only have to add it in one place.

### 2. Installing and Configuring the _Right_ Plugins

The initial journey involved some trial and error. We first tried `eslint-plugin-tailwindcss`, but it had issues with our Tailwind v4 setup. The AI helped diagnose this and suggested a better alternative. The final commit shows the installation of two key packages:

- `eslint-plugin-better-tailwindcss`: A fantastic plugin for sorting classes and catching duplicates and conflicts.
- `@poupe/eslint-plugin-tailwindcss`: Another great plugin that adds more advanced checks, like preferring theme tokens and validating CSS modifiers.

### 3. Dialing in the Rules

This was the most crucial part. The AI configured the new plugins with a sensible set of rules, turning some on as warnings and others as errors:

```javascript
// Tailwind CSS rules
'better-tailwindcss/sort-classes': 'warn',
'better-tailwindcss/no-duplicate-classes': 'error',
'better-tailwindcss/no-conflicting-classes': 'error',
'better-tailwindcss/no-unregistered-classes': 'off', // We turned this off because we use custom design tokens
'better-tailwindcss/enforce-shorthand-classes': 'warn',

// Poupe Tailwind CSS rules
'tailwindcss/no-conflicting-utilities': 'error',
'tailwindcss/prefer-theme-tokens': 'warn',
'tailwindcss/valid-modifier-syntax': 'error',
```

Notice the `no-unregistered-classes` rule is off. The AI correctly identified from the linter output that our custom design tokens (like `bg-primary`) were being flagged, and recommended disabling this rule to avoid noise, which was exactly the right call.

### 4. Automatically Fixing What It Could

The best part? The new `sort-classes` rule didn't just flag inconsistent class ordering—it fixed it. The git commit is full of small, satisfying changes where messy class strings were automatically reordered into a logical, consistent format:

**Before:**

```jsx
<div className='flex justify-center items-center h-32'>
```

**After:**

```jsx
<div className='flex h-32 items-center justify-center'>
```

This happened across dozens of files. It’s a small change, but it adds up to a huge improvement in code quality and developer experience, and it was all done automatically.

## The Result: Effortless Code Quality

After the AI finished its work, our ESLint setup was transformed. It's now:

- **Easy to read and maintain.**
- **Using modern, effective plugins** for our specific stack.
- **Automatically enforcing** a consistent style for our utility classes.

This experience was a powerful reminder that AI assistants are more than just code generators. They can be expert systems administrators, helping to configure and maintain the complex tooling that modern development relies on. It took a task that was a source of frustration and turned it into a clean, automated part of our workflow. And for that, I am very grateful.

## The Final Architecture: Dual-Config with Shared Rules

The AI helped me implement a sophisticated dual-config architecture that solves the performance issues while maintaining comprehensive linting coverage. Here's how it works:

### 1. Shared Configuration (`eslint.shared.config.js`)

The shared config provides the foundation with common plugins, settings, and rules that apply across the entire project:

```javascript
// Common plugins used across all TypeScript configs
const COMMON_PLUGINS = {
  "@typescript-eslint": tseslint.plugin,
  "react-hooks": reactHooks,
  "react-refresh": reactRefresh,
  import: importPlugin,
  prettier: prettierPlugin,
  "react-dom": reactDom,
  perfectionist,
  "react-x": reactX,
  "unused-imports": unusedImports,
  visual: visualComplexity,
  "better-tailwindcss": betterTailwindcss,
  tailwindcss: poupeTailwindcssPlugin,
}

// Factory function to create TypeScript configs with different rule sets
const createTypeScriptConfig = (...tsRuleSets) => ({
  languageOptions: {
    parser: tseslint.parser,
    parserOptions: {
      ecmaFeatures: {
        jsx: true,
      },
    },
  },
  plugins: COMMON_PLUGINS,
  rules: {
    ...COMMON_RULES,
    // Merge all provided TypeScript rule sets
    ...Object.assign({}, ...tsRuleSets),
  },
  settings: COMMON_SETTINGS,
})
```

This factory pattern allows us to create different TypeScript configurations with varying levels of strictness.

### 2. App Configuration (`eslint.app.config.js`)

The app config implements the performance-optimized approach:

```javascript
export default [
  // Global ignores
  {
    ignores: [...sharedIgnores, "shared/**"],
  },
  // App TypeScript files WITHOUT type-aware rules (for speed)
  {
    files: appFiles,
    languageOptions: {
      ...typescriptConfig.languageOptions,
      globals: browserGlobals,
    },
    plugins: typescriptConfig.plugins,
    rules: typescriptConfig.rules,
    settings: typescriptConfig.settings,
  },
  // Test files override WITH type-aware rules
  {
    files: ["**/*.test.{js,jsx,ts,tsx}"],
    languageOptions: {
      ...typescriptConfig.languageOptions,
      parserOptions: {
        ...typescriptConfig.languageOptions.parserOptions,
        project: "./tsconfig.test.json",
        tsconfigRootDir: import.meta.dirname,
      },
      globals: {
        ...globals.jest,
        ...browserGlobals,
      },
    },
    plugins: typescriptConfig.plugins,
    rules: {
      ...typescriptConfig.rules,
      ...testConfig.rules,
    },
    settings: typescriptConfig.settings,
  },
]
```

### 3. The Performance Solution

The key insight was creating two distinct TypeScript configurations:

- **`typescriptConfig`**: Uses `tseslint.configs.recommended` and `tseslint.configs.stylistic` - fast, syntax-based rules
- **`typeAwareConfig`**: Uses `tseslint.configs.recommendedTypeChecked`, `tseslint.configs.strictTypeChecked`, and `tseslint.configs.stylisticTypeChecked` - comprehensive type-aware rules

By applying the fast config to app files and the comprehensive config only to test files, we get:

- **Fast development feedback** - ESLint runs quickly during coding
- **Thorough validation** - Type-aware rules catch issues in tests where they matter most
- **Maintainable architecture** - Shared configuration keeps everything DRY

This architecture demonstrates how AI can help design sophisticated solutions that balance performance with functionality, turning a frustrating configuration problem into an elegant, scalable system.
