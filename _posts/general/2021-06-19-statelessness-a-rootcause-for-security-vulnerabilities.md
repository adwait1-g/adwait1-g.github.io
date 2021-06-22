---
layout: post
title: Statelessness - Rootcause of many Security Vulnerabilities
categories: general
comments: true
---

Hello friend,

Whenever a vulnerability like the Buffer Overflow Vulnerability(BOF) is present in a software, there are a variety of ways to exploit it and take control of the system. A few well known exploit methods are Shellcode injection, Return-to-Libc, ROP(Return Oriented Programming), SROP(Sigreturn Oriented Programming) and its other friends. The main problem here is the BOF - the attacker somehow has control over the Instruction Pointer and can hijack the control flow. That is all the BOF gives an attacker. But how he exploits it is completely left to him and might use any of the techniques listed above or use a completely new technique to get a shell.

The BOF is just used as an enabler/starter for the exploit methods to work. If we go deeper into each of these exploit methods, we can find that each of these methods exploit yet another vulnerability in the system to achieve the objective. Let us call these vulnerabilities **sub-vulnerabilities**.

Let us take a simple example to understand the concept of sub-vulnerabilities. Consider the Shellcode Injection exploit method. The attacker wants to execute some shellcode on a vulnerable application and get a shell. The necessary condition for this exploit method to work is control over the Instruction Pointer. The presence of a classic Stack-Overflow vulnerability satisfies the necessary condition. But is this enough for the Shellcode Injection method to work? Are there any other conditions to be satisfied for Shellcode Injection to work? Ofcourse. The Stack must be **executable**.

Generally, the stack the place where we place data - so it is writable and readable. But assume for some reason, the stack for this vulnerable application is executable as well. Now, the Shellcode Injection exploit method has a chance to work. In other words, the stack being executable is a vulnerability in itself. One may not be able to exploit it directly, but when there is already an enabler vulnerability(like BOF), an executable stack can prove itself dangerous.  am calling such a vulnerability as a sub-vulnerability.

There are many such sub-vulnerabilities in different types of software. Not just software, sub-vulnerabilities can be present in protocols as well - as design flaws. Suppose a vulnerability is present, it might enable the attacker to exploit a design flaw - which is probably is not exploitable in the first place without the enabler.

We now understand vulnerabilities and sub-vulnerabilities. Let us go one step further. What might be the root cause of such vulnerabilities? It could be just about anything. It could be an implementation problem. It could be a design problem. Or it could be a concious design based on a fundamentally problematic concept. Problematic does not mean flawed. It could give rise to problems and open up vulnerabilities under certain conditions. To understand this better, let us take the example of ARP.

## 1. Address Resolution Protocol (ARP)

# 1.1 Need for ARP

Consider a network of boxes connected to each other through a switch. Physically, an Ethernet cable connects the machine to the switch - like this, all the machines are connected. Each machine is given an IP Address (say statically configured). Each machine has one Ethernet NIC and it has a unique Ethernet Address.

Suppose Box-A (IP: 10.10.10.2) wants to talk to Box-B(IP: 10.10.10.3) - this means a program in Box-A wants to talk to another program in Box-B. How will this communication happen? Let us consider the construction and journey of a packet from Box-A to Box-B. Assume that a a telnet server is listening on Box-B. A telnet client is run in Box-A which is instructed to connected to Box-B.

1. **telnet** is an Application Layer protocol. It will have its own application data. This data goes to the Transport Layer - here, the TCP layer.
2. The TCP layer adds its header. The source-port will be some port given to the telnet client by the OS(assuming that it does not bind itself to a port). The destination-port is 23 - this is the default telnet listening port. This segment is sent to the next layer - the Internet Layer.
3. The IPv4 Layer adds its header with source-address as 10.10.10.2 and destination-address as 10.10.10.3. The packet is sent to the next layer - the Ethernet Layer.
4. Now, this layer should add the Ethernet header. It knows the source Ethernet address - which is the Box-A's Ethernet address. Assume that it is 11.22.33.44.55.66. Now, comes the interesting part. What is the Destination Ethernet address? We conceptually know that it is Box-B's Ethernet Address (let it be 11.22.33.44.55.67). But the TCP/IP stack in Box-A is **not aware** of it. Also note that this is the most crucial piece of information - without which the data cannot be transported to Box-B. What do we do? How do we get Box-B's Ethernet Address?

