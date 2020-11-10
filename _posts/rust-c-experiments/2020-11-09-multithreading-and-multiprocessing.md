---
title: Multithreading and multiprocessing
categories: Rust
comments: true
layout: post
---

In the [previous post](/rust/2020/11/08/what-does-blocking-mean.html), we explored what blocking I/O is and also encountered this problem: Can we serve multiple connections at the same time?

## 1. The problem

Let us go over the problem once again. We wrote a very simple [TCP server](https://github.com/adwait1-G/Rust-C-Experiments/blob/main/sync-async/server_v1.c) in the last post where it has the following code.

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

It is quite easy to figure out what is going on here. Once ```accept()``` returns with the new socket descriptor, the ```serve_connection()``` function is called. It serves that connection. **Only** after that connection is done, we go back to ```accept()```. If there are already new connection requests queued up (there is a listen queue of 50), ```accept()``` returns immediately. But again only that connection is served. Even if there are other connections in the queue. Because we have a finite sized listen queue, we might miss out on many connection requests.

Can we do anything about this? Can we somehow be fair to all these connections? Serve all these connections? That is the problem we will be exploring.

## 2. Multiprocessing

One way to solve this problem is to use a **new process** to handle a new connection. When ```accept()``` returns, we will create a new process and let it handle this connection.

How exactly are we going to spawn a new process? Using the [fork()](https://www.man7.org/linux/man-pages/man2/fork.2.html) system call. Its a very straight-forward system call.

In fact, the changes are very minimal to achieve our goal.

```c
        // Wait till we get a connection request
        ret = accept(sock_fd, (struct sockaddr *)&client_addr, &client_addr_len);
        if (ret < 0)
        {
            printf("accept() failed\n");
            return -1;
        }
        client_fd = ret;

        // Handle the request
        
        // Create a new process here.
        // Call the serve_connection only in the child.
        pid = fork();
        if (pid == 0) /* Child process */
        {
            serve_connection(client_fd);
        }

        printf("Serving request for client no %d using process %d\n", i, pid);
        i += 1;
    }
```

You make a call to ```fork()```. While calling it, there is just one process. But its speciality is that it returns in two different process - the caller(or parent process) and the newly forked child process. It returns 0 in the child process and the child's processID in the parent process.

One thing to understand is that when a ```fork()``` happens, all resources between the parent and the child process are shared. Child has access to the server socket and the parent socket has access to the new socket returned by ```accept```. Both processes have access to all resources. It is our responsibility to clean up the resources that we don't want. The parent process doesn't need to keep the socket opened by ```accept()``` open - so close it. In the same way, the child process doesn't need to keep the server socket open. Let us add this code.

```c
        // Handle the request
        
        // Create a new process here.
        // Call the serve_connection only in the child.
        pid = fork();
        if (pid == 0) /* Child process */
        {   
            // Close the server socket in the child.
            close(sock_fd);

            // Serve the connection.
            serve_connection(client_fd);

            // Close the client socket once done.
            close(client_fd);

            // Child process's job is done. Kill it!
            exit(0);
        }
        else
        {
            // Close the new socket returned by accept()
            close (client_fd);
        }

        printf("Serving request for client no %d using process %d\n", i, pid);
        i += 1;
    }
```

We are clear on what we need to do. Call ```serve_connection()``` only in the child process, thus the condition which checks ```pid == 0```. In the parent process, let us just log the child process's PID and the client number.

With the above code, what happens when ```serve_connection()``` returns in the child process? It also tries to call ```accept()```. But the server socket ```sock_fd``` belongs to the parent. That might lead to undefined behavior. Let us close the client socket descriptor in ```serve_connection``` and kill the process. The entire program is present [here](https://github.com/adwait1-G/Rust-C-Experiments/blob/main/sync-async/server_v2.c).

Compile it and run it.

```
Rust-C-Experiments/sync-async$ ./a.out 127.0.0.1 4200
Listening at (127.0.0.1, 4200)
Serving request for client no 0 using process 32049
6: adwaith

Serving request for client no 1 using process 32051
Serving request for client no 2 using process 32078
Serving request for client no 3 using process 32089
```

The above shows that one connection is served. Later, 3 connection requests come in together and then they are served by three different processes.

This way, our problem of serving multiple connections at the same time is solved.

## 2. Multithreading

Instead of spawning new processes, we can also use threads to solve this problem.

Let us use the standard [pthreads](https://man7.org/linux/man-pages/man7/pthreads.7.html) for this task.

The following is the pseudo-code.

1. Block at accept()
1. accept() returns with a new socket descriptor.
2. Create a new thread P, it needs to execute the ```serve_connection()``` function.
    - Once it is done, it can be killed.

Lets see how to create a new pthread. The [pthread_create](https://man7.org/linux/man-pages/man3/pthread_create.3.html) manpage is pretty detailed. It also has an example of how to create a new pthread using ```pthread_create()```.

I gathered the following from the manpage.

1. Initialize pthread creation attributes - ```pthread_attr_init()```.
2. Create as many threads you wan't using ```pthread_create()```
3. How do we destroy them? We have the following options.
    - It calls pthread_exit(3), specifying an exit status value that is available to another thread in the same process that calls pthread_join(3).
    - It returns from start_routine().  This is equivalent to calling pthread_exit(3) with the value supplied in the return statement.
    - It is canceled (see pthread_cancel(3)).
    - Any of the threads in the process calls exit(3), or the main thread performs a return from main().  This causes the termination of all threads in the process.

For us, the first or second options is suitable. Once a thread is done serving a connection, let is get destroyed.

We will be using the same pthread creation attributes for all the threads we create/spawn. So, that needs to be called before we enter the infinite loop.

```c
    // Initialize the pthread creation attributes
    ret = pthread_attr_init(&attr);
    if (ret != 0)
    {
        printf("pthread_attr_init() failed\n");
        return -1;
    }
```

Once that is done, we just need to spawn the thread using ```pthread_create```.

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

        ret = pthread_create(&tinfo, &attr, serve_connection, &client_fd);
    }
```

```tinfo``` is a locally defined ```pthread_t``` object. We then pass the attributes, the function and finally the argument. To make it generic, a ```void *``` needs to be passed. In the thread, we can typecast it back to the structure we want. In our case, it is simply an integer - a socket descriptor. We pass a reference to it.

All good right? Is it really?

If you have programmed in Rust or have some experience writing C, you might have already identified the issue here.

There is one object, two threads are racing for it. Can you identify the object and the two threads? Its the ```client_fd``` variable. We pass a reference to ```client_fd``` to ```serve_connection``` which is a whole other thread. It will be peacefully using ```client_fd``` for ```recv()```, ```send()``` etc., Suddenly, in the server's main thread, the ```accept``` returns and executes the ```client_fd = ret``` and now that thread has lost its socket descriptor forever.

Given an object, there can be multiple readers and no writers OR one writer and no one else.

What should we do? Idea is that the new socket belongs to the new thread and the server's main thread has nothing to do with it. So, ```client_fd``` has to be moved or its ownership needs to be passed to the new thread. ```client_fd``` is a stack object and by definition belongs to the server's main thread. What can be done?

We can just make a copy of ```client_fd``` on heap and pass it to the new thread. We know that the new thread owns it. So, it is the new thread's responsibility to clean it up. Let us see how this code looks like.

```c
client_fd = ret;

        // Create a thread here.
        // Make a copy of the client_fd.
        arg_client_fd = calloc(1, sizeof(int));
        if (arg_client_fd == NULL)
        {
            printf("calloc() failed\n");
            return -1;
        }

        *arg_client_fd = client_fd;
        ret = pthread_create(&tinfo, &attr, serve_connection, arg_client_fd);
```

Obviously, the ```serve_connection()``` has to be changed. It needs to abide by the prototype of a pthread's start_routine. The prototype is the following.

```c
 void *(*start_routine) (void *)
```

It needs to return a ```void *``` and take in a ```void *```. Make the corresponding changes in the ```serve_connection()``` definition. Also make sure to close the socket and free the heap memory of ```arg_client_fd```. Both of them were **moved** into this new thread and thus the new thread has to take care of them.

You can find the full listing of this version [here](https://github.com/adwait1-G/Rust-C-Experiments/blob/main/sync-async/server_v3.c).

Let us compile and run it.

```
Rust-C-Experiments/sync-async$ gcc server_v3.c -pthread
Rust-C-Experiments/sync-async$ ./a.out 127.0.0.1 4200
Listening at (127.0.0.1, 4200)
```

Now start bombarding it with connections. You should see that it behaves very similar to the fork-version of the server.

```
Rust-C-Experiments/sync-async$ ./a.out 127.0.0.1 4200
Listening at (127.0.0.1, 4200)
Serving client with fd: 6 using thread with tid = 1614, pid = 1605
6: woiefoweihf

Serving client with fd: 7 using thread with tid = 1616, pid = 1605
Serving client with fd: 6 using thread with tid = 1638, pid = 1605
Serving client with fd: 8 using thread with tid = 1649, pid = 1605
```

I also wrote a small function to retrieve the Thread-ID. Refer to the full listing of the program and make use of it if you want.

I hope you understood why we wrote the fork-version before the pthread-version. The pthread-version is a bit more complex - issues creeping in if we are not vigilant.

## 4. What did we achieve?

So what did we actually accomplish in the last two sections?

We had a problem with us: Can we serve multiple connections at the same time?

We wanted some way to implement a solution and we did it here. We have two versions - fork and pthread version.

What did we not do?

We didn't go deep into the fork() system call or pthreads. This post is not intended to be a tutorial and hence just skimmed through it.

Which version is better? fork or pthread version? Does spawning and killing processes/threads like that take a toll on performance? Let us explore these questions in a separate post.

## 5. What remains now?

If you closely observe each new process/thread which deals with a single connection, how does it behave? It actually behaves like the original server we wrote - one which serves one connection at a time.

We are happy because the server's main thread is not **blocked** by any connection, but that doesn't mean we have solved the blocking problem. Another thread/process is suffering through the blocking issue. In each of these processes/threads, the I/O calls are still blocking. The process/thread still waits for these calls, doing nothing, wasting precious time.

Is there anything we can do about it? Because simple multiprocessing/multithreading in our case is certainly not the most efficient solution.

Lets take an example. Consider a server state where there are 100 active connections and thus there are 100 threads. Each thread does some work, calls some I/O system call, waits, goes ahead to do some more work. Work might mean anything. It might mean processing the request, crafting an appropriate response - basically CPU intensive work. Assume that if serving a connection takes a total of 100ms, say 50ms of it is spend in I/O - basically waiting for it to get over. Each thread does 50ms of CPU work and 50ms of I/O waiting.

We know that the thread does absolutely nothing during those 50ms of I/O. So, can you think of any scheme of using lesser number of threads to do the same amount of work? By work I always mean running code on the CPU. 

Consider the following. A connection conn-1 comes in. A thread is spawned and it starts serving that connection. Does some work and eventually makes an I/O call. Now, it is doing nothing. When it is doing nothing, a new connection conn-2 comes to the server. What do we conventionally do? We spawn a new thread and let it serve the new connection. But is that necessary? Can we do something else? Anyway there is a thread simply doing nothing there. Why can't it just take up conn-2?

There is one thread. You work here when you have to wait there, you work there when you have to wait here. But how exactly are we going to make it happen? What if there is work in both places? When there is no work in both places, the thread can sleep :P

This will raise a lot of questions. How exactly can we make that thread serve conn-2? We conventionally used ```pthread_create()``` as the starting point. But now, that thread is in the middle of a function call(the I/O call), waiting for it. How can we pull it out of it and simply force it to execute some new function? Is this really possible?

Suppose some technique exists to magically pull a thread from there to here and it can serve this new connection? Remember that serving a new connection is simply calling a new function call ```serve_connection()```. When it is running some code in ```serve_connection()```, what if conn-1's I/O is done? What is this thread going to do? Will it just abandon conn-2's code and go back to doing conn-1's work? Before all of that, how will the thread even know conn-1's I/O is complete to go there?

If we have answers for all these questions, we can use one thread to serve two connections. Obviously the next question is this: Why not more than two connections?

What are we trying to do here? We are simply trying to do some useful work instead of waiting for some I/O to finish, that is all. And see how quickly it got complex.

## 6. Conclusion

With that, I would like to conclude this post.

We solved one problem, but a more interesting and challenging problem lies in front of us: Can we use lesser number of threads to do the same amount of work? Can we somehow make a thread do useful work while some I/O is happening elsewhere which it cares about?

We will be exploring this problem in detail in rest of the blog posts.

That is for now.

Thanks for reading :-)