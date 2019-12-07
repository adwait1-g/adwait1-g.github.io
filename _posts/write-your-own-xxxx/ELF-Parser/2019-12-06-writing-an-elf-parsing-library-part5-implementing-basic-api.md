---
title: Writing an ELF Parsing Library - Part5 - Implementing basic API
categories: write your own XXXX
layout: post
comments: true
---

Hello Friend!

In the [third article](/write/your/own/xxxx/2019/12/02/writing-an-elf-parsing-library-part3-internal-data-structures-1.html), we decided on 4 basic API functions which will be exposed to programmers.

It is important that you have gone through previous 2 articles([1](/write/your/own/xxxx/2019/12/02/writing-an-elf-parsing-library-part3-internal-data-structures-1.html), [2](/write/your/own/xxxx/2019/12/05/writing-an-elf-parsing-library-part4-internal-data-structures-2.html)) to understand this article.

We'll implement those 4 API functions in this article.

## 0. Introduction

The following are the API functions.

**1.** ```elfp_init()```: Initializes the library. Makes it usable.
**2.** ```elfp_open()```: This function can be used to open an ELF file for parsing.
**3.** ```elfp_close()```: Closes an ELF file. Should be called once its processing is done.
**4.** ```elfp_fini()```: De-inits the library. Frees up all the resources being used by the library.

We implemented the 2 core data structures in the last articles. With that in mind, we'll implement these 4 functions.

Create a new file ```elfp_basic_api.c``` in ```src``` directory. We'll put all the definitions there.

Lets get started!

## 1. elfp_init(): Initializes the library

This function makes the library usable.

First let us think what all initialization is needed.

The main data structure of the library is ```main_vec```, an instance of ```elfp_main_vector```. This data structure stores references to all active ```elfp_main``` objects.

For this to happen, the vector should be allocated some memory. And this can happen through its initialization.

The following is the declaration.

```c
/*
 * elfp_init: Initializes the library. 
 *      * MUST be called before any other library functions are called.
 *      
 * @return: 0 on success, -1 on failure.
 */
int 
elfp_init();
```

Implementation is simple. Init the main vector and come out.

```c
int
elfp_init()
{
        int ret;
                                                                  
        /* Initialize main_vec */                                 
        ret = elfp_main_vec_init();                               
        if(ret == -1)                                             
        {                                                         
                elfp_err_warn("elfp_init", "elfp_main_vec_init() failed");
                return -1;
        }
        
        return 0;
}
```

Put the implementation in ```src/elfp_basic_api.c```.

With that, we are ready to implement our second function ```elfp_open()```.

## 2. elfp_open(): Opens an ELF file for processing

This function does a bunch of things.

It needs to create the ```elfp_main``` object. Then the object should be added to ```main_vec```. Then it has to return the ```handle``` to the user.

It takes in ```file_path``` as argument.

```c
/*
 * elfp_open: Opens the specfied ELF file and returns a handle.
 *
 * @arg0: Path / name of ELF File
 *
 * @return: A non-negative integer - handler on success.
 *              (-1) on failure.
 */
int
elfp_open(const char *elfp_elf_path);
```

Let us implement it.

**1.** Basic check.

```c
int
elfp_open(const char *elfp_elf_path)
{
        /* Basic check */
        if(elfp_elf_path == NULL)
        {
                elfp_err_warn("elfp_open", "NULL argument passed");
                return -1;
        }
```

**2.** Creating an ```elfp_main``` object for the give file.

```c
        /* Create the elfp_main object */
        main = elfp_main_create(elfp_elf_path);
        if(main == NULL)
        {
                elfp_err_warn("elfp_open", "elfp_main_create() failed");
                return -1;
        }
```

**3.** Now, we need to add it to the main vector.

```c
        /* Once created, it needs to be added to main_vec */
        ret = elfp_main_vec_add(main);
        if(ret == -1)
        {
                elfp_err_warn("elfp_open", "elfp_main_vec_add() failed");
                return -1;
        }

        handle = ret;
```

We should get the user handle from ```elfp_main_vec_add()

**4.** Update the ```elfp_main``` object with its handle.

```c
        /* Update the handle */
        elfp_main_update_handle(main, handle);
