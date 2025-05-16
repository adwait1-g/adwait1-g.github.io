---
layout: post
title: Program Execution Internals - Part2
categories: rebeseries
comments: true
---

Hey fellow pwners!

In the previous article, we understood how simple C code constructs are compiled into assembly, understood them. We used **gdb-peda** to dissect the examples we had taken up.

In this article, we will discuss one of the most interesting and important concepts in Program Execution Internals. We will be discussing **how a function call happens** in detail. You can think of this article as a landmark article because concepts explained here are the basics for the coming up posts. So, make sure you understand the things explained here clearly.

There were a few things which were deliberately not covered in detail. All those concepts will be explained in this article.

So far, most articles were explained using 64-bit Binaries. But in this article, we will look at **Function Call Mechanism** in both **32-bit** binaries and **64-bit** binaries because there are significant differences between the 2 mechanisms and it is important to know these differences.

This is article number **6** . So, create a directory named **post_6** in the **rev_eng_series** and store all the files related to this article there.

Let us start!

## Important concepts:

1.  **32-bit and 64-bit executables** : 

a. **32-bit executables** :

*   A 32-bit executable is prepared by the compiler to run on a 32-bit systems. Though it is made for 32-bit systems, we can run these on a few 64-bit systems also(Eg: Linux).

*   A 32-bit executable uses the **x86** architecture to generate the executable. So, in 32-bit Intel executables, the compiler will be using **eax**, **ebx**, **ecx**, **edx**, **esi**, **edi**, **esp**, **ebp**, **eip** and **eflags** . It cannot use any of the 64-bit registers because the 32-bit processors just don't have those 64-bit registers in them.

*   When we say, a 32-bit executable uses the x86 architecture, it is not only the registers we are talking about. We are talking about the instructions also. The compiler can use the instructions designed only for 32-bit processors and cannot use instructions designed for 64-bit processors.

b. **64-bit executables** :

*   A 64-bit executable is prepared by the compiler to run on 64-bit systems.

*   It is common sense that 64-bit executables cannot be run on 32-bit systems for a simple reason that 32-bit systems doesn't have those 64-bit registers. To generate 64-bit executables, the compiler can use rax, rbx......r14, 15.

*   In one of the older posts, we saw that a 64-bit register(Say rax) can broken down into it's 32-bit equivalent(eax), 16-bit equivalent(ax), 8-bit equivalent(al). So, as we are able to access these sub-registers of a big 64-bit register, the compiler can use these in a 64-bit executable. That is, Compiler can also use eax, ebx etc., (The 32-bit equivalent of those 64-bit registers) because eax is nothing but the first 32-bits of rax from right. Similarly, all 32-bit equivalents(eax, ebx...), 16-bit equivalents(ax, bx...), 8-bit equivalents(al, bl, ...) are also used.

I hope you have some clarity on what to look for when you see a 32-bit executable and a 64-bit executable. You will have a lot of clarity on this at the end of this article.

1.  **A note on esp, ebp, rsp, rbp** : 

a. **64-bit executables** :

*   When we were discussing about the registers, we had discussed that **rsp** and **rbp** have very specific purposes of managing the stack which we saw in detail in previous post. Note that **rsp** and **rbp** are **64-bit** registers.

*   We have discussed the memory layout of an executable. Let us focus on the Stack Memory of 64-bit processes. The Stack is the part of the whole memory used to store local variables, used for Function calls etc., In 64-bit processes, stack is a huge pile of memory given to us in chunks of **8 bytes** . Look at the following diagram:

![Stack Alignment 32 bit](/assets/2018-09-22-program-execution-internals-:-part-2/Stack_alignment1.png)

*   So, whenever we execute **push Reg1** , the following happens:
    
        sub rsp, 0x08
        mov qword[rsp], Reg64
        

*   Here, Reg64 can be anything. It can be any of the 64-bit registers, their 32-bit equivalents, 16-bit equivalents or 8-bit equivalents. They can also be memory locations. Irrespective of what it is, is is stored in that 8-byte chunk(Observe rsp being decremented by 8 bytes)

*   If you execute **pop Reg64**, the following happens:
    
        mov Reg64, qword[rsp]
        add rsp, 0x08
        

*   Here, the **pop** instruction loads whatever is present on top of the stack to Reg64. So, the top 8 bytes is loaded into Reg64 and StackPointer(rsp) is incremented by 8 bytes.

*   Note that both push and pop are operations on the top of the stack - which is 8-bytes wide. So, Reg1 has to be 8 bytes. **push rcx** is valid because the 8-byte value in rcx register is copied onto the stack whose width is also 8 bytes. If the instruction **push ecx** is executed in a 64-bit process, we definitely will get an error. Because ecx is 4-bytes but width of stack is 8 bytes in a 64-bit process.

*   So, it is important to note the width of the stack. **push** and **pop** operate on registers whose size is equal to the width of the stack. In 64-bit processes, the stack is 8-byte wide. So, the stack is said to have an **8-byte alignment** .

*   Consider the above diagram again:
    
    *   Suppose Value of rsp = 0. So, 8 bytes pointed by rsp are bytes **0 to 7**. **rsp+8** will be pointing to bytes **8 to 15**. **rsp+16** will be pointing to bytes **16 to 23**. **rsp+24** will be pointing to bytes **24 to 31**. Then there is **rbp** whose value is **rsp+32** . **rbp** / **rsp+32** points to bytes **32 to 39**. We have seen that in the middle of a function execution, **rbp** will point to **Old rbp** value. So, bytes 32-39 in the stack has the **Old rbp** value. This is not depicted in the picture, but I hope the understanding is clear. 

b. **32-bit executables** :

*   The whole concept is same, but here, the stack is **4-byte aligned** .

*   Let us go over the concept once again which will reinforce your understanding.

*   Consider the following diagram:

![Stack_Alignment_32_bit](/assets/2018-09-22-program-execution-internals-:-part-2/Stack_alignment2.png)

*   There is the stack, a huge piece of memory in the form of a rectangle given to us to store Local variables, take care of functions calls and more. For 32-bit systems, the **width** of that rectangle is **4-bytes** (32-bits).

