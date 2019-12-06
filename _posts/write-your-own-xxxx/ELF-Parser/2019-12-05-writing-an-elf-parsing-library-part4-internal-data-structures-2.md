---
title: Writing an ELF Parsing Library - Part4 - Internal Data Structures - 2
categories: write your own XXXX
layout: post
comments: true
---

Hello Friend!

In the [previous article](/write/your/own/xxxx/2019/12/02/writing-an-elf-parsing-library-part3-internal-data-structures-1.html), we discussed a few basic API we want to expose to the programmer, defined 2 important data structures ```elfp_main``` and ```elfp_main_vector```.

In this article, we'll be writing functions to manage these 2 data structures.

## 0. elfp_main: Per-file data structure

```elfp_main``` is a structure which has all the data related to an open ELF file. Let us take a look at it.

```c
#define ELFP_FILEPATH_SIZE 256

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

What all functions do we need?

1. When a new file is passed to ```elfp_open()```, a new ```elfp_main``` object should be created. So, a ```create()``` function is necessary.
2. Once the processing is done, we need clean up everything related to it. So, a ```fini()``` function is necessary.


Lets get to work!

### a. elfp_main_create(): Creating a new elfp_main object for a given file

Whenever we have to write a ```create()``` function for an object, we have 2 ways to do it.

1. The ```create()``` function can allocate memory and return a reference to an empty object. The caller can do the hard work of populating its members - ```fd```, ```path```, ```start_addr```, ```file_size```, ```handle```.

2. The ```create()``` function can take the ```file_path``` as argument and it can do the hardwork of populating its members.

I can see 1 advantage of the second approach over first. We won't have to write ```update()``` functions for every member because the ```create()``` will be updating it. We'll need update functions when a function other than the data structure's set of functions tries to manipulate its values. 

Let us go with the second approach. ```elfp_main_create()``` will be taking ```file path``` as argument.

```c
/*
 * elfp_main_create: Creates a new elfp_main object and returns a
 *      reference to it.
 * 
 * @arg0: File path - A NULL terminated string. 
 *
 * @return: NULL on failure, Reference to an empty elfp_main object on success.
 */
