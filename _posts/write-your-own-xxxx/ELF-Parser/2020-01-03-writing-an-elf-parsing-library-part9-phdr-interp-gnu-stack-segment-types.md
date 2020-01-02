---
title: Writing an ELF Parsing Library - Part9 - PHDR, INTERP and GNU_STACK segment types
categories: write your own XXXX
layout: post
comments: true
---

Hello Friend!

In the last 2 articles([1](/write/your/own/xxxx/2019/12/08/writing-an-elf-parsing-library-part7-program-headers.html), [2](/write/your/own/xxxx/2019/12/09/writing-an-elf-parsing-library-part8-program-header-table.html)), we discussed about **Program Headers** in good detail. We explored various types of Segments which can be part of an ELF file.

Now, we are in a position to understand every segment in detail. We will do a detailed analysis on what each type of segment contain, data structures associated with it and understanding why that segment is needed.

In this article, we'll take up 3 fairly simple segment types ```PHDR```, ```INTERP``` and ```GNU_STACK``` and clearly understand each segment in detail.

Lets start!

## 0. Introduction

Let us use a simple hello program for our exploration.

```c
$ cat hello.c 
#include <stdio.h>
#include <unistd.h>

int main()
{
	printf("Hello!\n");
	return 0;
}
$
$ gcc hello.c -o hello
```

We'll also be using ```elfparse```, the ELF parsing tool we wrote using our library. You can download the source and build it from [here](https://github.com/write-your-own-XXXX/ELF-Parser).

To get the full picture of every segment, we'll write parsing code for every segment. To do this, we'll need some initial code. Let us write that first and then dive into individual segments.

## 1. Infra to parse Segments

Thinking from programmer's point of view, he should have a simple function, which specifies the handle and segment type which he wishes to dump. We'll have one more function which just gives a pointer to that segment, in case the programmer wants to parse the segment himself.

Create a new C sourcefile ```elfp_seg.c ```. Let us put all function definitions related to segment parsing there. Because they are API exposed to programmers, we'll declare functions in ```elfp.h```.

We'll start with the second function - the function which returns pointer(s) to segments of a specified segment type. Note that there might be multiple segments of the same type. Example: We have seen executables having 2 ```PT_LOAD``` type segments. In that case, we'll need to return pointers to both the segments.

Take a look at its declaration - goes in ```elfp.h```.

```c
/*
 * elfp_seg_get(): 
 * 
 * @arg0: elfp handle
 * @arg1: Segment name. Eg: "INTERP", "TLS", "LOAD", "DYNAMIC" etc.,
 * @arg2: A pointer to an unsigned long integer. This is the second 
 *              return value of this function.
 *  
 * @return: A pointer to an array of (void *) pointers, each pointer
 *              pointing to a segment.
 * 
 * Essentially, you'll be getting the following info.    
 * 
 * 1. An array of pointers, each of them pointing to a segment of the
 *      specified type.
 * 2. Total number of pointers in the above array.
 */
void**  
elfp_seg_get(int handle, const char *seg_type, unsigned long int *ptr_count);
```

There are a few cases to consider.

1. Happy path where there are one or more segments of the requested type.
2. Some internal error occurs and the function returns an error.
3. A case where there are no segments of the requested type.

From the function's return type, we can convey only 2 cases to the caller - because it can either be NULL or a some positive value.

How do we convey the third case?

We can use that ```ptr_count``` to do that. Now, take a look at the declaration.

```c
/*
 * elfp_seg_get(): 
 * 
 * @arg0: elfp handle
 * @arg1: Segment name. Eg: "INTERP", "TLS", "LOAD", "DYNAMIC" etc.,
 * @arg2: A pointer to an unsigned long integer. This is the second
 *              return value of this function.
 * 
 * @return: A pointer to an array of (void *) pointers, each pointer
 *              pointing to a segment.
 *
 * Essentially, you'll be getting the following info.
 *
 * 1. An array of pointers, each of them pointing to a segment of the
 *      specified type.
 * 2. Total number of pointers in the above array.
 *
 * 3 cases can occur:
 * a. One or more segments of requested type are present - Happy case.
 * 
 * b. Some internal error occurs and library returns an error.
 *      * @return = NULL
 *      * @arg2 = 1
 *
 * c. No segments of requested type are present.
 *      * @return = NULL
 *      * @arg2 = 0
 *
 * From @arg2, the programmer should know what actually happened
 * and why the function returned a NULL.
 */

void**
elfp_seg_get(int handle, const char *seg_type, unsigned long int *ptr_count);
```

With that done, let us implement it.

**1.** Basic check

```c
void**      
elfp_seg_get(int handle, const char *seg_type, unsigned long int *ptr_count)    
{    
        /* Basic checks */    
        if(seg_type == NULL || ptr_count == NULL ||     
                                elfp_sanitize_handle(handle) == -1)    
        {    
                elfp_err_warn("elfp_seg_get", "Invalid argument(s) passed");    
                goto fail_err;    
        }    
```

**2.** As always, we'll need to parse 32-bit and 64-bit executables separately. Let us first get PHT and class of the ELF file. Depending on its class, let us write 2 other functions to do the job for us.

Let us get the PHT.

```c
        int ret;
        void **ptr_arr = NULL;
        void *pht = NULL;
        unsigned long int class;

        /* Get the PHT */
        pht = elfp_pht_get(handle, &class);
        if(pht == NULL)
        {
                elfp_err_warn("elfp_seg_get", "elfp_pht_get() failed");
                goto fail_err;
        }
```

Based on **class**, let us decide.

```c
        switch(class)
        {
                case ELFCLASS32:
                        ptr_arr = elfp_seg32_get(handle, pht, seg_type, ptr_count);
                        if(ptr_arr == NULL)
                        {
                                elfp_err_warn("elfp_seg_get", 
                                "elfp_seg32_get() failed / no segment of requested type found");           
                        }
                        return ptr_arr;
                
                /* 64-bit ELF files and any other case is analyzed as 64-bit
                 * ELF files */
                default:
                        ptr_arr = elfp_seg64_get(handle, pht, seg_type, ptr_count);
                        if(ptr_arr == NULL)
                        {
                                elfp_err_warn("elfp_seg_get", 
                                "elfp_seg64_get() failed / no segment of requested type found");
                        }
                        return ptr_arr;
        }
```

Let us get to ```elfp_seg64_get()```'s implementation first. The 32-bit counterpart will be very similar.

### Implementation of elfp_seg64_get()

Let us jot down the plan, later get to implementation.

1. With segment type given to us in string form, we need to convert it to ```PT_XXXX``` form so that we can work easily.

2. With PHT and segment type, we can catch hold of all the Program Headers of the requested segment type.

3. Allocate memory to store the pointers to those segments - an array of pointers.

4. Iterate through the PHT and update the above array. To find the address of each segment, we'll need the starting address of the mapped ELF file.

5. This array is dynamically allocated and needs to be freed at the end. Don't forget to add this to the free-address vector.

That is the plan. Let us start!

