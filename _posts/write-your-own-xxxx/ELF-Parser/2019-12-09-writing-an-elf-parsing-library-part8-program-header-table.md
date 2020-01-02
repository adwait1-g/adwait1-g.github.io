---
title: Writing an ELF Parsing Library - Part8 - Program Header Table
categories: write your own XXXX
layout: post
comments: true
---

Hello Friend!

In the [previous article](/write/your/own/xxxx/2019/12/08/writing-an-elf-parsing-library-part7-program-headers.html), we discussed about Program Headers in detail. We also wrote code to parse any given Program Header.

In this article, we'll talk about **Program Header Table**, an array of Program Headers present in **runnable** ELF files like ```EXEC``` and ```DYN```.

## 0. Introduction

For a program to run properly, various things are needed.

1. Need code, global variables, all the read-only data present.
2. If the ELF file is dynamically linked, we'll need all info related to it, so that the Dynamic Linker can be prepared.
3. If the programmer wants to add any security measure like ```RELRO``` or inform the linker about Stack executability, a Program Header is used.

Each of these is present in the ELF file as a **segment**. So, there are multiple segments => We need multiple Program Headers to describe them. And thus, we have our **Program Header Table**.

We'll be using a lot of what we discussed in the [previous article](/write/your/own/xxxx/2019/12/08/writing-an-elf-parsing-library-part7-program-headers.html). Its best if you go through it before you go to the next section.

## 1. Parsing the Program Header Table

We now know that the **Program Header Table** is simply an array of Program Headers. How do we parse this?

Simple.

1. Get the starting address of the Program Header Table.
2. Get the total number of Program Headers present in the table.
3. Iterate through the table and dump all the headers using the parse function ```elfp_phdr_dump()``` we wrote in previous article.

The programmer gets 2 API functions to use.

1. A function which simply returns the pointer to the Program Header Table. Programmer should do the hard work of parsing it.

2. A proper dump function which will dump the complete table in human-readable form.

### a. elfp_pht_get(): Gets a pointer to Program Header table

This can be used by the programmer if he wants to write his own dump function.

```c
/*
 * elfp_pht_get:
 *  
 * @arg0: Handle
 * @arg1: A reference to an unsigned long integer. The class of the ELF
 *      object is sent to the programmer through this. Without class,    
 *      programmer cannot parse the PHT.
 * 
 * @return: A pointer to PHT on success, NULL on failure.
 */
void*
elfp_pht_get(int handle, unsigned long int *class);
```

Implementation.

**1.** Sanity check

```c
void*
elfp_pht_get(int handle, unsigned long int *class)
{
        int ret;
        elfp_main *main = NULL;
        void *pht = NULL;
        Elf64_Ehdr *e64hdr = NULL;
        Elf32_Ehdr *e32hdr = NULL;

        /* Sanity check */
        ret = elfp_sanitize_handle(handle);
        if(ret == -1)
        {
                elfp_err_warn("elfp_pht_get", "Handle failed the sanity test");
                return NULL;
        }
```

**2.** Get the class

```c
        /* Get the class */
        main = elfp_main_vec_get_em(handle);
        *class = elfp_main_get_class(main);

```

**3.** Based on the class, return the pointer.

Note that we still don't know if this ELF file even has Program Headers. Only ```EXEC``` and ```DYN``` types have it. We should handle the case where the user passes an object file and asks for Program Headers.

```c
        /* Return based on class */
        switch((*class))
        {
                case ELFCLASS32:
                        e32hdr = (Elf32_Ehdr *)elfp_main_get_staddr(main);
                        /* Check if this has no Program Headers */
                        if(e32hdr->phnum == 0)
                                goto no_pht;
                        pht = ((unsigned char *)e32hdr + e32hdr->e_phoff);
                        return pht;

                /*ELFCLASS64, anything else will be treated as 64-bit objects */
                default:                                         
                        e64hdr = (Elf64_Ehdr *)elfp_main_get_staddr(main);
                        /* Check if this has no Program Headers */
                        if(e64hdr->phnum == 0)
                                goto no_pht;
                        pht = ((unsigned char *)e64hdr + e64hdr->e_phoff);
                        return pht;
        }

no_pht:
        *class = ELFCLASSNONE;
        return NULL;
}
```

Let us go on to implement ```elfp_pht_dump()```.

### b. elfp_pht_dump(): Program Header Table dumper

