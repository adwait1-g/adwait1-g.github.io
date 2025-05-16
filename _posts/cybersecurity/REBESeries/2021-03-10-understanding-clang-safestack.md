---
layout: post
title: Understanding clang's SafeStack
categories: rebeseries
comments: true
---

Hello everyone!

In this post, we will be exploring one of clang's interesting security features - the [SafeStack](https://clang.llvm.org/docs/SafeStack.html). Idea is to go over the documentation page, get an idea and take a few examples to understand it better.

# 1. Introduction

Normally, the function stack is where all the local variables, caller's base pointer and return address are stored. The local variables can contain anything: Buffers, structures, primitive variables, function pointers etc., Which of these variables are being safely accessed? Accessing which of these variables are causing some sort of memory problem? Let us take an example to understand these questions better. Consider **prog1.c**.

```c
cpi-safestack$ cat prog1.c
#include <stdio.h>
int main()
{
	long int x = 10;
	long int arr[100] = {0};
	
	x = 123;
	arr[93] = 12345;

	printf("arr[93]: (%p, 0x%lx), x: (%p, 0x%lx)\n", arr+93, arr[93], &x, x);

	return 0;
}
```

It initializes 2 objects - a primitive variable ```x``` and an array ```arr```. It also accesses them and changes some value.

Note that these memory accesses are safe. You can **prove** that these accesses are safe. Instead of accessing the element at index 93, let us ask the user **where** and **what** to write.

```c
cpi-safestack$ cat prog2.c
#include <stdio.h>
int main()
{
	long int x = 10, n = 0;
	long int arr[100] = {0};
	
	x = 123;

	printf("Enter n: ");
	scanf("%ld", &n);

	printf("Enter value: ");
	scanf("%ld", &arr[n]);

	printf("arr[%ld]: (%p, 0x%lx), x: (%p, 0x%lx)\n", n, arr+n, arr[n], &x, x);

	return 0;
}
```

In this program, there is no way to prove that all memory accesses in this program are safe. For the array accesses, only n=0-99 are safe. Any 'n' apart from that results in illegal memory access and ideally should not be allowed in the program. Such accesses can result in undefined behavior which is not desirable. Let us compile this program and run it a couple of times - with illegal indices.

```
cpi-safestack$ clang-12 prog2.c -o prog2 -g

cpi-safestack$ ./prog2
Enter n: 100
Enter value: 123
arr[100]: (0x7ffe2be737f0, 0x7b), x: (0x7ffe2be73800, 0x7b)

cpi-safestack$ ./prog2
Enter n: 101
Enter value: 124
arr[124]: (0x7ffe46defdf0, 0x0), x: (0x7ffe46defd40, 0x7b)

cpi-safestack$ ./prog2
Enter n: 102
Enter value: 125
arr[102]: (0x7ffd6e9f3540, 0x7d), x: (0x7ffd6e9f3540, 0x7d)

cpi-safestack$ ./prog2
Enter n: 103
Enter value: 126
arr[103]: (0x7ffda5871e98, 0x7e), x: (0x7ffda5871e90, 0x7b)

cpi-safestack$ ./prog2
Enter n: 104
Enter value: 127
arr[104]: (0x7ffd03424510, 0x7f), x: (0x7ffd03424500, 0x7b)

cpi-safestack$ ./prog2
Enter n: 105 1218
Enter value: arr[105]: (0x7ffcc476e3d8, 0x4c2), x: (0x7ffcc476e3c0, 0x7b)
Segmentation fault (core dumped)

cpi-safestack$ ./prog2
Enter n: 105
Enter value: 128
arr[105]: (0x7fff893cea18, 0x80), x: (0x7fff893cea00, 0x7b)
Segmentation fault (core dumped)

cpi-safestack$ ./prog2
Enter n: 106
Enter value: 129
arr[106]: (0x7ffeef1f1c30, 0x81), x: (0x7ffeef1f1c10, 0x7b)

cpi-safestack$ ./prog2
Enter n: 107
Enter value: 130
arr[107]: (0x7ffff4423bc8, 0x82), x: (0x7ffff4423ba0, 0x7b)
```

Slowly observe the values index of ```arr```, the value of ```x``` for each run. For n=101, the index is somehow 124 (although we know that it is 101). ```arr[101]``` is printed to be 0 (although we entered 124). For n=102, the value of ```x``` also turned 125(0x7d) (but its actual value is 123(0x7b)). Finally for n=105, the program crashed peacefully.

This is the typical definition of undefined behavior. Let us see why this happened. Reading through the program's objdump will tell us how its stack-frame looks like.
```
<arr - 100 * 8 bytes><padding - 8 bytes>< n = 0, 8 bytes><x = 10/123 8 bytes><padding><return-address>
```

This is a rough diagram, not to scale. because ```arr``` is a ```long int``` array, ```arr[101]``` gave us ```n```'s memory location, ```arr[102]``` gave us ```x```'s memory location. We kept moving right, we landed on the stack location where the return-address is stored.

Worse, the user can overwrite the return-address with any value he likes and can **hijack** the **control-flow** of the program.

Premise is that there is lot of C/C++ code out there which has bugs like these. Ideal way is to fix all of them, but that is not possible. So it is better to have exploit mitigation methods - mechanisms to protect against these attacks in the presence of such vulnerabilities. Control-Flow Hijacking is a problem the community is tackling from early 1990s. Exploit methods have changed (Code Injection, Return2Libc, ROP, JOP etc.,) but the root cause is the same - Control-Flow Hijacking. If there is a way to prevent Control-Flow Hijacking from happening, then none of these attacks would work.

Enter SafeStack.

# 2. What is SafeStack?