elfp_main*
elfp_main_create(const char *file_path);
```

Now comes the interesting part, the implementation.

What all does the create function have to do? It basically has to allocate memory for a new ```elfp_main``` object and populate its members.

**1.** Basic check

```c
elfp_main*
elfp_main_create(const char *file_path)
{
        /* Basic check */
        if(file_path == NULL)
        {
                elfp_err_warn("elfp_main_create", "NULL argument passed");
                return NULL;
        }
```

**2.** The following are the variables we need.

```c
        int ret;
        elfp_main *main = NULL;
        struct stat st;
        unsigned char magic[4] = {'\0', '\0', '\0', '\0'};
        void *start_addr = NULL;
```
* You'll know where each variable is used as we proceed.


**3.** Allocate memory for the object

```c
        /* Allocate memory */
        main = calloc(1, sizeof(elfp_main));
        if(main == NULL)
        {
                elfp_err_warn("elfp_main_create", "calloc() failed");
                return NULL;
        }
```

We now have memory for the object. There are 6 members:
1. ```file descriptor``` of the ELF file
2. ```file size```
3. ```start address``` of the file's memory map.
4. ```path```
5. ```handle``` - which is given to the user
6. The ```free_vector``` - used to store **to-be-freed** addresses.

**4.** Updating the ```file descriptor```.

Before we ```open()``` up the file, we need to know if it exists, if we have the read permissions. We can check that using the ```access()``` system call.

```c
        /* Check if we can read the file or not */
        ret = access(file_path, R_OK);
        if(ret == -1)
        {
                elfp_err_warn("elfp_main_create", "access() failed");
                elfp_err_warn("elfp_main_create", "File doesn't exist / No read permissions");
                goto return_free;
        }
```

* The ```R_OK``` is a flag to check if we have read permissions. 

* By doing this, we'll come to know if we are even allowed to process this file. If we don't have the permissions(or file doesn't exist), we'll ```free()``` the memory allocated for the ```elfp_main``` object and return ```NULL```. The ```return_free``` label does the same.

```c
return_free:
        free(main);
        return NULL;
```

If we have the permissions,lets ```open()``` the file.

```c
        /* Open the file */
        ret = open(file_path, O_RDONLY);
        if(ret == -1)
        {
                elfp_err_warn("elfp_main_create", "open() failed");
                goto return_free;
        }
        /* Update the file descriptor */
        main->fd = ret;
```
* We just need to read the file and nothing else. So, we'll open it in ```O_RDONLY``` mode.
* ```open()``` on success returns the ```file descriptor``` to that file. Let us update our ```elfp_main``` object.

**5.** Checking if the file is ELF or not.

The user/programmer can pass any file. We need to check if the file passed is an ELF file or not.

The way to do it is to check it's **magic characters**. 

> The first 4 characters of ANY ELF file is 0x7f, E, L, F. In pure ascii, they are 0x7f, 0x45, 0x4c, 0x46.

If the file's first 4 characters don't match ELF's magic characters, then we clean up and return.

```c
        /*
         * 2. Check if the file is ELF or not.
         */
        ret = read(main->fd, magic, 4);
        if(ret != 4)
        {
                elfp_err_warn("elfp_main_create", "read() failed");
                goto return_close;
        }

        if(strcmp(magic, ELFMAG) != 0)
        {
                elfp_err_warn("elfp_main_create", 
                "Not an ELF file according to the magic characters");
                goto return_close;
        }
```

* First ```read()``` the first 4 characters into a buffer and compare them with ```ELFMAG```.

* The label ```return_close``` does the same.

```c
return_close:
        close(main->fd);

return_free:
        free(main);
        return NULL;
```

If it is an ELF file, we'll move forward.

**6.** Updating the file size

At first, I didn't know any method to find a file's size.

I was thinking, I'll start with the first byte and go till I encounter an ```EOF```(End-Of-File) byte(ascii value = 0x4). But then the problem is an ELF file is a binary file. It can have the ascii value **0x4** even inside the file. So, this method doesn't work.

There is a command called ```size``` which will print the number of characters in a file, lines, words. I thought I can take that output and parse it to get only the number of characters - which is the file size. This is a hack and I was not happy with it.

After a lot of time, I found out that there is a function to do that. There is a class of functions which will fetch you the ```status``` of a specified file. Let us look at its manpage.

```
ELF-Parser/src$ man 2 stat
STAT(2)                                  Linux Programmer's Manual                                 STAT(2)

NAME
       stat, fstat, lstat, fstatat - get file status

SYNOPSIS
       #include <sys/types.h>
       #include <sys/stat.h>
       #include <unistd.h>

       int stat(const char *pathname, struct stat *statbuf);
       int fstat(int fd, struct stat *statbuf);
       int lstat(const char *pathname, struct stat *statbuf);
```

* There are multiple functions. We'll use the second function ```fstat``` because we already have the file opened.

* ```fstat``` takes in 2 arguments. First is the open file descriptor. Second is a reference to an empty ```struct stat``` object. You can read the man page to know the structure's members. One of its members is file size. 

* You can look at the variables used. There is a ```struct stat st``` declared there, which we will use here.

```c
        /*
         * 3. File size
         */
        ret = fstat(main->fd, &st);
        if(ret == -1)
        {
                elfp_err_warn("elfp_main_create", "fstat() failed");
                goto return_close;
        }
        /* Update size */
        main->file_size = st.st_size;
```

**7.** The path

```c
        /*
         * 4. Update path
         */
        strncpy(main->path, file_path, ELFP_FILEPATH_SIZE);
```

**8.** Mapping the file to the process's address space

Finally, we are at a stage where we can map the ELF file into the process's address space. I am specifically telling that it is mapped into the **process's address space** and NOT **process's memory** for a reason.

```mmap()``` works in the following manner. When I request the OS to map certain file using ```mmap()```, it allocates a part of the process's address space for that file. If the file size is (say) 4096 bytes, it'll give the address range (say) **0x1234 - 0x2234** to the mapped file.

Does this mean the file is **copied** onto memory? Not really. It is never copied into memory in the first place.

Suppose I do the following. What happens?

```c
Elf64_Ehdr *ehdr = (Elf64_Ehdr *)main->start_addr;
printf("Entry Address: 0x%lx\n", ehdr->e_entry);
```
Here, I am accessing the ```e_entry``` member. If the file is not in memory, how do we get access to it?

This is what happens. When we try to access some part of the file, a **page fault** is generated and that **page** which has the piece of file we requested for is loaded into memory(RAM).

Now, let us map it.

```c
        /*
         * 5. Update start address
         */
        start_addr = mmap(NULL, main->file_size, PROT_READ, MAP_PRIVATE,
                                        main->fd, 0);
        if(start_addr == MAP_FAILED)
        {
                elfp_err_warn("elfp_main_create", "mmap() failed");
                goto return_close;
        }
        main->start_addr = (unsigned char *)start_addr;
```

With that, we are done updating 4 file related members.

**9.** Initializing the free_vector.

```elfp_main``` object has an instance of ```elfp_free_addr_vector``` in it. While processing the ELF file, many new objects may be created through ```malloc```/```calloc``` which we have to clean up later. We use this free_vector to make note of all these addresses. We have written the ```init``` function for it in the previous article. Let us use it.

```c
        /* 
         * 6. Initialize the free list *
         */
        ret = elfp_free_addr_vector_init(&main->free_vec);
        if(ret != 0)
        {
                elfp_err_warn("elfp_main_create",
                                "elfp_free_addr_vector_init() failed");

                goto return_munmap;
        }
```

* In case if this fails, we have to clean-up everything.

```c
return_munmap:
        munmap(main->start_addr, main->file_size);

return_close:
        close(main->fd);

return_free:
        free(main);
        return NULL;
}
```

The only member left is the ```handle```. Who generates this integer? If the programmer opens up 2 files, how do we(library) decide the descriptor for each of those open files? 

Certainly, the ```elfp_main_create()``` function cannot do it. We are yet to build a mechanism which will make the descriptor thing work.

```create()``` function won't be updating ```handle```. An external function will be updating it. We'll need an ```update()``` function for ```handle```.

If everything goes well, ```elfp_main_create()``` will return back the reference to the ```elfp_main``` object it worked on.

```c
        
        return main;
