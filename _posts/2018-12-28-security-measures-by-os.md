---
layout: post
title: How does the Operating System defend itself?
categories: Reverse Engineering and Binary Exploitation Series
comments: true
---

Hey fellow pwners!

In the last few posts, we have seen the Buffer Overflow Vulnerability in good detail, how we can use shellcode to exploit it and get a shell. So, we have seen the attack part of a BOF. In this post, let us discuss how to defend from such attacks due to BOFs. 

BOFs are not new at all. They have been around from a really long time(first discovered in 1990s) and are still there. Different defenses are designed by researchers and engineers and are then administered into the Operating System. 

So, we will be talking about few very famous and quite effective security measures that the OS is empowered with to keep the system safe. 

This is the 13th post. So, create a directory named **post_13** inside the **rev_eng_series** directory. 

 
## 1. Stack Cookie

Consider the following program: 

    rev_eng_series/post_13$ cat vuln.c 
    #include<stdio.h>

    void func() {

        int var = 0;
        char buffer[100];

        gets(buffer);
    }

    int main() {

        printf("Before calling func\n");
        func();
        printf("After calling func\n");

        return 0;
    }

The program is pretty straight forward. It calls a function **func** which calls the **gets** function with buffer of size **100** bytes. 

### Analysis 

1. Let us compile the program **vuln.c** in 2 different ways to get 2 different executables. 

        rev_eng_series/post_13$ gcc vuln.c -o vuln_normal
        rev_eng_series/post_13$ gcc vuln.c -o vuln_nostkp -fno-stack-protector

    * We get 2 executables **vuln_normal** and **vuln_nostkp**. In most of the previous posts related to BOF, we have compiled a program in the second manner. It says **-fno-stack-protector**. Note that the **f** stands for **flag**. So, in the second case, we are actually **setting the flag** which will make sure there is **no** stack protector. 

    * What is this stack protector then? Let us dig a bit deeper and see. 

2. Let us get the disassemblies of **func** in both the executables. The following are the disassemblies: 

        Disassembly of func from vuln_normal: 
        00000000004005d6 <func>:
        4005d6:	55                   	push   rbp
        4005d7:	48 89 e5             	mov    rbp,rsp
        4005da:	48 83 c4 80          	add    rsp,0xffffffffffffff80
        4005de:	64 48 8b 04 25 28 00 	mov    rax,QWORD PTR fs:0x28
        4005e5:	00 00 
        4005e7:	48 89 45 f8          	mov    QWORD PTR [rbp-0x8],rax
        4005eb:	31 c0                	xor    eax,eax
        4005ed:	c7 45 8c 00 00 00 00 	mov    DWORD PTR [rbp-0x74],0x0
        4005f4:	48 8d 45 90          	lea    rax,[rbp-0x70]
        4005f8:	48 89 c7             	mov    rdi,rax
        4005fb:	b8 00 00 00 00       	mov    eax,0x0
        400600:	e8 bb fe ff ff       	call   4004c0 <gets@plt>
        400605:	90                   	nop
        400606:	48 8b 45 f8          	mov    rax,QWORD PTR [rbp-0x8]
        40060a:	64 48 33 04 25 28 00 	xor    rax,QWORD PTR fs:0x28
        400611:	00 00 
        400613:	74 05                	je     40061a <func+0x44>
        400615:	e8 86 fe ff ff       	call   4004a0 <__stack_chk_fail@plt>
        40061a:	c9                   	leave  
        40061b:	c3                   	ret  
    

        Disassembly of func from vuln_nostkp: 
        0000000000400566 <func>:
        400566:	55                   	push   rbp
        400567:	48 89 e5             	mov    rbp,rsp
        40056a:	48 83 ec 70          	sub    rsp,0x70
        40056e:	c7 45 fc 00 00 00 00 	mov    DWORD PTR [rbp-0x4],0x0
        400575:	48 8d 45 90          	lea    rax,[rbp-0x70]
        400579:	48 89 c7             	mov    rdi,rax
        40057c:	b8 00 00 00 00       	mov    eax,0x0
        400581:	e8 ca fe ff ff       	call   400450 <gets@plt>
        400586:	90                   	nop
        400587:	c9                   	leave  
        400588:	c3                   	ret  


    * It is better if you open 2 terminals and have both the disassemblies side by side. It will be easy to compare them and draw conclusions.    


3. Let us talk about **func** of **vuln_nostkp** : 

    * The StackFrame of size **0x70 / 112** bytes is built. 
    
    * **rbp-0x4** is set to **0x0**. This is **var** variable. 
    
    * **rdi** is loaded with **rbp-0x70** and then **gets** is called. This means **rbp-0x70** is the starting address of **buffer** of 100 bytes. 
    
    * **gets** is called. 
    
    * StackFrame is destructed and control returns back to main function(if we let it to :P). 
    
    * We can say that this is the exact copy of the C function we wrote. 

4. Now, let us talk about **func** of **vuln_normal** : 

    * First, the StackFrame is of size **128 bytes**. 
    
    * This has a few instructions which were not there in the func of **vuln_nostkp**. 
     
    * Let us go through it's disassembly to understand it. 

    * Construction of StackFrame: 

            4005d6:	55                   	push   rbp
            4005d7:	48 89 e5             	mov    rbp,rsp
            4005da:	48 83 c4 80          	add    rsp,0xffffffffffffff80

    * 2 New instructions: 
    
            4005de:	64 48 8b 04 25 28 00 	mov    rax,QWORD PTR fs:0x28
            4005e5:	00 00 
            4005e7:	48 89 45 f8          	mov    QWORD PTR [rbp-0x8],rax

        * **8 bytes** at a wierd location **fs:0x28** is loaded into **rbp-0x8**. 

    * After gets, 4 new instructions: 

            400606:	48 8b 45 f8          	mov    rax,QWORD PTR [rbp-0x8]
            40060a:	64 48 33 04 25 28 00 	xor    rax,QWORD PTR fs:0x28
            400611:	00 00 
            400613:	74 05                	je     40061a <func+0x44>
            400615:	e8 86 fe ff ff       	call   4004a0 <__stack_chk_fail@plt>

        * The 8 bytes loaded into **rbp-0x8** are loaded back to **rax**. 

        * Then, **rax** is **xor**ed with **8** bytes at **fs:0x28**. If the content in rax is the same as 8 bytes at fs:0x28, then rax has **0** after the xor instruction is executed. Most importantly, the **zero flag** of **eflags** is set(to 1) when **xor** of the 2 operands is 0. So, if they are equal, **zero flag** is set. 

        * The **je** looks at **zero flag** and decides if the operands of xor(or cmp for that matter) are equal or not. Why should the zero flag be set if they are equal? This is because  internally(at the hardware level), the difference of the 2 operands is calculated. If the difference is 0, it simply means they are equal. To signify this, the **zero flag** is set. This means the difference is **zero**. 

        * The point is, if content in **rax** is equal to **qword fs:0x28**, then **je** is executed. If they are equal, here it is jumping to **func+0x44** which is **leave** instruction. 

        * If they are not equal, then this instruction **call   4004a0 < __stack_chk_fail@plt >** is executed. This is a library function which we have never encountered before. It's name is **__stack_chk_fail**. It means, if Stack check fails, execute it. 

    
    * Hold on. This is what we saw now. 

        * A qword from **fs:0x28** is copied into **rbp-0x8**. 
        
        * The actual function is executed. 

        * The 8 bytes at **rbp-0x8** is compared with **fs:0x28**. We now have to proceed depending on if they are equal or not. 

        * Are you seeing what I am seeing? You copy some value at **fs:0x28** into **rbp-0x8**. You again compare those 2 and check if they are equal or not. Don't you think they are always equal? They should be right because they simply are the same values. Let us check this out in more detail. 
    