```

At this point, the library should be able to handle further parse requests.

**5.** Let us return the handle to the user.

```c
        return handle;
}
```

With that, we have implemented our second function.

## 3. elfp_close(): Closing a file after processing

Once the programmer is done processing a file, he can free up the resources the library used to process the file - so that it can be used elsewhere.

The only way the programmer identifies a file is through the ```handle```. So, the programmer passes the handle to ```elfp_close()``` and we need to take care of the rest.


```c
/*
 * elfp_close: Closes everything about the specified handle.
 *
 * @arg0: User handle obtained from an elfp_open call.
 * 
 * @return: 0 on success, -1 on failure.
 */
int
elfp_close(int user_handle);
```

We need to free up all resources related to that file - basically the ```elfp_main``` object associated with it. We need to de-init it.

All we have is the handle. But we need the corresponding ```elfp_main``` object.

At the moment, we don't have any ```elfp_main_vec``` function to do the job for us. So, we'll write one - ```elfp_main_vec_get_em()```.

```c
/*
 * elfp_main_vec_get_em: Returns the elfp_main object corresponding to 
 *      a given user handle.
 *
 * @arg0: User handle, an integer.
 *
 * @return: Reference to an elfp_main object.
 */

elfp_main*
elfp_main_vec_get_em(int handle);
```

It is a very simple function. Just returning the object.

```c
elfp_main*
elfp_main_vec_get_em(int handle)
{ 
        return main_vec.vec[handle];
}
```

Because these are related to internal data structures, the declaration and definition should go into ```src/include/elfp_int.h``` and ```src/elfp_int.c``` respectively.

Let us come back to ```elfp_close()```'s implementation.

Once we have gotten the ```elfp_main``` object, we need to de-init it. That is the implementation.

**1.** Get the ```elfp_main``` object.

```c
int
elfp_close(int handle)
{
        elfp_main *main = NULL;
        int ret;

        /* Get the elfp_main object corresponding to the handle */
        main = elfp_main_vec_get_em(handle);
```

**2.** Check if it has been freed before

```c
        /* If it has already been freed, then its cool! */
        if(main == NULL)
                return 0;
```
* If it has already been de-inited, then no need to call ```elfp_main_fini()``` on it. Let us simply return success.

**3.** De-init it and return.

```c
        /* Else, let us free it now */
        ret = elfp_main_fini(main);
        if(ret == -1)
        {
                elfp_err_warn("elfp_close", "elfp_main_fini() failed");
                return -1;
        }

        /* All good */
        return 0;
}
```

```elfp_close()```'s implementation is complete.

## 4. elfp_fini(): De-inits the library

Once the programmer is done with our library, its best to release all the resources being used by the library, so that it can be put to use elsewhere.

This is facilitated by ```elfp_fini()``` function. Its declaration goes like this.

```c
/*
 * elfp_fini: Cleans up everything and deinits the library.
 */
void
elfp_fini();
```

What all should be released?

Resources allotted to every active file must be released - basically de-init every active ```elfp_main``` object. In the end, free up the vector. 

All this is already being done by ```elfp_main_vec_fini()```. It needs to be called.

Implmentation.

```c
void
elfp_fini()
{       
        elfp_main_vec_fini();
}
```

We have completed the 4-API implementation.

## 5. Do you see a problem in elfp_close()?

Can you take a closer look at ```elfp_close()```'s implementation and see if the implementation works correctly?

Consider the following scenario.

```c
handle1 = elfp_open("file1.elf");
handle2 = elfp_open("file2.elf");

/* After processing file1.elf, programmer realizes that he doesn't need file2.elf. So, he tries to close it */

elfp_close(handle2);
```

Consider a case where ```elfp_open()``` returned an error on opening **file2.elf**. So, ```handle2``` is essentially **-1**.

Obviously, the programmer didn't check for errors and confidently tried to close it.

How will our ```elfp_close()``` function handle this case? Let us walk through the code.

**1.** Get the corresponding ```elfp_main``` object.

```c
        /* Get the elfp_main object corresponding to the handle */
        main = elfp_main_vec_get_em(handle);