**1.** Basic checks: The caller needs to do it.

**2.** Variables used.

```c
void**
elfp_seg64_get(int handle, Elf64_Phdr *pht, const char *seg_type, unsigned long int *ptr_count)
{
        /* No sanity checks */

        int ret;
        Elf64_Ehdr *ehdr = NULL;
        Elf64_Phdr *ph = NULL;
        elfp_main *main = NULL;
        void *start_addr = NULL;
        int phnum;
        int enc_seg_type;
        int i;
        unsigned long int count, total;
        void **ptr_arr = NULL;
        elfp_free_addr_vector *free_vec = NULL;
        void **temp = NULL;
```

Let us start doing small tasks which will help us do the large ones.

**3.** At the moment, we have a pointer to PHT with us. To iterate through it, we need the total number of Program Headers present in PHT. Let us find it out.

```c
        /* Get the total number of program headers */    
        ehdr = elfp_ehdr_get(handle);    
        if(ehdr == NULL)    
        {    
                elfp_err_warn("elfp_seg64_get", "elfp_ehdr_get() failed");    
                goto fail_err;   
        }    
        phnum = ehdr->e_phnum;    
```

```fail_err``` is just a label which sets ```ptr_count``` to 1 signifying it was an internal error and returns a ```NULL```.

IF the header is corrupted,

```c
        /* In case of corrupted headers:    
         * The upper bound is simply based on the datatype used to store the    
         * number of program headers in ELF header. A uint16 is used. */    
        if(phnum == 0 || phnum > UINT16_MAX)    
        {    
                elfp_err_warn("elfp_seg64_get", "Invalid number of Program Headers");    
                goto fail_err;
        }
```

Let us move to our next small task.

**4.** We need find the the starting address of the mapped ELF file. We'll need it later to get the addresses of segments (if they exist).

```c
        /* Get the starting address of the ELF file mapped to memory */
        main = elfp_main_vec_get_em(handle);
        if(main == NULL)
        {
                elfp_err_warn("elfp_seg64_get", "elfp_main_vec_get_em() failed");
                goto fail_err;
        }

        start_addr = elfp_main_get_staddr(main);
        if(start_addr == NULL)
        {
                elfp_err_warn("elfp_seg64_get", "elfp_main_get_staddr() failed");
                goto fail_err;
        }
```

**5.** Now, let us convert the segment type in string form to the standard ```PT_XXXX``` form. I want you to write the function for that.

```c
        /* The user/programmer gives the segment name in string form.
         * We need to convert it into PT_XXXX form, so that it'll be easy
         * for us to iterate and compare */
        enc_seg_type = elfp_seg_get_type(seg_type);
        if(enc_seg_type == -1)
        {
                elfp_err_warn("elfp_seg64_get", 
                        "Invalid Segment entered / I don't know how to parse it");
                goto fail_err;
        }
```

Now, we are ready to do some heavylifting.

**6.** Allocate some memory. But how much memory to allocate? We'll never know how many segments are present before iterating through PHT once. Considering linker generated ELF files, we know that certain segments like ```INTERP```, ```DYNAMIC``` are present once. There can be multiple ```LOAD```s and so on. I think we need to prepared for the worst case. Be ready to list any number of segments.

How do we do that? The following is a plan.

Initially, we allocate reasonable amount of memory, say we allocate memory for 5 addresses. In normal cases, I think this is more than enough, knowing that there are many segments which are one in number.

Later, while iterating through PHT if we find that there are more than 5 segments, we dynamically increase its size.

Let us start with allocation of memory.

```c
        /* A naive way: Allocate memory for 5 segments.
         * realloc() to the rescue! */
        ptr_arr = calloc(5, sizeof(void *));
        if(ptr_arr == NULL)
        {
                elfp_err_warn("elfp_seg64_get", "malloc() failed");
                goto fail_err;
        }
```

**7.** Now, let us iterate through PHT.

```c
        count = 0;
        total = 5;
        for(i = 0; i < phnum; i++)
        {
                ph = pht + i;
                if(ph->p_type == enc_seg_type)
                {
                        /* If it has hit our limit, then */
                        if(count == total)
                        {
                                temp = realloc(ptr_arr, (total + 5) * sizeof(void *));
                                if(temp == NULL)
                                {
                                        elfp_err_warn("elfp_seg64_get",
                                        "realloc() failed. Unable to accomodate all segments of the given type");
                                        /* We need to decide what to do here. Should we simply send
                                         * the segments collected so far to the caller, or should we abort
                                         * this operation, free up the memory and return an error.
                                         *
                                         * We are returning an error */
                                        goto fail_free;
                                }
                                ptr_arr = temp;
                                total = total + 5;
                        }
                        ptr_arr[count] = (void *)(start_addr + ph->p_offset);
                        count++;
                }                                                                                                                                                        
        }
```

I need you to go through the code thoroughly and understand what it is doing.

Every iteration,

1. It'll compare the Program Header's type with the requested type. If they are the same then,

    ```c
                ph = pht + i;
                if(ph->p_type == enc_seg_type)
                {
    ```

2. We need to find the segment's starting address using Program Header info and add it to the array. But, what if that array is full. So, before even doing that, we need to check if that array is full. If it is, allocate more memory.

    ```c
                            /* If it has hit our limit, then */
                        if(count == total)
                        {
                                temp = realloc(ptr_arr, (total + 5) * sizeof(void *));
                                if(temp == NULL)
                                {
                                        elfp_err_warn("elfp_seg64_get",
                                        "realloc() failed. Unable to accomodate all segments of the given type");
                                        /* We need to decide what to do here. Should we simply send
                                         * the segments collected so far to the caller, or should we abort
                                         * this operation, free up the memory and return an error.
                                         *
                                         * We are returning an error */
                                        goto fail_free;
                                }
                                ptr_arr = temp;
                                total = total + 5;
                        }

    ```

3. Now, add the address peacefully.

    ```c
                            ptr_arr[count] = (void *)(start_addr + ph->p_offset);
                        count++;
                }
    ```

After iterating through the PHT, our array is ready!

**8.** What if there are no segments?

```c
        /* What if there are no such segments?
         *
         * This case should be different from an erroneous case.
         * This should be treated as a normal case */
        if(count == 0)
        {
                elfp_err_warn("elfp_seg64_get", "No segments of the requested type are present");
                
                /* For this case, count will be 0 */
                *ptr_count = 0;
                free(ptr_err);
                return NULL;
        }
```

**9.** Some cost cutting. One possibility is that we might have allocated more memory than we need for the array. Say ```count``` is 7, we would have allocated memory for 10. Let us free that extra memory.

```c
        /* All set. We may have allocated more memory. Let us cut it */
        if(count < total)
        {
                temp = realloc(ptr_arr, count * sizeof(void *));
                if(temp == NULL)
                {
                        elfp_err_warn("elfp_seg64_get",
                        "realloc() failed. Unable to remove the extra memory allocated");
                        /* This shouldn't happen. But it may happen.
                         * Let us just leave it. */
                }
                ptr_arr = temp;
        }
```

