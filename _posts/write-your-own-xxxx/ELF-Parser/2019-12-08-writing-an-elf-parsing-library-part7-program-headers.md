---
title: Writing an ELF Parsing Library - Part - Program Headers
categories: write your own XXXX
layout: post
comments: true
---

Hello Friend!

In the [previous article](/write/your/own/xxxx/2019/12/07/writing-an-elf-parsing-library-part6-the-elf-header.html), we explored the ELF header. We came across something called as **Program Header Table**.

In this article, we'll be discussing about **Program Headers**, **Program Header Table**, **Segments**, on how they are essential for a program's execution.

Lets start!

## 0. Introduction

There are 4 ELF file types - ```EXEC```, ```DYN```, ```CORE``` and ```REL```.

The executables and shared objects are the ELF files which can be **run**. Object files cannot be run, neither can core files.

These ELF files(```EXEC``` and ```DYN``` types) are divided into **Segments**. Each of these segments is essential for its execution. Note that Object files and core files don't have the concept of Segments.

The entire discussion in today's article is related to **EXEC** and **DYN** types.

When an entity(like OS or our library) tries to process the Segments, we need to know where that segment is present inside the ELF file, what are its permissions, what it contains.

All this metadata about a segment is present in a **Program Header**. Generally there are multiple segments in an ELF file. So, we need an array of these Program Headers to describe all the segments. This array of Program Headers is called **Program Header Table**.

Let us take a simple example to understand why segments are essential, what these Program Headers contain that make them important.

Consider the following program:

```c
$ cat hello.c
#include <stdio.h>
#include <unistd.h>

int main()
{
	printf("Hello!\n");
	printf("My PID: %d\n", getpid());

	while(1);
}
$ gcc hello.c -o hello
$ ./hello
Hello!
My PID: 3176
^C
```

* It is a simple program which tells its ```pid``` and goes into an infinite loop.

Run it.

```
$ ./hello
Hello!
My PID: 3220

```

Let us look at its ```/proc/PID/maps``` file. This file has the complete memory layout of this program. What is present at what address, what are its permissions and more.

```
$ cat /proc/3220/maps
560e00acf000-560e00ad0000 r-xp 00000000 08:05 7209412                    /home/dell/Documents/pwnthebox/exp/hello
560e00ccf000-560e00cd0000 r--p 00000000 08:05 7209412                    /home/dell/Documents/pwnthebox/exp/hello
560e00cd0000-560e00cd1000 rw-p 00001000 08:05 7209412                    /home/dell/Documents/pwnthebox/exp/hello
560e012a7000-560e012c8000 rw-p 00000000 00:00 0                          [heap]
7f46290b4000-7f462929b000 r-xp 00000000 08:05 13112024                   /lib/x86_64-linux-gnu/libc-2.27.so
7f462929b000-7f462949b000 ---p 001e7000 08:05 13112024                   /lib/x86_64-linux-gnu/libc-2.27.so
7f462949b000-7f462949f000 r--p 001e7000 08:05 13112024                   /lib/x86_64-linux-gnu/libc-2.27.so
7f462949f000-7f46294a1000 rw-p 001eb000 08:05 13112024                   /lib/x86_64-linux-gnu/libc-2.27.so
7f46294a1000-7f46294a5000 rw-p 00000000 00:00 0 
7f46294a5000-7f46294cc000 r-xp 00000000 08:05 13111996                   /lib/x86_64-linux-gnu/ld-2.27.so
7f46296b4000-7f46296b6000 rw-p 00000000 00:00 0 
7f46296cc000-7f46296cd000 r--p 00027000 08:05 13111996                   /lib/x86_64-linux-gnu/ld-2.27.so
7f46296cd000-7f46296ce000 rw-p 00028000 08:05 13111996                   /lib/x86_64-linux-gnu/ld-2.27.so
7f46296ce000-7f46296cf000 rw-p 00000000 00:00 0 
7fff06fd1000-7fff06ff2000 rw-p 00000000 00:00 0                          [stack]
7fff06ffb000-7fff06ffe000 r--p 00000000 00:00 0                          [vvar]
7fff06ffe000-7fff07000000 r-xp 00000000 00:00 0                          [vdso]
ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]
```

Let us closely go through this output.

