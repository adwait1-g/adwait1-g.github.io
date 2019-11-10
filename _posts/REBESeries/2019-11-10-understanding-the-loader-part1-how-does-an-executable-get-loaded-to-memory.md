---
title: Understanding the Loader - Part1 - How does an executable get loaded to memory?
layout: post
categories: Reverse Engineering and Binary Exploitation Series
comments: true
---

Hello friend!

A program is just a dead piece of software lying in your hard-drive. But when you run it, an instance of the program is created and the program comes alive. This is known as a process.

In bunch of previous posts, we have seen what happens **after** a program starts getting executed - main() gets executed, various functions are called and returned to, new objects are created, bunch of them are freed. 

We have not explored how an executable is loaded to memory? How it's dependent libraries are loaded into memory?

We'll explore the same in this post and hope to get an answers to the questions.

Let us get started!

## 0. Introduction

Let us use a simple hello program for our exploration.

```c
rev_eng_series/post_19: cat hello.c
#include<stdio.h>
int main() {
	
	printf("Hello World!\n");
	while(1);
	return 0;
}
```

Let us compile it in a normal manner.
```
rev_eng_series/post_19: gcc hello.c -o hello
```

We are trying to find out how a program starts its execution. So, we'll inspect the executable with some basic tools and see if we can get some info.

**1.** Looking at the ELF header.
```
rev_eng_series/post_19: readelf -h hello
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
  Class:                             ELF64
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              EXEC (Executable file)
  Machine:                           Advanced Micro Devices X86-64
  Version:                           0x1
  Entry point address:               0x400430
  Start of program headers:          64 (bytes into file)
  Start of section headers:          6464 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           56 (bytes)
  Number of program headers:         9
  Size of section headers:           64 (bytes)
  Number of section headers:         30
  Section header string table index: 27
```
* From the header, we know that the **Entry point Address** for this program is **0x400430**. This address is where the program's first instruction is located. So, this is obviously the start of execution of the program.

* Let us run the program using gdb.

```
rev_eng_series/post_19: gdb -q hello
Reading symbols from hello...(no debugging symbols found)...done.
gdb-peda$ 
gdb-peda$ b *0x400430
Breakpoint 1 at 0x400430
gdb-peda$ run
Starting program: /home/adwi/my_projects/blog_related/rev_eng_series/post_19/hello 
warning: the debug information found in "/lib64/ld-2.23.so" does not match "/lib64/ld-linux-x86-64.so.2" (CRC mismatch).

[----------------------------------registers-----------------------------------]
RAX: 0x1c 
RBX: 0x0 
RCX: 0x7fffffffdac8 --> 0x7fffffffdef0 ("XDG_VTNR=7")
RDX: 0x7ffff7de7ac0 (<_dl_fini>:	push   rbp)
RSI: 0x1 
RDI: 0x7ffff7ffe168 --> 0x0 
RBP: 0x0 
RSP: 0x7fffffffdab0 --> 0x1 
RIP: 0x400430 (<_start>:	xor    ebp,ebp)
R8 : 0x7ffff7ffe6f8 --> 0x0 
R9 : 0x0 
R10: 0x3d ('=')
R11: 0xb ('\x0b')
R12: 0x400430 (<_start>:	xor    ebp,ebp)
R13: 0x7fffffffdab0 --> 0x1 
R14: 0x0 
R15: 0x0
EFLAGS: 0x206 (carry PARITY adjust zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x40042a:	add    BYTE PTR [rax],al
   0x40042c:	add    BYTE PTR [rax],al
   0x40042e:	add    BYTE PTR [rax],al
=> 0x400430 <_start>:	xor    ebp,ebp
   0x400432 <_start+2>:	mov    r9,rdx
   0x400435 <_start+5>:	pop    rsi
   0x400436 <_start+6>:	mov    rdx,rsp
   0x400439 <_start+9>:	and    rsp,0xfffffffffffffff0
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffdab0 --> 0x1 
0008| 0x7fffffffdab8 --> 0x7fffffffdeaf ("/home/adwi/my_projects/blog_related/rev_eng_series/post_19/hello")
0016| 0x7fffffffdac0 --> 0x0 
0024| 0x7fffffffdac8 --> 0x7fffffffdef0 ("XDG_VTNR=7")
0032| 0x7fffffffdad0 --> 0x7fffffffdefb ("XDG_SESSION_ID=c7")
0040| 0x7fffffffdad8 --> 0x7fffffffdf0d ("XDG_GREETER_DATA_DIR=/var/lib/lightdm-data/adwi")
0048| 0x7fffffffdae0 --> 0x7fffffffdf3d ("CLUTTER_IM_MODULE=xim")
0056| 0x7fffffffdae8 --> 0x7fffffffdf53 ("rvm_bin_path=/home/adwi/.rvm/bin")
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value

Breakpoint 1, 0x0000000000400430 in _start ()
gdb-peda$ 
```

* We are yet to execute our first instruction. 

Do you observe something unusual?

Who set the **Instruction Pointer** to **0x400430** in the first place?
For a program to run, parts of the executable needs to be copied from the hard-drive to main memory, necessary libraries need to be copied to main memory and only then execution can start. Let us have a look at the **maps** file.
```
rev_eng_series/post_19: ps -e | grep hello
 5501 pts/18   00:00:00 hello
rev_eng_series/post_19: cat /proc/5501/maps
00400000-00401000 r-xp 00000000 08:02 9441559                            /home/adwi/my_projects/blog_related/rev_eng_series/post_19/hello
00600000-00601000 r--p 00000000 08:02 9441559                            /home/adwi/my_projects/blog_related/rev_eng_series/post_19/hello
00601000-00602000 rw-p 00001000 08:02 9441559                            /home/adwi/my_projects/blog_related/rev_eng_series/post_19/hello
7ffff7a0d000-7ffff7bcd000 r-xp 00000000 08:02 25694809                   /lib/x86_64-linux-gnu/libc-2.23.so
7ffff7bcd000-7ffff7dcd000 ---p 001c0000 08:02 25694809                   /lib/x86_64-linux-gnu/libc-2.23.so
7ffff7dcd000-7ffff7dd1000 r--p 001c0000 08:02 25694809                   /lib/x86_64-linux-gnu/libc-2.23.so
7ffff7dd1000-7ffff7dd3000 rw-p 001c4000 08:02 25694809                   /lib/x86_64-linux-gnu/libc-2.23.so
7ffff7dd3000-7ffff7dd7000 rw-p 00000000 00:00 0 
7ffff7dd7000-7ffff7dfd000 r-xp 00000000 08:02 25694777                   /lib/x86_64-linux-gnu/ld-2.23.so
7ffff7fc1000-7ffff7fc4000 rw-p 00000000 00:00 0 
7ffff7ff7000-7ffff7ffa000 r--p 00000000 00:00 0                          [vvar]
7ffff7ffa000-7ffff7ffc000 r-xp 00000000 00:00 0                          [vdso]
7ffff7ffc000-7ffff7ffd000 r--p 00025000 08:02 25694777                   /lib/x86_64-linux-gnu/ld-2.23.so
7ffff7ffd000-7ffff7ffe000 rw-p 00026000 08:02 25694777                   /lib/x86_64-linux-gnu/ld-2.23.so
7ffff7ffe000-7ffff7fff000 rw-p 00000000 00:00 0 
7ffffffdd000-7ffffffff000 rw-p 00000000 00:00 0                          [stack]
ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]
```
* This is the memory layout of our process. There are lot of things present here. The text segment, data segment, read-only data segment, the C library(**libc**), something called **ld-2.23.so**, stack and more.