*   When you **push Reg32**, the 4 bytes value in Reg32 is pushed onto the top 4-bytes of the stack. When you **pop Reg32**, the 4-bytes at the top of the stack is loaded into Reg32 and esp is incremented by 4 bytes.

Go over the concept once again. The practical execution which we do will help you clear the concepts.

# Program1

Let us consider the following example:

    ~/rev_eng_series/post_6$ cat code1.c
    #include<stdio.h>
    
    int add(int a, int b) {
    
        int x1, x2;
        x1 = a;
        x2 = b;
    
    return x1 + x2;
    }
    
    int main() {
    
    int x = 10, y = 20, sum = 0;
    
    sum = add(x, y);
    
    printf("x = %d, y = %d, sum = %d\n", x, y, sum);
    
    return 0;
    }
    

Overview of the program:

*   The program is straight forward. The main function has 3 local variables, x = 10, y = 20 and sum = 0. The **add** function takes in 2 arguments **x** and **y** and returns the **total** of the 2 numbers. That ReturnValue is stored in **sum** local variable.

*   The printf() function prints values of x, y and sum .

*   The **add** function has 2 local variables, **x1** and **x2** which are exact copies of the function's arguments **a** and **b** respectively. The function **add** then returns **x1 + x2**.

## Analysis of 32-bit Function Call Mechanism:

**NOTE**: To get a 32-bit executable,you should have a **32-bit libc** shared library.To install the 32-bit libc, execute the following instruction and you are ready to go!

    ~/rev_eng_series/post_6$ sudo apt-get install gcc-multilib 
    

**1**. Compiling **code1.c** to get a 32-bit executable **code1_32** .

    ~/rev_eng_series/post_6$ gcc code1.c -o code1_32 -m32
    

*   The **m32** option should be used to get a 32-bit binary. 

### Static Analysis of the executable!

*   Static Analysis is Analysis done without running the program. It can be using readelf, file, reading and understanding disassembly. 

**1**. Understanding the disassembly of **main** function:

    ~/rev_eng_series/post_6$ gdb -q code1_32
    Reading symbols from code1_32...(no debugging symbols found)...done.
    gdb-peda$ disass main
    Dump of assembler code for function main:
       0x08048427 <+0>: lea    ecx,[esp+0x4]
       0x0804842b <+4>: and    esp,0xfffffff0
       0x0804842e <+7>: push   DWORD PTR [ecx-0x4]
       0x08048431 <+10>:    push   ebp
       0x08048432 <+11>:    mov    ebp,esp
       0x08048434 <+13>:    push   ecx
       0x08048435 <+14>:    sub    esp,0x14
       0x08048438 <+17>:    mov    DWORD PTR [ebp-0x14],0xa
       0x0804843f <+24>:    mov    DWORD PTR [ebp-0x10],0x14
       0x08048446 <+31>:    mov    DWORD PTR [ebp-0xc],0x0
       0x0804844d <+38>:    push   DWORD PTR [ebp-0x10]
       0x08048450 <+41>:    push   DWORD PTR [ebp-0x14]
       0x08048453 <+44>:    call   0x804840b <add>
       0x08048458 <+49>:    add    esp,0x8
       0x0804845b <+52>:    mov    DWORD PTR [ebp-0xc],eax
       0x0804845e <+55>:    push   DWORD PTR [ebp-0xc]
       0x08048461 <+58>:    push   DWORD PTR [ebp-0x10]
       0x08048464 <+61>:    push   DWORD PTR [ebp-0x14]
       0x08048467 <+64>:    push   0x8048510
       0x0804846c <+69>:    call   0x80482e0 <printf@plt>
       0x08048471 <+74>:    add    esp,0x10
       0x08048474 <+77>:    mov    eax,0x0
       0x08048479 <+82>:    mov    ecx,DWORD PTR [ebp-0x4]
       0x0804847c <+85>:    leave  
       0x0804847d <+86>:    lea    esp,[ecx-0x4]
       0x08048480 <+89>:    ret    
    End of assembler dump.
    gdb-peda$ 
    

Starting from instruction **0x08048431 <+10>: push ebp**

**a**. Construction of StackFrame:

    0x08048431 <+10>:    push   ebp
    0x08048432 <+11>:    mov    ebp,esp
    0x08048434 <+13>:    push   ecx
    0x08048435 <+14>:    sub    esp,0x14
    

*   A StackFrame of size **0x14** (20) bytes is constructed.It is important to note that 20 is a multiple of 4 - which is the align value of stack memory in 32-bit processes. Let us look at the **push ecx** instruction when we run the program using gdb. 

**b**. Variables:

    0x08048438 <+17>:    mov    DWORD PTR [ebp-0x14],0xa
    0x0804843f <+24>:    mov    DWORD PTR [ebp-0x10],0x14
    0x08048446 <+31>:    mov    DWORD PTR [ebp-0xc],0x0 
    

*   At the memory location **ebp - 0x14**, **0xa** is stored. From the value being stored, we can deduce that this is variable **x** . 
*   Similarly, memory locations **ebp - 0x10** and **ebp - 0xc** are locations of variables **y** and **sum** respectively. 

**c**. Calling **add** function :

    0x0804844d <+38>:    push   DWORD PTR [ebp-0x10]
    0x08048450 <+41>:    push   DWORD PTR [ebp-0x14]
    0x08048453 <+44>:    call   0x804840b <add>
    

*   Here, 2 values are being pushed onto the stack and then **add** function is called. Notice that the 2 values are values at locations **ebp - 0x10** and **ebp - 0x14**, which are variables **x** and **y** respectively. Note that the add function had 2 arguments - **add(x, y)** . This is a very important observation.

**d** **0x08048458 <+49>: add esp,0x8** : This is a very important instruction. We saw that 2 4-byte values(totally 8 bytes) are pushed onto the stack before calling **add** and we identified them as arguments to **add** function. We know that if anything is pushed onto the stack, the **esp** is decremented by 4 bytes. That is, **sub esp, 0x4** is internally executed. As 2 things are pushed here, **sub esp, 0x4** is executed twice. So, the new value of esp = old_esp - 0x8. After the execution of **add**, those 2 4-byte values are still in the stack which we have to clean and make space for upcoming instructions. So, as counter to the 2 **sub esp, 0x4** instructions, one **add esp, 0x8** is executed. So, by adding **8** to the current **esp** value, **esp** will go back to the old value. We will run the program with gdb and everything we spoke here will be clear.

