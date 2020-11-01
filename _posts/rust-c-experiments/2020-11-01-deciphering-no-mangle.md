---
title: Deciphering Rust's no_mangle
categories: Rust
comments: true
layout: post
---

When I was exploring the Rust FFI, I came across ```#[no_mangle]```. Even though I used C++ before and I had seen mangled symbols, I never really bothered to understand why mangling was done. Also Rust's ```#[no_mangle]``` is interesting for several reasons. So, this post is about mangling!

This post is written using Rust 1.47 compiler version.

## 1. Introduction

When you start a C project with multiple components, all the functions, structures, macros etc., defined for that component generally have the component name prefixed to their names. For example, assume your project has two components **c1** and **c2** and both of them have ```init``` and ```cleanup``` functions. How would the naming be? Generally, they would be named as ```c1_init```, ```c2_init```, ```c1_cleanup``` and ```c2_cleanup```. Why is it named this way? Because in C, there is just one huge global namespace. Because we don't want symbols to collide and have the same symbol(say ```init```) refering to two different functions, we use that sort of naming convention.

This problem is solved in C++ using namespaces. Each component has its own namespace. While writing programs, we refer to the functions in this way: ```c1::init```, ```c2::init```, ```c1::cleanup```, ```c2::cleanup```. This is how we use it. But how is each symbol internally stored in the symbol table? They can be stored as "c1::init", "c2::init", "c1::cleanup", "c2::cleanup". Languages, compilers keep getting intelligent, but one component still remains the same.

The linker. It doesn't understand C++, Rust or any other language. It just understands the C-way of doing it - all the symbols need to be unique, thats all. It just has one global namespace where all the symbols are present. With the help of compile-time namespaces and corresponding symbol generation, the linker doesn't complain.

Moving forward, C++ allows something called function overloading. It means the same symbol can be used to define two different functions. For example, consider in component **c1**, you have two ```add``` functions.

```c
namespace c1
{

int add (int a, int b)
{
	return (a+b);
}

int add (int a, int b, int c)
{
	return (a+b+c);
}

} /* namespace c1 */

```

Try compiling them, the program will compile without any issues. But here, both of these are present in the same namespace. According to the concept we have built so far, the compiler should have generated symbols ```c1::add``` and ```c1::add``` for both the functions. With this, the linker should have thrown an error right? But it didn't. So, what might be happening here?

What differentiates the two functions there?

It is the number of arguments. The first one takes two arguments, second takes three. If we can somehow store this information as part of the symbol, this would solve the problem. Assuming we are the compiler, let us do it this way - ```c1::add2``` and ```c1::add3```. Note that while writing programs, you will still use ```c1::add``` and ```c1::add``` in both cases, but based on the number of arguments passed to it, the compiler intelligently replaces them with ```c1::add2``` or ```c1::add3```.

Now, you want to concatenate two strings. How would you write that?

```c
string add (string s1, string s2)
{
	return (s1+s2);
}
```

Our concept  generates ```c1::add2``` as the symbol name even for this string adding function - because it is based on number of arguments. The linker complains here. It fails because it is colliding with the number adding function. What can we do? What differentiates these functions?

The argument types.

Let us extend our concept to include both argument number and argument types in the symbols. Something like this: ```c1::add2ii```, ```c1::add3iii```, ```c1::add2ss``. **i** is used for ```int```, **s** is used for ```std::string```. This has solved the problem.

So can you see what is happening to the symbols here? They have the original name, but also some data(or metadata) one many not recognize upfront. These are simple examples we took. In real projects, a robust mechanism is necessary to make sure all the symbols are unique and linking happens smoothly.

Enter **mangling**. I looked up its meaning in the dictionary, it means destroy or severely damage. And that is probably what is happening to these symbols :P. The following are the actual C++ generated mangled symbols for the above ```add``` functions.

```
    55: 0000000000000e2a    20 FUNC    GLOBAL DEFAULT   14 _ZN2c13addEii
    73: 0000000000000e3e    28 FUNC    GLOBAL DEFAULT   14 _ZN2c13addEiii
    88: 0000000000000e5a    84 FUNC    GLOBAL DEFAULT   14 _ZN2c13addENSt7__cxx1112b
