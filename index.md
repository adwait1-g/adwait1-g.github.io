---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
comments: false
---

Hello Friend!

Welcome to pwnthebox!

This is the place where I write about the stuff I am exploring, stuff I am interested in.

# Reverse Engineering and Binary Exploitation Series

[Link to Reverse Engineering and Binary Exploitation Series](/reverse/engineering/and/binary/exploitation/series/2019/03/25/reverse-engineering-and-binary-exploitation-series-mainpage.html) 

This is a series of articles on Reverse Engineering and Binary Exploitation. The first few articles will help you reverse engineer small programs using gdb, objdump, readelf. Most of the articles focus on Binary Exploitation. As of now, I have written about the famous Buffer Overflow vulnerability, different methods to exploit like Traditional shellcode Injection, Return-To-Libc, Return Oriented Programming in detail with hands-on examples. I will be discussing different vulnerabilities like Format String vulnerability, problems with GOT and PLT(dynamic linking). I also plan to discuss how presence of more than one vulnerability can help us rip apart the Operating System's security measures with the help of these exploits.

Though these are old vulnerabilities, they are still found in embedded systems(outdated kernels), even if firmware updated, the security feature is kept off for god knows what reason. There are lot of such possibilities. Many routers lack basic security measures like ASLR, DEP, RELRO which can make them too vulnerable to exploits we discuss. 

This is basically a red-team approach to Operating Systems Security.

Happy pwning!
           
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

Happy Networking!

# moloch

[moloch](https://molo.ch) is a system which can used for large scale, indexed packet capture and search. What this means is, it can capture, store and retrieve(on search) a large number of packets. The [website](https://molo.ch) describes the system in detail. It is opensource! You can read it's sourcecode [here](https://github.com/aol/moloch). The README of the github repo is amazing. It gives a overview of the system.

The following are a few articles about moloch. 

1. [Installing moloch](/moloch/2019/05/22/installing-moloch.html): I spent a lot of time to get it working. So, I thought I can list the procedure and a few places I spend time figuring it out.

A lot more coming up!

# Blogging

### Setting up a Blog using Jekyll

[Link to Setting up a Blog using Jekyll](/blogging/2019/03/25/setting-up-a-blog-using-jekyll-mainpage.html)

I was using WordPress for 6 months after I started my blog and then migrated to GitHub Pages. I have written 2 articles on how to completely migrate to GitHub Pages.

Happy blogging!

# Random Stuff

[Link to Random Stuff](/random/stuff/2019/04/28/random-stuff-mainpage.html)

This is literally random stuff. Just something I think about sometimes. There might be stuff which might trigger you. Read it at your own discretion. 

---------------------------------------------------
