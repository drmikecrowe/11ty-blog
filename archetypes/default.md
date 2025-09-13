---
# Basic Content Information
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
description: "Brief description of your blog post for SEO and social sharing"
date: {{ .Date }}
draft: true

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