Now, we are all set. We have an array of pointer, each one pointing to a segment of requested type.

**10.** We need to add it to the free address vector.

```c
        /* Now, we have a pointer which we should add to the free address vector */
        free_vec = elfp_main_get_freevec(main);
        if(free_vec == NULL)
        {
                elfp_err_warn("elfp_seg64_get",
                                "elfp_main_get_freevec() failed");
                goto fail_free;
        }
        
        ret = elfp_free_addr_vector_add(free_vec, ptr_arr);
        if(ret == -1)
        {
                elfp_err_warn("elfp_seg64_get",
                                "elfp_free_addr_vector_add() failed");
                goto fail_free;
        }
```

**11.** We are good to go!

```c
        /* At this point, we have an array of pointers, each pointer
         * pointing to a segment of requested type.
         *
         * It is time to return */
        *ptr_count = count;
        
        return ptr_arr;
```

This was a crazy function to write.

```elfp_seg32_get()``` - the 32-bit version of this function is very similar, just that you will be working with 32-bit structures.

Now, the dump function.

### elfp_seg_dump(): Dumps a specified segment

This function is pretty simple.

We can get the pointers to the segments from ```elfp_seg_get()```. Based on segment type, we write dump functions.

Its declaration is very similar to ```elfp_seg_get()```.

```c
/*
 * elfp_seg_dump: Dumps the specified segment, if it is dumpable.
 *
 * @arg0: elfp handle
 * @arg1: Segment name. Eg: "INTERP", "TLS", "LOAD", "DYNAMIC" etc.,
 *
 * @return: 0 on success, -1 on failure.
 */

int
elfp_seg_dump(int handle, const char *seg_type);
```

Let us implement it.

**1.** Basic check

```c
int
elfp_seg_dump(int handle, const char *seg_type)
{
        /* Basic check */
        if(seg_type == NULL || elfp_sanitize_handle(handle) == -1)
        {
                elfp_err_warn("elfp_seg_dump", "Invalid argument(s) passed");
                return -1;
        }
```

**2.** Here, we have 2 options. Directly call ```elfp_seg_get()``` or determine the class, write 2 different functions and call ```elfp_segN_get()``` functions inside them. We'll go ahead with the second option.

```c
        /* Get the pointer to the PHT */
        pht = elfp_pht_get(handle, &class);
        if(pht == NULL)
        {
                elfp_err_warn("elfp_seg_dump", "elfp_pht_get() failed");
                return -1;
        }

        switch(class)
        {
                case ELFCLASS32:
                        ret = elfp_seg32_dump(handle, pht, seg_type);                                                                                                    
                        if(ret == -1)                                                                                                                                    
                        {                                                                                                                                                
                                elfp_err_warn("elfp_seg_dump", "elfp_seg32_dump() failed");                                                                              
                                return -1;                                                                                                                               
                        }                                                                                                                                                
                        return 0;                                                                                                                                        
                
                /* 64-bit ELF files and any other case is analyzed as 64-bit
                 * ELF files */
                default:
                        ret = elfp_seg64_dump(handle, pht, seg_type);
                        if(ret == -1)
                        {
                                elfp_err_warn("elfp_seg_dump", "elfp_seg64_dump() failed");
                                return -1;
                        }
                        return 0;
        }
}
```

Based on class, we have ```elfp_seg64_dump()``` and ```elfp_seg32_dump()```. Let us implement the 64-bit version.

### Implementation of elfp_seg64_dump()

**1.** Go ahead and get the segments' addresses.

```c
int
elfp_seg64_dump(int handle, Elf64_Phdr *pht, const char *seg_type)
{
        /* No need for basic checks because they are all sanitized inputs */
        
        int ret;
        void **ptr_arr = NULL;
        unsigned long int ptr_count;
        int enc_seg_type;

        /* We have the elfp_seg64_get() function. Let us use it and quickly
         * get our segment pointer array */
        ptr_arr = elfp_seg64_get(handle, pht, seg_type, &ptr_count);
        if(ptr_arr == NULL)
        {
                elfp_err_warn("elfp_seg64_dump", "elfp_seg64_get() failed");
                return -1;
        }
```

**2.** Get the segment type in standard form, so that we can work easily.

```c
        /* Depending on the segment type, we need to dump it */
        enc_seg_type = elfp_seg_get_type(seg_type);
        if(enc_seg_type == -1)
        {
                elfp_err_warn("elfp_seg64_dump", "elfp_seg_get_type() failed");
                return -1;
        }
```

**3.** Based on segment type, let us dump the segment.

```c
        /* Now, let us start */
        switch(enc_seg_type)
        {
        /*
                case PT_INTERP:
                        elfp_seg_dump_interp(ptr_arr, ptr_count);
                        return 0;
                
                default:
                        elfp_err_warn("elfp_seg64_dump",
                        "Still have to write parse code");
                        return -1;
        */
        }
```


We'll have something like that. I hope you get the idea.

As and when we discuss a segment type, all we have to do is just write a dump function and add a ```case``` inside the ```switch()``` statement. All the other code is written and ready.

I want you to write the 32-bit version of this.

We are done with Segment Dump infra here. Let us get back to exploring segments!

## 2. PHDR

Let us see what the manpage says.

```
                 PT_PHDR     The  array  element,  if  present, specifies the location and size of the program header table itself,
                             both in the file and in the memory image of the program.  This segment type may not  occur  more  than
                             once  in  a file.  Moreover, it may occur only if the program header table is part of the memory image
                             of the program.  If it is present, it must precede any loadable segment entry.
```

If present, it specifies the location and size of the **Program Header Table** itself.

Let us take a look at ```PHDR``` Program Header in our ```hello``` program.

```
$ ./elfparse ./hello
.
.
.
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
.
.
```

* Its file offset is **64 bytes**, which is just after ELF header.

* Take a look at the Segment size. It is **504 bytes**. This is the total size of the Program Header Table.
    * There are 9 Program Headers, each of size 56 bytes. You can look at ```elfparse```'s output.

Let us take a look at a few shared libraries' ```PHDR```.


```
$ ./elfparse /lib/x86_64-linux-gnu/libc-2.27.so 
.
.
.
==================================================
Program Header Table: 

Entry 00: 
00. Type: PHDR (Entry for header table)
01. Flags: r--
02. Segment file offset: 64 bytes
03. Virtual Address: 0x40
04. Physical Address: 0x40
05. Segment size in file: 560 bytes
06. Segment size in memory: 560 bytes
07. Segment Alignment: 0x8
---------------------------------------------
```

```libc-2.27.so``` has a ```PHDR```.

Let us try some random shared library.

