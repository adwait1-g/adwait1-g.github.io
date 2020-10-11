---
layout: page
title: Rust-C-Experiments
categories: Rust
---

# Rust-C Experiments

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