**1.** The first address space has permissions ```r-x``` - Read and Execute. This mostly has our code in it.
**2.** The second has permissions ```r--```. This has all the **read-only** data in it. 
**3.** Next is the place where global variables reside.

**4.** And then there is ```libc``` mapped onto our program's address space. How did anyone know we used C library functions?
**5.** Then there is something called ```ld-2.27.so```. What is this? Why is it present?

How is this memory layout structured like this?

Who specified the address ranges and permissions to each of those address spaces belonging to our program? If ```libc``` is mapped, then the fact that our program uses C library functions should be stored somewhere in our executable right?

All this happens because of **Program Headers**. Each of our ```hello``` program's address spaces is a **segment** present inside the executable. Where can the loader find that segment in the file, the address where it should be mapped, the permissions that mapping needs to be given etc., all these details about a segment are present in the **Program Header**.

And there are multiple segments. To cover them, we have a **Program Header Table**.

I hope you have got some idea about what Program Header Table is. I am sure you'll get more clarity as you read through the article.

Create a new C sourcefile ```elfp_phdr.c``` in ```src``` directory. All the code related to Program Headers are going into that file.

## 1. Understanding the Program Header

First of all, why is it even called Program header?

It is short for **Program Segment Header**. Every Program is divided into Segments, and each Segment has a header. And that header is known as Program Segment Header.

What all does a **Program Header** have? Lets take a look at the 64-bit structure. You can refer ```elf.h``` or ```elf```'s manpage to get it.

```c
typedef struct
{
  Elf64_Word    p_type;                 /* Segment type */
  Elf64_Word    p_flags;                /* Segment flags */
  Elf64_Off     p_offset;               /* Segment file offset */
  Elf64_Addr    p_vaddr;                /* Segment virtual address */
  Elf64_Addr    p_paddr;                /* Segment physical address */
  Elf64_Xword   p_filesz;               /* Segment size in file */
  Elf64_Xword   p_memsz;                /* Segment size in memory */
  Elf64_Xword   p_align;                /* Segment alignment */
} Elf64_Phdr;
```

To understand Program Headers properly, we'll have to explore each of these members in detail.

### a. **p_type**: Segment type

There are various types of segments. Each segment has an important part of the executable. Let us take a look at the types.

```c
/* Legal values for p_type (segment type).  */

#define PT_NULL         0               /* Program header table entry unused */
#define PT_LOAD         1               /* Loadable program segment */
#define PT_DYNAMIC      2               /* Dynamic linking information */
#define PT_INTERP       3               /* Program interpreter */
#define PT_NOTE         4               /* Auxiliary information */
#define PT_SHLIB        5               /* Reserved */
#define PT_PHDR         6               /* Entry for header table itself */
#define PT_TLS          7               /* Thread-local storage segment */
#define PT_NUM          8               /* Number of defined types */
#define PT_LOOS         0x60000000      /* Start of OS-specific */
#define PT_GNU_EH_FRAME 0x6474e550      /* GCC .eh_frame_hdr segment */
#define PT_GNU_STACK    0x6474e551      /* Indicates stack executability */
#define PT_GNU_RELRO    0x6474e552      /* Read-only after relocation */
#define PT_LOSUNW       0x6ffffffa
#define PT_SUNWBSS      0x6ffffffa      /* Sun Specific segment */
#define PT_SUNWSTACK    0x6ffffffb      /* Stack segment */
```

**1. PT_LOAD**: Loadable program segment

There are a few segments which need to be **loaded into main memory** for the program to execute.

The segment which contains **code** is a Loadable program segment. The one which contains **read-only** data is a Loadable program segment. The segment which contains global variables is Loadable.

Let us take a look at the first few entries of ```/proc/PID/maps``` again.

```
560e00acf000-560e00ad0000 r-xp 00000000 08:05 7209412                    /home/dell/Documents/pwnthebox/exp/hello
560e00ccf000-560e00cd0000 r--p 00000000 08:05 7209412                    /home/dell/Documents/pwnthebox/exp/hello
560e00cd0000-560e00cd1000 rw-p 00001000 08:05 7209412                    /home/dell/Documents/pwnthebox/exp/hello
```

Look at these. These 3 address spaces are basically 3 ```PT_LOAD``` type segments loaded into memory. As we parse the Program Header Table, you'll realize this.