```
$ ./elfparse /usr/lib/x86_64-linux-gnu/librt.so
.
.
.
==================================================
Program Header Table: 

Entry 00: 
00. Type: LOAD (Loadable program segment)
01. Flags: r-x
02. Segment file offset: 0 bytes
03. Virtual Address: 0x0
04. Physical Address: 0x0
05. Segment size in file: 27700 bytes
06. Segment size in memory: 27700 bytes
07. Segment Alignment: 0x200000
---------------------------------------------
Entry 01: 
00. Type: LOAD (Loadable program segment)
01. Flags: rw-
02. Segment file offset: 28008 bytes
03. Virtual Address: 0x206d68
04. Physical Address: 0x206d68
05. Segment size in file: 1284 bytes
06. Segment size in memory: 3704 bytes
07. Segment Alignment: 0x200000
---------------------------------------------
Entry 02: 
00. Type: DYNAMIC (Dynamic Linking information)
01. Flags: rw-
02. Segment file offset: 28032 bytes
03. Virtual Address: 0x206d80
04. Physical Address: 0x206d80
05. Segment size in file: 560 bytes
06. Segment size in memory: 560 bytes
07. Segment Alignment: 0x8
---------------------------------------------
Entry 03: 
00. Type: NOTE (Auxillary Information)
01. Flags: r--
02. Segment file offset: 456 bytes
03. Virtual Address: 0x1c8
04. Physical Address: 0x1c8
05. Segment size in file: 68 bytes
06. Segment size in memory: 68 bytes
07. Segment Alignment: 0x4
---------------------------------------------
Entry 04: 
00. Type: GNU_EH_FRAME (GCC .eh_frame_hdr segment)
01. Flags: r--
02. Segment file offset: 23248 bytes
03. Virtual Address: 0x5ad0
04. Physical Address: 0x5ad0
05. Segment size in file: 556 bytes
06. Segment size in memory: 556 bytes
07. Segment Alignment: 0x4
---------------------------------------------
Entry 05: 
00. Type: GNU_STACK (Indicates stack executability)
01. Flags: rw-
02. Segment file offset: 0 bytes
03. Virtual Address: 0x0
04. Physical Address: 0x0
05. Segment size in file: 0 bytes
06. Segment size in memory: 0 bytes
07. Segment Alignment: 0x10
---------------------------------------------
Entry 06: 
00. Type: GNU_RELRO (Read-only after relocation)
01. Flags: r--
02. Segment file offset: 28008 bytes
03. Virtual Address: 0x206d68
04. Physical Address: 0x206d68
05. Segment size in file: 664 bytes
06. Segment size in memory: 664 bytes
07. Segment Alignment: 0x1
---------------------------------------------
```

See, this doesn't have a ```PHDR```. It is strange.

In the manpage, there is a statement:

> Moreover, it may occur only if the program header table is part of the memory image of the program.

It is not present in ```librt.so```. Does this mean its PHT is not part of of the memory image?

We discussed that the very reason PHT is present is to define the memory layout of that particular ELF file. But here, there is a twist.

Note that we don't necessarily need ```PHDR``` segment to process PHT. All the necessary info to process it is present in the ELF header.

But this is strange. Our analysis is missing something.

Coming to dumping of ```PHDR``` segment. The PHT is the segment. We can just dump PHT when the programmer requests to dump the segment related to ```PHDR```. We already have a function ```elfp_pht_dump()``` to dump the complete PHT. I need you to add it as a case.

The ```switch()``` statement in ```elfp_seg_dump()``` now has one valid ```case```.

```c
        /* Now, let us start */
        switch(enc_seg_type)
        {
                case PT_PHDR:
                        ret = elfp_pht_dump(handle);
                        if(ret == -1)
                        {       
                                elfp_err_warn("elfp_seg64_dump",
                                                "elfp_pht_dump() failed");
                                return 0;
                        }
                        break;
                        
                default:
                        elfp_err_warn("elfp_seg64_dump",  
                                        "Still have to write parse code");
                        return -1;
        }
```

Let us move to the next segment type.

## 3. INTERP

Manpage first.

```
                 PT_INTERP   The array element specifies the location and size of a null-terminated pathname to invoke as an inter‐
                             preter.  This segment type is meaningful only for executable files (though it  may  occur  for  shared
                             objects).   However  it may not occur more than once in a file.  If it is present, it must precede any
                             loadable segment entry.
```

In simple words, it is a string which is essentially the path of the **interpreter**.

Let us take a look at ```hello```'s ```INTERP``` Program Header.

```
$ ./elfparse ./hello
.
.
.
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
```

From this we know where this string is present. It is present at a file-offset of **568 bytes**. Let us open up ```hello``` in a hexeditor and take a look at it.

```
00000230  01 00 00 00  00 00 00 00   2F 6C 69 62  36 34 2F 6C       ......../lib64/l
00000240  64 2D 6C 69  6E 75 78 2D   78 38 36 2D  36 34 2E 73       d-linux-x86-64.s
00000250  6F 2E 32 00  04 00 00 00   10 00 00 00  01 00 00 00       o.2.............
```

568 bytes translates to **0x238**. So, the string is **/lib64/ld-linux-x86-64.so.2**. Let us check it out.