**e**. Storing back the return value of **add** function:

    0x0804845b <+52>:    mov    DWORD PTR [ebp-0xc],eax
    

*   We know that the return value of a function is stored in **eax** register. So, value in eax register is being copied to memory at location **ebp - 0xc** which is the **sum** variable. After this nstruction, **sum** variable has the sum of the 2 numbers. 

**f**. Calling **printf** function:

    0x0804845e <+55>:    push   DWORD PTR [ebp-0xc]
    0x08048461 <+58>:    push   DWORD PTR [ebp-0x10]
    0x08048464 <+61>:    push   DWORD PTR [ebp-0x14]
    0x08048467 <+64>:    push   0x8048510
    0x0804846c <+69>:    call   0x80482e0 <printf@plt>
    

*   4 values are being pushed and then **printf** is called. **ebp-0xc** is memory location of sum. **ebp-0x10** is memory location of **y** . **ebp-0x14** is the memory location of **x** . Then a **32-bit value = 0x8048510** is pushed. This is the printf() statement:
    
        printf("x = %d, y = %d, sum = %d\n", x, y, sum);
        

*   **IMPORTANT** :
    
    *   **sum** is the last argument passed to the printf(). But, it was the first to be pushed onto the stack. 
    *   **y** is the second argument from the last but was second to be pushed onto the stack. 
    *   **x** is the third argument from the last but was third to be pushed onto the stack. 
    *   The **Format String** - **x = %d, y = %d, sum = %d\n** is passed by reference. For that matter, any string is passed by reference, meaning it's memory location is passed as argument. So, **0x8048510** is the address of the format string, which is passed last. 

*   Notice the pattern: The last argument being pushed first. First argument being pushed last.

**g**. Ending the **main** function:

    0x08048474 <+77>:    mov    eax,0x0
    0x08048479 <+82>:    mov    ecx,DWORD PTR [ebp-0x4]
    0x0804847c <+85>:    leave  
    0x0804847d <+86>:    lea    esp,[ecx-0x4]
    0x08048480 <+89>:    ret   
    

*   Return value = 0 is loaded into eax, StackFrame is destructed and control is returned to caller. 

Now that we have understood the code, let us execute it and understand better.

### Dynamic Analysis:

Dynamic Analysis, as the name suggests running it and analyzing it. We will be doing Dynamic Analysis of this program with the help of gdb.

**3**. Executing the program with gdb:

As we have seen how local variables are stored in stack, now let us straight jump to the function call mechanism. First, let us see the **add** function call. Breaking at **0x0804844d** .

    $ gdb -q code1_32
    Reading symbols from code1_32...(no debugging symbols found)...done.
    gdb-peda$ b *0x0804844d
    Breakpoint 1 at 0x804844d
    gdb-peda$ 
    

*   Let us run!
*   Let us focus on the **code** and **stack** parts.
    
        [-------------------------------------code-------------------------------------]
           0x8048438 <main+17>: mov    DWORD PTR [ebp-0x14],0xa
           0x804843f <main+24>: mov    DWORD PTR [ebp-0x10],0x14
           0x8048446 <main+31>: mov    DWORD PTR [ebp-0xc],0x0
        => 0x804844d <main+38>: push   DWORD PTR [ebp-0x10]
           0x8048450 <main+41>: push   DWORD PTR [ebp-0x14]
           0x8048453 <main+44>: call   0x804840b <add>
           0x8048458 <main+49>: add    esp,0x8
           0x804845b <main+52>: mov    DWORD PTR [ebp-0xc],eax
        [------------------------------------stack-------------------------------------]
        0000| 0xffffccd0 --> 0x1 
        0004| 0xffffccd4 --> 0xa ('\n')
        0008| 0xffffccd8 --> 0x14 
        0012| 0xffffccdc --> 0x0 
        0016| 0xffffcce0 --> 0xf7fb03dc --> 0xf7fb11e0 --> 0x0 
        0020| 0xffffcce4 --> 0xffffcd00 --> 0x1 
        0024| 0xffffcce8 --> 0x0 
        0028| 0xffffccec --> 0xf7e16637 (<__libc_start_main+247>:   add    esp,0x10)
        [------------------------------------------------------------------------------]
        Legend: code, data, rodata, value
        
        Breakpoint 1, 0x0804844d in main ()
        gdb-peda$ 
        

*   We have stopped at the perfect instruction. The next instruction to be executed is **push DWORD PTR [ebp-0x10]** . Let us checkout the 4 bytes at location **ebp-0x10**.
    
        gdb-peda$ x/xw $ebp-0x10
        0xffffccd8: 0x00000014
        gdb-peda$ 
        

*   So, the value is **0x14** which is **20**. This is variable **y**. Notice that **y** was the **second** argument to **add** function (add(x, y)) but it is being pushed **first** .

*   Let us execute it using the **ni** instruction:
    
        [-------------------------------------code-------------------------------------]
           0x804843f <main+24>: mov    DWORD PTR [ebp-0x10],0x14
           0x8048446 <main+31>: mov    DWORD PTR [ebp-0xc],0x0
           0x804844d <main+38>: push   DWORD PTR [ebp-0x10]
        => 0x8048450 <main+41>: push   DWORD PTR [ebp-0x14]
           0x8048453 <main+44>: call   0x804840b <add>
           0x8048458 <main+49>: add    esp,0x8
           0x804845b <main+52>: mov    DWORD PTR [ebp-0xc],eax
           0x804845e <main+55>: push   DWORD PTR [ebp-0xc]
        [------------------------------------stack-------------------------------------]
        0000| 0xffffcccc --> 0x14 
        0004| 0xffffccd0 --> 0x1 
        0008| 0xffffccd4 --> 0xa ('\n')
        0012| 0xffffccd8 --> 0x14 
        0016| 0xffffccdc --> 0x0 
        0020| 0xffffcce0 --> 0xf7fb03dc --> 0xf7fb11e0 --> 0x0 
        0024| 0xffffcce4 --> 0xffffcd00 --> 0x1 
        0028| 0xffffcce8 --> 0x0 
        [------------------------------------------------------------------------------]
        Legend: code, data, rodata, value
        0x08048450 in main ()
        gdb-peda$ 
        

