---
layout: page
title: C, Rust and more!
categories: rust
---

All the code used/written in the posts are present in [this repository](https://github.com/adwait1-G/Rust-C-Experiments).

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
<br/>

To be continued.