```
$ /lib64/ld-linux-x86-64.so.2 
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

And that is the **interpreter** for you. It is called by different names. It is called **Dynamic Linker**, **Loader** because it does all these jobs.

Understanding what the Interpreter does can in itself be a separate series of articles. It does a lot of things. 

It also has a manpage, which is crazy full of information. It is literally a gold mine. Checkout ```man ld.so```. If you want to understand the Interpreter in detail, you may read [this article series](/reverse/engineering/and/binary/exploitation/series/2019/11/10/understanding-the-loader-part1-how-does-an-executable-get-loaded-to-memory.html).

In short, you can think about the Interpreter like this. The Interpreter is this very caring parent to a baby (any process we run). It does everything to make sure that the process runs seemlessly. It identifies the libraries the program depends on and maps it to memory. Once the environment for program is setup, control is transfered to the process. Interpreter's job doesn't end here.  When the program calls a library function, that function is linked at runtime by none other than the Interpreter. That is a jist of what the interpreter does.

Now, let us dump it.

It is a string. So, dumping it is a very easy job.

```c
void
elfp_seg_dump_interp(void **ptr_arr, unsigned long int ptr_count)
{
        int i;
        for(i = 0; i < ptr_count; i++)
        {
                printf("The interpreter requested by this executable: %s\n", (char *)ptr_arr[i]);
        }
}
```

Normally, there is only ```INTERP``` segment if present. We should be able to handle malformed ELF files too.

Add that function to ```elfp_seg64_dump()```'s ```switch()``` statement.

Let us build the library, write a very simple application which simply dumps any given ELF file's interpreter.

Let us build and install the library. For this, you'll need to add ```elfp_seg.c``` to the Makefile, because it is a new sourcefile.

```
$ make install
make build
make[1]: Entering directory '/home/dell/Documents/projects/write-your-own-XXXX/ELF-Parser/src'
# Building the library
gcc elfp_int.c elfp_basic_api.c elfp_ehdr.c elfp_phdr.c elfp_seg.c -c -fPIC -fstack-protector-all -O2
gcc elfp_int.o elfp_basic_api.o elfp_ehdr.o elfp_phdr.o elfp_seg.o -shared -fstack-protector-all -O2 -o libelfp.so
mkdir build
mv libelfp.so *.o build
make[1]: Leaving directory '/home/dell/Documents/projects/write-your-own-XXXX/ELF-Parser/src'
sudo cp build/libelfp.so /usr/lib/x86_64-linux-gnu
sudo mkdir /usr/include/elfp
sudo cp ./include/elfp.h /usr/include/elfp
```

The library is set. Let us write the application.

```c
$ cat dump_interp.c 
#include <stdio.h>
#include <elfp/elfp.h>

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

	/* Open up the ELF file for processing */
	ret = elfp_open(path);
	if(ret == -1)
	{
		fprintf(stderr, "Unable to open file using libelfp.\nExiting..\n");
		elfp_fini();
		return -1;
	}

	fd = ret;
	
	/* Let us dump the INTERP segment */
	ret = elfp_seg_dump(fd, "INTERP");
	if(ret == -1)
	{
		fprintf(stderr, "elfp_seg_dump() failed\n");
		elfp_fini();
		return -1;
	}

	/* Close this file */
	elfp_close(fd);

	/* De-init the library */
	elfp_fini();

	return 0;
}
```

It is a very simple application. Let us compile it.

```
$ gcc dump_interp.c -o dump_interp -lelfp
```

Let us start our experimentation. Let us try it on itself.

```
$ ./dump_interp ./dump_interp
The interpreter requested by this executable: /lib64/ld-linux-x86-64.so.2
```

Let us check a 32-bit executable. Compile ```hello``` to get a 32-bit executable.

```
$ gcc hello.c -o hello_32 -m32
$
```

Now the dump.

```
$ ./dump_interp ./hello_32
The interpreter requested by this executable: /lib/ld-linux.so.2
```

Verify this by opening it up with an editor.

The manpage tells that this segment is meaningful only for executable objects. So, ideally it should not be present in Shared Libraries.

Let us checkout ```libc.so```.

```
$ ./dump_interp /lib/x86_64-linux-gnu/libc.so.6 
The interpreter requested by this executable: /lib64/ld-linux-x86-64.so.2
```

It has an interpreter. It might be an executable. Let us try running it.

```
$ /lib/x86_64-linux-gnu/libc.so.6 
GNU C Library (Ubuntu GLIBC 2.27-3ubuntu1) stable release version 2.27.
Copyright (C) 2018 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.
There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.
Compiled by GNU CC version 7.3.0.
libc ABIs: UNIQUE IFUNC
For bug reporting instructions, please see:
<https://bugs.launchpad.net/ubuntu/+source/glibc/+bugs>.
```

It is infact an executable.

Let us try it on some random shared library.

```
$ ./dump_interp /usr/lib/x86_64-linux-gnu/librt.so 
elfp_seg64_get: No segments of the requested type are present
elfp_seg64_dump: elfp_seg64_get() failed
elfp_seg_dump: elfp_seg64_dump() failed
elfp_seg_dump() failed
```

It actually doesn't have an ```INTERP``` segment. You can verify it by dumping its PHT.

So, we now have a dump function for ```INTERP``` segment.

## 4. GNU_STACK

Let us see what elf's manpage has to say.

```
                 PT_GNU_STACK
                             GNU extension which is used by the Linux kernel to control the state of the stack via the flags set in
                             the p_flags member.
```

This is a very interesting segment type.

First question is, why do we need to convey the **state of the stack**?

Stack is a place for data and some control variables like Return Address, Frame Pointer. To satisfy this, it is enough if stack has read-write permissions. There is no question for executability.

After reading a bunch of old articles online, got to know that in the **absence of this Program Header, stack is made executable** - [read this](http://refspecs.linuxbase.org/LSB_3.0.0/LSB-PDA/LSB-PDA/progheader.html). So, if we need the stack to be read-write only, we **must** have this Program Header.

So, the default configuration is an executable stack. I want to verify this.

This is the plan. Let us change the ```PT_GNU_STACK``` header to a ```PT_NULL``` header using the hexeditor. Because ```PT_NULL``` is symbolic of an unused Program Header entry, it is ignored. Let us do it.

**1.** Find where the Program Header.

```
$ ./elfparse ./hello
.
.
.
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
.
.
```

This is the 8th Program Header. PHT starts from the 64th byte and size of each Program Header is 56 bytes.

So, file offset of ```PT_GNU_STACK``` Program Header is (64 + 56 * 7) = **456 bytes**. Note that this may be different for your ELF file.

The first member of ```Elf64_Phdr``` structure is ```p_type```, which is a 4-byte member. 

This is ```PT_GNU_STACK``` which is actually the following.

```c
#define PT_GNU_STACK    0x6474e551      /* Indicates stack executability */
```

We need to change **0x6474e551** to **0x00000000** which is ```PT_NULL```.

It is currently like this:

```
000001C0  04 00 00 00  00 00 00 00   51 E5 74 64  06 00 00 00                ........Q.td....
```

Look at bytes 9-12. It is present in little-endian form. It is actually **64-74-E5-51** which is ```PT_GNU_STACK```. Let us change it to **00-00-00-00**.

```
000001C0  04 00 00 00  00 00 00 00   00 00 00 00  06 00 00 00               ................
```

Save and run it.

```
$ ./hello
Hello!
$
```

It ran properly, so there were no other problems.

Now, let us check its stack permissions. Open it up in gdb, break at ```main()``` and run. When it breaks, we'll take a look at its ```/proc/PID/maps``` file.

Let us run it using gdb.

```
$ gdb -q hello
Reading symbols from hello...(no debugging symbols found)...done.
gdb-peda$ b main
Breakpoint 1 at 0x63e
gdb-peda$ run
Starting program: /home/dell/Documents/pwnthebox/exp/hello
.
.
Breakpoint 1, 0x000055555555463e in main ()
gdb-peda$ 
```

Let us get its PID.

```
gdb-peda$ getpid
5610
```

Check ```/proc/5610/maps``` file.

```
$ cat /proc/5610/maps
555555554000-555555555000 r-xp 00000000 08:05 7209364                    /home/dell/Documents/pwnthebox/exp/hello
555555754000-555555755000 r-xp 00000000 08:05 7209364                    /home/dell/Documents/pwnthebox/exp/hello
555555755000-555555756000 rwxp 00001000 08:05 7209364                    /home/dell/Documents/pwnthebox/exp/hello
7ffff79e4000-7ffff7bcb000 r-xp 00000000 08:05 13112024                   /lib/x86_64-linux-gnu/libc-2.27.so
7ffff7bcb000-7ffff7dcb000 ---p 001e7000 08:05 13112024                   /lib/x86_64-linux-gnu/libc-2.27.so
7ffff7dcb000-7ffff7dcf000 r-xp 001e7000 08:05 13112024                   /lib/x86_64-linux-gnu/libc-2.27.so
7ffff7dcf000-7ffff7dd1000 rwxp 001eb000 08:05 13112024                   /lib/x86_64-linux-gnu/libc-2.27.so
7ffff7dd1000-7ffff7dd5000 rwxp 00000000 00:00 0 
7ffff7dd5000-7ffff7dfc000 r-xp 00000000 08:05 13111996                   /lib/x86_64-linux-gnu/ld-2.27.so
7ffff7fd7000-7ffff7fd9000 rwxp 00000000 00:00 0 
7ffff7ff7000-7ffff7ffa000 r--p 00000000 00:00 0                          [vvar]
7ffff7ffa000-7ffff7ffc000 r-xp 00000000 00:00 0                          [vdso]
7ffff7ffc000-7ffff7ffd000 r-xp 00027000 08:05 13111996                   /lib/x86_64-linux-gnu/ld-2.27.so
7ffff7ffd000-7ffff7ffe000 rwxp 00028000 08:05 13111996                   /lib/x86_64-linux-gnu/ld-2.27.so
7ffff7ffe000-7ffff7fff000 rwxp 00000000 00:00 0 
7ffffffde000-7ffffffff000 rwxp 00000000 00:00 0                          [stack]
ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]
```

As expected!!

The stack is executable. So, we have verified it.

You can also see that if you make the flags ```rwx``` instead of ```rw-```, the stack becomes executable.

I wanted to know if a reason existed for stack executability being an option(apart from experimentation).

I found [this](https://www.win.tue.nl/~aeb/linux/hh/protection.html) webpage. I stumbled upon some crazy stuff. There is actually a legitimate reason. Let us explore that.

Consider the following program.

```c
$ cat tramp.c 
#include <stdio.h>