*   After execution of **push DWORD PTR [ebp-0x10]**, the above is the status. Observe the stack: **esp (Top of Stack) = 0xffffcccc** and points to **0x14** as expected. The **esp** value before this instruction got executed is **0xffffccd0** . Look at this: We pushed the value **0x14**. The **esp = 0xffffccd0 is decremented to esp = 0xffffcccc**. It has got decremented by 4 bytes as it is a 32-bit process. I hope you are able to see whatever we had discussed in the beginning of the article regarding stack, alignment and push instruction.

*   Moving on, let us execute the next instruction - **push DWORD PTR [ebp-0x14]** - which is variable **x** .
    
        [-------------------------------------code-------------------------------------]
           0x8048446 <main+31>: mov    DWORD PTR [ebp-0xc],0x0
           0x804844d <main+38>: push   DWORD PTR [ebp-0x10]
           0x8048450 <main+41>: push   DWORD PTR [ebp-0x14]
        => 0x8048453 <main+44>: call   0x804840b <add>
           0x8048458 <main+49>: add    esp,0x8
           0x804845b <main+52>: mov    DWORD PTR [ebp-0xc],eax
           0x804845e <main+55>: push   DWORD PTR [ebp-0xc]
           0x8048461 <main+58>: push   DWORD PTR [ebp-0x10]
        Guessed arguments:
        arg[0]: 0xa ('\n')
        arg[1]: 0x14 
        arg[2]: 0x1 
        arg[3]: 0xa ('\n')
        arg[4]: 0x14 
        [------------------------------------stack-------------------------------------]
        0000| 0xffffccc8 --> 0xa ('\n')
        0004| 0xffffcccc --> 0x14 
        0008| 0xffffccd0 --> 0x1 
        0012| 0xffffccd4 --> 0xa ('\n')
        0016| 0xffffccd8 --> 0x14 
        0020| 0xffffccdc --> 0x0 
        0024| 0xffffcce0 --> 0xf7fb03dc --> 0xf7fb11e0 --> 0x0 
        0028| 0xffffcce4 --> 0xffffcd00 --> 0x1 
        [------------------------------------------------------------------------------]
        Legend: code, data, rodata, value
        0x08048453 in main ()
        gdb-peda$ 
        

*   A similar procedure occurs. The value **0xa**(10) is pushed onto the stack. Notice this: gdb-peda is guessing the arguments passed to the **add** function and evidently, it's guess is wrong. We have only 2 arguments but it is showing arg[0] to arg[4] - which is 5 arguments=>wrong! . So, don't get mislead by a tool, look at the code by yourself and understand.

*   So, the 2 arguments of **add** function are pushed onto the stack. Notice that the top of the stack now is **esp = 0xffffccc8** and **value = 0xa** .

*   Now, let us get into **add** function. Use the **si** command / Step Instruction to execute it.
    
        gdb-peda$ si
        

*   Just entering **add**, but not executing any instructions:
    
        [-------------------------------------code-------------------------------------]
           0x8048402 <frame_dummy+34>:  add    esp,0x10
           0x8048405 <frame_dummy+37>:  leave  
           0x8048406 <frame_dummy+38>:  jmp    0x8048380 <register_tm_clones>
        => 0x804840b <add>: push   ebp
           0x804840c <add+1>:   mov    ebp,esp
           0x804840e <add+3>:   sub    esp,0x10
           0x8048411 <add+6>:   mov    eax,DWORD PTR [ebp+0x8]
           0x8048414 <add+9>:   mov    DWORD PTR [ebp-0x8],eax
        [------------------------------------stack-------------------------------------]
        0000| 0xffffccc4 --> 0x8048458 (<main+49>:  add    esp,0x8)
        0004| 0xffffccc8 --> 0xa ('\n')
        0008| 0xffffcccc --> 0x14 
        0012| 0xffffccd0 --> 0x1 
        0016| 0xffffccd4 --> 0xa ('\n')
        0020| 0xffffccd8 --> 0x14 
        0024| 0xffffccdc --> 0x0 
        0028| 0xffffcce0 --> 0xf7fb03dc --> 0xf7fb11e0 --> 0x0 
        [------------------------------------------------------------------------------]
        Legend: code, data, rodata, value
        0x0804840b in add ()
        

*   There are a few points to notice:
    
    *   Look at the stack now. We just jumped from **main** to **add** and not yet executed any instructions. But, the top of the stack has changed. It had **0xa** before **call** instruction, but now, it has something else - **0x8048458 (<main+49>: add esp,0x8)** . Let us check out what this instruction is.
    
    *   Look back into the **disassembly of main** .The instruction **0x8048458 (<main+49>: add esp,0x8)** is present just after **0x08048453 <+44>: call 0x804840b < add >** .
    
    *   So, after the **add** function is executed, the next instruction in the disassembly of main is **0x8048458 (<main+49>: add esp,0x8)** . So, after **add** is done executed, the **<main+49>** is the next instruction to be executed. The address **0x8048458** is the **Return Address** of **add** function. What we can understand from this is that, **call** instruction is made up of the following 2 instructions:
        
        push ReturnAddress jmp JumpAddress
    
    *   In this case, **ReturnAddress = 0x8048458** and **JumpAddress = 0x804840b** .
    
    *   Finally, the ReturnAddress of a function is pushed onto the stack by the **call** instruction before executing that function.

*   Let us make a note of the **ebp** value. It is **0xffffcce8**. So, **Old_ebp = 0xffffcce8** .

*   Let us skip the StackFrame Construction part. Let us break at **0x8048411 <add+6>: mov eax,DWORD PTR [ebp+0x8]** .
    
        gdb-peda$ b *0x8048411
        
    
    Breakpoint 2 at 0x8048411