```

With that, we are done with ```elfp_main_create()```. Who can use this function? ```elfp_open()``` can use this. When the programmer passes a file path to the library through ```elfp_open()```, ```elfp_open()``` can call ```elfp_main_create()``` and create an ```elfp_main``` object. We'll implement ```elfp_open()``` in the next article.

We'll write the ```update()``` for ```handle``` member.

### b. elfp_main_update_handle(): Update the user handle

We saw that ```create()``` is not capable of deciding the ```handle```. So, an external function needs to find the handle and update it. To do that, we'll write an update function. The following is its declaration.

```c
/*
 * elfp_main_update_handle: Updates 'handle' of elfp_main object.
 *
 * @arg0: Reference to an elfp_main object.
 * @arg1: An integer which is this file's unique descriptor.
 *
 * @return: 0 on success, -1 on failure.
 */
int
elfp_main_update_handle(elfp_main *main, int handle);
```

Its implementation is simple. Just update the handle.

```c
int
elfp_main_update_handle(elfp_main *main, int handle)
{
        if(main == NULL || handle < 0)
        {
                elfp_err_warn("elfp_main_update_handle", "Invalid argument(s) passed");
                return -1;
        }

        main->handle = handle;

        return 0;
}
```

Finally, we have to write the ```fini``` function, which will free up everything.

### c. elfp_main_fini(): Clean up everything related to an elfp_main object

This function is the exact opposite of the ```create()``` function. What was opened there should be closed here. What was allocated there should be freed here. What was mapped there should be unmapped here.

The declaration is straight forward.

```c
/*
 * elfp_main_fini: Cleans up everything related to a given elfp_main object.
 *
 * @arg0: Reference to an elfp_main object
 *
 * @return: 0 on success, -1 on failure.
 */