Who put all of this in the process's address space?

What is the Operating System's role in getting a program running? Is there any other program which helps our program run? What exactly is the mechanism of running any process?

These are the questions we'll be seeking answers to in this post.

## 1. Does our program need a helper to run?

When I started looking at how this mechanism works, I didn't have any idea. So, I started looking inside the executable for clues. 

Every program is divided into **segments**, where a segment is an essential piece of the program, without which the program may not run properly. Let us take a look at these segments once.
```
rev_eng_series/post_19: readelf --segments hello

Elf file type is EXEC (Executable file)
Entry point 0x400430
There are 9 program headers, starting at offset 64

Program Headers:
  Type           Offset             VirtAddr           PhysAddr
                 FileSiz            MemSiz              Flags  Align
  PHDR           0x0000000000000040 0x0000000000400040 0x0000000000400040
                 0x00000000000001f8 0x00000000000001f8  R E    8
  INTERP         0x0000000000000238 0x0000000000400238 0x0000000000400238
                 0x000000000000001c 0x000000000000001c  R      1
      [Requesting program interpreter: /lib64/ld-linux-x86-64.so.2]
  LOAD           0x0000000000000000 0x0000000000400000 0x0000000000400000
                 0x00000000000006dc 0x00000000000006dc  R E    200000
  LOAD           0x0000000000000e18 0x0000000000600e18 0x0000000000600e18
                 0x0000000000000220 0x0000000000000228  RW     200000
  DYNAMIC        0x0000000000000e28 0x0000000000600e28 0x0000000000600e28
                 0x00000000000001d0 0x00000000000001d0  RW     8
  NOTE           0x0000000000000254 0x0000000000400254 0x0000000000400254
                 0x0000000000000044 0x0000000000000044  R      4
  GNU_EH_FRAME   0x00000000000005b4 0x00000000004005b4 0x00000000004005b4
                 0x0000000000000034 0x0000000000000034  R      4
  GNU_STACK      0x0000000000000000 0x0000000000000000 0x0000000000000000
                 0x0000000000000000 0x0000000000000000  RW     10
  GNU_RELRO      0x0000000000000e18 0x0000000000600e18 0x0000000000600e18
                 0x00000000000001e8 0x00000000000001e8  R      1

 Section to Segment mapping:
  Segment Sections...
   00     
   01     .interp 
   02     .interp .note.ABI-tag .note.gnu.build-id .gnu.hash .dynsym .dynstr .gnu.version .gnu.version_r .rela.dyn .rela.plt .init .plt .plt.got .text .fini .rodata .eh_frame_hdr .eh_frame 
   03     .init_array .fini_array .dynamic .got .got.plt .data .bss 
   04     .dynamic 
   05     .note.ABI-tag .note.gnu.build-id 
   06     .eh_frame_hdr 
   07     
   08     .init_array .fini_array .dynamic .got 
```
* There are various types of segments. You can refer to [this post](/reverse/engineering/and/binary/exploitation/series/2018/07/02/what-does-an-executable-contain-internal-structure-of-an-ELF-executable-part1.html) for in-detail explanation of the types. Each segment has a header, called the **program header** which gives information about that particular segment. Look at the **INTERP** header. It says,

> Requesting program interpreter: /lib64/ld-linux-x86-64.so.2

What is a program interpreter? What does it do? Let us check it out.
```
rev_eng_series/post_19: ls -l /lib64/ld-linux-x86-64.so.2
lrwxrwxrwx 1 root root 32 Feb  6  2019 /lib64/ld-linux-x86-64.so.2 -> /lib/x86_64-linux-gnu/ld-2.23.so

rev_eng_series/post_19: file /lib/x86_64-linux-gnu/ld-2.23.so
/lib/x86_64-linux-gnu/ld-2.23.so: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, BuildID[sha1]=c0adbad6f9a33944f2b3567c078ec472a1dae98e, stripped
```
* It is a symbolic link to a file **ld-2.23.so**, which is a **shared object**. 

Started googling about it. The first result I got was a manual page.
```
rev_eng_series/post_19: man ld.so
LD.SO(8)                   Linux Programmer's Manual                  LD.SO(8)

NAME
       ld.so, ld-linux.so* - dynamic linker/loader

SYNOPSIS
       The dynamic linker can be run either indirectly by running some dynami‐
       cally linked program or shared object (in which  case  no  command-line
       options  to  the dynamic linker can be passed and, in the ELF case, the
       dynamic linker which is stored in the .interp section of the program is
       executed) or directly by running:

       /lib/ld-linux.so.*  [OPTIONS] [PROGRAM [ARGUMENTS]]

DESCRIPTION
       The  programs  ld.so  and ld-linux.so* find and load the shared objects
       (shared libraries) needed by a program, prepare the program to run, and
       then run it.

```
* Wow! This is the **Dynamic Linker / Loader**. 

> The dynamic linker can be run either indirectly by running some dynamically linked program or shared object.

Any program we compile is dynamically linked by default. So, every time we run it, the **Dynamic Linker / Loader** gets invoked.

> In the ELF case, the dynamic linker which is stored in the .interp section of the program is executed.

If you go back to the previous section of the post and see, the **.interp** section is nothing but the **INTERP** segment. So, whenever we run a program, the interpreter present in that section gets invoked.

> or directly by running:
	/lib/ld-linux.so.*  [OPTIONS] [PROGRAM [ARGUMENTS]]

This is new. It can also be invoked directly by running in the above manner. 

Let us run it directly and see what we get.

```
eries/post_19: /lib64/ld-linux-x86-64.so.2 
Usage: ld.so [OPTION]... EXECUTABLE-FILE [ARGS-FOR-PROGRAM...]
You have invoked `ld.so', the helper program for shared library executables.
This program usually lives in the file `/lib/ld.so', and special directives
in executable files using ELF shared libraries tell the system's program
loader to load the helper program from this file.  This helper program loads
the shared libraries needed by the program executable, prepares the program
to run, and runs it.  You may invoke this helper program directly from the
command line to load and run an ELF executable file; this is like executing
that file itself, but always uses this helper program from the file you
specified, instead of the helper program file specified in the executable
file you run.  This is mostly of use for maintainers to test new versions
of this helper program; chances are you did not intend to run this program.

  --list                list all dependencies and how they are resolved
  --verify              verify that given object really is a dynamically linked
			object we can handle
  --inhibit-cache       Do not use /etc/ld.so.cache
  --library-path PATH   use given PATH instead of content of the environment
			variable LD_LIBRARY_PATH
  --inhibit-rpath LIST  ignore RUNPATH and RPATH information in object names
			in LIST
  --audit LIST          use objects named in LIST as auditors
```

That is a comprehensive explanation of what this program is. 

This is the **helper program** for shared library executables. 

> This program usually lives in the file `/lib/ld.so', and special directives in executable files using ELF shared libraries tell the system's program
loader to load the helper program from this file.

The special directive might be the **INTERP** segment. It tells the system's program loader to load the helper program from this file. 

So, the system (Operating System) refers to the **INTERP** segment and load the specified helper program.

> This helper program loads the shared libraries needed by the program executable, prepares the program to run, and runs it.

So, this is the one which is loading everything needed by our program, facilitating our program to run.

To summarize what we have explored till now,

> There is a helper program called the **Program Interpreter**, **Dynamic Linker** or the **Loader** helps our (any dynamically linked) program to run. It loads the necessary libraries and does everything to make sure our program runs.

> If the program is run directly, the OS **loads** the **helper program** and then gives it control to take care of the rest.

We'll see how we can run our hello program using the helper program.
```
rev_eng_series/post_19: /lib64/ld-linux-x86-64.so.2 ./hello
Hello World!