**2. PT_DYNAMIC**: Dynamic Linking information

How do we use library functions like ```printf()```, ```scanf()```, ```getpid()``` etc.,?

It is through this beautiful mechanism called **Dynamic Linking**. The code for these functions are present in some other library. But when the call to ```printf()``` happens, you jump to that library and execute ```printf()```.

How do we know what library these functions are present in? The linker by default put ```libc```'s info in an executable, unless asked not to.

To use math functions or the pthread library, you would have compiled your program with ```-lm``` and ```-lpthread``` options respectively. Here, you are informing the linker that have used functions in the math library or the pthread library and you want that information inside your executable.

How will this information present in your executable help?

Let us write a small program to understand this. Take a program which uses a math function.

```c
$ cat math.c
#include <stdio.h>
#include <math.h>

int main()
{
	float x = 1.2234;
	printf("sin(%f) = %lf\n", x, sin(x));

    while(1); /* Helps in experimenting */
}
```

Let us compile it normally.

```
$ gcc math.c -o math
/tmp/ccI3N4Dh.o: In function `main':
math.c:(.text+0x1b): undefined reference to `sin'
collect2: error: ld returned 1 exit status
```

It doesn't know where to find the definition of ```sin()``` function. But we know it is present in the math library. We'll link it with the math library.

```
$ gcc math.c -o math -lm
$ ls -l math
-rwxr-xr-x 1 dell dell 8344 Dec  8 12:32 math
```

Let us run it.

```
$ ./math
sin(1.223400) = 0.940262

```

We are more interested in the libraries loaded into the memory layout. Let us take a look at it.

```
$ ps -e | grep math
 6322 pts/0    00:00:50 math
```

Lets take a look at its maps file.

```
$ cat /proc/6322/maps
55b397dc2000-55b397dc3000 r-xp 00000000 08:05 7209466                    /home/dell/Documents/pwnthebox/exp/math
55b397fc2000-55b397fc3000 r--p 00000000 08:05 7209466                    /home/dell/Documents/pwnthebox/exp/math
55b397fc3000-55b397fc4000 rw-p 00001000 08:05 7209466                    /home/dell/Documents/pwnthebox/exp/math
55b399e92000-55b399eb3000 rw-p 00000000 00:00 0                          [heap]
7fb386acc000-7fb386cb3000 r-xp 00000000 08:05 13112024                   /lib/x86_64-linux-gnu/libc-2.27.so
7fb386cb3000-7fb386eb3000 ---p 001e7000 08:05 13112024                   /lib/x86_64-linux-gnu/libc-2.27.so
7fb386eb3000-7fb386eb7000 r--p 001e7000 08:05 13112024                   /lib/x86_64-linux-gnu/libc-2.27.so
7fb386eb7000-7fb386eb9000 rw-p 001eb000 08:05 13112024                   /lib/x86_64-linux-gnu/libc-2.27.so
7fb386eb9000-7fb386ebd000 rw-p 00000000 00:00 0 
7fb386ebd000-7fb38705a000 r-xp 00000000 08:05 13112087                   /lib/x86_64-linux-gnu/libm-2.27.so
7fb38705a000-7fb387259000 ---p 0019d000 08:05 13112087                   /lib/x86_64-linux-gnu/libm-2.27.so
7fb387259000-7fb38725a000 r--p 0019c000 08:05 13112087                   /lib/x86_64-linux-gnu/libm-2.27.so
7fb38725a000-7fb38725b000 rw-p 0019d000 08:05 13112087                   /lib/x86_64-linux-gnu/libm-2.27.so
7fb38725b000-7fb387282000 r-xp 00000000 08:05 13111996                   /lib/x86_64-linux-gnu/ld-2.27.so
7fb387467000-7fb38746c000 rw-p 00000000 00:00 0 
7fb387482000-7fb387483000 r--p 00027000 08:05 13111996                   /lib/x86_64-linux-gnu/ld-2.27.so
7fb387483000-7fb387484000 rw-p 00028000 08:05 13111996                   /lib/x86_64-linux-gnu/ld-2.27.so
7fb387484000-7fb387485000 rw-p 00000000 00:00 0 
7ffe1c83b000-7ffe1c85c000 rw-p 00000000 00:00 0                          [stack]
7ffe1c96e000-7ffe1c971000 r--p 00000000 00:00 0                          [vvar]
7ffe1c971000-7ffe1c973000 r-xp 00000000 00:00 0                          [vdso]
ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]
```

