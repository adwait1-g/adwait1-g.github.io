---
layout: page
title: C, Rust and more!
categories: Rust
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

# What is this about?

Whenever C code is written, you can visualize the type of assembly code the compiler emits - unless you use some of the really aggressive optimizations out there. It gives you that transparency/visibility of how the code looks like at runtime. This way, you know the cost of certain piece of code for sure. For me, cost is the amount of assembly code emitted when certain piece of code is compiled. C generates code which just does the job - nothing more, nothing less. That is because there is no syntactic sugar hiding complex code, no hidden abstractions. What you write is what is going to run.

Now coming to Rust.

I have been using Rust for about 6-7 months(as of 11 Oct 2020) and I can say I am slowly getting used to Rust concepts like ownership, borrowing, the awesome borrow checker, the strictness of the compiler in general. Unlike C, Rust provides a lot of abstractions. Starting from the simple ```usize```, ```iter()``` for arrays/vectors to high-level abstractions like async/await where code boils down to a state machine - and a lot of other features/abstractions I don't know about. Just by looking at the code, I am finding it hard to tell what the assembly code looks like - because of the abstraction and my lack of expertise in the language. Let me give you an example to make myself more clear.

Consider the example of array element access. When you say ```x = arr[index]```, let us see what happens in C and in Rust.

In C, it would emit assembly code like the following.
```asm
; Assuming that arr is a uint64_t array.
; rbx has the base address of arr.
; rcx is the index
; rdx has the address of variable x

mov rax, qword[rbx + rcx * 8] 
mov qword[rdx], rax
```

When you write that line of code, you know that it would look like this at assembly level. But in Rust, the same would look like this.

```asm
; Assuming that arr is a uint64_t array.
; Assume size of arr is 20
; rbx has the base address of arr.
; rcx is the index
; rdx has the address of variable x

; First checks if the index is less than size of array
cmp rcx, 20
jge panic   ; This is the rust's panic.

; If we are here, it means the index is in-bounds.
mov rax, qword[rbx + rcx * 8]
mov qword[rdx], rax
```

Yes. There is bound-checking code before you access it.
The instructions used for bound-checking is slightly different - which will be covered in one of the posts, but the above is the gist. I like the fact that the bound-checking code is clear and straight-forward. It cannot get any better. The same code would look like the following in C.

```c
assert(index < 20);
x = arr[index];
```

It would panic(or in C terms seg-fault) if that assertion fails. Just imagine writing that ```assert()``` for each and every array access you make. Rust does that for you. But there are a lot of obvious cases where you know for sure that you won't go beyond bounds. In C, you have a choice of not putting that assert. Is there a choice in Rust?

Now an array access in Rust is deciphered for me. I know the type of code emitted when an array element is accessed. This is a piece of language internals you know now. But can you use this knowledge somewhere?

Suppose you are iterating through the array ```arr```. In C, it would look like this.
```c
for(i = 0; i < 20; i++)
{
    printf("%d\n", arr[i]);
}
```

In Rust,  we might write it like this.

```rust
for i in 0..20
{
    println!("{}", arr[i]);
}
```

Now we know what happens here. There is bound-checking code(those two extra instructions) for every access - there is a compare and branch-miss for every access. Now the question is, is there any way to reduce this cost? Of course there is. The following code works.
```rust
for arr_val in arr.iter()
{
    println!("{}", arr_val);
}
```

Iterators! We can use these. But how does the assembly code for this look like? What exactly does ```iter()``` do? What is its cost? For starters, the code doesn't have bound-checking code. In the second case, the compiler knows that we are iterating through the array - the compiler makes sure we don't go beyond the valid bounds. In the first case, the compiler doesn't know we are iterating through the array. We are simply running a loop from 0 to 19 and doing an array element access(which is separate)- that is why runtime code is needed to check array-index bounds.

There is one problem. If we use the ```iter()``` way, we can't assign values to array elements. For that, we can use ```iter_mut()``` and dereference ```arr_val```. But at what cost does that come? How does it look like at runtime?

I hope you get the point. These are the type of insights I want to get out of these analyses. It is an attempt to understand the language better and use the right constructs for a task.

First of all, In C, there are a bunch of constructs we keep using again and again - I want to checkout those constructs in Rust. Compare them with the C emitted assembly code, see the difference, see what less/extra it is doing, reason out. In the end, I should be able to visualize the assembly code emitted by the rust compiler.