```

They are indeed destroyed. Beautiful names like ```c1::add``` are converted to ```_ZN2c13addEii```. Major reason being the simplicity of the linker - it just understands the C-way of doing things.

I hope that gives you an understanding of what mangling is and why it is done. The Itanium C++ ABI specifies clear [mangling rules](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#mangling) a compiler should follow. This consistency is very important. If I mangle the symbols in one way and the library authors used another mangling algorithm, I won't be able to link my program against that library.

## 2. Mangling in Rust

The [Rust RFC 2603](https://rust-lang.github.io/rfcs/2603-rust-symbol-name-mangling-v0.html) describes mangling in full detail.

## 3. The #[no_mangle]

I am not particularly interesting in how mangling happens in Rust. I am more interested in how mangling is suppressed in Rust. Whenever you are doing a Rust+C project - where you need to deal with C calling Rust or Rust calling C, mangling is suppressed. We ask the compiler not to mangle the symbols. That is because C doesn't understand mangling. This also means that we, the programmers should make sure symbol collisions doesn't happen - the same way we took care in pure C.

You can mark something(a function, structure etc.,) with ```#[no_mangle]``` and Rust compiler will not mangle it. But when I was exploring this, I saw that marking something as ```#[no_mangle]``` not just suppressed mangling but also did a lot of other things.

Let us start by creating a project - **nomangle**.

```
Rust-C-Experiments/deciphering-unmangling$ cargo new nomangle
     Created binary (application) `nomangle` package
```

Let us write a simple function in it.

```rust
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ cat main.rs 
fn some_function()
{
	println!("Hello, this is some_function!");
}

fn main()
{
	some_function();
}
```

```some_function``` is our function of interest. Compile and make sure it runs.

```
Rust-C-Experiments/deciphering-unmangling/nomangle$ cargo run
   Compiling nomangle v0.1.0 (/home/dell/Documents/pwnthebox/Rust-C-Experiments/deciphering-unmangling/nomangle)
    Finished dev [unoptimized + debuginfo] target(s) in 0.26s
     Running `target/debug/nomangle`
Hello, this is some_function!
```

Lets take a look at how ```some_function``` looks like in the symbol table.

```
Rust-C-Experiments/deciphering-unmangling/nomangle/target/debug$ objdump --syms ./nomangle | grep nomangle
./nomangle:     file format elf64-x86-64
0000000000005060 l     F .text	0000000000000044              _ZN8nomangle13some_function17h25e403d45aed5054E
00000000000050b0 l     F .text	0000000000000008              _ZN8nomangle4main17h999083d6469bfb6dE
```

Look at the first entry, its all mangled up.

You can see that **l** after the address. It means that the symbol is **LOCAL**. The following is **readelf**'s output.

```
Rust-C-Experiments/deciphering-unmangling/nomangle/target/debug$ readelf -s nomangle | grep nomangle
    51: 0000000000005060    68 FUNC    LOCAL  DEFAULT   14 _ZN8nomangle13some_functi
    52: 00000000000050b0     8 FUNC    LOCAL  DEFAULT   14 _ZN8nomangle4main17h99908
```

Let us now define it as ```pub fn some_function``` and see if there is any change in visibility. The pub really doesn't change anything. That is because **pub** is a compile-time enforcement and not a link-time enforcement. So, that wouldn't be visible for us here. Here, it still says it is **l** or local. This is still not visible to the outside world.

The **extern** keyword is present specifically to do that. Let us define it this way: ```pub extern fn some_function``` and checkout.