5. Let us run the program **vuln_normal** to understand what these new instructions do. 

        rev_eng_series/post_13$ gdb -q vuln_normal
        Reading symbols from vuln_normal...(no debugging symbols found)...done.
        gdb-peda$ b func
        Breakpoint 1 at 0x4005da
        gdb-peda$ 

    * Consider the following state of the program: 

            [----------------------------------registers-----------------------------------]
            RAX: 0x0 
            RBX: 0x0 
            RCX: 0x7ffff7b042c0 (<__write_nocancel+7>:	cmp    rax,0xfffffffffffff001)
            RDX: 0x7ffff7dd3780 --> 0x0 
            RSI: 0x602010 ("Before calling func\n")
            RDI: 0x1 
            RBP: 0x7fffffffda40 --> 0x7fffffffda50 --> 0x400650 (<__libc_csu_init>:	push   r15)
            RSP: 0x7fffffffd9c0 --> 0x602010 ("Before calling func\n")
            RIP: 0x4005de (<func+8>:	mov    rax,QWORD PTR fs:0x28)
            R8 : 0x602000 --> 0x0 
            R9 : 0xd ('\r')
            R10: 0x7ffff7dd1b78 --> 0x602410 --> 0x0 
            R11: 0x246 
            R12: 0x4004e0 (<_start>:	xor    ebp,ebp)
            R13: 0x7fffffffdb30 --> 0x1 
            R14: 0x0 
            R15: 0x0
            EFLAGS: 0x207 (CARRY PARITY adjust zero sign trap INTERRUPT direction overflow)
            [-------------------------------------code-------------------------------------]
            0x4005d6 <func>:	push   rbp
            0x4005d7 <func+1>:	mov    rbp,rsp
            0x4005da <func+4>:	add    rsp,0xffffffffffffff80
            => 0x4005de <func+8>:	mov    rax,QWORD PTR fs:0x28
            0x4005e7 <func+17>:	mov    QWORD PTR [rbp-0x8],rax
            0x4005eb <func+21>:	xor    eax,eax
            0x4005ed <func+23>:	mov    DWORD PTR [rbp-0x74],0x0
            0x4005f4 <func+30>:	lea    rax,[rbp-0x70]
            [------------------------------------stack-------------------------------------]
            0000| 0x7fffffffd9c0 --> 0x602010 ("Before calling func\n")
            0008| 0x7fffffffd9c8 --> 0x7fffffffdb30 --> 0x1 
            0016| 0x7fffffffd9d0 --> 0x0 
            0024| 0x7fffffffd9d8 --> 0x7ffff7a87409 (<_IO_new_do_write+121>:	mov    r13,rax)
            0032| 0x7fffffffd9e0 --> 0x0 
            0040| 0x7fffffffd9e8 --> 0x7ffff7dd2620 --> 0xfbad2a84 
            0048| 0x7fffffffd9f0 --> 0xa ('\n')
            0056| 0x7fffffffd9f8 --> 0x4006d4 ("Before calling func")
            [------------------------------------------------------------------------------]
            Legend: code, data, rodata, value
            0x00000000004005de in func ()
            gdb-peda$ 

    * The instruction **mov    rax,QWORD PTR fs:0x28** is yet to be executed. Let us now checkout the value of the segment register **fs**. 

            gdb-peda$ i r fs
            fs             0x0	0x0

    * In [this](https://www.pwnthebox.net/reverse/engineering/and/binary/exploitation/series/2018/08/12/introduction-to-x86-assembly-programming.html) I have discussed what Segmentation is and how segment registers work. In 64-bit OSs, Segmentation is not used but Segment Registers(cs, ds, es, fs, gs, ss) are used for special purposes. 

    * In this case, we see that value in the Segment Register **fs** is **0**. So, fs:0x28 results in the address 0x28. Try finding what is present at the address 0x28. 

            gdb-peda$ x/10x 0x28
            0x28:	Cannot access memory at address 0x28

    * So, what is happening here? Is our program accessing an address that is outside of the address space? As far as I know, every Segment Register has a Base Register and a Limit Register which are **not visible** to the process. So, when fs:0x28 is accessed, essentially the BaseAddress(stored in Base Register) is added to **0x28**. The Sum / new address is checked against the Address present in Limit Register. If the Address is within Limit, then that data can be accessed. You can go through [this stackoverflow answer](https://stackoverflow.com/questions/33370110/where-base-and-limit-registers-are-located)  to understand this. 

    * So, the process is **not** accessing data at address **0x28**. It is instead accessing data at the address HiddenBaseAddress + 0x28. The OS knows the HiddenBaseAddress and it will fetch the required data and give it to the process. 

    * Let us execute that instruction. This is what **rax** has now. 

            [----------------------------------registers-----------------------------------]
            RAX: 0x9c75fc6824bbf500 

    * It looks like some random 8-byte number. Note that the value will mostly be different for you. 

    * It is then placed at the  memory location **rbp-0x8**.  

            gdb-peda$ x/2x $rbp-0x8
            0x7fffffffda38:	0x24bbf500	0x9c75fc68
            gdb-peda$ 

    * Let us take a look at the stackframe of **func**. Note that Address of **buffer** is **rbp-0x70**. 

            gdb-peda$ x/40xw $rsp
            0x7fffffffd9c0:	0x00602010	0x00000000	0xffffdb30	0x00007fff
            0x7fffffffd9d0:	0x00000000	0x00000000	0xf7a87409	0x00007fff
            0x7fffffffd9e0:	0x00000000	0x00000000	0xf7dd2620	0x00007fff
            0x7fffffffd9f0:	0x0000000a	0x00000000	0x004006d4	0x00000000
            0x7fffffffda00:	0xffffdb30	0x00007fff	0xf7a8781b	0x00007fff
            0x7fffffffda10:	0x00000013	0x00000000	0xf7dd2620	0x00007fff
            0x7fffffffda20:	0x004006d4	0x00000000	0xf7a7c7fa	0x00007fff
            0x7fffffffda30:	0x00000000	0x00000000	0x24bbf500	0x9c75fc68
            0x7fffffffda40:	0xffffda50	0x00007fff	0x00400634	0x00000000
            0x7fffffffda50:	0x00400650	0x00000000	0xf7a2d830	0x00007fff

            gdb-peda$ print $rbp-0x74
            $2 = (void *) 0x7fffffffd9cc

    * The StackFrame looks something like this. 

            <var - 4 bytes><Buffer - 100 bytes><Padding - 4 bytes><8-byte random number><Old rbp - 8 bytes><Return Address - 8 bytes>
    

    * When **gets** is executed, you have control of the complete StackFrame except the **var** - 4 bytes. 

    * Let us continue our analysis. 

            [-------------------------------------code-------------------------------------]
            0x4005f4 <func+30>:	lea    rax,[rbp-0x70]
            0x4005f8 <func+34>:	mov    rdi,rax
            0x4005fb <func+37>:	mov    eax,0x0
            => 0x400600 <func+42>:	call   0x4004c0 <gets@plt>
            0x400605 <func+47>:	nop
            0x400606 <func+48>:	mov    rax,QWORD PTR [rbp-0x8]
            0x40060a <func+52>:	xor    rax,QWORD PTR fs:0x28
            0x400613 <func+61>:	je     0x40061a <func+68>
            Guessed arguments:
            arg[0]: 0x7fffffffd9d0 --> 0x0 
            [------------------------------------stack-------------------------------------]
            0000| 0x7fffffffd9c0 --> 0x602010 ("Before calling func\n")
            0008| 0x7fffffffd9c8 --> 0xffffdb30 
            0016| 0x7fffffffd9d0 --> 0x0 
            0024| 0x7fffffffd9d8 --> 0x7ffff7a87409 (<_IO_new_do_write+121>:	mov    r13,rax)
            0032| 0x7fffffffd9e0 --> 0x0 
            0040| 0x7fffffffd9e8 --> 0x7ffff7dd2620 --> 0xfbad2a84 
            0048| 0x7fffffffd9f0 --> 0xa ('\n')
            0056| 0x7fffffffd9f8 --> 0x4006d4 ("Before calling func")
            [------------------------------------------------------------------------------]
            Legend: code, data, rodata, value
            0x0000000000400600 in func ()
            gdb-peda$ 
            aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa


    * Let us focus on the last few instructions starting from **mov    rax,QWORD PTR [ rbp-0x8 ]**. After execution, **rax** has that 8-byte random number - expected!

    * After executing **xor    rax,QWORD PTR fs:0x28**, the following is the state: 

            [----------------------------------registers-----------------------------------]
            RAX: 0x0 
            RBX: 0x0 
            RCX: 0x7ffff7dd18e0 --> 0xfbad2288 
            RDX: 0x7ffff7dd3790 --> 0x0 
            RSI: 0x60243e --> 0xa ('\n')
            RDI: 0x7fffffffd9ee --> 0xa0000 ('')
            RBP: 0x7fffffffda40 --> 0x7fffffffda50 --> 0x400650 (<__libc_csu_init>:	push   r15)
            RSP: 0x7fffffffd9c0 --> 0x602010 ("Before calling func\n")
            RIP: 0x400613 (<func+61>:	je     0x40061a <func+68>)
            R8 : 0x60243f --> 0x0 
            R9 : 0x0 
            R10: 0x57 ('W')
            R11: 0x246 
            R12: 0x4004e0 (<_start>:	xor    ebp,ebp)
            R13: 0x7fffffffdb30 --> 0x1 
            R14: 0x0 
            R15: 0x0
            EFLAGS: 0x246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
            [-------------------------------------code-------------------------------------]
            0x400605 <func+47>:	nop
            0x400606 <func+48>:	mov    rax,QWORD PTR [rbp-0x8]
            0x40060a <func+52>:	xor    rax,QWORD PTR fs:0x28
            => 0x400613 <func+61>:	je     0x40061a <func+68>
            | 0x400615 <func+63>:	call   0x4004a0 <__stack_chk_fail@plt>
            | 0x40061a <func+68>:	leave
            | 0x40061b <func+69>:	ret
            | 0x40061c <main>:	push   rbp
            |->   0x40061a <func+68>:	leave  
                0x40061b <func+69>:	ret
                0x40061c <main>:	push   rbp
                0x40061d <main+1>:	mov    rbp,rsp
                                                                            JUMP is taken
            [------------------------------------stack-------------------------------------]
            0000| 0x7fffffffd9c0 --> 0x602010 ("Before calling func\n")
            0008| 0x7fffffffd9c8 --> 0xffffdb30 
            0016| 0x7fffffffd9d0 ('a' <repeats 30 times>)
            0024| 0x7fffffffd9d8 ('a' <repeats 22 times>)
            0032| 0x7fffffffd9e0 ('a' <repeats 14 times>)
            0040| 0x7fffffffd9e8 --> 0x616161616161 ('aaaaaa')
            0048| 0x7fffffffd9f0 --> 0xa ('\n')
            0056| 0x7fffffffd9f8 --> 0x4006d4 ("Before calling func")
            [------------------------------------------------------------------------------]
            Legend: code, data, rodata, value
            0x0000000000400613 in func ()
            gdb-peda$ 


    * As expected, those 2 values are equal. rax is set to 0. And peda is telling us that the **JUMP is taken**. We had thought of this. 

    * Look at where it is jumping. It is jumping to **0x40061a < func+68 >:	leave**. What it is doing is **bypassing** the **__stack_chk_fail** function. 

    * From this, we can conclude that if the 8-bytes at **rbp-0x8** and **fs:0x28** are equal, then the function returns without any problem. Else, the program doesn't return. It calls **__stack_chk_fail**. 


    * Now obviously the thought is, how can we make sure **__stack_chk_fail** is called? Let us have a look at the StackFrame again. 

            <var - 4 bytes><Buffer - 100 bytes><Padding - 4 bytes><8-byte random number><Old rbp - 8 bytes><Return Address - 8 bytes>
    
    * It is clearly visible. There is gets to help us :P . Give a long enough input to overwrite that 8-byte random number. Job done!

    * Let us run the program and overwrite that 8-byte random number on stack. This is the  input I will be giving. 

            >>> 'a' * 104 + 'b' * 8
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabbbbbbbb'

    * Run the program again. In my program, these are the important addresses. Look at your gdb output and make a note of these addresses. 

            gdb-peda$ print $rbp-0x8            --- Address of 8-byte random number
            $1 = (void *) 0x7fffffffda38

            gdb-peda$ print $rbp-0x70           --- Address of buffer of 100 bytes
            $2 = (void *) 0x7fffffffd9d0

    * This time, the 8-byte random number = **0xbc2a6c2c01afcd00**

    * I entered the input. Consider the following state. 

            [----------------------------------registers-----------------------------------]
            RAX: 0x6262626262626262 ('bbbbbbbb')
            RBX: 0x0 
            RCX: 0x7ffff7dd18e0 --> 0xfbad2288 
            RDX: 0x7ffff7dd3790 --> 0x0 
            RSI: 0x602490 --> 0xa ('\n')
            RDI: 0x7fffffffda40 --> 0x7fffffffda00 ('a' <repeats 56 times>, "bbbbbbbb")
            RBP: 0x7fffffffda40 --> 0x7fffffffda00 ('a' <repeats 56 times>, "bbbbbbbb")
            RSP: 0x7fffffffd9c0 --> 0x602010 ("Before calling func\n")
            RIP: 0x40060a (<func+52>:	xor    rax,QWORD PTR fs:0x28)
            R8 : 0x602491 --> 0x0 
            R9 : 0x6161616161616161 ('aaaaaaaa')
            R10: 0x6161616161616161 ('aaaaaaaa')
            R11: 0x246 
            R12: 0x4004e0 (<_start>:	xor    ebp,ebp)
            R13: 0x7fffffffdb30 --> 0x1 
            R14: 0x0 
            R15: 0x0
            EFLAGS: 0x246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
            [-------------------------------------code-------------------------------------]
            0x400600 <func+42>:	call   0x4004c0 <gets@plt>
            0x400605 <func+47>:	nop
            0x400606 <func+48>:	mov    rax,QWORD PTR [rbp-0x8]
            => 0x40060a <func+52>:	xor    rax,QWORD PTR fs:0x28
            0x400613 <func+61>:	je     0x40061a <func+68>
            0x400615 <func+63>:	call   0x4004a0 <__stack_chk_fail@plt>
            0x40061a <func+68>:	leave  
            0x40061b <func+69>:	ret
            [------------------------------------stack-------------------------------------]
            0000| 0x7fffffffd9c0 --> 0x602010 ("Before calling func\n")
            0008| 0x7fffffffd9c8 --> 0xffffdb30 
            0016| 0x7fffffffd9d0 ('a' <repeats 104 times>, "bbbbbbbb")
            0024| 0x7fffffffd9d8 ('a' <repeats 96 times>, "bbbbbbbb")
            0032| 0x7fffffffd9e0 ('a' <repeats 88 times>, "bbbbbbbb")
            0040| 0x7fffffffd9e8 ('a' <repeats 80 times>, "bbbbbbbb")
            0048| 0x7fffffffd9f0 ('a' <repeats 72 times>, "bbbbbbbb")
            0056| 0x7fffffffd9f8 ('a' <repeats 64 times>, "bbbbbbbb")
            [------------------------------------------------------------------------------]
            Legend: code, data, rodata, value
            0x000000000040060a in func ()
            gdb-peda$ 

    * As expected, the 8-byte random number at **rbp-0x8** is overwritten by **bbbbbbbb** - Checkout the register **rax**. 

    * Now, obviously the **__stack_chk_fail** is executed. Let us step into that function. Let us see what it does. 

            [----------------------------------registers-----------------------------------]
            RAX: 0xde480e4e63cdaf62 
            RBX: 0x0 
            RCX: 0x7ffff7dd18e0 --> 0xfbad2288 
            RDX: 0x7ffff7dd3790 --> 0x0 
            RSI: 0x602490 --> 0xa ('\n')
            RDI: 0x7fffffffda40 --> 0x7fffffffda00 ('a' <repeats 56 times>, "bbbbbbbb")
            RBP: 0x7fffffffda40 --> 0x7fffffffda00 ('a' <repeats 56 times>, "bbbbbbbb")
            RSP: 0x7fffffffd9c0 --> 0x602010 ("Before calling func\n")
            RIP: 0x400615 (<func+63>:	call   0x4004a0 <__stack_chk_fail@plt>)
            R8 : 0x602491 --> 0x0 
            R9 : 0x6161616161616161 ('aaaaaaaa')
            R10: 0x6161616161616161 ('aaaaaaaa')
            R11: 0x246 
            R12: 0x4004e0 (<_start>:	xor    ebp,ebp)
            R13: 0x7fffffffdb30 --> 0x1 
            R14: 0x0 
            R15: 0x0
            EFLAGS: 0x282 (carry parity adjust zero SIGN trap INTERRUPT direction overflow)
            [-------------------------------------code-------------------------------------]
            0x400606 <func+48>:	mov    rax,QWORD PTR [rbp-0x8]
            0x40060a <func+52>:	xor    rax,QWORD PTR fs:0x28
            0x400613 <func+61>:	je     0x40061a <func+68>
            => 0x400615 <func+63>:	call   0x4004a0 <__stack_chk_fail@plt>
            0x40061a <func+68>:	leave  
            0x40061b <func+69>:	ret    
            0x40061c <main>:	push   rbp
            0x40061d <main+1>:	mov    rbp,rsp
            No argument
            [------------------------------------stack-------------------------------------]
            0000| 0x7fffffffd9c0 --> 0x602010 ("Before calling func\n")
            0008| 0x7fffffffd9c8 --> 0xffffdb30 
            0016| 0x7fffffffd9d0 ('a' <repeats 104 times>, "bbbbbbbb")
            0024| 0x7fffffffd9d8 ('a' <repeats 96 times>, "bbbbbbbb")
            0032| 0x7fffffffd9e0 ('a' <repeats 88 times>, "bbbbbbbb")
            0040| 0x7fffffffd9e8 ('a' <repeats 80 times>, "bbbbbbbb")
            0048| 0x7fffffffd9f0 ('a' <repeats 72 times>, "bbbbbbbb")
            0056| 0x7fffffffd9f8 ('a' <repeats 64 times>, "bbbbbbbb")
            [------------------------------------------------------------------------------]
            Legend: code, data, rodata, value
            0x0000000000400615 in func ()
            gdb-peda$ 

    * Let us break at **__stack_chk_fail**. 

            gdb-peda$ b __stack_chk_fail
            Breakpoint 2 at 0x7ffff7b260f0: file stack_chk_fail.c, line 28.

    * Let us checkout this function using the **x/** command. 


            gdb-peda$ x/40i 0x7ffff7b260f0
            => 0x7ffff7b260f0 <__stack_chk_fail>:	lea    rdi,[rip+0x7638a]        # 0x7ffff7b9c481
            0x7ffff7b260f7 <__stack_chk_fail+7>:	sub    rsp,0x8
            0x7ffff7b260fb <__stack_chk_fail+11>:	call   0x7ffff7b26100 <__GI___fortify_fail>
            0x7ffff7b26100 <__GI___fortify_fail>:	push   r12
            0x7ffff7b26102 <__GI___fortify_fail+2>:	push   rbp
            0x7ffff7b26103 <__GI___fortify_fail+3>:	mov    rbp,rdi
            0x7ffff7b26106 <__GI___fortify_fail+6>:	push   rbx
            0x7ffff7b26107 <__GI___fortify_fail+7>:	lea    rdi,[rip+0x7638b]        # 0x7ffff7b9c499
            0x7ffff7b2610e <__GI___fortify_fail+14>:	mov    ecx,0x5
            0x7ffff7b26113 <__GI___fortify_fail+19>:	mov    rsi,rbp
            0x7ffff7b26116 <__GI___fortify_fail+22>:	lea    r12,[rip+0x74b18]        # 0x7ffff7b9ac35
            0x7ffff7b2611d <__GI___fortify_fail+29>:	repz cmps BYTE PTR ds:[rsi],BYTE PTR es:[rdi]
            0x7ffff7b2611f <__GI___fortify_fail+31>:	seta   al
            0x7ffff7b26122 <__GI___fortify_fail+34>:	setb   dl
            0x7ffff7b26125 <__GI___fortify_fail+37>:	sub    eax,edx
            0x7ffff7b26127 <__GI___fortify_fail+39>:	movsx  eax,al
            0x7ffff7b2612a <__GI___fortify_fail+42>:	cmp    eax,0x1
            0x7ffff7b2612d <__GI___fortify_fail+45>:	sbb    ebx,ebx
            0x7ffff7b2612f <__GI___fortify_fail+47>:	add    ebx,0x2
            0x7ffff7b26132 <__GI___fortify_fail+50>:	nop    WORD PTR [rax+rax*1+0x0]
            0x7ffff7b26138 <__GI___fortify_fail+56>:	mov    rax,QWORD PTR [rip+0x2b01b9]        # 0x7ffff7dd62f8 <__libc_argv>
            0x7ffff7b2613f <__GI___fortify_fail+63>:	lea    rsi,[rip+0x76359]        # 0x7ffff7b9c49f
            0x7ffff7b26146 <__GI___fortify_fail+70>:	mov    rdx,rbp
            0x7ffff7b26149 <__GI___fortify_fail+73>:	mov    edi,ebx
            0x7ffff7b2614b <__GI___fortify_fail+75>:	mov    rcx,QWORD PTR [rax]
            0x7ffff7b2614e <__GI___fortify_fail+78>:	test   rcx,rcx
            0x7ffff7b26151 <__GI___fortify_fail+81>:	cmove  rcx,r12
            0x7ffff7b26155 <__GI___fortify_fail+85>:	xor    eax,eax
            0x7ffff7b26157 <__GI___fortify_fail+87>:	call   0x7ffff7a84510 <__libc_message>
            0x7ffff7b2615c <__GI___fortify_fail+92>:	jmp    0x7ffff7b26138 <__GI___fortify_fail+56>

    * It calls another function **__GI__fortify_fail**. Let us take up reversing and understanding this in another post. 

    * Let us just continue and see what we get. 

            gdb-peda$ continue
            Continuing.
            *** stack smashing detected ***: /home/adwi/ALL/rev_eng_series/post_13/vuln_normal terminated

            Program received signal SIGABRT, Aborted.

    * So, we understood that if the 8 bytes at on stack and fs:0x28 are not equal, then the program gets aborted. 

    * Come out of gdb, execute **vuln_normal** a few times with inputs of different lengths. 

6. Let us understand the use of terminating the program when the 8-byte random number on stack is corrupted. 

    * The StackFrame looks like this: 

            <var - 4 bytes><Buffer - 100 bytes><Padding - 4 bytes><8-byte random number><Old rbp - 8 bytes><Return Address - 8 bytes>
    
    * You see a gets in vuln_normal. You give an appropriate input in order to overwrite the Return Address. In the process of doing it, we are **corrupting** the 8-byte random number. You know what happens if it is corrupted - the program is killed right away. 

    * As you might be guessing, this is the first security feature of this post. As explained in the previous statement, if you want to overwrite the Return Address, the 8-byte random number is present to **protect** the program from **Control Flow Hijacking**. 

    * The 8-byte random number is called the **Stack Cookie** / **Stack Canary**. You might have read things like Corrupting the cookie, stealing the cookie etc., . They all mostly refer to this Stack Cookie. 

7. Let us do some analysis on the cookies

    * Run **vuln_normal** a few times and collect a few cookies. A few cookies I got are

            0xc28f23b1a1cc3b00
            0x6c02ea8837b9a700
            0x7af1b99401ed0100
            0xdb7bb12090585e00
            ----
    
    * You can see that they all are random. You cannot just collect the cookie using gdb and try to break the security feature. Because it is random, we will have to think of other methods to break it. 

    * Note that the last byte of all the cookie values is a **NULL byte** - 0x00. Why? 

        * Suppose I design a method to get the cookie value. A few vulnerable functions are sprintf, scanf, strcpy etc., They all identify the end of a string by a NULL character. Suppose your payload is like this:

                'a' * 104 + '\x00\x12\x23\x34\x45\x56\x67\x78' + 'bbbbbbbb' + NewAddress

        * Those functions see the **NULL byte** and it stops copying / taking input. So, exploit fail :( . 

    
    * This means we have a 56-bit number to find instead of 64-bit number. 2^56 = 72,057,594,037,927,936 - That is huge!


This is the Stack-Cookie security feature which is administered during compilation. I hope you have understood the meaning of **no-stack-protector** - the flag we used in many of the previous posts to understand BOFs. Because with the stack protector, we saw what is happening. It just doesn't allow us to do anything. So, we had to remove the stack protector before we started experimenting. 

8. Let us quickly look at a 32-bit example of this. Let us compile **vuln.c** to get a 32-bit executable. 

    * A few cookie values are

            0xcdaf9200
            0x21ef100
            0x91910100
            0xbeb08d00
    
    * It is a 4-byte number out of which 1 byte is a NULL byte. So, we have 24-bits left. That is 16777216 values. Looks getable. 


This was about the **Stack Cookie** security feature. The idea is simple. Before you overwrite Return Address, you first have to get the Cookie. If you don't get the correct cookie value, then it means the Stack Cookie is **corrupted** and program is terminated immediately. 

For full details, [this](/assets/2018-12-28-security-measures-by-os/StackGaurd.pdf) is the official paper which introduces Stack Cookie. It is called StackGaurd. Give it a read. It is just amazing!

## Non-Executable Stack

What we are doing is, we are understanding all the security features we disabled in previous posts. We used this compiler option **-z execstack** .  As you have seen, we used this option to make our **stack** executable. We did so because we injected code onto the stack and to execute it, the stack should be executable. 

This means, by default the Stack is **Non-Executable**. Why is that? Let us understand.  

1. Consider the program **vuln.c**  we wrote. You compile it normally. 

        rev_eng_series/post_13$ gcc vuln.c -o vuln
        vuln.c: In function ‘func’:
        vuln.c:8:2: warning: implicit declaration of function ‘gets’ [-Wimplicit-function-declaration]
        gets(buffer);
        ^
        /tmp/cc4p7E9O.o: In function `func':
        vuln.c:(.text+0x2b): warning: the `gets' function is dangerous and should not be used.

    * Run the program. 

            rev_eng_series/post_13$ ./vuln
            Before calling func

    * Let us go to **/proc** directory and check out the details of the address space. On my machine, vuln's PID = 16221. Let us go to /proc/PID. This is what the **maps** file had. 

            00400000-00401000 r-xp 00000000 08:02 5518106                            /home/adwi/ALL/rev_eng_series/post_13/vuln
            00600000-00601000 r--p 00000000 08:02 5518106                            /home/adwi/ALL/rev_eng_series/post_13/vuln
            00601000-00602000 rw-p 00001000 08:02 5518106                            /home/adwi/ALL/rev_eng_series/post_13/vuln
            0062a000-0064b000 rw-p 00000000 00:00 0                                  [heap]
            7f20c81f6000-7f20c83b6000 r-xp 00000000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7f20c83b6000-7f20c85b6000 ---p 001c0000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7f20c85b6000-7f20c85ba000 r--p 001c0000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7f20c85ba000-7f20c85bc000 rw-p 001c4000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7f20c85bc000-7f20c85c0000 rw-p 00000000 00:00 0
            7f20c85c0000-7f20c85e6000 r-xp 00000000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
            7f20c87ba000-7f20c87bd000 rw-p 00000000 00:00 0
            7f20c87e5000-7f20c87e6000 r--p 00025000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
            7f20c87e6000-7f20c87e7000 rw-p 00026000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
            7f20c87e7000-7f20c87e8000 rw-p 00000000 00:00 0
            7ffc0ba9c000-7ffc0babe000 rw-p 00000000 00:00 0                          [stack]
            7ffc0bb56000-7ffc0bb59000 r--p 00000000 00:00 0                          [vvar]
            7ffc0bb59000-7ffc0bb5b000 r-xp 00000000 00:00 0                          [vdso]

    * Look at the stack. It's permissions are **rw-**. So, you can read values off of it, you can write into it. But, you cannot execute stuff present in it. 


    * Now compile **vuln.c** with **-z execstack**. Check it's **/proc/PID/maps** file. You'll see that the stack's permissions is **rwx**. 

    * There is one small task for you. Compile **vuln.c** with just **-fno-stack-protector** and try exploiting it. You know how to inject shellcode, how to overwrite ReturnAddress of a function. 

    * You will see that you **can** inject code into the stack(buffer) but it gets executed, the process dies of a **Segmentation Fault**. 


This is the second security feature of today's post. Making Stack non-executable. Even if you are able to inject your shellcode into the stack, you just cannot execute it. Exploit fail :( . 

This is an example. This is applicable for heap also. If the buffer is in the heap, then instead of stack overflow, it'll be a heap overflow. If the heap is executable, we can run that code. 

The point to note is that if we can **write** into an address, then that address should be made **non-executable**. Why is this? If we are dealing with a vulnerable program, we can inject code into a part of address space(eg: stack), overwrite the ReturnAddress but it can **never** be executed because that part of address space is just non-executable. You can only read and write into it. 

Same is with address spaces with executable code. When you have executable in it, you can **never** write into it by default(unless you use an option to disable it). Suppose there are 100 instructions in a function. The first 30 instructions are vulnerable to an exploit which will help in overwriting a few instructions in the code segment. So, what I will do is I craft an exploit and overwrite the instructions started from the 31st instruction with my Reverse-TCP Shellcode. So, my Reverse-TCP Shellcode is executed without any problem. Note that this is possible only when an executable address space is writable. 

Because of these reasons, by default you will not find any address space in **maps** file with **rwx** permissions. It can **either** be **writable / executable** but cannot be both. I hope this point is clear. 

That is why this security feature is known as **W^X** or **W XOR X**. The XOR value of 2 operands is **1** only when one of them is 0 and other is 1. This is a simple way to signify that either W(write flag) should be 1 or X(execute flag) should be 1, but not both 1 at the same time. 

Microsoft called this feature **Data Execution Prevention / DEP**. 

Intel calls this feature **XD / Execute Disable**. This is because there is a **XD bit** set for all address spaces like stack, heap. 

It is also called **NX / No Execute** bit. 

There are different names given to this security technique but the concept is the same. 

This was about the **W XOR X** security feature. 

Now that we know this security technique, let us dig a little bit deeper. Let us see how we can set the permissions of a given address space. 

1. Consider the following program: 

        rev_eng_series/post_13$ cat mprotect.c 
        #include<sys/mman.h>
        #include<stdio.h>
        #include<unistd.h>

        int main() {

            printf("pid = %d, check the /proc/PID/maps file now\n", getpid());
            getchar();
            
            // The crux of this program!
            mprotect((void *)0x400000, 0x1000, PROT_READ | PROT_WRITE | PROT_EXEC);
            
            
            printf("Check that file again!\n");
            
            getchar();

            return 0;
        }

    * This is a simple program. It spits out it's PID - helpful! . It uses a function called **mprotect** or **memory protect**. This function is used to set the permissions of a given address space. 

2. The following is the manpage of **mprotect**. 

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


    * The function is pretty clear. This C library function is infact a wrapper to the **mprotect** system call. 

    * In this program, I am setting the 4096 bytes starting at address **0x400000** to **rwx**. 

3. Let us compile and execute the program. 

        rev_eng_series/post_13$ gcc mprotect.c 
        rev_eng_series/post_13$ ./a.out
        pid = 19465, check the /proc/PID/maps file now

    * The **maps** file: 

            00400000-00401000 r-xp 00000000 08:02 5518107                            /home/adwi/ALL/rev_eng_series/post_13/a.out
            00600000-00601000 r--p 00000000 08:02 5518107                            /home/adwi/ALL/rev_eng_series/post_13/a.out
            00601000-00602000 rw-p 00001000 08:02 5518107                            /home/adwi/ALL/rev_eng_series/post_13/a.out
            017e2000-01803000 rw-p 00000000 00:00 0                                  [heap]
            7f897b0d6000-7f897b296000 r-xp 00000000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7f897b296000-7f897b496000 ---p 001c0000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7f897b496000-7f897b49a000 r--p 001c0000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7f897b49a000-7f897b49c000 rw-p 001c4000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7f897b49c000-7f897b4a0000 rw-p 00000000 00:00 0 
            7f897b4a0000-7f897b4c6000 r-xp 00000000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
            7f897b69a000-7f897b69d000 rw-p 00000000 00:00 0 
            7f897b6c5000-7f897b6c6000 r--p 00025000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
            7f897b6c6000-7f897b6c7000 rw-p 00026000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
            7f897b6c7000-7f897b6c8000 rw-p 00000000 00:00 0 
            7ffea193e000-7ffea1960000 rw-p 00000000 00:00 0                          [stack]
            7ffea197d000-7ffea1980000 r--p 00000000 00:00 0                          [vvar]
            7ffea1980000-7ffea1982000 r-xp 00000000 00:00 0                          [vdso]
            ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]
    
    * Note that the **00400000-00401000** address space's permissions is **r-x**. It is non-writable as discussed. This is because this address space is the text segment - it contains machine code in it. 

    * Let us continue. Just press enter and you get this. 

            rev_eng_series/post_13$ ./a.out
            pid = 19465, check the /proc/PID/maps file now

            Check that file again!

    * Now, **mprotect** is executed. If it is successfully executed, then we should see **rwx** permissions in that address space. The following is the maps file: 

            rev_eng_series/post_13$ cat /proc/19465/maps
            00400000-00401000 rwxp 00000000 08:02 5518107                            /home/adwi/ALL/rev_eng_series/post_13/a.out
            00600000-00601000 r--p 00000000 08:02 5518107                            /home/adwi/ALL/rev_eng_series/post_13/a.out
            00601000-00602000 rw-p 00001000 08:02 5518107                            /home/adwi/ALL/rev_eng_series/post_13/a.out
            017e2000-01803000 rw-p 00000000 00:00 0                                  [heap]
            7f897b0d6000-7f897b296000 r-xp 00000000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7f897b296000-7f897b496000 ---p 001c0000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7f897b496000-7f897b49a000 r--p 001c0000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7f897b49a000-7f897b49c000 rw-p 001c4000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7f897b49c000-7f897b4a0000 rw-p 00000000 00:00 0 
            7f897b4a0000-7f897b4c6000 r-xp 00000000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
            7f897b69a000-7f897b69d000 rw-p 00000000 00:00 0 
            7f897b6c5000-7f897b6c6000 r--p 00025000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
            7f897b6c6000-7f897b6c7000 rw-p 00026000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
            7f897b6c7000-7f897b6c8000 rw-p 00000000 00:00 0 
            7ffea193e000-7ffea1960000 rw-p 00000000 00:00 0                          [stack]
            7ffea197d000-7ffea1980000 r--p 00000000 00:00 0                          [vvar]
            7ffea1980000-7ffea1982000 r-xp 00000000 00:00 0                          [vdso]
            ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]
    
    * Bingo! Look at that change.

    * You can use **strace** to understand more. 

