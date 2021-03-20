---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
comments: false
---

Hello Friend!

Welcome to pwnthebox!

This is the place where I write about the stuff I am exploring, stuff I am interested in.

[List of all posts](/2020/11/22/list-of-all-posts.html).

# 8. Systems Security papers and more!

I am planning to read a few papers on Control Flow Integrity, Control Flow Hijacking, Binary Analysis etc., All work related to that will be listed below.

1. [Understanding clang's SafeStack](/papers/2021/03/10/understanding-clang-safestack.html): My attempt to understand the SafeStack security mechanism. I have tried to understand what the mechanism is, what it does and how it is implemented. An emphasis is given on how the mechanism looks like at assembly level. I believe that this is the first step to understand [Code Pointer Integrity](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/kuznetsov).

2. [Writing simple LLVM Passes](/papers/2021/03/19/writing-simple-llvm-passes.html): There are multiple compiler-based security mechanisms out there - StackGuard, SafeStack etc., which are all compiler passes. I had never explored the LLVM project nor had written a pass before. In this article, I try to a few simple passes which read the IR and prints stuff - function names, its return-type, arguments etc.,

# 7. Exploring Rust

## 1. General posts about C and Rust

1 -- [Intro to rustenv](/rust/2020/10/11/intro-to-rustenv.html): If you don't have sudo access to install the rust toolchain or don't want to install it globally, you can use rustenv.
<br/>
2 -- [Rust Startup](/rust/2020/10/11/rust-startup.html): A vanilla introduction to the code that runs before the Rust's main function.
<br/>
3 -- [Primitive Datatypes](/rust/2020/10/25/primitive-types.html): An exploratory journey into Rust's arrays, tuples and integer datatypes. 
<br/>
4 -- [Calling C code from Rust](/rust/2020/10/31/rust-calling-c.html): It is common to have an existing infra written in C/C++ and wanting to write new code in Rust. In such cases, Rust code will have to call C code. This post gives an intro on how it can be done.
<br/>
5 -- [Deciphering Rust's no_mangle](/rust/2020/11/01/deciphering-no-mangle.html): The #[no_mangle] shows some interesting behavior when I was playing around with Rust FFI. Some of it is documented here.
<br/>

## 2. Understanding Event-driven programming and Rust's async/await

From quite some time, I have wanted to explore Rust's async/await feature, the [tokio](https://tokio.rs/) runtime, [Futures](https://docs.rs/futures/0.3.7/futures/), the [async-std](https://github.com/async-rs/async-std) - basically the whole asynchronous part of Rust.

A lot of keywords like synchronous, asynchronous, blocking, non-blocking, promises, futures, event, waiting etc., keep floating around and I am having a hard time understanding it. I have some really stupid doubts like if I don't wait for the I/O I issued, who will wait? Is there someone else waiting for me while I do something else? How will I get notified when that I/O is done? Is a callback registered or is it signal based? Is a new thread spawned which waits for that I/O to happen and joins back once it is done? and many more questions like these. Basically, I have absolutely no clarity over these concepts.

Because of that, I am planning to start with the first time I encountered the word non-blocking I/O - the [O_NONBLOCK](https://www.gnu.org/software/libc/manual/html_node/Open_002dtime-Flags.html) flag which can be passed to the [open()](https://man7.org/linux/man-pages/man2/open.2.html) and eventually reach Rust's async/await concept. In these posts, we will be exploring some interesting system calls like [select](https://man7.org/linux/man-pages/man2/select.2.html), [poll](https://man7.org/linux/man-pages/man2/poll.2.html), [epoll](https://man7.org/linux/man-pages/man7/epoll.7.html), what event-driven means, how it works, does threading play any role etc., I am not sure of the list of things that we might go through because I just know the starting point as of writing this post. Hope is that we will understand what direction we need to go in order to reach Rust's async/await.

One thing about these posts: These posts are not really refined blog posts. They are way more casual. Might have stupid examples and mistakes as well(I have made sure there are no mistakes though. If there are, please let me know). I am trying to understand these concepts and recording these things will help me understand better.

1 -- [What does blocking mean?](/rust/2020/11/08/what-does-blocking-mean.html): Gives an introduction to blocking I/O. Introduces the reader to two problems: Can we serve multiple client connections at the same time? Can we somehow bypass the blocking nature of I/O and use that time to do some useful work?
<br/>
2 -- [Multithreading and multiprocessing](/rust/2020/11/09/multithreading-and-multiprocessing.html): This post explores the first problem introduced in (1) - Can we serve multiple client connections at the same time?
<br/>
3 -- [Is a single thread enough? - Events, Notifications and Event Loop](/rust/2020/11/11/is-a-single-thread-enough.html): Explores the idea of a single thread doing literally everything! We rewrite the server using the select system call and discuss some other concepts like events, notification and event-loop.
<br/>
4 -- [What is polling?](/rust/2020/11/19/what-is-polling.html): Explores the idea of polling. Introduces the concept of **non-blocking** calls along the way. In the end, we implement a single-threaded polling-based server.
<br/>
5 -- [Is a single thread enough? - Exploring the epoll system call](/rust/2020/11/20/is-a-single-thread-enough-epoll.html): TODO
<br/>
6 --[Writing a callback-based event notification library](/rust/2020/11/21/writing-a-callback-based-event-notification-library.html): TODO
<br/>

In the last couple of posts, we explored a lot of things in C. Started with a single request-response server, then made it into a multithreaded server. Then we explored event notification mechanisms like select and poll - wrote an echo server using them. We saw how multiple connections can be handled with a single thread.

With that, we come to the end of event-driven in C. I hope you have a fair idea of what an event is, what an event-loop looks like, what all happens in it. We started off with understanding the blocking problem and then tried to solve or work around it in a number of ways.

The next couple of posts will revolve around Rust. We will again start by implementing an echo server which uses blocking calls, then slowly build on it in the same way we did in C.

7 -- [Simple echo server in Rust](/rust/2020/11/29/simple-echo-server-in-rust.html): An echo server which serves one connection at a time - makes uses of blocking calls.

# 6. Operating Systems and Security

1. [Reverse Engineering and Binary Exploitation Series](/reverse/engineering/and/binary/exploitation/series/2019/03/25/reverse-engineering-and-binary-exploitation-series-mainpage.html): An introduction to OS Security, Assembly Programming, Binary Exploitation, Vulnerabilities and more!

2. [Breaking ASLR](/breaking/aslr/2019/10/30/breaking-aslr-mainpage.html): ASLR is a security technique which helps in mitigating code-reuse attacks, prevents jumping to buffers etc., It basically randomizes the addresses of a process. This is the documentation of my research on ASLR and on attempts to break it.

# 5. Write your own XXXX

[Write your own XXXX: Home](/write/your/own/xxxx/2019/09/10/write-your-own-xxxx-mainpage.html)

One way to understand a concept or a topic is to read about it in great detail. For example, how does a debugger work? Linux provides a system call called ```ptrace``` which helps in tracing any process. The signal ```SIGSTOP``` is used to stop a process which is essentially a break-point, ```SIGCONT``` to continue.

You'll understand how a debugger works at a conceptual level, that signals are used to control the program execution, ```ptrace``` is used to get the trace process's inside information.

Do you want to know how exactly something works? Then write it! Code it up!

This is about the same. Writing your own **anything**. This is the place where I document them. As I write the tool, I'll write how the tool is written, piece by piece. You may use it like a tutorial, or another article about something you want to understand better.

# 4. Computer Networks

1. [Packet Overflow!](/packet/overflow/2019/03/25/packet-overflow-mainpage.html): An introduction to Computer Networks, packets, wireshark, network programming!


# 3. Blogging

1. [Setting up a Blog using Jekyll](/blogging/2019/03/25/setting-up-a-blog-using-jekyll-mainpage.html): A complete tutorial on setting up a blog using Jekyll


# 2. Tools and frameworks

[Tools and Frameworks](/2019/09/19/tools-and-frameworks-mainpage.html): Writeups about some tools I have explored.


# 1. Random Stuff

Here is the non-technical part of this blog. Random stuff, stuff I care about, I would like to rant about and more!

[Link to Random Stuff](/random/stuff/2019/04/28/random-stuff-mainpage.html)

---------------------------------------------------
