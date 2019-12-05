---
title: Writing an ELF Parsing Library - Part3 - Internal-data-structures - 1
categories: Write your own XXXX
layout: post
comments: true
---

Hello Friend!

In the [first article](/write/your/own/xxxx/2019/11/15/writing-an-elf-parsing-library-part1-what-is-elf.html), we discussed about ELF in brief. In the [second article](/write/your/own/xxxx/2019/11/15/writing-an-elf-parsing-library-part2-piloting-the-library.html), we discussed how our library will look like, how we need to handle errors etc.,

In this article, we'll start writing the library.

Any file format library would have the basic components.

1. **Init component**: Initializes the library, initializes the internal data structures. At the end of this, the library should be usable.

2. **File Input**: A well defined way to take the input from the programmer(user) and process it properly, fill in the internal data structures before the input file is parsed.

3. **Core of the library**: Parsing a given ELF file. This is the part where we'll have to go through every data structure present in the ELF file and convert it into human readable form.

4. **File Close**: Once the parsing is done, the programmer should be able to close that file. This way, all the resources used to parse that file are freed - it can be used for new files.

5. **Deinit/Fini component**: Once the programmer is done with everything, he has to deinitialize the library, clean up everything(like freeing allocated memory) and come out.

In this and next article, we'll be focusing on (1), (5), (2) and (4).

Lets start!

## 0. elfp's Error Infra

Whenever a runtime error occurs, our library should not crash. It should handle the error in an appropriate way and convey the error to the programmer.

There are various ways to do this. We'll resort to the easiest way.

We'll have 2 types of error-handling functions, one which warns about an error and other which terminates the program when an error occurs.

The following is the directory structure of the library's source.

```
ELF-Parser$ tree .
.
├── examples
├── README.md
└── src
    └── include
```

Create a new file ```elfp_err.h``` in ```src/include```. As discussed in the previous article, add the filename, description and license to it.

```c
/*
 * File: elfp_err.h
 *
 * Description: elfparse's error handling infra.
 *
 * License: 
 *
 *            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
 *                  Version 2, December 2004
 *  
 * Copyright (C) 2019 Adwaith Gautham <adwait.gautham@gmail.com>
 *
 * Everyone is permitted to copy and distribute verbatim or modified
 * copies of this license document, and changing it is allowed as long
 * as the name is changed.
 *
 *          DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
 * TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
 *
 * 0. You just DO WHAT THE FUCK YOU WANT TO.
 */

#ifndef _ELFP_ERR_H
#define _ELFP_ERR_H

/* Everything comes here */

#endif /* _ELFP_ERR_H */
```

### a. elfp_err_warn: Warning function

This function simply prints the error statement and does nothing else. Good to log errors.

```c
static void
elfp_err_warn(const char *function_name, const char *err_msg)
{
	fprintf(stderr, "%s: %s\n", function_name, err_msg);
}
```

It takes the function name and error message as arguments. With this, we'll know the root cause of the error and how it propagated to the top.

### b. elfp_err_exit: Exit on errors

When certain critical runtime errors occur, it is best to terminate the program. So, the following function.

```c
static void
elfp_err_exit(const char *function_name, const char *err_msg)
{
	elfp_err_warn(function_name, err_msg);
	fprintf(stderr, "Exiting...\n");
	exit(-1);
}
```

It'll warn and then exit.


## 1. elfp.h: The Header file describing library's API

The API(functions and/or data structures) exposed to users should be present in one single header file. Let us name it ```elfp.h```. Create a new file in ```src/include```.

```
ELF-Parser$ cd src
ELF-Parser/src$ cd include
ELF-Parser/src/include$ 
ELF-Parser/src/include$ touch elfp.h
ELF-Parser/src/include$ ls
elfp.h
```

As discussed in [previous article](/write/your/own/xxxx/2019/11/15/writing-an-elf-parsing-library-part2-piloting-the-library.html), put the filename, description and license in this file.

```c
ELF-Parser/src/include$ head -n 25 elfp.h 
/*
 * File: elfp.h
 *
 * Description: Listing of all API exposed to the programmer
 *
 * License: 
 *
 *            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
 *                  Version 2, December 2004
 *  
 * Copyright (C) 2019 Adwaith Gautham <adwait.gautham@gmail.com>
 *
 * Everyone is permitted to copy and distribute verbatim or modified
 * copies of this license document, and changing it is allowed as long
 * as the name is changed.
 *
 *          DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
 * TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
 *
 * 0. You just DO WHAT THE FUCK YOU WANT TO.
 */
```

