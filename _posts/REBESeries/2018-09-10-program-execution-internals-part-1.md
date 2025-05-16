---
layout: post
title: Program Execution Internals - Part1
categories: rebeseries
comments: true
---

Hello Fellow pwners!

In the previous post, we discussed what a process is and the memory layout of a running process. It gave a general picture of what types of variables are present in what part of memory.

In this post, we will go a little deep. We will take different C Coding constructs like **if** , **for** , **struct** etc., and see how they are implemented at the assembly level. Let us look at how memory is allocated for different types of variables and more.

To do this, we will use the famous Debugger - **gdb** (**GNU Debugger**) . A Debugger will help us **dissect** any program the way we want which help in understanding the program better. Along with gdb, we will use an add-on python script called **PEDA** (**Python Exploit Development Assistance**) . This script will help us use the GNU Debugger in convenient manner.

Also, create a directory named **post_5** in the **rev_eng_series** directory and store all the stuff we explore in the **post_5** directory.

## 1\. Installing gdb and peda:

1.  gdb is installed by default in any gnu/linux system. As we are using Ubuntu, it is already present.

2.  Installing peda:
    
        $ git clone https://github.com/longld/peda.git ~/peda 
        $ echo "source ~/peda/peda.py" >> ~/.gdbinit
        

3.  Now when you start gdb, you have to get something like this:
    
        $ gdb
        GNU gdb (Ubuntu 7.11.1-0ubuntu1~16.5) 7.11.1
        Copyright (C) 2016 Free Software Foundation, Inc.
        License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
        This is free software: you are free to change and redistribute it.
        There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
        and "show warranty" for details.
        This GDB was configured as "x86_64-linux-gnu".
        Type "show configuration" for configuration details.
        For bug reporting instructions, please see:
        <http://www.gnu.org/software/gdb/bugs/>.
        Find the GDB manual and other documentation resources online at:
        <http://www.gnu.org/software/gdb/documentation/>.
        For help, type "help".
        Type "apropos word" to search for commands related to "word".
        gdb-peda$ 
        

With this, you are ready to go!

This post will be fully hands-on and there won't be much theory to learn. It is all what we have discussed in previous articles. Let us take good number of examples and examine how C language is converted into assembly language by the compiler.

In the first set of examples, let us discuss about how variables of different datatypes are stored in memory. In the second set, we will have a look into different C constructs.

## 2\. Practicals

## Program1

    ~/rev_eng_series/post_5$ cat code1.c
    #include<stdio.h> 
    
    int gv = 2000;
    
    int main() {
    
        char c = 'a';
    short int s = 1234;
    int i = 4837538;
    long int l = 2348027502937;
    
        static int si = 394738;
    
    return 0;
    }
    ~/rev_eng_series/post_5$ gcc code1.c -o code1 -g
    

a. This is **code1.c** . In this program, we will look at the very basics. We have been telling that stack is used to store local variables, but never saw how. This program is all about that. There are local variables of different datatypes. Let us see how they are stored in **stack** .

*   Compile the **code1.c** sourcefile with the **-g** option. It stores **Debugging Symbols** in the executable which is used by the **Debugger** and make our analysis easy. 

### Analysis:

*   To **load** an executable to gdb,
    
        ~/rev_eng_series/post_5$ gdb code1
        GNU gdb (Ubuntu 7.11.1-0ubuntu1~16.5) 7.11.1
        Copyright (C) 2016 Free Software Foundation, Inc.
        License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
        This is free software: you are free to change and redistribute it.
        There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
        and "show warranty" for details.
        This GDB was configured as "x86_64-linux-gnu".
        Type "show configuration" for configuration details.
        For bug reporting instructions, please see:
        <http://www.gnu.org/software/gdb/bugs/>.
        Find the GDB manual and other documentation resources online at:
        <http://www.gnu.org/software/gdb/documentation/>.
        For help, type "help".
        Type "apropos word" to search for commands related to "word"...
        Reading symbols from code1...done.
        gdb-peda$ 
        

*   Observe the line **Reading symbols from code1...done.** . These are the symbols which are added to the executable(here **code1**) when compiled with **-g** option.

*   Everytime when you open an ELF File with gdb, gdb will print all of it's version details, License details. To suppress it from print all those details, you can do this:
    
        ~/rev_eng_series/post_5$ gdb -q code1
        Reading symbols from code1...done.
        gdb-peda$ 
        

*   We have not yet run our executable. At this stage, **gdb** is fully aware of our executable, it's symbols, functions etc.,

*   If we run the program like the way we run normally on the terminal, then we are not making use of the amazing facilities offered by gdb. gdb offers a special facility called **BreakPoints** . That is, if you want to stop your execution at a particular instruction, you can **set** a BreakPoint there, you can inspect the instruction, memory at that moment and then go to the next instruction.

*   We want to analyze the whole **main** function. So, let us set a BreakPoint at **main** function.
    
        gdb-peda$ break main
        Breakpoint 1 at 0x4004da: file code1.c, line 7.
        gdb-peda$ 
        

**NOTE**: The addresses like 0x4004da might change on your computer. It might be different. Follow the concept properly.

*   Note that this is **BreakPoint 1** and is set at the address **0x4004da** . This means, this address is where the **main** function begins. gdb also know in which line of the C sourcefile we are breaking. If you want print your sourcecode, you can use the **list** intruction.
    
        gdb-peda$ list
        1   #include<stdio.h>
        2   
        3   int gv = 2000;
        4   
        5   int main() {
        6   
        7       char c = 'a';
        8       short int s = 1234;
        9       int i = 4837538;
        10      long int l = 2348027502937;
        gdb-peda$ 
        11      
        12      static int si = 394738;
        13      
        14      return 0;
        15  }
        gdb-peda$ 
        

*   To understand the internal working, it is best if we have the **assembly code** for the main function. To get the assembly code, you have to **disassemble** the executable.
    
        gdb-peda$ disass main
        Dump of assembler code for function main:
        0x00000000004004d6 <+0>:    push   rbp
        0x00000000004004d7 <+1>:    mov    rbp,rsp
        0x00000000004004da <+4>:    mov    BYTE PTR [rbp-0xf],0x61
        0x00000000004004de <+8>:    mov    WORD PTR [rbp-0xe],0x4d2
        0x00000000004004e4 <+14>:   mov    DWORD PTR [rbp-0xc],0x49d0a2
        0x00000000004004eb <+21>:   movabs rax,0x222b1586159
        0x00000000004004f5 <+31>:   mov    QWORD PTR [rbp-0x8],rax
        0x00000000004004f9 <+35>:   mov    eax,0x0
        0x00000000004004fe <+40>:   pop    rbp
        0x00000000004004ff <+41>:   ret    
        End of assembler dump.
        gdb-peda$ 
        