int
elfp_main_fini(elfp_main *main);
```

Implementation is simple.

**1.** Basic check

```c
int
elfp_main_fini(elfp_main *main)
{
        /* Basic check */
        if(main == NULL)
        {
                elfp_err_warn("elfp_main_fini", "NULL argument passed");
                return -1;
        }
```

**2.** Unmap the mapped region.

```c
        /* unmap the file */
        munmap(main->start_addr, main->file_size);
```

**3.** Close the file

```c
        /* Close the file */
        close(main->fd);
```

**4.** De-init the free vector.

```c
        /* De-init the free vector */
        elfp_free_addr_vector_fini(&main->free_vec);
```

**5.** Free up the ```elfp_main``` object itself. And we are good to go!

```c
        /* Now that we have cleaned up everything inside the object,
         * it is time to clean the object itself */
        free(main);

        return 0;
}
```

We are done with ```elfp_main_fini```. Note that this function can be used by ```elfp_close()``` to clean up everything related to a particular file.

With that, we have successfully implemented the functions required to manage ```elfp_main``` structure.

Now, let us hop on to our next data structure ```elfp_main_vector```, the one which is responsible for supporting multiple files.

## 1. elfp_main_vector: Support for multiple files

The functioning of the library revolves around this data structure. Let us take a look at it.

```c
#define ELFP_MAIN_VECTOR_INIT_SIZE 1000

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

/* Newly added */
elfp_main_vector main_vec;
```

Note that there is only one instance of this structure for the entire library - ```main_vec```.

This is also a vector, similar to ```elfp_free_addr_vector```. So, we'll need 3 functions to manage it - ```init```, ```add``` and ```fini```.

### a. elfp_main_vec_init(): Initializes main_vec

Its declaration is simple.

```c
/*
 * elfp_main_vec_init: Initializes main_vec structure
 * 
 * @return: 0 on success, -1 on failure.
 */
int
elfp_main_vec_init();
```

What all should the ```init``` function do?

**1.** It needs to allocate memory to store pointers.

```c
int
elfp_main_vec_init()
{ 
        
        /* Update initial size */
        main_vec.total = ELFP_MAIN_VECTOR_INIT_SIZE;

        /* Allocate memory */
        main_vec.vec = calloc(main_vec.total, sizeof(elfp_main *)); 
        if(main_vec.vec == NULL)
        {
                elfp_err_warn("elfp_main_vec_init", "calloc() failed");
                elfp_err_warn("elfp_main_vec_init", "Fatal Error. Library cannot be used");
                return -1;
        }
```

**2.** Update ```latest```.

```c
        /* Initially, there is nothing */
        main_vec.latest = 0;

        return 0;
}
```

### b. elfp_main_vec_add(): Add an elfp_main reference to main_vec

This is a very important function. Whenever a new ```elfp_main``` object is created, it should be added to ```main_vec```. So, the function takes in one argument: Reference to an ```elfp_main``` object.


The ```elfp_main_create()``` was able to do everything except decide on a ```handle``` for that particular ELF file. We can use this main vector to implement a mechanism which will give us a unique handle for every open file. Let us see how it can be done.

Let us go over the data structure again. It has 3 members.

1. **vec**: The array of pointers, each pointer pointing to an ```elfp_main``` object.
2. **total**: The size of the vector - Total number of pointers it can hold.
3. **latest**: Number of ```elfp_main``` pointers present in the vector at the moment.

The vector's size is initialized to 1000. In the beginning, ```latest``` is 0. This means, there are ```0``` pointers stored in the beginning. When one pointer is added, ```latest``` should be incremented and it becomes ```1```.

So, an ```elfp_main``` reference can be added to this vector in the following manner.

```c
main_vec.vec[main_vec.latest] = some_elfp_main_obj;
main_vec.latest += 1;
```

The reference is put into the vector and ```latest``` is incremented.

What can act as a ```handle``` here? A ```handle``` is simply an integer which is unique for a given ```elfp_main``` object. **The index of this elfp_main reference in main_vec can be used as handle**.

```main_vec.vec[0]``` will fetch be some ```elfp_main``` object's reference. ```main_vec.vec[1]``` will fetch me reference of a different object.

The ```index``` is unique to that object. We'll write the ```add()``` function keeping this in mind.

The ```add()``` function should be able to return the ```handle``` to the ```elfp_main``` being passed to it. So, the following is its declaration.

```c
/*
 * elfp_main_vec_add: Adds an elfp_main reference to main_vec.
 *
 * @arg0: Reference to an elfp_main structure.
 *
 * @return: handle(a non-positive integer) on success,
 *              -1 on failure.
 */