**Enter ARP**. What it does is in its name: It resolves the Internet Address to give Hardware/Ethernet Address. So IF you have Box-B's IP Address, you can have its Ethernet Address with the help of this protocol. Box-A has Box-B's IPv4 address (10.10.10.3). Box-A uses the IPv4 address 10.10.10.3, executes the Address Resolution Protocol and fetches Box-B's Ethernet Address which is 11.22.33.44.55.67.

Once Box-A obtains Box-B's Ethernet address, the Ethernet Frame is constructed and sent to the Physical Layer to send the frame to the switch. The switch receives the frame, refers to its Ethernet-Address to Port mapping and sends the frame to the port where Box-B is connected.

That is how data is transferred from one box to another when both are inside a network.

# 1.2 How does ARP work?

In the above subsection, we simply told that the Box-B's IPv4 address is taken, Address Resolution Protocol is executed and then it gives us the Box-B's Ethernet address. But how does this actually work?

There is no formula or anything to derive the Ethernet address of a Box. You should simply ask for the Ethernet address over the network. A typical ARP request is like the following:

> Hello everyone! Who has 10.10.10.3? Tell 10.10.10.2

But whom should we ask this? Everyone in the network. In technical terms, the ARP request is broadcasted to the network.

When such a request is sent to everyone, who knows the answer to this? Box-B definitely knows the answer because it is his identity. Box-B sends back a targeted response to Box-A:

> Hello Box-A! 10.10.10.3 is at 11.22.33.44.55.67

Once Box-A gets the Ethernet address, it goes ahead and sends the frame to Box-B.

In short, that is how ARP works.

# 1.3 ARP request-response structures

The above subsection was intended to be an introduction to ARP. Now, let us checkout the packet structure of ARP request and response. The structure is present in **/usr/include/net/if_arp.h**.

```c
struct arphdr                                                                   
  {                                                                             
    unsigned short int ar_hrd;      /* Format of hardware address.  */          
    unsigned short int ar_pro;      /* Format of protocol address.  */          
    unsigned char ar_hln;       /* Length of hardware address.  */              
    unsigned char ar_pln;       /* Length of protocol address.  */              
    unsigned short int ar_op;       /* ARP opcode (command).  */                
#if 0                                                                           
    /* Ethernet looks like this : This bit is variable sized                    
       however...  */                                                           
    unsigned char __ar_sha[ETH_ALEN];   /* Sender hardware address.  */         
    unsigned char __ar_sip[4];      /* Sender IP address.  */                   
    unsigned char __ar_tha[ETH_ALEN];   /* Target hardware address.  */         
    unsigned char __ar_tip[4];      /* Target IP address.  */                   
#endif                                                                          
  };
```

The same header is used for both request and response. the ```ar_op``` or the ARP opcode tells if it is a request or response. The following is how the actual ARP request looks like:

```c
struct arphdr                                                                   
  {                                                                             
    unsigned short int ar_hrd; = ARPHRD_ETHER (Ethernet 10/100 Mbps)
    unsigned short int ar_pro; = 0x0800 (IPv4 Protocol)
    unsigned char ar_hln;      = 6 (bytes)
    unsigned char ar_pln;      = 4 (bytes)
    unsigned short int ar_op;  = ARPOP_REQUEST
    
    unsigned char __ar_sha[ETH_ALEN]; = 11.22.33.44.55.66
    unsigned char __ar_sip[4];        = 10.10.10.2
    unsigned char __ar_tha[ETH_ALEN]; = 00.00.00.00.00.00
    unsigned char __ar_tip[4];        = 10.10.10.3
  };
```

Note how the Target hardware address is 00.00.00.00.00.00. This is what we need to find.

This ARP request is **broadcasted**. The default ethernet broadcast address is ff.ff.ff.ff.ff.ff. This broadcast address would be the destination address in the ethernet frame header.

Assume no one knows who has 10.10.10.3 except for Box-B itself. So, Box-B sends back the following response.