```
Bingo! Exact same thing happened.

At this point, we have an answer to our question at a conceptual level - The OS along with the **helper program** makes sure our program runs.

I want to dig deep. I want to find the functions involved, I want to find the exact place where these libraries are **mapped** to the process's address space.

## 2. Exploring the helper

Before running the helper with gdb, we'll do some basic analysis on it, find out more about it.

Let us take a look at the strings present in the helper.

### a. Strings

```
rev_eng_series/post_19: strings /lib64/ld-linux-x86-64.so.2 > ld.so.str
```

The following are the first few strings.

```
_rtld_global
__get_cpu_features
_dl_find_dso_for_object
_dl_make_stack_executable
__libc_stack_end
__libc_memalign
malloc
_dl_deallocate_tls
__libc_enable_secure
__tls_get_addr
_dl_get_tls_static_info
calloc
_dl_debug_state
_dl_argv
_dl_allocate_tls_init
_rtld_global_ro
realloc
_dl_tls_setup
_dl_rtld_di_serinfo
_dl_mcount
_dl_allocate_tls
_r_debug
free
ld-linux-x86-64.so.2
```
* They look like the functions called by the helper.

* I found another set of strings, which look like source-files where the definition of some of these functions might be present.

```
rtld.c
get-dynamic-info.h
do-rel.h
setup-vdso.h
dl-load.c
dl-lookup.c
dl-deps.c
dl-hwcaps.c
../elf/dl-runtime.c
dl-fini.c
dl-misc.c
dl-conflict.c
dl-tls.c
.
.
.
```

We can [search](https://duckduckgo.com/?q=rtld.c+where+is+it%3F&t=canonical&ia=web) for the above files. 

**rtld.c** is part of **glibc**, the GNU C Library. We'll be referring to glibc's sourcecode often to understand what functions are present, what they do etc.,

* You can either use glibc's [github mirror](https://github.com/bminor/glibc) to browse the sourcecode, or you can download a copy.

```
rev_eng_series/post_19/glibc: git clone git://sourceware.org/git/glibc.git
```

If you are using **vim** to open and read files, use **ctags** to browse through code. [This article](https://andrew.stwrt.ca/posts/vim-ctags/) should help.

With that, let us take a look at **rtld.c**.

```
rev_eng_series/post_19/glibc/elf: head rtld.c
/* Run time dynamic linker.
   Copyright (C) 1995-2019 Free Software Foundation, Inc.
   This file is part of the GNU C Library.
.
.
```

* It says **Runtime Dynamic Linker**. So, this should be the main sourcefile of our helper program. 

As we analyze the helper with gdb, we'll know what sourcefiles and functions to look for.

### b. Analyzing with gdb and reading sourcecode

We have seen that if we simply run the helper, it dies after printing it's Usage info. We'll execute it with **./hello** as the argument. That should set the right path for debugging.

```
rev_eng_series/post_19: gdb -q /lib64/ld-linux-x86-64.so.2 
Reading symbols from /lib64/ld-linux-x86-64.so.2...Reading symbols from /usr/lib/debug//lib/x86_64-linux-gnu/ld-2.23.so...done.
done.
gdb-peda$ 
gdb-peda$ b _start
Breakpoint 1 at 0xc30
gdb-peda$ run ./hello
Starting program: /lib64/ld-linux-x86-64.so.2 ./hello

[----------------------------------registers-----------------------------------]
RAX: 0x0 
RBX: 0x0 
RCX: 0x0 
RDX: 0x0 
RSI: 0x0 
RDI: 0x0 
RBP: 0x0 
RSP: 0x7fffffffdaf0 --> 0x2 
RIP: 0x7ffff7dd7c30 (<_start>:	mov    rdi,rsp)
R8 : 0x0 
R9 : 0x0 
R10: 0x0 
R11: 0x0 
R12: 0x0 
R13: 0x0 
R14: 0x0 
R15: 0x0
EFLAGS: 0x202 (carry parity adjust zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x7ffff7dd7c1f <oom+20>:	mov    edi,0x7f
   0x7ffff7dd7c24 <oom+25>:	call   0x7ffff7df24f0 <__GI__exit>
   0x7ffff7dd7c29:	nop    DWORD PTR [rax+0x0]
=> 0x7ffff7dd7c30 <_start>:	mov    rdi,rsp
   0x7ffff7dd7c33 <_start+3>:	call   0x7ffff7dd89b0 <_dl_start>
   0x7ffff7dd7c38 <_dl_start_user>:	mov    r12,rax
   0x7ffff7dd7c3b <_dl_start_user+3>:	
    mov    eax,DWORD PTR [rip+0x225037]        # 0x7ffff7ffcc78 <_dl_skip_args>
   0x7ffff7dd7c41 <_dl_start_user+9>:	pop    rdx
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffdaf0 --> 0x2 
0008| 0x7fffffffdaf8 --> 0x7fffffffdef1 ("/lib64/ld-linux-x86-64.so.2")
0016| 0x7fffffffdb00 --> 0x7fffffffdf0d --> 0x6f6c6c65682f2e ('./hello')
0024| 0x7fffffffdb08 --> 0x0 
0032| 0x7fffffffdb10 --> 0x7fffffffdf15 ("XDG_VTNR=7")
0040| 0x7fffffffdb18 --> 0x7fffffffdf20 ("XDG_SESSION_ID=c7")
0048| 0x7fffffffdb20 --> 0x7fffffffdf32 ("XDG_GREETER_DATA_DIR=/var/lib/lightdm-data/adwi")
0056| 0x7fffffffdb28 --> 0x7fffffffdf62 ("CLUTTER_IM_MODULE=xim")
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value

Breakpoint 1, 0x00007ffff7dd7c30 in _start ()
gdb-peda$ 
```

We are yet to to execute the helper program's first instruction. Let us look at the **maps** file.

```
gdb-peda$ getpid
14049
```

```
rev_eng_series/post_19: cat /proc/14049/maps
7ffff7dd7000-7ffff7dfd000 r-xp 00000000 08:02 25694777                   /lib/x86_64-linux-gnu/ld-2.23.so
7ffff7ff7000-7ffff7ffa000 r--p 00000000 00:00 0                          [vvar]
7ffff7ffa000-7ffff7ffc000 r-xp 00000000 00:00 0                          [vdso]
7ffff7ffc000-7ffff7ffe000 rw-p 00025000 08:02 25694777                   /lib/x86_64-linux-gnu/ld-2.23.so
7ffff7ffe000-7ffff7fff000 rw-p 00000000 00:00 0                          [heap]
7ffffffdd000-7ffffffff000 rw-p 00000000 00:00 0                          [stack]
ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]
```

There is just bare minimum loaded into the address space: heap, stack, vsyscall, vdso, vvar and the helper program's text segment and data segment.

I went through every function from ```_start``` till a segment gets mapped. It is a complex mechanism.

So, we'll try to get a gist of it.

Loading something into memory means that something is being ```mmap```ed. So, let us break at ```mmap``` and continue. Then we'll get backtrace the list of functions called from ```_start``` till ```mmap```.

```
gdb-peda$ b mmap
Breakpoint 2 at 0x7ffff7df23c0: file ../sysdeps/unix/sysv/linux/wordsize-64/mmap.c, line 33.
gdb-peda$ continue
Continuing.
```

Because this is the first ```mmap```, the **maps** file should still look the same as above. Verify the same.

The following is the execution state.

```
[----------------------------------registers-----------------------------------]
RAX: 0x400000 ('')
RBX: 0x5 
RCX: 0x812 
RDX: 0x5 
RSI: 0x1000 
RDI: 0x400000 ('')
RBP: 0x7fffffffd4e0 --> 0x0 
RSP: 0x7fffffffd1d8 --> 0x7ffff7ddd9e1 (<_dl_map_object_from_fd+1713>:	cmp    rax,0xffffffffffffffff)
RIP: 0x7ffff7df23c0 (<__mmap>:	test   rdi,rdi)
R8 : 0x3 
R9 : 0x0 
R10: 0x7fffffffd1e0 --> 0x400000 ('')
R11: 0x601038 
R12: 0x7ffff7ffe170 --> 0x0 
R13: 0x7fffffffd5c8 --> 0x500000006 
R14: 0x2 
R15: 0x802
EFLAGS: 0x206 (carry PARITY adjust zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x7ffff7df23b9 <close+25>:	mov    DWORD PTR [rcx],eax
   0x7ffff7df23bb <close+27>:	or     rax,0xffffffffffffffff
   0x7ffff7df23bf <close+31>:	ret    
=> 0x7ffff7df23c0 <__mmap>:	test   rdi,rdi
   0x7ffff7df23c3 <__mmap+3>:	push   r15
   0x7ffff7df23c5 <__mmap+5>:	mov    r15,r9
   0x7ffff7df23c8 <__mmap+8>:	push   r14
   0x7ffff7df23ca <__mmap+10>:	mov    r14d,ecx
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffd1d8 --> 0x7ffff7ddd9e1 (<_dl_map_object_from_fd+1713>:	cmp    rax,0xffffffffffffffff)
0008| 0x7fffffffd1e0 --> 0x400000 ('')
0016| 0x7fffffffd1e8 --> 0x401000 
0024| 0x7fffffffd1f0 --> 0x4006dc 
0032| 0x7fffffffd1f8 --> 0x4006dc 
0040| 0x7fffffffd200 --> 0x0 
0048| 0x7fffffffd208 --> 0x5 
0056| 0x7fffffffd210 --> 0x600000 ('')
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value

Breakpoint 2, __mmap (addr=0x400000, len=0x1000, prot=prot@entry=0x5, flags=flags@entry=0x812, fd=fd@entry=0x3, offset=0x0)
    at ../sysdeps/unix/sysv/linux/wordsize-64/mmap.c:33
33	../sysdeps/unix/sysv/linux/wordsize-64/mmap.c: No such file or directory.
gdb-peda$ 
```

We need to check which object is getting mapped.

So, the arguments of ```mmap``` are the following:
1. Address = 0x400000
2. Length = 0x1000 (4096 bytes)

3. Prot = 5 ```PROT_READ | PROT_EXEC``` or ```1 | 4```

4. Flags = We won't know till we go through the series of function calls happened so far.
5. File Descriptor = 3	/* Let us check this out */
6. Offset = 0	/* From beginning of the file */

