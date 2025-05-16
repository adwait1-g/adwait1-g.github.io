---
layout: post
title: Introduction to Network Programming
categories: packetoverflow
comments: true
---
Hello Friend!

In the previous articles([article1](/packet/overflow/2019/02/01/operating-system-and-networking-stack-part1.html) & [article2](/packet/overflow/2019/02/01/operating-system-and-networking-stack-part2.html)), we got a rough picture of what TCP/IP stack is, where it is present, how communication happens between machines. 

In this article, we will see two machines talking to each other live! We will write programs which will make use of the OS's Networking Stack and then talk to each other. If you are a newbie to Computer Networks, I highly recommend you to read through the above mentioned articles because concepts discussed there will be used here to write programs.

Make sure your machine is connected to your network via WiFi or Ethernet.

Let us look at some important concepts which will help us write the programs. 

## 1. Pre-requisites

# a. How do you use any resource offered by the Operating System?

The Operating System offers an **Application Programming Interface(API)** - basically a well-defined set of functions which one can use to write programs. Let us look at a few examples. 

1. Input / Output API: **read**, **write**, **seek** etc., are functions to handle I/O operations. 

2. Process related API: **fork**, **wait**, **waitpid**, the **exec** function family. 

3. Memory handling API: **mmap**, **munmap**, **mprotect** help in mapping files onto memory, removing the mapping, setting permissions. 

Like this, there is an API which helps us use the Networking Stack. That API is specially called **Network API**. This article is about learning a few functions from that API, understand what they do and use them in writing programs. 

# b. What kind of programs do we write?

We will be writing **network** programs - the programs which communicate with each other over a network. 

When you look at the Internet, you would see a lot of machines present just to serve the data you need and you would see machines which have applications like your browsers, apps etc., requesting for that data. This is formally known as the **Server-Client Network Architecture**. This is one of the most popular network architectures and is extensively used in building systems. 

A **Client** is a process / application that requests for some data. The facebook app, google app, youtube app are all clients. 

A **Server** is a process which serves the requested data to clients. 

In this article, we will be writing simple server and client programs which can communicate with each other over the network.

# c. In what language do we write these network programs?

Linux offers an API in C programming language. Writing network programs in C might be daunting at first because there are a lot of details which we have to take care. Because we are new to Computer Networks itself, it will be difficult to make sense of all those details right in the beginning. 

That is why, let us write these programs in **python**. Python offers a beautiful and an amazingly simple Network API, which is straight to the point. It abstracts all those little details. It internally takes care of all those details.

With that, we are done with a general details that you should be aware of before writing network programs. 

Let us get started by discussing about the most fundamental concept in network programming, the **socket**. 

# d. What is a socket?

Before getting into what socket means in network programming, let us think what socket means in general. The one socket we all know is the **electric socket** / **plug point**. It generally has 3 / 5 holes in it and you can insert the plug in. What is this electric socket doing? What is its function?
It is an **endpoint** where you get access to electricity when you insert that plug of your Air cooler(or any electric appliance) and switch it on.

Observe what is happening. The socket is just an endpoint. There is a huge system behind it functioning at full throttle to deliver electricity at that socket. It all starts at the power station where electricity is generated. This has to be efficiently delivered to your home. How is it done? There are multiple transformers which help in stepping up and stepping down the voltage when necessary. There is a huge transmission and distribution network which helps electricity to be delivered to the electric pole which you see next to your home. From there, there is a connection to your home's main switch board. There is a complex wiring done to connect your home's main switch board and the socket. And there it is, you have electricity delivered at your socket. I just explained the whole system in a few lines. But the system is so complex and interesting that my friends in the Electrical department have multiple courses which help them understand the complete system.

The point is, there is a such a big-ass system, but all you see is just a socket embedded to the wall. It is an **end-point** to which electricity is delivered. The socket is successfully hiding (or abstracting) all those details. 

```
---------------------                                                       ---------------------
|                   |                                                       |                   |
|   Power Station   |                                                       |       Home        |
| (generates        |-------------------------------------------------------|                   |
|     electricity)  |  Complex system where transmission happens like magic | <----Socket       |
|                   |-------------------------------------------------------|                   |
|                   |                                                       |                   |
|                   |                                                       |                   |
---------------------                                                       ---------------------
```

Now, let us come back to Computer Networks. The network socket here does the **exact same thing**. It is just an end-point of communication. Look at the following diagram. 

