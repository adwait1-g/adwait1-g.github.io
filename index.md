---
layout: default
comments: false
order: 1
---

Hello!

Welcome to my space. I am Adwaith, I am an aspiring researcher/analyst. There are many subjects that have caught my attention - cybersecurity and computer systems during my bachelors, I rode that wave for good 6-7 years with all my excitment, have written quite a bit on it [here](/cybersecurity/). I have been interested in management and economics in the last 2-3 years. These days I try to read interesting economics publications and reports, write summaries of it, reproduce/implement the results, do comparisons and so on.

My favorite quote:

```
In God we trust, all others must bring data.

-- W. Edwards Deming
```

You may find all the posts below.

## Latest Posts

<ol>
{% assign total = site.posts | size %}
  {% for post in site.posts %}
    <li>
      <span>{{ post.date | date: "%Y, %B %d" }} - </span>
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
      
    </li>
  {% endfor %}
</ol>

Disclaimer: Its all me, anything written here doesn't represent the views/policies of any of my employers (previous, current, future). Cheers!