Finally, the check which makes sure this header file is included only once.

```c
#ifndef _ELFP_H
#define _ELFP_H

/* All the function declarations, data structures comes here */

#endif /* _ELFP_H */
```

We'll be needing one header file inside this - ```elf.h```.

```c
#ifndef _ELFP_H
#define _ELFP_H

#include <elf.h>

/* All the function declarations, data structures comes here */

#endif /* _ELFP_H */

```

With that, we are ready to design the API.

## 2. The API

**API**(Application Programming Interface) is the interface given to programmers to use our library. API can consist of functions, data structures, macros etc.,

### **a. Init and Fini**

How should the initialization API look like?

Internally, initialization could be a lot of work - creating necessary objects, initializing them and making them usable. But, the programmer should be able to initialize the library easily. So, the init function can look like this.

```c
/*
 * elfp_init: Initializes the library. 
 * 	* MUST be called before any other library functions are called.
 */
void
elfp_init();
```

We'll define the function later. Add the above declaration to ```elfp.h```.

Once the programmer is done using the library, he can free up all the resources used so that it can be used elsewhere. He can deinitialize the library in the following manner.

```c
/*
 * elfp_fini: Cleans up everything and deinits the library.
 */
void
elfp_fini();
```

* **fini** is short for **finish**.


### **b. Opening an ELF file**

Once the programmer is done initializing the library, he should be able to feed any ELF file as input file. We need to pre-process the file and keep it ready to parse any part requested by the programmer. We can have a function like this.

```c
void
elfp_open(const char *elfp_elf_path);
```

* The library takes in the path to ELF file as input. Later, we can have functions like ```elfp_parse_elf_header()```, ```elfp_parse_program_header()``` etc., to parse specific parts of the ELF file.

What if the programmer wants to parse another file? He'll have to call ```elfp_open()``` again. Now, 2 files are open. How will this work? Will the library erase all data related to the first file and put data related to the second file? Or will it store both? Even if it stores both, there is no way the programmer can tell which needs processing. For example, you do

```c
elfp_open("file1")
elfp_open("file2")

elfp_parse_elf_header()
```

Which file's ELF Header should the library parse? How will the library know? 

One solution is **to pass the ELF File path to every function**.

```c

elfp_open("file1")
elfp_open("file2")

elfp_parse_elf_header("file1")
elfp_parse_elf_header("file2")
```

This removes all the ambiguity and the library can be designed in a way to handle this.

There is a better, more elegant solution to this problem.

Notice how Linux handles this. The **open()** function opens up a file for reading/writing. It returns a **file descriptor**, which is used to uniquely identify that file.

```c

fd1 = open("file1.txt", O_RDONLY);
fd2 = open("file2.txt", O_RDWR);

```

We'll do the same.

The ```elfp_open()``` should return an integer, which is a unique descriptor for that ELF file. Now, the function looks like this.

```c
/*
 * elfp_open: Opens the specfied ELF file and returns a handle.
 *
 * @arg0: Path / name of ELF File
 *
 * @return: A non-negative integer - handler on success.
 * 		(-1) on failure.
 */
int
elfp_open(const char *elfp_elf_path);
```

All the parse functions will take this descriptor as argument, so that we can distinguish between files.

### **c. Closing an ELF file**

Once the programmer is done processing this file, he can close it so that the resources could be used elsewhere.

Because a file descriptor is used to identify the file, our close function looks like this.

```c
/*
 * elfp_close: Closes everything about the specified handle.
 *
 * @arg0: User handle obtained from an elfp_open call.
 */
int
elfp_close(int user_handle);
```

With that, we have 4 basic API.

## 3. Internal Data Structures

In the previous section, we decided on how the API should look like.

In this section, we'll take a step forward in implementing the 4 API.

To implement ```elfp_init``` and ```elfp_fini``` we need to define the internal data structures first. Only after that, we can write code to initialize / deinitialize them.

To implement ```elfp_close```, we need to know what data structures we maintain per open file.

What data(or metadata) do we need to store for every open file? Do we actually have to store any metadata? Asnwering these questions will help us in defining data structures needed for every file, Based on that, we can define data structures to extend the library to support multiple open files.

