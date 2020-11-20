---
title: What is polling?
categories: rust
comments: true
layout: post
---

In the [previous post](/rust/2020/11/11/is-a-single-thread-enough.html), we discussed about events and the ```select``` system call. We discussed that there are two ways to solve or work our way through the blocking problem: One is by using an event notification mechanism and other is through checking if the event happened at regular intervals. We have seen an example of the first mechanism in the previous post.

In this post, we will be exploring the concept of polling. We will try to rewrite our [echo server](https://github.com/adwait1-G/Rust-C-Experiments/blob/main/sync-async/echo_server_v1.c) using the polling mechanism.

A note: Do not confuse this with the [poll](https://man7.org/linux/man-pages/man2/poll.2.html). ```poll``` is another event notification system call similar to ```select```, but better in a couple of ways.

Lets start!

1. Talk about the newspaper/milk example again. How polling works there. - DONE
2. Although we are the only actor, we are taking help of one more element: The clock, the timer. Does kernel offer any timers? Taking kernel's help. - DONE
2. Slowly make them understand that implementing polling won't be possible with blocking system calls - exactly the point to introduce SOCK_NONBLOCK.
3. That would have setup the base for implementing polling. Go ahead and implement it.

## 1. A quick recap on polling

You are at home, busy with your work. You have subscribed for everyday milk, newspaper delivery. The milkman/newspaper guy comes and delivers it to your home. You drink the milk as soon as it is delivered, you read the newspaper as soon as it is delivered. Problem here is that you don't know when either of them will be delivered. You need to pick up the milk/newspaper as soon as possible and do the needful. How can you do this?

One bad, **blocking** solution is to leave your work, just open the door and stand there. Wait till they are delivered. This is very similar to the ```recv```, ```accept``` calls blocking. We don't want to do that.

What else can we do? We have explored the idea of an explicit event notification mechanism, like the door-bell. Whenever they are delivered, we want the milkman/newspaper guy to ring the door-bell. We hear the door-bell and we then go to the door, pick them up and do the needful. This mechanism involves a 3 main actors.

1. The milkman/newspaper guy: Responsible for ringing the door-bell. If he doesn't ring, then it is useless.
2. The door-bell itself: This is the explicit event notification mechanism present without which all of this is pointless.
3. You: You take action when you hear the door-bell sound.

But what if your home doesn't have a door-bell installed? What if the milkman/newspaper guy forgets ringing the door-bell? You would never know then. This way, you need an explicit mechanism installed/implemented and you need the milkman/newspaper guy to obey certain instructions (like ring the bell).

We also discussed one more way of doing this: **polling**. At a regular interval, you leave your work, go to the door and check if either milk/newspaper is present. If it is present, get them. If it is not, close the door and get back to work. Again after some time, you go and check the door if there is anything. This way, you are not totally sidelining your work (it is not fully blocking). You are simply spending some amount of time to make sure you process those things in time(before milk goes stale etc.,).

We will be rewriting our server using polling.

## 2. Are we the only actor? - The sense of time

You can see that polling does not require many actors. But are we the only actor? Can we solve the milk/newspaper problem all by ourself without any help? Go over the polling based solution and think about it.

We can't. We need to leave the work at **regular intervals** and then do the polling. We need a sense of time here. Suppose we use a simple alarm for that will ring every (say) 15 minutes. Whenver it rings, you will go and poll. If you think about it, this is also sort of event-based. 15 minutes passing by is an event. We are notified about that event through the alarm-ring. We then take action - which is to go to the door and check if anything has been delivered. Anyway, we need to keep track of time. Applying this idea to our server, we would also need a sense of time here.

Our server will have no work when there are no new connection requests or client data coming in. When there is no work, our server can sleep peacefully. So what we want to do is this: Sleep for some time, wake up, poll for events. If there are any events, process it. When done, go back to sleep. Which construct can we use achieve this?

The [sleep](https://man7.org/linux/man-pages/man3/sleep.3.html) suits our purpose. Let us open up a new C sourcefile and code the above.

```c
int main (int argc, char **argv)
{
    if (argc != 3)
    {
        printf("Usage: $ %s [host-ipv4-address] [port-number] [poll-time-interval]\n", argv[0]);
        return 0;
    }

    // Initialize the server socket here

    while (1)
    {
        // poll_for_events(server_fd, fds_list);
        sleep(poll_time_interval);
    }
```

Does that make sense? There is some function ```poll_for_events``` which is called. If there are I/O events(new connection requests/client data), they are processed. Then you sleep for some time. Again you wake up and poll. This keeps happening forever.

Initialize the server socket - create it, bind and listen on it.

```c
    // Lets create a socket.
    ret = socket(AF_INET, SOCK_STREAM, 0);
    if (ret < 0)
    {
        printf("socket() failed\n");
        return -1;
    }
    server_fd = ret;

    // Bind the socket to the passed (ip_address, port_no).
    server_addr.sin_port = htons(atoi(argv[2]));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr(argv[1]);
    
    ret = bind(server_fd, (const struct sockaddr *)&server_addr, sizeof(server_addr));
    if (ret < 0)
    {
        printf("bind() failed\n");
        return -1;
    }
    
    // Start listening
    ret = listen(server_fd, 50);
    if (ret < 0)
    {
        printf("listen() failed\n");
        return -1;
    }
    printf("Listening at (%s, %u)\n", ip_addr, port_no);

    // What do we do here?
    while (1)
    {
        poll_for_events(server_fd, fds_list);
        sleep(poll_time_interval);
    }
```

You can take ```poll_time_interval``` as a command-line argument. Write a dummy ```poll_for_events``` function and make sure the program works as intended.

## 3. Polling for events

As you can see, this is the core/workhorse of the server. It does all the work or polling and if events have happened, processing them.

The logic for polling is simple. You go to the door, open it and check if anything(milk/newspaper) is present. If they are not present, come back. If present, process and come back. Let us do the exact same thing now.

Here, we want to poll for 2 events: New connection requests - which will affect ```accept``` and Client Data which will affect ```recv```. Because there is only one thread, we can't poll them simultaneously. We need to poll one after the other. Poll simply means **check** if present. How do we check? In our case, the only way to know if there is a new connection request is by actually calling ```accept```. Similarly, the only way to know if there is client data on a connection-socket is by calling ```recv```. Let us go ahead and call them in the ```poll_for_events``` function.

First, let us call ```accept```.

```c
void poll_for_events (int server_fd, bool *fds_list)
{
    int                     ret = 0;
    int                     i = 0;
    int                     client_fd = 0;
    struct sockaddr_in      client_addr = {0};
    socklen_t               client_addr_len = 0;
    uint8_t                 request_buffer[10000] = {0};
    printf("poll_for_events invoked\n");

    // Poll for new requests by calling accept.
    ret = accept(server_fd, (struct sockaddr *)&client_addr, &client_addr_len);
    if (ret < 0)
    {
        printf("accept() failed\n");
        exit(-1);
    }
    client_fd = ret;

    // Reaching here means accept ret has a new
    // descriptor. We handle only 1024 descriptors. Note it.
    if (client_fd >= 1024)
    {
        close(client_fd);
    }
    else
    {
        // Add it to our list
        fds_list[client_fd] = true;
    }
```

Slowly read through the code, it is fairly simple. ```fds_list``` is used to keep note of all the valid socket descriptors which we need keep an eye on.

Next comes processing any client data on any socket. There can be multiple connections present. We need to iterate through them and call ```recv``` on each connection - in a hope that there is some client data. The following does it. If ```recv``` succeeds, then all you need to do is ```send()``` it back.

```c
// accept's job is done. Now onto recv

    // All numbers in fds_list may not be valid
    // descriptors. Check each one and if it is, call recv on it.
    for (i = 0; i < 1024; i++)
    {   
        // Check if it is a valid socket descriptor
        if (fds_list[i] == true)
        {
            // If it is, then call recv on it.
            ret = recv(i, request_buffer, sizeof(request_buffer), 0);
            if (ret < 0 || ret == 0)
            {
                // If ret < 0, then recv errored out. Cleanup needed.
                // If ret = 0, then client closed the connection. Cleanup needed.
                close(i);
                fds_list[i] = false;
            }

            // If we are here, that means recv succeeded.
            // All we need to do is send back the data.
            ret = send(i, request_buffer, sizeof(request_buffer), 0);
            if (ret < 0)    // Cleanup needed.
            {
                printf("send() failed\n");
                close (i);
                fds_list[i] = false;
            }
        }
```

That is the basic logic. Run your program a couple of times, with several connections and observe its behavior.

The obvious thing is that the call to ```accept``` blocks! If it goes through, ```recv``` might block.

This is not what we wanted right? We just wanted to check if there are events. If events have not happened, **we want to come back** and **not block**. But here, we block.

But that is the fundamental nature of ```accept``` and ```recv``` right? They block. Our "let us take chance and call it" method fails.

If you closely observe, it can sometimes be worse than a simple echo server which simply serves a connection at a time without the sleep and poll jazz.

How do we get the **just check, if not present, come back** functionality instead of blocking?

## 4. Will Non-blocking sockets help?

The sockets we have been creating and using so far are called **blocking sockets**. It means all the I/O calls called **on** such socket are blocking in nature. We call such calls as blocking calls.

We want to implement the following behavior: If the event has happened, the call should succeed and return meaningful code. If it has not happened, it should return telling that event we are waiting for has not yet happened.

Such calls are called **non-blocking** calls. It will either pass or fail, instantly. How do you use non-blocking calls?

To use them, you need to use **non-blocking sockets**. When we use non-blocking sockets, the I/O calls **on** them will be non-blocking. For example, we create a non-blocking socket and some time later, we call ```accept``` on it. It obviously won't block when there is a connection request in the queue. Point is that it won't block **even if there are no connection requests** in the queue. It will simply return telling there are no requests to process at the moment.

How do we create such **non-blocking sockets**? Let us go back to [socket manpage](https://man7.org/linux/man-pages/man2/socket.2.html). The following lines will help us.

>Since Linux 2.6.27, the type argument serves a second purpose: in
       addition to specifying a socket type, it may include the bitwise OR
       of any of the following values, to modify the behavior of socket():

>       SOCK_NONBLOCK   Set the O_NONBLOCK file status flag on the open file
                       description (see open(2)) referred to by the new file
                       descriptor.  Using this flag saves extra calls to
                       fcntl(2) to achieve the same result.

>       SOCK_CLOEXEC    Set the close-on-exec (FD_CLOEXEC) flag on the new
                       file descriptor.  See the description of the
                       O_CLOEXEC flag in open(2) for reasons why this may be
                       useful.


The ```SOCK_NONBLOCK``` flag should help us. It can be bitwise ORd with ```SOCK_STREAM``` and that will magically give us a non-blocking socket (or a socket on which I/O calls don't block). Let us go ahead and change our ```socket``` call to create a non-blocking one.

```c
    // Lets create a socket.
    ret = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK, 0);
    if (ret < 0)
    {
        printf("socket() failed\n");
        return -1;
    }
    server_fd = ret;
```

We know that ```accept``` returns a non-zero number on success - which is a valid socket descriptor. But what will it return when there no outstanding requests present? From [accept's manpage](https://man7.org/linux/man-pages/man2/accept.2.html),

> If no pending connections are present on the queue, and the socket is
       not marked as nonblocking, accept() blocks the caller until a
       connection is present.  If the socket is marked nonblocking and no
       pending connections are present on the queue, accept() fails with the
       error EAGAIN or EWOULDBLOCK.

It returns a ```EAGAIN``` or ```EWOULDBLOCK```. More about it from the manpage.

> EAGAIN or EWOULDBLOCK
              The socket is marked nonblocking and no connections are
              present to be accepted.  POSIX.1-2001 and POSIX.1-2008 allow
              either error to be returned for this case, and do not require
              these constants to have the same value, so a portable
              application should check for both possibilities.

Now our check of ```ret < 0``` simply kills the server. We need to change that because now, we have an error which is useful and telling us something. Let us check if the errorcode is either ```EAGAIN``` or ```EWOULDBLOCK```. If it is one of these, then let us continue. IF it is some other error, let us kill the server. You will have to include **errno.h** because EAGAIN and EWOULDBLOCK are defined there.

At this point, ```accept``` should **never** block. Either it should succeed on a outstanding request and return the descriptor for a new socket OR it should return asking us to try again later.

Here, ```accept()``` returns a plain **-1** on error, but from that we can't derive what error it is. We need to check the **errno** variable if it is ```EAGAIN``` or ```EWOULDBLOCK```. If it is anything else, let us kill the server. Here is the code that implements it.

```c
    // Poll for new requests by calling accept.
    ret = accept(server_fd, (struct sockaddr *)&client_addr, &client_addr_len);
    printf("accept() returned %d\n", ret);
    if (ret > 0)
    {
        // Success case: We have a new socket!
        client_fd = ret;
        
        // Reaching here means accept ret has a new
        // descriptor. We handle only 1023 descriptors. Note it.
        if (client_fd >= 1024)
        {
            close(client_fd);
        }
        else
        {
            fds_list[client_fd] = true;
        }
    }
    else if (ret < 0)
    {   
        // Some error occured. What error?
        // errno will have the proper error code, check it.
        if (errno == EAGAIN || errno == EWOULDBLOCK)
        {
            // Looks like there is no outstanding connection
            // request. So it is asking us to try later.
            printf("accept() returned EAGAIN or EWOULDBLOCK. Try again later\n");
        }
        else
        {
            // If it is any other error, it means something else
            // went wrong. Kill!
            printf("accept() failed\n");
            exit(-1);
        }
    }
```

Now compile it and run it. I have added a couple of ```printf```s here and there to know what is going on.

```
Rust-C-Experiments/sync-async$ gcc echo_server_v2.c
Rust-C-Experiments/sync-async$ ./a.out 127.0.0.1 4201 10
Listening at (127.0.0.1, 4201)
poll_for_events invoked
accept() returned -1
accept() returned EAGAIN or EWOULDBLOCK. Try again later
accept() done. Going to recv!
poll_for_events done. Going back to sleep
accept() returned -1
accept() returned EAGAIN or EWOULDBLOCK. Try again later
accept() done. Going to recv!
poll_for_events done. Going back to sleep
.
.
```

Now from another terminal, connect to it.

```
Rust-C-Experiments/sync-async$ telnet 127.0.0.1 4201
Trying 127.0.0.1...
Connected to 127.0.0.1.
Escape character is '^]'.
```

Sooner or later, it will get connected. If you try to connect when the server is sleeping, it won't connect immediately. Now, the following is what I see on the serverside.

```
accept() returned -1
accept() returned EAGAIN or EWOULDBLOCK. Try again later
accept() done. Going to recv!
poll_for_events done. Going back to sleep
poll_for_events invoked
accept() returned 7
accept() done. Going to recv!
```

And just stuck there. What do you think is happening?

It is **blocking** at ```recv```. Again, this is not the intended behavior. If there is no data, ```recv``` should also return something like ```EAGAIN``` or ```EWOULDBLOCK``` but it should not block.

Think about it. If it is blocking, then the socket we are operating on **is** a blocking socket. What is the socket we are working on? We are calling ```recv``` on the **new** socket created by ```accept```. Won't ```accept``` create non-blocking sockets? We have already passed ```SOCK_NONBLOCK``` to the server socket right? This requires a bit more work. Try going through [accept's manpage](https://man7.org/linux/man-pages/man2/accept.2.html) and figure out what is going on and what needs to be done.

> On Linux, the new socket returned by accept() does not inherit file status flags such as O_NONBLOCK and O_ASYNC from the listening socket.  This behavior differs from the canonical BSD sockets implementation.  Portable programs should not rely on inheritance or noninheritance of file status flags and always explicitly set all required flags on the socket returned from accept().

Using ```SOCK_NONBLOCK``` is exactly the same as usint the ```O_NONBLOCK``` on the file descriptor. Refer to the following lines from [socket's manpage](https://man7.org/linux/man-pages/man2/socket.2.html).

> SOCK_NONBLOCK   Set the O_NONBLOCK file status flag on the open file description (see open(2)) referred to by the new file descriptor.  Using this flag saves extra calls to fcntl(2) to achieve the same result.

It means the non-blocking nature of the server socket is **not inherited** into the sockets created by calling ```accept``` on it. We need to make **explicitly** make it non-blocking. But how do we do that? ```accept``` is creating the socket and we are not calling ```socket```. Is there a way to tell ```accept``` to create non-blocking sockets? If you look at ```accept```'s manpage, it has two functions - ```accept``` and ```accept4```. ```accept4``` has a **flags** argument.

```c
#define _GNU_SOURCE             /* See feature_test_macros(7) */
       #include <sys/socket.h>

       int accept4(int sockfd, struct sockaddr *addr,
                   socklen_t *addrlen, int flags);
```

Reading on, you will find the following lines.

> If flags is 0, then accept4() is the same as accept().  The following values can be bitwise ORed in flags to obtain different behavior:

> SOCK_NONBLOCK   Set the O_NONBLOCK file status flag on the open file description (see open(2)) referred to by the new file descriptor.  Using this flag saves extra calls to fcntl(2) to achieve the same result.

We should be using ```accept4``` and pass ```SOCK_NONBLOCK``` flag to the **flags** argument, like the following.

```c
    // Poll for new requests by calling accept.
    ret = accept4(server_fd, (struct sockaddr *)&client_addr, &client_addr_len, SOCK_NONBLOCK);
    printf("accept4() returned %d\n", ret);
```

Because now ```recv``` also won't block, we need to handle its errors properly - similar to ```accept```. Check its return value. If it some positive value, it means the client has sent some data. Let us send it back.

```c
           // If it is, then call recv on it.
            ret = recv(i, request_buffer, sizeof(request_buffer), 0);
            printf("recv() on descriptor %d returned %d\n", i, ret);
            if (ret > 0)
            {
                // recv returned success - it has received some data.
                // We need to send back that data.
                ret = send(i, request_buffer, sizeof(request_buffer), 0);
                if (ret < 0)
                {
                    // If send failed, let us close the connection,
                    // remove from our descriptor list.
                    printf("send() on descriptor %d failed\n", i);
                    close(i);
                    fds_list[i] = false;
                }
                else
                {
                    printf("send() succeeded on %d\n", i);
                }
            }
```

What do we do when ```recv``` returns 0? In our case, it would return 0 when the client has disconnected. We also need to close it and remove it from our list of descriptors.

```c
            else if (ret == 0)
            {
                // If recv has returned 0,
                // it means that the client has disconnected.
                // Let us also cleanup.
                close(i);
                fds_list[i] = false;
            }
```

Now to the interesting part, when it returns **-1** - an error. Similar to ```accept```, we need to check ```errno``` and take action.

```c
           else // ret < 0 
            {
                // recv has errored out.
                // Time to check errno.
                if (errno == EAGAIN || errno == EWOULDBLOCK)
                {
                    printf("recv() returned EAGAIN or EWOULDBLOCK. Try again later\n");
                }
                else
                {
                    // Something fatal. Kill the server.
                    printf("recv() failed\n");
                    exit(-1);
                }
            }
        }
```

Now, I think we are ready. Compile and run it.

```
Rust-C-Experiments/sync-async$ ./a.out 127.0.0.1 4201 10
Listening at (127.0.0.1, 4201)
poll_for_events invoked
accept4() returned -1
accept4() returned EAGAIN or EWOULDBLOCK. Try again later
accept4() done. Going to recv!
poll_for_events done. Going back to sleep
```

When the server is started and no client tries connecting to it, only ```accept4``` is tried. Till we have a valid socket descriptor returned by ```accept```, we won't call ```recv```. Now, let us connect to it using telnet.

```
poll_for_events done. Going back to sleep
poll_for_events invoked
accept4() returned 7
accept4() done. Going to recv!
recv() on descriptor 7 returned -1
recv() returned EAGAIN or EWOULDBLOCK. Try again later
poll_for_events done. Going back to sleep
poll_for_events invoked
accept4() returned -1
accept4() returned EAGAIN or EWOULDBLOCK. Try again later
accept4() done. Going to recv!
recv() on descriptor 7 returned -1
recv() returned EAGAIN or EWOULDBLOCK. Try again later
poll_for_events done. Going back to sleep
poll_for_events invoked
```

Do you see that? ```accept``` returned a positive number - a socket descriptor. But we have not sent any data yet. ```recv``` is called on it but it keeps giving ```EAGAIN``` or ```EWOULDBLOCK```.

Now let us send some data. Send when it asleep.

```
Rust-C-Experiments/sync-async$ telnet 127.0.0.1 4201
Trying 127.0.0.1...
Connected to 127.0.0.1.
Escape character is '^]'.
wiehfowiehfowiehfoiwefhwoiehfowiehfwoiehfwoiefhwoef
```

It should **block on the client side**. Because when it sends data, the server is "busy" sleeping. Once it goes to poll phase, it will ```recv``` and ```send``` back data.

```
poll_for_events invoked
accept4() returned -1
accept4() returned EAGAIN or EWOULDBLOCK. Try again later
accept4() done. Going to recv!
recv() on descriptor 7 returned 53
send() succeeded on 7
poll_for_events done. Going back to sleep
```

With that, we have a simple, polling based server. We make use of ```sleep()``` to get a sense of time. In the polling phase, we call ```accept4``` one time on the server socket, ```recv``` one time on all client-connected sockets.

Play around with the server, sending client requests at random time - see how it behaves.

## 5. Optimizations and cleanup

### 5.1 Separation of events

In the server, we can only about two types of events:

1. New connection requests at the server socket
2. Client data at one or more client-connected sockets.

Currently, we have put all the code inside on function called ```poll_for_events```. Instead of that, we can separate code based on events. Let us call them ```poll_for_new_conn_requests``` and ```poll_for_client_data```. We already have the code, we need to separate them in a proper manner. And finally call them both properly.

```c
    // What do we do here?
    while (1)
    {   
        poll_for_new_conn_requests(server_fd, fds_list);
        poll_for_client_data(fds_list);
        printf("Polling done. Going back to sleep\n");
        sleep(poll_time_interval);
    }
```

I see two advantages of doing this. One is the code looks cleaner - we have logically divided them. At the moment, only one thread is doing all the work. But if you observe, ```poll_for_new_conn_requests``` and ```poll_for_client_data``` can be run **parallely**. Code might get a bit compilcated then because both of them might be using the ```fds_list``` array at the same time - we will need a mutex/semaphore to solve the issue. But there is a possibility.

### 5.2 Is polling one time enough?

We are calling ```accept4``` just once every poll_time_interval(say this is 10 seconds). Suppose there is a surge of connections(say a 100) at the same time. We will be accepting one connection every 10 seconds here. In the same way, suppose a client wants to send data a number of times to the server. It won't be entertained properly - because ```recv``` on a client-connection socket is called once every 10 seconds. I think we are sleeping too much and not doing enough work. What can we do about this?

We can reduce the **poll_time_interval**. We have an inherent limitation in our implementation - ```sleep()``` takes only arguments in whole numbers. So 1 second is the smallest interval. What else can we do?

We can simply call ```accept4``` a couple of 100 times inside ```poll_for_new_conn_requests```. If there are connections requests, they will be accepted. If not, we will be doing some useless work, but we need to do that to ensure all clients are served properly. Same logic goes with ```recv``` as well. Try adding code to get this done.

## 6. send() is wierd!

Did you notice anything abnormal with the ```send()``` system call?

What does a call to ```send()``` do? It requests the kernel to send some data to the socket other side of connection. This means, **it is an I/O call**. Meaning it will inherently block - no matter how small the time is. To overcome this, we asked ```accept4``` to create non-blocking sockets so that any I/O call on it would not block.

We call ```recv``` and if it succeeds on a socket(meaning that client has sent some data), we are immediately ```send()```ing it back to client. Here, we actually don't feel ```send()``` blocking, but it still does.

Question is why does it block? Even when it is not supposed to? The following lines are from [send's manpage](https://man7.org/linux/man-pages/man2/send.2.html).

> When the message does not fit into the send buffer of the socket, send() normally blocks, unless the socket has been placed in nonblocking I/O mode.  In nonblocking mode it would fail with the error EAGAIN or EWOULDBLOCK in this case.  The select(2) call may be used to determine when it is possible to send more data.

Here, I think **send buffer** is referring to kernel buffer. We are sending 10,000 bytes of data. If it is larger than the kernel buffer, it blocks **unless** the socket is a non-blocking socket. That is fine.

But what happens when 10,000 bytes is **smaller** than kernel buffer? Will it block? Will it block even if the socket is a non-blocking one? This is not clear.

This happened with Linux Kernel 5.4.0-52-generic. You might be having a different kernel version, or other *NIX kernel or even windows.

Requires more research.

## 7. What did we achieve?

We wrote a simple, single-threaded, polling-based server. This uses **non-blocking I/O calls** to overcome the blocking problem in contrast to using a kernel-provided event notification mechanism like select.

We explored the concept of **polling** and touched upon **non-blocking calls**.

My implementation of the server is [here]https://github.com/adwait1-G/Rust-C-Experiments/blob/main/sync-async/echo_server_v2.c).

## 8. Conclusion

With that, I am ending this post.

I hope you have an idea about polling and non-blocking calls. Non-blocking calls are extremely useful and not just to implement polling. We will explore a lot of interesting things around non-blocking calls.

All the posts in this series revolve around events and event-driven paradigm - like having an event loop, using an event notification mechanism, taking action. I decided to write this post for two reasons: One is it would give a good idea of polling - where you initiate to do work(sometimes useless work) to check if any events have happened in contrast to the lazy event driven style. Other is that I felt that this is the natural place to introduce non-blocking calls. Polling requires non-blocking calls - there was a purpose. So, introducing it was easier.

Now that we have an single-threaded event-driven server using select and a single-threaded polling-based server, play around with them. Think about which one is more responsive, which one does more work, which one is lazy, which does how much of useless work etc., These are the things we have not discussed and we will in one of the future posts.

In the next post, we will explore the [poll](https://man7.org/linux/man-pages/man2/poll.2.html) system call. This is also an I/O event notifier like select, but there are differences. It is better in a bunch of ways.

I hope you learnt something out of this post.

Thank you for reading :-)