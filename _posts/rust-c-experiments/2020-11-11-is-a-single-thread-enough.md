---
title: Is a single thread enough? - Events, Notifications and Event Loop
categories: Rust
comments: true
layout: post
---

In the [previous post](/rust/2020/11/09/multithreading-and-multiprocessing.html), we explored how multithreading and multiprocessing can help in offloading the blocking problem to the threads/processes handling the connections. At the end, we had a short discussion on the possibility of having less number of threads and still doing the same amount of work. That is, do we need 100 threads to serve 100 connections? or can we do it in 50 threads? or 20 threads? etc.,

Can we do it all in a single thread? Maybe. In this post, let us take this challenge - of doing everything using a single thread. Whenever a new connection comes in, we are not supposed to spawn a thread/process and offload the blocking problem to it. You (the main thread) need to deal with this blocking problem head-on. Remember that the kernel is always there to help you :P

## 1. What is an event?

You are busy working from home. You are the only person staying at home. You have subscribed to services like milk and newspaper. As soon as they are delivered, you need to pick them up and you need to drink the milk and read the newspaper. Note that they can be delivered at different times. But there is a challenge: You have no idea when either of them will be delivered. You need to pick them up and do the needful as soon as they delivered. How are you going to do it?

The milkman might come at some time, just keep the milk outside the door and just go away. You have no way of knowing it. The newspaper guy might come, keep the newspaper outside the door and go away. Again, there is no way to know it. How do we solve this?

Generally, there are two ways to solve these types of problems. You can stop your work, open the door, checkout if anything is there. If there is nothing, go back to work and checkout the door again sometime later. At time point in time, milk will be present here(the milkman would have delivered and left silently). You pick it up and and drink it. You keep checking regularly. Maybe sometime later, the newspaper would be present there. You pick it up and read it. After that, you obviously don't have to check for anything else - you are done. You can carry on with your work.

What is another way to solve it? When the milkman delivers the milk, he can shout to pick up the milk (happens in India), or just ring the door-bell and go away. What do you do when the bell is rung? You leave whatever you are doing(generally) and checkout the door - see what happened, why the bell was rung. You see milk there. When you see the milk there, you know what to do - you need to drink it. The same with the newspaper. The newspaper guy keeps the newspaper there, rings the bell and goes away. You will do the rest.

What are we doing here? We are **expecting** for **something to happen** - like the milk being delivered, newspaper being delivered. We do **not know** when that something will happen though. Formally, this "something to happen" is known as an **event**. The following is the dictionary meaning of the word event: "a thing that happens or takes place, especially one of importance". Basically, it is anothing which requires your attention.

The first solution where you check regularly if the **event** has occured (if the milk is delivered, if the newspaper is delivered) is called known as **polling**. You **poll** for events regularly. Once those events are done (once you pick up the milk, pick up the newspaper), you don't have to poll anymore - you stop polling for them. Implementing this solution is easy. You need to make up your mind saying: I will check for events(milk, newspaper) every 15 minutes. Once this is decided, it is a matter of implementation. You stop the work you are busy with every 15 minutes, go check. If an event has occured (if milk/newspaper or both are present), you do the needful - drink the milk, read the newspaper and get back to your work. Quite simple. Note that you are the only actor here - only you are doing the job of polling.

What do you think about the second solution? Consider that the milkman/newspaper guy rings the bell. What does the bell signify? It is an **explicit event notification mechanism**. The event happens (the milk/newspaper is delivered), but it doesn't stop there. There is a system in place which can be used to notify you about that event as well. Here, several actors are necessary to make this solution work:

1. First of all, there should be a bell installed in your home. In other words, the explicit event notification mechanism needs to be **installed** or **implemented**. If it is not implemented, this solution makes absolutely no sense. The event notification mechanism is at the heart of this solution.

2. The milkman/newspaper guy should be **willing** to ring the bell. It might so happen that they forget to ring the bell in a hurry and go away. You will never know about the event then.

And ofcourse you are the third actor.

I hope you understand the two solutions.

Let us now come back to our blocking problem. Can you see how you can implement a **blocking** solution to the above milk/newspaper problem? It is quite simple. You stop the work you are busy with, just open the door and stand in front of it - till you get the milk/newspaper. Till you get something, you will simply be standing, doing nothing. Sounds a bit extreme right?