```
Rust-C-Experiments/deciphering-unmangling/nomangle/target/debug$ readelf --syms ./nomangle | grep nomangle
    51: 0000000000005060    68 FUNC    LOCAL  DEFAULT   14 _ZN8nomangle13some_functi
    52: 00000000000050b0     8 FUNC    LOCAL  DEFAULT   14 _ZN8nomangle4main17h99908
```

This is wierd. It is still a **LOCAL** symbol. But ```extern``` was supposed to make it **GLOBAL** - make it available to the rest of the world to call it.

Now comes the most wierd part - the ```#[no_mangle]```. When we mark ```some_function``` with ```#[no_mangle]```, I expect just the mangling not to happen. It should be something like this.

```
Rust-C-Experiments/deciphering-unmangling/nomangle/target/debug$ readelf --syms ./nomangle | grep nomangle
    51: 0000000000005060    68 FUNC    LOCAL  DEFAULT   14 some_function
    52: 00000000000050b0     8 FUNC    LOCAL  DEFAULT   14 _ZN8nomangle4main17h99908
```

Let us put it and see what happens. You can mark it in the following manner.

```rust
Rust-C-Experiments/deciphering-unmangling/nomangle/target/debug$ readelf -s nomangle | grep some_function
   714: 0000000000005060    68 FUNC    GLOBAL DEFAULT   14 some_function
```

There you go! It didn't mangle, but now it is **GLOBAL** as well. What does this actually mean? Who all can call this function? Who all is it visible to?

To understand this better, let us not build an executable. Instead, let us get the set of relocatable(**.o**) files that we get out of compiling **main.rs**. Comment out the ```main``` function. It should look like the following.

```rust
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ cat main.rs
#[no_mangle]
pub extern fn some_function()
{
	println!("Hello, this is some_function!");
}

/*
fn main()
{
	some_function();
}
*/
```

Now, compile to get the relocatable files.

```
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ rustc main.rs --crate-type staticlib
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ ls -l libmain.a 
-rw-r--r-- 1 dell dell 17472762 Nov  1 16:36 libmain.a
```

It gives an archive - which is basically a bunch of relocatable files packed together. You can use the **ar** utility and list all the relocatable files it has.

```
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ ar t ./libmain.a
main.main.3a1fbbbh-cgu.0.rcgu.o
main.main.3a1fbbbh-cgu.1.rcgu.o
main.ruuf8avppfzdwhl.rcgu.o
std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o
panic_unwind-48d342a8b48d1d01.panic_unwind.vko21qfi-cgu.0.rcgu.o
miniz_oxide-14bc0820888c8eb3.miniz_oxide.dm3304v5-cgu.0.rcgu.o
adler-9cbd9e217bff06bc.adler.edb64bo7-cgu.0.rcgu.o
object-31826136df98934e.object.1aonhe3x-cgu.0.rcgu.o
addr2line-075976a117c8fd5d.addr2line.6lqg7ags-cgu.0.rcgu.o
gimli-2d5cbedfbf17a011.gimli.er7lmuo3-cgu.0.rcgu.o
rustc_demangle-0474372ff08c5319.rustc_demangle.7fpy91vt-cgu.0.rcgu.o
hashbrown-d437c34460d2315a.hashbrown.77wbcla3-cgu.0.rcgu.o
rustc_std_workspace_alloc-fb61ed1b8cc4de79.rustc_std_workspace_alloc.4oazxke6-cgu.0.rcgu.o
unwind-bf76d1b643bfc9f0.unwind.8zful0z9-cgu.0.rcgu.o
cfg_if-a1b53aa7fddcf418.cfg_if.1gcs8m6x-cgu.0.rcgu.o
libc-28585e57fac45c73.libc.1uk68pdz-cgu.0.rcgu.o
alloc-64801769bc15ab28.alloc.ax07ilsa-cgu.0.rcgu.o
compiler_builtins-cd9f15a39fb65cbc.compiler_builtins.cb4bpgt7-cgu.0.rcgu.o
compiler_builtins-cd9f15a39fb65cbc.compiler_builtins.cb4bpgt7-cgu.1.rcgu.o
.
.
.
compiler_builtins-cd9f15a39fb65cbc.compiler_builtins.cb4bpgt7-cgu.10.rcgu.o
compiler_builtins-cd9f15a39fb65cbc.compiler_builtins.cb4bpgt7-cgu.86.rcgu.o
compiler_builtins-cd9f15a39fb65cbc.compiler_builtins.cb4bpgt7-cgu.87.rcgu.o
clzdi2.o
clzsi2.o
clzti2.o
cmpdi2.o
cmpti2.o
ctzdi2.o
ctzsi2.o
ctzti2.o
divdc3.o
divsc3.o
divxc3.o
extendhfsf2.o
ffsti2.o
floatdisf.o
subvsi3.o
subvti3.o
truncdfhf2.o
truncdfsf2.o
truncsfhf2.o
ucmpdi2.o
ucmpti2.o
apple_versioning.o
rustc_std_workspace_core-541997b56bb98660.rustc_std_workspace_core.9s54uo0x-cgu.0.rcgu.o
core-cdea3c81adab3d12.core.271eo4m4-cgu.0.rcgu.o
```