The **/proc/PID/** directory has every single detail about a process. Let us find which file the descriptor **3** belongs to.

```
rev_eng_series/post_19: cd /proc/14049/
/proc/14049: cd fd
/proc/14049/fd: ls
/proc/14049/fd: ls -l 3
lr-x------ 1 adwi adwi 64 Nov  9 19:35 3 -> /home/adwi/my_projects/blog_related/rev_eng_series/post_19/hello
```

Now, we know the file, but there are many segments that are to be mapped. Let us now find which one this is. Let us go through the segments' list of **hello** program again.

```
rev_eng_series/post_19: readelf --segments ./hello

Elf file type is EXEC (Executable file)
Entry point 0x400430
There are 9 program headers, starting at offset 64

Program Headers:
  Type           Offset             VirtAddr           PhysAddr
                 FileSiz            MemSiz              Flags  Align
  PHDR           0x0000000000000040 0x0000000000400040 0x0000000000400040
                 0x00000000000001f8 0x00000000000001f8  R E    8
  INTERP         0x0000000000000238 0x0000000000400238 0x0000000000400238
                 0x000000000000001c 0x000000000000001c  R      1
      [Requesting program interpreter: /lib64/ld-linux-x86-64.so.2]
  LOAD           0x0000000000000000 0x0000000000400000 0x0000000000400000
                 0x00000000000006dc 0x00000000000006dc  R E    200000
.
.
.
ection to Segment mapping:
  Segment Sections...
   00     
   01     .interp 
   02     .interp .note.ABI-tag .note.gnu.build-id .gnu.hash .dynsym .dynstr .gnu.version .gnu.version_r .rela.dyn .rela.plt .init .plt .plt.got .text .fini .rodata .eh_frame_hdr .eh_frame
   .
   .
   .
```

* It is the **LOAD** type segment. Multiple sections constitute of this single segment.
* **VirtAddr** of that segment is 0x400000.
* Size of 0x6dc - 1756 bytes. But 4096 bytes are being mapped - a full page.

So, it is confirmed that this segment is being mmaped.

Now, let us trace all the function calls made to come to mmap.

```
gdb-peda$ bt
#0  __mmap (addr=0x400000, len=0x1000, prot=prot@entry=0x5, flags=flags@entry=0x812, fd=fd@entry=0x3, offset=0x0)
    at ../sysdeps/unix/sysv/linux/wordsize-64/mmap.c:33
#1  0x00007ffff7ddd9e1 in _dl_map_segments (loader=0x7ffff7ffe170, has_holes=<optimized out>, maplength=<optimized out>, nloadcmds=0x2, 
    loadcmds=<optimized out>, type=<optimized out>, header=<optimized out>, fd=<optimized out>, l=0x7ffff7ffe170) at ./dl-map-segments.h:90
#2  _dl_map_object_from_fd (name=name@entry=0x7fffffffdf0c "./hello", origname=origname@entry=0x0, fd=<optimized out>, 
    fbp=fbp@entry=0x7fffffffd580, realname=<optimized out>, loader=loader@entry=0x0, l_type=0x0, mode=0x20000000, stack_endp=0x7fffffffd578, 
    nsid=0x0) at dl-load.c:1245
#3  0x00007ffff7ddfc27 in _dl_map_object (loader=loader@entry=0x0, name=0x7fffffffdf0c "./hello", type=type@entry=0x0, 
    trace_mode=trace_mode@entry=0x0, mode=mode@entry=0x20000000, nsid=nsid@entry=0x0) at dl-load.c:2498
#4  0x00007ffff7ddc24e in dl_main (phdr=<optimized out>, phnum=0x7, user_entry=0x7fffffffda38, auxv=0x7fffffffdd90) at rtld.c:978
#5  0x00007ffff7df08ad in _dl_sysdep_start (start_argptr=start_argptr@entry=0x7fffffffdaf0, dl_main=dl_main@entry=0x7ffff7dd91e0 <dl_main>)
    at ../elf/dl-sysdep.c:249
#6  0x00007ffff7dd8c2a in _dl_start_final (arg=0x7fffffffdaf0) at rtld.c:323
#7  _dl_start (arg=0x7fffffffdaf0) at rtld.c:429
#8  0x00007ffff7dd7c38 in _start ()
```

Let us go to every function definition and see what each function is doing. Re-run the program in gdb. Put break-points at all these functions.


**1.** **_start**:  We started with ```_start```. It is the starting point of the helper program. It is present in ```glibc/sysdeps/x86_64/dl-machine.h```.

```c
/* SRC: glibc/sysdeps/x86_64/dl-machine.h */

