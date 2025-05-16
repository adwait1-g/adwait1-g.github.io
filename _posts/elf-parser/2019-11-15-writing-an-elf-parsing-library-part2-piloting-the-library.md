---
title: Writing an ELF Parsing Library - Part2 - Piloting the Library
layout: post
categories: elfparser
comments: true
---

Hello Friend!

In the [previous article](/write/your/own/xxxx/2019/11/15/writing-an-elf-parsing-library-part1-what-is-elf.html), we discussed the ELF.

We'll take a small detour and talk about what it means to write a library, how it should look like. Once we are done with that, we'll start writing it.

I am writing this article with zero experience in writing libraries. It has mostly been reading other libraries' code, using other libraries and going through header files to understand how the user-API looks like.

## 0. What does writing a library mean?

Writing a library means that the programmer can use our library to build his own customized tools, the way he wants.

We need to provide a clean, easy to use API(**Application Programming Interface**) using which the programmer can write his programs(Applications). The API is basically set of functions, data structures.

As we write the library, we'll also write a ELF-Parser using our library.

Let us take an example.

Refering to our hello example in the [previous article](/write/your/own/xxxx/2019/11/15/writing-an-elf-parsing-library-part1-what-is-elf.html). Let us take a look at the libraries it is dependent on.

```
$ ldd hello
	linux-vdso.so.1 =>  (0x00007ffc8bffa000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007ff92a0d7000)
	/lib64/ld-linux-x86-64.so.2 (0x00007ff92a4a1000)
```
* We'll build a library similar to ```libc.so.6```. We'll have a ```libelfp.so``` which has everything. The way there are multiple header files a programmer refer to, to use libc, we'll also have a header file with details about all the API, data structures exposed to the programmer.

## 1. How should the API look like?

The API needs to be simple to use. Simple, intuitive functions for the user. The library needs to do all the heavy-lifting and give the desired output.

Let us start with a simple example.

**1.** This is an ELF parsing library. It means, we need to pass the file name of the ELF to be parsed to the library. We can define a function like this.

```c
char *filepath = "./a.out";     /* This can be any ELF file */
lib_path(filepath);
```

**2.** We encountered something called the ```ELF Header```, which is always the first thing to be present in any ELF file. Now, the programmer wants to dump its contents in human readable form. The function to dump it may look like this.

```c
lib_dump_elf_header();
```

**3.** This API works if there is only one ELF file. What if the programmer wants to analyze multiple ELF files in his program? He might do something like this with the above API.

```c
lib_path(filepath1);
lib_dump_elf_header(); /* First file's ELF Header dumped */

lib_path(filepath2);
lib_dump_elf_header(); /* Second file'e ELF Header dumped */
```
* What if the user wants to print say the ```Program Header Table``` of ELF file1? He'll have to run ```lib_path(filepath1)``` again. This is uncomfortable and dirty.

* We can have unique descriptors for each ELF file the programmer wishes to open. It is like having a unique **file descriptor** for every file you open.

```c
int des = lib_path("./a.out");
lib_dump_elf_header(des);
```

* This way, any number of files can be opened and parsed.

**4.** Suppose the programmer doesn't like our dump function, he should have the freedom to write his own dump function. How do we make that happen?

For this to happen, we need to parse the ELF Header and store the parsed information in another structure. This structure should be exposed to the programmer. How will the API look like now?

```c
int des = lib_path("./a.out");
parsed_elf_header *pelf_hdr = lib_get_elf_header(des);
```
* Here, we need to define the ```parsed_elf_header``` structure, its members clearly so that the programmer can refer to it and write his function.

As we make the library more easy and flexible to use, our work as library writers increases. It totally depends on you where you want to draw the line. If you are interested in writing a good library, and you have the time, then I suggest you write a crazy one!

That was a glimpse of how our API would look like.

## 2. Thoughts on errors and handling them

### a. Considering all cases

Everything we discussed above was about the **happy path**. The user passes a valid ELF file, our library parses it and dumps information.

* This may not be the case always. It can go wrong in various ways.
	* The file may not be passed at all. The user may pass ```NULL``` for "fun". If we dereference it without checking, the program crashes - NULL Pointer dereferencing.
	* Even if it is a non-NULL string, the file may not exist.
	* Even it it exists, it may not be an ELF file.
	* Even if it an ELF file, its internal bytes may be corrupted, say the ELF Header has some trash.
	* Inside the file, anything might be wrong.
	* If EVERYTHING goes right, **only** then the ```lib_dump_elf_header``` will dump the ELF Header info in human readable form.

* We are just talking about taking a **file** as input to the library. Things can get pretty complex once we start parsing it.

* I hope you understand these cases. There are way more cases than just one happy path case. I had read somewhere that an **erroneous path** for **us** is just one another case for the program. Same applies for the happy path. It is just one case that the program should handle. So, if we don't write code to cover that case, we'll end up crashing the program. We need to write proper code to handle every case we know of. For me, this is a very important aspect of systems programming. Quoting some crazy programmer, "Take care of all the cases you know of. If there is a case you haven't taken care of, pray that the program crashes as soon as possible".

