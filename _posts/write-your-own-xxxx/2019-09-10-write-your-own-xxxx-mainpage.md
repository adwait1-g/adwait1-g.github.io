---
layout: page
title: Write your own XXXX
categories: Write your own XXXX
---

One way to understand a concept or a topic is to read about it in great detail. For example, how does a debugger work? Linux provides a system call called ```ptrace``` which helps in tracing any process. The signal ```SIGSTOP``` is used to stop a process which is essentially a break-point, ```SIGCONT``` to continue.

You'll understand how a debugger works at a conceptual level, that signals are used to control the program execution, ```ptrace``` is used to get the trace process's inside information.

Do you want to know how exactly something works? Then write it! Code it up!

This is about the same. Writing your own **anything**. This is the place where I document them. As I write the tool, I'll write how the tool is written, piece by piece. You may use it like a tutorial, or another article about something you want to understand better.

## 1. elfp: An ELF parsing library

[elfp: An ELF parsing library](/write/your/own/xxxx/2019/11/15/elf-parser-home.html): The **Executable and Linkable Format** is one of the most complex file formats I have come across till now. Every executable, library, object file in all UNIX-like systems are in this format. To understand this file format properly, I'll write a simple ELF-Parser, where I break-open a given ELF file, disect it into it's constituent components and dump them in human-readable form.