We know the logic. We get the pointer to the table, get the total number of headers and then dump each one of them by iterating through them.

The following is the declaration.

```c
/*
 * elfp_pht_dump: 
 *
 * @arg0: Handle
 *
 * @return: 0 on success, -1 on failure
 */
int
elfp_pht_dump(int handle);
```

Implementation.

**1.** Sanity check

```c
int
elfp_pht_dump(int handle)
{
        int ret;

        /* Sanity check */
        ret = elfp_sanitize_handle(handle);
        if(ret == -1)
        {
                elfp_err_warn("elfp_pht_dump", "Handle failed the sanity test");
                return -1;
        }
```

**2.** All the variables needed.

```c
        elfp_main *main = NULL;
        unsigned long int class;
        unsigned long int phnum;
        Elf64_Ehdr *e64hdr = NULL;
        Elf32_Ehdr *e32hdr = NULL;
        unsigned int i;
```

**3.** Get the class

```c
        /* Get the class */
        main = elfp_main_vec_get_em(handle);
        class = elfp_main_get_class(main);
```

**4.** Get the total number of Program Headers from ELF header.

```c
        switch(class)
        {
                case ELFCLASS32:
                        e32hdr = (Elf32_Ehdr *)elfp_main_get_staddr(main);
                        phnum = e32hdr->e_phnum;
                        break;

                case ELFCLASS64:
                        e64hdr = (Elf64_Ehdr *)elfp_main_get_staddr(main);
                        phnum = e64hdr->e_phnum;
                        break;

                /* Anything else is also considered as 64-bit object */
                default:
                        e64hdr = (Elf64_Ehdr *)elfp_main_get_staddr(main);
                        phnum = e64hdr->e_phnum;
        }
```

**5.** Note that this may be an object file or a core file and it may not have Program Headers. Put a check for that.

```c
        /* Check if there are any program headers */
        if(phnum == 0)
        {
                printf("There are no Program Headers in this file\n");
                return 0;
        }
```

**6.** Then use Program Header's dump function and dump the table.

```c
       /* Now we have everything. Let us dump everything */
        i = 0;
        printf("\n==================================================\n");
        printf("Program Header Table: \n\n");
        
        while (i < phnum)
        {
                printf("Entry %02u: \n", i);
                elfp_phdr_dump(handle, i);
                printf("---------------------------------------------\n");
                i = i + 1;
        }
```

**6.** Return success.

```c
        return 0;
}
```

With that, we have functions to parse the **Program Header Table**.

## 2. Integrating this into the library

Now that we have one more functionality - parsing Program Header table, we need to add it into the library.

To do that, we need to change the rule in the Makefile. We now need to compile ```elfp_phdr.c``` too so that it becomes part of the library. The new ```build``` rule is as follows.

```
build: 
        # Building the library
        $(CC) elfp_int.c elfp_basic_api.c elfp_ehdr.c elfp_phdr.c -c -fPIC $(CFLAGS)
        $(CC) elfp_int.o elfp_basic_api.o elfp_ehdr.o elfp_phdr.o -shared $(CFLAGS) -o libelfp.so
        mkdir build
        mv libelfp.so *.o build
```

Note that ```elfp_ehdr.c``` is also included.

## 3. Extending our sample application

Extending the sample application to parse the Program Header Table is very simple.

We just need to add a call to ```elfp_pht_dump()``` and we are done.

The new version of application works in the following manner.