```
---------------------                                                       ---------------------
|                   |                                                       |                   |
|     Machine A     |                                                       |     Machine B     |
|                   |-------------------------------------------------------|                   |
|        Socket 1-->|                   Magic Tunnel                        | <--Socket 2       |
|                   |-------------------------------------------------------|                   |
|                   |                                                       |                   |
|                   |                                                       |                   |
---------------------                                                       ---------------------
```

Notice the important difference between the electric socket and the network socket. 2 network sockets **communicate with each other**. Whereas an electric socket is just a single end point where electricity is delivered. 

Now, let us talk more about that Magic Tunnel in the above diagram. You already know that every machine has a networking stack. But is that enough for those 2 machines A and B to communicate with each other? 

No. There has to be a physical Computer Network present between A and B to talk to each other. If that is not present, how will data travel from A to B right?

That Magic Tunnel is Internet. It is a complex network of several routers, switches, access points etc., which make communication possible. When you browse for something, do you really **feel** that such a complex, heavy system is behind it? It feels so smooth and awesome!

A network socket abstracts everything. A network socket is just a hole into which you pump the data you want to reach the other socket. All the other details like **how** that data travels from A to B **hidden** from plainsight. 

There are 2 analogies between electric sockets and network sockets. 

1. **Types of sockets** 

    * Consider electric sockets. There are generally 2 types of electric socket at home - one for low-power consuming appliances like tubelight, fans, your phone charger etc., and other for high-power consuming appliances like mixer, washing machine, grinder etc., They are designed to support a specific type of appliance. If you plug in your washing machine's plug into a low-power socket, the system might get burnt because washing machines draw huge power, but the low-power sockets and its wiring are not designed to support this. 

    * On the same lines, there are different types of network sockets. If network layer uses IP and transport layer uses TCP, it is a TCP/IP socket. If network layer uses IP and transport layer uses UDP, it is a UDP/IP socket. Depending on the application, you have to choose the appropriate type of socket. At this point, do not worry much about what TCP, UDP, IP are. We will discuss them in detail in the coming articles. 

2. **The Generic design of a socket**

    * Consider that low-power electric socket. You can literally insert **any** low-power consuming appliance into that socket. It can power up light, fan, charger etc., It is designed to support **any** low-power consuming appliance. That is why, it is pretty generic in nature. 

    * Consider the TCP/IP socket. This is the most used type of network socket in the world. It is supporting so many types of application layer protocols like HTTP, FTP, SMTP. The socket is generic in nature.

Look at how amazingly similar they are. 

That was some theory about network socket. I hope you get an idea. 

Because we will be dealing with sockets, Network API is also known as **Socket API**. Network Programming is often refered to as **Socket Programming**.

# e. A small note about TCP/IP stack and sockets

At this point, we have an idea of what sockets are and we also know what TCP/IP stack is. The TCP/IP stack is the following. 

```
-------------------------
|   Application Layer   |
-------------------------   
|    Transport Layer    |
-------------------------
|     Network Layer     |
-------------------------
| Network Access Layer  |
-------------------------
```

The stack looks like above in theory. 

In practice, a programmer who wants to write programs cannot access all the layers directly. As we have seen, we have to use the Network API. The following is a more practical diagram of the stack. 

```
        -------------------------
        |   Application Layer   | <---------------------------- Userspace
------------------------------------------
|             Network  API               | <------------------- Interface connecting Userspace and Kernelspace
------------------------------------------
        |    Transport Layer    |       ----|
        -------------------------           |
        |     Network Layer     |           |<----------------- Kernel Space
        -------------------------           |
        | Network Access Layer  |       ----|
        -------------------------           
```

Analyze the above diagram. When you create a socket, you can specify details like Transport Layer protocol, Network Layer protocol, details related to each of those protocols and so on. These sockets are generic in nature. If you want something specific, then use a socket and write it in the application layer. The Application Layer protocols are like appliances. On a particular electric socket, you can plug in variety of appliances. In the same way, you can write a variety of application layer protocols on top of a network socket.

With that, let us get into Network Programming!!

## 2. Writing a simple server

Let us understand what a server is, what its functions are before writing code for it. 

We defined a server as a program which serves requested data to the client. 

What all should a server do?

1. Listen to incoming connections from various clients. 
2. If there are enough resources, accept that incoming connection - establish connection. Else, reject them.
3. Once connection is established, start serving the client's requests. 

That is what we want. Now, let us start writing code for it in python. 


# a. Modules need to write network programs

The **socket** module in python has all the data structures, functions etc., needed to write network programs. So, let us import it. 

Let us write a python function which will function as a server. 
```python
#!/usr/bin/env python3

import socket
import sys

def server(ServerIPAddress, ServerPortNumber) : 
```