### **a. How do we get an Input ELF File ready for parsing?**

When a programmer passes a file path to our library with ```elfp_open()``` function, what all do we need to do so that the core component of the library can take it for parsing?

Let us start with simple points.

First of all, we need to check if the library has the permissions to read that file or not.

Suppose we have the permissions, we need to ```open()``` the file for reading. Here, we get a ```file descriptor``` for the ELF file - which is essential and has to be stored.

Once we have opened it, we need to check if the file is actually an ELF file or some other file. How do we check this?

* We can use the **magic characters** to check it. The first 4 bytes of **any** ELF file is **0x7f**, **E**, **L**, **F**.

Now we know the file passed is a valid ELF file.

Suppose the programmer requests for ELF Header in human readable form. How do we get it? Let us think about it.

1. ELF Header is the structure present at the beginning of every ELF file.

2. From ```elf```'s manpage, the size of 64-bit ELF Header is **64 bytes**.

3. We can easily ```read()``` first 64 bytes of the file, put it into a buffer and then parse it.
    ```c
    unsigned char buffer[sizeof(Elf64_Ehdr)];
    ret = read(fd, buffer, sizeof(Elf64_Ehdr));
    ```

4. Then parse it.

    ```c
    Elf64_Ehdr *ehdr = (Elf64_Ehdr *)buffer;
    printf("Entry Address: %p\n", ehdr->e_entry);
    /* Similarly, all members are available now */
    ```
5. In the end, we'll have an array of buffers, each buffer having a piece of the ELF file.

Instead of this, how will it be if we can map the whole ELF file onto this process's address space? The complete file will be in one place, instead of various, individual buffers. Managing it will be simple.

This can be done using a system call called ```mmap```(**memory map**). This is an interesting system call, which we will discuss in length later.

For now, you can think that the complete ELF file is in memory. So, we can access any part of the file we want, we won't have to ```read()``` everytime. 

Let us take a look at ```mmap```'s manpage.

```
MMAP(2)                                           Linux Programmer's Manual                                          MMAP(2)

NAME
       mmap, munmap - map or unmap files or devices into memory

SYNOPSIS
       #include <sys/mman.h>

       void *mmap(void *addr, size_t length, int prot, int flags,
                  int fd, off_t offset);
```

* This system call returns an ```address``` to the beginning of file in memory. To locate every structure in the ELF file, this ```address``` is the reference address. So, we'll have to store this in our **per-file metadata**.

* The first argument is ```addr```. The user can suggest the OS to map the file at that particular address. Because we don't care where the OS maps our file, we'll pass a ```NULL``` to it.

* The second argument is the ```length``` of the mapping - this is the size of the file. This is also one essential piece of info about our ELF file. So, we'll store this also in our **per-file metadata**.

* Next is the ```prot```, basically the permissions of the mapping. We are just reading the file and nothing more. So, it'll be ```r--```.

*  Ignore the ```flags``` argument for now.

* ```fd``` is ELF file's ```open()``` file descriptor. We'll store this also in our metadata.

* ```offset``` is the offset from where the OS should map. We need the entire file. So, offset will be **0**.

Once we have mapped, ```mmap``` returns an ```address```, using which we can proceed further like this.

```c
Elf64_Ehdr *ehdr = (Elf64_Ehdr *)address;
printf("Entry Address: 0x%lx\n, ehdr->e_entry);
/* ehdr is the ELF Header now */
```

From this exercise, we got clarity over two things.

1. What all should our **per-file metadata** be?
2. We got the rough implementation of ```elfp_open()```.

### **b. elfp_main**: per-file metadata structure

Let us define a C structure ```elfp_main``` which will contain everything we noted in the above sub-section.

This is a data structure internal to the library. It will never be used by the programmer. So, to store all the internal data structures, we'll create another header file ```elfp_int.h``` in ```src/include```.

The structure looks like this.

```c
/*
 * struct elfp_main: An open file's metadata.
 */
#define ELFP_FILEPATH_SIZE	256

typedef struct elfp_main
{	
	/* File descriptor of the open file */
	int fd;

	/* File Path */
	char path[ELFP_FILEPATH_SIZE];

	/* Other details related to file */
	unsigned long int file_size;

	/* Starting address of mmap */
	unsigned char *start_addr;

    /* Handle sent to the user */
	int handle;

} elfp_main;
```

