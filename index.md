---
layout: default
comments: false
order: 1
---

Hello!

I am Adwaith. Welcome to my space. I am an aspiring management researcher/analyst. There are many subjects that have caught my attention - cybersecurity and computer systems during my bachelors, I rode that wave for good 6-7 years with all my excitment, have written quite a bit on it [here](/cybersecurity/). These days I am into all things management. Small businesses are my latest fascination.

All

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