*   You can use the **continue** gdb command to run **till** the next breakpoint. So, let us use it and stop at our BreakPoint2. The following is the current state:
    
        [-------------------------------------code-------------------------------------]
           0x804840b <add>: push   ebp
           0x804840c <add+1>:   mov    ebp,esp
           0x804840e <add+3>:   sub    esp,0x10
        => 0x8048411 <add+6>:   mov    eax,DWORD PTR [ebp+0x8]
           0x8048414 <add+9>:   mov    DWORD PTR [ebp-0x8],eax
           0x8048417 <add+12>:  mov    eax,DWORD PTR [ebp+0xc]
           0x804841a <add+15>:  mov    DWORD PTR [ebp-0x4],eax
           0x804841d <add+18>:  mov    edx,DWORD PTR [ebp-0x8]
        [------------------------------------stack-------------------------------------]
        0000| 0xffffccb0 --> 0x8000 
        0004| 0xffffccb4 --> 0xf7fb0000 --> 0x1b1db0 
        0008| 0xffffccb8 --> 0xf7fae244 --> 0xf7e16020 (call   0xf7f1db59)
        0012| 0xffffccbc --> 0xf7e160ec (test   eax,eax)
        0016| 0xffffccc0 --> 0xffffcce8 --> 0x0 
        0020| 0xffffccc4 --> 0x8048458 (<main+49>:  add    esp,0x8)
        0024| 0xffffccc8 --> 0xa ('\n')
        0028| 0xffffcccc --> 0x14 
        [------------------------------------------------------------------------------]
        Legend: code, data, rodata, value
        
        Breakpoint 2, 0x08048411 in add ()
        

*   Let us observe the **Stack** carefully. It is something like this:

![Stack_after_functioncall_32-bit](/assets/2018-09-22-program-execution-internals-:-part-2/Stack_after_functioncall_32-bit-1.png)

*   Let us understand the above diagram carefully:
    
    *   Space between **esp** and **ebp**(16 bytes) are for the function (add) to use. 
    *   \*ebp\** points to the **old ebp value**. 
    *   **ebp+4** points to the **ReturnAddress** . 
    *   **ebp+8** points to **Argument0(here, it is **0xa** or **x**) 
    *   **ebp+0xc** points to Argument1(here it is **0x14** or **y**)

*   Next instruction is **mov eax,DWORD PTR [ebp+0x8]**. We just saw that **ebp+8** points to Argument0 to a given function. This instruction is copying Argument0 into **eax** register. Let us see that happen.
    
        gdb-peda$ ni
        

*   And you will notice that **eax** now has the value **0xa** / 10.

*   The next few instructions are just moving stuff from and into memory. As we have already seen such instructions, let us skip those instructions and start inspecting from **0x08048423 <+24>: add eax,edx** . So, let us break there.
    
        gdb-peda$ b *0x08048423
        Breakpoint 3 at 0x8048423
        gdb-peda$ continue
        

*   The next 3 instructions are atmost important:
    
        0x8048423 <add+24>: add    eax,edx
        0x8048425 <add+26>: leave  
        0x8048426 <add+27>: ret    
        
    
    *   The **add eax, edx** instruction is computing the sum of **x** and **y** and the sum it is loaded back to **eax** because it is the **Return Value** . 

*   Let us go ahead and execute it. The following is the current state:
    
        [----------------------------------registers-----------------------------------]
        EAX: 0x1e 
        EBX: 0x0 
        ECX: 0xffffcd00 --> 0x1 
        EDX: 0xa ('\n')
        ESI: 0xf7fb0000 --> 0x1b1db0 
        EDI: 0xf7fb0000 --> 0x1b1db0 
        EBP: 0xffffccc0 --> 0xffffcce8 --> 0x0 
        ESP: 0xffffccb0 --> 0x8000 
        EIP: 0x8048425 (<add+26>:   leave)
        EFLAGS: 0x206 (carry PARITY adjust zero sign trap INTERRUPT direction overflow)
        [-------------------------------------code-------------------------------------]
           0x804841d <add+18>:  mov    edx,DWORD PTR [ebp-0x8]
           0x8048420 <add+21>:  mov    eax,DWORD PTR [ebp-0x4]
           0x8048423 <add+24>:  add    eax,edx
        => 0x8048425 <add+26>:  leave  
           0x8048426 <add+27>:  ret    
           0x8048427 <main>:    lea    ecx,[esp+0x4]
           0x804842b <main+4>:  and    esp,0xfffffff0
           0x804842e <main+7>:  push   DWORD PTR [ecx-0x4]
        [------------------------------------stack-------------------------------------]
        0000| 0xffffccb0 --> 0x8000 
        0004| 0xffffccb4 --> 0xf7fb0000 --> 0x1b1db0 
        0008| 0xffffccb8 --> 0xa ('\n')
        0012| 0xffffccbc --> 0x14 
        0016| 0xffffccc0 --> 0xffffcce8 --> 0x0 
        0020| 0xffffccc4 --> 0x8048458 (<main+49>:  add    esp,0x8)
        0024| 0xffffccc8 --> 0xa ('\n')
        0028| 0xffffcccc --> 0x14 
        [------------------------------------------------------------------------------]
        Legend: code, data, rodata, value
        0x08048425 in add ()
        gdb-peda$ 
        

*   A few important things to look at:
    
    *   Now, **eax** has **0x1e** which is **30** in decimal. So, it has the sum which is the Return Value of the function.
    
    *   Let us look at the stack again: The whole layout of the stack still remains the same. Let us look at the diagram once again:

![Stack_after_functioncall_32-bit](/assets/2018-09-22-program-execution-internals-:-part-2/Stack_after_functioncall_32-bit-1.png)

*   Except for the 2 values inside StackFrame of **add**(which we don't care about because a function can do whatever it wants inside it's StackFrame - Private:P), the layout remains the same.