int
elfp_main_vec_add(elfp_main *main);
```

The implementation is very similar to that of ```elfp_free_addr_vector_add()```, the ```add()``` function for the free vector. The only difference is, instead of returning ```0``` on success, this function will be returning the ```index``` of the passed ```elfp_main``` object in the main vector.

**1.** Basic check

```c
int
elfp_main_vec_add(elfp_main *main)
{
        /* Basic check */
        if(main == NULL)
        {
                elfp_err_warn("elfp_main_vec_add", "NULL argument passed");
                return -1;
        }
```

**2.**  These are the variables used.

```c

        void *new_addr = NULL;
        int handle;
```

**3.** Check if the vector is full. If it is, try allocating more memory and increase the vector length.

```c
        /* Check if the vector is full */
        if(main_vec.latest == main_vec.total)
        {
                /* Allocate more memory */       
                new_addr = realloc(main_vec.vec, 
                        (main_vec.total + ELFP_MAIN_VECTOR_INIT_SIZE) * sizeof(elfp_main *));
                
                if(new_addr == NULL)
                {
                        elfp_err_warn("elfp_main_vec_add", "realloc() failed");
                        return -1;
                }
                
                /* Zeroize the new memory */
                memset(((char *)new_addr) + main_vec.total * sizeof(elfp_main *), '\0',
                                ELFP_MAIN_VECTOR_INIT_SIZE * sizeof(elfp_main *));
                
                /* All set, change the members */
                main_vec.total = main_vec.total + ELFP_MAIN_VECTOR_INIT_SIZE;
                main_vec.vec = new_addr;
        }
```

Once this is done, the only thing left is to add the ```elfp_main``` reference to the vector.

**4.** Add it to the vector.

```c
        /* Add it */
        main_vec.vec[main_vec.latest] = main;
```

* Catch hold of the handle here. Note that ```main_vec.latest``` is the handle.

```c
        handle = main_vec.latest;
```

**5.** Update the ```latest```.

```c
        /* Then update it */
        main_vec.latest = main_vec.latest + 1;
```

**6.** Return the handle.

```c
        /* All good, we got the handle */
        return handle;
}
```

I hope you have understood how the ```index``` is the ```handle```.

### c. elfp_main_vec_fini(): Cleaning up the main vector

Cleaning up is simple.

Iterate through the vector and call ```elfp_main_fini()``` on each of pointers. Finally ```free()``` the memory allocated for the vector itself.

Before we implement this, I want you to consider the following scenario.

```c
fd1 = elfp_open("file1.elf");
fd2 = elfp_open("file2.elf");
fd3 = elfp_open("file3.elf");

/* Some processing happens */

elfp_close(fd2);

/* Some more processing happens on file1.elf and file3.elf */