[SafeStack](https://clang.llvm.org/docs/SafeStack.html) is a compiler-based protection mechanism against Control-Flow Hijacking. A function can have different types of variables: Primitive variables(int, char, float, double and family), arrays, structures, function-pointers etc., Different types of actions can be taken on each type of variable. We can read from it, write into it, get its address, iterate through it(if it is an array), access a structure's variables, call functions (using function-pointers) and more. Is a memory-access safe during such actions? Are we writing into a valid memory location?(hasn't it been freed before?), are we freeing an already freed up object? Are we iterating an array beyond its size? Are we copying data larger than the buffer's length?

Control-Flow Hijacking happens when there is an oppurtunity for a function-pointer to be overwritten - in that sense, the return-address is also a function pointer. We can put all such objects which need protection into one place. All the other memory objects can be placed someplace else (away from the protected objects). This way, even if a buffer in the unprotected area is overrun, nothing happens to our protected objects (the function pointers, return-address are safe and sound).

This solution focuses specifically on the **objects present in the stack**. All local variables, caller's base pointer, return-address are put into a function's stack-frame in C/C++. In a particular function, are all the memory-accesses to a particular object safe? Can we prove it? If we can prove it, put that object into something called **safe-stack**. If we cannot prove it, put it into another stack (which is called **unsafe-stack**). The two stacks are present in entirely different memory locations (they are not next to each other).

Let us apply the above concept to our **prog2.c** program and see what happens. There are 3 objects: ```x```, ```n``` and ```arr```. Accesses to ```x``` and ```n``` can be proven to be safe. But the same cannot be proven for ```arr``` - it might end in illegal memory access and we demonstrated it. We also showed that this vulnerability can be used to overwrite the return-address with the user's choice. So what we now do is we place ```x```, ```n```, return-address in the safe-stack. We place the array ```arr``` in the unsafe-stack. Because the two stacks are no way close to each other, even if some memory is illegally accessed using ```arr```, the return-address cannot be modified. Idea is that accesses to objects in the unsafe-stack will not affect objects and content in the safe-stack.

How do these two stacks look like in memory? What happens to our traditional runtime stack? Let us look at all these details in the next section.

# 3. SafeStack: Practical example

Before going ahead and compiling **prog2.c** with SafeStack, let us take a look at ```main```'s disassembly when compiled without it.

```asm
 344 00000000004005b0 <main>:                                                        
 345   4005b0:   55                      push   rbp                                  
 346   4005b1:   48 89 e5                mov    rbp,rsp                              
 347   4005b4:   48 81 ec 40 03 00 00    sub    rsp,0x340                            
 348   4005bb:   c7 45 fc 00 00 00 00    mov    DWORD PTR [rbp-0x4],0x0              
 349   4005c2:   48 c7 45 f0 0a 00 00    mov    QWORD PTR [rbp-0x10],0xa             
 350   4005c9:   00                                                                  
 351   4005ca:   48 c7 45 e8 00 00 00    mov    QWORD PTR [rbp-0x18],0x0             
 352   4005d1:   00                                                                  
 353   4005d2:   48 8d bd c0 fc ff ff    lea    rdi,[rbp-0x340]                      
 354   4005d9:   31 f6                   xor    esi,esi                              
 355   4005db:   ba 20 03 00 00          mov    edx,0x320                            
 356   4005e0:   e8 bb fe ff ff          call   4004a0 <memset@plt>                  
 357   4005e5:   48 c7 45 f0 7b 00 00    mov    QWORD PTR [rbp-0x10],0x7b            
 358   4005ec:   00                                                                  
 359   4005ed:   48 bf 14 07 40 00 00    movabs rdi,0x400714                         
 360   4005f4:   00 00 00                                                            
 361   4005f7:   b0 00                   mov    al,0x0                               
 362   4005f9:   e8 92 fe ff ff          call   400490 <printf@plt>                  
 363   4005fe:   48 bf 1e 07 40 00 00    movabs rdi,0x40071e                         
 364   400605:   00 00 00                                                            
 365   400608:   48 8d 75 e8             lea    rsi,[rbp-0x18]                       
 366   40060c:   b0 00                   mov    al,0x0                               
 367   40060e:   e8 9d fe ff ff          call   4004b0 <__isoc99_scanf@plt>          
 368   400613:   48 bf 22 07 40 00 00    movabs rdi,0x400722                         
 369   40061a:   00 00 00                                                            
 370   40061d:   b0 00                   mov    al,0x0                               
 371   40061f:   e8 6c fe ff ff          call   400490 <printf@plt>                  
 372   400624:   48 8b 45 e8             mov    rax,QWORD PTR [rbp-0x18]             
 373   400628:   48 8d b5 c0 fc ff ff    lea    rsi,[rbp-0x340]                      
 374   40062f:   48 c1 e0 03             shl    rax,0x3                              
 375   400633:   48 01 c6                add    rsi,rax                              
 376   400636:   48 bf 1e 07 40 00 00    movabs rdi,0x40071e
 377   40063d:   00 00 00                                                            
 378   400640:   b0 00                   mov    al,0x0                               
 379   400642:   e8 69 fe ff ff          call   4004b0 <__isoc99_scanf@plt>          
 380   400647:   48 8b 75 e8             mov    rsi,QWORD PTR [rbp-0x18]             
 381   40064b:   48 8d 95 c0 fc ff ff    lea    rdx,[rbp-0x340]                      
 382   400652:   48 8b 45 e8             mov    rax,QWORD PTR [rbp-0x18]             
 383   400656:   48 c1 e0 03             shl    rax,0x3                              
 384   40065a:   48 01 c2                add    rdx,rax                              
 385   40065d:   48 8b 45 e8             mov    rax,QWORD PTR [rbp-0x18]             
 386   400661:   48 8b 8c c5 c0 fc ff    mov    rcx,QWORD PTR [rbp+rax*8-0x340]      
 387   400668:   ff                                                                  
 388   400669:   4c 8b 4d f0             mov    r9,QWORD PTR [rbp-0x10]              
 389   40066d:   48 bf 30 07 40 00 00    movabs rdi,0x400730                         
 390   400674:   00 00 00                                                            
 391   400677:   4c 8d 45 f0             lea    r8,[rbp-0x10]                        
 392   40067b:   b0 00                   mov    al,0x0                               
 393   40067d:   e8 0e fe ff ff          call   400490 <printf@plt>                  
 394   400682:   31 c0                   xor    eax,eax                              
 395   400684:   48 81 c4 40 03 00 00    add    rsp,0x340                            
 396   40068b:   5d                      pop    rbp                                  
 397   40068c:   c3                      ret
```

Note the huge stack-frame being created in the prologue.

```asm
 345   4005b0:   55                      push   rbp                                  
 346   4005b1:   48 89 e5                mov    rbp,rsp                              
 347   4005b4:   48 81 ec 40 03 00 00    sub    rsp,0x340
```

The total-size is 0x340 / 832 bytes.

In the next few lines, it becomes clear that all the variables are present in the stack-frame.

```asm
 349   4005c2:   48 c7 45 f0 0a 00 00    mov    QWORD PTR [rbp-0x10],0xa    # x = 10        
 350   4005c9:   00                                                                  
 351   4005ca:   48 c7 45 e8 00 00 00    mov    QWORD PTR [rbp-0x18],0x0	# n = 0             
 352   4005d1:   00                                                                  
 353   4005d2:   48 8d bd c0 fc ff ff    lea    rdi,[rbp-0x340]   			# arr[100]                   
 354   4005d9:   31 f6                   xor    esi,esi                              
 355   4005db:   ba 20 03 00 00          mov    edx,0x320                            
 356   4005e0:   e8 bb fe ff ff          call   4004a0 <memset@plt>			# arr[100] = {0}
```

That is how it looks like in a normal compilation - and our program is vulnerable to Control-Flow Hijacking.

Now let us take **prog2.c** and compile it with **SafeStack** security feature.

```
cpi-safestack$ clang-12 prog2.c -o prog2_ss -g -fsanitize=safe-stack
```

The **-fsanitize=safe-stack** option needs to be used to compile a program with SafeStack.

Let us take a look at ```main```'s disassembly.

```asm
1769 0000000000401820 <main>:                                                        
1770   401820:   55                      push   rbp                                  
1771   401821:   48 89 e5                mov    rbp,rsp                              
1772   401824:   48 83 ec 40             sub    rsp,0x40                             
1773   401828:   48 8b 0d b1 17 20 00    mov    rcx,QWORD PTR [rip+0x2017b1]        # 602fe0 <__safestack_unsafe_stack_ptr@@Base+0x602fe0>
1774   40182f:   48 89 4d f0             mov    QWORD PTR [rbp-0x10],rcx             
1775   401833:   64 48 8b 01             mov    rax,QWORD PTR fs:[rcx]               
1776   401837:   48 89 45 e8             mov    QWORD PTR [rbp-0x18],rax             
1777   40183b:   48 89 c7                mov    rdi,rax                              
1778   40183e:   48 81 c7 d0 fc ff ff    add    rdi,0xfffffffffffffcd0               
1779   401845:   64 48 89 39             mov    QWORD PTR fs:[rcx],rdi               
1780   401849:   c7 45 fc 00 00 00 00    mov    DWORD PTR [rbp-0x4],0x0              
1781   401850:   48 89 c1                mov    rcx,rax                              
1782   401853:   48 83 c1 f8             add    rcx,0xfffffffffffffff8               
1783   401857:   48 89 4d d8             mov    QWORD PTR [rbp-0x28],rcx             
1784   40185b:   48 c7 40 f8 0a 00 00    mov    QWORD PTR [rax-0x8],0xa              
1785   401862:   00                                                                  
1786   401863:   48 89 c1                mov    rcx,rax                              
1787   401866:   48 83 c1 f0             add    rcx,0xfffffffffffffff0               
1788   40186a:   48 89 4d c8             mov    QWORD PTR [rbp-0x38],rcx             
1789   40186e:   48 c7 40 f0 00 00 00    mov    QWORD PTR [rax-0x10],0x0             
1790   401875:   00                                                                  
1791   401876:   31 f6                   xor    esi,esi                              
1792   401878:   89 75 c4                mov    DWORD PTR [rbp-0x3c],esi             
1793   40187b:   ba 20 03 00 00          mov    edx,0x320                            
1794   401880:   e8 0b f6 ff ff          call   400e90 <memset@plt>                  
1795   401885:   48 8b 4d e8             mov    rcx,QWORD PTR [rbp-0x18]             
1796   401889:   8b 45 c4                mov    eax,DWORD PTR [rbp-0x3c]             
1797   40188c:   48 c7 41 f8 7b 00 00    mov    QWORD PTR [rcx-0x8],0x7b             
1798   401893:   00                                                                  
1799   401894:   bf fd 1a 40 00          mov    edi,0x401afd                         
1800   401899:   88 45 e7                mov    BYTE PTR [rbp-0x19],al               
1801   40189c:   e8 cf f5 ff ff          call   400e70 <printf@plt>                  
1802   4018a1:   48 8b 75 c8             mov    rsi,QWORD PTR [rbp-0x38]             
1803   4018a5:   8a 45 e7                mov    al,BYTE PTR [rbp-0x19]               
1804   4018a8:   bf 07 1b 40 00          mov    edi,0x401b07                         
1805   4018ad:   48 89 7d d0             mov    QWORD PTR [rbp-0x30],rdi             
1806   4018b1:   e8 8a f6 ff ff          call   400f40 <__isoc99_scanf@plt>          
1807   4018b6:   8a 45 e7                mov    al,BYTE PTR [rbp-0x19]
1808   4018b9:   bf 0b 1b 40 00          mov    edi,0x401b0b                         
1809   4018be:   e8 ad f5 ff ff          call   400e70 <printf@plt>                  
1810   4018c3:   48 8b 7d d0             mov    rdi,QWORD PTR [rbp-0x30]             
1811   4018c7:   48 8b 4d e8             mov    rcx,QWORD PTR [rbp-0x18]             
1812   4018cb:   8a 45 e7                mov    al,BYTE PTR [rbp-0x19]               
1813   4018ce:   48 8b 51 f0             mov    rdx,QWORD PTR [rcx-0x10]             
1814   4018d2:   48 8d b4 d1 d0 fc ff    lea    rsi,[rcx+rdx*8-0x330]                
1815   4018d9:   ff                                                                  
1816   4018da:   e8 61 f6 ff ff          call   400f40 <__isoc99_scanf@plt>          
1817   4018df:   4c 8b 45 d8             mov    r8,QWORD PTR [rbp-0x28]              
1818   4018e3:   48 8b 4d e8             mov    rcx,QWORD PTR [rbp-0x18]             
1819   4018e7:   8a 45 e7                mov    al,BYTE PTR [rbp-0x19]               
1820   4018ea:   48 8b 71 f0             mov    rsi,QWORD PTR [rcx-0x10]             
1821   4018ee:   4c 8b 49 f8             mov    r9,QWORD PTR [rcx-0x8]               
1822   4018f2:   48 8d 94 f1 d0 fc ff    lea    rdx,[rcx+rsi*8-0x330]                
1823   4018f9:   ff                                                                  
1824   4018fa:   48 8b 8c f1 d0 fc ff    mov    rcx,QWORD PTR [rcx+rsi*8-0x330]      
1825   401901:   ff                                                                  
1826   401902:   bf 19 1b 40 00          mov    edi,0x401b19                         
1827   401907:   e8 64 f5 ff ff          call   400e70 <printf@plt>                  
1828   40190c:   48 8b 4d e8             mov    rcx,QWORD PTR [rbp-0x18]             
1829   401910:   48 8b 45 f0             mov    rax,QWORD PTR [rbp-0x10]             
1830   401914:   64 48 89 08             mov    QWORD PTR fs:[rax],rcx               
1831   401918:   31 c0                   xor    eax,eax                              
1832   40191a:   48 83 c4 40             add    rsp,0x40                             
1833   40191e:   5d                      pop    rbp                                  
1834   40191f:   c3                      ret
```

Let us go over the code line by line - we need to figure out what the two stacks are, what happens to the traditional runtime stack, what variables go into safe and unsafe-stack - and finally see how the program behaves when we try to an out-of-bounds array access.

Let us start with the prologue.

```asm
1770   401820:   55                      push   rbp                                  
1771   401821:   48 89 e5                mov    rbp,rsp                              
1772   401824:   48 83 ec 40             sub    rsp,0x40
```

The stack-frame size is reduced to 0x40 / 64 bytes (from 832 bytes). Infer what you can from it :P

The next few lines are new (not present in the older version).

```asm
1773   401828:   48 8b 0d b1 17 20 00    mov    rcx,QWORD PTR [rip+0x2017b1]        # 602fe0 <__safestack_unsafe_stack_ptr@@Base+0x602fe0>
1774   40182f:   48 89 4d f0             mov    QWORD PTR [rbp-0x10],rcx             
1775   401833:   64 48 8b 01             mov    rax,QWORD PTR fs:[rcx]               
1776   401837:   48 89 45 e8             mov    QWORD PTR [rbp-0x18],rax
```

At this point, get an instance of **prog2_ss** running with gdb, because it is going to get interesting.

What does ```QWORD PTR [rip+0x2017b1]``` have? Which part of the memory layout is this present? The address **0x602fe0** is present in the **read-only segment** of **prog2**. This can be found out in multiple ways. One way is to visit the **/proc/PID/maps** file - which has the entire memory-layout blueprint with it. What segment is present in what virtual address space and what permissions does that address space have. If you are using any gdb-plugins, it might have a command to fetch this information. I use [gdb-peda](https://github.com/longld/peda) which has the **vmmap** command which gives the memory layout info.

```
  1 00400000-00402000 r-xp 00000000 08:05 8917351                            /home/dell/Documents/pwnthebox/MS-PhD/exp/cpi-safestack/prog2_ss
  2 00602000-00603000 r--p 00002000 08:05 8917351                            /home/dell/Documents/pwnthebox/MS-PhD/exp/cpi-safestack/prog2_ss
  3 00603000-00604000 rw-p 00003000 08:05 8917351                            /home/dell/Documents/pwnthebox/MS-PhD/exp/cpi-safestack/prog2_ss
  4 7ffff6818000-7ffff6819000 ---p 00000000 00:00 0                                 
  5 7ffff6819000-7ffff7019000 rw-p 00000000 00:00 0                                 
  6 7ffff7019000-7ffff7200000 r-xp 00000000 08:05 13109391                   /lib/x86_64-linux-gnu/libc-2.27.so
  7 7ffff7200000-7ffff7400000 ---p 001e7000 08:05 13109391                   /lib/x86_64-linux-gnu/libc-2.27.so
  8 7ffff7400000-7ffff7404000 r--p 001e7000 08:05 13109391                   /lib/x86_64-linux-gnu/libc-2.27.so
  9 7ffff7404000-7ffff7406000 rw-p 001eb000 08:05 13109391                   /lib/x86_64-linux-gnu/libc-2.27.so
 10 7ffff7406000-7ffff740a000 rw-p 00000000 00:00 0                                 
 11 7ffff740a000-7ffff740d000 r-xp 00000000 08:05 13109394                   /lib/x86_64-linux-gnu/libdl-2.27.so
 12 7ffff740d000-7ffff760c000 ---p 00003000 08:05 13109394                   /lib/x86_64-linux-gnu/libdl-2.27.so
 13 7ffff760c000-7ffff760d000 r--p 00002000 08:05 13109394                   /lib/x86_64-linux-gnu/libdl-2.27.so
 14 7ffff760d000-7ffff760e000 rw-p 00003000 08:05 13109394                   /lib/x86_64-linux-gnu/libdl-2.27.so
 15 7ffff760e000-7ffff77ab000 r-xp 00000000 08:05 13109395                   /lib/x86_64-linux-gnu/libm-2.27.so
 16 7ffff77ab000-7ffff79aa000 ---p 0019d000 08:05 13109395                   /lib/x86_64-linux-gnu/libm-2.27.so
 17 7ffff79aa000-7ffff79ab000 r--p 0019c000 08:05 13109395                   /lib/x86_64-linux-gnu/libm-2.27.so
 18 7ffff79ab000-7ffff79ac000 rw-p 0019d000 08:05 13109395                   /lib/x86_64-linux-gnu/libm-2.27.so
 19 7ffff79ac000-7ffff79b3000 r-xp 00000000 08:05 13109408                   /lib/x86_64-linux-gnu/librt-2.27.so
 20 7ffff79b3000-7ffff7bb2000 ---p 00007000 08:05 13109408                   /lib/x86_64-linux-gnu/librt-2.27.so
 21 7ffff7bb2000-7ffff7bb3000 r--p 00006000 08:05 13109408                   /lib/x86_64-linux-gnu/librt-2.27.so
 22 7ffff7bb3000-7ffff7bb4000 rw-p 00007000 08:05 13109408                   /lib/x86_64-linux-gnu/librt-2.27.so
 23 7ffff7bb4000-7ffff7bce000 r-xp 00000000 08:05 13109406                   /lib/x86_64-linux-gnu/libpthread-2.27.so
 24 7ffff7bce000-7ffff7dcd000 ---p 0001a000 08:05 13109406                   /lib/x86_64-linux-gnu/libpthread-2.27.so
 25 7ffff7dcd000-7ffff7dce000 r--p 00019000 08:05 13109406                   /lib/x86_64-linux-gnu/libpthread-2.27.so
 26 7ffff7dce000-7ffff7dcf000 rw-p 0001a000 08:05 13109406                   /lib/x86_64-linux-gnu/libpthread-2.27.so
 27 7ffff7dcf000-7ffff7dd3000 rw-p 00000000 00:00 0                                 
 28 7ffff7dd3000-7ffff7dfc000 r-xp 00000000 08:05 13109386                   /lib/x86_64-linux-gnu/ld-2.27.so
 29 7ffff7fc5000-7ffff7fc9000 rw-p 00000000 00:00 0                                 
 30 7ffff7ff8000-7ffff7ffb000 r--p 00000000 00:00 0                          [vvar] 
 31 7ffff7ffb000-7ffff7ffc000 r-xp 00000000 00:00 0                          [vdso] 
 32 7ffff7ffc000-7ffff7ffd000 r--p 00029000 08:05 13109386                   /lib/x86_64-linux-gnu/ld-2.27.so
 33 7ffff7ffd000-7ffff7ffe000 rw-p 0002a000 08:05 13109386                   /lib/x86_64-linux-gnu/ld-2.27.so
 34 7ffff7ffe000-7ffff7fff000 rw-p 00000000 00:00 0                                 
 35 7ffffffdd000-7ffffffff000 rw-p 00000000 00:00 0                          [stack]
 36 ffffffffff600000-ffffffffff601000 --xp 00000000 00:00 0                  [vsyscall]
```

Take a look at line-2: **00602000-00603000 r--p 00002000 08:05 8917351 cpi-safestack/prog2_ss**. But this is not very informative - because we just know that is it in a read-only area. Let us take a look at **prog2_ss**'s sections using readelf.

```
-safestack$ readelf -S prog2_ss
There are 36 section headers, starting at offset 0x46c8:

Section Headers:
  [Nr] Name              Type             Address           Offset
       Size              EntSize          Flags  Link  Info  Align
  [ 0]                   NULL             0000000000000000  00000000
       0000000000000000  0000000000000000           0     0     0
  [ 1] .interp           PROGBITS         0000000000400270  00000270
       000000000000001c  0000000000000000   A       0     0     1
  [ 2] .note.ABI-tag     NOTE             000000000040028c  0000028c
       0000000000000020  0000000000000000   A       0     0     4
  [ 3] .note.gnu.build-i NOTE             00000000004002ac  000002ac
       0000000000000024  0000000000000000   A       0     0     4
  [ 4] .gnu.hash         GNU_HASH         00000000004002d0  000002d0
       00000000000000b4  0000000000000000   A       5     0     8
  [ 5] .dynsym           DYNSYM           0000000000400388  00000388
       0000000000000450  0000000000000018   A       6     1     8
  [ 6] .dynstr           STRTAB           00000000004007d8  000007d8
       00000000000002b8  0000000000000000   A       0     0     1
  [ 7] .gnu.version      VERSYM           0000000000400a90  00000a90
       000000000000005c  0000000000000002   A       5     0     2
  [ 8] .gnu.version_r    VERNEED          0000000000400af0  00000af0
       0000000000000090  0000000000000000   A       6     4     8
  [ 9] .rela.dyn         RELA             0000000000400b80  00000b80
       0000000000000060  0000000000000018   A       5     0     8
  [10] .rela.plt         RELA             0000000000400be0  00000be0
       0000000000000210  0000000000000018  AI       5    24     8
  [11] .init             PROGBITS         0000000000400df0  00000df0
       0000000000000017  0000000000000000  AX       0     0     4
  [12] .plt              PROGBITS         0000000000400e10  00000e10
       0000000000000170  0000000000000010  AX       0     0     16
  [13] .text             PROGBITS         0000000000400f80  00000f80
       0000000000000a12  0000000000000000  AX       0     0     16
  [14] .fini             PROGBITS         0000000000401994  00001994
       0000000000000009  0000000000000000  AX       0     0     4
  [15] .rodata           PROGBITS         00000000004019a0  000019a0
       00000000000001a0  0000000000000000   A       0     0     4
  [16] .eh_frame_hdr     PROGBITS         0000000000401b40  00001b40
       000000000000008c  0000000000000000   A       0     0     4
  [17] .eh_frame         PROGBITS         0000000000401bd0  00001bd0
       00000000000002e8  0000000000000000   A       0     0     8
  [18] .tbss             NOBITS           0000000000602d88  00002d88
       0000000000000020  0000000000000000 WAT       0     0     8
  [19] .preinit_array    PREINIT_ARRAY    0000000000602d88  00002d88
       0000000000000008  0000000000000008  WA       0     0     8
  [20] .init_array       INIT_ARRAY       0000000000602d90  00002d90
       0000000000000008  0000000000000008  WA       0     0     8
  [21] .fini_array       FINI_ARRAY       0000000000602d98  00002d98
       0000000000000008  0000000000000008  WA       0     0     8
  [22] .dynamic          DYNAMIC          0000000000602da0  00002da0
       0000000000000240  0000000000000010  WA       6     0     8
  [23] .got              PROGBITS         0000000000602fe0  00002fe0
       0000000000000020  0000000000000008  WA       0     0     8
  [24] .got.plt          PROGBITS         0000000000603000  00003000
       00000000000000c8  0000000000000008  WA       0     0     8
  [25] .data             PROGBITS         00000000006030c8  000030c8
       0000000000000010  0000000000000000  WA       0     0     8
  [26] .bss              NOBITS           00000000006030d8  000030d8
       0000000000000078  0000000000000000  WA       0     0     8
  [27] .comment          PROGBITS         0000000000000000  000030d8
       000000000000007c  0000000000000001  MS       0     0     1
  [28] .debug_info       PROGBITS         0000000000000000  00003154
       0000000000000093  0000000000000000           0     0     1
  [29] .debug_abbrev     PROGBITS         0000000000000000  000031e7
       000000000000005e  0000000000000000           0     0     1
  [30] .debug_line       PROGBITS         0000000000000000  00003245
       0000000000000077  0000000000000000           0     0     1
  [31] .debug_str        PROGBITS         0000000000000000  000032bc
       00000000000000bb  0000000000000001  MS       0     0     1
  [32] .debug_loc        PROGBITS         0000000000000000  00003377
       0000000000000077  0000000000000000           0     0     1
  [33] .symtab           SYMTAB           0000000000000000  000033f0
       0000000000000a98  0000000000000018          34    68     8
  [34] .strtab           STRTAB           0000000000000000  00003e88
       00000000000006e9  0000000000000000           0     0     1
  [35] .shstrtab         STRTAB           0000000000000000  00004571
       0000000000000154  0000000000000000           0     0     1
Key to Flags:
  W (write), A (alloc), X (execute), M (merge), S (strings), I (info),
  L (link order), O (extra OS processing required), G (group), T (TLS),
  C (compressed), x (unknown), o (OS specific), E (exclude),
  l (large), p (processor specific)
```

Please take a look at the entry-23 - the **.got** section. This is short for **Global Offset Table(GOT)**. This is a table which helps in resolving relocations at runtime. Generally, library functions and other global variables need to be resolved at runtime. Consider ```printf``` function for example. We include the header file *stdio.h* which declares the ```printf``` function and we use it in our program. We never define it. It is present in machine code form in *libc.so*. When the linker is linking your code, it never knows the absolute address of ```printf``` (because it is defined in another binary and can be mapped at different addresses). Because of this, we need a mechanism to resolve ```printf```'s address at runtime. The Global Offset Table and Procedure Linkage Table helps in resolving relocations at runtime.

Let us take a look at all the relocations that has to happen at runtime.

```
cpi-safestack$ objdump --dynamic-reloc ./prog2_ss

./prog2_ss:     file format elf64-x86-64

DYNAMIC RELOCATION RECORDS
OFFSET           TYPE              VALUE 
0000000000602fe0 R_X86_64_TPOFF64  __safestack_unsafe_stack_ptr@@Base
0000000000602fe8 R_X86_64_GLOB_DAT  __libc_start_main@GLIBC_2.2.5
0000000000602ff0 R_X86_64_GLOB_DAT  __gmon_start__
0000000000602ff8 R_X86_64_GLOB_DAT  stderr@GLIBC_2.2.5
0000000000603018 R_X86_64_JUMP_SLOT  pthread_attr_getguardsize@GLIBC_2.2.5
0000000000603020 R_X86_64_JUMP_SLOT  free@GLIBC_2.2.5
0000000000603028 R_X86_64_JUMP_SLOT  abort@GLIBC_2.2.5
0000000000603030 R_X86_64_JUMP_SLOT  __errno_location@GLIBC_2.2.5
0000000000603038 R_X86_64_JUMP_SLOT  getpid@GLIBC_2.2.5
0000000000603040 R_X86_64_JUMP_SLOT  printf@GLIBC_2.2.5
0000000000603048 R_X86_64_JUMP_SLOT  pthread_setspecific@GLIBC_2.2.5
0000000000603050 R_X86_64_JUMP_SLOT  memset@GLIBC_2.2.5
0000000000603058 R_X86_64_JUMP_SLOT  pthread_attr_init@GLIBC_2.2.5
0000000000603060 R_X86_64_JUMP_SLOT  __tls_get_addr@GLIBC_2.3
0000000000603068 R_X86_64_JUMP_SLOT  pthread_attr_getstacksize@GLIBC_2.2.5
0000000000603070 R_X86_64_JUMP_SLOT  dlvsym@GLIBC_2.2.5
0000000000603078 R_X86_64_JUMP_SLOT  fprintf@GLIBC_2.2.5
0000000000603080 R_X86_64_JUMP_SLOT  syscall@GLIBC_2.2.5
0000000000603088 R_X86_64_JUMP_SLOT  pthread_mutex_unlock@GLIBC_2.2.5
0000000000603090 R_X86_64_JUMP_SLOT  malloc@GLIBC_2.2.5
0000000000603098 R_X86_64_JUMP_SLOT  pthread_key_create@GLIBC_2.2.5
00000000006030a0 R_X86_64_JUMP_SLOT  pthread_attr_destroy@GLIBC_2.2.5
00000000006030a8 R_X86_64_JUMP_SLOT  __isoc99_scanf@GLIBC_2.7
00000000006030b0 R_X86_64_JUMP_SLOT  getrlimit@GLIBC_2.2.5
00000000006030b8 R_X86_64_JUMP_SLOT  dlsym@GLIBC_2.2.5
00000000006030c0 R_X86_64_JUMP_SLOT  pthread_mutex_lock@GLIBC_2.2.5
```

There are not only functions which need runtime resolution but also other data variables. Take a look at the first 4 entries.

```
DYNAMIC RELOCATION RECORDS
OFFSET           TYPE              VALUE 
0000000000602fe0 R_X86_64_TPOFF64  __safestack_unsafe_stack_ptr@@Base
0000000000602fe8 R_X86_64_GLOB_DAT  __libc_start_main@GLIBC_2.2.5
0000000000602ff0 R_X86_64_GLOB_DAT  __gmon_start__
0000000000602ff8 R_X86_64_GLOB_DAT  stderr@GLIBC_2.2.5
```

The following is the description of the .got section:

```
  [23] .got              PROGBITS         0000000000602fe0  00002fe0
         0000000000000020  0000000000000008  WA       0     0     8
```

This section starts at the virtual address 0x602fe0 and it is 0x20/32 bytes in size. Because it has a 8-byte boundary, it has 4(32 bytes/8) entries - each of size 8 bytes. The 4 entries are described above. What does an entry/record mean? What data does it contain?

We are specifically interested in the entry at the address 0x602fe0. using gdb, the following is the table values.

```
gdb-peda$ x/4qx 0x602fe0
0x602fe0:	0xffffffffffffffe0	0x00007ffff703ab10
0x602ff0:	0x0000000000000000	0x00007ffff7405840
```

The first entry at the address 0x602fe0 has the number **0xffffffffffffffe0**. It is of the type **R_X86_64_TPOFF64** and is bound to the symbol **__safestack_unsafe_stack_ptr@@Base**. What exactly does the number **0xffffffffffffffe0** mean? Its meaning is derived from the relocation-type - **R_X86_64_TPOFF64**. From page 78 of [this document](http://people.redhat.com/drepper/tls.pdf), the entry-value is the **Offset in Initial TLS block**.


To summarize, the Base Pointer to the unsafe-stack is present at an offset of 0xffffffffffffffe0 to the TLS block.

```
                                        |                        |
                                        |                        |
                                        |                        |
__safestack_unsafe_stack_ptr@@Base-->   |                        |
                                        |                        |
                                        |                        |
            Initial TLS block ---->     |                        |
```


Because the virtual address of the Initial TLS block is decided at runtime, the virtual address of **__safestack_unsafe_stack_ptr@@Base** is also decided at runtime. What we can have at compile-time is the offset at which our unsafe-stack would be present - so that we can calculate the actual address at runtime(the way we are doing now).

Coming back to the following lines of code.

```asm
1773   401828:   48 8b 0d b1 17 20 00    mov    rcx,QWORD PTR [rip+0x2017b1]        # 602fe0 <__safestack_unsafe_stack_ptr@@Base+0x602fe0>
1774   40182f:   48 89 4d f0             mov    QWORD PTR [rbp-0x10],rcx             
1775   401833:   64 48 8b 01             mov    rax,QWORD PTR fs:[rcx]
1776   401837:   48 89 45 e8             mov    QWORD PTR [rbp-0x18],rax
```

Line 1773 simply loads the offset into register ```rcx```. That offset is then stored at ```rbp-0x10```. The third instruction is interesting.

```asm
 1775   401833:   64 48 8b 01             mov    rax,QWORD PTR fs:[rcx]
```

The register **fs** represents the starting of the TLS block. ```fs:[rcx]``` would give us (TLS block's address + unsafe-stack-offset) which is the virtual address of our unsafe-stack. After line 1775 is executed, the following are the register values.

```asm
gdb-peda$ i r fs rcx rax
fs             0x0	0x0
rcx            0xffffffffffffffe0	0xffffffffffffffe0
rax            0x7ffff7019000	0x7ffff7019000
```

I have also found it strange that the fs register has a value of 0. According to the [linux kernel documentation page](https://www.kernel.org/doc/html/latest/x86/x86_64/fsgs.html), the **fs** register is a per-thread value.

> Each thread has its own FS base address so common code can be used without complex address offset calculations to access the per thread instances.

```rax = 0x7ffff7019000``` is where our unsafe-stack is located. You will be able to locate a **rw-** region in the memory layout of this process where this address is located.

```
Start              End                Perm	Name
0x00400000         0x00402000         r-xp	/home/dell/Documents/pwnthebox/MS-PhD/exp/cpi-safestack/prog2_ss
0x00602000         0x00603000         r--p	/home/dell/Documents/pwnthebox/MS-PhD/exp/cpi-safestack/prog2_ss
0x00603000         0x00604000         rw-p	/home/dell/Documents/pwnthebox/MS-PhD/exp/cpi-safestack/prog2_ss
0x00007ffff6818000 0x00007ffff6819000 ---p	mapped
0x00007ffff6819000 0x00007ffff7019000 rw-p	mapped
```

The last entry is where our main thread's unsafe-stack is located. Closely observe ```rax```'s value: It is ```0x00007ffff7019000```, the end-address of the TLS block. It would be really interesting to see how all this works with multiple threads.

```
                                                |                        | <------- unsafe-stack-base (0x00007ffff7019000)
                                                |                        |
                                                |                        |
                                                |                        |
                                                |                        |
                                                |                        |
                                                |                        |
Lowend-Address (0x00007ffff6819000) ------->    |                        |
```

Please note that the unsafe-stack (like traditional stack) grows upside-down.

Let me summarize what we did: We wanted to find where our unsafe-stack is located. We got to know that it is located somewhere in the TLS(Thread Local Storage) block. But where is it located inside TLS block? That info was given by our **.got** entry. In this example, the unsafe-stack is located at an offset of 0xffffffffffffffe0 from the TLS block beginning.

As of now, we have two stacks: The traditional runtime stack given to us by the OS and the other made-up unsafe-stack present in the TLS block. The traditional runtime-stack is the **safe-stack**.

With that, we are clear on what the two stacks are and where they are located. Let us continue reading ```main```'s disassembly. At this point, ```rax``` points to the unsafe-stack-base and ```rcx``` has the offset-value.

```asm
1781   401850:   48 89 c1                mov    rcx,rax                              
1782   401853:   48 83 c1 f8             add    rcx,0xfffffffffffffff8               
1783   401857:   48 89 4d d8             mov    QWORD PTR [rbp-0x28],rcx             
1784   40185b:   48 c7 4 0 f8 0a 00 00   mov    QWORD PTR [rax-0x8],0xa              
1785   401862:   00
```

I have skipped instructions 1777-1780. Will come to that later. Look at what the above instructions are doing: Line 1785 writes **0xa** into ```rax-0x8```. ```rax``` points to the unsafe-stack-base. **0xa** is written at ```rax-0x8```. So the unsafe-stack looks like the following now.

```
                                                |00 00 00 00  00 00 00 00| <------- unsafe-stack-base (0x00007ffff7019000)
                                                |                        |
                                                |                        |
                                                |                        |
                                                |                        |
                                                |                        |
                                                |                        |
Lowend-Address (0x00007ffff6819000) ------->    |                        |
`
```

The variable which is initialized to 10/0xa is **n**. This means **n** is placed in the unsafe-stack.

The instructions 1781-1783 calculates ```n```'s address and stores it in the safe-stack (```mov qword [rbp-0x28], rcx```).

The next few instructions are very similar to the above instructions.

```asm
1781   401850:   48 89 c1                mov    rcx,rax                              
1782   401853:   48 83 c1 f8             add    rcx,0xfffffffffffffff8               
1783   401857:   48 89 4d d8             mov    QWORD PTR [rbp-0x28],rcx             
1784   40185b:   48 c7 4 0 f8 0a 00 00   mov    QWORD PTR [rax-0x8],0xa              
1785   401862:   00                                                                  
1786   401863:   48 89 c1                mov    rcx,rax                              
1787   401866:   48 83 c1 f0             add    rcx,0xfffffffffffffff0               
1788   40186a:   48 89 4d c8             mov    QWORD PTR [rbp-0x38],rcx             
1789   40186e:   48 c7 40 f0 00 00 00    mov    QWORD PTR [rax-0x10],0x0             
1790   401875:   00                                                                  
1798   401893:   00
```

The following is the C-style pseudo-code for the above assembly code.

```c
// More meaningful symbols:
// rax = unsafe_stack_base;
// rcx = moving_ptr;

void *unsafe_stack_base = 0x00007ffff7019000;
void *moving_ptr = unsafe_stack_base;

// Make the pointer point to n.
// It is at a -8 offset wrt unsafe_stack_base
moving_ptr += -8;
*(uint64_t *)(moving_ptr) = 0xa; 	// The assembly code has (unsafe_stack_base-0x8)he same

// Next comes x.
// It is at a -16 offset wrt unsafe_stack_base
moving_ptr += -16;
*(uint64_t *)(moving_ptr) = 0x0;
```


I had ignored a few instructions at the beginning - which are related to buffer initialization.

```asm
1777   40183b:   48 89 c7                mov    rdi,rax                              
1778   40183e:   48 81 c7 d0 fc ff ff    add    rdi,0xfffffffffffffcd0               
1779   401845:   64 48 89 39             mov    QWORD PTR fs:[rcx],rdi
.
.
.
1791   401876:   31 f6                   xor    esi,esi                              
1792   401878:   89 75 c4                mov    DWORD PTR [rbp-0x3c],esi             
1793   40187b:   ba 20 03 00 00          mov    edx,0x320                            
1794   401880:   e8 0b f6 ff ff          call   400e90 <memset@plt>
```

Here, `Register rdi is made to point to the buffer. 0xfffffffffffffcd0 is 2's complement form for -816 bytes. With rdi having the buffer's address, rsi set to 0 (1791 ```xor esi,esi```) and edx loaded with 0x320(800 bytes), the buffer is being zeroized (```long int buffer[100] = {0};```).

With that, the unsafe-stack looks like the following:

```
                                        n---> |0a 00 00 00 00 00 00 00| <------- unsafe-stack-base (rax=0x00007ffff7019000)
                                        x---> |00 00 00 00 00 00 00 00|
                                              |00 00 00 00 00 00 00 00|
                                              |.                      |
                                              |.                      |
                                              |.                      |
                                              |.                      |
                                    buffer--> |00 00 00 00 00 00 00 00|
                                              |.                      |
                                              |.                      |
Lowend-Address (0x00007ffff6819000) --------> |                       |

```

When these variables were being initialized in the unsafe-stack, some metadata about these variables were being stored in the safe-stack. There are bunch of ```mov [rbp-XXXX], YYYY``` instructions sprinkled among these instructions. I urge you to identify those instructions and visualize how the safe-stack looks like.

```
                                <--4 bytes--><--4 bytes-->
rbp-0x40 (0x7fffffffd910)--->   |00 00 00 00  00 00 00 00| 
                                |       x's address      | (0x00007ffff7018ff0)
rbp-0x30 (0x7fffffffd920)--->   |00 00 00 00  00 00 00 00| 
                                |       n's address      | (0x00007ffff7018ff8)
rbp-0x20 (0x7fffffffd930)--->   |00 00 00 00  00 00 00 00|
                                |   unsafe-stack-base    | (0x00007ffff7019000)
rbp-0x10 (0x7fffffffd940)--->   |unsafe-stack-tls-offset | (0xffffffffffffffe0)
                                |00 00 00 00  00 00 00 00|
rbp      (0x7fffffffd950)--->   | Caller's Base Pointer  |
                                |     Return-Address     |
```

This is how safe-stack looks like. Whatever operations happen in the buffer or any variables in this example, nothing is going to affect the Return-Address and Caller's Base-Pointer.

At this point, we have sort of run the program without running it. Aim was to get a good understanding of what the two stacks are, where they are located.

Let us now run the program.

```
cpi-safestack$ ./prog2_ss
Enter n: 99 
Enter value: 12
arr[99]: (0x7fafe2c6dfe8, 0xc), x: (0x7fafe2c6dff8, 0x7b)

cpi-safestack$ ./prog2_ss
Enter n: 100
Enter value: 12
arr[12]: (0x7f1b09037d30, 0x0), x: (0x7f1b09037ff8, 0x7b)

cpi-safestack$ ./prog2_ss
Enter n: 101
Enter value: 12
arr[101]: (0x7fce2f1d3ff8, 0xc), x: (0x7fce2f1d3ff8, 0xc)

cpi-safestack$ ./prog2_ss
Enter n: 102
Enter value: 12
Segmentation fault (core dumped)

cpi-safestack$ ./prog2_ss
Enter n: 103
Enter value: 12
Segmentation fault (core dumped)
```

The program is crashing, but is it crashing because of a Control-Flow Hijack attempt? Let us check it out using ltrace.

```
cpi-safestack$ ltrace ./prog2_ss
getrlimit(3, 0x7fffa198f360, 0x7fffa198f3f8, 0x7fa31ede6bb0)                                            = 0
syscall(9, 0, 0x801000, 3)                                                                              = 0x7fa31d831000
syscall(10, 0x7fa31d831000, 4096, 0)                                                                    = 0
pthread_key_create(0x6030e8, 0x401550, 0, 0x7fa31e14d639)                                               = 0
memset(0x7fa31e031cd0, '\0', 800)                                                                       = 0x7fa31e031cd0
printf("Enter n: ")                                                                                     = 9
__isoc99_scanf(0x401b07, 0x7fa31e031ff0, 0x7fffa198ed60, 0Enter n: 102
)                                             = 1
printf("Enter value: ")                                                                                 = 13
__isoc99_scanf(0x401b07, 0x7fa31e032000, 102, 0x7fa31e032000Enter value: 12
 <no return ...>
 --- SIGSEGV (Segmentation fault) ---
 +++ killed by SIGSEGV +++
```

The program crashed while taking input. The unsafe-stack looks like this.


```
<buffer - 100 * 8 bytes><x - 8 bytes><n - 8 bytes> < libc.so's code segment present here>
                                                  ^
                                                  |
                                                 TLS Block ends(0x00007ffff7019000)
```

Take a look at the following. It tells where the TLS block ends and libc.so's code segment starts.

```
0x00007ffff6818000 0x00007ffff6819000 ---p	mapped
0x00007ffff6819000 0x00007ffff7019000 rw-p	mapped
0x00007ffff7019000 0x00007ffff7200000 r-xp	/lib/x86_64-linux-gnu/libc-2.27.so
```

When we tried to write to arr[100], we accessed 'x'. With arr[101], we accessed 'n'. Both belong to the stack and thus we were able to write into it. But with arr[102], we entered libc.so's code text segment - which is read-execute only - no write permissions. Because ```scanf``` tried to write into a non-writable address, the program crashed.

Because they variables were separated, Control-Flow Hijacking is made impossible.


# 4. Why were certain variables put into unsafe stack?

I was expecting ```x``` and ```n``` to be placed in safe-stack and only the array to be placed in the unsafe-stack. But surprisingly, all 3 objects were placed in the unsafe-stack. In this section, we will understand how this is working.

The array had to be placed in the unsafe-stack because there is no way to prove it is safe (because it solely depends on user-input). But what about ```x``` and ```n```? I am guessing that they were placed in the unsafe-stack because their addresses are used. Let us not use ```&x``` and see where ```x``` is placed. Consider **prog3.c**.

```c
cpi-safestack$ cat prog3.c
#include <stdio.h>
int main()
{
	long int x = 10, n = 0;
	long int arr[100] = {0};
	
	x = 123;

	printf("Enter n: ");
	scanf("%ld", &n);

	printf("Enter value: ");
	scanf("%ld", &arr[n]);

	printf("arr[%ld]: (%p, 0x%lx), x: (0x%lx)\n", n, arr+n, arr[n], x);

	return 0;
}
```

The only change is that we have not used ```&x```. Compile it with SafeStack. Let us checkout the new disassembly. In the entire disassembly, the following instructions are present.
```asm
1779   401850:   48 c7 45 f0 0a 00 00    mov    QWORD PTR [rbp-0x10],0xa             
1780   401857:   00
.
.
1791   40187d:   48 c7 45 f0 7b 00 00    mov    QWORD PTR [rbp-0x10],0x7b            
1792   401884:   00
```

This shows that ```x``` is now placed into the safe-stack.

Guarantees on memory-safety is best understood by using the Rust programming language. In Rust, getting the raw-pointer to a variable in not unsafe - you are simply getting its address. If you dereference it OR try performing some sort of arithmetic, then that is considered unsafe. The same logic could be applied here. In our code, we are getting the address of a variable but not doing anything with it (except from reading it).


# 5. Experimenting with some builtin functions

In the SafeStack documentation page, there are bunch of [Low-level API](https://clang.llvm.org/docs/SafeStack.html#low-level-api) listed. The following are the builtins listed. Let us use them in our program and get details about our unsafe-stack. Consider **prog4.c**.

```c
cpi-safestack$ cat prog4.c
#include <stdio.h>
int main()
{
	long int x = 10, n = 0;
	long int arr[100] = {0};
	
	x = 123;

	printf("Enter n: ");
	scanf("%ld", &n);

	printf("Enter value: ");
	scanf("%ld", &arr[n]);

	printf("arr[%ld]: (%p, 0x%lx), x: (0x%lx)\n", n, arr+n, arr[n], x);

	printf("1. Current unsafe stack pointer: %p\n", __builtin___get_unsafe_stack_ptr());
	printf("2. Botton of unsafe-stack: %p\n", __builtin___get_unsafe_stack_bottom());
	printf("3. Top of unsafe-stack: %p\n", __builtin___get_unsafe_stack_top());
	printf("4. Total capacity: %lu bytes\n", __builtin___get_unsafe_stack_top() - __builtin___get_unsafe_stack_bottom());
	printf("4. Size of unsafe-stack: %lu bytes\n", __builtin___get_unsafe_stack_top() - __builtin___get_unsafe_stack_ptr()) ;

	return 0;
}
```

Running it gave the following:

```
cpi-safestack$ ./prog4_ss
Enter n: 10
Enter value: 123
arr[10]: (0x7f928a3c7d20, 0x7b), x: (0x7b)
1. Current unsafe stack pointer: 0x7f928a3c7cd0
2. Botton of unsafe-stack: 0x7f9289bc8000
3. Top of unsafe-stack: 0x7f928a3c8000
4. Total capacity: 8388608 bytes
4. Size of unsafe-stack: 816 bytes
```

Interesting thing to do would be to checkout the implementations of these functions. With the code we have seen related to unsafe-stack, it should be easier to understand.

# 6. Conclusion and next steps

I hope you got an idea of what SafeStack is, how it actually looks like in memory, where it is located, what types of variables goes into an unsafe-stack etc.,

The SafeStack mechanism is part of the [Code Pointer Integrity](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/kuznetsov) project. As part of this, I would like to explore the following:

1. In BlackHat Europe 2016, there is a talk [Bypassing clang's SafeStack for Fun and profit](https://www.blackhat.com/eu-16/briefings/schedule/#bypassing-clangs-safestack-for-fun-and-profit-4965). With the understanding I have at the moment, I would like to explore the bypass mechanism.
2. Understanding Code Pointer Integrity
3. Get more clarity on TLS block and segment registers(fs, gs etc.,). The concepts around these are not very clear to me.

With that, we have come to the end of this article.

Thank you for reading :)