*   Now the important **leave** instruction: Let us execute it and see what happens:
    
        [----------------------------------registers-----------------------------------]
        EAX: 0x1e 
        EBX: 0x0 
        ECX: 0xffffcd00 --> 0x1 
        EDX: 0xa ('\n')
        ESI: 0xf7fb0000 --> 0x1b1db0 
        EDI: 0xf7fb0000 --> 0x1b1db0 
        EBP: 0xffffcce8 --> 0x0 
        ESP: 0xffffccc4 --> 0x8048458 (<main+49>:   add    esp,0x8)
        EIP: 0x8048426 (<add+27>:   ret)
        EFLAGS: 0x206 (carry PARITY adjust zero sign trap INTERRUPT direction overflow)
        [-------------------------------------code-------------------------------------]
           0x8048420 <add+21>:  mov    eax,DWORD PTR [ebp-0x4]
           0x8048423 <add+24>:  add    eax,edx
           0x8048425 <add+26>:  leave  
        => 0x8048426 <add+27>:  ret    
           0x8048427 <main>:    lea    ecx,[esp+0x4]
           0x804842b <main+4>:  and    esp,0xfffffff0
           0x804842e <main+7>:  push   DWORD PTR [ecx-0x4]
           0x8048431 <main+10>: push   ebp
        [------------------------------------stack-------------------------------------]
        0000| 0xffffccc4 --> 0x8048458 (<main+49>:  add    esp,0x8)
        0004| 0xffffccc8 --> 0xa ('\n')
        0008| 0xffffcccc --> 0x14 
        0012| 0xffffccd0 --> 0x1 
        0016| 0xffffccd4 --> 0xa ('\n')
        0020| 0xffffccd8 --> 0x14 
        0024| 0xffffccdc --> 0x0 
        0028| 0xffffcce0 --> 0xf7fb03dc --> 0xf7fb11e0 --> 0x0 
        [------------------------------------------------------------------------------]
        Legend: code, data, rodata, value
        0x08048426 in add ()
        gdb-peda$ 
        

*   Wow!, the stack has changed a lot. We are able to see that the **ReturnAddress** is on top of the stack. But, what happened to all of the other stuff?? Let's see!

*   The StackFrame of **add** function is no more. Is has got destructed. There is no **old ebp** anymore on the stack. So, it has been **popped** out of the stack. Let us look at the **ebp** register. It is **0xffffcce8** which is the **old ebp** value. So, it is safe to say that, after destruction of StackFrame, **pop ebp** was executed. From the observations made, we can say that **leave** is not a single instruction. It is a combination of instructions because it is doing more than one thing. Let us see what **leave** is:
    
    *   First, destruction of StackFrame is done by **mov esp, ebp** instruction. The **gap** / **space** between the StackPointer and **BasePointer** is made **0**.
    
    *   Then popping **old ebp** value into **ebp** register.
    
    *   From these, we can say **leave** essentially is:
        
            mov esp, ebp 
            pop ebp
            

*   Now, the last step. Returning back to the caller function. Note that the **ReturnAddress** is at the top of the stack. So, the function has to just do a **jmp** to that Address and it will be done.

*   After executing **ret**, this is the state:
    
        [-------------------------------------code-------------------------------------]
           0x804844d <main+38>: push   DWORD PTR [ebp-0x10]
           0x8048450 <main+41>: push   DWORD PTR [ebp-0x14]
           0x8048453 <main+44>: call   0x804840b <add>
        => 0x8048458 <main+49>: add    esp,0x8
           0x804845b <main+52>: mov    DWORD PTR [ebp-0xc],eax
           0x804845e <main+55>: push   DWORD PTR [ebp-0xc]
           0x8048461 <main+58>: push   DWORD PTR [ebp-0x10]
           0x8048464 <main+61>: push   DWORD PTR [ebp-0x14]
        [------------------------------------stack-------------------------------------]
        0000| 0xffffccc8 --> 0xa ('\n')
        0004| 0xffffcccc --> 0x14 
        0008| 0xffffccd0 --> 0x1 
        0012| 0xffffccd4 --> 0xa ('\n')
        0016| 0xffffccd8 --> 0x14 
        0020| 0xffffccdc --> 0x0 
        0024| 0xffffcce0 --> 0xf7fb03dc --> 0xf7fb11e0 --> 0x0 
        0028| 0xffffcce4 --> 0xffffcd00 --> 0x1 
        [------------------------------------------------------------------------------]
        Legend: code, data, rodata, value
        0x08048458 in main ()
        gdb-peda$ 
        

*   Look at the stack. There is no ReturnAddress also. So, we can look at **ret** instruction like this:
    
        pop Reg
        jmp Reg
        

*   So, the ReturnAddress is popped into **Reg** and then jump to the Address in **Reg**.

Now, we have completed the anslysis of Function Call Mechanism in a 32-bit process.

That was a lot of stuff. So, let us summarize everything:

1.  Caller function pushes arguments of callee function onto stack in this manner - **Last Argument is pushed First** . 
2.  After all arguments, the **call** instruction is executed. It pushes the **ReturnAddress** of the callee function and then jumps to the function. 
3.  The First instruction of a function is to store **old ebp** by pushing it onto the stack. 
4.  A StackFrame of appropriate size is constructed and function execution takes place. 
5.  The arguments are accessed in this manner(Suppose there are n arguments)
    
        Argument0 - ebp+8
        Argument1 - ebp+12
        Argument2 - ebp+16
        .
        .
        .
        ArgumentN-1 - ebp + 8 + 4 * (n-1)
        

6.  Any ArgumentX (assuming it starts from Argument0) is accessed like this:
    
        ArgumentX - ebp + 8 + 4 * (X-1)
        

7.  After the function execution, the **leave** instruction Destructs the StackFrame and restores the **old ebp** value by popping the stack into **ebp** .

8.  Finally, the **ret** instruction is executed where the **we jump to the Address present at the top of the stack** .

9.  **IMPORTANT** : Notice how the stack looks like after returning back to the caller function. It looks as if there was no function call, as if nothing happened. I hope you are able to appreciate this beautiful mechanism.

Notice the use of stack here. It is tremendous. We are using it to

*   Pass arguments to a function
*   To call and ret (pushing and popping ReturnAddress) - Basically , stack plays a key role in Function Call Mechanism. 
*   Local Variables of a function - which we have spoken about in good detail. 

This was a complete analysis of Function Calling Mechanism in 32-bit processes. Please go through the above section again, understand every bit properly because this the foundation of the future posts.

To reinforce our understanding, let us continue and see how that **printf** gets executed.