Look at that. It has ```libm```, which is the math library.

You can checkout the **strings** present in ```math``` executable. It should have the string ```libm.so``` in it.

```
$ strings math | grep lib
/lib64/ld-linux-x86-64.so.2
libm.so.6
libc.so.6
__libc_start_main
__libc_csu_fini
__libc_start_main@@GLIBC_2.2.5
__libc_csu_init
```

Note the second and third entry. They are the libraries this executable depends on.

So, a **PT_DYNAMIC** segment has all the information needed to make Dynamic Linking work properly. The list of dependent libraries is just one piece of information. Lot of other information is needed to make Dynamic Linking work which we didnt't discuss here. We'll discuss about **PT_DYNAMIC** segment in detail in future articles.

Note that this segment is present only in executables/shared objects which are dynamically linked.

**3. PT_INTERP**: Program Interpreter

We disussed that the **PT_LOAD** segments are loaded into memory, the **PT_DYNAMIC** segment is processed to get the list of dependent libraries and they are loaded into memory.

Later, when ```printf()``` is called, code present in ```libc``` is executed seamlessly. 

Who is doing all this? Who is loading these segments, libraries? Who is making Dynamic Linking work?

It is the **Program Interpreter**. It has various names. It is called the **Loader**, the **Dynamic Linker**. The ```ld-2.27.so``` which you saw in one of the maps file is this.

In the **PT_INTERP** segment, the path to the Program Interpreter is specified. It is invoked by the OS and then the Interpreter does its job. ```/lib64/ld-linux-x86-64.so.2``` is the defeult interpreter on my machine. I have written [this article](/reverse/engineering/and/binary/exploitation/series/2019/11/10/understanding-the-loader-part1-how-does-an-executable-get-loaded-to-memory.html) on how the Loader works in detail. You may go through it if you are interesting in learning how exactly various objects are loaded and a program is executed.

**4. PT_NOTE**: Auxillary information

Any information can be stored here. Normally, the **OS-ABI version** and **Build-ID** is present as notes. **PT_NOTE** is a segment with a lot of interesting things in itself. We'll be discussing about it in detail in future articles.

**5. PT_PHDR**: Header for the Program Header Table

This Program Header has info related to the Program Header Table. What all is needed to parse the Program Header Table?

Its **location** in the file and its **size** (which will indirectly tell us how many Program Headers are present). These two details are present in this header.

Note that there is **no** segment associated with this Program Header. This is a header present to help us process the PHT properly.

**6. PT_TLS**: Thread Local Storage segment

Normally, your program has one single data segment. The data segment is complete devoted to the only thread present.

But in multi-threaded programs, each thread would needs its own data segment. A thread's "own data segment" is called **Thread Local Storage or TLS**.

This segment gives a template on how the **Thread Local Storage** should look in memory. I am not very clear on what this segment is, data structures associated with it. I'll update this article once I get clarity on this. You can [read this](http://www.sco.com/developers/gabi/latest/ch5.pheader.html#tls) for some more info on TLS segment.

**7. PT_GNU_EH_FRAME**: GCC .eh_frame_hdr segment

We'll discuss more about this segment when we talk about ```.eh_frame```, ```.eh_frame_hdr``` sections.

**8. PT_GNU_STACK**: Indicates stack executability

When you run ```./a.out```, the first thing which happens is that the OS look at the **PT_INTERP** segment, looks at the Program Interpreter path. **The OS loads the Interpreter into memory**. The OS sets up a basic memory and hands over control to the interpreter.

This basic memory layout consists of **stack**, **heap**, **vvar**, **vsyscall**, **vdso** and the interpreter **ld-2.27.so** itself. Note that at this point, our executable ```a.out``` is not yet loaded into memory.

The **stack** setup by the OS comes with ```rw-``` permissions - We can read and write data, but not execute anything.

Gradually when the loader loads your executable, dependent libraries etc., and preps for ```a.out```'s execution, one thing it does is check what type of stack does ```a.out``` wants. At the end of the day, this **stack** belongs to the executable.