* [This article](http://250bpm.com/blog:140) talks about doing Rigorous Error Handling. I think this article is valuable. We'll be taking inputs from this article.

### b. Carelessness, Input Sanitisation, Vulnerabilities

I want to take a more realistic example.

* Suppose there is an internal library error and ```lib_path``` is programmed to return a ```-1``` on error.

```
int des = lib_path("./a.out");	/* For some reason, this function failed */
lib_dump_elf_header(des);	/* Oops! */
```

* The user doesn't handle it properly. He simply passed ```-1``` to ```lib_dump_elf_header```. I think this is a very common mistake we all make. We use ```malloc```, but don't check if it returned ```NULL``` or an actual address. We take it for granted that it always succeeds.

* How should our library handle it? Consider we have written ```lib_dump_elf_header``` in the following manner. 

```c
Elf64_Ehdr *ehdr = vector_of_elf_headers[des];
dump_elf_header(ehdr);
```

* We are maintaining an array of ELF Headers - each header belonging to an open file.

* In this case, ```des``` is ```-1```. So, the following is happening.

```
ehdr = vector_of_elf_headers[-1];
```

* This won't give an error. C is a very generous language. That actually means, 

```
vector_of_elf_headers-> [Header0] [Header1] [Header2] [Header3]...
```
* There is no header(-1), but for the program, it is simple pointer arithmetic. So, it'll do the following and return some address.
```
ehdr = vector_of_elf_headers - sizeof(Elf64_Ehdr)
```
* Now, we have accessed memory that doesn't belong to this vector. Our dump function goes ahead and parses whatever is present there and gives it to the user. Do you see what just happened? The user unknowingly **saw** what he was not supposed to see, something that doesn't belong to him. It exposes whatever is present out there. No doubt, this is a bug. This may not seem too much because this is just a file format parser. But consider the same thing happens in a root-owned program. The attacker might try to **expose** sensitive info which is not supposed to happen. So, a bug can escalate into a vulnerability depending on the context!

* The programmer didn't check for an error and it ended up in a **memory expose**.

**How to take care of this scenario?**

1. From programmer's perspective, he should have handled it properly. How would he know what ```lib_path``` would return on success, on error? We need to have proper documentation for that.
	* We need to give a **header file** with details of all the API functions, data structures etc., we would be exposing to the programmer, for him to use.
	* We should make it very clear there how to use a particular function, what a particular member of a structure means.
	* I personally loved [capstone](http://www.capstone-engine.org/)'s header file. It is so damn detailed, I am not sure how a programmer can make mistakes!
	* If you want to know something in Linux, what would you do? you try refering its manual page. We'll make it a point to write a proper manpage - like elf's and document everything clearly there.

2. Every after all this, the programmer fucks up. Now, it is on the library to handle it in the right manner.
	* The library should always take caution while processing any **input** given to it. It should **sanitise** the input before processing it. So, we'll have strict input sanitization procedures to make sure something like this doesn't happen. Search for **Input sanitization** and see how severe it can get if it is not done properly.

Most deadly vulnerabilities arise in file-parsers. Just search for **parser vulnerabilities** and have fun :P .


### c. Cleaning up is damn important

At some point in time, we all have made the mistake of **not freeing** the **malloc**d memory. We just want the program to work right?! We don't care about all that. The OS will anyway clean up when the program terminates.

The severity of any such programming mistake depends the context.

* Suppose the programmer wrote a very simple elf-parser using our library. Then it may not matter, although there are no guarantees.

* Suppose the programmer is writing some big application, of which our library is one small part. Suppose he opened 1000 files using our library. Consider our library **malloc**s 5000 bytes for each file - to store all the metadata. So, our library has used up a heap space of 1000 * 5000 = 5MB. Suppose the programmer is done processing the first 500 files and will never use it again (But note that they are still in memory). The programmer opens 500 new files for processing. Unfortunately, ```lib_path``` fails because of insufficient memory.

This is sad isn't it? The programmer was anyway not using the first 500 files. Logically, that memory could be used to process toe new 500 files. But that didn't happen. If only we had given a **clean-up** function which frees up the specified memory.

Something like ```lib_close(descriptor)```. This will close the case of that file and make room for any new file.

Before the program exits, we need to clean-up everything and leave gracefully.


With that, we'll end our short discussion on how our library will look like, API etc.,

## 3. How to initialize and manage data structures?

Consider a data structure as the following: 

```c
struct 
{
	void **addrs;
	unsigned long int n_addrs;
	unsigned long int size;
} to_be_freed_list;

struct to_be_freed_list free_us;
```
During the course of a program, a lot of new objects are created, lot of memory is allocated from heap using ```malloc``` / ```calloc```. At the end, we need to ```free``` up all this before leaving.

How do we do this? We use this vector of addresses to be freed. In the end, we'll iterate through the list and free every chunk of memory in one go.

What are the various operations on this structure?. 

1. It needs some initialization, we need to allocate some memory for ```addrs``` so that it actually stores some addresses. Also need to set ```n_addrs``` to ```0```.
2. Adding an address to this list is an operation.
3. The core of this data structure - freeing all that memory, another operation. And finally freeing memory allocated for ```addrs``` itself.

It is always better to define functions for each of these operations, instead of writing the code again and again.

**1.** ```free_list_init()```: This function initializes the structure ```free_us```.

```c
int
free_list_init()
{	
	/* Length of this vector is inited to 1000 */
	free_us.size = 1000;
	
	/* Allocate memory */
	free_us.addrs = calloc(free_us.size, sizeof(void *));
	if(free_us.addrs == NULL)
		return -1;
	
	/* Init this to 0 */
	free_us.n_addrs = 0;

	return 0;
}
```

**2.** ```free_list_fini()```: Deinitializes the structure.

```c
void
free_list_fini()
{
	/* Free the memory chunks first */
	for(unsigned i = 0; i < free_us.n_addrs; i++)
		free(free_us.addrs[i]);
	
	/* Free the array now */
	free(addrs);
	
	return;
}
```

**3.** ```add_addr_to_list(void *addr)```: Adds the specified address to the list.

```c
int
add_addr_to_list(void *addr)
{
	/* Check if the address is NULL */
	if(addr == NULL)
		return -1;
	
	void *new_addr = NULL;

	/* Maximum length of vector is free_us.size now. Check
	 * if we have reached the limit */
	if(free_us.n_addrs == free_us.size) /* Yes! */
	{	
		/* Double the vector size */
		new_addr = realloc(free_us.addrs, free_us.size * 2);
		if(new_addr == NULL)
			return -1;

		/* Read realloc's manpage to understand the following */
		for(int i = free_us.size; i < free_us.size * 2; i++)
			new_addr[i] = NULL;

		free_us.addrs = new_addr;

		free_us.size = free_us.size * 2;
	}

	/* Now, we can add peacefully */
	free_us.addrs[free_us.n_addrs] = addr;
	free_us.n_addrs += 1;

	return 0;
}
```

So, we have 3 functions for this data structure: ```free_list_init```, ```free_list_fini```, ```add_addr_to_list```. We can use these function to manipulate that data structure. Suppose we need to add an address to the list and we don't have the add function, we'll have to write that code again and again. Code becomes very dirty and chances of making mistakes are high. Instead, use a cleanly written function.

From now on, any data structure we define, it'll come with a set of functions, present specifically to interact with them - initialization, deinitialization, any operation relevant to that data structure.

## 4. Initializing every file in the library's sourcecode

Every file in the library's sourcecode, be it a C sourcefile or a header file, should have the following.

1. Filename
2. Description
3. License

Header files should have the conditional compilation check which makes sure it is included once.

## 5. What are our library's features?

We need to be clear on what our library does - its features.

This is what I have planned for this series.

1. Will parse only 64-bit ELF Format. As we progress, you'll see that 32-bit and 64-bit structures are different.
2. The programmer should be able to open **as many** files he wants at once.
3. The programmer should have the freedom to choose between using an in-built dump function for a particular structure and writing his own dump function. So, I'll be defining a proper structure which the user can use to write it.
4. Write support for **ALL** structures that are part of ELF. The sole goal of writing the library is to understand ELF better.

With that, we'll start designing and coding the library.

Some specifications about the library.

1. I want to name the library **elfp**, short form for **elf-parser**. Feel free to name your library anything you want.

2. Once we install the library in a machine, the header file ```elfp.h``` will have **everything** that a programmer needs to use our library.

3. Our directory structure would be simple.
```
$ tree ELF-Parser/
ELF-Parser/
|
|---> README.md: This README is the face of the library.
|
|---> src: All sourcecode lies here.
			|
			|---> src1.c
			|---> src2.c
			|---> src3.c
			.
			.
			include: This directory will have all the header files.
|
|---> examples: Has examples programs which uses the library
|
|---> Makefile: Helps in buiding, installing the library.
```

4. Name of every function / structure exposed to the user should start with ```elfp``` - ```elfp_dump_elf_header```, ```elfp_close``` etc., This avoid any namespace collisions. More importantly, you'll get a "feel" of writing a proper library :P


## 6. Conclusion

I hope you now have an idea of what a library is, thing we need to consider while writing one, how our library might look like.

Without further ado, we'll start writing code in the next article.

Thank you for reading!

------------------------------------------------------------

[Go to next post: Writing an ELF Parsing Library - Part3 - Internal Data Strucutures - 1](/write/your/own/xxxx/2019/12/02/writing-an-elf-parsing-library-part3-internal-data-structures-1.html)                    
[Go to previous post: Writing an ELF Parsing Library - Part1 - What is ELF?](/write/your/own/xxxx/2019/11/15/writing-an-elf-parsing-library-part1-what-is-elf.html)                    
