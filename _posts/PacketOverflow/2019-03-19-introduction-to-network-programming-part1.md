---
layout: post
title: Introduction to Network Programming - Part1
categories: Packet Overflow
comments: true
---

Hello everyone!

In the previous articles ([article1](00/packet/overflow/2019/02/01/operating-system-and-networking-stack-part1.html) and [article2](/packet/overflow/2019/02/01/operating-system-and-networking-stack-part2.html)), we discussed what a networking stack is, what TCP / IP stack is, different layers in it, why the stack is the way it is. 

In all modern machines, there is a Networking stack by default. It means that all those machines have necessary hardware and software required to get connected to a network.

In this article, we will use that Networking Stack and write programs which will talk to each other over a network.

## 1. How do we use the Networking Stack?

We want to write programs which make 2 machines communicate to each other over a network. Such programs are called **Network Programs**. 

To make that happen, there is the Networking Stack present in the Operating System. 

To make use of the facilities offered by the Operating System, we can use **System Calls** 