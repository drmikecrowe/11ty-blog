---
title: Dynamic Databricks Widgets
description: ""
date: 2024-05-04T16:25:19.053Z
preview: ""
draft: true
categories: []
type: default
excerpt: "Dynamic Databricks Widgets is a common problem, especially when working in Databricks. Changing one widget can lead to others adjusting in response. That can be a bit tricky, but it's not hard. Here's the secret: the widgets must be replaced as they change! For example, let's say you have a date input, and whenever it changes, you want a second widget to change. That second widget needs to be suffixed with an increasing number as the contents change."
tags:
  - tech
  - python
  - databricks
author: mike-crowe
seo:
  title:
  description: 
  image: 2024/05/databricks-widgets2.png
images: # relative to /src/assets/images/
  feature: 2024/05/databricks-widgets2.png
  thumb: 2024/05/databricks-widgets2.png
  slide:
---

Have you ever wished the Databricks widgets were a little more intelligent?  When you change one, the others adjust?

That's not too hard, but it's a bit tricy.  Here's the secret:  The widgets must be replaced as they change!  For example:

Let's say you have a date input, and whenever it changes, you want a second widget to change.  That second widget needs to be suffixed with an increasing number as the contents change.  Consider:

```py
    if interest_date != last_interest_date:
        try:
            dbutils.widgets.remove(f"issue{index1}")
        except:
            pass
        index1 += 1
    dbutils.widgets.dropdown(f"issue{index1}", "", ...)        
```

You need the try/catch the first time thru because the remove will fail.  Et Voila, changing widgets.

Here's a functioning example:

```py
interest_dates = {
    "20230730": [
        {"issue_name": "Issue 1", "upcs": ["1234", "5678"]},
        {"issue_name": "Issue 2", "upcs": ["9876", "5432"]},
    ],
    "20240114": [
        {"issue_name": "Issue 3", "upcs": ["1111", "2222"]},
        {"issue_name": "Issue 4", "upcs": ["3333", "4444"]},
    ],
}

last_interest_date, last_issue = (None, None)
index1, index2 = (1, 1)
dbutils.widgets.removeAll()


from random import sample
from time import sleep

keys = sorted(list(interest_dates.keys()))

dbutils.widgets.removeAll()
dbutils.widgets.dropdown(
    "date", "", [""] + [str(k) for k in sorted(interest_dates)], "1. Date"
)
interest_date = dbutils.widgets.get("date")
if interest_date:
    if interest_date != last_interest_date:
        try:
            dbutils.widgets.remove(f"issue{index1}")
            dbutils.widgets.remove(f"upc{index2}")
        except:
            pass
        index1 += 1
        index2 += 1
        last_interest_date = interest_date

    dbutils.widgets.dropdown(
        f"issue{index1}",
        "",
        [""] + [k["issue_name"] for k in interest_dates[interest_date]],
        "2. Issue",
    )
    issue = dbutils.widgets.get(f"issue{index1}")
    if issue:
        if issue != last_issue:
            try:
                dbutils.widgets.remove(f"upc{index2}")
            except:
                pass
            index2 += 1
            last_issue = issue
        current_issue = [
            k for k in interest_dates[interest_date] if k["issue_name"] == issue
        ].pop(0)

        dbutils.widgets.dropdown(
            f"upc{index2}",
            "",
            [""] + current_issue["upcs"],
            "3. UPC",
        )
        upc = dbutils.widgets.get(f"upc{index2}")
        if upc:
            displayHTML(f"You selected: <b>{upc}</b>")
```