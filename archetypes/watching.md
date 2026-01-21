---
title: "{{ replace .Name "-" " " | title }}"
description: "Our thoughts on {{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: false

# NOTE: Content is organized in YYYY-MM folders:
# - Movies: content/watching/movies/YYYY-MM/slug-name/index.md
# - TV: content/watching/tv/YYYY-MM/slug-name/index.md

# Categorization
genres:
  - ""  # Genre (e.g., Drama, Sci-Fi, Comedy, Thriller, Horror, etc.)
media_types:
  - ""  # Media type: TV or Movie
tags:
  - 2026  # Year watched (e.g., 2024, 2025, 2026)
  # - currently-watching  # Uncomment if actively following
  # - highly-recommended  # Uncomment for top picks
  # - worth-watching      # Uncomment for solid recommendations
rank:  # 1-5 ranking for highly-recommended/worth-watching items (1 = top, 5 = still good)

# Author Information
author: Mike Crowe

# Display Options
show_reading_time: true
featured_image: ""  # Optional: path to show/movie poster image
---

## Overview

Brief description of the show/movie.

## Our Take

What we thought about it.

## Rating

⭐⭐⭐⭐⭐ (X/5)