* While processing every file, many new objects will be created(using ```malloc```, ```calloc```). Once processing is done, we need free them all. To free them, we need to keep note of all those **addresses**. So, we'll maintain a simple vector inside ```elfp_main``` itself.

We'll use the following vector to store these addresses.

```c
typedef struct elfp_free_addr_vector
{
	void **addrs;
	unsigned long int total;
	unsigned long int count;
} elfp_free_addr_vector;
```

Add this structure definition to ```elfp_int.h```.

```elfp_main``` structure looks like this now.

```c
typedef struct elfp_main
{	
    /* File descriptor of the open file */
    int fd;

    /* File Path */
    char path[ELFP_FILEPATH_SIZE];

    /* Other details related to file */
    unsigned long int file_size;

    /* Starting address of mmap */
    unsigned char *start_addr;

    /* Handle sent to the user */
    int handle;

    /* Many functions allocate objects in heap and return the pointer 
     * to it to the user.
     *
     * Need to keep track of all this memory and free all of it in the end.
     */
    elfp_free_addr_vector free_vec;

} elfp_main;
```

With this, we have our ```per-file``` data structure ready.

### c. How do we extend this to support multiple open files?

We decided to build a library which can handle multiple open files at once.

How do we do it?

Simple solution is to just keep a **vector/array of the per-file structures**. As and when the programmer opens a new ELF file, a new ```elfp_main``` structure is created, initialized and put into the vector.

Let us now define the vector.

```c
/*
 * struct elfp_main_vector: A vector of elfp_main structure.
 *
 * Needed to handle multiple open files.
 */
typedef struct elfp_vector_main
{
    /* Array of pointer to elfp_main structure */
    elfp_main **vec;

    /* Size of the vector */
    unsigned long int total;

    /* Handle of the latest opened file.
     * This is NOT the total number of open files. */
    unsigned long int latest;

} elfp_main_vector;
```

Now, we have the 2 core data structures required for our library to work.

With every data structure we define, we also need to define functions to make the data structure work - to initialize it, update it, manipulate it, free it etc., What functions to define solely depends on the data structure.


## 4. elfp_free_addr_vector: Structure and Functions

This vector is used maintain the **to-be-freed** addresses. An instance of this structure is present in every ```elfp_main``` object.

```c
typedef struct elfp_free_addr_vector
{
	void **addrs;
	unsigned long int total;
	unsigned long int count;
} elfp_free_addr_vector;
```

The vector has 3 members: 

1. **addrs**: A pointer to a list of pointers(addresses) each of which will be freed in the end.
2. **total**: The total number of addresses which can be stored in the vector.
3. **count**: The number of vectors currently stored.

It can be seen that ```count <= total``` in a valid vector.

We'll now define all the functions needed to work with ```elfp_free_addr_vector``` structure.

### a. elfp_free_addr_vector_init(): Initializes the vector

This function should initialize a specified vector structure. The way to do it is to pass a reference to that vector structure to this function. The following is its declaration.

```c
/*
 * elfp_free_addr_vector_init: Initializes a free list
 * 
 * @arg0: A reference to an elfp_free_addr_vector structure.
 * 
 * @return: Returns -1 on error, 0 on successful initialization.
 */
int 
elfp_free_addr_vector_init(elfp_free_addr_vector *vec);
```
Put this declaration in ```elfp_int.h```.

What all should we do during initialization?

1. Allocate some memory for ```addrs``` to hold addresses.
2. Initialize ```count``` to 0.

Let us define it now.

**1.** Do the basic check.
```c
int
elfp_free_addr_vector_init(elfp_free_addr_vector *vec)
{
    /* Basic check */
    if(vec == NULL)
    {
        elfp_err_warn("elfp_free_addr_vector_init", "NULL argument passed");
        return -1;
    }     
```

**2.** Allocate memory to store 1000 addresses.
```c
    /* Total number of addresses it can hold at first is 1000 */
    vec->total = 1000;

    /* Allocate the same amount of memory */
    vec->addrs = calloc(vec->total, sizeof(void *));
    if(vec->addrs == NULL)
    {
        elfp_err_warn("elfp_free_vector_init", "calloc() failed");
        return -1;
    }
```

**3.** Initially, ```count``` is 0.
```c
    /* Init the count */
    vec->count = 0;

    /* Good to go! */
    return 0;
}
```

