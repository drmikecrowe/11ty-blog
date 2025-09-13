---
# Basic Content Information
title: "{{ replace .Name "-" " " | title }}"
description: "Brief description of your blog post for SEO and social sharing"
date: {{ .Date }}
draft: false

# Layout and Structure
layout: post
type: default
permalink: "" # Optional: Custom URL path (e.g., "/my-custom-url/")

# Content Summary
excerpt: "A compelling excerpt that will appear in post listings and social media previews"
preview: "" # Additional preview text if needed

# Categorization
categories:
  - tech # Options: tech, personal, pinnacle, etc.
tags:
  - tech
  - # Add relevant tags here

# Author Information
author: Mike Crowe

# SEO and Social Media
seo:
  title: "Custom SEO Title (optional - defaults to title)"
  description: "Custom SEO description (optional - defaults to description)"
  image: "images/your-featured-image.jpg" # Path to social media image
featured_image: "images/your-featured-image.jpg" # Main featured image

# Display Options
show_reading_time: true # Show estimated reading time
private: false # Set to true to prevent search engine indexing
omit_header_text: false # Hide the header text on the page
disable_share: false # Disable social sharing buttons

# Advanced Options
canonicalUrl: "" # Canonical URL if different from permalink
post_content_classes: "serif" # Content styling: "serif" or "sans-serif"
text_color: "mid-gray" # Text color class
body_classes: "avenir bg-near-white" # Body CSS classes
background_color_class: "bg-black" # Background color class
featured_image_class: "cover bg-center" # Featured image styling
cover_dimming_class: "bg-black-60" # Cover overlay styling
read_more_copy: "Read More" # Custom "read more" text

# Custom Parameters (for advanced use)
custom_param: "" # Add any custom parameters your theme might use
---

# Your Blog Post Title

Write your blog post content here. This template includes all the frontmatter fields that the Ananke theme supports, so you can customize the appearance and behavior of your post.

## Key Features of This Template

- **SEO Optimized**: Includes proper meta descriptions, titles, and social media images
- **Flexible Categorization**: Supports categories and tags for organization
- **Author Attribution**: Proper author information for bylines
- **Reading Experience**: Configurable reading time, text styling, and layout options
- **Social Sharing**: Built-in social sharing with customization options
- **Image Support**: Featured image support for both content and social media

## Frontmatter Field Explanations

### Required Fields

- `title`: The main title of your post
- `date`: Publication date in ISO 8601 format
- `draft`: Set to `false` to publish, `true` to keep as draft

### SEO Fields

- `description`: Meta description for search engines
- `seo.title`: Custom SEO title (overrides main title)
- `seo.description`: Custom SEO description
- `seo.image`: Image for social media sharing

### Display Options

- `show_reading_time`: Shows estimated reading time
- `featured_image`: Main image displayed with the post
- `excerpt`: Short summary for post listings

### Styling Options

- `post_content_classes`: Content typography ("serif" or "sans-serif")
- `text_color`: Text color CSS class
- `body_classes`: Body element CSS classes

## Usage Tips

1. **Images**: Place images in the `static/images/` directory and reference them in frontmatter
2. **Categories**: Use consistent category names across your site
3. **Tags**: Add relevant tags for better discoverability
4. **Excerpts**: Write compelling excerpts for better social sharing
5. **Drafts**: Use `draft: true` to work on posts before publishing

## Example Customizations

```yaml
# For a personal post
categories:
  - personal
tags:
  - life
  - reflection

# For a technical tutorial
categories:
  - tech
tags:
  - tutorial
  - programming
  - javascript

# For a series post
categories:
  - tech
tags:
  - series
  - part-1
```

This template provides a solid foundation for creating blog posts that work well with the Ananke theme while giving you flexibility to customize the appearance and behavior of each post.