int main()
{
	int x = 10;

	int addx(int a)
	{
		return (a+x);
	}
	
	int y = addx(23);
	printf("y = %d\n", y);

	return 0;
}
```

I didn't know we could define a function inside another function. C is really crazy!

Compile and run it. It runs just fine.

```
$ gcc tramp.c -o tramp
$ ./tramp 
y = 33
```

This is called **nesting** of functions - one function nested in another. And like any other local variable, this nested function is local to the function it is defined in.

Let us take a look at its ```GNU_STACK``` Program Header.

```
$ ./elfparse ./tramp
.
.
.
Entry 07: 
00. Type: GNU_STACK (Indicates stack executability)
01. Flags: rw-
02. Segment file offset: 0 bytes
03. Virtual Address: 0x0
04. Physical Address: 0x0
05. Segment size in file: 0 bytes
06. Segment size in memory: 0 bytes
07. Segment Alignment: 0x10
.
.
```

As expected, the stack is non-executable.

Let us consider another program.

```c
$ cat tramp2.c 
#include <stdio.h>

int main()
{
	int x = 10;

	int addx(int a)
	{
		return (a+x);
	}
	
	int (*fptr)(int) = addx;

	int y = fptr(23);
	printf("y = %d\n", y);

	return 0;
}
```

Let us compile it, but with a flag. We'll talk about that flag in a bit.

```
$ gcc tramp2.c -o tramp2 -ftrampolines
```

Let us check its ```GNU_STACK``` Program Header.

```
$ ./elfparse ./tramp2
.
.
.
Entry 07: 
00. Type: GNU_STACK (Indicates stack executability)
01. Flags: rwx
02. Segment file offset: 0 bytes
03. Virtual Address: 0x0
04. Physical Address: 0x0
05. Segment size in file: 0 bytes
06. Segment size in memory: 0 bytes
07. Segment Alignment: 0x10
.
.
```

Damn! It is executable.

Try compiling **tramp.c** with ```-ftrampolines``` flag. It's stack will still remain non-executable.

So, what does **tramp2.c** have which makes its stack executable when that flag is used to compile?

Take a look at **tramp.c** and **tramp2.c**. There is a small difference.

* A function pointer to the local-nested function is defined.
* That function pointer is used to call the local-nested function instead of its name itself.

Calling functions indirectly using function pointers is very common. This type of code is present everywhere. But this is a bit different. It is a **function pointer to a local-nested function**. Note that the stack still remains non-executable when the exact same thing is done, but the local function is not local and is defined outside.

So, what is the deal with **function pointer to a nested function** and the ```trampolines``` flag? Why is the stack made executable in this case?

Only reason to make it executable is to run some code which is present there. Let us verify this.

Let us run the program and check if there is a call to some code in stack. Let us look out for ```call```s, ```jmp```s or any similar instruction.

```
$ gdb -q tramp2
Reading symbols from tramp2...(no debugging symbols found)...done.
gdb-peda$ b main
Breakpoint 1 at 0x6c5
gdb-peda$ run
Starting program: /home/dell/Documents/pwnthebox/exp/tramp2 
.
.
.
```

Looking at its disassembly, there are only 3 ```call``` instructions and 1 ```je``` instruction. 2 calls are to ```printf``` and ```__stack_chk_fail``` - both are ```libc``` functions.

The only call left is the call to the nested function. The following is the assembly code.

```
   0x0000555555554725 <+100>:	mov    edi,0x17
   0x000055555555472a <+105>:	call   rax
   0x000055555555472c <+107>:	mov    DWORD PTR [rbp-0x3c],eax