With that, we have our init function. This is a function related to an internal data structure. Create a new C sourcefile ```elfp_int.c``` in ```src```. Put the above implementation there.

### b. elfp_free_addr_vector_fini(): Deinitializes the vector

The whole idea of having this structure is to free up all the stored addresses. This function will do the same.

This function should deinitialize a specified vector. So, a reference to that vector should be passed to this function. The following is its declaration.

```c
/*
 * elfp_free_addr_vector_fini: Deinitializes a free list.
 *      * It frees up all the stored addresses and
 *      frees up the memory allocated for the list.
 * 
 * @arg0: A reference to an elfp_free_addr_vector structure.
 */
void
elfp_free_addr_vector_fini(elfp_free_addr_vector *vec);
```

Add the above declaration to ```elfp_int.h```.

This function's implementation is quite simple.

**1.** Basic check.
```c
void
elfp_free_addr_vector_fini(elfp_free_addr_vector *vec)
{
        /* Basic check */
        if(vec == NULL)
        { 
                elfp_err_warn("elfp_free_addr_vector_fini", "NULL argument passed");
                return;
        }
```

**2.** Free up all the stored addresses.
```c
        /* First, free up all the stored addresses */
        for(unsigned long i = 0; i < vec->count; i++)
                free(vec->addrs[i]);
```

**3.** Free up memory allocated for ```addrs```.
```c
        /* Now, free up addrs */
        free(vec->addrs);
 
        /* All set */
        return;
}
```

With that, we have the deinit function ready. Put it into ```elfp_int.c```.

### c. elfp_free_addr_vector_add(): Adding an address to the vector

Whenever a new object is created for an open file, the object's address should be added to this list. Now, we'll implement the function which will add a given address to a specified vector. Based on its description, we'll have a function like this.

```c
int
elfp_free_addr_vector_add(elfp_free_addr_vector *vec, void *addr);
```

What all should this function do?

**1.** Basic check.
```c
int
elfp_free_addr_vector_add(elfp_free_addr_vector *vec, void *addr)
{
        /* Basic check */
        if(vec == NULL || addr == NULL)
        {                                                  
                elfp_err_warn("elfp_free_addr_vector_add", 
                                "NULL argument(s) passed");
                return -1;
        }
```

**2.** Check if the vector is full. If it is full, allocate more memory.

```c
        void *new_addr = NULL;

        /* Check if the vector is full */
        if(vec->count == vec->total)
        {       
                /* Allocate more memory */
                new_addr = realloc(vec->addrs, 
                        (vec->total + 1000) * sizeof(void *));
                if(new_addr == NULL)
                {       
                        elfp_err_warn("elfp_free_addr_vector_add",                     
                                        "realloc() failed");
                        return -1;
                }
                
                /* Initialize the new memory */
                memset(((char *)new_addr) + vec->total * sizeof(void *), '\0',
                                                1000 * sizeof(void *));
                
                vec->addrs = new_addr;
                vec->total = vec->total +  1000;
        }
```

**3.** Add the address to the vector.
```c
        /* Now, put the address into the list */
        vec->addrs[vec->count] = addr;
        vec->count = vec->count + 1;

        /* Good to go! */
        return 0;
}
```

With that, we are done with ```elfp_free_addr_vector``` structure. We have the structure and we have functions to work with it.

I suggest you to write a few sample C programs to make sure ```elfp_free_addr_vector``` works properly. Checkout [check_free_list.c](https://github.com/write-your-own-XXXX/ELF-Parser/blob/master/examples/check_free_list.c).

## 5. Conclusion

In this article, we decided on 4 important API functions - ```elfp_init```, ```elfp_open```, ```elfp_close```, ```elfp_fini```. 

Later, we defined 2 very important data structures ```elfp_main``` and ```elfp_main_vector**.

We also defined the free list vector ```elfp_free_addr_vector``` and wrote functions to manage it.

In the next article, we'll write functions for ```elfp_main``` and ```elfp_main_vector```.

Thank you for reading!

-------------------------------------------------
[Go to next article: Writing an ELF Parsing Library - Part4 - Internal Data Structures - 2](/404.html)                         
[Go to previous article: Writing an ELF Parsing Library - Part2 - Piloting the Library](/write/your/own/xxxx/2019/11/15/writing-an-elf-parsing-library-part2-piloting-the-library.html)