*   Consder the following instructions:
    
        0x804845e <main+55>:    push   DWORD PTR [ebp-0xc]
        0x8048461 <main+58>:    push   DWORD PTR [ebp-0x10]
        0x8048464 <main+61>:    push   DWORD PTR [ebp-0x14]
        0x8048467 <main+64>:    push   0x8048510
        0x804846c <main+69>:    call   0x80482e0 <printf@plt>
        

*   The **push DWORD PTR [ebp-0xc]** pushes the value in **sum** variable onto the stack. Notice that **sum** is the last argument of that printf() statement.

*   The **push DWORD PTR [ebp-0x10]** pushes the value in **y** variable onto the stack.

*   The **push DWORD PTR [ebp-0x14]** pushes the value in **x** variable onto the stack.

*   I hope you are able to make sense of what is happenning here.

*   Let us look at the next instruction. It is wierd. Some value **0x8048510** is being pushed onto the stack. Let us look at this instruction running and checkout what that value is. Let us break at **0x8048467** .
    
        gdb-peda$ b *0x8048467
        Breakpoint 4 at 0x8048467
        gdb-peda$ 
        

*   Look at this:
    
        gdb-peda$ x/s 0x8048510
        0x8048510:  "x = %d, y = %d, sum = %d\n"
        gdb-peda$ 
        

*   The **s** in x/s command prints the string at the specified address.

*   Note that **0x8048510** is the Address of the Format String **"x = %d, y = %d, sum = %d\n"**.

*   This is the meaning of **Passing by Reference** . Here, you are not passing the String itself. You are just passing it's Address / Reference which is actually easier. Because an Address is fixed in size - 4 bytes in a 32-bit executable. It is easier to handle that passing some string whose length we have to calculate - too much work :P

*   This is what the stack looks like after pushing all arguments onto the stack:
    
        [------------------------------------stack-------------------------------------]
        0000| 0xffffccc0 --> 0x8048510 ("x = %d, y = %d, sum = %d\n")
        0004| 0xffffccc4 --> 0xa ('\n')
        0008| 0xffffccc8 --> 0x14 
        0012| 0xffffcccc --> 0x1e 
        0016| 0xffffccd0 --> 0x1 
        0020| 0xffffccd4 --> 0xa ('\n')
        0024| 0xffffccd8 --> 0x14 
        0028| 0xffffccdc --> 0x1e 
        

*   And then printf() is called. That is actually an entirely different topic because printf() is a Standard Library function, it is **Dynamically Linked**. Let us talk about it in one of the later posts. Now, let us restrict ourselves to basics of Function Call Mechanism.

*   I hope you are able to make sense of the concepts we discussed so far.

Now that we are familiar with 32-bit Calling Mechanism, Let us race through the 64-bit mechanism.

### Analysis of 64-bit Function Call Mechanism:

**1**. First, compile **code1.c** normally to get **code1** executable. The reason to compile an executable normally and not with **-g** though it helps debugging is that real software is never compiled with **-g** option. So, practising debugging and figuring the variables etc., without debugging symbols is a good thing.

        ~/rev_eng_series/post_6$ gcc code1.c -o code1
    

**2**. Let us start our analysis and look at the disassembly of **main** first:

        ~/rev_eng_series/post_6$ gdb -q code1
        Reading symbols from code1...(no debugging symbols found)...done.
        gdb-peda$ disass main
        Dump of assembler code for function main:
           0x0000000000400546 <+0>: push   rbp
           0x0000000000400547 <+1>: mov    rbp,rsp
           0x000000000040054a <+4>: sub    rsp,0x10
           0x000000000040054e <+8>: mov    DWORD PTR [rbp-0xc],0xa
           0x0000000000400555 <+15>:    mov    DWORD PTR [rbp-0x8],0x14
           0x000000000040055c <+22>:    mov    DWORD PTR [rbp-0x4],0x0
           0x0000000000400563 <+29>:    mov    edx,DWORD PTR [rbp-0x8]
           0x0000000000400566 <+32>:    mov    eax,DWORD PTR [rbp-0xc]
           0x0000000000400569 <+35>:    mov    esi,edx
           0x000000000040056b <+37>:    mov    edi,eax
           0x000000000040056d <+39>:    call   0x400526 <add>
           0x0000000000400572 <+44>:    mov    DWORD PTR [rbp-0x4],eax
           0x0000000000400575 <+47>:    mov    ecx,DWORD PTR [rbp-0x4]
           0x0000000000400578 <+50>:    mov    edx,DWORD PTR [rbp-0x8]
           0x000000000040057b <+53>:    mov    eax,DWORD PTR [rbp-0xc]
           0x000000000040057e <+56>:    mov    esi,eax
           0x0000000000400580 <+58>:    mov    edi,0x400624
           0x0000000000400585 <+63>:    mov    eax,0x0
           0x000000000040058a <+68>:    call   0x400400 <printf@plt>
           0x000000000040058f <+73>:    mov    eax,0x0
           0x0000000000400594 <+78>:    leave  
           0x0000000000400595 <+79>:    ret    
        End of assembler dump.
        gdb-peda$ 
    

1.  As we have StackFrame Construction and StackFrame Destruction many times and are familiar with it, let us just focus on how **Arguments are passed** and Function Call & ret Mechanism. 

*   Passing Arguments to **add** function:
    
        0x0000000000400569 <+35>:    mov    esi,edx
        0x000000000040056b <+37>:    mov    edi,eax
        0x000000000040056d <+39>:    call   0x400526 <add>
        

*   Initially, **eax has 0xa - Argument0** and **edx has 0x14 - Argument1** - You can check that out by executing those instructions. Later, **mov esi, edx** is executed. So, now **esi has Argument1** . Similarly after executing **mov edi,eax**, **edi has Argument0** .

*   Passing Arguments to **printf** function:
    
        0x400575 <main+47>: mov    ecx,DWORD PTR [rbp-0x4]
        0x400578 <main+50>: mov    edx,DWORD PTR [rbp-0x8]
        0x40057b <main+53>: mov    eax,DWORD PTR [rbp-0xc]
        0x40057e <main+56>: mov    esi,eax
        0x400580 <main+58>: mov    edi,0x400624
        0x400585 <main+63>: mov    eax,0x0
        0x40058a <main+68>: call   0x400400 <printf@plt>
        

*   **edi**(Or rdi) has the Address **0x400624** which is the Address of the Format String - Argument0