/* Initial entry point code for the dynamic linker.
   The C function `_dl_start' is the real entry point;
   its return value is the user program's entry point.  */
#define RTLD_START asm ("\n\
.text\n\
        .align 16\n\
.globl _start\n\
.globl _dl_start_user\n\
_start:\n\
        movq %rsp, %rdi\n\
        call _dl_start\n\
_dl_start_user:\n\
        # Save the user entry point address in %r12.\n\
        movq %rax, %r12\n\
.
.
.
```

* ```_start``` is the original entry point. ```_dl_start``` is the C-entry point. Got to know ```_dl_start```'s return value is the user program's entry point, which should be the **user program's _start**. 

**2. _dl_start**: The actual entry point of the helper program. It's declaration goes like this.

```c
static ElfW(Addr) __attribute_used__
_dl_start (void *arg);
```

* The argument to this function is a **stack address** which is set in the following manner. Refer to gdb-peda's stack section.

```
arg		-> argc		= 2
arg + 8		-> argv[0]	"/lib64/ld-linux-x86-64.so.2"
arg + 16	-> argv[1]	"./hello"
arg + 24	-> argv[2]	NULL	/* Depicts end of argument vector */
arg + 32	-> env[0]	"XDG_VTNR=7"
arg + 40	-> env[1]	""XDG_SESSION_ID=c7"
.
.
.
```

* It does some initialization and fills in the dynamic linker (it's own) details into a ```struct link_map```. This structure describes a **loaded** shared object.

```c
/* SRC: glibc/include/link.h */

/* Structure describing a loaded shared object.  The `l_next' and `l_prev'
   members form a chain of all the shared objects loaded at startup.

   These data structures exist in space used by the run-time dynamic linker;
   modifying them may have disastrous results.

   This data structure might change in future, if necessary.  User-level
   programs must avoid defining objects of this type.  */