```
$ ./elfparse /bin/ls
==================================================
ELF Header: 
00. ELF Identifier: 7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
01. Class: 64-bit object
02. Data Encoding: 2's complement, little endian
03. ELF Version: Current version
04. OS/ABI: Unix System V ABI
05. ELF Type: (DYN) Shared object file
06. Architecture: AMD x86_64 architecture
07. Entry Address: 0x5850
08. Program Header Table file offset: 64 bytes
09. Section Header Table file offset: 132000 bytes
10. Flags: 0
11. ELF header size: 64 bytes
12. Program Header size: 56 bytes
13. Program Headers count: 9
14. Section Header size: 64 bytes
15. Section Header count: 28
16. Section Header String Table index: 27
==================================================

==================================================
Program Header Table: 

Entry 00: 
00. Type: PHDR (Entry for header table)
01. Flags: r-x
02. Segment file offset: 64 bytes
03. Virtual Address: 0x40
04. Physical Address: 0x40
05. Segment size in file: 504 bytes
06. Segment size in memory: 504 bytes
07. Segment Alignment: 0x8
---------------------------------------------
Entry 01: 
00. Type: INTERP (Program Interpreter)
01. Flags: r--
02. Segment file offset: 568 bytes
03. Virtual Address: 0x238
04. Physical Address: 0x238
05. Segment size in file: 28 bytes
06. Segment size in memory: 28 bytes
07. Segment Alignment: 0x1
---------------------------------------------
Entry 02: 
00. Type: LOAD (Loadable program segment)
01. Flags: r-x
02. Segment file offset: 0 bytes
03. Virtual Address: 0x0
04. Physical Address: 0x0
05. Segment size in file: 124648 bytes
06. Segment size in memory: 124648 bytes
07. Segment Alignment: 0x200000
---------------------------------------------
Entry 03: 
00. Type: LOAD (Loadable program segment)
01. Flags: rw-
02. Segment file offset: 126960 bytes
03. Virtual Address: 0x21eff0
04. Physical Address: 0x21eff0
05. Segment size in file: 4728 bytes
06. Segment size in memory: 9584 bytes
07. Segment Alignment: 0x200000
---------------------------------------------
Entry 04: 
00. Type: DYNAMIC (Dynamic Linking information)
01. Flags: rw-
02. Segment file offset: 129592 bytes
03. Virtual Address: 0x21fa38
04. Physical Address: 0x21fa38
05. Segment size in file: 512 bytes
06. Segment size in memory: 512 bytes
07. Segment Alignment: 0x8
---------------------------------------------
Entry 05: 
00. Type: NOTE (Auxillary Information)
01. Flags: r--
02. Segment file offset: 596 bytes
03. Virtual Address: 0x254
04. Physical Address: 0x254
05. Segment size in file: 68 bytes
06. Segment size in memory: 68 bytes
07. Segment Alignment: 0x4
---------------------------------------------
Entry 06: 
00. Type: GNU_EH_FRAME (GCC .eh_frame_hdr segment)
01. Flags: r--
02. Segment file offset: 111008 bytes
03. Virtual Address: 0x1b1a0
04. Physical Address: 0x1b1a0
05. Segment size in file: 2180 bytes
06. Segment size in memory: 2180 bytes
07. Segment Alignment: 0x4
---------------------------------------------
Entry 07: 
00. Type: GNU_STACK (Indicates stack executability)
01. Flags: rw-
02. Segment file offset: 0 bytes
03. Virtual Address: 0x0
04. Physical Address: 0x0
05. Segment size in file: 0 bytes
06. Segment size in memory: 0 bytes
07. Segment Alignment: 0x10
---------------------------------------------
Entry 08: 
00. Type: GNU_RELRO (Read-only after relocation)
01. Flags: r--
02. Segment file offset: 126960 bytes
03. Virtual Address: 0x21eff0
04. Physical Address: 0x21eff0
05. Segment size in file: 4112 bytes
06. Segment size in memory: 4112 bytes
07. Segment Alignment: 0x1
---------------------------------------------
```

Let us run it with a relocatable file.

```
$ ../app/elfparse ./elfp_ehdr.o
==================================================
ELF Header: 
00. ELF Identifier: 7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
01. Class: 64-bit object
02. Data Encoding: 2's complement, little endian
03. ELF Version: Current version
04. OS/ABI: Unix System V ABI
05. ELF Type: (REL) Relocatable file
06. Architecture: AMD x86_64 architecture
07. Entry Address: 0x0
08. Program Header Table file offset: 0 bytes
09. Section Header Table file offset: 23096 bytes
10. Flags: 0
11. ELF header size: 64 bytes
12. Program Header size: 0 bytes
13. Program Headers count: 0
14. Section Header size: 64 bytes
15. Section Header count: 16
16. Section Header String Table index: 15
==================================================
There are no Program Headers in this file

```

Note that relocatable files don't have a Program Header table.

## 4. Analyzing the output

Let us write a simple hello program and run our tool on it. And then analyze the output.

```c
$ cat hello.c
#include <stdio.h>
#include <unistd.h>

int main()
{
	printf("Hello!\n");
	return 0;
}
$ gcc hello.c -o hello -g
$ ./hello
Hello!
```

### a. ELF Header

