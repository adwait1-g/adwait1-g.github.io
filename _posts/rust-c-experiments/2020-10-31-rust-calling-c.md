# Rust calling C

When integrating C libraries into Rust, there should be a way to call C functions, use C structures from Rust. This post explores how to make this happen.

## 1. Simple example

Lets take the following header file.

```c
rust/Rust-C-experiments/rust-calling-c > cat word.h
#ifndef __WORD_H__
#define __WORD_H__

#include <stdbool.h>

typedef struct word_info
{
    char *word;
    bool validity;
} word_info_t;


char* get_word(word_info_t *w_info);

bool get_validity(word_info_t *w_info);


#endif /* __WORD_H__ */
```

Just having header file doesn't work, we need to implement those two functions, put them in a **libword.so**. The C code is fairly straight-forward.

```c
rust/Rust-C-experiments/rust-calling-c > cat word.c
#include <stdio.h>
#include "word.h"
#include <stdbool.h>

char *get_word (word_info_t *w_info)
{
    if (w_info == NULL)
    {
        return NULL;
    }

    return w_info->word;
}

bool get_validity (word_info_t *w_info)
{
    if (w_info == NULL)
    {
        return false;
    }

    return w_info->validity;
}
```

Let us make a shared library out of it.

```
rust/Rust-C-experiments/rust-calling-c > gcc -c word.c -fPIC
rust/Rust-C-experiments/rust-calling-c > gcc word.o -o libword.so -shared
```

Ideally, we need to make sure the library works - by writing test C programs. But we'll take it for granted and come back if there is an issue. There is one confirmation we can get using the ```readelf``` tool.

```
rust/Rust-C-experiments/rust-calling-c > readelf -s libword.so | grep get
     8: 00000000000006a4    32 FUNC    GLOBAL DEFAULT   11 get_validity
    10: 0000000000000685    31 FUNC    GLOBAL DEFAULT   11 get_word
    48: 00000000000006a4    32 FUNC    GLOBAL DEFAULT   11 get_validity
    50: 0000000000000685    31 FUNC    GLOBAL DEFAULT   11 get_word
```

The ```GLOBAL``` indicates that these functions are exposed to the outside world and other people can call it.

Goal is to able to use that structure in Rust - create new instances, manipulate them, call those functions from Rust. It is not just about using them in Rust, but when we pass an instance of ```word_info``` creating in Rust land to C(basically when we call ```get_word``` or ```get_validity```), C should be able to understand that instance as well.

Let us write a rust file which resembles the C header file.

Starting with the ```word_info_t``` structure,

1. We create an instance of ```word_info_t``` in Rustland and send it to Cland. Cland should be able to understand it. For that, Rust needs to laydown the members of the structure the way C would laydown in memory - basically, the memory layout needs to be like C memory layout.
    - To make this happen, Rust provides ```#[repr(C)]```.