Does ```a.out``` need a stack with ```rw-``` permission, or does it need the stack to have some other permissions, like ```rwx``` or ```r--```. This information of what the stack's permissions should be is present in ```PT_GNU_STACK``` header.

First, the stack belonged to the Program Interpreter and it worked with default permissions(**rw-**). Later, the stack is handed over to the executable to use. So, stack permissions should be what the executable wants it to be. The executable uses **PT_GNU_STACK** header to specify the stack permissions.

One point to note is, there is **no segment** corresponding to this header. It is a header specifically used to convey stack permissions and nothing more.

If you want to learn more about this, you can explore this took called ```execstack```. It manipulates this Program Header to make stack executable.

**9. PT_GNU_RELRO**: Read Only after relocation

This header is related to dynamic linking. 

What does dynamic linking mean?

What does linking mean? Linking is the process of stitching various object(or relocatable) files and giving addresses to every byte. Once the addresses are given to every byte, it means that the object files have been linked successfully.

Now, what does dynamic linking mean?

Normally, when we write a function, that function gets a permanent address once linking is done. But what about ```printf()``` which we have used in our program, but have not written it? It is present in ```libc``` shared object.

When ```printf()``` is called, its address is found out at runtime(or it is relocated / linked) with the help of dynamic linker and its address is then used.

What if ```printf()``` is called again? It would be inefficient to find its address again. Instead, the address is stored in a table. When ```printf()``` was called, the address is picked from this table and jumped to. Note that we can read and write into this table => its permissions are ```rw-```.

This method works, however it is vulnerable to attacks under certain conditions.

Suppose there is a vulnerability which allows me to **write whatever I want wherever I want**. So, I can write anything at any address.

I can make the program do unindended stuff with this.

1. Write ```exit()``` function's address in place of ```printf()```'s address in that table. So, the next time ```printf()``` is called by the program, it is actually never called. Instead, ```exit()``` is called and program is terminated.

There are deadly exploits present which help attackers give control over the machine, with these vulnerabilities combined.

Security researchers came up with a simple solution for this. 

Once relocation is done for ```printf()``` and its address is written into that table, make that entry **Read-Only**. This way, even if an attacker tries writing there, the program crashes but attacker is not given control of the system. It is aptly described as **Read Only after Relocation**.

It is the programmer's choice, whether to have this security measure in place or not. If he wants the security measure, then he can do so by introducing this new Program Header of type **PT_GNU_RELRO**. Again, this header doesn't have a corresponding segment. It is just a means to convey the **RELRO** message to the linker.

**10. PT_SUNWBSS & PT_SUNWSTACK** are types specific to **Sun Solaris** Systems. I am guessing that the **PT_SUNWSTACK** is similar to **PT_GNU_STACK**, but for Sun systems instead of GNU systems. I'll explore more on this and update this article.

With that, we have seen the various Segment types. It can be seen that these headers are mainly used to make the program run properly - **PT_LOAD**, **PT_DYNAMIC**, **PT_INTERP**. But, they are also used for a different purpose - just convey a message to the linker. **PT_GNU_STACK** informs the linker about the stack permissions the programmer wants for his application. **PT_GNU_RELRO** tells the linker either to enable the **Read-Only after relocation** security measure.

Let us move to the next member in the Program Header.

### b. **p_flags**: Segment flags

These are basically the security permissions of that segment. The following are possible flags:

```c
#define PF_X            (1 << 0)        /* Segment is executable */
#define PF_W            (1 << 1)        /* Segment is writable */
#define PF_R            (1 << 2)        /* Segment is readable */
```

The ```p_flags```member obviously can be any combination of the above flags.

### c. **p_offset**: Segment file offset

Where can I find the segment corresponding to a Program Header? It can be found at **p_offset** bytes from the beginning of ELF file.

### d. **p_vaddr**: Segment Virtual Address

This is the Virtual Address given to this segment. This address is where this particular segment would be present in the memory layout.

### e. **p_paddr**: Segment Physical Address

Whenever we talk about addresses in user space, we are in most cases talking about Virtual Addresses.

Physical Address if the actual address/location in RAM where some data is found. This is NEVER exposed to userspace applications. So, ```p_paddr``` will mostly have the Virtual Address itself.

### f. **p_filesz**: Segment size in file

How big is the segment in file? ```p_filesz``` will tell us that.

### g. **p_memsz**: Segment size in memory

