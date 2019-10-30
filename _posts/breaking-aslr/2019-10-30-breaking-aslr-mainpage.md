---
layout: page
title: Breaking ASLR
categories: Breaking ASLR
---

**Address Space Layout Randomization** is a security technique put in place to mitigate several types of code-reuse attacks like **Return-to-Libc**, **Return Oriented Programming** or just the idea of jumping to a particular place in the memory layout. 

ASLR was implemented in 2001, but research is still going on to break it. Looks like we are dealing with one hell of a security technique here.

This series is about my research on ASLR. It starts with what ASLR is and goes indefinitely. Ideal goal is to devise a definite method to break ASLR. This goal has motivated me to research more about ASLR.

If you are new to Operating System Security, Exploit development, you can refer to my [Reverse Engineering and Binary Exploitation Series](https://www.pwnthebox.net/reverse/engineering/and/binary/exploitation/series/2019/03/25/reverse-engineering-and-binary-exploitation-series-mainpage.html) and then come back to this series.

Lets get started!