*   **esi**(Or rsi) has **x** - Argument1

*   **edx**(Or rdx) has **y** - Argument2

*   **ecx**(Or rcx) has **sum** - Argument3

*   What is happening? 32-bit calling convention used stack - so simple. But What is happening here??
    
    *   There is a **Function Calling Convention** defined for 64-bit Linux Systems. The convention goes like this:
    
    *   The first 6 arguments(Argument 0 - 5) go into **rdi, rsi, rdx, rcx, r8, r9** registers. If there are any more arguments, they will pushed onto the stack.

*   Here, as there are 4 arguments, the stack is not being used. We are just using **rdi, rsi, rdx, rcx** and calling the function.

*   Note that **Calling a Function**, **Storing Local Variables**, **Returning back**, **Return Value of a function** are all the same.

*   The only difference is the way Arguments are passed and the way they are used in the callee function. The Argument0 goes into **rdi** register. So, the callee function will look at **rdi** for Argument0. It will not look at **ebp+8** because the first 6 arguments in 64-bit Linux executables are passed with the help of registers. Only if there are more than 6 arguments, stack is used.

*   I want you guys to analyze and verify this convention properly performing proper Dynamic Analysis on the 64-bit version using gdb.

*   The best way to get familar with these 2 conventions is to write small programs, functions and look at their disassembly, run it using gdb and play around with it.

*   Also verify that in 64-bit, if number of arguments are more that 6, the first 6 will be passed using registers, the rest will be passed using the stack.

If you have made it till here, then you are just amazing!

### A few important things!

**1**. This diagram will summarize the Function Call Mechanism:

 ![Stack construction and destruction][1]

*   This doesn't show how arguments are passed. It describes only Call and Ret mechanism. I have used 64-bit registers here, but it can be extended for 32-bit also.

*   One thing I want to point out is that look at the first Stack Layout and the last Stack Layout - they are one below the other. You will find no difference between them. It is as if a function call never happened. I am sorry I have repeated this multiple times, but I just feel it is so beautiful!

**2**. We just saw **how** function calls happen. We never really spoke about **why** the function call mechanisms are designed like this? Why is there those differences between 32-bit and 64-bit calling mechanisms? Let us understand everything one by one.

*   What we just analysed and understood is the 32-bit and 64-bit Function calling mechanisms specific to *NIX Systems. They are conventions designed in a very simple and probably most efficient manner.

*   The Convention is known as **Application Binary Interface** - **ABI** . Do not confuse this with Application Programming Interface - API. They are different.

*   An ABI for a system specifies all the rules to be followed when a particular binary is generated.

Let us take the example of 32-bit Intel Linux Binaries:

*   The 32-bit Intel ABI for Linux binaries says that Arguments have to be passed using stack, Return Address has to be stored in Stack, etc., 

Consider ABI of 64-bit Intel *NIX Binaries:

*   The first 6 arguments are passed to rdi, rsi, rdx, rcx, r8, r9 and rest of the argument if any should be passed via stack. One of the ABI conventions all 64-bit Linux Compilers follow. 

Let us have a look at ABI of 64-bit Intel Windows Binaries:

*   Even this specifies that first 4 arguments be passed via registers and register order is rcx, rdx, r8 and r9 and rest of the arguments via stack. 

You can note that the conventions are different.

*   It is important to understand that the underlying processor is the same. If we consider the 64-bit Intel processor, it is the same. But the programs are generated according to the ABI(not the Operating System). All *NIX systems like Linux, FreeBSD, OpenBSD etc., follow the same ABI.

*   Also, we have probably seen 3-4 mechanisms presented in the SystemV x64 ABI(ABI for all *NIX Intel systems).There are a lot of details in an ABI. Take a look at this [document][2]. This document is the SystemV x64 ABI.

*   The compiler we are using should know this ABI. We use gcc for Intel processors. So, it will know the ABI to be used to get the proper executable.

*   Suppose you didn't like the current ABI. You can definitely write an ABI of your own. In that case, we have to make sure that all the Shared Libraries the program uses(libc, dynamic linker etc., ) also abides by the new ABI. If we just compile the program using the new ABI, but the libc is still following the SystemV ABI, the program mostly will crash.

Eg: The normal Linux ABI says that the ReturnValue of a function is to be stored in **rax** / **eax** register. Suppose your ABI says you want to store it in stack(Just an example), that would be a problem. These ABIs are made to follow some uniformity in the executables we generate. Suppose I generate an executable in my Linux-64bit system. I should be able to run it on a FreeBSD-64bit system because they both follow the same ABI. I hope you are getting an idea of what ABI is.

*   Coming back to our question, why are the function mechanisms like this? Because we all follow the ABI and ABI is the standard which we have to follow. Why do we have to follow ABI? We follow ABI because it is a bunch of conventions and algorithms provided by researchers after confirming and testing they are the best ones to use (Safety and Performance). If you want to see the elegance and simplicity of SystemV ABI, just look at the 32-bit function call mechanism. It is so simple and so beautifully designed! 

1.  Why do we even have the concept of Stack Alignment? 

Ans: Checkout [this][3] stackoverflow answer. There is amazing explanation of why we need stack alignment.

With this, I would like to end this article. A lot was discussed in this article. We looked at how Functions are called in 32-bit and 64-bit Intel Linux programs. We got to know what ABI is.

I totally enjoyed writing this post. I hope you learnt something out of it.

Thank you!

* * *

PS: I made those Stack Diagrams using this website [sketch.io][4] . Check it out!

[Go to next post: Buffer Overflow Vulnerability - Part1](/reverse/engineering/and/binary/exploitation/series/2018/10/02/buffer-overflow-vulnerability-01.html)               
[Go to previous post: Program Execution Internals - Part1](/reverse/engineering/and/binary/exploitation/series/2018/09/10/program-execution-internals-part-1.html)






 [1]: /assets/2018-09-22-program-execution-internals-:-part-2/stackframe_construction_and_destruction.jpg
 [2]: https://www.uclibc.org/docs/psABI-x86_64.pdf
 [3]: https://stackoverflow.com/questions/672461/what-is-stack-alignment
 [4]: https://sketch.io/sketchpad