```
$ ./elfparse hello
==================================================
ELF Header: 
00. ELF Identifier: 7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
01. Class: 64-bit object
02. Data Encoding: 2's complement, little endian
03. ELF Version: Current version
04. OS/ABI: Unix System V ABI
05. ELF Type: (DYN) Shared object file
06. Architecture: AMD x86_64 architecture
07. Entry Address: 0x530
08. Program Header Table file offset: 64 bytes
09. Section Header Table file offset: 8696 bytes
10. Flags: 0
11. ELF header size: 64 bytes
12. Program Header size: 56 bytes
13. Program Headers count: 9
14. Section Header size: 64 bytes
15. Section Header count: 34
16. Section Header String Table index: 33
==================================================
```

**1. ABI**: It uses an ABI called **UNiX System V ABI**. This is an ABI used by almost all UNIX-like systems.


**2. Why is an executable classified as a Shared object file?**

```/bin/ls``` is an executable file as we know, but here it says it is a **Shared Object file**. Let us understand what is going on here. Let us verify our tool's output using another standard tool called ```file```.

```
$ file /bin/ls
/bin/ls: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/l, for GNU/Linux 3.2.0, BuildID[sha1]=9567f9a28e66f4d7ec4baf31cfbf68d0410f0ae6, stripped
```
* Even here it says its a shared object.

One property of a shared object is that it is **relocated** at runtime. It simply means that absolute addresses are given to the object after it is run. Let us verify this. Open up this executable with gdb.

```c
$ gdb -q hello
Reading symbols from hello...done.
gdb-peda$ b main
Breakpoint 1 at 0x63e: file hello.c, line 6.
```
* I set a breakpoint at ```main```. It says breakpoint has been set at ```0x63e```. Let us run it now.

This is what I get at the break-point.

```
[----------------------------------registers-----------------------------------]
RAX: 0x55555555463a (<main>:	push   rbp)
RBX: 0x0 
RCX: 0x555555554660 (<__libc_csu_init>:	push   r15)
RDX: 0x7fffffffe048 --> 0x7fffffffe391 ("CLUTTER_IM_MODULE=xim")
RSI: 0x7fffffffe038 --> 0x7fffffffe368 ("/home/dell/Documents/pwnthebox/exp/hello")
RDI: 0x1 
RBP: 0x7fffffffdf50 --> 0x555555554660 (<__libc_csu_init>:	push   r15)
RSP: 0x7fffffffdf50 --> 0x555555554660 (<__libc_csu_init>:	push   r15)
RIP: 0x55555555463e (<main+4>:	lea    rdi,[rip+0x9f]        # 0x5555555546e4)
R8 : 0x7ffff7dd0d80 --> 0x0 
R9 : 0x7ffff7dd0d80 --> 0x0 
R10: 0x2 
R11: 0x3 
R12: 0x555555554530 (<_start>:	xor    ebp,ebp)
R13: 0x7fffffffe030 --> 0x1 
R14: 0x0 
R15: 0x0
EFLAGS: 0x246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x555555554635 <frame_dummy+5>:	jmp    0x5555555545a0 <register_tm_clones>
   0x55555555463a <main>:	push   rbp
   0x55555555463b <main+1>:	mov    rbp,rsp
=> 0x55555555463e <main+4>:	lea    rdi,[rip+0x9f]        # 0x5555555546e4
   0x555555554645 <main+11>:	call   0x555555554510 <puts@plt>
   0x55555555464a <main+16>:	mov    eax,0x0
   0x55555555464f <main+21>:	pop    rbp
   0x555555554650 <main+22>:	ret
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffdf50 --> 0x555555554660 (<__libc_csu_init>:	push   r15)
0008| 0x7fffffffdf58 --> 0x7ffff7a05b97 (<__libc_start_main+231>:	mov    edi,eax)
0016| 0x7fffffffdf60 --> 0x1 
0024| 0x7fffffffdf68 --> 0x7fffffffe038 --> 0x7fffffffe368 ("/home/dell/Documents/pwnthebox/exp/hello")
0032| 0x7fffffffdf70 --> 0x100008000 
0040| 0x7fffffffdf78 --> 0x55555555463a (<main>:	push   rbp)
0048| 0x7fffffffdf80 --> 0x0 
0056| 0x7fffffffdf88 --> 0xbd59568e6dde263a 
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value

Breakpoint 1, main () at hello.c:6
6		printf("Hello!\n");
gdb-peda$ 
```

