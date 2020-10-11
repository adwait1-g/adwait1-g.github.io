---
title: Startup
categories: Rust
comments: true
layout: post
---

This sub-topic explores all the things which happen before Rust's ```main()``` function is called.

Make sure you have the rust toolchain before continuing. You can download it from [here](https://www.rust-lang.org/tools/install). In case you don't have sudo access, you can use [rustenv](https://pypi.org/project/rustenv/). [This]() post explains how to setup the rust toolchain using rustenv.

A simple hello program is used.
```rust
rust/Rust-C-experiments/startup > cat hello.rs
fn main()
{
    println!("Hello World!");
}
rust/Rust-C-experiments/startup > rustc hello.rs
rust/Rust-C-experiments/startup > ./hello
Hello World!
rust/Rust-C-experiments/startup > objdump -Mintel -D hello > hello.obj
```

The complete analysis will be done by reading through the objdump output and running the program through gdb.

##  Where does it all start?

Every executable should have a starting point - an address(or an associated symbol) where the executable's first instruction is present. In C programs, the ```_start** symbol is the starting point. Let us checkout the entry-point address using readelf.
```
rust/Rust-C-experiments/startup > readelf -h hello
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
  Entry point address:               0x7fe0
  Start of program headers:          64 (bytes into file)
  Start of section headers:          3196264 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           56 (bytes)
  Number of program headers:         10
  Size of section headers:           64 (bytes)
  Number of section headers:         41
  Section header string table index: 40
```

The address(relative address to be precise) is 0x7fe0. Let us checkout this address in the objdump output.
```asm
Disassembly of section .text:                                                   
                                                                                
0000000000007fe0 <_start>:                                                      
    7fe0:   31 ed                   xor    ebp,ebp                              
    7fe2:   49 89 d1                mov    r9,rdx                               
    7fe5:   5e                      pop    rsi                                  
    7fe6:   48 89 e2                mov    rdx,rsp                              
    7fe9:   48 83 e4 f0             and    rsp,0xfffffffffffffff0               
    7fed:   50                      push   rax                                  
    7fee:   54                      push   rsp                                  
    7fef:   4c 8d 05 aa 03 03 00    lea    r8,[rip+0x303aa]        # 383a0 <__libc_csu_fini>
    7ff6:   48 8d 0d 33 03 03 00    lea    rcx,[rip+0x30333]        # 38330 <__libc_csu_init>
    7ffd:   48 8d 3d 0c 03 00 00    lea    rdi,[rip+0x30c]        # 8310 <main>  
    8004:   e8 77 ff ff ff          call   7f80 <__libc_start_main@plt>         
    8009:   f4                      hlt                                         
    800a:   66 0f 1f 44 00 00       nop    WORD PTR [rax+rax*1+0x0]             
```

This code looks exactly like the one which is usually present in a C-compiled binary. It is even calling ```__libc_start_main```. In C-compiled binaries, ```__libc_start_main``` calls the main function defined in C-compiled program. Even here, it is calling a ```main``` function at 0x8310. Let us checkout what this ```main``` function is.

```asm
000000000008310 <main>:                                                        
    8310:   50                      push   rax                                  
    8311:   48 63 c7                movsxd rax,edi                              
    8314:   48 8d 3d a5 ff ff ff    lea    rdi,[rip+0xffffffffffffffa5]        # 82c0 <_ZN5hello4main17h391fdbb81e062d23E>
    831b:   48 89 34 24             mov    QWORD PTR [rsp],rsi                  
    831f:   48 89 c6                mov    rsi,rax                              
    8322:   48 8b 14 24             mov    rdx,QWORD PTR [rsp]                  
    8326:   e8 25 fe ff ff          call   8150 <_ZN3std2rt10lang_start17h7b7d3f0af67fc97cE>
    832b:   59                      pop    rcx                                  
    832c:   c3                      ret                                         
    832d:   0f 1f 00                nop    DWORD PTR [rax]      
```

This looks exactly like the ```main``` function present in a C-compiled executable. Let us take a close look at the function.

1. The C/C++'s ```main``` function generally takes two arguments: ```argc``` which is the argument count and ```argv``` which is the argument vector. In x64 linux binaries, first argument to any function is passed through the **rdi** register and the second is passed through the **rsi** register. Now let us go through the first couple of lines.
    ```asm
        8311:   48 63 c7                movsxd rax,edi                              
        8314:   48 8d 3d a5 ff ff ff    lea    rdi,[rip+0xffffffffffffffa5]        # 82c0 <_ZN5hello4main17h391fdbb81e062d23E>
        831b:   48 89 34 24             mov    QWORD PTR [rsp],rsi                  
        831f:   48 89 c6                mov    rsi,rax                              
        8322:   48 8b 14 24             mov    rdx,QWORD PTR [rsp]      
        8326:   e8 25 fe ff ff          call   8150 <_ZN3std2rt10lang_start17h7b7d3f0af67fc97cE>
    ```
- Because ```argc``` is of type int(32-bits), the edi sub-register(which constitutes of rdi's lower 32-bits) is signed extended(**sxd** in movsxd) and moved to rax.
- The address of some function ```_ZN5hello4main17h391fdbb81e062d23E``` is loaded into **rdi**.
- rsi - which points to the argument vector is loaded into a local variable in ```mov    QWORD PTR [rsp],rsi ```.
- rax OR ```argc``` is loaded into the rsi register.
- Finally, the argv OR the contents of that local variable is loaded into the **rdx** register.
- Then another function is called.

To summarize, the following is happening.
```asm
call _ZN3std2rt10lang_start17h7b7d3f0af67fc97cE(_ZN5hello4main17h391fdbb81e062d23E, argc, argv);
```

Those two symbols clearly look mangled. You might have seen such symbols in C++ binaries. If you take a look at the text part of the mangled symbols, it looks like this.
```asm
call std::rt::lang_start(hello::main, argc, argv);
```

That is neat isn't it?!

So this ```main``` function is still like the C main function and NOT the Rust main function. The rust main function is actually ```hello::main```. From this, it is clear that the rust's main function or rust's entry point is not directly called. I am guessing that ```std::rt::lang_start``` initializes the rust-lang runtime. Once that is done, the main function is called.

Let us fast forward to the place where our ```hello::main``` is called. Following the trail from here to the point where the call to ```hello::main``` is hard using objdump output. You can simply run it in gdb and catch the trail. Set a breakpoint at ```hello::main``` and get the backtrace.

```
#0  0x000055555555c2c0 in hello::main::h391fdbb81e062d23 ()
#1  0x000055555555c263 in core::ops::function::FnOnce::call_once::h6d508c60b417b782 ()
#2  0x000055555555c1c9 in std::sys_common::backtrace::__rust_begin_short_backtrace::hce0ef0fbfe872a02 ()
#3  0x000055555555c1a9 in std::rt::lang_start::_$u7b$$u7b$closure$u7d$$u7d$::h2dbdfbdebcc074cd ()
#4  0x0000555555571c01 in call_once<(),Fn<()>> () at /rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39/library/core/src/ops/function.rs:259
#5  do_call<&Fn<()>,i32> () at library/std/src/panicking.rs:373
#6  try<i32,&Fn<()>> () at library/std/src/panicking.rs:337
#7  catch_unwind<&Fn<()>,i32> () at library/std/src/panic.rs:379
#8  std::rt::lang_start_internal::h73711f37ecfcb277 () at library/std/src/rt.rs:51
#9  0x000055555555c188 in std::rt::lang_start::h7b7d3f0af67fc97c ()
#10 0x000055555555c32b in main ()
```

In more human-readable form,

1. _start <-- The actual entry-point of any linux executable. All the code before ```main``` initializes the C runtime.
2. main   <-- Any C/C++ programmer's entry point to the program.
3. std::rt::lang_start <-- All the code before ```hello::main``` initializes the Rust runtime.
4. A bunch of other functions part of rust-runtime initialization.
5. hello::main

That was a vanilla introduction to Rust startup. Intention is to understand more about Rust in general and then come back to understand the Rust runtime initialization. This post will be extended or another post under the same name will describe more internal details about the Rust runtime.