In both the above solutions (polling and the one using event notification mechanism), the need to process these events are not stopping you from working. You are working and there is some effort put into processing these events as well. This is what we wanted right? Our main thread should not be blocked at one particular I/O system call. Instead, it should be able to do some useful work (basically running code) and also take care of I/O events as they come along.

With that, for the blocking problem, we have two solutions in front of us. Which solution should we go for? Either of them can be used to solve the I/O blocking problem.

The polling solution is quite simple (simple in terms of code as well), but you will end up doing some useless work - all the times when you go to the door and there is no milk and newspaper there is essentially a waste right? This solution is computationally expensive. How often do you poll? Do you poll for milk/newspaper every minute? Do you poll for it every 30 minutes? Remember that the idea is that you need to process it as soon as it is delivered. But if your polling time interval increases, more likely that you will process it some time after it is delivered. But what happens when you poll very frequently? You might end up doing lot of useless work - go, check, nothing is there, come back. How do you fix on the polling time interval?

Now coming to the solution based on the explicit event notification mechanism. You will be doing your work, not caring about any of those events. Only when the door-bell is rung, you need to stop the work, go to the door and pick it up. Here, it feels like you just do the exact amount of work required right? You do it only when it comes and don't care about it otherwise. Here, we are not doing lot of useless work unlike polling, but at what cost? This is coming at the cost of an explicit event notification mechanism. Such a mechanism needs to be present to make it work right? If the door-bell is not present, no point. This comes at the cost of more code and higher code complexity.

Which one do we use?

We will be currently using the second solution. The kernel offers such explicit event notification mechanisms in the form of system calls. We can make use of them to solve the blocking problem. Just repeating it, the event notification works only because the kernel is providing a facility. If it was not present, we should have implemented polling all by ourself (which we will actually do in the next post).

I hope you understand what an event is, what an event notification is, what an event notification mechanism is.

Let us comeback to our server example.