With this, let us end our discussion on the second security feature - W XOR X. We understood what it does, how it stops attacks. Even if you inject code into stack/heap, you cannot execute it. If you try executing it, the process is simply killed. 

## Address Space Layout Randomization 

At this point, I hope you know what an Address space is. **00400000-00401000** is an Address space, **7ffea193e000-7ffea1960000** is an address space. 

Note that a 64-bit process can have 2^64 addresses - 0x0000000000000000 to 0xffffffffffffffff . Not all addresses are valid. Out of 2^64 addresses, a bunch of addresses are valid. You can open up **maps** file and look at the valid Address Spaces. 

Layout is all Address Spaces put together in a particular manner. We have already discussed about Memory Layout of a process in [this](/reverse/engineering/and/binary/exploitation/series/2018/08/18/memory-layout-of-a-process.html) post. 

We now know what Address Space Layout. What does Randomization mean? It simply means randomize stuff. 

So, Address Space Layout Randomization(ASLR) means - randomize the address spaces. Let us take up an example to understand this better. 

1. Consider this program: 

        rev_eng_series/post_13$ cat aslr.c 
        #include<stdio.h>
        #include<unistd.h>
        int main() {

            printf("pid = %d\n", getpid());
            while(1);
            
        }
        rev_eng_series/post_13$ gcc aslr.c -o aslr

    * Understand the program. 