We have stopped at ```0x55555555463e``` instead of ```0x63e```. This means ```0x55555555463e``` is the actual address. 

So, all the addresses were resolved after ```hello``` was run.

But why did this happen? Why is it useful? Let us understand this.

Note that the absolute address ```0x55555555463e``` = ```0x555555554000``` + ```0x63e```. This can be generalized as,

```
Absolute Address = Some_Number + Offset in file
```

The address of a particular byte in that executable solely depends on that ```Some_Number```. Code which have addressing scheme like this are called **Position Independent Code(PIC)**. Shared libraries consist of PIC because you don't know which address will be available to map it. Whichever address space is available, the library is mapped there.

If an executable has PIC, then they are called **Position Indepdendent Executables(PIEs)**. But, why should an executable have PIC?
One of its uses is to administer a security measure called **Address Layout Space Randomization(ASLR)**. This is a measure which defends the OS against certain attacks. In short, the ```Some_Number``` above is a random number. Everytime the program is run, ```Some_Number``` changes - it is random everytime. So, all the addresses are random everytime the program is run. How does this make the system more secure? You can read [this article](/reverse/engineering/and/binary/exploitation/series/2018/12/28/security-measures-by-os.html) to understand ASLR better.

Because an executable has PIC, it has been classified as a **Shared object file**.

**3. Architecture**: I am running a 64-bit Intel processor. So, it is normal to be using AMD64 architecture,

**4. Entry Point**: It says **0x530**. Note that this is an address relative to beginning of this ELF file. Absolute address is generated at runtime, as we discussed earlier.

**5. Program Header Table**:

We can come to know that the **Program Header Table** starts at an offset of **64** bytes into the file. This is basically right after the ELF header. Note that the size of ELF header is 64 bytes.

Size of each Program Header is **56** bytes. We can verify this from ```sizeof(Elf64_Phdr)```.

There are **9** Program Headers in this table.

**6. Section Header Table**:

This table is present at an offset of **8696** bytes into the file. There are **34** Section Headers in it, each of size **64** bytes.

There is something interesting about this table.

Total size of the table = **34** * **64** = **2176** bytes.

* **8696** + **2176** = **10872**, which is the total size of this ELF file.

```
$ ls -l hello
-rwxr-xr-x 1 dell dell 10872 Dec  9 13:49 hello
```

So, we now know that the Section Header Table is present at the end of an ELF file.

**7. Section Header String Table**: Index of this table is 33. We'll explore more into this table in one of the future articles.

That was about the ELF header. I urge you to experiment on other ELF files and get a better understanding.

### b. Program Header Table

In previous article and this one, we discussed types of Program Headers, what PHT is.

But we never really explored how an executable's PHT would look like, what Headers it has etc., Now, we'll take the same ```hello``` executable and explore its PHT using our own tool.

Let us take a look at the output and go over every Program Header.