What type of event are we expecting when we call ```accept```? They are new connection requests. Instead of calling ```accept``` (or just stand next to the door) and waiting for a new connection request to come in(wait for the milk to be delivered), we want the notification mechanism to notify us whenever the new connection request comes in (or when the milk is delivered). Once it notifies us, we will process that new connection request (milk) by calling ```accept``` on it (by drinking it). Does that make sense? The following lines are from [accept manpage](https://man7.org/linux/man-pages/man2/accept.2.html).

> In order to be notified of incoming connections on a socket, you can use select(2), poll(2), or epoll(7).  A readable event will be delivered when a new connection is attempted and you may then call accept() to get a socket for that connection.  Alternatively, you can set the socket to deliver SIGIO when activity occurs on a socket; see socket(7) for details.

[select](https://man7.org/linux/man-pages/man2/select.2.html), [poll](https://man7.org/linux/man-pages/man2/poll.2.html), [epoll](https://man7.org/linux/man-pages/man7/epoll.7.html) are the system calls - which are event notification mechanisms that the Linux Kernel provides.

What type of event are we expecting when we call ```recv``` on a socket? We are expecting some data from the other end of the connection. The following are the lines from [recv's manpage](https://man7.org/linux/man-pages/man2/recv.2.html).

> An application can use select(2), poll(2), or epoll(7) to determine when more data arrives on a socket.

The same notification mechanisms for two different types of events? Will that work? It should right?. We just have door-bell as the notification mechanism. It can cater to milk, newspaper, some guest who comes etc., The door-bell will tell you that there is an event you need to process. It doesn't tell you what event it is(is it milk, is it newspaper). Once you open the door, you need to check what the event is and accordingly take action.

Let us get started with the first system call: select.

## 2. The select system call

The [select manpage](https://man6.org/linux/man-pages/man2/select.2.html) is amazing as describes clearly what this does and what we can use it for.

> select() allows a program to monitor multiple file descriptors, waiting until one or more of the file descriptors become "ready" for some class of I/O operation (e.g., input possible).

It introduces the idea of a file descriptor being **ready** for an I/O operation. Let us see what this readiness means.

Given the server socket(anologous to the door), you can call ```accept``` on it anytime you want (you can open the door anytime you want). But there may not be any connection request present in the listen queue (there may not be milk there). What do you do then? You end up waiting and we are back to the blocking problem. When can we call ```accept``` and not block? When there is a connection request present in the listen queue. It means that socket is **ready** for the ```accept``` system call - which is actually an I/O operation. That is what ready means. When a particular event has happened at a socket, that socket is "ready". Consider a socket talking to a client and you are expecting some data from the client. Here, the system call we want to call is ```recv```, but we don't want to call it and wait. Instead, let us call it when that socket is ready. In this example, "ready" means that there is some client-sent data at this socket - which can be received. That was about **readyness** of a socket for an I/O operation.

Idea is that blocking calls do not block when the corresponding events happen. ```accept``` won't block when there is atleast one connection request in the listen queue. ```recv``` won't block when there is some client-sent data at a connection-socket.

The ```select``` system call is not as generic as the door-bell. With the door-bell, you have no clue what event has happened - you just know some event has happened and only when you open the door, you will know what that event is. First of all, ```select``` only notifies about I/O events. ```select``` can notify about multiple file descriptors, not just one(door-bell works just for that door). The ```select``` system call requires us(programmers) to create 3 seperate sets of descriptors: 

1. A set of descriptors you want to **read** from. Basically, ```select``` will tell you when one/more descriptors from that read-set is **ready** for reading.
2. A set of descriptors you want to **write** into.
3. A set of descriptors you want to monitor for exceptional events.

In this post, we will need only the **read-set**.

Cool, it will monitor those descriptors and notify us when some descriptor is ready for reading. But what exactly does **notify** mean? That idea of notification is still abstract - we don't know how it looks in our program. Let us start by rewriting our server using ```select```. That  should give an idea. Before going to the next section, please go through select's manpage.

### 2.1 Server using select

The entire program is listed [here](https://github.com/adwait1-G/Rust-C-Experiments/blob/main/sync-async/server_v4.c).

Let us start by deciding what sets of file descriptors we would need. For ```select```, we can pass three categories of descriptors: read-set, write-set and except-set. What types of sockets do we have? We have one server socket - which we use to listen and accept incoming connection requests. All the other sockets are spawned by ```accept``` - these are the connection-sockets.

Think of the kind of I/O we need to perform on these two types of sockets. On the server socket, we are waiting for a connection request. Once it is there, we will process it. If you think about it, in a wierd way, we simply want to **read** on that server socket. This is not a normal data-read, but a connection-request read. On all the other types of sockets, the first thing we want to do is to call ```recv``` on them. In other words, we want to **read** data from those sockets. All in all, we just need a ```read_set```. Let us initialize a **read_set**.

```c
    fd_set              read_set = {0};
```

Before entering the loop, you zeroize it.

```c
    // Before entering, initialize everything we need to call select.
    // This set is passed to select, it gets altered when select succeeds.
    FD_ZERO(&read_set);
```

We retain the infinite loop, because we want the server to run forever.

What are the descriptors we want to monitor? We want to monitor the server socket.

```c
    // Do the thing
    while (1)
    {
        memset(&client_addr, '\0', sizeof(client_addr));

        // Copy.
        FD_SET(sock_fd, &read_set);
```

Once that is done, let us call ```select```.

```c
        printf("Waiting for select() to succeed\n");
        ret = select(FD_SETSIZE, &read_set, NULL, NULL, NULL);
        if (ret <= 0)
        {
            printf("select() failed\n");
            return -1;
        }
        printf("After select, %d descriptors are ready!\n", ret);
```

What do you expect ```select``` to do here? Will it block? Will it not block?

The following lines are from select's manpage.

> On success, select() and pselect() return the number of file descriptors contained in the three returned descriptor sets (that is, the total number of bits that are set in readfds, writefds, exceptfds).  The return value may be zero if the timeout expired before any file descriptors became ready.

The ```select``` system call returns the total number of file descriptors which are **ready** for some sort of I/O operation. If there is no descriptor ready for an I/O operation, then it won't return aka it will block.

To start with, we just monitor one file descriptor: The server socket descriptor. If we just run the server and not send any connection requests, then ```select``` would block. Wait, we were trying to get rid of blocking and now even the event notification system call blocks?

It is important to understand that ```select``` blocks only when there is no work - or no descriptor is ready for an I/O operation. What work will you do when there no work? Only when some descriptor is ready, you will get some work. Until then, you can block/sleep. That is the behavior.

We send a connection request and ```select``` returns, what do we do? Note that ```select``` doesn't return directly the ready file descriptors. Instead, it uses the ```read_set``` we have passed to it. Suppose you ```FD_SET``` 10 descriptors into ```read_set``` - you want ```select``` to keep an eye on those 10 descriptors. Suppose one of the file descriptor becomes ready for an I/O system call. The ```select``` system call removes all the descriptors not-ready for I/O and just sets the one which is ready. So when ```select``` returns, the ```read_set``` would have just one descriptor which we can act on.

In our case, there is just one socket descriptor - the server socket. If ```select``` returns, we know that the server socket is ready for I/O. What system call should we call on it?

```c
        // Suppose it succeeds, we don't know which sockets are ready.
        // All the "ready" sockets are set in those sets.
        // We know the socket value, we need to go over them and see
        // which one to process first.
        
        // If this comes true, that means we have an incoming connection
        // waiting to be accepted.
        if (FD_ISSET(sock_fd, &read_set))
        {   
            printf("Inside sock_fd if\n");
            ret = accept(sock_fd, (struct sockaddr *)&client_addr, &client_addr_len);
            if (ret < 0)
            {
                printf("accept4() failed\n");
                return -1;
            }
            client_fd = ret;
            printf("client_fd = %d\n", client_fd);
```

You check if there the server socket is ready for I/O using the ```FD_ISSET``` macro. Using that macro, you can check if a file descriptor is set in the descriptors set. If it is ready, what should we do then?

The ```select``` system call will simply notify us that the server socket is ready for I/O. From the descriptors set, we know it is ready for some sort of read operation. But ```select``` does not do any type of I/O operation. We need to do it. What does it mean when server socket is ready for reading? It means one or more connection requests have come in. Let us go ahead and ```accept``` it. Will this call to ```accept``` block? It should not, because there is already a connection request there.

What do we do once we ```accept``` it? If we just go ahead and call ```serve_connection```, ```recv``` will again block us. We don't want to do that. We will call ```recv``` only when there is data from the client. And how will we know if there will be client-sent data at that socket? ```select``` is supposed to tell us. For ```select``` to tell us, we need to set this new socket descriptor to the ```read_set```. Let us set it.

```c
    FD_SET(client_fd, &read_set);
```

Once this is done, we go back to calling ```select```. If it blocks, then there are no incoming requests for the sockets nor any data to the new connection socket. Suppose a new connection request comes in, what happens?

The ```read_set``` currently has two descriptors. Once ```select``` succeeds due to a new incoming connection request, the ```read_set``` is modified to have just the server socket. This is how ```select``` works. When it returns, only the ready descriptors are set, rest of them are discarded from the set. So now, the fact that ```select``` should monitor the connection socket is lost. How to tackle this? We will need one more data structure to store all the descriptors select should be monitoring. Once it alters the ```read_set```, it needs to be reinitialized. Let us use a boolean array ```fds_list``` to see if a given number is a valid descriptor or not. From ```select```'s manpage, we know that it can only monitor descriptors with value less than ```FD_SETSIZE``` - which is 1024. So, we can have a 1024-element boolean array and maintain the validity of a descriptor.

Once a new socket is created due to ```accept```, we need to record it in our new array. Let us do it.

```c
        // If this comes true, that means we have an incoming connection
        // waiting to be accepted.
        if (FD_ISSET(sock_fd, &read_set))
        {   
            printf("Inside sock_fd if\n");
            ret = accept(sock_fd, (struct sockaddr *)&client_addr, &client_addr_len);
            if (ret < 0)
            {
                printf("accept4() failed\n");
                return -1;
            }
            client_fd = ret;
            printf("client_fd = %d\n", client_fd);

            // We want select to keep an eye on this new socket.
            fds_list[client_fd] = true;
```

Finally, we need to reinitialize the ```read_set``` with all the valid descriptors.

```c
            // When select returns, read_set would be modified
            // to keep just the "ready" descriptors. A couple of them
            // might be lost. Need to update read_set before
            // we pass it to select again.
            for (i = 0; i < FD_SETSIZE; i++)
            {
                if (fds_list[i] == true)
                {
                    FD_SET(i, &read_set);
                }
            }
```

Now, whenever a new socket is created, we request ```select``` to keep an eye on it. Why is it in the ```read_set```? Because for any new socket, we would want to call ```recv``` on it - basically read data. That is why all of them go into the ```read_set```.

Now let us come to the connection-socket case. What happens when a client sends data to the server? If that happens, then we have a socket **ready** for an I/O operation - which is reading data from it. Now that it is ready, we can call ```serve_connection``` on that connection-socket. ```recv``` won't block as well because there is already data waiting to be read.

How would we implement it? When ```select``` returns, we just know that one/more descriptors are ready for reading. We don't know which. We simply have to iterate through all the valid socket descriptors and check if each of them is set in the ```read_set``` by ```select```. If it is set, then we can call ```serve_connection``` on it.

```c
       else // This should cover all the other socket descriptors
        {
            // Should we iterate through our fds_list and check
            // which descriptor is present in the read/write/error sets?
            for (i = 0; i < FD_SETSIZE; i++)
            {   
                printf("Inside for: %d\n", i);
                // Check if this socket exists
                if (fds_list[i] == true)
                {   printf("Inside if\n");
                    // If it is ready to read, go for it.
                    if (FD_ISSET(i, &read_set))
                    {
                        printf("FD: %d\n", i);
                        // Read that data, and send back a response
                        serve_connection(i);
                        close(i);
                        FD_CLR(i, &read_set);
                        fds_list[i] = false;
                    }
                    else
                    {   
                        // If it is not ready to be read
                        // but is a valid descriptor, then
                        // select should monitor it.
                        FD_SET(i, &read_set);
                    }
                    
                }
            }
        }
```

You can find the entire program [here](https://github.com/adwait1-G/Rust-C-Experiments/blob/main/sync-async/server_v4.c). Compile and run it. Make sure it **feels** like the multi-threaded version of the server. Basically, multiple clients can hit the server and the server will still be responsive.

### 2.2 How is it able to manage with a single thread?

This is the first question I had when I wrote the server with select. There were still gaps and doubts about the ```select``` system call, how it is working. I want to discuss about that in detail in this subsection.

In the [second post](/rust/2020/11/09/multithreading-and-multiprocessing.html), we explored questions like these: Suppose the thread is executing code related to one connection conn-1, then suddenly data comes in for another connection conn-2 as well. What is thread supposed to do now? Will it stop executing conn-1 code and go to conn-2? etc., The following is how it works.

1. Block at ```select```. Wait for descriptors to become ready.
    - We are taking kernel's help to deal with the uncertainty.
    - Only when the kernel tells some descriptor is ready for I/O(can be accept, recv etc.,), we go ahead.

2. Suppose only one descriptor gets ready at a time. What happens?
    - This is a straight-forward case. When one descriptor is ready, select returns. We process it. The descriptor could be the server socket descriptor, or a connection socket. We take the corresponding action.

3. Many descriptors get ready at the same time (many clients might send data, many new connection requests can come in). How is this handled?
    - Because there is just one thread, we handle all of them in a serial manner - one after the other.
    - If you look at the code, we are looping around the entire ```fds_list```. We take every ready descriptor, call ```serve_connection``` on it. Because it is a ready descriptor, ```recv``` won't block. Once that is processed, we go to the next ready descriptor. Completely serial in nature.

4. We have called ```serve_connection``` on some socket. When the server thread is running that code, more connection requests come in, some other connection sockets get ready. How is this handled?
    - When the thread is running ```serve_connection``` code for one connection socket, it will just run its course. Once that is done and goes back to calling ```select```, then all the ready descriptors(be it connection sockets/server socket) are served on after the other - in a serial manner.

So when data comes in for conn-2 when the thread is processing conn-1, the thread finishes processing conn-1 and then go to conn-2. There is no magical switch-over that happens.

The following diagram summarizes the whole thing.

```
        ------------------------------
        | Start the server socket    |
        ------------------------------
                     ||
                     \/
        ------------------------------
        | Wait for ready descriptors |--<----
        ------------------------------      |
                     ||                     |
                     \/                     ^
        ------------------------------      |
        | Process all the ready      |      |
        | descriptors one after the  |      |
        | other.                     |      |
        ------------------------------      |    
                     ||                     |
                     \/                     |
                      ----------->-----------
```

Coming back to our question, how is the blocking problem being solved? ```select``` blocks only when there is absolutely nothing to do - when there are no ready descriptors. Even if there is one ready descriptor, it will return and we will process it. If there are lot of descriptors ready, each one of them will be processed one after the other.

So it comes to this: IF you are blocking, then you have nothing to do. Else, you keep looping and processing the I/O events. In this, you won't see anywhere waiting for an I/O event to happen - that is eliminated by ```select``` and its **readiness** concept.

## 3. Is this an Event Loop?

You might have heard of the two words: **Event Loop**. You might have also heard about the very famous NodeJs event loop. I am really fascinated by it.

The meaning of "Event Loop" lies in those two words itself. Does our server loop around indefinitely processing events each time it loops? Yes it does. So what we have here is a simple event loop.

## 4. What next?

In the next couple of posts, we will go through the other two system calls - ```poll``` and ```epoll```, rewriting our server using them. Along with that, there are a lot of buzz words related to topic.

1. Event loop
2. Event-driven programming
3. Synchronous-Asynchronous I/O
4. Non-blocking calls, Non-blocking I/O
5. Callbacks
6. Asynchronous Runtime

We have slowly started exploring (1) and (2). What we did today is actually event-driven programming. Everything revolves around events - waiting for them to happen, notifying that it has happened, processing them.

At the end of this series, we should have clarity on all the 6 listed above.

## 5. Event-driven is quite natural

Because I am used to writing blocking code - the normal do something, wait for it to finish and then continue only after it returns, it took a while to get used to event-driven programming. But now, it feels event-driven is very natural and you will find so many things in your life are event-driven.

We took the example of the door-bell. The door-bell is a event notification mechanism which is specific to events that happen around the home's door - milk, newspaper, amazon package, groceries getting delivered, people who want to enter the home etc., Is this the only type of events present? Not really. There are hundreds of different types of events that happen in the context of a home and various types of event notification mechanisms to notify you of those events. The washing-machine finishing its timer is an event, the siren which goes off at the end of that washing-machine-timer is the corresponding event notification mechanism. You are working, you keep getting messages/mails you need to respond to - the message ring-tone which goes off when you get a message is the corresponding event notification mechanism. The time becoming 6am is an event, the alarm going off at 6am is an event notification mechanism.

Those are examples of event-driven things happening around you. But surprising thing is, you also would have behaved in an event-driven manner. Waking up for that alarm is one example. Suppose you and your friends are going out somewhere. Your friend is picking you up and asks you to wait at some landmark. My reaction would be this: Let me know once you are 10 minutes away from the landmark, I will be there. Here, you don't want to go there and wait. Your friend being 10 minutes away from the landmark is the event. Your friend calls/messages you that he is 10 minutes away - you are being notified of the event here. You then start walking towards that landmark where you had to wait. By the time your friend comes to that landmark, you would have been there (that is the idea). Observing these things has helped me understand the nature of event-driven paradigm better.

## 6. Conclusion

With that, I would like to end this post.

I hope you got an idea of of what exactly the blocking problem is, how select is used to solve it, how it all happens in a single thread, what an event loop is. I really hope the door-bell example or any of those real-life like examples helped you in someway to get the concept.

In the next post, we will explore the [poll](https://man7.org/linux/man-pages/man2/poll.2.html) system call. Let us see how to use it, what facilities it provides and rewrite our server using **poll**.

Is this a complete replacement to multithreading? Which one is better? These are very interesting questions and let us comeback to them once we have a firm grip on basic event-driven concepts.

I learnt a lot while writing this post, hope you did too.

Thank you for reading :-)