2. Let us execute the program a few times and look at the **/proc/PID/maps** file. I have shown **maps** file of 2 instances. 


    
        rev_eng_series/post_13$ cat /proc/21085/maps
        00400000-00401000 r-xp 00000000 08:02 5518108                            /home/adwi/ALL/rev_eng_series/post_13/aslr
        00600000-00601000 r--p 00000000 08:02 5518108                            /home/adwi/ALL/rev_eng_series/post_13/aslr
        00601000-00602000 rw-p 00001000 08:02 5518108                            /home/adwi/ALL/rev_eng_series/post_13/aslr
        006bc000-006dd000 rw-p 00000000 00:00 0                                  [heap]
        7fdc7e067000-7fdc7e227000 r-xp 00000000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
        7fdc7e227000-7fdc7e427000 ---p 001c0000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
        7fdc7e427000-7fdc7e42b000 r--p 001c0000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
        7fdc7e42b000-7fdc7e42d000 rw-p 001c4000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
        7fdc7e42d000-7fdc7e431000 rw-p 00000000 00:00 0 
        7fdc7e431000-7fdc7e457000 r-xp 00000000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
        7fdc7e62b000-7fdc7e62e000 rw-p 00000000 00:00 0 
        7fdc7e656000-7fdc7e657000 r--p 00025000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
        7fdc7e657000-7fdc7e658000 rw-p 00026000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
        7fdc7e658000-7fdc7e659000 rw-p 00000000 00:00 0 
        7fff6dbba000-7fff6dbdc000 rw-p 00000000 00:00 0                          [stack]
        7fff6dbec000-7fff6dbef000 r--p 00000000 00:00 0                          [vvar]
        7fff6dbef000-7fff6dbf1000 r-xp 00000000 00:00 0                          [vdso]
        ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]


        rev_eng_series/post_13$ cat /proc/21157/maps
        00400000-00401000 r-xp 00000000 08:02 5518108                            /home/adwi/ALL/rev_eng_series/post_13/aslr
        00600000-00601000 r--p 00000000 08:02 5518108                            /home/adwi/ALL/rev_eng_series/post_13/aslr
        00601000-00602000 rw-p 00001000 08:02 5518108                            /home/adwi/ALL/rev_eng_series/post_13/aslr
        01ee2000-01f03000 rw-p 00000000 00:00 0                                  [heap]
        7f3938204000-7f39383c4000 r-xp 00000000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
        7f39383c4000-7f39385c4000 ---p 001c0000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
        7f39385c4000-7f39385c8000 r--p 001c0000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
        7f39385c8000-7f39385ca000 rw-p 001c4000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
        7f39385ca000-7f39385ce000 rw-p 00000000 00:00 0 
        7f39385ce000-7f39385f4000 r-xp 00000000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
        7f39387c8000-7f39387cb000 rw-p 00000000 00:00 0 
        7f39387f3000-7f39387f4000 r--p 00025000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
        7f39387f4000-7f39387f5000 rw-p 00026000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
        7f39387f5000-7f39387f6000 rw-p 00000000 00:00 0 
        7ffdfa2ce000-7ffdfa2f0000 rw-p 00000000 00:00 0                          [stack]
        7ffdfa2fd000-7ffdfa300000 r--p 00000000 00:00 0                          [vvar]
        7ffdfa300000-7ffdfa302000 r-xp 00000000 00:00 0                          [vdso]
        ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]


    * You execute it a few more number of times and make note of what is different between each of the **maps** files. 

    * The Addresses of **text Segment** (00400000-00401000), **Read-Only**(00600000-00601000), **Data Segment**(00601000-00602000), **vsyscall**(ffffffffff600000-ffffffffff601000) remain the same. They never changed. This may not be the case in your machine. If it is not, I will be addressing it in a moment. 

    * Consider the rest of the address spaces - libc.so, ld.so, stack, vvar, aslr - they are being randomized. 