*   Note that the **BreakPoint 1** is set at **0x4004da** which is **<+4>** . Let us set a BreakPoint at **0x4004d6** .
    
        gdb-peda$ b *0x4004d6
        Breakpoint 1 at 0x4004d6: file code1.c, line 5.
        gdb-peda$ 
        

*   We had just mentioned about **rsp** and **rbp** being **Stack Pointer** and **Base Pointer** in one of the previous articles. Now, let us understand what exactly these pointers are, what they do and why they are important.

*   We know that a function's **Local Variables** are stored in stack. Let us understand how exactly these variables are stored.

*   When a function is called, a part of the stack is allocated to the function. This part of the stack which is allocated to the function is known as **StackFrame** . So, to be more precise, a function's local variables are stored in it's **private** stack space called StackFrame.

*   The size of StackFrame solely depends on the number of local variables in the function. If there are more number of variables, size of StackFrame is big.

*   The **Base Address**(Address of Bottom) of the StackFrame is stored in **rbp** . The **Top Address**(Address of Top) of the StackFrame is stored in **rsp** .

*   Let us run the program to properly understand what a StackFrame is.
    
        gdb-peda$ run
        Starting program: /home/adwi/rev_eng_series/post_5/code1
        

*   This is what you get.

NOTE: The addresses shown in this post and addresses in your executable might be different. But the concepts are the same.

        [----------------------------------registers-----------------------------------]
        RAX: 0x4004d6 (<main>:  push   rbp)
        RBX: 0x0 
        RCX: 0x0 
        RDX: 0x7fffffffdbc8 --> 0x7fffffffdfdf ("XDG_VTNR=7")
        RSI: 0x7fffffffdbb8 --> 0x7fffffffdfb8 ("/home/adwi/rev_eng_series/post_5/code1")
        RDI: 0x1 
        RBP: 0x400500 (<__libc_csu_init>:   push   r15)
        RSP: 0x7fffffffdad8 --> 0x7ffff7a2d830 (<__libc_start_main+240>:    mov    edi,eax)
        RIP: 0x4004d6 (<main>:  push   rbp)
        R8 : 0x400570 (<__libc_csu_fini>:   repz ret)
        R9 : 0x7ffff7de7ab0 (<_dl_fini>:    push   rbp)
        R10: 0x846 
        R11: 0x7ffff7a2d740 (<__libc_start_main>:   push   r14)
        R12: 0x4003e0 (<_start>:    xor    ebp,ebp)
        R13: 0x7fffffffdbb0 --> 0x1 
        R14: 0x0 
        R15: 0x0 
        EFLAGS: 0x246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
        [-------------------------------------code-------------------------------------]
           0x4004ce <frame_dummy+30>:   call   rax
           0x4004d0 <frame_dummy+32>:   pop    rbp
           0x4004d1 <frame_dummy+33>:   jmp    0x400450 <register_tm_clones>
        => 0x4004d6 <main>: push   rbp
           0x4004d7 <main+1>:   mov    rbp,rsp
           0x4004da <main+4>:   mov    BYTE PTR [rbp-0xf],0x61
           0x4004de <main+8>:   mov    WORD PTR [rbp-0xe],0x4d2
           0x4004e4 <main+14>:  mov    DWORD PTR [rbp-0xc],0x49d0a2
        [------------------------------------stack-------------------------------------]
           0000| 0x7fffffffdad8 --> 0x7ffff7a2d830 (<__libc_start_main+240>:    mov    edi,eax)
           0008| 0x7fffffffdae0 --> 0x0 
           0016| 0x7fffffffdae8 --> 0x7fffffffdbb8 --> 0x7fffffffdfb8 ("/home/adwi/rev_eng_series/post_5/code1")
           0024| 0x7fffffffdaf0 --> 0x100000000 
           0032| 0x7fffffffdaf8 --> 0x4004d6 (<main>:   push   rbp)
           0040| 0x7fffffffdb00 --> 0x0 
           0048| 0x7fffffffdb08 --> 0x5bf888248267542a 
           0056| 0x7fffffffdb10 --> 0x4003e0 (<_start>: xor    ebp,ebp)
        [------------------------------------------------------------------------------]
        Legend: code, data, rodata, value
    
        Breakpoint 2, main () at code1.c:5
        5   int main() {
        gdb-peda$ 
    

*   This is how your terminal should look like. Important things to note are:
    
    *   **=> 0x4004d6 <main>: push rbp</main>** : This is the first instruction of main function. The **=>** mark is pointing to this instruction. **=>** always points to the instruction which gets executed next. So, this instruction is still not executed as of now, but will be executed next.
    
    *   Note the **rsp** and **rbp** values as of now. **rsp = 0x7fffffffdad8** and **rbp = 0x400500** .

*   Let us consider the next 2 instructions:
    
        0x4004d6 <main>:    push   rbp
        0x4004d7 <main+1>:  mov    rbp,rsp
        

*   The **push rbp** will push the present rbp value onto the stack. Currently, rbp has the Base Address of the Caller function and it is being pushed. Let us discuss why it is being pushed a bit later.

*   Lets execute **<main></main>** using the **ni** command. **ni** stands for **next instruction** . This executes 1 instruction at a time.
    
        gdb-peda$ ni
        

*   This is what the state is after **ni** command is executed.
    
        [-------------------------------------code-------------------------------------]
           0x4004d0 <frame_dummy+32>:   pop    rbp
           0x4004d1 <frame_dummy+33>:   jmp    0x400450 <register_tm_clones>
           0x4004d6 <main>: push   rbp
        => 0x4004d7 <main+1>:   mov    rbp,rsp
           0x4004da <main+4>:   mov    BYTE PTR [rbp-0xf],0x61
           0x4004de <main+8>:   mov    WORD PTR [rbp-0xe],0x4d2
           0x4004e4 <main+14>:  mov    DWORD PTR [rbp-0xc],0x49d0a2
           0x4004eb <main+21>:  movabs rax,0x222b1586159
        [------------------------------------stack-------------------------------------]
           0000| 0x7fffffffdad0 --> 0x400500 (<__libc_csu_init>:    push   r15)
           0008| 0x7fffffffdad8 --> 0x7ffff7a2d830 (<__libc_start_main+240>:    mov    edi,eax)
           0016| 0x7fffffffdae0 --> 0x0 
           0024| 0x7fffffffdae8 --> 0x7fffffffdbb8 --> 0x7fffffffdfb8 
           ("/home/adwi/rev_eng_series/post_5/code1")
           0032| 0x7fffffffdaf0 --> 0x100000000 
           0040| 0x7fffffffdaf8 --> 0x4004d6 (<main>:   push   rbp)
           0048| 0x7fffffffdb00 --> 0x0 
           0056| 0x7fffffffdb08 --> 0x5bf888248267542a 
        [------------------------------------------------------------------------------]
        Legend: code, data, rodata, value 
        0x00000000004004d7  5   int main() {
        gdb-peda$ 
        

*   Now the **=>** is pointing to **mov rbp, rsp** which means the **push rbp** is executed.

*   Note the top of the stack: **0000| 0x7fffffffdad0 --> 0x400500** . Note that **rsp** is now **0x7fffffffdad0** and Content at the top of the stack is **0x400500** which is the Old rbp value. So, everything has happened as expected.

*   Note that current values of **rbp = 0x400500** and **rsp = 0x7fffffffdad0** .

*   Let us execute the next instruction.
    
        gdb-peda$ ni
        

*   This is how the terminal looks like.
    
        [----------------------------------registers-----------------------------------]
        RAX: 0x4004d6 (<main>:  push   rbp)
        RBX: 0x0 
        RCX: 0x0 
        RDX: 0x7fffffffdbc8 --> 0x7fffffffdfdf ("XDG_VTNR=7")
        RSI: 0x7fffffffdbb8 --> 0x7fffffffdfb8 ("/home/adwi/rev_eng_series/post_5/code1")
        RDI: 0x1 
        RBP: 0x7fffffffdad0 --> 0x400500 (<__libc_csu_init>:    push   r15)
        RSP: 0x7fffffffdad0 --> 0x400500 (<__libc_csu_init>:    push   r15)
        RIP: 0x4004da (<main+4>:    mov    BYTE PTR [rbp-0xf],0x61)
        R8 : 0x400570 (<__libc_csu_fini>:   repz ret)
        R9 : 0x7ffff7de7ab0 (<_dl_fini>:    push   rbp)
        R10: 0x846 
        R11: 0x7ffff7a2d740 (<__libc_start_main>:   push   r14)
        R12: 0x4003e0 (<_start>:    xor    ebp,ebp)
        R13: 0x7fffffffdbb0 --> 0x1 
        R14: 0x0 
        R15: 0x0
        EFLAGS: 0x246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
        [-------------------------------------code-------------------------------------]
           0x4004d1 <frame_dummy+33>:   jmp    0x400450 <register_tm_clones>
           0x4004d6 <main>: push   rbp
           0x4004d7 <main+1>:   mov    rbp,rsp
        => 0x4004da <main+4>:   mov    BYTE PTR [rbp-0xf],0x61
           0x4004de <main+8>:   mov    WORD PTR [rbp-0xe],0x4d2
           0x4004e4 <main+14>:  mov    DWORD PTR [rbp-0xc],0x49d0a2
           0x4004eb <main+21>:  movabs rax,0x222b1586159
           0x4004f5 <main+31>:  mov    QWORD PTR [rbp-0x8],rax
        [------------------------------------stack-------------------------------------]
           0000| 0x7fffffffdad0 --> 0x400500 (<__libc_csu_init>:    push   r15)
           0008| 0x7fffffffdad8 --> 0x7ffff7a2d830 (<__libc_start_main+240>:    mov    edi,eax)
           0016| 0x7fffffffdae0 --> 0x0 
           0024| 0x7fffffffdae8 --> 0x7fffffffdbb8 --> 0x7fffffffdfb8 
           ("/home/adwi/rev_eng_series/post_5/code1")
           0032| 0x7fffffffdaf0 --> 0x100000000 
           0040| 0x7fffffffdaf8 --> 0x4004d6 (<main>:   push   rbp)
           0048| 0x7fffffffdb00 --> 0x0 
           0056| 0x7fffffffdb08 --> 0x5bf888248267542a 
        [------------------------------------------------------------------------------]
        Legend: code, data, rodata, value
        
        Breakpoint 1, main () at code1.c:7
        7       char c = 'a';
        gdb-peda$ 
        

*   **mov rbp, rsp** was executed. Value of rsp should have got copied into rbp. And that has happened. Value of rsp = 0x7fffffffdad0 and rbp = 0x7fffffffdad0. There are 2 important points to understand at this point:
    
    *   The value rbp had previously was overwritten by the value of rsp. If we had not pushed the old rbp value onto the stack, then we would have permanently lost that value. That is why, whenever a function is called, the **first job** done is to push the old rbp value onto the stack so that we won't lose it.
    
    *   Second point is that, now, rbp = rsp. Base pointer = Stack Pointer which means this is a **StackFrame with size = 0** . So, After **mov rbp, rsp** is executed, a StackFrame with size **0** is constructed.

*   From now, let us focus more on **Code** and the **Stack** part.

*   Let us execute the next instruction - **mov BYTE PTR [rbp-0xf],0x61** . After execution, this is the state.
    
        [-------------------------------------code-------------------------------------]
           0x4004d6 <main>: push   rbp
           0x4004d7 <main+1>:   mov    rbp,rsp
           0x4004da <main+4>:   mov    BYTE PTR [rbp-0xf],0x61
        => 0x4004de <main+8>:   mov    WORD PTR [rbp-0xe],0x4d2
           0x4004e4 <main+14>:  mov    DWORD PTR [rbp-0xc],0x49d0a2
           0x4004eb <main+21>:  movabs rax,0x222b1586159
           0x4004f5 <main+31>:  mov    QWORD PTR [rbp-0x8],rax
           0x4004f9 <main+35>:  mov    eax,0x0
        [------------------------------------stack-------------------------------------]
           0000| 0x7fffffffdad0 --> 0x400500 (<__libc_csu_init>:    push   r15)
           0008| 0x7fffffffdad8 --> 0x7ffff7a2d830 (<__libc_start_main+240>:    mov    edi,eax)
           0016| 0x7fffffffdae0 --> 0x0 
           0024| 0x7fffffffdae8 --> 0x7fffffffdbb8 --> 0x7fffffffdfb8 
           ("/home/adwi/rev_eng_series/post_5/code1")
           0032| 0x7fffffffdaf0 --> 0x100000000 
           0040| 0x7fffffffdaf8 --> 0x4004d6 (<main>:   push   rbp)
           0048| 0x7fffffffdb00 --> 0x0 
           0056| 0x7fffffffdb08 --> 0x5bf888248267542a 
        [------------------------------------------------------------------------------]
        Legend: code, data, rodata, value
        8       short int s = 1234; 
        gdb-peda$ 
        

*   Note that some value **0x61** is stored at the address **rbp - 0xf** . **0x61** is the **ascii** value of **a** . Let us take a deeper look at how the C code **char c = 'a'** is converted to **mov BYTE PTR [rbp-0xf],0x61** .
    
    *   **char c = 'a'** ==> **char c = 0x61** ==> **char [rbp - 0xf] = 0x61** ==> **BYTE PTR [rbp - 0xf] = 0x61** ==> **mov BYTE PTR[rbp - 0xf], 0x61** .
    
    *   Notice that **c** is no more present in the executable and it is replaced directly by a memory address **rbp - 0xf** . **BYTE PTR** signifies that it is a **char** because sizeof(char) is **1 byte** .

*   Let us now inspect the memory location **rbp - 0xf** using the **x/** command.
    
        gdb-peda$ x/10xb $rbp - 0xf
        0x7fffffffdac1: 0x61    0xff    0xff    0xff    0x7f    0x00    0x00    0x00
        0x7fffffffdac9: 0x00    0x00
        

*   Let me explain the above command used. The **x/** command is used to check out any portion of the memory. The 10xb stands for **show 10 bytes of data from the specified address in hexadecimal form** and separate every byte of data. Look at the above output. 0x61 is 1 byte, 0xff is 2nd byte, 0c7f is the 5th byte and so on.

*   You can also use the command like this: **x/10xw $rbp - 0xf** .
    
        gdb-peda$ x/10xw $rbp - 0xf
        0x7fffffffdac1: 0xffffff61  0x0000007f  0x00000000  0x00000000
        0x7fffffffdad1: 0x00004005  0x30000000  0xfff7a2d8  0x0000007f
        0x7fffffffdae1: 0x00000000  0xb8000000
        gdb-peda$ 
        
    
    *   Here **10xw** stands for 10 words(each word here = 4 bytes) and all data in hexadecimal form(x).
    
    *   Look at the first 4 bytes. It is **0xffffff61** . But the first byte should have been **0x61** right? Just know that even now, **0x61** is the first byte, but there is difference. There is a very important concept behind this. Let us talk about it at the end of the article.

*   So, at the end of this instruction, **rbp - 0xf** address has the value **0x61** which is **'a'**, the character variable which we had defined in our C program.

*   Let us move to the next instruction - **mov WORD PTR [rbp-0xe],0x4d2** . Checkout the value of decimal equivalent of **0x4d2** . It is **1234** . While doing analysis, it is good to have python interpreter opened in another terminal. You can do all these conversions very easily.

*   So, let us checkout the memory location specified by **rbp - 0xe**.
    
        gdb-peda$ x/10xb $rbp - 0xe
        0x7fffffffdac2: 0xd2    0x04    0xff    0x7f    0x00    0x00    0x00    0x00
        0x7fffffffdaca: 0x00    0x00
        gdb-peda$ 
        

*   So, it is stored as **0xd2 0x04** , in the reverse order of 0x04d2. Let us talk about this reversing later, but for now know that the number is stored in the memory location.

*   Now, I think you will be able to make sense of the next 3 instructions. So, I will skip them.

*   Directly coming to **0x4004f9 <main+35>: mov eax,0x0** . It is important to note that the **return value** of the main function is **0** . So, always at the end of **any** function, the **ReturnValue** is loaded into **rax** / **eax** .

*   Onto the next instruction: **0x4004fe <main+40>: pop rbp** .
    
    *   Before executing this instruction, rsp = 0x7fffffffdad0 and rbp = 0x7fffffffdad0 and top of the had this value - **0x400500** .
    
    *   In general, **pop Reg1** will do 2 things.
        
        mov Reg1, QWORD PTR [rsp] add rsp, 0x08
    
    *   So, **pop rbp** will load the Value at the top of the stack into Reg1 and add 0x08 to **rsp**.
    
    *   Let us execute it and see what happens.
        
        RBP: 0x400500 (<__libc_csu_init>: push r15) RSP: 0x7fffffffdad8 --> 0x7ffff7a2d830</__libc_csu_init>
    
    *   Observe the old and new values of rsp and rbp. It has changed as expected.

*   **ret** is executed and control goes back the caller function.

With this, we have successfully analyzed a simple C program's execution. We basically dealt with

*   What **rsp** and **rbp** are. 
*   Why we have to store **old rbp** in the stack - (push rbp)
*   How a StackFrame is constructed dynamically. 
*   How are local variables stored in stack. 
*   How is return value conveyed to the caller function - (mov eax, 0x0)
*   How is control returned back to the caller function - (ret)

## Program2

    ~/rev_eng_series/post_5$ cat code2.c
    #include<stdio.h>
    int main() {
    
        int a = 10, b = 15;
    
    if(a > b)
        printf("a is greater than b\n");
    
    return 0;
    }
    ~/rev_eng_series/post_5$ gcc code2.c -o code2
    

Let us get straight to analysis!

### Analysis:

    ~/rev_eng_series/post_5$ gdb -q code2
    Reading symbols from code2...(no debugging symbols found)...done.
    gdb-peda$ disass main
    Dump of assembler code for function main:
    
       0x0000000000400526 <+0>: push   rbp
       0x0000000000400527 <+1>: mov    rbp,rsp
       0x000000000040052a <+4>: sub    rsp,0x10
       0x000000000040052e <+8>: mov    DWORD PTR [rbp-0x8],0xa
       0x0000000000400535 <+15>:    mov    DWORD PTR [rbp-0x4],0xf
       0x000000000040053c <+22>:    mov    eax,DWORD PTR [rbp-0x8]
       0x000000000040053f <+25>:    cmp    eax,DWORD PTR [rbp-0x4]
       0x0000000000400542 <+28>:    jle    0x40054e <main+40>
       0x0000000000400544 <+30>:    mov    edi,0x4005e4
       0x0000000000400549 <+35>:    call   0x400400 <puts@plt>
       0x000000000040054e <+40>:    mov    eax,0x0
       0x0000000000400553 <+45>:    leave  
       0x0000000000400554 <+46>:    ret    
    End of assembler dump.
    gdb-peda$ 
    

Let us understand the assembly code first.

a. Construction of the StackFrame:

*   First, **mov rbp, rsp** means a StackFrame of size **0** is constructed. b. The next instruction is **sub rsp, 0x10** => Subtract 0x10 - 16 from current rsp value. This means, the difference between **rsp** and **rbp** is **16** bytes. So, a StackFrame of size 16 bytes is constructed for main function.

b. Body of the function:

*   **mov DWORD PTR [rbp-0x8],0xa** : A value **0xa** (10) is being copied into memory specified by address **rbp - 0x08** . It is 4 bytes in size. It is the local variable **a** .

*   **mov DWORD PTR [rbp-0x4],0xf** : A value **0xf** (15) is being copied into memory specified by address **rbp - 0x4** . It is 4 bytes in size. It is the local variable **b** .

*   Notice that names of local variables are no longer present in the program. Only the respective memory locations are present and that is the only way to access those variables.

*   **mov eax,DWORD PTR [rbp-0x8]** : Value at **rbp-0x8** is being copied into **eax** . So, eax will have **0xa** after the execution of this instruction.

*   **cmp eax,DWORD PTR [rbp-0x4]** : Value in **eax** is being compared with value at **rbp - 0x4** .

*   **jle 0x40054e <main+40>** : **jle** is Jump if Less than or Equal to some location. It means, If **Value in eax** <= **Value at rbp - 0x4** , then jump to **0x40054e** . 0x40054e is the end of the program.

*   If Value in eax > Value at rbp - 0x4, then **jle** doesn't get executed. So, the instructions after jle get executed.

*   **mov edi,0x4005e4 ; call 0x400400 <puts@plt>** : puts() is executed.

c. Destruction of the StackFrame:

*   We can see a new instruction **leave** . This is nothing but the following 2 instructions:
    
        mov rsp, rbp 
        pop rbp
        

*   First the StackFrame is destructed by that mov instruction.

*   Then, the Old rbp value is loaded into the rbp register.

*   ret => Return back to the caller function.

Now that we have a good overview of the main function, let us execute it by instruction by instruction.

d. Break at main function and run!

        gdb-peda$ b main 
        Breakpoint 1 at 0x40052a 
        gdb-peda$ run
    

*   Let us focus on the **code** and **stack** part a few required registers.
    
        [-------------------------------------code-------------------------------------]
            0x400521 <frame_dummy+33>:  jmp    0x4004a0 <register_tm_clones>
            0x400526 <main>:    push   rbp
            0x400527 <main+1>:  mov    rbp,rsp
         => 0x40052a <main+4>:  sub    rsp,0x10
            0x40052e <main+8>:  mov    DWORD PTR [rbp-0x8],0xa
            0x400535 <main+15>: mov    DWORD PTR [rbp-0x4],0xf
            0x40053c <main+22>: mov    eax,DWORD PTR [rbp-0x8]
            0x40053f <main+25>: cmp    eax,DWORD PTR [rbp-0x4]
        [------------------------------------stack-------------------------------------]
        0000| 0x7fffffffdad0 --> 0x400560 (<__libc_csu_init>:   push   r15)
        0008| 0x7fffffffdad8 --> 0x7ffff7a2d830 (<__libc_start_main+240>:   mov    edi,eax)
        0016| 0x7fffffffdae0 --> 0x0 
        0024| 0x7fffffffdae8 --> 0x7fffffffdbb8 --> 0x7fffffffdfbb ("/home/adwi/rev_eng_series/post_5/code2")
        0032| 0x7fffffffdaf0 --> 0x100000000 
        0040| 0x7fffffffdaf8 --> 0x400526 (<main>:  push   rbp)
        0048| 0x7fffffffdb00 --> 0x0 
        0056| 0x7fffffffdb08 --> 0x864ee2b3356e8653 
        [------------------------------------------------------------------------------]
        Legend: code, data, rodata, value
        
        Breakpoint 1, 0x000000000040052a in main ()
        gdb-peda$ 
        

*   At this point, **rsp = 0x7fffffffdad0** and **rbp = 0x7fffffffdad0** . Size of StackFrame = 0.

*   Execute the **sub rsp, 0x10** using the **ni** command.
    
        gdb-peda$ ni
        

*   This is the current state:
    
        [----------------------------------registers-----------------------------------]
        RAX: 0x400526 (<main>:  push   rbp)
        RBX: 0x0 
        RCX: 0x0 
        RDX: 0x7fffffffdbc8 --> 0x7fffffffdfe2 ("XDG_VTNR=7")
        RSI: 0x7fffffffdbb8 --> 0x7fffffffdfbb ("/home/adwi/rev_eng_series/post_5/code2")
        RDI: 0x1 
        RBP: 0x7fffffffdad0 --> 0x400560 (<__libc_csu_init>:    push   r15)
        RSP: 0x7fffffffdac0 --> 0x7fffffffdbb0 --> 0x1 
        RIP: 0x40052e (<main+8>:    mov    DWORD PTR [rbp-0x8],0xa)
        R8 : 0x4005d0 (<__libc_csu_fini>:   repz ret)
        R9 : 0x7ffff7de7ab0 (<_dl_fini>:    push   rbp)
        R10: 0x846 
        R11: 0x7ffff7a2d740 (<__libc_start_main>:   push   r14) 
        R12: 0x400430 (<_start>:    xor    ebp,ebp)
        R13: 0x7fffffffdbb0 --> 0x1 
        R14: 0x0 
        R15: 0x0
        EFLAGS: 0x206 (carry PARITY adjust zero sign trap INTERRUPT direction overflow)
        [-------------------------------------code-------------------------------------]
           0x400526 <main>: push   rbp
           0x400527 <main+1>:   mov    rbp,rsp
           0x40052a <main+4>:   sub    rsp,0x10
        => 0x40052e <main+8>:   mov    DWORD PTR [rbp-0x8],0xa
           0x400535 <main+15>:  mov    DWORD PTR [rbp-0x4],0xf
           0x40053c <main+22>:  mov    eax,DWORD PTR [rbp-0x8]
           0x40053f <main+25>:  cmp    eax,DWORD PTR [rbp-0x4]
           0x400542 <main+28>:  jle    0x40054e <main+40>
        [------------------------------------stack-------------------------------------]
        0000| 0x7fffffffdac0 --> 0x7fffffffdbb0 --> 0x1 
        0008| 0x7fffffffdac8 --> 0x0 
        0016| 0x7fffffffdad0 --> 0x400560 (<__libc_csu_init>:   push   r15)
        0024| 0x7fffffffdad8 --> 0x7ffff7a2d830 (<__libc_start_main+240>:   mov    edi,eax)
        0032| 0x7fffffffdae0 --> 0x0 
        0040| 0x7fffffffdae8 --> 0x7fffffffdbb8 --> 0x7fffffffdfbb ("/home/adwi/rev_eng_series/post_5/code2")
        0048| 0x7fffffffdaf0 --> 0x100000000 
        0056| 0x7fffffffdaf8 --> 0x400526 (<main>:  push   rbp)
        [------------------------------------------------------------------------------]
        Legend: code, data, rodata, value
        0x000000000040052e in main ()
        gdb-peda$ 
        

*   Here, **rsp = 0x7fffffffdac0** and **rbp = 0x7fffffffdad0** . There is an important thing to understand at this point. In the previous article, we had just discussed that **Stack grows Downward** in the Memory Layout of a process. Notice that **0x10** was subtracted from **rsp** and not added. So, this is **Stack growing downward** in action. For this reason, **Value of rsp** is always less than or equal to **Value of rbp** .

*   Let us check what our StackFrame has:
    
        gdb-peda$ x/16xb $rsp
        0x7fffffffdac0: 0xb0    0xdb    0xff    0xff    0xff    0x7f    0x00    0x00
        0x7fffffffdac8: 0x00    0x00    0x00    0x00    0x00    0x00    0x00    0x00
        

*   You can obviously check out the top of the stack with the gdb-peda output. You can see the top 8 bytes(**0000| 0x7fffffffdac0 --> 0x7fffffffdbb0 --> 0x1**) is some address and the next 8 bytes is just zeros.

*   At this stage, we have a proper **Private StackFrame** ready for main function.

*   Now, let us go ahead and execute the next instruction: (Showing only the code and stack part)
    
        [-------------------------------------code-------------------------------------]
           0x400527 <main+1>:   mov    rbp,rsp
           0x40052a <main+4>:   sub    rsp,0x10
           0x40052e <main+8>:   mov    DWORD PTR [rbp-0x8],0xa
        => 0x400535 <main+15>:  mov    DWORD PTR [rbp-0x4],0xf
           0x40053c <main+22>:  mov    eax,DWORD PTR [rbp-0x8]
           0x40053f <main+25>:  cmp    eax,DWORD PTR [rbp-0x4]
           0x400542 <main+28>:  jle    0x40054e <main+40>
           0x400544 <main+30>:  mov    edi,0x4005e4
        
        
        [------------------------------------stack-------------------------------------] 0000| 
        0000| 0x7fffffffdac0 --> 0x7fffffffdbb0 --> 0x1 
        0008| 0x7fffffffdac8 --> 0xa ('\n') 
        0016| 0x7fffffffdad0 --> 0x400560 (<\_\_libc_csu_init>: push r15) 
        0024| 0x7fffffffdad8 --> 0x7ffff7a2d830 (<\_\_libc_start_main+240>: mov edi,eax) 
        0032| 0x7fffffffdae0 --> 0x0 
        0040| 0x7fffffffdae8 --> 0x7fffffffdbb8 --> 0x7fffffffdfbb ("/home/adwi/rev_eng_series/post_5/code2") 
        0048| 0x7fffffffdaf0 --> 0x100000000 
        0056| 0x7fffffffdaf8 --> 0x400526 (<main>: push rbp) 
        [------------------------------------------------------------------------------] 
        Legend: code, data, rodata, value 
        0x0000000000400535 in main () 
        gdb-peda$
        

*   Now, Memory location **rbp - 0x8** should have **0xa** (10). Check out the the stack. Let us check out using the **x** command.
    
        0x0000000000400535 in main ()
        gdb-peda$ x/8xb $rbp - 0x8
        0x7fffffffdac8: 0x0a    0x00    0x00    0x00    0x00    0x00    0x00    0x00
        gdb-peda$ 
        

*   Let us execute the next instruction - **mov DWORD PTR [rbp-0x4],0xf**
    
        [-------------------------------------code-------------------------------------]
           0x40052a <main+4>:   sub    rsp,0x10
           0x40052e <main+8>:   mov    DWORD PTR [rbp-0x8],0xa
           0x400535 <main+15>:  mov    DWORD PTR [rbp-0x4],0xf
        => 0x40053c <main+22>:  mov    eax,DWORD PTR [rbp-0x8]
           0x40053f <main+25>:  cmp    eax,DWORD PTR [rbp-0x4]
           0x400542 <main+28>:  jle    0x40054e <main+40>
           0x400544 <main+30>:  mov    edi,0x4005e4
           0x400549 <main+35>:  call   0x400400 <puts@plt>
        [------------------------------------stack-------------------------------------]
        0000| 0x7fffffffdac0 --> 0x7fffffffdbb0 --> 0x1 
        0008| 0x7fffffffdac8 --> 0xf0000000a 
        0016| 0x7fffffffdad0 --> 0x400560 (<__libc_csu_init>:   push   r15)
        0024| 0x7fffffffdad8 --> 0x7ffff7a2d830 (<__libc_start_main+240>:   mov    edi,eax)
        0032| 0x7fffffffdae0 --> 0x0 
        0040| 0x7fffffffdae8 --> 0x7fffffffdbb8 --> 0x7fffffffdfbb ("/home/adwi/rev_eng_series/post_5/code2")
        0048| 0x7fffffffdaf0 --> 0x100000000 
        0056| 0x7fffffffdaf8 --> 0x400526 (<main>:  push   rbp)
        [------------------------------------------------------------------------------]
        Legend: code, data, rodata, value
        0x000000000040053c in main ()
        gdb-peda$ 
        

*   Now, Memory location **rbp - 0x4** should have **0xf** . Check the stack: **0008| 0x7fffffffdac8 --> 0xf0000000a** . This is the variable:
    
        gdb-peda$ x/4xb $rbp - 0x4
        0x7fffffffdacc: 0x0f    0x00    0x00    0x00
        gdb-peda$ 
        

*   Next instruction is straight forward: **mov eax,DWORD PTR [rbp-0x8]** - So skipping this.

*   Executing **cmp eax,DWORD PTR [rbp-0x4]** : Compares **Value in eax** with **Value at rbp - 0x04** and sets appropriate flags in the **EFLAGS** register.

*   Executing **jle 0x40054e <main+40>** : The **jle** instruction checks the **EFLAGS** register. If certain flags are set, only then the jump will happen. If not, the jump is not going to happen. Here, **Value in eax** < **Value at rbp - 0x04** (10 < 15) . So, the jump **happens** . The puts() is not executed.

*   After executing **jle**, we are here:
    
        [-------------------------------------code-------------------------------------]
           0x400542 <main+28>:  jle    0x40054e <main+40>
           0x400544 <main+30>:  mov    edi,0x4005e4
           0x400549 <main+35>:  call   0x400400 <puts@plt>
        => 0x40054e <main+40>:  mov    eax,0x0
           0x400553 <main+45>:  leave  
           0x400554 <main+46>:  ret    
           0x400555:    nop    WORD PTR cs:[rax+rax*1+0x0]
           0x40055f:    nop
        [------------------------------------stack-------------------------------------]
        0000| 0x7fffffffdac0 --> 0x7fffffffdbb0 --> 0x1 
        0008| 0x7fffffffdac8 --> 0xf0000000a 
        0016| 0x7fffffffdad0 --> 0x400560 (<__libc_csu_init>:   push   r15)
        0024| 0x7fffffffdad8 --> 0x7ffff7a2d830 (<__libc_start_main+240>:   mov    edi,eax)
        0032| 0x7fffffffdae0 --> 0x0 
        0040| 0x7fffffffdae8 --> 0x7fffffffdbb8 --> 0x7fffffffdfbb ("/home/adwi/rev_eng_series/post_5/code2")
        0048| 0x7fffffffdaf0 --> 0x100000000 
        0056| 0x7fffffffdaf8 --> 0x400526 (<main>:  push   rbp)
        [------------------------------------------------------------------------------] 
        Legend: code, data, rodata, value
        0x000000000040054e in main ()
        gdb-peda$ 
        

*   We bypassed the puts(). **mov eax, 0x0** is **return 0** ;

*   Let us understand what **leave** does as it is a new instruction for us.

*   Current state: **rsp = 0x7fffffffdac0** , **rbp = 0x7fffffffdad0** .

*   After leave: **rsp = 0x7fffffffdad8** , **rbp = 0x400560** .

Analysis:

*   **leave** = **mov rsp, rbp** ; **pop rbp** . 
*   Current state: **rsp = 0x7fffffffdac0** , **rbp = 0x7fffffffdad0**
*   After **mov rsp, rbp**, the state is: **rsp = 0x7fffffffdad0** , **rbp = 0x7fffffffdad0** . The point to understand is, the StackFrameis destructed and that stack space of 16 bytes is freed. 
*   **pop rbp** : The top of the stack has the value **0x400560** . So, **rsp = 0x7fffffffdad0** points to **0x400560** . When **pop rbp** is executed, the value at the top of the stack(**0x400560**) is loaded into **rbp** **AND** **rsp** is incremented by **8** bytes. So, rsp = 0x7fffffffdad0 becomes rsp = 0x7fffffffdad0 + 8 => rsp = 0x7fffffffdad8 .

*   The ret will return control to the caller function.

That ends the analysis of a simple C program. So, the 2 examples taken above were to understand 2 things:

a. How variables are stored in stack and how to see the stack using gdb. b. How Assembly instructions are executed.

Now, let us give gdb a break and look at reading only assembly instructions and see what it does.

## Program3

    ~/rev_eng_series/post_5$ cat code3.c
    #include<stdio.h>
    int main() {
    
        int i = 0;
    
    while(i < 10) {
        printf("%d\n", i);
        i = i + 1;
    }
    
    return 0;
    }
    ~/rev_eng_series/post_5$ gcc code3.c -o code3
    

*   This is a simple program with a while loop.

*   We want only the Assembly code of this program. Let us not get into running this. Let us understand the program just by reading code.

*   If we want only Assembly code, we don't have to use gdb and then do **disass main** to get the **Disassembly** . You can use this tool called **objdump** . Let us see how.
    
    ~/rev_eng_series/post_5$ objdump -Mintel -D code3 > code3.objdump

*   **-M** stands for machine / processor. We want it in the Intel Syntax. If you don't specify it, you will the Disassembly in AT&T Syntax.

*   **-D** stands for Full Disassembly. Meaning, all parts of the file is disassembled . If **-d** is used, only selected parts are disassembled. Either ways, we will get the disassembly of the main function which is what we want.

*   **>** simply puts the output of objdump into a file named **code3.objdump** .

*   Let's open that file and see what it has:

*   It has a lot of sections. Let us focus on the **main** function for now.
    
        0000000000400526 <main>:
          400526:       55                      push   rbp
          400527:       48 89 e5                mov    rbp,rsp
          40052a:       48 83 ec 10             sub    rsp,0x10
          40052e:       c7 45 fc 00 00 00 00    mov    DWORD PTR [rbp-0x4],0x0
          400535:       eb 18                   jmp    40054f <main+0x29>
          400537:       8b 45 fc                mov    eax,DWORD PTR [rbp-0x4]
          40053a:       89 c6                   mov    esi,eax
          40053c:       bf e4 05 40 00          mov    edi,0x4005e4
          400541:       b8 00 00 00 00          mov    eax,0x0
          400546:       e8 b5 fe ff ff          call   400400 <printf@plt>
          40054b:       83 45 fc 01             add    DWORD PTR [rbp-0x4],0x1
          40054f:       83 7d fc 09             cmp    DWORD PTR [rbp-0x4],0x9
          400553:       7e e2                   jle    400537 <main+0x11>
          400555:       b8 00 00 00 00          mov    eax,0x0
          40055a:       c9                      leave
          40055b:       c3                      ret
          40055c:       0f 1f 40 00             nop    DWORD PTR [rax+0x0]
        

Analysis:

a. Construction of StackFrame:

    400526:       55                      push   rbp
    400527:       48 89 e5                mov    rbp,rsp
    40052a:       48 83 ec 10             sub    rsp,0x10
    

*   A StackFrame of size 0x10(16) bytes is constructed. 

b. **40052e** :

    40052e:       c7 45 fc 00 00 00 00    mov    DWORD PTR [rbp-0x4],0x0
    

*   4 bytes specified by **rbp - 0x4** is set to 0. It is 4 bytes because of **DWORD PTR** . 

c. **400535** :

    400535:       eb 18                   jmp    40054f <main+0x29>
    

*   This is a simple Jump to instruction at **0x40054f**. This jmp is like C's **goto** construct. It will just jump without any condition - Unconditional Jump. 

d. **40054f** :

    40054f:       83 7d fc 09             cmp    DWORD PTR [rbp-0x4],0x9
    400553:       7e e2                   jle    400537 <main+0x11>
    

*   It is comparing Value at **rbp - 0x4** with 9(Comparing **i** with 9). If i is less than equal to 9, then it will jump to instruction at **0x400537** . At this point, Value at **rbp - 0x4** is 0. So, We jump to instruction at **0x400537**. It is important to note that our condition was **i < 10** but here, **i <= 9** is being done. Both are obviously the same. 

** There is important thing to understand: When we describe a while() loop, what we say is First the condition inside is checked, only then the body of the while is executed if the condition satisfies. Here, we just did the same thing. First executed the **cmp** instruction which is the while condition. The **jle** instruction decides if we have to jump into body of while loop or just move out of it.

** I hope you are able to appreciate the amount of clarity you get regarding day-to-day code constructs by understanding it's assembly equivalent code.

e. Body of while() :

    400537:       8b 45 fc                mov    eax,DWORD PTR [rbp-0x4]
    40053a:       89 c6                   mov    esi,eax
    40053c:       bf e4 05 40 00          mov    edi,0x4005e4
    400541:       b8 00 00 00 00          mov    eax,0x0
    400546:       e8 b5 fe ff ff          call   400400 <printf@plt>
    40054b:       83 45 fc 01             add    DWORD PTR [rbp-0x4],0x1
    

*   The printf() is executed. Then **add DWORD PTR [rbp-0x4],0x1** adds 1 to **i**. Then, the following 2 instructions will be executed which are the while() condition check and whether or not to jump into body of while() or out of it.
    
    40054f: 83 7d fc 09 cmp DWORD PTR [rbp-0x4],0x9 400553: 7e e2 jle 400537 <main+0x11>

f. End:

    400555:       b8 00 00 00 00          mov    eax,0x0
    40055a:       c9                      leave
    40055b:       c3                      ret
    

*   When **DWORD PTR[rbp - 0x4]** becomes 10, **jle** doesn't get executed. So, the above instructions are executed.

I hope you have understood how a while loop works in detail. You will have to write programs to understand **for** and **do while** loops on your own.

## Program4

In this example, we will see how a structure is translated into assembly level.

    ~/rev_eng_series/post_5$ cat code4.c
    #include<stdio.h>
    int main() {
    
    struct details {
    
        char name[30];
        int rollno;
    };
    
    return 0;
    } 
    ~/rev_eng_series/post_5$ gcc code4.c -o code4
    

a. Let us checkout it's disassembly quickly.

    00000000004004d6 <main>:
      4004d6:   55                      push   rbp
      4004d7:   48 89 e5                mov    rbp,rsp
      4004da:   b8 00 00 00 00          mov    eax,0x0
      4004df:   5d                      pop    rbp
      4004e0:   c3                      ret    
    

b. Wow! There is no sign of structure inside the Assembly code. Why is this?

This will take us back to C programming basics. You would have probably studied that Definition of a structure won't take memory. But, if you declare a struct of that type, that will take memory.

We saw the same thing. We had the definiton of the structure, but there were no **instances** of that structure. So, Assembly code is pretty simple.

c. To this C program, let us declare a **struct details student1** and see what the disassembly looks like.

    0000000000400546 <main>:
      400546:   55                      push   rbp
      400547:   48 89 e5                mov    rbp,rsp
      40054a:   48 83 ec 30             sub    rsp,0x30
      40054e:   64 48 8b 04 25 28 00    mov    rax,QWORD PTR fs:0x28
      400555:   00 00 
      400557:   48 89 45 f8             mov    QWORD PTR [rbp-0x8],rax
      40055b:   31 c0                   xor    eax,eax
      40055d:   b8 00 00 00 00          mov    eax,0x0
      400562:   48 8b 55 f8             mov    rdx,QWORD PTR [rbp-0x8]
      400566:   64 48 33 14 25 28 00    xor    rdx,QWORD PTR fs:0x28
      40056d:   00 00 
      40056f:   74 05                   je     400576 <main+0x30>
      400571:   e8 aa fe ff ff          call   400420 <__stack_chk_fail@plt>
      400576:   c9                      leave  
      400577:   c3                      ret    
    

d. Let us analyze it to understand better. For now, **ignore** instructions at addresses **0x40054e**, **0x400557** and **0x400571** . These require a bit of explanation which I will cover in the next post.

Analysis:

i. Construction of StackFrame:

        400546: 55                      push   rbp
        400547: 48 89 e5                mov    rbp,rsp
        40054a: 48 83 ec 30             sub    rsp,0x30
    

*   A StackFrame of size 0x30(48) bytes is constructed. 

ii. Next:

        40055b: 31 c0                   xor    eax,eax
        40055d: b8 00 00 00 00          mov    eax,0x0
    

*   **xor eax, eax** set eax to 0 and so does **mov eax, 0x0** . I don't know why the compiler has compiled these 2 instructions together. Something to think about. 

iii. End:

        400576: c9                      leave  
        400577: c3                      ret 
    

*   This will end the main function and return control to the caller function. 

In this example, we saw Stack space being allocated for the structure student1. If we had given **student1.name** a string and a number to **student1.rollno**, then we would have seen that code.

That is an exercise left to you .

With the 4 examples, I hope you have got some clarity on how programs are executed, how the compiler converts a C program into equivalent assembly code, how different types of variables are stored.

With this article, we know how C programs are converted to executables, what those executables contain, how does it look like in the memory when an executable is run and how our C programs are converted to assembly code and then executed.

Things you can do to understand the concepts better:

1.  You can write your own programs, disassemble it and understand the internals. As you also got introduced to gdb, you can run it and see all the registers and memory locations. There are many code constructs which we did not cover like if-else, if-else-if, switch, for(), do-while, union etc., Write programs and understand.

2.  We just used 4-5 gdb commands in this article. But, gdb is a Debugger which is very powerful. We will slowly unleash it's power as we move ahead.

And

A few things which were not covered properly:

1.  In every example, there were instructions related to printf() but I did not give much emphasis on them. This was done deliberately because it requires a few new concepts to understand function calls.

2.  Why bytes are stored in reverse order? (When we checked out the stack using x/ command).

3.  In the structure example, I asked you to ignore a few instructions. Even these require a few concepts to understand.

All 3 are important concepts and will be discussed in depth in the next article.

With this, I will end this article. I hope you enjoyed the article and learnt something out of it. Thank you!

****************************************************************
[Go to next post: Program Execution Internals - Part2](/reverse/engineering/and/binary/exploitation/series/2018/09/22/program-execution-internals-part-2.html)              
[Go to previous post: Memory Layout of a Process](/reverse/engineering/and/binary/exploitation/series/2018/08/18/memory-layout-of-a-process.html)