```c
==================================================
Program Header Table: 

Entry 00: 
00. Type: PHDR (Entry for header table)
01. Flags: r--
02. Segment file offset: 64 bytes
03. Virtual Address: 0x40
04. Physical Address: 0x40
05. Segment size in file: 504 bytes
06. Segment size in memory: 504 bytes
07. Segment Alignment: 0x8
---------------------------------------------
Entry 01: 
00. Type: INTERP (Program Interpreter)
01. Flags: r--
02. Segment file offset: 568 bytes
03. Virtual Address: 0x238
04. Physical Address: 0x238
05. Segment size in file: 28 bytes
06. Segment size in memory: 28 bytes
07. Segment Alignment: 0x1
---------------------------------------------
Entry 02: 
00. Type: LOAD (Loadable program segment)
01. Flags: r-x
02. Segment file offset: 0 bytes/write/your/own/xxxx/2019/12/08/writing-an-elf-parsing-library-part7-program-headers.html
03. Virtual Address: 0x0
04. Physical Address: 0x0
05. Segment size in file: 2096 bytes
06. Segment size in memory: 2096 bytes
07. Segment Alignment: 0x200000
---------------------------------------------
Entry 03: 
00. Type: LOAD (Loadable program segment)
01. Flags: rw-
02. Segment file offset: 3512 bytes
03. Virtual Address: 0x200db8
04. Physical Address: 0x200db8
05. Segment size in file: 600 bytes
06. Segment size in memory: 608 bytes
07. Segment Alignment: 0x200000
---------------------------------------------
Entry 04: 
00. Type: DYNAMIC (Dynamic Linking information)
01. Flags: rw-
02. Segment file offset: 3528 bytes
03. Virtual Address: 0x200dc8
04. Physical Address: 0x200dc8
05. Segment size in file: 496 bytes
06. Segment size in memory: 496 bytes
07. Segment Alignment: 0x8
---------------------------------------------
Entry 05: 
00. Type: NOTE (Auxillary Information)
01. Flags: r--
02. Segment file offset: 596 bytes
03. Virtual Address: 0x254
04. Physical Address: 0x254
05. Segment size in file: 68 bytes
06. Segment size in memory: 68 bytes
07. Segment Alignment: 0x4
---------------------------------------------
Entry 06: 
00. Type: GNU_EH_FRAME (GCC .eh_frame_hdr segment)
01. Flags: r--
02. Segment file offset: 1772 bytes
03. Virtual Address: 0x6ec
04. Physical Address: 0x6ec
05. Segment size in file: 60 bytes
06. Segment size in memory: 60 bytes
07. Segment Alignment: 0x4
---------------------------------------------
Entry 07: 
00. Type: GNU_STACK (Indicates stack executability)
01. Flags: rw-
02. Segment file offset: 0 bytes
03. Virtual Address: 0x0
04. Physical Address: 0x0
05. Segment size in file: 0 bytes
06. Segment size in memory: 0 bytes
07. Segment Alignment: 0x10
---------------------------------------------
Entry 08: 
00. Type: GNU_RELRO (Read-only after relocation)
01. Flags: r--
02. Segment file offset: 3512 bytes
03. Virtual Address: 0x200db8
04. Physical Address: 0x200db8
05. Segment size in file: 584 bytes
06. Segment size in memory: 584 bytes
07. Segment Alignment: 0x1
---------------------------------------------
```

The PHT starts with a ```PHDR``` type Program Header. As we know, this type of header is used to describe the Table. Lets take a look at its details.

```
Entry 00: 
00. Type: PHDR (Entry for header table)
01. Flags: r--
02. Segment file offset: 64 bytes
03. Virtual Address: 0x40
04. Physical Address: 0x40
05. Segment size in file: 504 bytes
06. Segment size in memory: 504 bytes
07. Segment Alignment: 0x8
```

* The PHT is itself a segment and its header is ```PHDR```. 
* Its permissions is ```r--``` - Read-only. This makes sense because the PHT has metadata of all segments and its critical info.
* This segment(or PHT) starts from an offset of 64 bytes.
* Virtual Address is **0x40**, which is simply the offset(64-bytes). This is because we are dealing with a Position Independent Executable.
* Segment size is **504 bytes**. We know that this is a 64-bit executable. From this we know the size of a Program Header = 56 bytes. From all this info, we know that there are **9** Program Headers in this Table. So, we actually don't need ELF header's help for processing. To process a PHT, all we need is the ELF file's class - is it 32/64 bit and Pointer to PHT.

Next is the **INTERP** header.

```
Entry 01: 
00. Type: INTERP (Program Interpreter)
01. Flags: r--
02. Segment file offset: 568 bytes
03. Virtual Address: 0x238
04. PhysicalPT_LOAD     The  array  element  specifies  a loadable segment, described by p_filesz and
                             p_memsz.  The bytes from the file are mapped to the beginning of  the  memory
                             segment.   If  the segment's memory size p_memsz is larger than the file size
                             p_filesz, the "extra" bytes are defined to hold the value 0 and to follow the
                             segment's  initialized area.  The file size may not be larger than the memory
                             size.  Loadable segment entries in the program header table appear in ascend‐
                             ing order, sorted on the p_vaddr member.
 Address: 0x238
05. Segment size in file: 28 bytes
06. Segment size in memory: 28 bytes
07. Segment Alignment: 0x1
```

We discussed that this segment just has the path to a Program Interpreter. From this entry, we know that the path is present 568 bytes into the file and is 28 bytes long. Let us checkout the Program Interpreter. 

Let us use a hexdump tool for this.

```
$ xxd hello > hello.xxd
```

In that file, at an offset of 568 (0x238) bytes, I found this.