struct link_map
  {
    /* These first few members are part of the protocol with the debugger.
       This is the same format used in SVR4.  */

    ElfW(Addr) l_addr;          /* Difference between the address in the ELF
                                   file and the addresses in memory.  */
    char *l_name;               /* Absolute file name object was found in.  */
    ElfW(Dyn) *l_ld;            /* Dynamic section of the shared object.  */
    struct link_map *l_next, *l_prev; /* Chain of loaded objects.  */
.
.
```
* I told this function writes it's own details into a structure. But, where is that variable declared? Is it a global variable or a local variable? There are 2 things which can happen at compile-time(**not** run-time!).
	* There is a global link_map structure declared specifically to store the Dynamic Linker's details: 

	```c
	/* SRC: glibc/sysdeps/generic/ldsodefs.h */

	  /* Structure describing the dynamic linker itself.  We need to
	     reserve memory for the data the audit libraries need.  */
  	EXTERN struct link_map _dl_rtld_map;
	```
	* Either this can be filled out OR a **local** variable can be declared and it can be filled.
	* Again, this is a compile-time option, whether to use global or local variable. I think the default-build comes with using the global variable. Although I cannot think of a case where the local-variable option is useful.

* Once the structure is filled, ```_dl_start_final``` is called.

**3. _dl_start_final**: The following is it's declaration.

```c
/* SRC: glibc/elf/rtld.c */

/* This is the second half of _dl_start (below).  It can be inlined safely
   under DONT_USE_BOOTSTRAP_MAP, where it is careful not to make any GOT
   references.  When the tools don't permit us to avoid using a GOT entry
   for _dl_rtld_global (no attribute_hidden support), we must make sure
   this function is not inlined (see below).  */

#ifdef DONT_USE_BOOTSTRAP_MAP
static inline ElfW(Addr) __attribute__ ((always_inline))
_dl_start_final (void *arg)
#else
static ElfW(Addr) __attribute__ ((noinline))
_dl_start_final (void *arg, struct dl_start_final_info *info)

```
* **BOOTSTRAP_MAP** is nothing but the ```_dl_rtld_map``` - the global link_map structure. This is the path taken. So, the first variant is called - ```_dl_start_final(void *arg)```. The argument passed to ```_dl_start``` is passed to this unchanged.

* A bunch of members in ```_dl_rtld_map``` are updated here.

* The following is important.

```c
/* SRC: glibc/elf/rtld.c */

/* Call the OS-dependent function to set up life so we can do things like
     file access.  It will call `dl_main' (below) to do all the real work
     of the dynamic linker, and then unwind our frame and run the user
     entry point on the same stack we entered on.  */
  start_addr = _dl_sysdep_start (arg, &dl_main);
```

So, our next function called is ```_dl_sysdep_start```, which returns the start address of the user-program.

**4. _dl_sysdep_start**: This is present in the source-file ```libc/elf/dl-sysdep.c```, whose description is the following: 

```c
Operating system support for run-time dynamic linker.  Generic Unix version.
```

* The description of this function was given as a comment in ```_dl_start_final```. This function is responsible of setting up **life**. A reference to another function named ```dl_main``` is passed to this function. It does all the real-work of the linker.

```c
/* SRC: glibc/elf/dl-sysdep.c */

ElfW(Addr)
_dl_sysdep_start (void **start_argptr,
                  void (*dl_main) (const ElfW(Phdr) *phdr, ElfW(Word) phnum,
                                   ElfW(Addr) *user_entry, ElfW(auxv_t) *auxv))
{
```
* We know the first argument - ```arg``` from the beginning.
* The second one is a function. Let us analyze it when time comes.
* This plays around with interesting data structures like the **Auxillary vector(auxv)**, **Program Headers**, gather lot of info about the program to be run. We'll talk about these in detail later.
* This function calls ```dl_main```.

```c
(*dl_main) (phdr, phnum, &user_entry, GLRO(dl_auxv));
  return user_entry;
```

**5. dl_main**: This function is the heart of the helper program. 

```c
static void
dl_main (const ElfW(Phdr) *phdr,
         ElfW(Word) phnum,
         ElfW(Addr) *user_entry,
         ElfW(auxv_t) *auxv)
{
  const ElfW(Phdr) *ph;
  enum mode mode;
  struct link_map *main_map;
  size_t file_size;
  char *file;
  bool has_interp = false;
.
.
.
```

It does the following.

* It checks if ld.so is the program itself, or it was invoked indirectly by running a user-program. If it is run as a program, the command-line arguments to it are parsed. 
* In our case, There are 2 command-line arguments: ```/lib64/ld-linux-x86-64.so.2``` and ```./hello```.

* This is where the main executable(user-program) is mapped.

```c
/* SRC: glibc/elf/rtld.c */

        {
          RTLD_TIMING_VAR (start);
          rtld_timer_start (&start);
          _dl_map_object (NULL, rtld_progname, lt_executable, 0,
                          __RTLD_OPENEXEC, LM_ID_BASE);
          rtld_timer_stop (&load_time, start);
        }       
```
* I think the function ```_dl_map_object``` is responsible for mapping our executable. 
* There is still lot left in ```dl_main```. But we'll move on to ```_dl_map_object``` and come back later.

**6. _dl_map_object**: Maps in the shared object file NAME.

```c
/* SRC: glibc/elf/dl-load.c */

/* Map in the shared object file NAME.  */
         
struct link_map *
_dl_map_object (struct link_map *loader, const char *name,
                int type, int trace_mode, int mode, Lmid_t nsid)

```

* This function checks if an object is already **loaded**. If it is, then it returns back. If it not, then it'll proceed.
* It searches for the object in several places - **LD_LIBRARY_PATH**, **RUNPATH**. Note that this is a function not just to load our executable, but in general any shared object. 
* It finds the **file** and opens it to get a file descriptor.
* It calls ```_dl_new_object``` which returns a new ```struct link_map``` object for the segment which is going to be mapped.
* If it gets a file descriptor for the file, it calls up ```_dl_map_object_from_fd``` which will eventually map the specified object.
* Note that this function returns a **link_map** object, probably belonging to the object it maps onto memory.

```c
return _dl_map_object_from_fd (name, origname, fd, &fb, realname, loader,
                                 type, mode, &stack_end, nsid);
```

**7. _dl_map_object_from_fd**: Map in the shared object NAME, given an open file descriptor to it.



```c
struct link_map *
_dl_map_object_from_fd (const char *name, const char *origname, int fd,
                        struct filebuf *fbp, char *realname,
                        struct link_map *loader, int l_type, int mode,
                        void **stack_endp, Lmid_t nsid)
```
* This function is damn interesting. The following is gdb's input.

```
Breakpoint 5, _dl_map_object_from_fd (
    name=name@entry=0x7fffffffdf0c "./hello", origname=origname@entry=0x0, 
    fd=0x3, fbp=fbp@entry=0x7fffffffd580, realname=0x7ffff7ffe168 "./hello", 
    loader=loader@entry=0x0, l_type=0x0, mode=0x20000000, 
    stack_endp=0x7fffffffd578, nsid=0x0) at dl-load.c:893

```

* There are a few arguments which we don't know of. Let us look into them.
* the ```struct filebuf```.

```c
/* Type for the buffer we put the ELF header and hopefully the program
   header.  This buffer does not really have to be too large.  In most
   cases the program header follows the ELF header directly.  If this
   is not the case all bets are off and we can make the header
   arbitrarily large and still won't get it read.  This means the only
   question is how large are the ELF and program header combined.  The
   ELF header 32-bit files is 52 bytes long and in 64-bit files is 64
   bytes long.  Each program header entry is again 32 and 56 bytes
   long respectively.  I.e., even with a file which has 10 program
   header entries we only have to read 372B/624B respectively.  Add to
   this a bit of margin for program notes and reading 512B and 832B
   for 32-bit and 64-bit files respecitvely is enough.  If this
   heuristic should really fail for some file the code in
   `_dl_map_object_from_fd' knows how to recover.  */
struct filebuf
{
  ssize_t len;
#if __WORDSIZE == 32
# define FILEBUF_SIZE 512
#else
# define FILEBUF_SIZE 832
#endif
  char buf[FILEBUF_SIZE] __attribute__ ((aligned (__alignof (ElfW(Ehdr)))));
};
```

* It is just beautiful, how clear this comment is. 
* This structure should ideally contain the ELF Header and Program Header Table in it. The comment makes it very clear. You can inspect using gdb to confirm it. 
* If the link_map structure is not present for the object we are about to map, it is created using the ```_dl_new_object``` function.
* It gathers all the ```LOAD``` type segments present in this shared object / executable by scanning through the Program Header table.
* It calculates the address-space needed by ALL LOAD-segments, the total ```maplength```.

* Finally, it calls ```_dl_map_segments``` to map the necessary segments of that object into memory.

**8. _dl_map_segments**: Map a shared object's segments.

* Refer to ```glibc/elf/dl-map-segments.h```
* It has interesting comments.

```c
/* This implementation assumes (as does the corresponding implementation
   of _dl_unmap_segments, in dl-unmap-segments.h) that shared objects
   are always laid out with all segments contiguous (or with gaps
   between them small enough that it's preferable to reserve all whole
   pages inside the gaps with PROT_NONE mappings rather than permitting
   other use of those parts of the address space).  */
```
* All segments belonging to a shared object are mapped in a contiguous manner - one next to another.

* If you have observed the **maps** file, you can see a few address-ranges with no permissions - **---p**. No read, No write, No execute - ```PROT_NONE	```. Now, I get why these address-ranges exist. That comment explains it.
	* If the gaps between the segments are small enough, they are given the ```PROT_NONE``` mappings rather than permitting "other use".
* The function goes like this.

```c
static __always_inline const char *
_dl_map_segments (struct link_map *l, int fd,
                  const ElfW(Ehdr) *header, int type,
                  const struct loadcmd loadcmds[], size_t nloadcmds,
                  const size_t maplength, bool has_holes,
                  struct link_map *loader)
```

* It's arguments tell a lot about what this function does.
1. ```struct link_map *l```: link_map structure for this shared object / executable.
2. ```int fd```: The Open file descriptor, opened by ```_dl_map_object_from_fd```

3. ```const ElfW(Ehdr) *header```: This is the ELF Header of the shared object at hand.
4. ```int type```: Type of ELF file - Is it an executable(```ET_EXEC```), or a shared object(```ET_DYN```) or anything else.
5. ```const struct loadcmd loadcmds[]```: Each ```loadcmd``` structure contains info about each **LOAD** segment present in this file. Let us checkout the structure.

```c
/* This structure describes one PT_LOAD command.
   Its details have been expanded out and converted.  */
struct loadcmd
{  
  ElfW(Addr) mapstart, mapend, dataend, allocend;
  ElfW(Off) mapoff;
  int prot;                             /* PROT_* bits.  */
}
```
* As the comment says, this structure says 1 ```PT_LOAD``` command. Our executable had **2** PT_LOAD commands. So, in this case, ```loadcmds[]``` should be an array of structure with length 2.

6. ```size_t nloadcmds```: Length of the ```loadcmds[]``` array.
7. ```const size_t maplength```, ```bool has_holes```: We'll come back to this later.
8. ```struct link_map *loader```: This should be the loader's link_map - ```_dl_rtld_map```.

* It iterates through the ```loadcmds[]``` array and maps each one of the LOAD-segment.

```c
  while (c < &loadcmds[nloadcmds])
    {
      if (c->mapend > c->mapstart
          /* Map the segment contents from the file.  */
          && (__mmap ((void *) (l->l_addr + c->mapstart),
                      c->mapend - c->mapstart, c->prot,
                      MAP_FIXED|MAP_COPY|MAP_FILE,
                      fd, c->mapoff)
              == MAP_FAILED))
        return DL_MAP_SEGMENTS_ERROR_MAP_SEGMENT;
.
.
```

* So, this function finally maps the segment to memory. Let us see the change in the maps file after the following is executed.

```
Breakpoint 1, __mmap64 (addr=0x400000, len=0x1000, prot=prot@entry=0x5, 
    flags=flags@entry=0x812, fd=fd@entry=0x3, offset=0x0)
```

* Before the above mmap: 

```
7ffff7dd6000-7ffff7dfd000 r-xp 00000000 08:02 9465210                    /home/adwi/my_projects/blog_related/rev_eng_series/post_19/ld.so
7ffff7ff7000-7ffff7ffa000 r--p 00000000 00:00 0                          [vvar]
7ffff7ffa000-7ffff7ffc000 r-xp 00000000 00:00 0                          [vdso]
7ffff7ffc000-7ffff7ffe000 rw-p 00026000 08:02 9465210                    /home/adwi/my_projects/blog_related/rev_eng_series/post_19/ld.so
7ffff7ffe000-7ffff7fff000 rw-p 00000000 00:00 0                          [heap]
7ffffffdd000-7ffffffff000 rw-p 00000000 00:00 0                          [stack]
ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]
```

* After the above mmap: 

```
00400000-00401000 r-xp 00000000 08:02 9441559                            /home/adwi/my_projects/blog_related/rev_eng_series/post_19/hello
7ffff7dd6000-7ffff7dfd000 r-xp 00000000 08:02 9465210                    /home/adwi/my_projects/blog_related/rev_eng_series/post_19/ld.so
7ffff7ff7000-7ffff7ffa000 r--p 00000000 00:00 0                          [vvar]
7ffff7ffa000-7ffff7ffc000 r-xp 00000000 00:00 0                          [vdso]
7ffff7ffc000-7ffff7ffe000 rw-p 00026000 08:02 9465210                    /home/adwi/my_projects/blog_related/rev_eng_series/post_19/ld.so
7ffff7ffe000-7ffff7fff000 rw-p 00000000 00:00 0                          [heap]
7ffffffdd000-7ffffffff000 rw-p 00000000 00:00 0                          [stack]
ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]
```

Inside that while loop, all segments present in the opened shared object / executable are mapped.

To summarize what we have done so far, 

> The helper program loads the necessary segments of all the required files into memory.

1. ```_start```, ```_dl_start```, _dl_start_final```, ```_dl_sysdep_start``` do the necessary initializations for loading to start.

2. ```dl_main```: Mainly responsible for loading of executable-segments, segments of shared libraries etc.,

3. ```_dl_map_object```: Called with the ```filename```. This function resolves the given name into an **absolute path**, if it is name of a library, it searches in various places specified in ```LD_LIBRARY_PATH```, finds the file, opens it(gets the file descriptor) and finally calls ```_dl_map_object_from_fd``` to get the job done.

4. ```_dl_map_object_from_fd```: Identifies and gathers all **LOAD-type** segments present in the open file. Important metadata is collected about the open file and then passed to ```_dl_map_segments``` which gets the job done.

5. ```_dl_map_segments```: This is where the magic happens. All the LOAD-type segments are mapped onto memory here.


With that, I hope you have got some clarity over how segments of an object is loaded onto memory.

## 3. What about the dependencies?

We saw how an executable's segments get mapped. Every dynamically linked executable would have used functions from various shared libraries. So, there are objects our executable depends on.

So, the helper program should first finds out the dependencies of an object and then starts loading them.

The following is the gdb-backtrace of loading ```libc.so```.

```
gdb-peda$ bt
#0  __mmap64 (addr=addr@entry=0x0, len=len@entry=0x2000, prot=prot@entry=0x3, 
    flags=flags@entry=0x22, fd=fd@entry=0xffffffff, offset=offset@entry=0x0)
    at ../sysdeps/unix/sysv/linux/mmap64.c:51
#1  0x00007ffff7deed47 in malloc (n=0x4a2) at dl-minimal.c:73
#2  0x00007ffff7deee11 in calloc (nmemb=<optimized out>, size=size@entry=0x1)
    at dl-minimal.c:103
#3  0x00007ffff7de0daf in _dl_new_object (
    realname=0x7ffff7ffee80 "/lib/x86_64-linux-gnu/libc.so.6", 
    libname=0x400319 "libc.so.6", type=0x1, loader=0x7ffff7ffe1a0, mode=0x0, 
    nsid=0x0) at dl-object.c:89
#4  0x00007ffff7ddb973 in _dl_map_object_from_fd (name=0x400319 "libc.so.6", 
    origname=0x0, fd=0x3, fbp=0x7fffffffcd90, 
    realname=0x7ffff7ffee80 "/lib/x86_64-linux-gnu/libc.so.6", 
    loader=0x7ffff7ffe1a0, l_type=0x1, mode=0x0, stack_endp=0x7fffffffcd88, 
    nsid=0x0) at dl-load.c:996
#5  0x00007ffff7dde5da in _dl_map_object (loader=0x7ffff7ffe1a0, 
    name=0x400319 "libc.so.6", type=0x1, trace_mode=0x0, mode=<optimized out>, 
    nsid=<optimized out>) at dl-load.c:2218
#6  0x00007ffff7de2df2 in openaux (a=a@entry=0x7fffffffd320) at dl-deps.c:64
#7  0x00007ffff7def48b in _dl_catch_exception (
    exception=exception@entry=0x7fffffffd300, 
    operate=operate@entry=0x7ffff7de2dc0 <openaux>, 
    args=args@entry=0x7fffffffd320) at dl-error-skeleton.c:196
#8  0x00007ffff7de30a6 in _dl_map_object_deps (map=map@entry=0x7ffff7ffe1a0, 
    preloads=<optimized out>, npreloads=npreloads@entry=0x0, 
    trace_mode=trace_mode@entry=0x0, open_mode=open_mode@entry=0x0)
    at dl-deps.c:248
#9  0x00007ffff7dd9b63 in dl_main (phdr=<optimized out>, phnum=<optimized out>, 
    user_entry=<optimized out>, auxv=<optimized out>) at rtld.c:1797
#10 0x00007ffff7dee4af in _dl_sysdep_start (
    start_argptr=start_argptr@entry=0x7fffffffdaa0, 
    dl_main=dl_main@entry=0x7ffff7dd8270 <dl_main>) at ../elf/dl-sysdep.c:253
#11 0x00007ffff7dd7e26 in _dl_start_final (arg=0x7fffffffdaa0) at rtld.c:447
#12 _dl_start (arg=0x7fffffffdaa0) at rtld.c:537
#13 0x00007ffff7dd71f8 in _start ()
   from /home/adwi/my_projects/blog_related/rev_eng_series/post_19/ld.so
gdb-peda$
```

* Once an object's segments are loaded, it's dependencies are checked. Our executable has **libc** as a dependency. This is noted by the helper program and ```_dl_map_object_deps``` is called to take care of this.

* Refering to ```glibc/elf/dl-deps.c```: It says **Load the dependencies of a mapped object**.

* It can be seen that from the function ```_dl_map_object``` till ```mmap```, the procedure of mapping segments of a dependent library is similar(not same) to that of mapping segments of the executable. 

* The part which is unexplored is **how does the helper program gets to know all dependencies of a given executable**. This is something we need to focus on. We'll talk about this in detail in one of the later posts.

## 4. Difference between running ld.so as a program and invoking indirectly

We saw earlier that there are 2 ways to invoke the helper program. One by just running it like any other program, other is by running any dynamically linked program. 

What we explored so far in this post is the first scenario. We ran the helper program like a normal program, with our hello program as an argument to it. Is the same procedure followed when the program is run directly? Let us find out.

We saw that the helper program is given control first, and later the program is given control. So, Let us try breaking at ```_dl_start``` and ```_start```(This is user program's _start) and run it.

```
rev_eng_series/post_19: gdb -q -nh hello
Reading symbols from hello...(no debugging symbols found)...done.
(gdb) 
(gdb) b _start
Breakpoint 1 at 0x400430
(gdb) b _dl_start
Function "_dl_start" not defined.
Make breakpoint pending on future shared library load? (y or [n]) y
Breakpoint 2 (_dl_start) pending.
(gdb) 
```

* Let us run it.

```
(gdb) run ./hello
Starting program: /home/adwi/my_projects/blog_related/rev_eng_series/post_19/hello ./hello
warning: the debug information found in "/lib64/ld-2.23.so" does not match "/lib64/ld-linux-x86-64.so.2" (CRC mismatch).


Breakpoint 2, _dl_start (arg=0x7fffffffdaa0) at rtld.c:353
353	rtld.c: No such file or directory.
```

* Let us check the **maps** file. 

```
rev_eng_series/post_19: cat /proc/16240/maps
00400000-00401000 r-xp 00000000 08:02 9441559                            /home/adwi/my_projects/blog_related/rev_eng_series/post_19/hello
00600000-00602000 rw-p 00000000 08:02 9441559                            /home/adwi/my_projects/blog_related/rev_eng_series/post_19/hello
7ffff7dd7000-7ffff7dfd000 r-xp 00000000 08:02 25694777                   /lib/x86_64-linux-gnu/ld-2.23.so
7ffff7ff7000-7ffff7ffa000 r--p 00000000 00:00 0                          [vvar]
7ffff7ffa000-7ffff7ffc000 r-xp 00000000 00:00 0                          [vdso]
7ffff7ffc000-7ffff7ffe000 rw-p 00025000 08:02 25694777                   /lib/x86_64-linux-gnu/ld-2.23.so
7ffff7ffe000-7ffff7fff000 rw-p 00000000 00:00 0 
7ffffffdd000-7ffffffff000 rw-p 00000000 00:00 0                          [stack]
ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]
```

* So, even before the helper program starts to execute, the LOAD-type segments of our executable have already been mapped. After a bunch of ```mmap```s, the breakpoint at ```_start``` kicked in.

```
(gdb) c
Continuing.

Breakpoint 1, 0x0000000000400430 in _start ()
```

With this, we know that there is a difference between the 2 ways of running the helper program. If the helper program is directly run, only it, stack, heap etc., are loaded onto memory by the Operating System. But when the user program is run, the Operating System loads the user program's segments, the helper program's segments, stack, heap etc., . The helper program's job is to identify the libraries the user program depends on and then load them.

There is one more point to note here. Referring to the **Usage** note that the helper program threw, 
```
rev_eng_series/post_19: /lib64/ld-linux-x86-64.so.2 
Usage: ld.so [OPTION]... EXECUTABLE-FILE [ARGS-FOR-PROGRAM...]
You have invoked `ld.so', the helper program for shared library executables.
This program usually lives in the file `/lib/ld.so', and special directives
in executable files using ELF shared libraries tell the system's program
loader to load the helper program from this file.  This helper program loads
the shared libraries needed by the program executable, prepares the program
to run, and runs it.  You may invoke this helper program directly from the
command line to load and run an ELF executable file; this is like executing
that file itself, but always uses this helper program from the file you
specified, instead of the helper program file specified in the executable
file you run.  This is mostly of use for maintainers to test new versions
of this helper program; chances are you did not intend to run this program.
```

* Read the last part.
> You may invoke this helper program directly from the
command line to load and run an ELF executable file; this is like executing
that file itself, but **always uses this helper program** from the file you
specified, **instead of the helper program file specified in the executable**
file you run.  This is mostly of use for maintainers to test new versions
of this helper program; chances are you did not intend to run this program.

* So, when the helper program is run directly, **IT** is used to setup the execution and **NOT** the one specified inside the **INTERP** segment of the executable. This didn't matter in the examples I took because I was using the helper program same as specified in any executable on my machine - ```/lib64/ld-linux-x86-64.so.2```. But when new versions of the helper program are written, this method is used. I think this is a very important to make note of.

## 5. How exactly is control transferred from ld.so to the user program?

We have seen how the control always goes to the helper program first and only then to the user program. But we didn't see how exactly the transfer of control would happen. 

Let us have a look at the helper program's ```_start``` code.

```c
/* Initial entry point code for the dynamic linker.
   The C function `_dl_start' is the real entry point;
   its return value is the user program's entry point.  */
#define RTLD_START asm ("\n\
.text\n\
        .align 16\n\
.globl _start\n\
.globl _dl_start_user\n\
_start:\n\
        movq %rsp, %rdi\n\
        call _dl_start\n\
_dl_start_user:\n\
        # Save the user entry point address in %r12.\n\
        movq %rax, %r12\n\
        # See if we were run as a command with the executable file\n\
        # name as an extra leading argument.\n\
        movl _dl_skip_args(%rip), %eax\n\
        # Pop the original argument count.\n\
        popq %rdx\n\
        # Adjust the stack pointer to skip _dl_skip_args words.\n\
        leaq (%rsp,%rax,8), %rsp\n\
        # Subtract _dl_skip_args from argc.\n\
        subl %eax, %edx\n\
        # Push argc back on the stack.\n\
        pushq %rdx\n\
        # Call _dl_init (struct link_map *main_map, int argc, char **argv, char **env)\n\
        # argc -> rsi\n\
        movq %rdx, %rsi\n\
        # Save %rsp value in %r13.\n\
        movq %rsp, %r13\n\
        # And align stack for the _dl_init call. \n\
        andq $-16, %rsp\n\
        # _dl_loaded -> rdi\n\
        movq _rtld_local(%rip), %rdi\n\
        # env -> rcx\n\
        leaq 16(%r13,%rdx,8), %rcx\n\
        # argv -> rdx\n\
        leaq 8(%r13), %rdx\n\
        # Clear %rbp to mark outermost frame obviously even for constructors.\n\
        xorl %ebp, %ebp\n\
        # Call the function to run the initializers.\n\
        call _dl_init\n\
        # Pass our finalizer function to the user in %rdx, as per ELF ABI.\n\
        leaq _dl_fini(%rip), %rdx\n\
        # And make sure %rsp points to argc stored on the stack.\n\
        movq %r13, %rsp\n\
        # Jump to the user's entry point.\n\
        jmp *%r12\n\
.previous\n\
");
```

* The code looks a little cluttered, but there are comments almost for every assembly instruction which is helpful.
* ```_dl_start``` returns the **User program's starting address**. A return value is always stored in the ```rax``` register.
* The Return address is stored in ```r12``` register before proceeding. You can see the following: 

```c
_dl_start_user:\n\
        # Save the user entry point address in %r12.\n\
        movq %rax, %r12\n\
```

* ```_dl_init``` is called - which will call the initializers. We'll see what this is in one of the future posts.

* Finally, there is a ```jmp r12``` instruction and we enter the user program.

## 6. How does the helper program get control in the first place?

We saw that in any case, the helper program is the first entity to get control. But for that to happen, the helper program's segments need to be mapped onto memory, along with providing stack, vvar, vdso, vsyscall address-spaces. And finally control is transferred to ```_start``` of helper program.

Who does this?

The Operating System does. As of now, I don't have a code-level understanding of how this happens. I have read that the OS is responsible for this.

As the series progresses, we'll read Linux sourcecode to understand these things.

## 7. Conclusion

I hope you have got some idea on how segments from an object(executable / shared object) is loaded to main memory. 

The helper program is quite a complex program to describe in a single post. 

We are not clear as to how the helper program identifies all the dependencies of an object(an executable or a shared object).

We came across some interesting data structures like ```struct link_map```, **Auxillary vector**, ```struct filebuf```, ```struct loadcmd``` etc., and all functions revolve around these data structures.

We have some idea about **loading** of necessary objects. But we have not yet explored how a library function can be called from a user program. We don't know how exactly **dynamic linking** works.

We also saw don't know how exactly the OS loads the helper program, stack, vvar etc., before transferring control the it.

So we have a lot to explore. We'll take up all the above topics in future posts.

That is for now.

Thank you for reading!

-------------------------------------------------------------------
