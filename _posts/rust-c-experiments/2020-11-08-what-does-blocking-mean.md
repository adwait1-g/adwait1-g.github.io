---
title: What does blocking mean?
categories: Rust
comments: true
layout: post
---

Let us start this series by understanding a basic and fairly simple concept - blocking.

## 1. What is blocking?

Lets write a very simple TCP server - which will help us throughout the post. The complete code is present [here](https://github.com/adwait1-G/Rust-C-Experiments/blob/main/sync-async/server_v1.c).

Create a TCP socket.

```c
    // Lets create a socket.
    ret = socket(AF_INET, SOCK_STREAM, 0);
    if (ret < 0)
    {
        printf("socket() failed\n");
        return -1;
    }
    sock_fd = ret;
```

A server needs to **bind** or **latch** to a (IPAddress, PortNumber) tuple.

```c
    // Bind the socket to the passed (ip_address, port_no).
    server_addr.sin_port = htons(atoi(argv[2]));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr(argv[1]);
    
    ret = bind(sock_fd, (const struct sockaddr *)&server_addr, sizeof(server_addr));
    if (ret < 0)
    {
        printf("bind() failed\n");
        return -1;
    }
```

The next step decides the fate of this socket. It is a server socket and thus needs to **listen** to incoming connection requests.

```c
    // Start listening
    ret = listen(sock_fd, 50);
    if (ret < 0)
    {
        printf("listen() failed\n");
        return -1;
    }
    printf("Listening at (%s, %u)\n", ip_addr, port_no);
```

Once this is called on the socket, it can never send or receive data during its lifetime. It can just listen to incoming connections.

Now, we have our small server setup ready. It is time to accept connections.

```c
    // Do the thing
    while (1)
    {
        memset(&client_addr, '\0', sizeof(client_addr));
        
        // Wait till we get a connection request
        ret = accept(sock_fd, (struct sockaddr *)&client_addr, &client_addr_len);
        if (ret < 0)
        {
            printf("accept() failed\n");
            return -1;
        }
        client_fd = ret;

        // Handle the request
        printf("Serving request for client no %d!\n", i);
        serve_connection(client_fd);

        // Once done, close it
        close(client_fd);
        i += 1;
    }
```

It is a server and should never stop serving requests, thus the infinite loop.

Compile it and try running this program. You can comment the call to ```serve_connection``` for now.

```
Rust-C-Experiments/sync-async$ ./a.out 127.0.0.1 4200
Listening at (127.0.0.1, 4200)


```

Why is nothing happening? Let us dig a bit deeper. Lets use the ```ltrace``` utility to see whats going on.

```
Rust-C-Experiments/sync-async$ ltrace ./a.out 127.0.0.1 4200
atoi(0x7ffef260fa8d, 0x7ffef260eb28, 0x7ffef260eb48, 0x5563af46dd80)                              = 4200
socket(2, 1, 0)                                                                                   = 3
atoi(0x7ffef260fa8d, 1, 0, 0x7f1337d37077)                                                        = 4200
htons(4200, 0x7ffef260fa90, 0, 0x1999999999999999)                                                = 0x6810
inet_addr("127.0.0.1")                                                                            = 0x100007f
bind(3, 0x7ffef260ea10, 16, 0x7ffef260ea10)                                                       = 0
listen(3, 50, 16, 0x7f1337d36a27)                                                                 = 0
printf("Listening at (%s, %u)\n", "127.0.0.1", 4200Listening at (127.0.0.1, 4200)
)                                              = 31
memset(0x7ffef260ea20, '\0', 16)                                                                  = 0x7ffef260ea20
accept(3, 0x7ffef260ea20, 0x7ffef260e9f4, 0x7ffef260ea20
```

You will see that the process has just **stopped** after calling ```accept()```. In other words, ```accept()``` is yet to return. This is what **blocking** means.

When is it going to return? Will it ever return?

Open up another terminal and try connecting to it. You may use **netcat** or even **telnet** is enough.

```
dell@adwi:~/Documents/pwnthebox/Rust-C-Experiments/sync-async$ telnet 127.0.0.1 4200
Trying 127.0.0.1...
Connected to 127.0.0.1.
Escape character is '^]'.

```

If you something like above, then you should see the the following in your server terminal.

```
accept(3, 0x7ffef260ea20, 0x7ffef260e9f4, 0x7ffef260ea20
 <no return ...>
--- SIGWINCH (Window changed) ---
<... accept resumed> )                                                                            = 6
printf("Serving request for a client no "..., 0Serving request for a client no 0!
)                                                  = 35
```

So, ```accept()``` returned.

Now comes the interesting part. Once it returns, we call the ```serve_connection()``` which handles the client connection. Note that this function's definition depends on what type of server this is. Whatever we have coded so far doesn't tell us which type of server it is - is it HTTP Server, FTP Server etc.,

Important point to note is that **it can take as much time it wants** to return. Why is that? Lets discuss further.

For simplicity sake, the following is our ```serve_connection``` definition.

```c
void serve_connection (int client_fd)
{   
    uint8_t         request_buffer[10000] = {0};
    uint8_t         response_buffer[10000] = {0};
    int             ret = 0;

    // Only one request response!
    ret = recv(client_fd, request_buffer, sizeof(request_buffer), 0);
    if (ret < 0)
    {
        printf("recv() failed for fd = %d\n", ret);
        return;
    }

    // Print the request (symbolic of processing the request)
    printf("%d: %s\n", client_fd, request_buffer);

    // Send back response
    ret = send(client_fd, "Hello from server!", 19, 0);
    if (ret < 19)
    {
        printf("send() failed for fd = %d\n", ret);
        return;
    }

    // Done, go back.
    return;
}
```

Its pretty straightforward. It tries to receive something from the client. Once it receives, it will send back a string to the server.

This is an interesting function and a lot can happen here. Lets see.

If your server terminal is still open, you might see the following.

```
accept(3, 0x7ffef260ea20, 0x7ffef260e9f4, 0x7ffef260ea20
 <no return ...>
--- SIGWINCH (Window changed) ---
<... accept resumed> )                                                                            = 6
printf("Serving request for a client no "..., 0Serving request for a client no 0!
)                                                  = 35
memset(0x7ffef2609ba0, '\0', 10000)                                                               = 0x7ffef2609ba0
memset(0x7ffef260c2b0, '\0', 10000)                                                               = 0x7ffef260c2b0
recv(6, 0x7ffef2609ba0, 10000, 0
```

The process has just stopped or **blocked** at ```recv```. Natural right? Server is waiting to receive some data from the client. Till the client sends something, you will keep waiting.

Even when the client sends the data to server, the server doesn't receive it immediately. It has come through lot of routers, switches covering a lot of physical distance - there is some inevitable propagation delay.

A lot of things can happen when the packets are travelling in a network. The packet might get corrupted in the middle and get dropped, or it might be dropped by a router just due to congestion. Suppose there are 20 packets and the third gets dropped. The TCP protocol won't leave till it gets that 3rd packet. What is the impact?

The ```recv()``` won't return till the data **successfully** comes through. Although all the details are abstracted from us, it will reflect in the amount of time taken for ```recv()``` to return.

This is called **blocking I/O**. Input/Output or I/O generally refers to you reading/writing to disk OR receving/sending data to a network.

Generally, two kinds of code are present in a program. One that requires a lot of your CPU time - CPU intensive code and other which is I/O intensive - code which keeps reading/writing to disk or keeps doing Network I/O. When the CPU is running your code, some **work** is being done. But when some I/O happens(consider that call to ```send()```), you pass to the **kernel** the buffer you want to send to the device connected to you. Once you call that system call, there is nothing in your hands.

1. Kernel code runs and it sends the data to the network.
2. The packets now travel through the network - this part is not even in kernel's hands.
3. If any packet is dropped, kernel code is invoked again and this keeps happening till you get an acknowledgement from the other end that it has received all of the data.

What do our process do during this time? It patiently **waits**. Only when the system call returns, we continue. That is a lot of time wasted. Why exactly is it wasted? If there was some way to bypass this time-waste, we could have run more server code, accepted more connections (where again we'll have to wait at some point). But we atleast do some useful work of catering to some other connections.

The above example was very specific to the Network I/O's ```send()```. Lets consider a couple of other I/O based system calls.

We discussed ```recv``` before and we saw that is blocking as well. Take a simple ```write``` to disk. Even there, you pass the buffer you want to write to some file to the system call. In the small programs we write, we(humans) don't **feel** the blocking part - because all we do is write some amount of bytes. Even if you write 5MB at once, it happens in milliseconds and hence a human can't really feel the blocking. But think what your process could do if it had those milliseconds? It would have executed a couple million instructions. Even ```read``` is like that. You tell the **kernel** which file to read from and also pass the buffer where the **kernel** should store after reading from file. This also feels fast, but it is still blocking in reality. Try writing a simple network client - which tries to ```connect()``` to some server out there. In normal cases, it doesn't feel like a blocking call at all. It returns within no time (for humans :P). But even there, the TCP handshake needs to happen - again something your process can do nothing about, but to wait.

Till each of these I/O related system calls return, our program will be waiting. In other words, those system calls are said to be **blocking** system calls - they are **blocking** the execution of our program. They just block your execution till something(which is totally not in your hands) happen. But also note that this the I/O is relevant. It is part of your program and can't be ignored.

Sometimes, there might be function calls inside our program itself which just take lot of time - a highly CPU intensive piece of program. Is it a blocking function call? Not really. That is still your code running. So, thats not a blocking call.

I hope you got an idea of what blocking calls and blocking I/O means.

Continuing with our server program, it waits till it receives some data from client. It prints it (printf is also blocking I/O, because it calls write in the end and data is being written to monitor - hardware), and sends some data to the client and go back.

Once ```serve_connection``` returns, we close that socket associated with the client and go back to waiting for a new connection at ```accept```. If there are already requests queued (we passed queue-size = 50 in the ```listen``` call), ```accept``` returns immediately.

Just play around with the server a little bit. Switch it on and try opening up multiple clients, see how it works, what happens etc.,

## 2. Problems?

We have a couple of problems in our server. 

1. It can only serve one connection at a time. If there are more connection requests, they are simply queued - not accepted.

2. We have the blocking I/O issue which magnifies the problem of handling one connection at a time.

In the whole of this series, we will be talking about the above two problems.

This program doesn't do a lot of things right, starting with the most important thing - error handling. It doesn't handle it at all. It simply returns errors without cleaning up - which is wrong. It is just enough for learning and exploring these concepts.

## 3. The know it all!

Consider the blocking I/O issue. Consider the ```send()``` example where send some data to our connection.

The following is ```send()```'s prototype from manpage.

```c
ssize_t send(int sockfd, const void *buf, size_t len, int flags);
```

You tell where to send the data using your socket descriptor, what to send, how much is there to send. Whom do you tell all this? the **kernel**! Once this function is called, our code has no idea when it will return. It returns when it returns.

Does the kernel also feel the same way? It is the one sending the data. It should ideally know everything about how much time the entire operation takes. But that is not the case. Once kernel sends a packet of data out, it also has no idea what happens to that packet. It might get dropped or it might go in one shot. So even for kernel, there is an element of **uncertainty** or **suspense** :P . Only when the final ACK comes back, the kernel knows that the data has been sent successfully(or that the I/O was is successful). If you think about it, kernel is also dealing with blocking I/O. But, the point to note is that kernel will **definitely** know the end of an I/O operation at some point in time.

See this.

1. Our program has no idea when that I/O call returns. In other words, our program has no idea for how long that I/O call blocks.
2. Kernel is closer to the action and it will know for sure after certain developments happen(like getting the last ACK). Kernel definitely has more knowledge on what is happening with a particular I/O call, it will know when an I/O is done.

Is there someone who know everything about an I/O operation? How much time it takes? When it returns? Not really, no one. One can only estimate the time taken, there is no deterministic way to find out what happens to a packet after its injected to the network. There is **uncertainty**. There are a lot of actors doing their own things(your program, kernel, the WiFi Card, large number of routers in the middle, firewall, the other end-device etc.,).

Why are we even discussing who knows how much about that I/O call our program made? We don't want our process to wait, thats why. If someone knew how much time a particular I/O operation takes and it tells us that (say) it takes 20 ms, I would call ```recv``` and somehow just go ahead and run some more server code. Right after 20 ms have passed by, I would come back, take the return value/buffer and process it. But there is no "know it all" entity like that. But the situation is not that bad. We have our **kernel**. Kernel would know when an I/O operation is over. Can this information be used? Can the kernel tell us when an I/O is done? How will it help us? Lets revisit this point in the future posts.

## 4. What does Synchronous mean?

When we use blocking system calls, what we are doing is essentially synchronous programming. What is synchronous about it? Why is it called so? I think it would be good to discuss this when we encounter this beast called **asynchronous**. That will happen in one of the future posts.

## 5. Conclusion

We have come to the end of the post.

I hope you got some idea about what blocking I/O means. We have two problems to explore.

1. Our server serves just one connection at a time.
2. Is there any way to bypass the time-waste which happens through blocking I/O calls? Can we just somehow bypass the blocking calls?

Just remember that although no one entity knows everything about an I/O operation, the kernel is very close to it and it will help us. It knows for sure when an I/O operation is over. Do not forget this :P

In the next post, we will be exploring some ways to solve problem (1).

Side note: I realized that TCP is such a wonderful protocol. It tries to deal with this I/O uncertainty in a deterministic manner. Because it cares about the uncertainty, it is also a good protocol to choose when one needs to understand blocking. It just doesn't return till everything is fine or atleast get an acknowledgement that its all screwed up. UDP that way is really boring - you just send the packets and return - not caring about what happened to them.

That is it for this post.

Thanks for reading :)