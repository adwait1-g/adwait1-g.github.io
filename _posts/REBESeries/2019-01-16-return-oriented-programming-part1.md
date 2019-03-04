---
layout: post
title: Return Oriented Programming - Part1
categories: Reverse Engineering and Binary Exploitation Series
comments: true
---

Hey fellow pwners!

In the previous post, we saw 3 really effective security techniques which the Operating System uses to defend itself against different types of attacks. As we discussed, this and the next few posts will be about trying to defeat those security techniques. 

In this post, I will discuss one of the most exciting exploit methods ever. This exploit method is known as **Return Oriented Programming(ROP)**. This method aims to defeat the **Write XOR Execute** security technique. 

When I first started reading the research paper which described this method, I felt it was out of this world! Thanks to Ryan Roemer, Erik Buchanan, Hovav Shacham and Stefan Savage for coming up with this wonderful exploit method. 

The final goal of this method is simple. One shoule be able to run arbitrary code in the victim's machine with **W XOR X** enabled. 

This is the 14th post of this series. So, create a directory **post_14** inside **rev_eng_series**. 

In will be discussing all the concepts for x86_64 architecture. The concepts remain the same for x86 arch. So, I am sure you guys can also follow. 

Let us get started!

## Pre-requisites

There are 3 essential pre-requisites needed to understand this exploit method. 

# 1. What does rip register do?

**rip** is the **Instruction Pointer(IP)** register. It always **points** to the next instruction to be executed. This means, **rip** has the **address** of the next instruction to be executed. 

There is an exception here. Conside the following assembly code snippet. 

    current instruction:    mov rax, 0x1234
                rip --->    jmp 0x403480
                            inc r15
                            mul rax, r15

The current instruction getting executed is **mov rax, 0x1234**. So, **rip** points to the next instruction to be executed - which is **jmp 0x403480**. 

After **mov rax, 0x1234** is executed, this is the state. 

                            mov rax, 0x1234
    current instruction:    jmp 0x403480
                rip --->    inc r15
                            mul rax, r15

Now look at this.  Current instruction which is getting executed is **jmp 0x403480**. As you can see, this is a **jmp** instruction. So, the next instruction to be executed is the instruction at the address **0x403480**. Just after **jmp 0x403480** is executed, the address **0x403480** is loaded into **rip** because there lies the next instruction to be executed. 

Just before such control instructions are executed, **rip** points to the instruction next to the current instruction being executed. Just after execution, **rip** is changed to appropriate address where the actual next instruction is found. So, be careful when dealing with control instructions like jmp and it's derivatives, call, ret etc., 

Let us modify our definition of Instruction Pointer a little bit. If the current instruction is a non-control instruction, then Instruction Pointer points to the instruction next to the current instruction. If the current instruction is a Control instruction, then Instruction Pointer points to the instruction next to the current instruction just before current instruction is executed. Just after it is executed, the Instruction Pointer points to the appropriate instruction which depends on the control instruction executed. 

This might be confusing. But it is important to understand this. 

This was our first pre-requisite. 

# 2. What is rsp? 

As we know, **rsp** is the register which **points** to the **top of the stack**. It is also called as **Stack Pointer**. 

# 3. How does a function call work ?

We had a detailed discussion of function call mechanism in [this](/reverse/engineering/and/binary/exploitation/series/2018/09/22/program-execution-internals-part-2.html) post. If you are not familiar, it is better to go back and understand this before you move any forward in this post. 

In a nutshell, in 64-bit executables, the first **6** arguments are passed to the function using registers(rdi, rsi, rdx, rcx, r8, r9). If there are more, all the extra ones are put on the stack. The function is called using **call** instruction. The control is returned back to the called function using a **ret** instruction. 

We have now brushed up the required pre-requisites. Now, lets get right into ROP. 


## About ROP

The bottom-line is, how do we bypass W XOR X? Let us list the things we have to deal with because W XOR X is enabled. 

1. Cannot execute code in any **rw-** address spaces.

    * If we have a BOF, we can definitely inject code, but executing it is impossible.       





