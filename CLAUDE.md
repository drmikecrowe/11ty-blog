# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal tech blog ("Mike's Shiny Objects") built with Hugo static site generator using the Ananke theme. Deployed to AWS S3/CloudFront.

## Common Commands

### Development

```bash
hugo server           # Local dev server (http://localhost:1313/)
hugo server -D        # Include draft posts
hugo                  # Build site to public/
```

### Creating Content

```bash
# Standard blog post
hugo new posts/YYYY/YYYY-MM-DD-my-post-title/index.md

# With specific archetype
hugo new posts/my-series.md --kind series-post
hugo new posts/my-tutorial.md --kind technical-tutorial

# TV show review
hugo new watching/tv/show-name/index.md --kind watching

# Movie review
hugo new watching/movies/movie-name/index.md --kind watching
```

### Deployment

```bash
./full-deploy.sh      # Build and deploy to S3 + CloudFront invalidation
                      # Requires AWS_PROFILE=personal-mike-AdministratorAccess

# Or manually:
hugo && aws s3 sync public/ s3://mikesshinyobjects.tech --delete
```

### Infrastructure

```bash
pulumi up             # Deploy/update AWS infrastructure (S3, CloudFront, Route53, ACM)
pulumi preview        # Preview changes
```

## Architecture

### Content Structure

```
content/
  _index.md           # Homepage content
  posts/
    _index.md         # Posts listing page
    YYYY/             # Posts organized by year
      YYYY-MM-DD-slug/
        index.md      # Post content (page bundles for images)
  watching/
    _index.md         # "What We're Watching" landing page
    tv/
      _index.md       # TV shows listing
      show-name/
        index.md      # Individual show review
    movies/
      _index.md       # Movies listing
      movie-name/
        index.md      # Individual movie review
```

### Watching Tags

- `currently-watching` - Shows/movies actively following
- `highly-recommended` - Top picks
- `2024`, `2025`, etc. - Year watched

### Theme Customization

Custom layouts override the Ananke theme in `layouts/`:
- `_default/single.html` - Single page template
- `partials/page-header.html` - Page header partial
- `posts/` - Post-specific templates

### Infrastructure (Pulumi)

`pulumi.ts` provisions:
- S3 bucket for static hosting
- CloudFront distribution with HTTPS
- ACM certificate with DNS validation
- Route53 A records for domain

Config in `Pulumi.mikesshinyobjects.yaml`.

## Blog Post Frontmatter

Key fields for the Ananke theme:

```yaml
title: "Post Title"
date: 2026-01-05T12:00:00-05:00
draft: false
description: "SEO description"
categories: [tech]           # tech, personal, pinnacle
tags: [tag1, tag2]
author: Mike Crowe
featured_image: "images/hero.jpg"  # Relative to post bundle
show_reading_time: true
```

See `archetypes/README.md` for full frontmatter reference and available templates.

## Issue Tracking

This project uses **beads** (`bd`) for issue tracking. See `AGENTS.md` for workflow.