Along with that, let us import the **sys** module too. It has functions to exit the program, it has functions to manage commandline arguments etc.,

# b. Creating a socket

```python
    ListenSocket = socket.socket()
```

The ```socket()``` method of **socket** module returns a socket object. Do not worry about the type of socket and other details. Why do we need a socket? You will know in the coming steps. 

# c. Bind the socket to an (IPAddress, PortNumber) pair. 

How will the client get connected to the server? There should be some type of address to get connected right? That address is the (IPAddress, PortNumber) tuple. Let us use the ```bind()``` method to bind that socket to that tuple. 

```python
    ServerPair = (ServerIPAddress, ServerPortNumber)
    ListenSocket.bind(ServerPair)
```

At this point, you have a socket created. You also know which IP Address and which Port Number to bind the server to. Now, let us get into the crux of the server. 

# d. Making the socket listen to incoming connection requests

We have the socket and we know where the server socket is bound to. Now, let us come to server's first function - it should be capable of listening to incoming connection requests. We can make the socket we have opened to listen. We will use the ```listen()``` method to do it. 

```python
    RequestQueueLength = 1
    ListenSocket.listen(RequestQueueLength)
    print("Server listening at ", ServerPair)
```

Concept is simple. The server can handle one incoming request at a time. Suppose 5 request come at once. What it can do is, it can put all of those request in a queue and process each of them one after the other. ```RequestQueueLength``` is the length of that queue. We can decide that. Here, the queue length is 1. It means, if 2 connection request come at a time, only one is processed. The other is dropped. You can change the queue length to any number you want. 

At this point, the server is listening to incoming connection requests. But what should it do when it encounters a connection request??

# e. Accept the request if enough resources are present

When a connection request comes to the listening socket, either it has to accepted or rejected. The ```accept()``` method takes care of that. 

```python
    ClientHandleSocket, ClientPair = ListenSocket.accept()
    print("Connected to Client at ", ClientPair)
```

The ```accept()``` does something really interesting. Assume that the **ListenSocket** listens to a connection request. It hands over the control to ```accept()``` method. The ```accept()``` method looks at the amount of resources the system has. If it has enough resources, it **accepts** the request and the connection is established. 

If connection is established, ```accept()``` returns two items. 

1. The first item is a **new** socket - **ClientHandleSocket**. This socket is created **just** to handle that one established connection. Where is the client? What is the address of the other end of the connection?

2. It is the **ClientPair** - a tuple of (IPAddress, PortNumber) of the client which made the connection request.

Notice what is happening. There is a socket which is continuously listening for incoming connection requests. As soon as a connection request came in, a new socket is created to handle that new connection. The listening socket **never ever** talks with any of the clients at any cost. Its **only** job is to listen to requests and hand it over to ```accept()``` method. The ```accept()``` method will see what to do with that request. 

At this point, our server is able to accept incoming connection requests. But, what to do after establishing the connection with a client?

# f. Send and Recieve data 

Because this is like a proof-of-concept server, we will keep the interaction between the client and server short. 

In general, once the connection is established, the server waits for client's request. The client sends a request of what data it wants. So, let us use the ```recv()``` method and try recieving the data that is sent by the client. 

```python
    ClientData = ClientHandleSocket.recv(10000)
    ClientData = ClientData.decode('utf-8')
```

Note that we are using the newly created socket here. 

That **10000** is the size of the recieve buffer. The server can atmost recieve 10000 bytes of data from client. You can change it to any size you want. For now, ignore the next statement. 

Once we have received data, we will send some data back to the client. That way, we will know that the client and server have communicated with each other. 

```python
    SendData = "Hey Client! This is the Server. I have successfully recieved your message."
    SendData = bytes(SendData.encode('utf-8'))
    ClientHandleSocket.send(SendData)
```

Remember that you can only send and receive data of the type **bytes**. If you don't convert any data into **bytes** type, you will get an error.

# g. Close the socket

Once the communication with the client is done, close the socket. This is mandatory because to create and operate a socket, the Operating System allocates certain amount of resources to it. Once you know that you won't use that socket anymore, you can close that socket so that all those resources are **freed**(deallocated) and can be used by the OS for something else(probably another socket). 

```python
    ClientHandleSocket.close()
    print("Connection close with client at ", ClientPair)
```

Note that this will **terminate** the connection with that client. The server is still up and running.

If you want to close the server itself, you have to close the listening socket. **The listening socket is the heart of the server**. If it is on, the server is on. If it is closed, the server is dead. Let us kill the server.  

