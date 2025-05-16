---
title: Writing an ELF Parsing Library - Part6 - The ELF Header
categories: elfparser
layout: post
comments: true
---

Hello Friend!

In previous articles, we implemented data structures necessary for the library to work, implemented a few basic API functions which will be used by the programmer.

Now, we are all set to write the **Core of the library - the ELF parsing component**.

In this article, we'll be dissecting ELF's very first structure, the **ELF header**.

Lets start!

## 0. Pre-requisites

We'll need access to ```elfp_main```'s members. So, let us write the ```get()``` functions for all its members before we actually start exploring the ELF header.

**1.** File descriptor

```c
/*
 * elfp_main_get_fd: Gets the file descriptor.
 *
 * @arg0: Reference to an elfp_main object
 *
 * @return: Returns fd
 */
int
elfp_main_get_fd(elfp_main *main);
```

Implementation is simple.

```c
int
elfp_main_get_fd(elfp_main *main)
{
        /* Basic check */
        if(main == NULL)
        {
                elfp_err_warn("elfp_main_get_fd", "NULL argument passed");
                return -1;
        }

        returun main->fd;
}
```

Write similar ```get()``` functions for all the members. We'll be using them later.

These are functions related to ```elfp_main``` structure. So, put the declarations and definitions into ```elfp_int.h``` and ```elfp_int.c``` respectively.

## 1. Introduction

**ELF** stands for **Executable and Linkable Format**. This is a file format of Executables, object files, shared objects, core files in most of the UNIX-like systems. You can read [this article](/write/your/own/xxxx/2019/11/15/writing-an-elf-parsing-library-part1-what-is-elf.html) to get an idea of what ELF is.

The **ELF header** is the header of every ELF file. It is present in the **beginning** of every ELF file and serves as a map to the rest of the file. You can go to any part of the file with help of the data present in ELF header.

We'll be refering to ```elf.h``` header file and ```elf```'s manpage for all purposes.

We'll be going through each ELF header's members in detail, and writing code to parse it.

## 2. What is the API exposed to the programmer?

In the [second article](/write/your/own/xxxx/2019/11/15/writing-an-elf-parsing-library-part2-piloting-the-library.html), we discussed the features of our library. One of them was this: The programmer should have the **choice** between using the library's dump function and writing a dump function of his own.

The programmer will have the following API:

2. ```elfp_get_ehdr()```: This returns the pointer to ELF header. The programmer should do all the hard work of parsing it.

3. ```elfp_dump_ehdr()```: THis function parses the ELF header and dumps it in human-readable form.

Because these are exposed to the programmers, we'll put the function declarations in ```elfp.h```.

```c
/******************************************************************************
 * Parsing the ELF Header.
 *
 * 1. elfp_dump_ehdr: An in-built function which dumps the ELF Header in
 *      human readable form.
 *
 * 2. elfp_get_ehdr: A function which returns a reference to an elfp_ehdr
 *      instance, using which the programmer can write a dump function.
 *
 *****************************************************************************/

/*
 * elfp_dump_ehdr:
 *
 * @arg0: User Handle
 * 
 * @return: 0 on success, -1 on failure.
 */
int 
elfp_dump_ehdr(int handle);

/*
 * elfp_get_ehdr:
 *
 * @arg0: User Handle
 *
 * @return: Pointer to ELF header.
 *      * A void pointer is returned because we wouldn't know
 *      if it is a 32-bit or 64-bit object till e_ident is parsed.
 */
void*
elfp_get_ehdr(int handle);
```

Implementing ```elfp_get_ehdr()``` is not difficult. We need to get the ```start_addr``` of the ```elfp_main``` object corresponding to the ```handle``` supplied.

**1.** Sanitizing the handle!

```c
void*
elfp_get_ehdr(int handle)
{
        int ret;
        void *addr = NULL;
        elfp_main *main = NULL;
        
        /* First sanitize it */
        ret = elfp_sanitize_handle(handle);
        if(ret == -1)
        {
                elfp_err_warn("elfp_get_ehdr", "Handle failed sanity test");
                return NULL;
        }
```