```
* **0x17** is 23. That is the only argument. It is loaded into ```edi``` - as per System V ABI.
* Then the ```call``` is made.

Let us break at this call and inspect the address to which it'll jump after the call. The following is the state of execution just before ```call rax``` is executed.

```
[----------------------------------registers-----------------------------------]
RAX: 0x7fffffffdce4 --> 0x5555555546aabb49 
RBX: 0x0 
RCX: 0x5555555546aa (<addx.2251>:	push   rbp)
RDX: 0x7fffffffdce0 --> 0x46aabb490000000a 
RSI: 0x7fffffffddf8 --> 0x7fffffffe159 ("/home/dell/Documents/pwnthebox/exp/tramp2")
RDI: 0x17 
RBP: 0x7fffffffdd10 --> 0x555555554760 (<__libc_csu_init>:	push   r15)
RSP: 0x7fffffffdcd0 --> 0x1 
RIP: 0x55555555472a (<main+105>:	call   rax)
R8 : 0x7ffff7dd0d80 --> 0x0 
R9 : 0x7ffff7dd0d80 --> 0x0 
R10: 0x2 
R11: 0x3 
R12: 0x5555555545a0 (<_start>:	xor    ebp,ebp)
R13: 0x7fffffffddf0 --> 0x1 
R14: 0x0 
R15: 0x0
EFLAGS: 0x206 (carry PARITY adjust zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x55555555471d <main+92>:	mov    QWORD PTR [rbp-0x38],rax
   0x555555554721 <main+96>:	mov    rax,QWORD PTR [rbp-0x38]
   0x555555554725 <main+100>:	mov    edi,0x17
=> 0x55555555472a <main+105>:	call   rax
   0x55555555472c <main+107>:	mov    DWORD PTR [rbp-0x3c],eax
   0x55555555472f <main+110>:	mov    eax,DWORD PTR [rbp-0x3c]
   0x555555554732 <main+113>:	mov    esi,eax
   0x555555554734 <main+115>:	lea    rdi,[rip+0xa9]        # 0x5555555547e4
Guessed arguments:
arg[0]: 0x17 
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffdcd0 --> 0x1 
0008| 0x7fffffffdcd8 --> 0x7fffffffdce4 --> 0x5555555546aabb49 
0016| 0x7fffffffdce0 --> 0x46aabb490000000a 
0024| 0x7fffffffdce8 --> 0xba49000055555555 
0032| 0x7fffffffdcf0 --> 0x7fffffffdce0 --> 0x46aabb490000000a 
0040| 0x7fffffffdcf8 --> 0x555590e3ff49 
0048| 0x7fffffffdd00 --> 0x7fffffffdd20 --> 0x1 
0056| 0x7fffffffdd08 --> 0x76e9f43fd236700 
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x000055555555472a in main ()
gdb-peda$ 

```

* ```rax``` holds the value **0x7fffffffdce4**. It is pointing to some wierd value **0x5555555546aabb49**. Let us check where this value is present in the memory layout.

```
gdb-peda$ find 0x5555555546aabb49
Searching for '0x5555555546aabb49' in: None ranges
Found 1 results, display max 1 items:
[stack] : 0x7fffffffdce4 --> 0x5555555546aabb49 
```

That is it. Got it!

Let us see what code is present at that stack address.

```
gdb-peda$ x/10i 0x7fffffffdce4 
   0x7fffffffdce4:	movabs r11,0x5555555546aa
   0x7fffffffdcee:	movabs r10,0x7fffffffdce0
   0x7fffffffdcf8:	rex.WB jmp r11
   0x7fffffffdcfb:	nop
   0x7fffffffdcfc:	push   rbp
   0x7fffffffdcfd:	push   rbp
   0x7fffffffdcfe:	add    BYTE PTR [rax],al
   0x7fffffffdd00:	and    ch,bl
   0x7fffffffdd02:	(bad)  
```

First instruction is ```movabs r11,0x5555555546aa```. What is **0x5555555546aa**? Take a look at disassembly of the nested function.

```
00000000000006aa <addx.2251>:
 6aa:   55                      push   rbp                  
 6ab:   48 89 e5                mov    rbp,rsp
 6ae:   89 7d fc                mov    DWORD PTR [rbp-0x4],edi
 6b1:   4c 89 d0                mov    rax,r10
 6b4:   4c 89 55 f0             mov    QWORD PTR [rbp-0x10],r10
 6b8:   8b 10                   mov    edx,DWORD PTR [rax]
 6ba:   8b 45 fc                mov    eax,DWORD PTR [rbp-0x4]
 6bd:   01 d0                   add    eax,edx
 6bf:   5d                      pop    rbp
 6c0:   c3                      ret 
```

**0x5555555546aa** = **File-offset of nested function** + **0x555555554000**.

So, **0x5555555546aa** is certainly the nested function's address.

Let us step into its execution.

```
   0x7fffffffdcee:	movabs r10,0x7fffffffdce0
=> 0x7fffffffdcf8:	rex.WB jmp r11
   0x7fffffffdcfb:	nop
   0x7fffffffdcfc:	push   rbp
   0x7fffffffdcfd:	push   rbp
   0x7fffffffdcfe:	add    BYTE PTR [rax],al

```

This instruction is wierd. It says ```jmp r11``` and we know that ```r11``` register has our local-nested function's address. So, we should now essentially jump to our **local-nested function**. But, what is that ```rex.WB```? Let us check it out.

The [osdev wikipage](https://wiki.osdev.org/X86-64_Instruction_Encoding#REX_prefix) confirms that this is a valid instruction.

```
A REX prefix must be encoded when:

* using 64-bit operand size and the instruction does not default to 64-bit operand size; or
* using one of the extended registers (R8 to R15, XMM8 to XMM15, YMM8 to YMM15, CR8 to CR15 and DR8 to DR15); or
* using one of the uniform byte registers SPL, BPL, SIL or DIL. 
```

The second point clears things off. So, this is according to the Intel ISA.

Let us run this instruction and jump to our **local-nested function**. Now we are here.

```
[-------------------------------------code-------------------------------------]
   0x5555555546a1 <frame_dummy+1>:	mov    rbp,rsp
   0x5555555546a4 <frame_dummy+4>:	pop    rbp
   0x5555555546a5 <frame_dummy+5>:	jmp    0x555555554610 <register_tm_clones>
=> 0x5555555546aa <addx.2251>:	push   rbp
   0x5555555546ab <addx.2251+1>:	mov    rbp,rsp
   0x5555555546ae <addx.2251+4>:	mov    DWORD PTR [rbp-0x4],edi
   0x5555555546b1 <addx.2251+7>:	mov    rax,r10
   0x5555555546b4 <addx.2251+10>:	mov    QWORD PTR [rbp-0x10],r10
```

From here, it is pretty straight forward. This function gets executed and it returns back to ```main()```.

We now know why we needed executable stack. There was some code present there.

But we still haven't found the answer to our main question: What is the link between using function pointer to call local function and the trampolines option?

Let us see what GCC itself has to [say](https://gcc.gnu.org/onlinedocs/gccint/Trampolines.html).

> GCC has traditionally supported nested functions by creating an executable trampoline at run time when the address of a nested function is taken. This is a small piece of code which normally resides on the stack, in the stack frame of the containing function. The trampoline loads the static chain register and then jumps to the real address of the nested function.

The official name for that code present in stack is called **trampoline**. I realize why it is called trampoline. Trampoline is that rubber sheet you can jump on. You jump from a height and jump back to (say) some other height.

In a similar manner, We start with ```main()```, go to trampoline code and then jump to our local-nested function.

In normal cases, ```main()``` directly calls our **local-nested function**. But in this case, the following is happening.

```
                                  0x00000x5555555546aa: addx.2251
                                      |
    0x00005555555546c1: main          |
                |                     |
                |                     |
                |                    /|\
                | (1)                 |(3)
               \|/                    |
                |                     |
                |                     |
                |       (2)           |          
            -------------->---------------
            | Trampoline: 0x7fffffffdce4 |
            ------------------------------

```

The piece from GCC tells that the trampoline code is present in the caller's stackframe. Let us check it out.

The following is code from ```main()```'s disassembly.

```
 6c1:   55                      push   rbp
 6c2:   48 89 e5                mov    rbp,rsp
 6c5:   48 83 ec 40             sub    rsp,0x40
 6c9:   64 48 8b 04 25 28 00    mov    rax,QWORD PTR fs:0x28
 6d0:   00 00 
 6d2:   48 89 45 f8             mov    QWORD PTR [rbp-0x8],rax
 6d6:   31 c0                   xor    eax,eax
 6d8:   48 8d 45 10             lea    rax,[rbp+0x10]
 6dc:   48 89 45 f0             mov    QWORD PTR [rbp-0x10],rax
 6e0:   48 8d 45 d0             lea    rax,[rbp-0x30]
 6e4:   48 83 c0 04             add    rax,0x4
 6e8:   48 8d 55 d0             lea    rdx,[rbp-0x30]
 6ec:   66 c7 00 49 bb          mov    WORD PTR [rax],0xbb49
 6f1:   48 8d 0d b2 ff ff ff    lea    rcx,[rip+0xffffffffffffffb2]        # 6aa <addx.2251>
 6f8:   48 89 48 02             mov    QWORD PTR [rax+0x2],rcx
 6fc:   66 c7 40 0a 49 ba       mov    WORD PTR [rax+0xa],0xba49
 702:   48 89 50 0c             mov    QWORD PTR [rax+0xc],rdx
 706:   c7 40 14 49 ff e3 90    mov    DWORD PTR [rax+0x14],0x90e3ff49
 70d:   b8 0a 00 00 00          mov    eax,0xa
 712:   89 45 d0                mov    DWORD PTR [rbp-0x30],eax
 715:   48 8d 45 d0             lea    rax,[rbp-0x30]
 719:   48 83 c0 04             add    rax,0x4
 71d:   48 89 45 c8             mov    QWORD PTR [rbp-0x38],rax
 721:   48 8b 45 c8             mov    rax,QWORD PTR [rbp-0x38]
 725:   bf 17 00 00 00          mov    edi,0x17
 72a:   ff d0                   call   rax
.
.
```

The ```sub rsp, 0x40``` instruction suggests that the stackframe is 64(0x40) bytes in size.

```
        rsp---->|               |
                |               |
                |               |
                |               |
                |               |
                |               |
                |               |
        rbp---->|               |
```

The following instructions,

```
 6e0:   48 8d 45 d0             lea    rax,[rbp-0x30]
 6e4:   48 83 c0 04             add    rax,0x4
 6e8:   48 8d 55 d0             lea    rdx,[rbp-0x30]
 6ec:   66 c7 00 49 bb          mov    WORD PTR [rax],0xbb49
```

changes the stack into this.

```
(rbp-x40)rsp--->|                       |
                |                       |
    (rbp-0x30)->|            bb 49      |
                |                       |
                |                       |
                |                       |
                |                       |
        rbp---->|                       |
```

Next up, there are instructions which puts the local-nested function's address onto stack.

```
 6f1:   48 8d 0d b2 ff ff ff    lea    rcx,[rip+0xffffffffffffffb2]        # 6aa <addx.2251>
 6f8:   48 89 48 02             mov    QWORD PTR [rax+0x2],rcx
```

Our local-nested function's address is ```0x00005555555546aa```. After the above 2 instructions are executed, this is what the stack looks like.

```
(rbp-x40)rsp--->|                       |
                |                       |
    (rbp-0x30)->|            bb 49 aa 46|
                |55 55 55 55 00 00      |
                |                       |
                |                       |
                |                       |
        rbp---->|                       |
```

If you read through the assembly code till ```call rax```, you'll see that **direct machine code** was placed in the stack.

Although we are getting more clarity, we still haven't answered the question of why we need this trampoline code when a function pointer is used to call the local-nested function. I'll update the article once I figure out the answer for this.

That was one crazy reason for having an executable stack.

There is also a reason for **not** having an executable stack - its a security risk. An executable stack along with a buffer overflow vulnerability is the best think that can happen to an attacker. If you want to understand more about this, you can read [my series](/reverse/engineering/and/binary/exploitation/series/2019/03/25/reverse-engineering-and-binary-exploitation-series-mainpage.html) on buffer overflows, exploitation, defence measures by OS, breaking those defence measures and more!

Coming back to ```GNU_STACK```, we need to write a get and a dump function. But this Program Header actually doesn't represent any segment in file. It simply conveys stack permissions using the ```p_flags``` member. 

This is an exception for our get function. Here, the get function should return the Program Header's ```p_flags``` member because that is the most important info. Dump function should take that ```p_flags``` and process it to dump the same in human-readable form. 

We'll add an exception case to ```elfp_seg32_get()``` and ```elfp_seg64_get()```. Take a look at the following change in ```elfp_seg64_get()```.

```c
                        /* If it is GNU_STACK, then p_flags is to be sent back
                         * to the caller.*/
                        if(ph->p_type == PT_GNU_STACK)
                        {
                                ptr_arr[count] = (void *)(ph->p_flags);
                                count++;
                        }
                        else
                        {
                                ptr_arr[count] = (void *)(start_addr + ph->p_offset);
                                count++;
                        }

```

We just had the ```else``` case before. Here, we are simply sending the flags back, instead of segment addresses. We need to add this to ```elfp_seg_get()```'s description.

Let us write ```elfp_seg_dump_gnu_stack()```, which dumps the stack permissions.

```c
void
elfp_seg_dump_gnu_stack(void **ptr_arr, unsigned long int ptr_count)
{
        int i;
        unsigned int flags;

        for(i = 0; i < ptr_count; i++)
        {
                printf("Stack permissions: %s\n", elfp_phdr_decode_flags);
        }
}
```

As simple as that.

Add this ```case``` into that switch case present in ```elfp_seg64_dump()``` and ```elfp_seg32_dump()```.

With that, we have successfully completed dumping ```GNU_STACK```.

Let us write a simple application like ```dump_interp```, which will dump the stack permissions. We need to make a call to ```elfp_seg_dump(fd, "GNU_STACK")``` instead of ```elfp_seg_dump(fd, "INTERP")```.

Let us try it out on ```tramp``` and ```tramp2```.

```
$ ./dump_gnu_stack tramp
Stack permissions: rw-
$
$ ./dump_gnu_stack tramp2
Stack permissions: rwx
```

## 5. Conclusion

We explored 3 interesting segment types - ```PHDR```, ```INTERP``` and ```GNU_STACK```. 

The ```INTERP``` and ```GNU_STACK``` are 2 crazy segment types. Interpreter is one beast of a software. I actually started exploring the Interpreter and stopped in the middle to write this series, because to clearly understand what the Interpreter is doing, I had to clearly understand the ELF clearly.

Stack executability is one more fantastic topic to explore. [This series](/reverse/engineering/and/binary/exploitation/series/2019/03/25/reverse-engineering-and-binary-exploitation-series-mainpage.html) will introduce you to Buffer overflows, stack executability, how it makes the system unsecure.

```dump_interp.c``` and ```dump_gnu_stack.c``` are put in the **examples** directory.

You can find all the code written so far [here](https://github.com/write-your-own-XXXX/ELF-Parser/releases/tag/Part9).

With that, we'll end this article.

In the next article, we'll explore one more interesting segment type, ```PT_NOTE```.

I had a lot of fun researching and writing this article. I hope you also had fun and learnt something out of it.

Thank you for reading!

------------------------------------------------------------------------
[Go to next article: Writing an ELF Parsing Library - Part10 - NOTE segment type](/404.html)         
[Go to previous article: Writing an ELF Parsing Library - Part8 - Program Header Table](/write/your/own/xxxx/2019/12/09/writing-an-elf-parsing-library-part8-program-header-table.html)