Make sure ```some_function``` is present in the archive.

```
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ readelf --syms libmain.a | grep some_function
    10: 0000000000000000    68 FUNC    GLOBAL DEFAULT    3 some_function
```

Great! It is present in the archive, in the form we want.

Now is a good time to explain LOCAL and GLOBAL. Suppose we write a C program which calls ```some_function```. If the symbol here was LOCAL, then it wouldn't be accessible to the C program. Because it is GLOBAL, it will be accessible to the C program. If a symbol is GLOBAL, that symbol is accessible out of the relocatable file it is present in.

Let us go ahead and write a C program to confirm our understanding. 

```
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ cat code1.c
void some_function();

int main()
{
	some_function();
}
```

Let us now use **gcc** and compile the C sourcefile along with all those relocatable files in the archive.

```
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ gcc code1.c libmain.a -o code1
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::mutex::ReentrantMutex::init':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:107: undefined reference to `pthread_mutexattr_init'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:110: undefined reference to `pthread_mutexattr_settype'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:114: undefined reference to `pthread_mutexattr_destroy'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::mutex::Mutex::init':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:52: undefined reference to `pthread_mutexattr_init'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:54: undefined reference to `pthread_mutexattr_settype'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:58: undefined reference to `pthread_mutexattr_destroy'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:52: undefined reference to `pthread_mutexattr_init'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:54: undefined reference to `pthread_mutexattr_settype'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:58: undefined reference to `pthread_mutexattr_destroy'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:52: undefined reference to `pthread_mutexattr_init'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:54: undefined reference to `pthread_mutexattr_settype'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:58: undefined reference to `pthread_mutexattr_destroy'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::mutex::ReentrantMutex::init':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:107: undefined reference to `pthread_mutexattr_init'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:110: undefined reference to `pthread_mutexattr_settype'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:114: undefined reference to `pthread_mutexattr_destroy'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::mutex::Mutex::init':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:52: undefined reference to `pthread_mutexattr_init'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:54: undefined reference to `pthread_mutexattr_settype'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:58: undefined reference to `pthread_mutexattr_destroy'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::mutex::ReentrantMutex::init':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:107: undefined reference to `pthread_mutexattr_init'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:110: undefined reference to `pthread_mutexattr_settype'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/mutex.rs:114: undefined reference to `pthread_mutexattr_destroy'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread_local_key::create':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:10: undefined reference to `pthread_key_create'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:10: undefined reference to `pthread_key_create'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread_local_key::destroy':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:27: undefined reference to `pthread_key_delete'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:27: undefined reference to `pthread_key_delete'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread_local_key::get':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:22: undefined reference to `pthread_getspecific'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread_local_key::create':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:10: undefined reference to `pthread_key_create'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:10: undefined reference to `pthread_key_create'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread_local_key::destroy':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:27: undefined reference to `pthread_key_delete'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:27: undefined reference to `pthread_key_delete'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread_local_key::set':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:16: undefined reference to `pthread_setspecific'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread_local_key::create':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:10: undefined reference to `pthread_key_create'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:10: undefined reference to `pthread_key_create'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread_local_key::destroy':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:27: undefined reference to `pthread_key_delete'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:27: undefined reference to `pthread_key_delete'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread_local_key::get':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:22: undefined reference to `pthread_getspecific'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread_local_key::set':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:16: undefined reference to `pthread_setspecific'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread_local_key::get':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:22: undefined reference to `pthread_getspecific'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread_local_key::create':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:10: undefined reference to `pthread_key_create'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:10: undefined reference to `pthread_key_create'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread_local_key::destroy':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:27: undefined reference to `pthread_key_delete'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:27: undefined reference to `pthread_key_delete'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread_local_key::create':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:10: undefined reference to `pthread_key_create'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:10: undefined reference to `pthread_key_create'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread_local_key::destroy':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:27: undefined reference to `pthread_key_delete'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread_local_key.rs:27: undefined reference to `pthread_key_delete'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::rwlock::RWLock::write':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/rwlock.rs:73: undefined reference to `pthread_rwlock_wrlock'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::rwlock::RWLock::raw_unlock':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/rwlock.rs:112: undefined reference to `pthread_rwlock_unlock'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/rwlock.rs:112: undefined reference to `pthread_rwlock_unlock'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::rwlock::RWLock::write':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/rwlock.rs:73: undefined reference to `pthread_rwlock_wrlock'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::rwlock::RWLock::raw_unlock':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/rwlock.rs:112: undefined reference to `pthread_rwlock_unlock'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/rwlock.rs:112: undefined reference to `pthread_rwlock_unlock'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::rwlock::RWLock::read':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/rwlock.rs:23: undefined reference to `pthread_rwlock_rdlock'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::rwlock::RWLock::raw_unlock':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/rwlock.rs:112: undefined reference to `pthread_rwlock_unlock'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/rwlock.rs:112: undefined reference to `pthread_rwlock_unlock'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread::guard::get_stack_start':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread.rs:301: undefined reference to `pthread_getattr_np'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread.rs:305: undefined reference to `pthread_attr_getstack'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::condvar::Condvar::init':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/condvar.rs:47: undefined reference to `pthread_condattr_setclock'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::weak::fetch':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/weak.rs:66: undefined reference to `dlsym'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/weak.rs:66: undefined reference to `dlsym'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::process::process_inner::<impl std::sys::unix::process::process_common::Command>::do_exec':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/process/process_unix.rs:216: undefined reference to `pthread_sigmask'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::weak::fetch':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/weak.rs:66: undefined reference to `dlsym'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread::pthread_attr_setstacksize':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread.rs:30: undefined reference to `pthread_attr_setstacksize'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread::Thread::new':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread.rs:62: undefined reference to `pthread_attr_setstacksize'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread.rs:66: undefined reference to `pthread_create'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread::Thread::join':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread.rs:191: undefined reference to `pthread_join'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `<std::sys::unix::thread::Thread as core::ops::drop::Drop>::drop':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread.rs:210: undefined reference to `pthread_detach'
libmain.a(std-f14aca24435a5414.std.54pte2sm-cgu.0.rcgu.o): In function `std::sys::unix::thread::guard::current':
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread.rs:410: undefined reference to `pthread_getattr_np'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread.rs:413: undefined reference to `pthread_attr_getguardsize'
/rustc/18bf6b4f01a6feaf7259ba7cdae58031af1b7b39//library/std/src/sys/unix/thread.rs:426: undefined reference to `pthread_attr_getstack'
collect2: error: ld returned 1 exit status
```

From looking at the undefined references, we need to link it against **libdl.so** and **libpthread.so**.

```
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ gcc code1.c libmain.a -o code1 -lpthread -ldl
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ ls
code1  code1.c  libmain.a  main.rs
```

Let us run it.

```
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ ./code1
Hello, this is some_function!
```

Nice! It worked.

Without marking the function as ```#[no_mangle]```, the function won't be **GLOBAL** - so we can't call it from C.