3. How will this help in mitigating attacks? 

    * Consider the shellcode injection using BOF. We injected the shellcode in a perfect location and then we had to jump to that **exact** location. We overwrote the ReturnAddress of a function with the address of shellcode. 

    * One problem we faced is how to find the exact location. To make our exploit more reliable, we used the **NOP-Sled**. 

    * Just have a look at the starting addresses of the stack in the above 2 memory maps. They are **7fff6dbba000** and **7ffdfa2ce000**. Their difference is 6233702400 bytes. Can we really have such a big NOP-sled to cover this randomness? That is impractical. So, exploit fail :( .

    * Code Injection is one exploit method. We will see other exploit methods in the coming posts which are also made difficult because of ASLR. 


4. What all does ASLR randomize? 

    * There are 3 levels of randomization. 

    * **Level2** : Randomize literally everything!

    * **Level1** : Randomize mmap base, stack and vdso spaces randomized.

    * **Level0** : Don't randomize anything. 

    * These levels can be seen like this: 

            rev_eng_series/post_13$ cat /proc/sys/kernel/randomize_va_space 
            2

        * If you recall what we did in earlier posts, we set this value to 0 - disable randomization and then start out experimentation.     

    * [This stackoverflow answer](https://stackoverflow.com/questions/11238457/disable-and-re-enable-address-space-layout-randomization-only-for-myself) is related to levels of randomization.


5. Why didn't text, data, read-only and vsyscall segments' address spaces didn't get randomized?  

    * As far as my knowledge, this is specific to different Linux Distributions like Ubuntu, Debian, Arch etc., In Ubuntu, by default these segments are not randomized(or fixed). 

    * For the Operating System to randomize any Segment's Address space, that segment has to be **Position Independent**. That is it should have **Position Independent Code**. 

    * In the above examples, the position of **text** segment was fixed to **0x400000 - 0x401000**. Similarly the other 2 segments' positions were also fixed. In most programs we wrote and compiled, this was the cases. These 3 segments' address spaces were fixed. 

    * The idea of Position Independent Code is that given some starting address **X** to the text segment, the address space X to X + 0x1000 should be the text segment. If X is random, then the address space of text segment is random => This way, the goal of randomizing the text segment is acheived. 

    * As we discussed before, by default the Address Spaces of text, data, read-only segment are fixed or NON-PIC. As they are fixed, they cannot be randomized. 

    * Let us first generate what are known as **Position Independent Executables / PIEs** which has Position Independent Code in it. 

    * We have the  **aslr.c**  program. Let us generate the executable in the following manner. 

            rev_eng_series/post_13$ gcc -fPIE -pie aslr.c -o aslr_pie

        * This will generate **aslr_pie** which has position independent code in it. 

        * To confirm this, we can use **readelf**. 

                rev_eng_series/post_13$ readelf -h aslr_pie 
                ELF Header:
                Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
                Class:                             ELF64
                Data:                              2's complement, little endian
                Version:                           1 (current)
                OS/ABI:                            UNIX - System V
                ABI Version:                       0
                Type:                              DYN (Shared object file)
                Machine:                           Advanced Micro Devices X86-64
                Version:                           0x1
                Entry point address:               0x670
                Start of program headers:          64 (bytes into file)
                Start of section headers:          6728 (bytes into file)
                Flags:                             0x0
                Size of this header:               64 (bytes)
                Size of program headers:           56 (bytes)
                Number of program headers:         9
                Size of section headers:           64 (bytes)
                Number of section headers:         31
                Section header string table index: 28


        * Look at the entry point. It has some address **0x670** and the type is **DYN** / Shared Object file. Normally, the executables are of the type EXEC but here this is of the type DYN. This means, it is dynamically linked at runtime. 

        * Do not get confused. Yes. We had discussed that functions of a Shared Library is dynamically linked. But we have actually leveled up - Security wise. We need randomization not only for stack, heap and shared libraries but for all other segments. 

    * Now, let us run **aslr_pie** and look at it's maps file. 

            rev_eng_series/post_13$ cat /proc/26457/maps
            558dc9a72000-558dc9a73000 r-xp 00000000 08:02 5518105                    /home/adwi/ALL/rev_eng_series/post_13/aslr_pie
            558dc9c72000-558dc9c73000 r--p 00000000 08:02 5518105                    /home/adwi/ALL/rev_eng_series/post_13/aslr_pie
            558dc9c73000-558dc9c74000 rw-p 00001000 08:02 5518105                    /home/adwi/ALL/rev_eng_series/post_13/aslr_pie
            558dcb11c000-558dcb13d000 rw-p 00000000 00:00 0                          [heap]
            7f6a66b75000-7f6a66d35000 r-xp 00000000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7f6a66d35000-7f6a66f35000 ---p 001c0000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7f6a66f35000-7f6a66f39000 r--p 001c0000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7f6a66f39000-7f6a66f3b000 rw-p 001c4000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7f6a66f3b000-7f6a66f3f000 rw-p 00000000 00:00 0 
            7f6a66f3f000-7f6a66f65000 r-xp 00000000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
            7f6a67139000-7f6a6713c000 rw-p 00000000 00:00 0 
            7f6a67164000-7f6a67165000 r--p 00025000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
            7f6a67165000-7f6a67166000 rw-p 00026000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
            7f6a67166000-7f6a67167000 rw-p 00000000 00:00 0 
            7ffccd1a5000-7ffccd1c7000 rw-p 00000000 00:00 0                          [stack]
            7ffccd1f8000-7ffccd1fb000 r--p 00000000 00:00 0                          [vvar]
            7ffccd1fb000-7ffccd1fd000 r-xp 00000000 00:00 0                          [vdso]
            ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]

    * Look at the address spaces. They are very different from the normal non-pic addresses we had encountered before. 

    * Let us run **aslr_pie** again. 

            rev_eng_series/post_13$ cat /proc/26585/maps
            55c06d342000-55c06d343000 r-xp 00000000 08:02 5518105                    /home/adwi/ALL/rev_eng_series/post_13/aslr_pie
            55c06d542000-55c06d543000 r--p 00000000 08:02 5518105                    /home/adwi/ALL/rev_eng_series/post_13/aslr_pie
            55c06d543000-55c06d544000 rw-p 00001000 08:02 5518105                    /home/adwi/ALL/rev_eng_series/post_13/aslr_pie
            55c06df78000-55c06df99000 rw-p 00000000 00:00 0                          [heap]
            7fea56e9d000-7fea5705d000 r-xp 00000000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7fea5705d000-7fea5725d000 ---p 001c0000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7fea5725d000-7fea57261000 r--p 001c0000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7fea57261000-7fea57263000 rw-p 001c4000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7fea57263000-7fea57267000 rw-p 00000000 00:00 0 
            7fea57267000-7fea5728d000 r-xp 00000000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
            7fea57461000-7fea57464000 rw-p 00000000 00:00 0 
            7fea5748c000-7fea5748d000 r--p 00025000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
            7fea5748d000-7fea5748e000 rw-p 00026000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
            7fea5748e000-7fea5748f000 rw-p 00000000 00:00 0 
            7fffe8210000-7fffe8232000 rw-p 00000000 00:00 0                          [stack]
            7fffe83dc000-7fffe83df000 r--p 00000000 00:00 0                          [vvar]
            7fffe83df000-7fffe83e1000 r-xp 00000000 00:00 0                          [vdso]
            ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]


    * There you go. Even they are randomized. 