```c
struct arphdr                                                                   
  {                                                                             
    unsigned short int ar_hrd; = ARPHRD_ETHER (Ethernet 10/100 Mbps)
    unsigned short int ar_pro; = 0x0800 (IPv4 Protocol)
    unsigned char ar_hln;      = 6 (bytes)
    unsigned char ar_pln;      = 4 (bytes)
    unsigned short int ar_op;  = ARPOP_REPLY
    
    unsigned char __ar_sha[ETH_ALEN]; = 11.22.33.44.55.67
    unsigned char __ar_sip[4];        = 10.10.10.3
    unsigned char __ar_tha[ETH_ALEN]; = 11.22.33.44.55.66
    unsigned char __ar_tip[4];        = 10.10.10.2
  };
```

Here, the source of this ARP response is Box-B. The source hardware address is 11.22.33.44.55.67 and source IPv4 address is 10.10.10.3. We know the target hardware and IPv4 addresses - which is Box-A. Once Box-A receives this, it looks at the sender MAC and IPv4 address, it extracts the MAC address and goes ahead with the communication with Box-B.

I would urge you to use Wireshark and command-line tools like **arp**, **arping** to get a live picture of ARP.

This was about the packet structure.

# 1.4 ARP Cache

Whenever Box-A wants to talk to Box-B, should it execute ARP, get Box-B's Ethernet address and then start talking? What if Box-A just saves Box-B's Ethernet address?

Yes, that can be done - it can be **cached**. Small amount of memory is used to store this IP-Address to Ethernet-Address mapping.

But when you cache something like this, it is followed by the usual cache problems: What if Box-B's IPv4 address change? - then the mapping becomes invalid or sometimes even wrong if the same IPv4 address is given to some Box-D. For how long will the mapping be valid? How often should Box-A refresh the cache?

# 1.5 Important properties

Now let us talk about something more interesting.

### 1.5.1 Can anyone can respond?

When Box-A broadcasts an ARP request to get the Ethernet address of Box-B, who answers to the request?

In the above subsection, Box-B itself answered - this is the example we took. BUT, can anyone else answer? Consider another Box-C which also knows Box-B's Ethernet address (maybe Box-C spoke to Box-B sometime back and had cached Box-B's Ethernet address). When Box-A broadcasts the request, suppose Box-C gets the request but due to some reason, the request doesn't reach Box-B. Now, a number of questions arise. A few of them are listed below.

1. Can Box-C respond with Box-B's Ethernet address? Is the protocol designed that way?
2. Even if it responds, will Box-A accept it? Because what **authority** does Box-C have? Why should Box-A even believe what Box-C say? Does Box-C actually give Box-B's address or some fake address? What if Box-C's cache entry is an invalid one? Does Box-A have a way to verify it?

I think these are natural questions which arise. ARP is a simple protocol. It accepts whatever is given to it.

To answer (1), Yes. Box-C can respond with Box-B's Ethernet address. To generalize this, anyone who **has the answer** can respond.

To answer (2), Yes. Box-A will accept what Box-C sends. Finally, Box-A simply accepts what Box-C sends. There is no question of authorization here. Box-A will **blindly** believe whatever Box-C sends. Box-A **does not** cross verify what it has got. It will simply use it.

Can there be any adverse consequences?

### 1.5.2 Is it really request-response?

The way we discussed in the above subsections, ARP feels like a proper request-response protocol.

When one box broadcasts a request, if anyone has the response (generally the destination box itself), it will send the response. This is generally how ARP is used.

From the above subsection, we saw that anyone can send a response. But what we saw was a response packet to a request. Can (say) Box-C simply send ARP response packet to Box-A? - without Box-A asking for it?

Indeed. This infact demostrates the **looseness** of ARP. Box-C(or any other box for that matter) can simply send an ARP response to any other box. The target box simply accepts the response and possibly stores the new IPv4-Address to Ethernet-Address mapping in its ARP cache.

# 1.6 Introduction to Statelessnesss

We saw some basic (and wierd) behavior of ARP. What are the consequences? Is it fine to have such behavior? Let us see.

As we discussed in subsection 1.5.1, any box can respond to a request. Although it is good in a way, how can one trust the response? The responder box could have gone rogue. It might be compromised. How do we verify the Ethernet Address send by that responder?

Subsection 1.5.2 is very interesting. Any box can simply send a response to a box even if it didn't ask for it - and ARP is okay with it. This reveals a very interesting property of ARP.

What is the responsible way of fetching the Ethernet Address?

