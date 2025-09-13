---
# Basic Content Information
title: "Series Title - Part X of Y"
description: "Description of this specific part in the series"
date: { { .Date } }
draft: false

# Layout and Structure
layout: post
type: default
permalink: "" # Optional: Custom URL path

# Content Summary
excerpt: "A compelling excerpt for this part of the series"
preview: "" # Additional preview text if needed

# Categorization
categories:
  - tech # Options: tech, personal, pinnacle, etc.
tags:
  - tech
  - series
  - part-1 # Update part number
  -  # Add relevant tags here

# Author Information
author: Mike Crowe

# SEO and Social Media
seo:
  title: "Series Title - Part X: Specific Focus"
  description: "Detailed description of this specific part in the series"
  image: "images/series-featured-image.jpg"
featured_image: "images/series-featured-image.jpg"

# Display Options
show_reading_time: true
private: false
omit_header_text: false
disable_share: false

# Series Information (Custom Fields)
series:
  name: "Your Series Name"
  part: 1 # Part number in series
  total_parts: 6 # Total parts in series
  previous_part: "" # URL to previous part (if any)
  next_part: "" # URL to next part (if any)
  series_description: "Overview of what this series covers"

# Advanced Options
canonicalUrl: ""
post_content_classes: "serif"
text_color: "mid-gray"
body_classes: "avenir bg-near-white"
background_color_class: "bg-black"
featured_image_class: "cover bg-center"
cover_dimming_class: "bg-black-60"
read_more_copy: "Read More"

# Custom Parameters
custom_param: ""
---

# Series Title - Part X of Y

**Part X of Y: [Series Name]**

This is part X of a Y-part series exploring [series topic]. In this installment, we'll focus on [specific topic for this part].

## Series Overview

[Brief description of what this series covers and why it's valuable]

**Series Parts:**

- **Part 1:** [Previous Part Title](/posts/previous-part-url/) - [Brief description]
- **Part 2:** [Current Part Title](/posts/current-part-url/) - [Brief description] ← **You are here**
- **Part 3:** [Next Part Title](/posts/next-part-url/) - [Brief description]
- **Part 4:** [Future Part Title](/posts/future-part-url/) - [Brief description]
- **Part 5:** [Future Part Title](/posts/future-part-url/) - [Brief description]
- **Part 6:** [Future Part Title](/posts/future-part-url/) - [Brief description]

---

## Introduction

[Introduction to this specific part of the series]

## Main Content

[Your main content for this part]

## Key Takeaways

- [Key point 1]
- [Key point 2]
- [Key point 3]

## What's Next

In the next part of this series, we'll explore [next topic]. [Brief teaser about what's coming next].

---

## Series Navigation

<div style="display: flex; justify-content: space-between; margin: 2rem 0; padding: 1rem; background-color: #f8f9fa; border-radius: 8px;">

<div style="flex: 1; text-align: left;">
**← Previous:** [Previous Part Title](/posts/previous-part-url/) <!-- Update with actual URL -->
</div>

<div style="flex: 1; text-align: center;">
**Part 1 of 6** <!-- Update with actual part numbers -->
</div>

<div style="flex: 1; text-align: right;">
**Next →:** [Next Part Title](/posts/next-part-url/) <!-- Update with actual URL -->
</div>

</div>

## Series Features

This template includes special features for series posts:

### Series Metadata

- `series.name`: The overall series name
- `series.part`: Current part number
- `series.total_parts`: Total number of parts
- `series.previous_part`: URL to previous part
- `series.next_part`: URL to next part
- `series.series_description`: Overview of the series

### Navigation

- Built-in series navigation at the bottom
- Clear indication of current part
- Links to previous/next parts when available

### SEO Optimization

- Series-specific titles and descriptions
- Consistent tagging with series information
- Proper internal linking between parts

## Usage Tips for Series

1. **Consistent Naming**: Use consistent naming patterns for series parts
2. **Update Links**: Keep previous_part and next_part URLs updated
3. **Series Overview**: Include a clear overview of what the series covers
4. **Cross-References**: Link between related parts
5. **Progress Indicators**: Show readers where they are in the series

## Example Series Structure

```yaml
# Part 1
series:
  name: "AI-Assisted Development Workflow"
  part: 1
  total_parts: 6
  previous_part: ""
  next_part: "/posts/part-2-url/"

# Part 2
series:
  name: "AI-Assisted Development Workflow"
  part: 2
  total_parts: 6
  previous_part: "/posts/part-1-url/"
  next_part: "/posts/part-3-url/"

# Part 6 (Final)
series:
  name: "AI-Assisted Development Workflow"
  part: 6
  total_parts: 6
  previous_part: "/posts/part-5-url/"
  next_part: ""
```

This template provides everything you need to create engaging, well-structured series posts that work seamlessly with the Ananke theme.
