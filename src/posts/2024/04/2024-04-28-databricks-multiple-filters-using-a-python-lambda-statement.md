---
title: Databricks Multiple Filters using a Python Lambda statement
description: ""
date: 2024-04-28T22:35:26.033Z
preview: ""
draft: false
categories:
  - pinnacle
type: default
excerpt: "Do you use Databricks?  I do.  And I love it.  But sometimes it's hard to filter down a large dataframe to just what you want.  Maybe you want to filter on 11 different columns?  Or 11 different columns with different operators?  Well, I've got a trick for that, and it's pretty elegant."
tags:
  - tech
  - python
  - databricks
author: mike-crowe
seo:
  title:
  description: 
  image: 2024/04/databricks-filtering.webp
images: # relative to /src/assets/images/
  feature: 2024/04/databricks-filtering.webp
  thumb: 2024/04/databricks-filtering.webp
  slide:
---

Recently, I ran into a case where I needed to check if 11 different fields were null.  Yes, I could have used Copilot (or my preferred Codeium) to generate it for me, but I knew it had to be easier.  There had to be an easier way...

Here's the scenario:

- You have a list of conditions in a python list (in my case, I pasted it as separate lines and did a `conditions = """condition 1\ncondition2\n...".split("\n")`).  Doesn't matter how you specify your conditions, just that it's a list somehow
- You have a way of associating this list with a set of Databricks columns

Here's what I found:

- There's a python function [reduce](https://docs.python.org/3/library/functools.html#functools.reduce) in `functools` that takes a list a reduces it down to a result
- You specify _how_ this list is "reduced", such as "and each element of this list together"

Here's how it works.  first, I have an array of `join_columns` which are the common columns between two datasets.  In my setup, each column of `join_columns` maps to the corresponding filter:

```py
conditions = [F.col(join_columns[i]) == filter_cols[i] for i in range(2)]
```

Now, we use the `reduce` function to combine these into a condition for filtering:

```py
condition = functools.reduce(lambda a, b: a & b, conditions)
```

So, in this case, we are saying all these conditions should be `and`'d together -- or rather all of them should match.  Naturally, had I wanted _any of them to match_, this would have have been:

```py
condition = functools.reduce(lambda a, b: a | b, conditions)
```

(the `&` is now a `|`)

That's it--I now have a condition that I can use:

```py
res_df = input_df.filter(condition)
```