2. Second condition for C to understand our instance is that, the members need to be C-like. We can't pass Rust's String and expect C to understand it.
    - For this, we can use [c_char](https://doc.rust-lang.org/std/os/raw/type.c_char.html). Rust's bool is same as C's bool.

Let us go ahead and define the struct.

```rust
rust/Rust-C-experiments/rust-calling-c > cat word.rs
use std::os::raw::c_char;

#[repr(C)]
pub struct word_info_t
{
    pub word: *const c_char,
    pub validity: bool,
}
```

The ```struct``` is fairly straight-forward. You need to add ```pub``` everywhere because they are all private fields by default. Now, let us go ahead and declare those two C functions in Rust form.

1. Generally, the compiler searches for the function definition. But here, we don't have it. It is present in the shared library. How do we convey this to the compiler?
    - ```extern``` keyword can be used.

2. Every language has a certain way of calling functions. It will follow a convention or a set rule on things like
    - How to pass arguments to the callee function - should I use the stack or the registers or both etc., There will be some rule.
    - How should the callee send back the return value
    - And many more such rules.
Rust might be following a certain convention to call other Rust functions. But, when Rust calls a C function, it can't call it the way it calls a Rust function. It needs to follow the rules of the C programming language here. How do we convey this info to the compiler?

- The ```"C"``` can be used. All in all, ```extern "C"``` should get the job done.

Just as a side note, the conventions/rules are called the ABI - Application Binary Interface. Each language has it - but it is not really a language property/trait. It is a property of (language, OS, processor architecture etc.,). There can't be one rule like this: I will pass all arguments through registers. Because in some platform like x86, there are just 8 general purpose registers and they cannot be used for passing arguments. So, ABI is written keeping a lot of things in mind.

Coming back, lets declare these two functions.

```rust
extern "C"
{
    pub fn get_word (w_info: *const word_info_t) -> *const c_char;
    pub fn get_validity (w_info: *const word_info_t) -> bool;
}
```

Note that the functions should be made public explicitly.

Now we have the basic stuff setup.

We need some function which creates an instance of ```word_info_t``` and calls these functions - to test if this works. Open up a ```main.rs```.

How do we declare C-like strings in Rust? The Rust FFI (Foreign Function Interface) offers the ```CString``` type. Let us create a ```CString``` now.

```rust
fn main()                                                                       
{                                                                               
    /* Create a CString */                                                      
    let cstr = CString::new("Cisco!").expect("CString::new() failed");
```

Note that ```main``` owns the CString here. There is one more type called ```CStr``` which we will talk about later.

Now, let us create a ```word_info_t``` structure.

```rust
    let w_info = word::word_info_t                                              
    {                                                                           
        word: cstr.as_ptr(),                                                    
        validity: false,                                                        
    };
```

That is how powerful ```CString``` is. A reference to it can be generated using ```as_ptr()```.

Now the last part: Calling these functions.

```rust
    unsafe                                                                      
    {                                                                           
        println!("word: {:?}, validity: {:?}", word::get_word(&w_info), word::get_validity(&w_info));
    };
```

The following is the full listing of **main.rs**.

```rust
rust/Rust-C-experiments/rust-calling-c > cat main.rs
mod word;
use std::ffi::CString;

fn main()
{
    /* Create a CString */
    let cstr = CString::new("Cisco!").expect("CString::new() failed");
    let w_info = word::word_info_t
    {
        word: cstr.as_ptr(),
        validity: false,
    };

    unsafe
    {
        println!("word: {:?}, validity: {:?}", word::get_word(&w_info), word::get_validity(&w_info));
    };
}
```

With that, let us try compiling now.

```
rust/Rust-C-experiments/rust-calling-c > rustc main.rs
error: linking with `cc` failed: exit code: 1
  |
  = note: "cc" "-Wl,--as-needed" "-Wl,-z,noexecstack" "-m64" "-Wl,--eh-frame-hdr" "-L" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib" "main.main.7rcbfp3g-cgu.0.rcgu.o" "main.main.7rcbfp3g-cgu.1.rcgu.o" "main.main.7rcbfp3g-cgu.10.rcgu.o" "main.main.7rcbfp3g-cgu.11.rcgu.o" "main.main.7rcbfp3g-cgu.12.rcgu.o" "main.main.7rcbfp3g-cgu.13.rcgu.o" "main.main.7rcbfp3g-cgu.14.rcgu.o" "main.main.7rcbfp3g-cgu.15.rcgu.o" "main.main.7rcbfp3g-cgu.2.rcgu.o" "main.main.7rcbfp3g-cgu.3.rcgu.o" "main.main.7rcbfp3g-cgu.4.rcgu.o" "main.main.7rcbfp3g-cgu.5.rcgu.o" "main.main.7rcbfp3g-cgu.6.rcgu.o" "main.main.7rcbfp3g-cgu.7.rcgu.o" "main.main.7rcbfp3g-cgu.8.rcgu.o" "main.main.7rcbfp3g-cgu.9.rcgu.o" "-o" "main" "main.4s37gsrti678ik8u.rcgu.o" "-Wl,--gc-sections" "-pie" "-Wl,-zrelro" "-Wl,-znow" "-nodefaultlibs" "-L" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib" "-Wl,--start-group" "-Wl,-Bstatic" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/libstd-f14aca24435a5414.rlib" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/libpanic_unwind-48d342a8b48d1d01.rlib" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/libminiz_oxide-14bc0820888c8eb3.rlib" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/libadler-9cbd9e217bff06bc.rlib" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/libobject-31826136df98934e.rlib" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/libaddr2line-075976a117c8fd5d.rlib" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/libgimli-2d5cbedfbf17a011.rlib" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/librustc_demangle-0474372ff08c5319.rlib" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/libhashbrown-d437c34460d2315a.rlib" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/librustc_std_workspace_alloc-fb61ed1b8cc4de79.rlib" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/libunwind-bf76d1b643bfc9f0.rlib" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/libcfg_if-a1b53aa7fddcf418.rlib" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/liblibc-28585e57fac45c73.rlib" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/liballoc-64801769bc15ab28.rlib" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/librustc_std_workspace_core-541997b56bb98660.rlib" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/libcore-cdea3c81adab3d12.rlib" "-Wl,--end-group" "/nobackup/agautham/rust/renv/rust/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/libcompiler_builtins-cd9f15a39fb65cbc.rlib" "-Wl,-Bdynamic" "-ldl" "-lrt" "-lpthread" "-lgcc_s" "-lc" "-lm" "-lrt" "-lpthread" "-lutil" "-ldl" "-lutil"
  = note: main.main.7rcbfp3g-cgu.1.rcgu.o: In function `main::main::h2d6c3d678af9e020':
          main.7rcbfp3g-cgu.1:(.text._ZN4main4main17h2d6c3d678af9e020E+0xbb): undefined reference to `get_word'
          main.7rcbfp3g-cgu.1:(.text._ZN4main4main17h2d6c3d678af9e020E+0xd1): undefined reference to `get_validity'
          collect2: error: ld returned 1 exit status
          

error: aborting due to previous error
```

It says ```undefined reference``` to ```get_word``` and ```get_validity```. Does that make sense?

Rust just knows where it is declared. It is defined elsewhere(in **libword.so**) which Rust is not aware of. How do we tell the compiler that it needs to look for these functions in **libword.so**? it is exactly how we can specify in **gcc**. The ```-L``` and ```-l``` options can be used.

```
rust/Rust-C-experiments/rust-calling-c > rustc -L. -lword main.rs
```

The ```-L``` option can be used to specify the directory where the compiler needs to search for shared libraries. By default, it search certain paths, but here, we need to search the current directory - thats why we passed a **.** along with ```-L```. The ```-l``` is used to specify the name of the shared object. It should proceed without any errors.

Let us run **main**.

```
rust/Rust-C-experiments/rust-calling-c > ./main
word: 0x5566d8142170, validity: false
```

Nice! We are almost there I feel. It is printing the address. Instead we need it to print the string content. Let us see how it can be done.

When we had to send the string from Rustland to Cland, we used ```CString```. Here, when we need to use a Cland string in Rust, we use ```CStr```. I hope you got the difference. This is how you do it.

```rust
    unsafe                                                                      
    {                                                                           
        let cstr2: &CStr = CStr::from_ptr(word::get_word(&w_info));             
        println!("word: {:?}, validity: {:?}", cstr2, word::get_validity(&w_info));
    };                                                                          
}
```

This code speaks a lot. Notice that ```cstr2``` is a reference. It is a **borrowed reference**. We are borrowing it from Cland, although we know that Rustland owns the string. then we print it. Lets compile and run it.

```
rust/Rust-C-experiments/rust-calling-c > rustc -L. -lword main.rs
rust/Rust-C-experiments/rust-calling-c > ./main
word: "Cisco!", validity: false
```

And that is how one can call C-library functions from Rust.

A few key points to remember.

1. Considering we are in Rust land,
    - We create a string and we own it. If we need to pass this **owned** string to C, ```CString``` is used.
    - If there is some string in Cland and we need to **borrow** it(or get a **borrowed reference**) to it, then ```CStr``` is used.

## 2. Using bindgen!

That was a very simple example - one structure, two functions. We wrote the Rust declarations by hand. But consider real scenarios where each header file has lots of structure definitions, function declarations, inline functions etc., Hand-writing each of those header files is not possible.

Enter [bindgen](https://github.com/rust-lang/rust-bindgen)!!

This tool takes header files.

Not just that, we need a better way to link Rust executables against C libraries. For a project, we will be using **cargo** and it should offer some way to do it.

Now, let us do it the standard way using the available tools.

Start with creating a new project - **word**.

```
rust/Rust-C-experiments/rust-calling-c > cargo new word
     Created binary (application) `word` package