elfp_fini();
```

The second file is closed using ```elfp_close()```. This internally uses ```elfp_main_fini()``` to clean up everything related to **file2.elf**'s ```elfp_main``` object.

Now, in the end ```elfp_fini()``` is called. This calls ```elfp_main_vec_fini()```, which plans on iterating through the vector and de-initing ALL ```elfp_main``` objects.

Initially, there were 3 objects: elfp_main1, elfp_main2, elfp_main3.
Later, the second was de-inited. So, now there are only elfp_main1, elfp_main3.

So, ideally ```elfp_main_vec_fini()``` should call ```elfp_main_fini()``` only on objects elfp_main1 and elfp_main3 and **NOT** on elfp_main2, because it is already freed. But how will it know?

How do we fix this problem?

To fix this, we'll need a small patch for ```elfp_main_fini()```. When it is de-initing a given ```elfp_main``` object, it should inform ```main_vec``` about it. So, we need a function to do the same.

Let us call that function ```elfp_main_vec_inform()```. It should take in the ```handle``` and inform ```main_vec``` that the ```elfp_main``` object associated with that handle is being de-inited.

How will it inform?

Simple solution. It can set the correponding pointer to NULL. We'll define a function which ```elfp_main_fini()``` can call to do that.

Here is the declaration.

```c
/*
 * elfp_main_vec_inform: Informs main_vec about de-initing of a    
 *      elfp_main object.
 * 
 * @arg0: Handle to that elfp_main object. 
 */
void
elfp_main_vec_inform(int handle);
```

Implementation.

```c
void
elfp_main_vec_inform(int handle)
{
        main_vec.vec[handle] = NULL;
}
```

It is as simple as that. So, when ```elfp_main_vec_fini()``` iterates through the vector, it should call ```elfp_main_fini()``` on only the non-NULL pointers.

We need to call ```elfp_main_vec_inform()``` from ```elfp_main_fini()```. Make sure you update its implementation.

Now that we are done with this patch, let us come back to ```elfp_main_vec_fini()```.

Here is the declaration.

```c
/*
 * elfp_main_vec_fini: Cleans up the main_vec.
 *      Should be called only if the library is about to be de-inited.
 */       
void
elfp_main_vec_fini();
```

The following is the implementation. It follows the discussion we had before.

**1.** Iterate through the vector and clean up all the active ```elfp_main``` objects.

```c
void
elfp_main_vec_fini()
{       
        unsigned long int i;  
    
        /* Iterate through the vector and free all the active objects */
        for(i = 0; i < main_vec.latest; i++)
        { 
                /* Thanks to our inform() function */
                if(main_vec.vec[i] != NULL)
                        elfp_main_fini(main_vec.vec[i]);
        }
```

**2.** Free up the vector.

```c
        /* Free up the vector itself */
        free(main_vec.vec);
        
        return;
}
```

With that, we have successfully completed the implementation of our second data structure.

## 2. Testing our implementation

I want you to write a few programs which will use these 2 data structures and make sure your implementation is correct, works without any memory leaks. You can use [valgrind](http://www.valgrind.org/) to check for memory leaks.

You can check out [check_elfp_main.c](https://github.com/write-your-own-XXXX/ELF-Parser/blob/master/examples/check_elfp_main.c) and [check_main_vec.c](https://github.com/write-your-own-XXXX/ELF-Parser/blob/master/examples/check_main_vec.c).

## 3. Conclusion

With that, we have come to the end of this article.

We discussed a lot of stuff in this article. We implemented 2 core data structures of our library. You can get the sourcecode [here](https://github.com/write-your-own-XXXX/ELF-Parser/releases/tag/Part4).

With this done, we are ready to implement the 4 basic API we discussed in the previous article. We'll do the same in the next article.

I hope you enjoyed this article.

Thank you for reading!

---------------------------------------------
[Go to next article: Writing an ELF Parsing Library - Part5 - Implementing basic API](/write/your/own/xxxx/2019/12/06/writing-an-elf-parsing-library-implementing-basic-api.html)          
[Go to previous article: Writing an ELF Parsing Library - Part3 - Internal Data Structures - 1](/write/your/own/xxxx/2019/12/02/writing-an-elf-parsing-library-part3-internal-data-structures-1.html)