**2.** Get the corresponding ```elfp_main``` object.

```c
        main = elfp_main_vec_get_em(handle);
        if(main == NULL)
        {
                elfp_err_warn("elfp_get_ehdr", "elfp_main_vec_get_em() failed");
                return NULL;
        }
```

**3.** Get the start address using the ```get()``` function you wrote in the previous section.

```c
        addr = elfp_main_get_staddr(main);
        if(addr == NULL)
        {       
                elfp_err_warn("elfp_get_ehdr", "elfp_main_get_staddr() failed");
                return NULL;
        }
        
        return addr;
}
```

To implement ```elfp_dump_ehdr()```, we first need to under the ELF header properly.

## 2. Understanding the ELF header

We need to go through each of its members and get a clear idea of what that member is doing. The following is the 64-bit ELF header.

```c
typedef struct
{
  unsigned char e_ident[EI_NIDENT];     /* Magic number and other info */
  Elf64_Half    e_type;                 /* Object file type */
  Elf64_Half    e_machine;              /* Architecture */
  Elf64_Word    e_version;              /* Object file version */
  Elf64_Addr    e_entry;                /* Entry point virtual address */
  Elf64_Off     e_phoff;                /* Program header table file offset */
  Elf64_Off     e_shoff;                /* Section header table file offset */
  Elf64_Word    e_flags;                /* Processor-specific flags */
  Elf64_Half    e_ehsize;               /* ELF header size in bytes */
  Elf64_Half    e_phentsize;            /* Program header table entry size */ 
  Elf64_Half    e_phnum;                /* Program header table entry count */
  Elf64_Half    e_shentsize;            /* Section header table entry size */ 
  Elf64_Half    e_shnum;                /* Section header table entry count */ 
  Elf64_Half    e_shstrndx;             /* Section header string table index */
} Elf64_Ehdr;
```

Lets take up a member, understand it properly and write code to dump it in human-readable form.

Lets write the initial code and keep the function ready to write parsing code.

**1.** Get the starting address.

```c
int
elfp_dump_ehdr(int handle)
{
        void *ehdr = NULL;
        int ret;
        unsigned char *e_ident = NULL;
        char *decoded_str = NULL;
        unsigned int i;

        /* Get the header */
        ehdr = elfp_get_ehdr(handle);
        if(ehdr == NULL)
        {
                elfp_err_warn("elfp_dump_ehdr", "elfp_get_ehdr() failed");
                return -1;
        }
        
        /* Now that we have the header, let us parsing. */
        printf("==================================================\n");
        printf("ELF Header: \n");
        i = 0;
```

### a. **e_ident**: ELF Identification array

When anyone(be it the OS, or tools like ours) starts processing an ELF file, we won't know anything about that file. Essential details like is it 32-bit or 64-bit, what is its target OS(Linux, OpenBSD etc.,), what is its target architecture(AMD64, i386, ARM etc.,), we won't know anything.

These details are very important for us to parse this file properly. For example, Consider the ELF header itself. The 64-bit version is **64 bytes** in size. The 32-bit version is **52 bytes**. Suppose we have a 32-bit ELF file, but we treat it as a 64-bit ELF file, this would be a disaster. 

Instead of doing the following, 

```c
Elf32_Ehdr *ehdr = (Elf32_Ehdr *)start_addr;
```

I do

```c
Elf64_Ehdr *ehdr = (Elf64_Ehdr *)start_addr;
```

All the processing which happens after this will be **erroneous**.

To make sure this doesn't happen, the ELF format presents the ```e_ident``` array, which has ALL the necessary details to process this ELF file properly. It is present to make sure this ELF file is **identified** properly and thereby processed in the right manner.
The ```EI_NIDENT``` is 16. ```e_ident``` is a 16-byte long array, independent of the ELF file. These 16 bytes will always be there at the beginning of every ELF file, irrespective of the OS, architecture or any other details.

We'll print ```e_ident``` array. This is part of ```elfp_dump_ehdr()```.