IF the segment is loaded into memory, how much memory will it take? That is specified by ```p_memsz```. With the experimentation I have done so far, ```p_filesz``` has always been equal to ```p_memsz```.

### h. **p_align**: Segment Alignment

At what boundary should this segment reside?

This member has the value to which the segment is aligned in memory and in the file.

I hope you got an idea of what a Program Header is, what it can contain, its members etc.,

```elf```'s manpage has a gist of what we discussed so far. I suggest you to go through it once.

Now that we understand the structure of a Program Header, let us write code to parse it.

## 2. Decode functions for members in encoded form

Before we parse the Program Header, there are members which are in encoded form and need decode functions. Let us write them.

These decode functions can be used by the programmer if he wishes to write his own dump function. So, put the declarations in ```elfp.h``` and definitions in the new sourcefile ```elfp_phdr.c```.

### a. **p_type**: Segment type

The following is the declaration.

```c
/*
 * elfp_phdr_decode_type: Decodes the Segment type
 * 
 * @arg0: Segment type     
 * 
 * @return: Decoded string.        
 */
const char*
elfp_phdr_decode_type(unsigned long int type);
```

Implementation is simple.

```c
const char*
elfp_phdr_decode_type(unsigned long int type)
{
        switch(type)
        {
                case PT_NULL:
                        return "NULL (Program Header unused)";

                case PT_LOAD:
                        return "LOAD (Loadable program segment)";

                case PT_DYNAMIC:
                        return "DYNAMIC (Dynamic Linking information)";
.
.
.
                case PT_GNU_RELRO:
                        return "GNU_RELRO (Read-only after relocation)";

                case PT_SUNWBSS:
                        return "SUNWBSS (Sun Specific segment)";

                case PT_SUNWSTACK:
                        return "SUNWSTACK (Stack segment)";

                /* Anything else is invalid */
                default:
                        return "Invalid type";
        }
}
```

### b. **p_flags**: Security permissions

There are 3 flags:

```c
#define PF_X            (1 << 0)        /* Segment is executable */
#define PF_W            (1 << 1)        /* Segment is writable */
#define PF_R            (1 << 2)        /* Segment is readable */
```

```p_flags``` can be any combination of the above 3 values.

Write the decode function for this.

## 3. A small detour

To parse a Program Header properly, we should know if the ELF file is 32-bit or 64-bit object.

We'll be needing this info in many places. We'll add ```class``` to ```elfp_main``` structure - so that it is available and won't have to find out every time we need it.

Whre do we update it? I am thinking of updating it in ```elfp_main_create()``` so that the ELF's class is available for all later operations.

We'll need to write a ```get()``` function for it.

```c
unsigned long int
elfp_main_get_class(elfp_main *main)
{       
        /* Basic check */
        if(main == NULL)
        {       
                elfp_err_warn("elfp_main_get_class", "NULL argument passed");
                return ELFCLASSNONE;
        }
        
        return main->class;
}
```

## 4. Dump function for Program Header

The programmer will use the ```handle``` to identify the ELF file. We know that there may be multiple Program Headers in an ELF file. So, the programmer will also have to pass the ```index``` of the Program Header he wants to be dumped. Let us call the function ```elfp_phdr_dump()```.

```c
/*
 * elfp_phdr_dump:
 *
 * @arg0: Handle
 * @arg1: Program Header's index in the Program Header table.
 *
 * @return: 0 on success, -1 on failure.
 */
int
elfp_phdr_dump(int handle, int index);
```

Let us implement it.

**1.** Sanitize the handle

```c
int
elfp_phdr_dump(int handle, int index)
{
        int ret;
        unsigned long int class;
        elfp_main *main = NULL;

        /* Sanitize the handle */
        ret = elfp_sanitize_handle(handle);
        if(ret == -1)
        {
                elfp_err_warn("elfp_phdr_dump", "Handle failed sanity test");
                return -1;
        }
```

**2.** We'll have to parse a Program Header based on its class. So, we'll have 2 more functions ```elfp_p32hdr_dump()``` and ```elfp_p64hdr_dump()``` to dump 32-bit and 64-bit Program Headers respectively.

Get the class.

```c
        main = elfp_main_vec_get_em(handle);
        if(main == NULL)
        {
                elfp_err_warn("elfp_phdr_dump", "elfp_main_vec_get_em() failed");
                return -1;
        }

        class = elfp_main_get_class(main);
```

