---
layout: default
comments: false
order: 1
---

Hello!

I am Adwaith. I am a business student at the [ESCP Business School](https://escp.eu/programmes/master-in-management), Europe. I am part of the [PGDM-IB](https://www.mdi.ac.in/programmes/post-graduate-diploma-in-management-international-business-pgdm-ib) programme at the [Management Development Institute, Gurgaon](https://www.mdi.ac.in/), India. I recently finished my spring semester at ESCP's Berlin campus and currently spending the summer interning as an Analyst at a business consulting startup.

I spent my first two semesters spending time exploring different fields in management. In the previous semester, I spent some time understanding that a lot of IT, AI, ML, Information Systems is used in the field of management, this was through a specialization I took at ESCP Berlin. There seems to be bunch of topics that are a neat intersection of Computer Science, Mathematics and Management. There is a lot of efforts going into using technology and building better management systems. For example, highly sophisticated Decision Support Systems used by today's managers are purely an innovation at this intersection, Quality Control is a facet of Operations Management, Industrial Image Processing and Computer Vision is a great field to explore in the field of Quality Control in Manufacturing, or how Business Process Management is part of Information and Operations Management, Process Mining is a leading way to work with Business Processes, or the proposal of the idea of Physical Internet, which is based on the design and architecture of Digital Internet. I can go on and on about this beautiful intersection, and I would like to explore something on these lines. This is what interests me these days. I plan to write about this in near future.

## Latest Posts

<ol>
{% assign total = site.posts | size %}
  {% for post in site.posts %}
    <li>
      <strong>{{ total | minus: forloop.index0 }}</strong>.
      <span>{{ post.date | date: "%Y, %B %d" }} - </span>
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
      
    </li>
  {% endfor %}
</ol>