6. What exactly is getting randomized here? 

    * As we discussed before, only the **Base Address** is randomized. Let us clearly understand what this mean. 

    * Consider the following example.  

        * libc.so Shared Library size = 0x50000 bytes   (not accurate, just an example)

    * Consider the complete Address Space of a process : 0x0000000000000000 - 0xffffffffffffffff. 

    * What does a libc.so contain? It has a huge list of Standard functions compiled together in 1 single file. Suppose libc.so is something like this: 

            0x000: printf
            0x020: scanf
            0x040: system
            0x060: getpid
            0x080: getchar
            0x100: gets

        * As this is a Shared Object, code inside it is dynamically linked. At runtime, an address is given to it. 

        * If ASLR is enabled, some random Base Address is given to libc.so . This way, addresses of all these functions seem random. 

        * But the point to note is, the functions inside libc.so are not randomized. They are all the same. What this means is, whether you randomize address space of libc.so or not, printf is always at offset 0x0 from beginning, scanf is always at offset 0x20 from beginning, system is always at offset 0x40 from beginning and so on.


We saw that any address space can be randomized.

This is the third security feature of this post - ASLR. It is about giving a random Base Address to every address space. 

It is important to understand these 3 features in good detail because they defend the system against different attacks. There are also attempts to bypass / defeat these methods. Because as the security techniques used become stronger, exploits focus on defeating them and then get control of the system. 