Call the right dump function.

```c
        ehdr = (Elf64_Ehdr *)elfp_main_get_staddr(main);
        phnum = ehdr->e_phnum;  

        /* Sanitize the index */
        if(index < 0 || index > phnum)  
                        elfp_p64hdr_dump(main, index);
                        break;
                
                /* All invalid cases are considered as 64-bit objects */
                default:
                        elfp_p64hdr_dump(main, index);
        }
        
        return 0;
}
```

We'll implement ```elfp_p64hdr_dump()``` here. The 32-bit version is very similar.

### **elfp_p64hdr_dump()**: Dumping a 64-bit Program Header

**1.** First thing to do is sanitize the index. We'll have the same problem we had with unsanitized handle if we don't do it.

```c
int
elfp_p64hdr_dump(elfp_main *main, int index)
{
        Elf64_Ehdr *ehdr = NULL;
        unsigned int phnum;  
        Elf64_Phdr *phdr = NULL;
        unsigned int i;

        ehdr = (Elf64_Ehdr *)elfp_main_get_staddr(main);
        phnum = ehdr->e_phnum;  

        /* Sanitize the index */
        if(index < 0 || index >= phnum)  
        {
                elfp_err_warn("elfp_p64hdr_dump", "Index failed the sanity test");
                return -1;
        }
```

**2.** Get the requested Program Header.

```c
        /* Get the header */
        phdr = (Elf64_Phdr *)((unsigned char *)ehdr + ehdr->e_phoff);
        phdr = phdr + index;
```

**3.** Dump them.

* Type
    
    ```c
        /* Dump them */
        i = 0;
        
        /* Type */
        printf("%02u. Type: %s\n", i++, elfp_phdr_decode_type(phdr->p_type));

    ```

* Flags
    
    ```c
        /* Flags */
        printf("%02u. Flags: %s\n", i++, elfp_phdr_decode_flags(phdr->p_flags));
    ```

* Offset

    ```c
        /* Segment file offset */
        printf("%02u. Segment file offset: %lu bytes\n", i++, phdr->p_offset);
    ```

* Virtual Address

    ```c
        /* Virtual Address */
        printf("%02u. Virtual Address: 0x%lx\n", i++, phdr->p_vaddr);
    ```

I want you to write the rest.

With that, we have function to parse any given Program Header.

## 6. Integrating this into the library

Now, we have the functionality of parsing any given Program Header. We need to add this to the library.

To do this, we need to compile ```elfp_phdr.c``` and make it part of ```libelfp.so```. The following is the updated build rule present in **Makefile**.

```
build: 
        # Building the library
        $(CC) elfp_int.c elfp_basic_api.c elfp_ehdr.c elfp_phdr.c -c -fPIC $(CFLAGS)
        $(CC) elfp_int.o elfp_basic_api.o elfp_ehdr.o elfp_phdr.o -shared $(CFLAGS) -o libelfp.so
        mkdir build
        mv libelfp.so *.o build
```

## 7. Testing our implementation

Write a few C programs using our implementation. Checkout [check_elfp_phdr.c](https://github.com/write-your-own-XXXX/ELF-Parser/blob/master/examples/check_elfp_phdr.c).

## 8. Conclusion

We'll end this article here.

We discussed what a Program Header is, various types of Program Headers - each of their uses, different security permissions a Header can have and more.

We also wrote functions to parse a given Program Header. The programmer has 2 new API functions: ```elfp_phdr_dump()``` and ```elfp_phdr_get()``` along with a few decode functions.

There are a few parts which I didn't implement in this article. They are an exercise for you to complete.

You can find the code we have written so far [here](https://github.com/write-your-own-XXXX/ELF-Parser/releases/tag/Part7).

I hope you have understood what Program Headers are.

In the next article, we'll be exploring the **Program Header Table** in detail.

Thank you for reading!

--------------------------------------------------
[Go to next article: Writing an ELF Parsing Library - Part8 - Program Header Table](/404.html).          
[Go to previous article: Writing an ELF Parsing Library - Part6 - The ELF Header](/write/your/own/xxxx/2019/12/07/writing-an-elf-parsing-library-part6-the-elf-header.html)