When we send a request for something, we **wait** for the response. Technically, a thread handling this request might be waiting. It is more likely to be event-driven. You send out a request and setup a watchdog for responses to that request. Once an ARP response comes and the NIC notifies us, we take action - check if the response goes well with out request and take further action(maybe updating the ARP cache or simply continuing the communication with the destination box).

Generally, one accepts a response **only** if he has requested for it. To know if a box has sent out a request, the box should **remember** it - remember the fact that it has sent out a request and a response might come back anytime soon.

But in the case of ARP, does that apply? Even if Box-A had not asked for Box-B's address through an ARP request, a Box-D could keep sending ARP responses to Box-A and Box-A accepts and uses the response without questioning. ARP is a simple protocol and **does not remember anything**.

Informally speaking, ARP is a **loose** protocol. It does not have any checks and verification mechanisms, no request-response relationship. Formally, it is classified as a **Stateless** protocol. The information that it ideally has to remember is called the **State**.

# 1.7 Consequences of Statelessness

ARP is stateless(or loose) by design. There are a few exploit methods which directly take advantage of its statelessness. ARP spoofing, ARP cache poisoning attacks/exploits are the most popular.

Let us understand ARP spoofing better.

Consider a bunch of machines in a switched network. Let us specifically take 3 boxes: Box-A(10.10.10.2, 11.22.33.44.55.66), Box-B(10.10.10.3, 11.22.33.44.55.67) and Box-C(10.10.10.4, 11.22.33.44.55.68). Box-A wants to talk to Box-B. Box-C is a rogue machine which wants to hijack the conversation between Box-A and Box-B and feed Box-A with some back information. Now, how can it do that? With the help of ARP.

