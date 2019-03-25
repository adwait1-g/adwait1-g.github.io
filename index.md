---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
comments: false
---

# Why I started this blog?

[Why I started this blog?](/why/i/started/this/blog2018/06/11/why-i-started-this-blog.html)

# Reverse Engineering and Binary Exploitation Series

[Link to Reverse Engineering and Binary Exploitation Series](/reverse/engineering/and/binary/exploitation/series/2019/03/25/reverse-engineering-and-binary-exploitation-series-mainpage.html) 

This is a series of articles on Reverse Engineering and Binary Exploitation. The first few articles will help you reverse engineer small programs using gdb, objdump, readelf. Most of the articles focus on Binary Exploitation. As of now, I have written about the famous Buffer Overflow vulnerability, different methods to exploit like Traditional shellcode Injection, Return-To-Libc, Return Oriented Programming in detail with hands-on examples. I am planning to write 1 or 2 more articles on Return Oriented Programming because I just finished a project related to it and I have a lot to write about. 
Once that is done, I will be discussing different vulnerabilities like Format String vulnerability, problems with GOT and PLT(dynamic linking). I also plan to discuss how presence of more than one vulnerability can help us rip apart the Operating System's security measures against these attacks. 

Though these are old vulnerabilities, they are still found in embedded systems(outdated kernels), even if firmware updated, the security feature is kept off for god knows what reason. There are lot of such possibilities. Many routers lack basic security measures like ASLR, DEP, RELRO which can make them too vulnerable to exploits we discuss. 

This is basically a red-team approach to Operating Systems Security.

           
# Packet Overflow!

[Link to Packet Overflow!](/packet/overflow/2019/03/25/packet-overflow-mainpage.html)

Packet Overflow! is a new series of articles I am starting to understand Computer Networks better.

In this series, we are going to have fun playing around with packets, capturing them, dissecting and analyzing them, understanding the different Networking Protocols used. It is going to be a hands-on series with a bit of theory.

We will be doing 3 things very frequently in this series.

1. Writing simple network programs
2. Capturing packets using a tool like Wireshark which will help us analyze them.
3. Read RFCs(Request For Comments) to understand the protocol better.

Let us start with covering some important pre-requisites.

In the first few posts, I will be introducing Network Programming and Introduction to Wireshark. Once it is done, we are ready to start our journey with packets!

# Blogging

### Setting up a Blog using Jekyll

[Link to Setting up a Blog using Jekyll](/blogging/2019/03/25/setting-up-a-blog-using-jekyll-mainpage.html)

I was using WordPress for 6 months after I started my blog and then migrated to GitHub Pages. I have written 2 articles on how to completely migrate to GitHub Pages. 