```c
        /*
         * e_ident array
         */
        e_ident = (unsigned char *)ehdr;
        
        /* Print the entire array */
        printf("%02u. ELF Identifier: ", i++);
        for(unsigned j = 0; j < EI_NIDENT; j++)
        {
                printf("%02x ", e_ident[j]);
        }
        printf("\n");
```

Let us dig deeper.

**1. Byte 0 - 3**: ELF magic characters

The first 4 bytes are ELF's signature characters **\x7fELF**. If the file is an ELF file, then the first 4 bytes of that file **MUST** be these 4 bytes.

While creating the ```elfp_main``` object for this file, we have already checked for magic characters. So, this needs no more processing.

**2. Byte 4**: ELF file's Class

This byte tells if this ELF object is a **32-bit / 64-bit** object. The following is from ```elf.h```.

```c
#define EI_CLASS        4               /* File class byte index */
#define ELFCLASSNONE    0               /* Invalid class */
#define ELFCLASS32      1               /* 32-bit objects */
#define ELFCLASS64      2               /* 64-bit objects */
#define ELFCLASSNUM     3
```

The following encoding is used here to convey the class of the object.

1. Class = 1 if it is a 32-bit object
2. Class = 2 if it is a 64-bit object
3. Class = 0 if it is an Invalid class

This is very concise and this is how encoding should be. 

But we need it in human readable form. We should process this byte and tell the user/programmer if this is a 32-bit, 64-bit object or an object with invalid class.

Let us write a function which will decode this and returns a human-readable string. Put this in ```elfp_ehdr.c```.

```c
const char*
elfp_ehdr_decode_class(unsigned long int class)
{       
        switch(class)
        {       
                case ELFCLASS32:
                        return "32-bit object";
                        
                case ELFCLASS64:
                        return "64-bit object";
                        
                /* Everything else is invalid */
                default:
                        return "Invalid class";
        }
}
```

This way, we have a function which properly decodes the ```class``` of this ELF object. Because this can help the programmer in writing his own dump function, put the declaration in ```elfp.h```.

Now that we have a decode function, we can add its parsing code to ```elfp_dump_ehdr()```.

```c
        /* 1. Class */
        printf("%02u. Class: %s\n", i++, elfp_ehdr_decode_class(e_ident[EI_CLASS]));
```


**3. Byte 5**: Data encoding

This byte will tell us what type of encoding has been used to encode data - Is it **little-endian** or **big-endian**.

```c
#define EI_DATA         5               /* Data encoding byte index */
#define ELFDATANONE     0               /* Invalid data encoding */
#define ELFDATA2LSB     1               /* 2's complement, little endian */
#define ELFDATA2MSB     2               /* 2's complement, big endian */
#define ELFDATANUM      3
```

Let us write a decode function for this.

```c
const char*
elfp_ehdr_decode_dataenc(unsigned long int data_enc)
{       
        switch(data_enc)
        {       
                case ELFDATA2LSB:
                        return "2's complement, little endian";
         
                case ELFDATA2MSB:
                        return "2's complement, big endian";  
                        
                /* Anything else is invalid */
                default: 
                        return "Invalid Data Encoding";
        }
}
```

Put the implementation in ```elfp_ehdr.c``` and declaration in ```elfp.h```.

Let us write its bit in ```elfp_dump_ehdr()```.

```c
        /* 2. Data encoding */
        printf("%u. Data Encoding: %s\n", i++, elfp_ehdr_decode_dataenc(e_ident[EI_DATA]));
```

**4. Byte 6**: ELF File version

I am guessing there were various ELF versions before. But now, there is only one version, the ```EV_CURRENT```.

A simple decode function should do.

```c
const char*
elfp_ehdr_decode_version(unsigned long int version)
{       
        switch(version)
        {       
                case EV_CURRENT:
                        return "Current version";
         
                /* Everything else is invalid */
                default:  
                        return "Invalid ELF version";
        }
}
```

Its piece in ```elfp_dump_ehdr()```.