```python
    ListenSocket.close()
    print("Server terminated!")
```

With that, we have our small server ready. You can download the complete server script [here](/assets/PacketOverflow/2019-05-02-introduction-to-network-programming-part1/server.py).

Now, let us write a simple client to complement the server we have written. 

## 3. Writing a simple client

When we defined the server, we saw that it has a few specific functions it has to perform. Similar to that, the client also has a few specific functions. 

What all should a client do?

1. Identify which server to connect to. 
2. Send a connection request to the server. Assuming the connection is established, 
3. Send the request and wait for server's reply. 

Now, we will write code to make it happen. 

# a. The required header code

```python
#!/usr/bin/env python3

import socket
import sys

def client(ServerIPAddress, ServerPortNumber): 
```

# b. Create a socket

Here, there is only one socket - which tries to connect to the server. 

```python
    ClientSocket = socket.socket()
```

# c. Specify the Server's address

The client should clearly know the server's address.

```python
    ServerPair = (ServerIPAddress, ServerPortNumber)
```

# d. Connect to the server

We will use the ```connect()``` method to connect to the server.
```python
    ClientSocket.connect(ServerPair)
    print("Connected to ", ServerPair)
```

You might ask, why didn't we bind the client's socket to a particular (IPAddress, PortNumber) pair. Just think, is there a need to do it?

When you want to google something, you would be concerned about Google Server's IP Address and Port number. Will you ever think about what your IP Address is and what port number the socket is bound to? 

You can bind the socket to a (IPAddress, PortNumber) pair, but it is not a compulsion. The IP Address is decided by the network your machine is connected to. OS **allots** a random port number to the socket. It is infact advantageous to not bind it to a pair. Suppose the port 1234 is bound to some other socket but you are not aware of it. You will get an error if you try binding it. If you leave it to the OS, it will see which port number is free and that will be alloted to the socket. 

# e. Send and recieve data

It is always the client which initiates the connection and sends the data request. The connection initiation was done in the previous step. Now, let us send some data. 

```python
    SendData = str(input("Enter your message to server: "))
    SendData = bytes(SendData.encode('utf-8'))
    ClientSocket.send(SendData)
```
Note that once the server receives the above data, it sends some data back to the client. So, let us receive that data. 

```python
    ServerData = ClientSocket.recv(10000)
    ServerData = ServerData.decode('utf-8')
    print("Server: ", ServerData)
```

With that, we are done with sending and receiving data. 

# f. Closing the socket

This is mandatory. You know why :P
```python
    ClientSocket.close()
    print("Client job done!")
```

With that, we have written our small client. You can download the complete script from [here](/assets/PacketOverflow/2019-05-02-introduction-to-network-programming-part1/client.py). 

## 4. Running our client and server

To run these, open up two terminals. One for client and other for server.

Go through the scripts again before you run it. 

Run the server first. Let it wait for our client to get connected. 

```
# Server Terminal
$ python3 server.py 127.0.0.1 1234
Server listening at  ('127.0.0.1', 1234)
```

The IP Address used here is **127.0.0.1** and Port number is **1234**. 

Now, we know the server is opened at **(127.0.0.1, 1234)**. Let us connect the client to this server. 

```
# Client Terminal
$ python3 client.py 127.0.0.1 1234
Connected to  ('127.0.0.1', 1234)
Enter your message to server:
```

As soon as client gets connected, you will see a message at the server side, saying it is connected to a client at an addres. 
```
# Server Terminal
$ python3 server.py 127.0.0.1 1234
Server listening at  ('127.0.0.1', 1234)
Connected to client at  ('127.0.0.1', 48378)
```

Observer that port number **48378** - It is the port number the client socket is bound to. It is a port alloted by the OS to that socket. 

Now, client is asking you to type in some message. Go ahead and type in something. 
```
# Client Terminal
$ python3 client.py 127.0.0.1 1234
Connected to  ('127.0.0.1', 1234)
Enter your message to server: Hey Server! This is the client. Very nice to talk to you over a network!
```

As you press an enter, observe the server terminal. 
```
# Server Terminal
$ python3 server.py 127.0.0.1 1234
Server listening at  ('127.0.0.1', 1234)
Connected to client at  ('127.0.0.1', 48378)
Client:  Hey Server! This is the client. Very nice to talk to you over a network!
Data sent back to client
Connection closed with client at  ('127.0.0.1', 48378)
Server terminated!
$
```

The server has received the client's message. It has also sent back a message back to the client. 

Let us look at the client terminal. 

