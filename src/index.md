---
# This is a full listing of available Frontmatter options, available for any content (.md) file.
title: Mike's Shiny Objects
layout: page
excerpt: # used for page excerpts and META (will be overwritten if SEO used below)
author: mike-crowe # only displayed on Post lists and detail views. Defaults to _data/meta.authorURL
eleventyNavigation: # Required if want to display in Main Nav Bar
  key: main # "main" is required
  title: Welcome # as it will appear in the nav
  order: 1 # order to display in the nav (index = 1)
seo: # SEO values are used for OG and will overwrite 'title' and 'excerpt' above
  title: Mike's Shiny Objects
  description: Mike's Thoughts, Solutions, Creations and Ah-Ha's
  image: # used for OG:image and Twitter:image. Overrides default set in _data/meta.siteImage
hero: graphic # options: carousel, graphic, video, split (text & image)
heroSettings:
  height:
    mobile: # options = h-1/1 (default = full screen), h-1/2, h-1/3, h-3/4, h-9/10, h-48 (12rem, 192px), h-56 (14rem, 224px), h-64 (16rem, 256px)
    desktop: # leave blank to inherit "mobile" height (default = full screen)
  bg:
    color: # default bg-black
    image: home/hero.webp # relative to /assets/images/
    imagePosition: # options = bg-center (default), bg-left, bg-right
    video: #pixabay-john-macdougall.mp4 # local relative /assets/video/, or full https://... if remote?
    opacityMobile: opacity-50 # options opacity-n, 5, 10, 15, 20, 25, 50, 75, 100 (default)
    opacityDesktop: opacity-75 # Leave blank to inherit opacityMobile, use same options as opacityMobile
  headingText: Mike's Shiny Objects
  headingTextColor: # default = text-white (can use any TailwindCSS text-[color]-[xxx])
  headingTextCase: # default = as typed - options: uppercase, lowercase, capitalize
  subheadingText: |
    <p>Thoughts, Solutions, Creations and things that make me go Ah-Ha</p>
    <hr />
    <p>I'm a Principal Consultant at Pinnacle Solutions Group.  Check out the about page for more details.</p>

    <p>Here, I navigate through the twists and turns of life, exploring topics that intrigue me, provoke thought, or simply bring a smile to my face. Much like the number 42 in Life, the Universe, and Everything, these musings may hold profound significance to some, but most will likely quickly move on because it's too esoteric. Regardless, I invite you to join me on this journey of exploration and discovery. After all, sometimes the most meaningful adventures are found in the unexpected places.</p>

    <p>And yes, the crow theme is a play on my name and the urban legend that crow's like shiny objects.  Of course, it's not really a thing, but it sure feels like it should be.  It does make for a great blog title tho...<p>

  buttonText: My Blog # no button generated if left blank
  buttonURL: /blog/ # full url required. Example: https://thisdomain.com/somepage/
  buttonTextColor: # leave blank to inherit from /src/_data/colors.buttonCustom or buttonDefault
  buttonBgColor: # leave blank to inherit from /src/_data/colors.buttonCustom.bg or buttonDefault.bg
  buttonBgHover: # leave blank to inherit from /src/_data/colors.buttonCustom.bgHover or buttonDefault.bgHover
  buttonBorder: # leave blank to inherit from /src/_data/colors.buttonCustom.border or buttonDefault.border
---


<ol class="pt-4">
{%- for post in collections.post | limit(10) -%}
  <li><a class="underline" href="{{ post.url }}">{{ post.data.title }}</a></li>
{%- endfor -%}
</ol>