```c
        /* 3. Version */
        printf("%02u. ELF Version: %s\n", i++, elfp_ehdr_decode_version(e_ident[EI_VERSION]));
```

**5. Byte 7**: OS-ABI

We know what OS is. Let us discuss what ABI is.

We have seen what **API** is. It stands for **Application Programming Interface**. These are well-define methods(functions and/or data structures) to use some other piece of code. Each function tells what parameters it takes, what it returns, what it does. As beautifully put in [this quora answer](https://www.quora.com/What-exactly-is-an-Application-Binary-Interface-ABI-Who-defines-it-the-operating-system-a-programming-language), **API is a contract between 2 pieces of source code**.

Now, we'll come to **ABI**. It stands for **Application Binary Interface**. The ABI defines how functions are called, how parameters are passed to a function at assembly level, how return value is given back to the caller. ABI also defines a lot of other things - like how system calls are invoked, does stack grow downwards or upwards. ABI is the set of rules present for 2 binaries to be able to communicate with each other with consistency.

Let me give you an example.

Let us consider that decode function we wrote. It'll be part of our library ```libelfp.so```. Consider that we followed standard AMD64 ABI to build the library.

Say the programmer is writing a tool called ```elfparse``` using our library. But the programmer follows a non-standard ABI to construct the ```elfparse``` executable.

Consider the case where the programmer uses the decode function ```elfp_ehdr_decode_class()```. Our library is a binary constructed using standard ABI. Standard ABI tells that the return value of a function should always be loaded into ```rax``` register. The programmer calls this function and the return value is in ```rax``` now.

But the programmer is using a different non-standard ABI to construct his tool ```elfparse```. Say his ABI expects the return value to be present in ```rbx``` register.

This way, the executable ```elfparse``` will never be able to get the actual return value, because there is an **ABI mismatch**.

The binaries ```elfparse``` and ```libelfp.so``` won't be able work with each other because they follow different ABI.

=> **An ABI is a contract between pieces of binary code**.

Concept is simple. When various unrelated pieces of code are expected to work with each other in a proper manner, there needs to be a set of common rules that all those pieces of code need to follow. Those rules are called **Application Binary Interface**. **ABI is a set of rules enforced by the Operating system on a specific architecture**.

You can refer to my [Reverse Engineering and Binary Exploitation Series](https://www.pwnthebox.net/reverse/engineering/and/binary/exploitation/series/2019/03/25/reverse-engineering-and-binary-exploitation-series-mainpage.html) to underrstand Standard ABI in detail.

Coming back to the OS-ABI byte, the following are the choices. Refering to ```elf.h```,

```c
#define EI_OSABI        7               /* OS ABI identification */
#define ELFOSABI_NONE           0       /* UNIX System V ABI */
#define ELFOSABI_SYSV           0       /* Alias.  */
#define ELFOSABI_HPUX           1       /* HP-UX */
#define ELFOSABI_NETBSD         2       /* NetBSD.  */
#define ELFOSABI_GNU            3       /* Object uses GNU ELF extensions.  */
#define ELFOSABI_LINUX          ELFOSABI_GNU /* Compatibility alias.  */
#define ELFOSABI_SOLARIS        6       /* Sun Solaris.  */
#define ELFOSABI_AIX            7       /* IBM AIX.  */
#define ELFOSABI_IRIX           8       /* SGI Irix.  */
#define ELFOSABI_FREEBSD        9       /* FreeBSD.  */
#define ELFOSABI_TRU64          10      /* Compaq TRU64 UNIX.  */
#define ELFOSABI_MODESTO        11      /* Novell Modesto.  */
#define ELFOSABI_OPENBSD        12      /* OpenBSD.  */
#define ELFOSABI_ARM_AEABI      64      /* ARM EABI */
#define ELFOSABI_ARM            97      /* ARM */
#define ELFOSABI_STANDALONE     255     /* Standalone (embedded) application */
```

All UNIX-like systems use the **UNIX System V ABI**. Let us write a decode function for this.

```c
const char*
elfp_ehdr_decode_osabi(unsigned long int osabi)
{
        switch(osabi)
        {
                case ELFOSABI_SYSV: /* ELFOSABI_NONE */
                        return "Unix System V ABI";

                case ELFOSABI_HPUX:
                        return "HP-UX";

                case ELFOSABI_NETBSD:
                        return "NetBSD";

                case ELFOSABI_GNU: /* ELFOSABI_LINUX */
                        return "Object uses GNU ELF extensions";
.
.
.
                case ELFOSABI_ARM_AEABI:
                        return "ARM EABI";

                case ELFOSABI_ARM:
                        return "ARM";

                case ELFOSABI_STANDALONE:
                        return "Standalone(embedded) application";

                /* Anything else is invalid */
                default:
                        return "Invalid OSABI";
        }
}
```

You can refer to [ABI's wikipedia page](https://en.wikipedia.org/wiki/Application_binary_interface) for more details.

Let us write its dump statement in ```elfp_dump_ehdr()```.

```c
        /* 4. OS-ABI */
        printf("%02u. OS/ABI: %s\n", i++, elfp_ehdr_decode_osabi(e_ident[EI_OSABI]));
```

**6. Byte 8**: ABI Version

There is no info about it. I am guessing this is **0x00**.

We are down 9 bytes now (0-8). The rest are padding bytes, normally set to to 0.

I hope you got an idea of what ```e_ident``` array is.

At this point, we have parsed the ```e_ident``` array. Now, we need to parse other members of the ELF header. To parse the rest of the header, we should know if this ELF is 32-bit / 64-bit. We know this from ```e_ident```'s ```EI_CLASS``` byte. 

The next part of ```elfp_dump_ehdr()``` looks like this.

```c
        /* Based on e_ident, I know if this is a 32-bit or a
         * 64-bit ELF object. */
        
        switch(e_ident[EI_CLASS])
        {
                case ELFCLASS32:
                        elfp_dump_e32hdr(ehdr);
                        break;

                case ELFCLASS64:
                        elfp_dump_e64hdr(ehdr);
                        break;

                /* Invalid cases are considered to be 64-bit
                 * objects */
                default:
                        elfp_dump_e64hdr(ehdr);
        }
```

Based on the class, we have separate parsing functions.

In further sub-sections, we'll be writing code for ```elfp_dump_e64hdr()```, the function which will dump all the other members of 64-bit ELF header.

```elfp_dump_e64hdr()``` start like this.

```c
void
elfp_dump_e64hdr(void *start_addr)
{
        Elf64_Ehdr *ehdr = start_addr;
        unsigned int i = 5;
```

* ```i``` is the serial number.

### b. **e_type**: Object file type

As we discussed [here](https://www.pwnthebox.net/write/your/own/xxxx/2019/11/15/writing-an-elf-parsing-library-part1-what-is-elf.html), the ELF is used to encode various types of files - executable, object files, shared library, core files.

This member will tell us which type of file this ELF file is. The following are the options.

```c
/* Legal values for e_type (object file type).  */

#define ET_NONE         0               /* No file type */
#define ET_REL          1               /* Relocatable file */
#define ET_EXEC         2               /* Executable file */
#define ET_DYN          3               /* Shared object file */
#define ET_CORE         4               /* Core file */
#define ET_NUM          5               /* Number of defined types */
```

Let us write a decode function for this.

```c
const char*
elfp_ehdr_decode_type(unsigned long int type)
{       
        switch(type)
        { 
                case ET_REL:
                        return "Relocatable file";
                        
                case ET_EXEC:
                        return "Executable file";
                        
                case ET_DYN:
                        return "Shared object file";
                        
                case ET_CORE:
                        return "Core file";
                        
                /* Anything else is trash */
                default:
                        return "Invalid ELF file type";
        }       
}
```

Let us put its dump statement in ```elfp_dump_e64hdr()```.

```c
        /*
         * 1. e_type
         */
        printf("%02u. ELF Type: %s\n", i++, elfp_ehdr_decode_type(ehdr->e_type));
```

### c. **e_machine**: Architecture

This member encodes the type of architecture(or roughly processor) this executable was built for. It'll tell if it was built to run on Intel 386 processor, Intel IA64, AMD64, ARM, Motorola 68k etc.,

This is a very important field. The following are a few architectures in the huge list present in ```elf.h```.

```c
#define EM_NONE          0      /* No machine */
#define EM_M32           1      /* AT&T WE 32100 */
#define EM_SPARC         2      /* SUN SPARC */
#define EM_386           3      /* Intel 80386 */
#define EM_68K           4      /* Motorola m68k family */
#define EM_88K           5      /* Motorola m88k family */
#define EM_IAMCU         6      /* Intel MCU */
#define EM_860           7      /* Intel 80860 */
#define EM_MIPS          8      /* MIPS R3000 big-endian */
#define EM_S370          9      /* IBM System/370 */
#define EM_MIPS_RS3_LE  10      /* MIPS R3000 little-endian */
.
.
```

You may be familiar with a few architectures. A few popular ones are **Intel 80386**, **Motorola m68k**, **IBM System/370**, **ARM**, **AMD64**.

Write a decode function for this. You'll come across a lot of unheard architectures, which is a good learning!

With that, we are done with all the members which exist in encoded form. We have written decode functions to convert them into human-readable form.

The following is the dump statement.

```c
        /*
         * 2. e_machine
         */
        printf("%02u. Architecture: %s\n", i++, elfp_ehdr_decode_machine(ehdr->e_machine));
```

### d. **e_entry**: Entry Point Virtual Address

When a program is run, execution should start somewhere. The ```e_entry``` is the address of first instruction to be executed - basically the entry point to the program.

As programmers, it is normal to think that ```main()``` is the entry point of our programs, and for all practical purposes it is.

But from the OS's perspective, ```main()``` is just another function.

The ```_start``` symbol is the **actual entry point** of any executable. Write a simple program and check out its disassembly using objdump.

This is the value itself and doesn't need any decoding.

If you want to learn more about this, you can read [this](https://www.pwnthebox.net/reverse/engineering/and/binary/exploitation/series/2019/11/10/understanding-the-loader-part1-how-does-an-executable-get-loaded-to-memory.html) article.

The following is its dump statement.

```c
        /*
         * 3. e_entry
         */
        printf("%02u. Entry Address: %p\n", i++, (void *)ehdr->e_entry);
```

### e. **e_phoff**: Program Header Table file offset

The complete ELF file is logically divided into partitions known as **segments**. Each segment is essential for proper execution of that ELF file.

To know the segments' details, a data structure called **Program Header Table** is used. This is a table or an array of **Program Header**s, each Program Header has details about each segment.

If there are 10 segments, the Program Header Table contains 10 Program Headers, each for one segment.

**Program Header communicates with the Operating System and tells at what virtual memory that particular segment should be loaded, what its permissions are etc.,**

How do we know where the Program Header Table is in the ELF file? All we now have is the starting address of the ELF file and the ELF header.

The member ```e_phoff``` tells us at what offset from the file-beginning this Table is present.

In normal cases, the Program Header Table is present right after the ELF header.

We'll be talking about Program Header Table in detail in future articles.

The following is its dump statement.

```c
        /*
         * 4. e_phoff
         */
        printf("%02u. Program Header Table file offset: %lu bytes\n", 
                                                        i++,ehdr->e_phoff);
```

### f. **e_shoff**: Section Header Table file offset

Another way to partition an ELF file is through **sections**.

And there is a **Section Header Table** which gives details about all the sections.

The way a Program Header communicates with the OS and tells about that segment, a Section Header communicates with the **linker** and tells everything about that section.

It should be noted that the same ELF file is divided into segments and sections.

You can refer to [this wonderful stackoverflow qn](https://stackoverflow.com/questions/14361248/whats-the-difference-of-section-and-segment-in-elf-file-format) to understand better.

We'll also discuss about Sections and Section Header Table in detail in future articles.

The member **e_shoff** tells us at what offset from the file-beginning is the Section Header Table present.

This is the dump statement.

```c
        /*
         * 5. e_shoff
         */
        printf("%02u. Section Header Table file offset: %lu bytes\n",
                                                        i++, ehdr->e_shoff);
```

Similarly, write dump statements for rest of the members.

### g. **e_flags**: Processor-specific flags

Let us ignore this field for now.

### h. **e_ehsize**: ELF header size

This tells us the size of the ELF header.

### i. **e_phentsize**: Program header Table entry size

Program Header Table entry is simply a **Program Header**. The ```e_phentsize``` informs us about the size of each Program Header.

### j. **e_phnum**: Program Header Table entry count

This is the number of Program Headers present in the Table.

### k. **e_shentsize**: Section Header Table entry size

This tells us the **size of each Section Header**.

### l. **e_shnum**: Section Header Table entry count

This tells us the number of Section Headers present in the Section Header table. It should be noted that each section has a header. So, **e_shnum** also tells us the total number of sections present in this ELF file.

### m. **e_shstrndx**: Section Header String Table index

It should be noted that **every section** has a name - **.text**, **.data**, **.rodata**, **.plt**, **.got** etc.,

Where are these names(strings) stored in the ELF file?

It is stored in another section called **.shstrtab**: **Section Header String Table**.

As we discussed before, the Section Header Table is an array of Section Headers. The **.shstrtab** is present at the index ```e_shstrndx```. If you consider ```SHT[e_shnum]``` to be the Section Header Table, ```SHT[e_shstrndx]``` is the Section Header of ```.shstrtab```.

With that, we have parsed a 64-bit ELF header completely. ```elfp_dump_e32hdr()``` should be very similar to ```elfp_dump_e64hdr()```. Only difference is the initial typecast: ```Elf32_Ehdr *ehdr = start_addr``` instead of ```Elf64_Ehdr```. I want you to write ```elfp_dump_e32hdr()``` on your own.

We have successfully written parse code for ELF header. I hope you have understood what ELF header is, its contents.

## 3. Building the library

We are now in a position to build the library ```libelfp.so```. Let us write a simple **Makefile** to do the same.

This is how the ```src``` directory looks like.

```
ELF-Parser/src$ tree .
.
├── elfp_basic_api.c
├── elfp_ehdr.c
├── elfp_int.c
└── include
    ├── elfp_err.h
    ├── elfp.h
    └── elfp_int.h

1 directory, 6 files
```

**1.** Create a new file in ```src``` directory with the name **Makefile**.

Let us create a rule called **build**:

```
# All the built files(object files and library) will be found in the build directory.
build: 
        gcc elfp_int.c elfp_basic_api.c elfp_ehdr.c -c -fPIC  
        gcc elfp_int.o elfp_basic_api.o elfp_ehdr.o -shared -o libelfp.so  
        mkdir build
        mv libelfp.so *.o build
```

* Go through the rule properly. It creates a shared library ```libelfp.so```. Then it puts all the object files and the library into a directory named ```build```.

Try running it once.

```
/ELF-Parser/src$ make build
gcc elfp_int.c elfp_basic_api.c elfp_ehdr.c -c -fPIC
gcc elfp_int.o elfp_basic_api.o elfp_ehdr.o -shared -o libelfp.so
mkdir build
mv libelfp.so *.o build
ELF-Parser/src$
ELF-Parser/src$
ELF-Parser/src$ ls build
elfp_basic_api.o  elfp_ehdr.o  elfp_int.o  libelfp.so
```

With that, we have our library. 

But we want to use it the way we use ```libc```, or ```pthread``` library. For that, we'll have to copy ```libelfp.so``` into ```/usr/lib/86_64-linux-gnu```. We'll also copy ```elfp.h```, the header file with API into ```/usr/include```. Let us write a rule for the same.

```c
install:
        make build
        sudo cp build/libelfp.so /usr/lib/x86_64-linux-gnu
        sudo mkdir /usr/include/elfp
        sudo cp ./include/elfp.h /usr/include/elfp
```

Run this and you can start using the library.

## 4. Writing a sample application

Let us write a simple ELF parsing application using our library.

First of all, install the library by running ```make install```.

Let us call the application ```elfparse```. Open up a C sourcefile ```elfparse.c``` in ```src``` directory.

**0.** Header files

```c
#include <stdio.h>
#include <elfp/elfp.h>
```

**1.** Initializing the library

```c
int 
main(int argc, char **argv)
{
        if(argc != 2)
        {
                fprintf(stdout, "Usage: $ %s <elf-file-path>\n", argv[0]);
                return -1;
        }

        int ret;
        int fd;
        const char *path = argv[1];
        
        /* Initialize the library */
        ret = elfp_init();
        if(ret == -1)
        {
                fprintf(stderr, "Unable to initialize libelfp.\nExiting..\n");
                return -1;
        }
```

**2.** Opening the ELF file for processing.

```c
        /* Open up the ELF file for processing */
        ret = elfp_open(path);
        if(ret == -1)
        {
                fprintf(stderr, "Unable to open file using libelfp.\nExiting..\n");
                elfp_fini();
                return -1;
        }

        fd = ret;
```

**3.** Let us dump the ELF header.

```c
        /* Dump the ELF header */
        elfp_dump_ehdr(fd);
```

**4.** Let us de-init the library and exit.

```c
        /* De-init the library */
        elfp_fini();

        return 0;
}
```

We'll compile it in the following manner. Before compiling, make sure you have installed the library.

```c
ELF-Parser/src$ gcc elfparse.c -o elfparse -lelfp
ELF-Parser/src$ ls -l elfparse
-rwxr-xr-x 1 dell dell 8616 Dec  8 00:53 elfparse
```

Note the ```-lelfp``` option. This tells the linker that our application depends on the library ```libelfp.so```.

We have the application. Let us run it on a few executables.

```
ELF-Parser/src$ ./elfparse /bin/bash
==================================================
ELF Header: 
00. ELF Identifier: 7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
01. Class: 64-bit object
02. Data Encoding: 2's complement, little endian
03. ELF Version: Current version
04. OS/ABI: Unix System V ABI
05. ELF Type: (DYN) Shared object file
06. Architecture: AMD x86_64 architecture
07. Entry Address: 0x31520
08. Program Header Table file offset: 64 bytes
09. Section Header Table file offset: 1111712 bytes
10. Flags: 0
11. ELF header size: 64 bytes
12. Program Header size: 56 bytes
13. Program Headers count: 9
14. Section Header size: 64 bytes
15. Section Header count: 28
16. Section Header String Table index: 27
==================================================
ELF-Parser/src$
ELF-Parser/src$ ./elfparse /bin/ls
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
```

Our reference output is ```readelf```'s output. Compare its output with ours.

We have a sample ELF parsing application ready. As and when we parse other parts of ELF, we'll keep enhancing the application. Complete code to ```elfparse``` is [here](https://github.com/write-your-own-XXXX/ELF-Parser/blob/master/src/elfparse.c).

## 5. Conclusion

We did a lot in this article.

We went through the ELF header, wrote dump function for it. We built the library, wrote a Makefile to make it easier. We also wrote a sample application which uses our library.

There were few things which were left unexplained - things like Segments, Sections, Program Header, Section Header. We'll be discussing about each of these in good detail in future articles. So, don't worry if you have not understood something properly.

You can get the sourcecode we have written so far [here](https://github.com/write-your-own-XXXX/ELF-Parser/releases/tag/Part6).

In the next article, we'll be exploring **Segments** and **Program Header Table** in detail.

That is it for this article.

Thank you for reading!

----------------------------------------------------------
[Go to next article: Writing an ELF Parsing Library - Part7 - Program Headers](/write/your/own/xxxx/2019/12/08/writing-an-elf-parsing-library-part7-program-headers.html)              
[Go to previous article: Writing an ELF Parsing Library - Part5 - Implementing basic API](/write/your/own/xxxx/2019/12/06/writing-an-elf-parsing-library-part5-implementing-basic-api.html)