```
# Client Terminal
$ python3 client.py 127.0.0.1 1234
Connected to  ('127.0.0.1', 1234)
Enter your message to server: Hey Server! This is the client. Very nice to talk to you over a network!
Server:  Hey Client! This is the Server. I have successfully recieved your message.
Client job done!
$
```
Client has received the server's message. 

With that, we are done writing our tiny client and server. 

## 5. A few interesting things

# a. Speciality of the listen method

The basic functionality of any server is to listen for incoming connection requests. A socket can be converted into a listening socket by executing the ```listen()``` method. There is an important concept here. 

A listening socket never communicates with any of the clients. Its only job is to receive a connection request and hand it over to the ```accept()``` method. 

A socket which never talks to other sockets is called a **Passive Socket**. A socket which talks to other sockets is called an **Active Socket**. The ```listen()``` method decides whether the socket is going to be a passive or an active socket. Once the ```listen()``` method is executed on a socket, it can **never** talk to other sockets - so that socket becomes a passive socket. You cannot execute ```send()```, ```recv()``` and other methods on a passive socket. The ```listen()``` decides the fate of a socket :P

# b. Writing better servers

What we wrote is a tiny server capable of handling just one client. In reality, a server should be capable of handling multiple clients simultaneously. If you are interested, you can make use of **multithreading**, **multiprocessing** python modules to write better servers.

# c. Which type of sockets did we use?

We never really thought what type of sockets to use while writing both client and server. In the beginning, we saw that there are TCP/IP sockets, UDP/IP sockets etc., but we did not mention the use of a particular type of socket explicitly. The whole point of this article was to introduce you to the concept of socket, socket creation and handling functions without getting into too much of specifics. Python helped in abstracting all those details. Do not worry about the type of socket we used. As we move ahead in the series, you will know what socket we used. 

# d. What is 127.0.0.1 ?

You can checkout your machine's IP Address using the **ifconfig** command on Linux. If you are using Windows, you can run the **ipconfig** command. 

```
$ ifconfig

enp2s0    Link encap:Ethernet  HWaddr 44:a8:42:f9:91:2f  
          UP BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)

lo        Link encap:Local Loopback  
          inet addr:127.0.0.1  Mask:255.0.0.0
          inet6 addr: ::1/128 Scope:Host
          UP LOOPBACK RUNNING  MTU:65536  Metric:1
          RX packets:8760 errors:0 dropped:0 overruns:0 frame:0
          TX packets:8760 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:2568412 (2.5 MB)  TX bytes:2568412 (2.5 MB)

wlp3s0    Link encap:Ethernet  HWaddr 48:45:20:44:00:9d  
          inet addr:192.168.0.106  Bcast:192.168.0.255  Mask:255.255.255.0
          inet6 addr: fe80::541:8ce0:9435:b5c5/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:26380 errors:0 dropped:0 overruns:0 frame:0
          TX packets:12194 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:29942126 (29.9 MB)  TX bytes:2020066 (2.0 MB)

```

I am currently using my home's WiFi network. So, my IP Address is **192.168.0.106** - the IP Address under the interface name **wlp3s0**.

Instead of using this IP Address, I used this wierd looking IP Address **127.0.0.1**. What is this IP Address?

It is called the **Loopback IP Address**. Look at the above output. We used the **lo** interface. 

Normally, all the Network interfaces are hardware - Network Interface Cards. These are real network hardware which help your machine get connected to a network. This Loopback Interface is a **software** interface. it doesn't connect to the internet. It is an interface designed for testing purposes. 

For more details about loopback interface, you can read [this  stackoverflow answer](https://askubuntu.com/questions/247625/what-is-the-loopback-device-and-how-do-i-use-it). 

## 6. Conclusion

We have come to the end of this article. I hope you learnt how to write small network programs. Network Programming is a tool we will be using in future articles in understanding Network protocols better. You can visit [this repository](https://github.com/adwait1-G/How-does-the-Internet-work) where I have discussed in short how the Internet works. 

With this article, we are done with 2 out of 3 pre-requisites. We have a basic idea of the networking stack and we are able to write small network programs. In the next article, we will look an amazing network tool called [Wireshark](https://www.wireshark.org/). It is used to capture packets, dissect them and read its contents and more. 

That is it for now. 

Thank you for reading and happy networking :)

--------------------------------------------------------------------
[Go to next article: Introduction to Wireshark](/packet overflow!/2019/09/08/introduction-to-wireshark.html)                   
[Go to previous article: Operating System and Networking Stack - Part2](/packet/overflow/2019/02/01/operating-system-and-networking-stack-part2.html)     