```
* ```elfp_main_vec_get_em()``` simply returns ```main_vec.vec[handle]```. What happens now?

Essentially, ```main_vec.vec[-1]``` is being requested.

For the computer, this is simple pointer arithmetic and nothing more.

If ```main_vec.vec```'s address is **0x1000**. So, the vector looks like this.

```
0x1000 -> <ptr1> <ptr2> <ptr3> <ptr4> ....
```

Each ```ptrX``` is 8 bytes long(in a 64-bit machine).

Address of ```ptr1``` = 0x1000
Address of ```ptr2``` = 0x1008
Address of ```ptr3``` = 0x1010
.
.

When we try to fetch ```main_vec.vec[-1]```, We are trying to access the ```elfp_main pointer``` at address **0x1000 - 8** = **0xff8**.

This is memory which was not allocated to us. So, this is a classic case of **Illegal Memory Access**.

This is definitely a problem.

Let us continue our analysis and see where it can lead us to.

What can be present at the address **0xff8**? Arguably anything. Suppose some integer **0x1234** is present.

Our library **thinks** this is a valid address, an address pointing to an ```elfp_main``` object. At this point, ```main = 0x1234```.

**2.** Next step is to free the resources.

```c
        /* Else, let us free it now */
        ret = elfp_main_fini(main);
        if(ret == -1)
        {
                elfp_err_warn("elfp_close", "elfp_main_fini() failed");
                return -1;
        }
```

* ```elfp_main_fini()``` dereferences this pointer. When this happens, our program **crashes**. Because **0x1234** is mostly an invalid address. Unhandled runtime errors are not good!

If it is filled with **0**s instead of **0x1234**, we are saved because there is a check for **NULL** in ```elfp_close()```.

If it a valid address, we may end up changing some other objects.

What do we do to prevent this?

In the [second article](/write/your/own/xxxx/2019/11/15/writing-an-elf-parsing-library-part2-piloting-the-library.html), we discussed a concept called **Input Sanitization**. Basically, not trusting an user input and checking its validity.

Let us write a function which will sanitize the ```handle``` passed by the programmer. It should allow further processing only if it a valid handle. If it is some invalid value, we return an error.

At this point, we need a definition for **Invalid handle**. What handle value is considered invalid?

We'll make a list.

1. From the structure of ```main_vec```, we know that handle cannot be a negative integer. 0 is the first valid handle.

2. Any integer greater than ```main_vec.latest``` is invalid. There can be atmost ```main_vec.latest``` number of active files.

3. If an file has been ```elfp_close()```d, then its descriptor is invalid.

The following is its declaration.

```c
/*
 * elfp_sanitize_handle: Sanitizes the user fed handle.
 * 
 * @arg0: User handle
 * 
 * @return: 0 if the user handle is valid. -1 if user handle is invalid.
 */
int
elfp_sanitize_handle(int handle);
```

Implementation.

**1.** Basic range check.

```c
int
elfp_sanitize_handle(int handle)
{
        /* Basic boundary checks */                 
        if(handle < 0 || handle >= main_vec.latest)
        {
                elfp_err_warn("elfp_sanitize_handle", "Invalid Handle passed");
                return -1;
        }
```

**2.** Check if this handle has been closed before or not.

```c
        elfp_main *main = NULL;
        /* Now we know that the handle is in the valid range.
         * Let us see if it has been closed before */
        main = elfp_main_vec_get_em(handle);
        if(main == NULL)
        {
                elfp_err_warn("elfp_sanitize_handle", "Handle already closed");
                return -1;
        }
```

**3.** Let us return.

```c
        return 0;
}
```

With that, we have our sanitization function. Put these into ```elfp_int.h``` and ```elfp_int.c``` respectively.

Add the ```elfp_sanitize_handle()``` in ```elfp_close()```.

We have now successfully completed implementing the 4 basic API functions.

## 6. Testing our implementation

I want you to write C programs to test our implementation, make sure it is functioning as intended. Check for memory leaks using valgrind.

Check out [check_basic_api.c](https://github.com/write-your-own-XXXX/ELF-Parser/blob/master/examples/check_basic_api.c).

## 7. Conclusion

We have come to the end of this article.

I hope you have an idea of where we are going.

At this point, we have the internal data structures functioning properly, we have API for programmers. You can find all the code written so far [here](https://github.com/write-your-own-XXXX/ELF-Parser/releases/tag/Part5).


Now, we need to start working on the **Core of the library - the ELF parsing part**.

We'll be focusing on different components in an ELF file. In each article, let us take one ELF component, understand it properly and then write parse functions to dump it in human readable form.

We'll start with the ELF Header in the next article.

That is it for now.

Thank you for reading!

------------------------------------------------------
[Go to next article: Writing an ELF Parsing Library - Part6 - The ELF Header](/write/your/own/xxxx/2019/12/07/writing-an-elf-parsing-library-part6-the-elf-header.html)                     
[Go to previous article: Writing an ELF Parsing Library - Part4 - Internal Data Structures - 2](/write/your/own/xxxx/2019/12/05/writing-an-elf-parsing-library-part4-internal-data-structures-2.html)
