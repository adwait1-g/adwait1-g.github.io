---
title: Intro to rustenv
categories: rust
comments: true
layout: post
---

In case you don't have sudo access on the machine you are working on or you don't want to install the rust toolchain globally, you can follow this post and install the toolchain in one place and you can activate it whenever you want.

# 1. Bringinig up the Rust environment

This assumes that the [virtualenv](https://virtualenv.pypa.io/en/stable/) package is installed in your system. Generally, systems that don't give you sudo access have virtualenv installed in them - so that you can download and use any python packages you want. Similarly, there is one for rust too - the [rustenv](https://pypi.org/project/rustenv/). This is also a python package. The following are the steps to install it.

Create a directory with name of your choice - store everything related to Rust there.

```
> mkdir rust
> cd rust
rust >
```

Create a python virtual environment first.

```
rust > virtualenv venv -p python3
Running virtualenv with interpreter /usr/local/bin/python3
Using base prefix '/sw/packages/python3/current'
New python executable in rust/venv/bin/python3
Also creating executable in rust/venv/bin/python
Installing setuptools, pip, wheel...done.
rust >
```

Activate that environment.

```
rust > source ./venv/bin/activate
(venv) rust >
```

In this environment, let us install rustenv.

```
(venv) rust > pip3 install rustenv
Collecting rustenv
  Using cached rustenv-0.0.2-py2.py3-none-any.whl (4.1 kB)
Installing collected packages: rustenv
Successfully installed rustenv-0.0.2
(venv) rust >
```

Now create a rust environment and activate it.

```
(venv) rust > rustenv renv
info: downloading installer
info: profile set to 'default'
info: default host triple is x86_64-unknown-linux-gnu
info: syncing channel updates for 'stable-x86_64-unknown-linux-gnu'
info: latest update on 2020-10-08, rust version 1.47.0 (18bf6b4f0 2020-10-07)
info: downloading component 'cargo'
info: downloading component 'clippy'
info: downloading component 'rust-docs'
info: downloading component 'rust-std'
info: downloading component 'rustc'
info: downloading component 'rustfmt'
info: installing component 'cargo'
info: Defaulting to 500.0 MiB unpack ram
info: installing component 'clippy'
info: installing component 'rust-docs'
 12.9 MiB /  12.9 MiB (100 %)  10.4 MiB/s in  1s ETA:  0s
info: installing component 'rust-std'
 21.2 MiB /  21.2 MiB (100 %)  11.2 MiB/s in  1s ETA:  0s
info: installing component 'rustc'
 66.5 MiB /  66.5 MiB (100 %)  13.2 MiB/s in  5s ETA:  0s
info: installing component 'rustfmt'
info: default toolchain set to 'stable'

  stable installed - rustc 1.47.0 (18bf6b4f0 2020-10-07)


Rust is installed now. Great!

To get started you need Cargo's bin directory 
(rust/renv/rust/bin) in your PATH
environment variable.

To configure your current shell run 
source rust/renv/rust/env
```

Activating it.

```
(venv) rust > source renv/bin/activate 
(renv) (venv) rust > rustc --version
rustc 1.47.0 (18bf6b4f0 2020-10-07)
```

Now you are ready.

## 1.1 Hello program in Rust

Let us run a hello program to make sure our setup works.

Create a new project using cargo

```
(renv) (venv) rust > cargo new hello
     Created binary (application) `hello` package
(renv) (venv) rust > cd hello
(renv) (venv) rust/hello > cargo run
   Compiling hello v0.1.0 (rust/hello)
    Finished dev [unoptimized + debuginfo] target(s) in 0.33s
     Running `target/debug/hello`
Hello, world!
```

With that, your rust environment is ready. Whenever you want to deactivate it, you can simply enter ```deactivate``` and the environment will come to an end.
