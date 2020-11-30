---
title: Simple echo server in Rust
categories: rust
comments: true
layout: post
---

This post is the first Rust-based post in our event-driven journey. We will be exploring Rust's Networking API and using them to write a simple echo server.

## 1. Networking in Rust

Let us see the basic networking API Rust offers.

There are two types of sockets: Active and passive sockets. Active sockets are the ones which have a peer connected at the other end and data can be sent and received at this socket. Passive socket can just listen to connection requests - it can never talk to clients, send/receive data.

When the [socket()](https://man7.org/linux/man-pages/man2/socket.2.html) system call is called to create a new socket, an active socket is created by default. We have two choices: We can use [connect()](https://man7.org/linux/man-pages/man2/connect.2.html) and talk to a peer - the active socket remains active and data can be sent/received via this socket. But if we call [listen](https://man7.org/linux/man-pages/man2/listen.2.html) on that socket, it is converted to a passive socket where it is capable of listening new connection requests.

Rust provides two Tcp based API: [TcpListener](https://doc.rust-lang.org/std/net/struct.TcpListener.html) and [TcpStream](https://doc.rust-lang.org/std/net/struct.TcpStream.html). TcpListener is the passive socket abstraction - which can be used to create servers. TcpStream is an active socket abstraction.

The TcpListener provides a bunch of methods to manage and use it. It can be bound to a particular (IPaddress, PortNo) tuple, you can accept connections on it or get an iterator over the connections returned by this listener. The [doc page](https://doc.rust-lang.org/std/net/struct.TcpListener.html) lists all the API.

In C, when we call ```accept()``` on a listening socket, we get a descriptor for a new active socket - which is used to talk to the peer. Similarly, calling ```accept()``` here returns a ```TcpStream```.

This is what we will be using to write the echo server. But Rust offers a lot more and it is all listed in [std::net](https://doc.rust-lang.org/std/net/) docpage.

## 2. Creating a server

Let us create a TcpListener, bind it to an address tuple - basically do all the basic stuff and get a simple server running - which can accept incoming connection requests.

### 2.1 Command-line arguments

Let us take the IP Address and Port Number as command-line arguments. We can use the ```std::env::args()``` to get the arguments. The server must be given two arguments - ip-address and port-number. Totally, there will be three arguments.

```rust
fn main () -> io::Result<()>
{
    // Get the arguments
    let args: Vec<String> = env::args().collect();
    if args.len() != 3
    {
        println!("Usage: {} [ipv4 address] [port number]", args[0]);
        return Ok(())
    }
```

### 2.2 Creating a TcpListener

The following is the example given in the [docpage](https://doc.rust-lang.org/std/net/struct.TcpListener.html#examples).

```rust
fn main() -> std::io::Result<()> {
    let listener = TcpListener::bind("127.0.0.1:80")?;
```

Let us do the same thing. A ```&str``` is passed to the ```bind()``` method there. We need to construct it using the command-line arguments we have.

```rust
    // Generate the address tuple
    let ip_addr = args[1];
    let port_no = args[2];
    let mut address = String::new();
```

Is this going to compile? Not really. It gives the following error.

```
Rust-C-Experiments/sync-async$ rustc echo_server_v0.rs 
error[E0507]: cannot move out of index of `std::vec::Vec<std::string::String>`
  --> echo_server_v0.rs:24:19
   |
24 |     let ip_addr = args[1];
   |                   ^^^^^^^
   |                   |
   |                   move occurs because value has type `std::string::String`, which does not implement the `Copy` trait
   |                   help: consider borrowing here: `&args[1]`
```

Let us get an immutable reference to ```args[1]``` instead of trying to **move** it into ```ip_addr```. That should work. What would also work is to create a clone of ```args[1]``` like this.

```rust
    let ip_addr = args[1].clone();
    let ip_addr = args[2].clone();
```

This would work as well. But borrowing it would be better. ```clone()``` creates a new copy of that string which is not needed in our case.

Apart from the event-driven, networking stuff we do in these posts, let us discuss the errors we encounter in detail - that would give a better grip on the language. This would be done at the end of every post.

Coming back, let us construct the address. It should look like this: ```127.0.0.1:4200```. We want to do something like this: ```ip_addr```+ ":" + ```port_no```. How would you do it? Read through [String's docpage](https://doc.rust-lang.org/std/string/struct.String.html) and come up with a solution.

```rust
    // Generate the address tuple
    let ip_addr = &args[1];
    let port_no = &args[2];
    let mut address = String::new();
    address.push_str(ip_addr.as_str());
    address.push_str(":");
    address.push_str(port_no.as_str());
```

Now we can create the TcpListener.

```rust
    // Create the listener
    let listener = net::TcpListener::bind(&address)?;
    println!("Listening at {}", address);
```

Once this is done, we enter the infinite loop where we accept and serve connections.

```rust
    loop
    {

    }
```

Compile and make sure your program is working as intended.

### 2.3 The server loop

Logic is simple: We ```accept``` a connection (if any) or block till a request comes in. If we accept, we then serve the connection. Go through [TcpListener's docpage](https://doc.rust-lang.org/std/net/struct.TcpListener.html) and come up with the code.

It can be done in the following way.

```rust
    // Let us start the server
    loop
    {
        match listener.accept()
        {
            Ok((client_stream, client_addr)) =>
            {
                println!("Connection from {:?} accepted", client_addr);
                serve_connection(client_stream)?;
            }
            Err(error) =>
            {
                println!("Error: {:?}", error);
                return Ok(());
            }
        }
    }
```

At C level, the ```accept()``` system call did two things on success: It returns a descriptor for the new client-handling socket. The other is it fills the Client-Address details. If you look at ```accept()```'s prototype, we pass a pointer to a ```struct sock_addr``` which is populated by the ```accept()``` system call. So it returns two things: A socket descriptor handling the client and client details.

Rust's [accept() method](https://doc.rust-lang.org/std/net/struct.TcpListener.html#method.accept)  equivalent also does the same.

```rust
pub fn accept(&self) -> Result<(TcpStream, SocketAddr)>
```

It returns a tuple (Rust has a tuple datatype) with two members: A ```TcpStream```(equivalent to the socket descriptor) and a ```SocketAddr``` which has the client details.

If you see, in the code I have written, the ```client_stream``` is being **moved** into ```serve_connection```. Logically, that function has to own it and once it returns, we should not be caring about that connection - it should die when that ```serve_connection``` returns.

The ```serve_connection``` is just this at the moment.

```rust
fn serve_connection (mut client_stream: net::TcpStream) -> std::result::Result<(), std::io::Error>
{   
    todo!();
}
```

Compile and run this one. Try connecting to this server.

```
Rust-C-Experiments/sync-async$ ./echo_server_v0 127.0.0.1 4200
Listening at 127.0.0.1:4200
```

Let us connect to it.

```
Rust-C-Experiments/sync-async$ telnet 127.0.0.1 4200
Trying 127.0.0.1...
Connected to 127.0.0.1.
Escape character is '^]'.
```

Just when this happens, the ```serve_connection``` is called and the server panics - that is because of the ```todo!()``` we have put, nothing to be worried about. The ```todo!()``` macro is really cool!

```
dell@adwi:~/Documents/pwnthebox/Rust-C-Experiments/sync-async$ ./echo_server_v0 127.0.0.1 4200
Listening at 127.0.0.1:4200
Connection from 127.0.0.1:34942 accepted
thread 'main' panicked at 'not yet implemented', echo_server_v0.rs:56:5
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

We are ready with the server loop.

### 2.4 Implementing serve_connection

What is this function supposed to do?

We are writing an echo server. The client can keep sending data and we should keep sending it back. The client can be connected to the server for as much time it wants. This is a simple ```loop{}``` inside which we do the receive and send operations.

Rust abstracts away the C recv, send API. There are two traits [Read](https://doc.rust-lang.org/std/io/trait.Read.html) and [Write](https://doc.rust-lang.org/std/io/trait.Write.html). These traits are implemented for TcpStream([Read](https://doc.rust-lang.org/std/net/struct.TcpStream.html#impl-Read), [Write](https://doc.rust-lang.org/std/net/struct.TcpStream.html#impl-Write)), so we get to use the **read()** and **write()** methods on it. Use them and implement the function.

Let us read some data from the stream.

```rust
    // In a loop, we recv data and send back.
    loop
    {
        // Receive data
        let read_bytes_num = client_stream.read(&mut request_buffer)?;
```

Will this call block? The following lines are from [Read trait's read() method](https://doc.rust-lang.org/std/io/trait.Read.html#tymethod.read).

> This function does not provide any guarantees about whether it blocks waiting for data, but if an object needs to block for a read and cannot, it will typically signal this via an Err return value.

That is understandable, because it depends on the internal implementation. But in our case, it will block. We are using a traditional, blocking socket(we have not called [set_nonblocking](https://doc.rust-lang.org/std/net/struct.TcpStream.html#method.set_nonblocking)).

There is one thing we need to take care about. If the client on the other side has disconnected, how will we know? The following lines about the ```read()``` method.

> If the return value of this method is Ok(n), then it must be guaranteed that 0 <= n <= buf.len(). A nonzero n value indicates that the buffer buf has been filled in with n bytes of data from this source. If n is 0, then it can indicate one of two scenarios:

>   1. This reader has reached its "end of file" and will likely no longer be able to produce bytes. Note that this does not mean that the reader will always no longer be able to produce bytes.
>   2. The buffer specified was 0 bytes in length.

We obviously won't specify a 0-length buffer. So the first-one should help us. If ```read()``` returns 0, then we have reached EOF or in our case the client has disconnected. The ```recv``` system call specifically returns 0 when the client has shutdown from its end. So I think we can confidently use that.

```rust
        // Receive data
        let read_bytes_num = client_stream.read(&mut request_buffer)?;
        if read_bytes_num == 0 
        {
            // The client has closed the connection
            println!("Returning back from server_connection");
            return Ok(());
        }
```

Once we return, the ```client_stream``` gets cleaned up thereby closing the connection from our end as well.

Now we send(or write()) the data to the same stream.

```rust
        // Send it
        client_stream.write(&request_buffer[..read_bytes_num])?;
```

Before we go back to the beginning of the loop, we need to zeroize the buffer we used.

```rust

        // Clean up the buffer
        request_buffer = [0; 10000];
    }
```

With that, we are ready with our echo server. My implementation is present [here](https://github.com/adwait1-G/Rust-C-Experiments/blob/main/sync-async/echo_server_v0.rs).

Play around with it and understand clearly what it is doing.

## 3. The blocking problem

The I/O calls we made - like ```accept()```, ```read()``` etc., are all blocking in nature. They won't return till that I/O operation is done. We have explored the blocking problem in detail [here](/rust/2020/11/08/what-does-blocking-mean.html) in case you want to understand it in detail.

In short, till a blocking call returns, we are just stuck there, doing nothing. How can this be solved?

## 4. Understanding errors

### 4.1 The Copy Trait error

The [Copy docpage](https://doc.rust-lang.org/std/marker/trait.Copy.html) explains this problem. But let us go over it here as well.

Let us start with a very simple example.

```rust
Rust-C-Experiments/sync-async$ cat code1.rs
fn main()
{
        let x: i32 = 10;
        let y = x;
        println!("x = {}, y = {}", x, y);
}
```

The intention here is to make a **copy** or make a **duplicate** of ```x``` in ```y```. Try compiling it.

```
Rust-C-Experiments/sync-async$ rustc code1.rs
Rust-C-Experiments/sync-async$ ./code1
x = 10, y = 10
```

Now let us try doing the same with ```x``` as a ```std::String```. Intention is make a copy of the String.

```rust
Rust-C-Experiments/sync-async$ cat code2.rs
fn main()
{
        let x = String::from("SomeString");
        let y = x;
        println!("x = {}, y = {}", x, y);
}
```

Think about it, will this code compile? This is identical to the code we wrote during the server implementation.

```
Rust-C-Experiments/sync-async$ rustc code2.rs
error[E0382]: borrow of moved value: `x`
 --> code2.rs:5:29
  |
3 |     let x = String::from("SomeString");
  |         - move occurs because `x` has type `std::string::String`, which does not implement the `Copy` trait
4 |     let y = x;
  |             - value moved here
5 |     println!("x = {}, y = {}", x, y);
  |                                ^ value borrowed here after move

error: aborting due to previous error

For more information about this error, try `rustc --explain E0382`.
```

A ```std::String``` is internally a ```Vec<u8>```. A ```Vec``` is a struct of three members:

1. ```data_ptr```: Pointer to data
2. ```data_len```: Length used
3. ```data_cap```: Total Capacity

Now let us think again, our intention is to make a copy/duplicate of the String. But what exactly does that mean?

1. Will both copies (x and y) point to the same memory? - basically should they have the same data pointer?
```
    x     y                              
    |     |
    |     |  
    |     |
    |     |
    v     V
--------------
| SomeString |
--------------
```

2. Or by copy do we mean a **deep copy**? Where even the data pointed by the pointers are copied into a new memory location?
```
      x                    y                              
      |                    |
      |                    |  
      |                    |
      |                    |
      v                    V
--------------      ---------------
| SomeString |      | SomeString  |
--------------      ---------------
```

Implementing (1) is simple. You just do a ```memcpy```. But what about (2)? Whenever there is a pointer to some data, new memory needs to be allocated and that data should be copied onto this new memory location.

Assume ```y``` is a shallow-copy of ```x``` - both of them point to the same memory location. You spawn a thread and **move** ```x``` into it. Once the thread is done running, ```x``` is cleaned up. This means the memory pointed by ```x``` is freed. Suppose we are still using ```y``` in our main thread. What are we doing here?

That memory location is freed and is invalid (this happened in one thread). In the main thread, we are still using it as if nothing has happened. This is the classic **use-after-free** bug. So bitwise copy (or simple, shallow-copy) bit us in the *** here.

How do we solve it? Making a deep-copy solves it. Both of them point to different memory locations. So even if one is freed, other is intact. The ```clone()``` does this. That is why ```ip_addr = args[1].clone()``` compiled because this doesn't cause any use-after-free issues.

What does all this have to do with the **Copy** trait? It is the way Rust makes sure such use-after-free bugs don't happen because of Shallow-copy.

```Copy``` is a trait which can be implemented on datatypes which don't lead to such bugs. It is a simple bitwise copy. i8, u8, ...., i128, u128, f64 implements the ```Copy``` trait - just doing a ```y = x``` is enough to make a safe, valid of copy of ```x```.

But structs with pointers to heap memory(like Vec, String) - if we implement the ```Copy``` trait for them, it can end up in a use-after-free bug. That is why, ```Copy``` trait is not implemented for Vec. Now let us come back to the error.

```
Rust-C-Experiments/sync-async$ rustc code2.rs
error[E0382]: borrow of moved value: `x`
 --> code2.rs:5:29
  |
3 |     let x = String::from("SomeString");
  |         - move occurs because `x` has type `std::string::String`, which does not implement the `Copy` trait
4 |     let y = x;
  |             - value moved here
5 |     println!("x = {}, y = {}", x, y);
  |                                ^ value borrowed here after move

error: aborting due to previous error

For more information about this error, try `rustc --explain E0382`.
```

So code like ```y = x``` compiles only if the datatype of ```x``` implements a ```Copy``` trait. In other words, that code works only if bitwise-copy of ```x``` is memory-safe.

Go over [Copy's docpage](https://doc.rust-lang.org/std/marker/trait.Copy.html) again and make sure you understand it.

This is a lifetimes problem. For how long does an object live? If I know for how much time exactly an object lives, then we can pass references to it and somehow magically invalidate them when the object dies (or cleaned up). Borrowing ```args[1]``` (using ```ip_addr = &args[1]```) is safe in the way we used it. What happens if that reference is passed to a new thread? The parent thread still owns it, but a reference to it is present in another thread. If the parent thread exits before the new thread, then this also is a use-after-free. This kind of code will not compile.

## 5. A note on Rust's abstraction

I had not used Rust's networking API before. Now that I see this, it abstracts away a ton of things. The entire server is about 65 lines. The C-equivalent was around 120 lines. We don't have to bother about socket creation, calling listen on it. There are high-level datatypes like IpAddr, SocketAddr which we can use.

Honestly, I felt uncomfortable not having the C-level visibility into things. Need to get used to it.

### 5.1 Blocking sockets vs Calls

In C, we create blocking sockets. And therefore any I/O call on it blocks. If we create a non-blocking socket, I/O call on it doesn't block.

Rust abstracts away the sockets part. There are just **calls** here - either they are blocking or non-blocking.

## 6. Conclusion

With that, we have come to the end.

We wrote a super-simple echo server which serves just one client at a time. We used blocking calls to implement it.

In the next post, we will be implementing a multithreaded echo server - each thread serving one client.

Thank you for reading :-)