1. Whenever Box-A wants to talk to Box-B, it will require Box-B's Ethernet address. It will send out an ARP request to get it.
2. Now, we know that anyone box can send an ARP response to any box in the network. Our Box-C can send an ARP response to Box-A with the following details:
  - Target IP Address: 10.10.10.3 (Box-B's IPv4 address)
  - Target Ethernet Address: 11.22.33.44.55.68 (Box-C's Ethernet address)
3. Box-A on receives the response. Box-A **thinks** that the Ethernet Address of a box with IPv4 Address 10.10.10.3 is 11.22.33.44.55.68. In other words, from Box-A's point of view, Box-C is actually Box-B. So whenever Box-A talks, it thinks it is talking to Box-B but in reality it is talking to Box-C.

In order to make sure Box-A keeps talking to Box-C, Box-C should keep fooling Box-A by sending malicious ARP responses. See how easy it is to fool a box and steal another box's identity?

One can easily write such continuously ARP response pinging tools. That is going to be a good exercise.

To conclude, Statelessness is at the heart of this attack. If ARP was a stateful protocol, it would be a strict request-response protocol - where it would not entertain **spurious** ARP responses.

# 1.8 That fundamentally problematic concept

This is one example of Statelessness and its problems. This is one of the fundamentally problematic concept we will be discussing. Statelessness has a lot of advantages as well - stateless protocols and mechanisms are performant. I think this is the age old tug of war between performance and security.

## 2. SigReturn Oriented Programming (SROP)

SigReturn Oriented Programming (SROP) is one of the most beautiful exploit methods to take control of the system after hijacking control-flow. [Here](https://ieeexplore.ieee.org/document/6956568) is the full paper. You may read [this](/reverse/engineering/and/binary/exploitation/series/2021/05/09/sigreturn-oriented-programming.html) article to understanding SROP better.

In here, we will not go into the gymnastics of SROP. Instead we will explore how this attack was made possible. What are the conditions to be met for this attack to work.

The basic condition is that the attacker should have control over the Instruction Pointer. This behaves as an enabler vulnerability which opens up the room for crazier sub-vulnerabilities to be exploited. SROP identifies one such crazy sub-vulnerability and exploits it.

Before proceeding, I would request the reader to read the paper OR the article mentioned above. This is to understand the exploit method better. I will not be describing the method here. We will proceed assuming that you understand SROP.

# 2.1 Signal handling: A Stateless mechanism

### 2.1.1 Introduction

Consider the following C program.

```c
srop$ cat code2.c
#include <stdio.h>
#include <signal.h>

void sigint_handler(int x)
{
	printf("sigint_handler says Hi!\n");
}

int main()
{
	/* Register the handler */
	signal(SIGINT, sigint_handler);
	printf("Entering infinite loop.\n");
	while(1);
}
```

In the above program, we first register a signal handler. Whenever this process receives **SIGINT** signal, the function ```sigint_handler()``` is invoked. Once it is registered, the program enters an infinite loop. Let us run the program.

```
srop$ ./code2
Entering infinite loop.

^Csigint_handler says Hi!
^Csigint_handler says Hi!
^Csigint_handler says Hi!
```

Whenever you press **Ctrl+C**, a SIGINT is sent to the process - this triggers the execution of the ```sigint_handler```.

How does it all work?

Whenever we want to execute a system call, a **context switch** happens. We change from user-context to kernel-context. But what happens during this switch? Something called the **Process Control Block (PCB)** is stored. What does this PCB contain? It simply has the values of all the registers and other metadata related to the user-context. It is all the information required to load back the user-context (userspace code) once the kernel code is done executing.

The situation is a bit different here. There are 2 user-contexts present here. We start with one user-context - here it is a simple ```while(1)``` loop. When we press **Ctrl+C**, magic happens and then the ```sigint_handler()``` is executed - which is also userspace code. So we switch from one user-context to another. For the sake of differentiation, let us call the infinite loop as the process-context and the signal handler code as signal-context - but again, remember that both of them are userspace code and we switch from one user-context to another. What is the procedure?

The procedure is very similar to a standard user-to-kernel context switch. All the necessary information and metadata of the process-context is first stored and then control is transferred to the signal-context. Once the signal-context is done running, the stored information and metadata is used to load back the process-context.

At a conceptual level, this is how signals work.

### 2.1.2 Specifics

Now, let us get into some specifics. Where exactly is this metadata stored? Who does this context switch? Are there any system calls involved? Once signal handler is done running, how is the original process-context loaded back?

1. Where is the metadata stored?
  - The metadata is stored in the process's runtime stack itself.
  - This metadata is called a **signal frame**. This signal-frame has all the metadata required to load back the original process-context.

2. Who stores it?
  - The kernel stores it. 

3. Once the signal-handler is done running, who loads back the process-context?
  - A small piece of userspace code is called. This userspace code inturn calls a system-call called the ```sigreturn```. This system call restores the process-context.

Now, let us list down all the steps - starting from sending the signal to the process to restoring back the process-context.

1. The user presses the Ctrl+C button and sends the SIGINT signal to our process.
2. The kernel forms the **signal-frame** - which is all the metadata related to the original process-context. The kernel then places this signal-frame on the process's userspace runtime-stack. After it is placed, control is transferred to the signal-handler.
3. Signal-handler runs and is done executing. This is also a function. Once it is done, where does it return to? It returns to a **stub-code** in the userspace which calls the ```sigreturn``` system call. The following is the stub-code.

  ```c
  <__restore_rt>:	mov    rax,0xf
  <__restore_rt+7>:	syscall
  ```
  - **0xf** is ```sigreturn```'s system call number.
4. This system call removes the signal-frame from the runtime-stack, loads back the original process-context. Execution will start from where it had stopped.

More importantly, the **rip** register present in the signal-frame is loaded back to the CPU register. This is how control is given back to the process-context. So when I say cleanup, it means removing the signal-frame from the runtime stack and trnasferring control to the code present at **rip** value stored in that signal-frame.

One thing what we did not look into is the structure of the signal-frame. It has lot of details in it. I request you to read subsection 2.3.2 of [this](/reverse/engineering/and/binary/exploitation/series/2021/05/09/sigreturn-oriented-programming.html) article.

### 2.1.3 Statelessness?

While changing to signal-context, the kernel creates the signal-frame, places it in the runtime-stack and then gives control to the signal handler. While changing back to process-context, the kernel(the ```sigreturn``` syscall) cleans up the signal-frame, loads back the register values etc., present in the signal-frame to the CPU and then gives control to process-context.

Here, the kernel cleans up whatever it had setup a while ago. Is there a check for that? When the kernel(sigreturn) is about to cleanup a signal-frame, does it check if the kernel had set it up? What if somehow an attacker sets up a fake signal-frame and triggers a cleanup - in this case, the kernel should outright reject the cleaning up and should rightfully terminate the process. But does this happen?

Not really. And there lies the core issue.

In normal cases, the kernel sets up the signal-frame and later it(sigreturn) is called to cleanup and give control to process-context. This is how the signal-handling mechanism is expected to work. This is similar to the case when Box-A broadcasts an ARP request and Box-B rightfully responds to it. This is how ARP is expected to work.

But in ARP, we have seen that Box-A may accept responses even when it has not sent any ARP request. In the same way, can the kernel(sigreturn system call) cleanup something the kernel itself has not setup?

Yes. Fact is that setting up and cleaning up signal-frames are 2 independent mechanisms. They are totally unrelated to each other - very similar to how ARP request and response are independent of each other and are not coupled. When ```sigreturn``` is called to cleanup a signal-frame, it **does not know** and **does not care** about who setup that signal-frame. All it cares about is that a signal-frame is present in the runtime-stack and it should clean up.

What are the consequences of this type of mechanism? As we discussed, one consequence is that ```sigreturn``` cleans up **any** signal-frame present in the runtime-stack.

Suppose you have a program with a classic Stack-Overflow vulnerability in it. Here, you have 2 things at your disposal: One is that you have control over the Instruction Pointer - you can run whatever code you want. Second is that you have control over the data present in the runtime-stack. With this, you can point the Instruction-Pointer to the userspace stub-code which will call ```sigreturn```. Next is you can create a **fake** signal-frame in the runtime-stack. Once the ```ret``` instruction is executed, we call ```sigreturn``` to cleanup the signal-frame **we** setup.

What type of signal-frame could we setup? To start with, we could write ```rax``` value as 60 - which is the system call for exit. We could write ```rdi``` with any number we need - as an argument to the ```exit()``` system call. Then finally, we could write ```rip``` with the ```syscall``` instruction virtual address - where could we find that? It is similar to finding ROP gadgets. We should browse through the binary - we might get one. After this, when the ```ret``` instruction is executed, the kernel(sigreturn) loads these values into the processor's registers and transfers control to the address present in ```rip```. This way, we executed the ```exit()``` system call and killed the program.

### 2.1.4 Conclusion

First of all, this would not have been possible if there is no **enabler** vulnerability. In the above example, the enabler vulnerability is a classic Stack Overflow. If there no such vulnerability, the attacker would not have gotten control of the stack and Instruction Pointer.

What we have is a sub-vulnerability. This arose due to the nature of signal-handling mechanism in Linux. The signal-handling mechanism is Stateless by design - the formation-cleanup of signal-frame are independent of each other. There is no way to check the authenticity of a signal-frame - who exactly set it up? Is it the kernel or some other code? The **looseness** of this mechanism is at the bottom of this.

I would request the reader to go through the [SROP paper](https://ieeexplore.ieee.org/document/6956568) to know more. It is a beautiful paper an amazing exploit method.

The next few exploit methods/mechanisms go beyond Statelessness. We will see how many other mechanisms which are highly performant and simple also suffer from similar problems. With an enabler vulnerability present, a lot of stuff opens up for attack and exploitation.

## 3. Return Oriented Programming (ROP)

Return Oriented Programming (ROP) is a code-reuse attack method which uses the code present in the code segment to exploit the system. The necessary condition for this exploit to work is that the attacker should have control over the Instruction Pointer. The stack doesn't not have to be Executable.

# 3.1 Are function calls stateful?

Whenever a caller function ```call```s a callee, the address of the next instruction is ```push```ed into the runtime stack and then control is transferred to the callee function. The Return-Address is **the only** way to go back to the caller. This is a small piece of state information to trace back the caller. Along with that, the state also contains the pointer to the caller stack frame. This is also **the only** way to make the Base Pointer point to the caller's stack frame once the callee is done running.

When control is being transferred to the callee, memory is allocated, necessary information required to go back to the original state is stored in that memory and then callee takes charge. This is the **state** stored by the caller.

Conceptually, there is a very strict relationship between the ```call``` and ```ret``` instructions. Every ```call``` should be responded by a ```ret``` at some point in time, every ```ret``` executed should have had a ```call``` to begin with. This relationship between ```call``` and ```ret``` is supported by a small piece of information - the return-address. 

That is at a conceptual level. But in practice, things are different. There is no relationship between ```call``` and ```ret```. They are simply 2 independent instructions which are not bound to each other in any way. A ```call``` simply pushes the return-address and jumps to a destination address. With that, ```call```'s job is over. A ```ret``` pops the stack once and jumps to that popped content(it will assume that it is an address).

The ```call```-```ret``` relationship is enforced by the compiler. It generates code which abides to the above concept - and that is the only way the ```call```-```ret``` relationship is maintained. There is no other enforcement. With the presence of an ```enabler``` vulnerability, the conventional ```call```-```ret``` relationship can be broken. The attacker can use these 2 independent instructions to his advantage in any possible way he wants.

In this section, we will see one such attack: Return Oriented Programming (ROP). It does exactly this. It breaks the conventional ```call```-```ret``` relationship enforced by the compiler code and goes on to do some crazy stuff.

# 3.2 Introduction to ROP

[Here](https://hovav.net/ucsd/dist/rop.pdf) is the link to the paper. To get a comprehensive picture of ROP, you may read my posts: [ROP-Part1](/reverse/engineering/and/binary/exploitation/series/2019/01/16/return-oriented-programming-part1.html), [ROP-Part2](/reverse/engineering/and/binary/exploitation/series/2019/03/30/return-oriented-programming-part2.html).

In ROP exploits, short pieces of code (typically a few instructions) ending with the ```ret``` instruction are chosen, stitched together to achieve an objective. Such short pieces of code are called gadgets. Suppose we want to execute the ```exit(1)``` system call, what all do we need to do? The ```rax``` register should be loaded with 60 (exit's system call number), ```rdi``` with 1 (the argument) and finally execute the ```syscall``` instruction. We need to first find such gadgets and place their addresses in the runtime-stack. Suppose we find the following gadgets:

```
// To load the syscall number into rax
0x401010: pop rax; ret

// To load 1 into rdi
0x401234: pop rdi; ret

// syscall gadget
0x404532: syscall; ret
```

We use these gadgets and stitch them together in the following manner:

```
| 0x401010  |
|     60    |  
| 0x401234  |
|     1     |
| 0x404532  |
```

And when the vulnerable function's ```ret``` is first executed, control goes to the first gadget. 60 is loaded into ```rax```. Then again ```ret``` is executed which gives control to the second gadget - this loads 1 into ```rdi```. Then the second gadget's ```ret``` is executed which gives control to the syscall gadget. The ```syscall``` instruction is executed and program come to an end.

Here, the strict ```call```-```ret``` relationship is broken and ```ret``` is being used in a "wierd" way to achieve a malicious objective. This would not be possible without an enabler vulnerability present. Because it is present, this one sub-vulnerability is exposed.

## 4. Conclusion

# 4.1 Fooling someone

So far, we have seen 3 examples of what happens if the internal mechanisms are **loose** in nature. A lot of possibilitites open up in the presence of a enabler vulnerability.

In Return-to-Libc, by creating fake state (return-address, arguments etc.,), you fool the ABI - the framework that governs the working of functions, arguments etc., You are fooling another function present in the userspace.

But in SROP, you fool the kernel itself - by creating fake signal-frames. I expected the kernel to have some sort of authenticity check - say it could cryptographically sign the signal-frame with its own private key. That way, it can reject any signal-frames created by any other entity.

The same goes with ARP spoofing. Even if it is stateless, we should be confident on who sends it, who can be trusted etc.,

# 4.2 Moving forward

The following things is what I would be focusing on.

1. Explore more exploits, attacks, sub-vulnerabilities present - read papers and do practicals.
2. If there are no enabler vulnerabilities, it would become really hard to exploit these sub-vulnerabilities. For that, we need to use a safer language to write our programs. Rust is one such alternative. I would like to go deep into Rust internals.
3. I want to under all the kernelspace-userspace interfaces present in Linux, get to know how each one of them work. SROP exploited one such interface. I am interested in finding such "wierd" interfaces.
4. For some time, looking at everything through the lens of States - Is a mechanism stateful, stateless, what state does it store, can it be corrupted, faked, who authenticates the state etc.,

Most of the information in this article is well known and there is nothing new as a concept. But idea was to take a few attacks/exploits out there and look at them through the lens of States. I wanted to look at how "tight" or "loose" these mechanisms are.

With that, we have come to end of this post. I will be writing follow up posts as and when I explore something new with respect to the 4 points listed above - will be focusing on (1) and (3).

Thanks for reading :-)