My understanding is that the ```extern``` keyword is supposed to do this job, but ```#[no_mangle]``` is doing it. Let us remove both ```pub``` and ```extern```, and try the same thing again. Let us see what we get.

```rust
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ cat main.rs
#[no_mangle]
fn some_function()
{
	println!("Hello, this is some_function!");
}

/*
fn main()
{
	some_function();
}
*/
```

Now, let us compile it to get the archive.

```
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ rustc main.rs --crate-type staticlib
```

Let us checkout the ```some_function``` symbol.

```
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ readelf --syms libmain.a | grep some_function
    10: 0000000000000000    68 FUNC    GLOBAL DEFAULT    3 some_function
```

It is exactly like how it was with ```extern``` and ```pub```. Lets compile and run.

```
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ gcc code1.c libmain.a -o code1 -lpthread -ldl
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ ./code1
Hello, this is some_function!
```

Ideally, this shown not compile because the function doesn't have the ```extern``` keyword with it.


So far, this function can be called by other C source files linked together to make a single executable. Let us take it to the next level.

Let us make a Dynamic library out of **libmain.a**. Then link our **code1** program against that shared library. Generating shared library out of libmain.a is easy.

1. Extract all the object files in the archive.

```
Rust-C-Experiments/deciphering-unmangling/nomangle/src/libmain$ ls
libmain.a
Rust-C-Experiments/deciphering-unmangling/nomangle/src/libmain$ ar -x libmain.a
Rust-C-Experiments/deciphering-unmangling/nomangle/src/libmain$ gcc -shared *.o -o libmain.so
```