2. What we can make use of is some stuff in the **r-x** address spaces. These are executable address spaces, full of code. If at all we have to execute some instructions and we find those instructions in these executable address spaces, we can use Control Flow Hijacking to execute those instructions. Note that because of BOF, we can jump to literally **any** address in the address space. 

    * There are multiple executable address spaces. Few of them are the process's text segment, shared libraries' executable address space, dynamic linker's executable address space. Write a program and look at it's **/proc/PID/maps** file to see all the executable address spaces. 

When we used Code Injection, we injected standard shellcode to get a normal shell. We injected the reverse-tcp shellcode to control the victim's system from remote. So, essentially we could execute anything because we could inject anything and execute it. So, we had a lot of fun executing whatever we wanted, got higher privileges etc., 

But because of W XOR X, all that fun and power is snatched from us :( . All we got is the executable parts of the address space, code present there which we can use if we want. 

So, can we get back our power from this? Can we get a shell in this constrained environment?

ROP is the answer to this. Yes. We can get a shell. 

ROP makes use of the code present in the executable address spaces of a process. It does not inject any new code because that is not helpful. As it **re-uses** the code present in the process's address space, ROP is classified as a **Code Reuse Exploit Method**. 

Let me explain this again. There is a lot of code(machine code) present in a process's address space. There is the text segment, which is the code we wrote in C(or any high-level compiled language) and then got converted to machine code. There is the complete Standard C library, the **libc** in it. It also has the dynamic linker, the **ld.so** which takes care of multiple things like dynamic linking, interpreting instructions etc., So, there is a lot of code. All this code is present to perform or help in performing tasks specified by the programmer. This is their **primary** reason. All this code is present to help complete the task programmed by the programmer. 

We instead are using parts of this code to make our exploit ready. ROP uses small code snippets in this huge sea of code to prepare the exploit. This is **re-using** code to make our exploit. That is why this exploit method belongs to the class of **Code reuse exploit methods**. I hope this is clear. 

## Basics of ROP

The above section was a superficial coverage of what ROP is. In this section, let us get into the crux of ROP. 

It is a question that drives this exploit method. The question is this: **"Can we write programs with rsp as the Instruction Pointer?"** . 

Let us think about this. Normally, **rip** register is the Instruction Pointer of the program when executed. Can **rsp** do the job of an Instruction Pointer is the question. 

This will give rise to a lot of questions. I feel the 3 obvious ones are: 

1. Why was **rsp** chosen and not any other register?
2. How will programs look if **rsp** is the Instruction Pointer?
3. Will this help in defeating W XOR X and get a shell?

Let us take up question 2 first. The answer to that will automatically answer question 1 and 3. 

### How will programs look like if rsp is the Instruction Pointer?

Before we even get to this question, we must check if **rsp** can even be the Instruction Pointer. That is, can **rsp** point to an instruction that will get executed next. 

We have to understand the fact that **rsp** is the Stack Pointer and not the Instruction Pointer. So, **rsp** cannot behave like an Instruction Pointer magically. We have put in some external effort and make rsp **behave** as the Instruction Pointer. 

Let us see what properties of **rsp** we can exploit to make this possible. An Instruction Pointer will always point to the instruction next to the current instruction. When do you think **rsp** points to an Address of an instruction? We have seen that it points to an Address of an instruction just before **ret** of a function is executed and control is transferred to the instruction at that address. So, at that moment, rsp actually behaved as an Instruction Pointer. 

Let us take a closer look at this. **rsp** points to an Address just before **ret** instruction is executed. Just after **ret** is executed, control is transferred to the instruction pointed by that address. Think about it. Instead of ret, suppose you had a mov or a call, would **rsp** behave as an Instruction Pointer?

It behaved as an Instruction Pointer because of the **ret** instruction. 

This is a very important observation we have made. **rsp** can be made to behave as an Instruction Pointer with the help of **ret** instructions. Place an address at the top of the stack - rsp is pointing to that address. Then execute a **ret** instruction. Automatically, control is transferred to the instruction at that address. I hope you can see why this exploit method is named **Return Oriented Programming**. The complete exploit is driven by ret instructions. It is not a paradigm of programming, but a one of a kind exploit method.

Another thing to note is that **rsp** is incremented by 4 bytes once **ret** is executed because the stack is popped once. 

From here, we will slowly build on this observation we have made. 

What we have achieved so far is: given an address, we can overwrite the ReturnAddress of that vulnerable function with this address and execute instructions present at that address. This is the instance where rsp is behaving as the Instruction Pointer. Note that these addresses I am talking about can belong only to the executable address spaces of the process. 

What we want is a bit more advanced that this. We want is a shell - that is an execve system call. Let us consider executing the **exit** system call for now. **exit** system call is this: 

    mov rax, 0x1
    mov rbx, 0x0
    int 0x80

Remember that ROP is about using code snippets already present in the executable address spaces of the process. I have the vulnerable program with me. Now, I have to execute these 3 instructions one after the other. 

What we saw is that we can execute instructions at a particular address by overwriting the vulnerable function's ReturnAddress with that address. So, if we find machine code of **mov rax, 0x1** somewhere in the address space, we will be able to execute it. 

Suppose we found it at **addr0**. We can overwrite the ReturnAddress of the vulnerable function with **addr0** and execute **mov rax, 0x1**. This is how the stack states would look like:  

    |     addr0     |  <--Actually ReturnAddress of vulnerable function     |               |
    |               |                                                       |               |
    |               |       ret(of vulnerable function)                     |               |   + Code at addr0 is executed
    |               | ----------------------------------------------------> |               |
    |               |                                                       |               |
    |               |                                                       |               |


Now, we are 1 instruction through. We have 2 more to go. One problem with this is that after **mov rax, 0x1** is executed, all instructions after **mov rax, 0x1** are also executed, which is not needed. So, we should see that right after **mov rax, 0x1** is executed, the execution should ideally be passed to **mov rbx, 0x0** instruction. How do we do that? Suppose **mov rbx, 0x0** is found at **addr1** Address in the address space. 

    rsp---->|     addr0     |                               rsp---->|     addr1     |
            |     addr1     |                                       |               |
            |               |   ret(of vulnerable function)         |               |
            |               |  --------------------------------->   |               |  + Code at addr0 is executed. 
            |               |                                       |               |
            |               |                                       |               |

                 Stack1                                                  Stack2

Consider the stack setup like Stack1. Code at **addr0** anyway gets executed - It is evident from the above stack diagrams. What we need to execute is code at **addr1** - **mov rbx, 0x1**. Consider Stack2. **rsp** points to **addr1** because when **ret** is executed, the **rsp** is incremented by 4 bytes(because of the pop action) . What do we need if we want code at **addr1** is executed? Yes. We will need a **ret** instruction. This is the observation we made a while ago. So, we want **rsp** to behave as Instruction Pointer again. How do we do it? simple, execute an ret instruction. 

When should the **ret** instruction get executed? What we want is **mov rax, 0x1** is executed and right after that, we want **mov rbx, 0x0** to be executed. So, we will need the **ret** instruction just after **mov rax, 0x1** instruction. So, essentially the following will be happening. 


    rsp---->|     addr0     |                               rsp---->|     addr1     |                                       |               |
            |     addr1     |                                       |               |                                       |               |
            |               |   ret(of vulnerable function)         |               |    ret(present after mov rax, 0x1)    |               |
            |               |  --------------------------------->   |               |   ------------------------------->    |               | + Code at addr1 is executed.
            |               |                                       |               |                                       |               |
            |               |                                       |               |                                       |               |        

                                                                 + + Code at addr0 is executed   

                 Stack1                                                  Stack2


So, our conclusion from this exercise was that just finding **mov rax, 0x1** instruction in the executable address spaces is not enough. We instead have to find **mov rax, 0x1; ret**. The instruction we want to execute followed by a ret instruction. This **ret** instruction makes sure **mov rbx, 0x0** is executed because **addr1** is pointed by **rsp** in Stack2. 

Now, we have executed **mov rbx, 0x0**. We need to execute one more instruction - **int 0x80**. What do we do? Simple. We repeat the same steps. 

Finding **mov rbx, 0x0** is not sufficient because there should be an **ret** instruction to make **rsp** behave as an Instruction Pointer. So, we have to find **mov rbx, 0x0; ret**. Once we have found, we have to setup the stack in the following manner. Assume **int 0x80** is present at **addr2**. 

    addr0:  mov rax, 0x1
            ret

    addr1:  mov rbx, 0x0
            ret

    addr2:  int 0x80




    rsp---->|     addr0     |                               rsp---->|    addr1      |                               rsp---->|    addr2      |
            |     addr1     |                                       |    addr2      |                                       |               |
            |     addr2     |   ret(of vulnerable function)         |               |   ret(next to mov rax, 0x1)           |               |
            |               |  ---------------------------------->  |               |  --------------------------------->   |               |
            |               |                                       |               |                                       |               |
            |               |                                       |               |                                       |               |

                                                                  + (mov rax, 0x1) is executed                             + (mov rbx, 0x0) is executed. 



                                        |               |
                                        |               |
           ret(next to mov rbx, 0x0)    |               |
        ---------------------------->   |               |
                                        |               |
                                        |               |
                                      
                                      + (int 0x80) is executed. 

At this point, do not worry about the presence of these gadgets in an executable. Assume all these are present.

What we can conclude from the above discussion is that finding machine code of the instructions we want is **not** sufficient. We need machine code of the instruction followed by an **ret** instruction. This is to ensure **rsp** remains to be the Instruction Pointer throughout.  

There are a few points to be noted. 

1. The code snippets ending with **ret** instructions are called **ROP-Gadgets** or just **Gadgets**. So, when **rsp** is made to behave as the Instruction Pointer, the program is not a sequence of simple instructions. It is a sequence or a **chain** of ROP-Gadgets.

2. Just finding the required ret-ending code snippets is not enough. The most important thing is to set up the stack in the right manner. We wanted to execute the gadgets in the following manner: **mov rax, 0x1; ret** , **mov rbx, 0x0; ret**, **int 0x80**. So, the stack should have addresses in that order: **addr0**, **addr1**, **addr2**. 

So, this was a very simple example of ROP. I hope you have understood the basics of ROP. 

Now, let us get back to the 3 questions which we had before we started the above discussion: 

1. Why was **rsp** chosen and not any other register?
2. How will programs look if **rsp** is the Instruction Pointer?
3. Will this help in defeating W XOR X and get a shell?

We have seen how programs look like if **rsp** is the Instruction Pointer. The program is a chain of ROP Gadgets. So, we have a comprehensive answer to question2. 

**Question1** : Why was **rsp** chosen and not any other register?

**rsp** behaves like an Instruction Pointer at the end of every function call when **ret** is executed. This was extended to execute the instructions we want by searching and chaining ret-ending code snippets. This is by no means proof for not using any other register. But it just shows rsp is best for this.

**Question3** : Will this help in defeating W XOR X and get a shell?

In the above explanation, we executed the exit system call when W XOR X was enabled. We did not inject code or anything like that. So, this proves that W XOR X was defeated in this example. Can we get a shell? This is what we have to discuss. We executed the **exit** system call by chaining those gadgets. But there are a few things we assumed for the ease of explanation. They are 

1. We just told "find" the gadgets. Is there any algorithm to find them? We didn't talk about it. 

2. We didn't actually search for those gadgets in an executable file. We just explained it in a conceptual manner. So, it might so happen that we don't find the required gadgets. What are required are **mov rax, 0x1; ret**, **mov rbx, 0x0; ret**, **int 0x80**. What if we didn't find these gadgets?

Exploring these 2 points will give the answer for Question3. 

We are left with Question3. Let us take this up in the next post. 

With that, let us end this post. 

# Comclusion

We could have discussed ROP by just taking examples, tools available. But I felt that is not the right way to introduce ROP to someone. The right way to introduce ROP to someone is to describe how it was designed.

In case you have any doubts, leave a comment below. 

We just got an introduction to ROP in this post. In the next post, we will see how to find the gadgets, what to do if we did not find the right gadgets and other issues and most importantly, do some practicals!

That is it for this post. I learnt a lot while writing this post. Hope you did too. 

Thanks for reading :)

-------------------------------------------------
[Go to next post: Return Oriented Programming - Part2](/404.html)       
[Go to previous post: Defeating Write XOR Execute! - Ret2Libc - Part1](/reverse/engineering/and/binary/exploitation/series/2019/03/04/return-to-libc-part1.html)