```

Copy only the **main.rs** into the ```src``` directory. It should look like this.

```
rust/Rust-C-experiments/rust-calling-c/word > tree .
.
├── Cargo.toml
└── src
    ├── main.rs

1 directory, 3 files
```

You can install bindgen in the following manner.

```
$ cargo install bindgen
```

That should install it. To generate bindings, the following command can be used.

```
rust/Rust-C-experiments/rust-calling-c > bindgen word.h -o word.rs                                                                                                                                   
thread 'main' panicked at 'Unable to find libclang: "the `libclang` shared library at /usr/lib64/clang-private/libclang.so.7 could not be opened: libclangAST.so.7: cannot open shared object file: No such file or directory"', /nobackup/
```


I kept getting this error. After some digging, I found out that the ```libclang``` is used by bindgen. And it is loaded using [clang-sys](https://github.com/KyleMayes/clang-sys). clang-sys searches for clang-related libraries in the following places: ```LD_LIBRARY_PATH``` and ```LIBCLANG_PATH```. In my system, clang libraries are found at ```/usr/lib64/clang-private```. Setting ```LIBCLANG_PATH``` didn't help, but setting ```LD_LIBRARY_PATH``` helped. Put them in bashrc file. Run it again.

```
t/Rust-C-experiments/rust-calling-c > bindgen word.h -o word.rs
word.h:4:10: fatal error: 'stdbool.h' file not found
word.h:4:10: fatal error: 'stdbool.h' file not found, err: true
thread 'main' panicked at 'Unable to generate bindings: ()', /nobackup/agautham/rust/renv/rust/registry/src/github.com-1ecc6299db9ec823/bindgen-0.55.1/src/main.rs:54:36
stack backtrace:
   0: rust_begin_unwind
             at /rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39/library/std/src/panicking.rs:475
   1: core::panicking::panic_fmt
             at /rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39/library/core/src/panicking.rs:85
   2: core::option::expect_none_failed
             at /rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39/library/core/src/option.rs:1221
   3: std::panicking::try
   4: bindgen::main
note: Some details are omitted, run with `RUST_BACKTRACE=full` for a verbose backtrace.
```

It doesn't know where stdbool.h is present. How do we specify it?