In the coming posts, we will see a whole new set of exploit methods which aims to defeat each of the security techniques. You will see how far we can go in defeating these techniques. 


So that was about the 3 important security measures administered by the Operating System. 


## A few important things

### 1. Where is the stack cookie stored? 

While we were experimenting with Stack Cookies, we came across the segment register **fs**. We got to know that the Stack Cookie is originally present at **fs:0x28**. We saw that **fs** has a value 0x0. We also discussed that every Segment Address is associated with Base Address. All this is theory. I wanted to findout where exactly the stack cookie is stored. One thing was for sure. As the program is able to access it, it **must** be present in it's Address space. 

**gdb** has this excellent feature of finding something in a process's address space. I used it to find it out. 

1. Open up **vuln_normal** in gdb. 

        rev_eng_series/post_13$ gdb -q vuln_normal
        Reading symbols from vuln_normal...(no debugging symbols found)...done.
        gdb-peda$ disass func
        Dump of assembler code for function func:
        0x00000000004005d6 <+0>:	push   rbp
        0x00000000004005d7 <+1>:	mov    rbp,rsp
        0x00000000004005da <+4>:	add    rsp,0xffffffffffffff80
        0x00000000004005de <+8>:	mov    rax,QWORD PTR fs:0x28
        0x00000000004005e7 <+17>:	mov    QWORD PTR [rbp-0x8],rax
        0x00000000004005eb <+21>:	xor    eax,eax
        0x00000000004005ed <+23>:	mov    DWORD PTR [rbp-0x74],0x0
        0x00000000004005f4 <+30>:	lea    rax,[rbp-0x70]
        0x00000000004005f8 <+34>:	mov    rdi,rax
        0x00000000004005fb <+37>:	mov    eax,0x0
        0x0000000000400600 <+42>:	call   0x4004c0 <gets@plt>
        0x0000000000400605 <+47>:	nop
        0x0000000000400606 <+48>:	mov    rax,QWORD PTR [rbp-0x8]
        0x000000000040060a <+52>:	xor    rax,QWORD PTR fs:0x28
        0x0000000000400613 <+61>:	je     0x40061a <func+68>
        0x0000000000400615 <+63>:	call   0x4004a0 <__stack_chk_fail@plt>
        0x000000000040061a <+68>:	leave  
        0x000000000040061b <+69>:	ret    
        End of assembler dump.
        gdb-peda$ b *0x00000000004005e7
        Breakpoint 1 at 0x4005e7

    * Let us run it and get the cookie value.  

            [----------------------------------registers-----------------------------------]
            RAX: 0xe9c6553f05b78900 
            RBX: 0x0 
            RCX: 0x7ffff7b042c0 (<__write_nocancel+7>:	cmp    rax,0xfffffffffffff001)
            RDX: 0x7ffff7dd3780 --> 0x0 
            RSI: 0x602010 ("Before calling func\n")
            RDI: 0x1 
            RBP: 0x7fffffffda50 --> 0x7fffffffda60 --> 0x400650 (<__libc_csu_init>:	push   r15)
            RSP: 0x7fffffffd9d0 --> 0x602010 ("Before calling func\n")
            RIP: 0x4005e7 (<func+17>:	mov    QWORD PTR [rbp-0x8],rax)
            R8 : 0x602000 --> 0x0 
            R9 : 0xd ('\r')
            R10: 0x7ffff7dd1b78 --> 0x602410 --> 0x0 
            R11: 0x246 
            R12: 0x4004e0 (<_start>:	xor    ebp,ebp)
            R13: 0x7fffffffdb40 --> 0x1 
            R14: 0x0 
            R15: 0x0
            EFLAGS: 0x203 (CARRY parity adjust zero sign trap INTERRUPT direction overflow)
            [-------------------------------------code-------------------------------------]
            0x4005d7 <func+1>:	mov    rbp,rsp
            0x4005da <func+4>:	add    rsp,0xffffffffffffff80
            0x4005de <func+8>:	mov    rax,QWORD PTR fs:0x28
            => 0x4005e7 <func+17>:	mov    QWORD PTR [rbp-0x8],rax
            0x4005eb <func+21>:	xor    eax,eax
            0x4005ed <func+23>:	mov    DWORD PTR [rbp-0x74],0x0
            0x4005f4 <func+30>:	lea    rax,[rbp-0x70]
            0x4005f8 <func+34>:	mov    rdi,rax
            [------------------------------------stack-------------------------------------]
            0000| 0x7fffffffd9d0 --> 0x602010 ("Before calling func\n")
            0008| 0x7fffffffd9d8 --> 0x7fffffffdb40 --> 0x1 
            0016| 0x7fffffffd9e0 --> 0x0 
            0024| 0x7fffffffd9e8 --> 0x7ffff7a87409 (<_IO_new_do_write+121>:	mov    r13,rax)
            0032| 0x7fffffffd9f0 --> 0x0 
            0040| 0x7fffffffd9f8 --> 0x7ffff7dd2620 --> 0xfbad2a84 
            0048| 0x7fffffffda00 --> 0xa ('\n')
            0056| 0x7fffffffda08 --> 0x4006d4 ("Before calling func")
            [------------------------------------------------------------------------------]
            Legend: code, data, rodata, value

            Breakpoint 1, 0x00000000004005e7 in func ()
            gdb-peda$

    * The cookie value is **0xe9c6553f05b78900**. 

    * Let us use the **find** feature of gdb. Let us find the cookie value. 

            gdb-peda$ find 0xe9c6553f05b78900
            Searching for '0xe9c6553f05b78900' in: None ranges
            Found 1 results, display max 1 items:
            mapped : 0x7ffff7fcd728 --> 0xe9c6553f05b78900 

    * Bingo! There it is. It is present at the address **0x7ffff7fcd728**. Note that you might get a different address and addresses can change. 

    * I wanted to see which address space it belongs to - stack, libc.so, ld.so or what. 

    * I got the PID from gdb and directly opened up the **maps** file. 

            gdb-peda$ getpid
            30001

    * The following is the **/proc/PID/maps** file: 

            rev_eng_series/post_13$ cat /proc/30001/maps
            00400000-00401000 r-xp 00000000 08:02 5518100                            /home/adwi/ALL/rev_eng_series/post_13/vuln_normal
            00600000-00601000 r--p 00000000 08:02 5518100                            /home/adwi/ALL/rev_eng_series/post_13/vuln_normal
            00601000-00602000 rw-p 00001000 08:02 5518100                            /home/adwi/ALL/rev_eng_series/post_13/vuln_normal
            00602000-00623000 rw-p 00000000 00:00 0                                  [heap]
            7ffff7a0d000-7ffff7bcd000 r-xp 00000000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7ffff7bcd000-7ffff7dcd000 ---p 001c0000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7ffff7dcd000-7ffff7dd1000 r--p 001c0000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7ffff7dd1000-7ffff7dd3000 rw-p 001c4000 08:02 25694643                   /lib/x86_64-linux-gnu/libc-2.23.so
            7ffff7dd3000-7ffff7dd7000 rw-p 00000000 00:00 0 
            7ffff7dd7000-7ffff7dfd000 r-xp 00000000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
            7ffff7fcc000-7ffff7fcf000 rw-p 00000000 00:00 0 
            7ffff7ff7000-7ffff7ffa000 r--p 00000000 00:00 0                          [vvar]
            7ffff7ffa000-7ffff7ffc000 r-xp 00000000 00:00 0                          [vdso]
            7ffff7ffc000-7ffff7ffd000 r--p 00025000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
            7ffff7ffd000-7ffff7ffe000 rw-p 00026000 08:02 25694615                   /lib/x86_64-linux-gnu/ld-2.23.so
            7ffff7ffe000-7ffff7fff000 rw-p 00000000 00:00 0 
            7ffffffdd000-7ffffffff000 rw-p 00000000 00:00 0                          [stack]
            ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]
                        
    * If you observe, the address falls in the **7ffff7fcc000-7ffff7fcf000 rw-p 00000000 00:00 0** address space. It doesn't have a specific name but is a valid address space. This is good because it always bugged me what is present in these unnamed address spaces. I got some answer for one of such address spaces. 

    * So, the cookie is present in a **rw-** address space. 

    * I actually am not satisfied with what I have found out. Because Stack Cookie is something which is to be kept in a secure manner. I don't know how good it is to keep in a **writable** address space. If it is read-only, then it would be better. These are just my first thoughts. 