Lets checkout the symbol table.

```
Rust-C-Experiments/deciphering-unmangling/nomangle/src/libmain$ readelf --syms libmain.so | grep some_function
  1388: 000000000009ea70    68 FUNC    GLOBAL DEFAULT   12 some_function
  2612: 000000000009ea70    68 FUNC    GLOBAL DEFAULT   12 some_function
```

What are these two entries?

Note that a symbol is visible to the outside world when it is present in the Dynamic Symbol Table(**.dynsym**). 

```
Rust-C-Experiments/deciphering-unmangling/nomangle/src/libmain$ readelf --dyn-syms libmain.so | grep some_function
  1388: 000000000009ea70    68 FUNC    GLOBAL DEFAULT   12 some_function
```

Alright, it is present in the Dynamic Symbol table. So, other programs can call this function. Let us compile **code1.c**.

```
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ gcc code1.c -c -fPIC
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ gcc code1.o -o code1
code1.o: In function `main':
code1.c:(.text+0xa): undefined reference to `some_function'
collect2: error: ld returned 1 exit status
```

Now, it should work if we link it against **libmain.so**.

```
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ gcc code1.o -o code1 -L. -lmain -lpthread -ldl -lm
Rust-C-Experiments/deciphering-unmangling/nomangle/src$ ./code1
Hello, this is some_function!
```

## 4. Conclusion

Sorry if this felt like a FFI tutorial, but thats when one would generally use ```#[no_mangle]```.

Someone raised the same concern in the [Rust Internals Forum](https://internals.rust-lang.org/t/precise-semantics-of-no-mangle/4098). 

With that, I will end this tutorial. All the examples here doesn't follow best practices or standard way to do it. But exploring in non-standard ways opened up a lot of interesting things.

Thanks for reading!