```
00000230: 0100 0000 0000 0000 2f6c 6962 3634 2f6c  ......../lib64/l
00000240: 642d 6c69 6e75 782d 7838 362d 3634 2e73  d-linux-x86-64.s
00000250: 6f2e 3200 0400 0000 1000 0000 0100 0000  o.2.............
```

* The string is ```/lib64/ld-linux-x86-64.so.2```. So, this is the Program Interpreter which will be used to run the ```hello``` program. If you are interesting in learning more about Program Interpreter, you can read [this article](/reverse/engineering/and/binary/exploitation/series/2019/11/10/understanding-the-loader-part1-how-does-an-executable-get-loaded-to-memory.html).


Next comes 2 **LOAD** type headers.

```
Entry 02: 
00. Type: LOAD (Loadable program segment)
01. Flags: r-x
02. Segment file offset: 0 bytes
03. Virtual Address: 0x0
04. Physical Address: 0x0
05. Segment size in file: 2096 bytes
06. Segment size in memory: 2096 bytes
07. Segment Alignment: 0x200000
---------------------------------------------
Entry 03: 
00. Type: LOAD (Loadable program segment)
01. Flags: rw-
02. Segment file offset: 3512 bytes
03. Virtual Address: 0x200db8
04. Physical Address: 0x200db8
05. Segment size in file: 600 bytes
06. Segment size in memory: 608 bytes
07. Segment Alignment: 0x200000
```

From the permissions, I am guessing the first one has code in it because it is ```r-x``` - only Read and Execute. The Second one should be the data segment, where global variables are stored.

You can see an interesting thing in the second one. Its size in memory is larger than size in file. What could be the reason?

I found the following in ```elf```'s manpage.

```
PT_LOAD                      The  array  element  specifies  a loadable                                  segment, described by p_filesz and
                             p_memsz.  The bytes from the file are mapped to the beginning of  the  memory
                             segment.   If  the segment's memory size p_memsz is larger than the file size
                             p_filesz, the "extra" bytes are defined to hold the value 0 and to follow the
                             segment's  initialized area.  The file size may not be larger than the memory
                             size.  Loadable segment entries in the program header table appear in ascend‐
                             ing order, sorted on the p_vaddr member.
```

* One thing I don't understand is, why are the segments aligned to **0x200000**? I'll update the post once I find out.

Next is a **DYNAMIC** type header.

```
Entry 04: 
00. Type: DYNAMIC (Dynamic Linking information)
01. Flags: rw-
02. Segment file offset: 3528 bytes
03. Virtual Address: 0x200dc8
04. Physical Address: 0x200dc8
05. Segment size in file: 496 bytes
06. Segment size in memory: 496 bytes
07. Segment Alignment: 0x8
```

This will have all the info needed to make Dynamic Linking work.

Next 2 are **NOTE** and **GNU_EH_FRAME** headers. We'll discuss about these 2 in detail in future articles.

The next two are **GNU_STACK** and **GNU_RELRO**. We have discussed in detail about these 2 types in the previous article.

So, this is what PHT of a typical executable looks like. PHDR to describe the PHT, INTERP, LOAD, DYNAMIC which helps the program run. NOTE to convey auxillary info. GNU_STACK and GNU_RELRO to convey some other important info to the linker.

I urge you to explore Program Headers of shared libraries, see if you find any diffrerence between its PHT and this.

## 5. Conclusion

With this, we'll end this article.

In this article, we saw what Program Headers are, we discussed about PHT, various Segment types, different permissions a segment could have and more.

We wrote parse functions for Program Header and later used it to parse the Program Header Table.

We also saw what Program Headers are present in a typical executable.

You can find the code we have written so far [here](https://github.com/write-your-own-XXXX/ELF-Parser/releases/tag/Part8).

In the next few articles, we'll be exploring each of the **segments** in detail, what role they play in running a program and of course write parse code for each segment.

That is for this article. I hope you learnt something out of this.

Thank you for reading!

----------------------------------------------------
[Go to next article: Writing an ELF Parsing Library - Part9 - PHDR, INTERP and GNU_STACK segment types](/write/your/own/xxxx/2019/01/03/writing-an-elf-parsing-library-part9-phdr-interp-gnu-stack-segment-types.html)              
[Go to previous article: Writing an ELF Parsing Library - Part7 - Program Headers](/write/your/own/xxxx/2019/12/08/writing-an-elf-parsing-library-part7-program-headers.html).