### 2. What other protection techniques can we use to keep our systems safe? 

First and foremost thing to do is to use Secure API. Know in detail about every Library function you use. The manpage is written especially for this reason. Open it up and spend some time reading it. If there are any identified bugs with a function, it will definitely be specified. From this you can either decide to use it or chuck it. 

There is a function called **memcpy**. The following is a part from it's manpage. 

    MEMCPY(3)                  Linux Programmer's Manual                 MEMCPY(3)

        NAME
            memcpy - copy memory area

        SYNOPSIS
            #include <string.h>

            void *memcpy(void *dest, const void *src, size_t n);

        DESCRIPTION
            The  memcpy()  function  copies  n bytes from memory area src to memory
            area dest.  The memory areas must not overlap.  Use memmove(3)  if  the
            memory areas do overlap.

        RETURN VALUE
            The memcpy() function returns a pointer to dest.

        ATTRIBUTES
            For   an   explanation   of   the  terms  used  in  this  section,  see
            attributes(7).

            ┌──────────┬───────────────┬─────────┐
            │Interface │ Attribute     │ Value   │
            ├──────────┼───────────────┼─────────┤
            │memcpy()  │ Thread safety │ MT-Safe │
            └──────────┴───────────────┴─────────┘
        CONFORMING TO
            POSIX.1-2001, POSIX.1-2008, C89, C99, SVr4, 4.3BSD.

        NOTES
            Failure to observe the requirement that the memory areas do not overlap
            has  been  the  source  of  real  bugs. 

It is a simple function. It copies certain number of bytes from source to destination. Unlike strcpy, it has an argument where you can specify the number of bytes to copy. Does this mean this is the best and will not open up the system with vulnerabilities? Let us checkout the CVE Database. Take a look at [this link](https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=memcpy). Most of them are BOFs causing SegFault or Arbitrary Code execution. You will realize that just specifying the number of bytes doesn't make your system secure. You have to make sure the user is not able to control it. 

### 3. Will Stack Cookie Technique mitigate all types of attacks? 

I am adding this section because I want to get into the Stack Cookie technique in a bit more detail. What we have understood is the Stack Cookie is corrupted when the attacker attempts to overwrite the Return Address. 

What if I don't have to perform Control Flow Hijacking to get control of the system? Let us consider this code snippet. 

    int main() {
        
        char buffer[100];
        int admin = 0;
        
        gets(buffer);
        
        if(admin)
                system("/bin/sh");
    }       
        
It is pretty simple. If **admin** value is non-zero, you get a shell. Here, there is no code which controls the value of admin. But we have our friend **gets** with us here. 

The StackFrame might look like this: 

    <buffer - 100 bytes><admin - 4 bytes>

The payload is straight forward. Just give an input of length > 100 bytes. You'll get a shell. 

So, the point to note from this example is, Stack Cookie protects your program from **Stack Smashing**. It doesn't detect corruption of any internal stack variables because it was not designed to do that. This is a very important point. One of the CTF problems had a name overflowme. I assumed that it would involve Control Flow Hijacking. But it had StackGaurd enabled. Then when I went through the disassembly, I got to know that the challenge required to corrupt one of such internal stack variables. 

How can we protect the program from this now? You should have already noticed. The compiler keeps all such variables before the buffer. You can notice it in **vuln_normal**. It's stackframe is something like this: 

    <var - 4 bytes><buffer - 100 bytes><padding - 4 bytes><8-byte Cookie>

So, even if you try to give a longer input, the **var** is safe. Thanks to the intelligent compiler.

###  4. Will W^X technique mitigate all types of attacks? 

If you closely observe, even this doesn't take care of corruption of internal stack variables. Take it for granted that the compiler takes care of it. 

This technique goes one step ahead of StackGaurd / Stack Cookie technique. Suppose somehow I break the StackGaurd by some method I designed to guess the cookie. I then return to the buffer where I have stored the shellcode. When it is executed, boom! You get a Segmentation Fault and process is killed. 

So, you can think of W^X as a gaurd for StackGaurd. It will work even if StackGaurd fails. 

### 5. Will ASLR mitigate all types of attacks? 

As I am thinking about this, this actually is the saviour of all. We saw the difference of the 2 addresses when you run the program twice. It is impossible to guess addresses because they are very random. If you plan to disable ASLR somehow, I am sorry. Only root can do it.

Let us see in future posts what we can do to get over this method. 

### 6. Comparision between Stack Cookie technique and W XOR X technique 

We saw both techniques end up in termination of the process. All this will have a cost. Let us see what it is. 

1. StackGaurd

    * The Stack Cookie technique introduces 6 new instructions in the main code of a function. The **__stack_chk_fail** function calls another function. That function calls another. There are lot of things that happen before the process is aborted. Check it out using gdb. 

    * So, this is definitely coming with a certain overhead - of having more code than you want.

    * The Stack Cookie is stored in the Address Space as we saw in one of the previous sections. So, that is 8 bytes of memory. I was curious if that Address Space where Stack Cookie is stored is being used for anything else. So, let us take a look at the **maps** file of **vuln_nostkp** - the executable which doesn't have the stack protector. Yes. That address space is still there. It means, it is being used for something else. 

    * To conclude, some overhead in terms of memory - instructions, **stack_chk_fail**, Cookie and factors I am not aware of at this point.

    * It will definitely use some CPU to execute those instructions to abort the program. 

2. W^X: 

    * It is infact a zero-penalty technique. 

For complete details, read the [StackGaurd paper](/assets/2018-12-28-security-features-by-os/StackGaurd.pdf). This has complete comparision. 


### 7. How good are these techniques? 

I would say they are really good. They save the system from being pwned. Then all have one thing in common. They focus on the root cause of the problems. 

Consider W ^ X. It invalidates every single attack that tries to store code and execute it. There are so many such attacks. 

Take ASLR. I am just amazed by it. It literally protects from all these attacks. 

So, a security technique should ideally be like this. A technique known to protect the system from one very specific doesn't help in long run because we would have 100s of techniques to be administered for every small vulnerability. 


### 8. Is this the best we can do? 

All the techniques end up in a Segmentation Fault. We know that even Segmentation Fault is a good unintended behavior for a program. We can DOS the programs by continuously giving inputs that will cause it to segfault. If you open the CVE Database(Common Vulnerability and Exposure), you will see that so many BOFs end up being used as DOS attacks if all these security techniques are enabled. 

Yes. The attacker didn't get the shell. They didn't pwn our server. But Server dying is definitely not we want. So, definitely research is required in this area to come up with better techniques. 

## Conclusion

I hope you are now able to appreciate the security features, why we disabled them in previous posts. 

In the coming posts, we will be discussing new exploit methods which aim to break each of these security techniques. Let us see how far we can go in defeating them. 

So, that is it for this post. This turned out to be one more long post. I thought there are only 3 security features to be discussed but as I wrote the article, it became big. This post in particular will be updated continuously. 

 I learnt a lot while writing this post. I hope you learnt something from it.

 Thank you for reading :)





