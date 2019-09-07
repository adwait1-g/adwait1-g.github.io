---
layout: post
title: Operating System and Networking Stack - Part2
categories: Packet Overflow
comments: true
---

Hello friend!

In the [previous article](/packet/overflow/2019/02/01/operating-system-and-networking-stack-part1.html), we discussed basics of Computer Networks, Ethernet, Physical Layer and Data-Link Layer. 

## Overview

In the previous article, this is the problem we were trying to solve: 

There are 100 networks. Each network is a switch along with a few devices connected to it. Machine A is present in Network1. Machine B is present in Network100. All networks are isolated - they are not connected to one another by any means. Machine A wants to send a file to B. How can we make this possible?

This is the model we were discussing: 

                    ---------------
                    |   Magic     |
                    |   Device    |
                    ---------------
                     |  ......  |
                     |          |
                     |          |
                     |          |
                  SwitchN1   SwitchN100
                  | | | |    | | | |
                  | | | |    | | | |
                  A Q W E    B S D F


There is some device all the 100 switches are connected to. A sends a frame to SwitchN1. SwitchN1 sends that frame to the Magic Device. That device, without sending the frame to every other switch, it sends the frame to the Switch to which B is connected. So, no energy wasted. Also, because of that, we can connect say 1000 such networks to that magic device(assuming it has those many number of physical ports). 

Is such a technology possible? Can such a device be designed?

Yes. The Internet today is powered by that Technology. 

So, in this article, we will be talking about this technology, understanding it better. 

## TCP / IP Suite!

What we need here is a system to connect these different individual networks with each other. So, we need to build a bigger network where each of the smaller networks is connected to each other. So, what we need is an **Internetwork** or a **Network of Networks**. 

**Vinton G Cerf**([wiki](https://en.wikipedia.org/wiki/Vint_Cerf)) and **Bob Kahn**([wiki](https://en.wikipedia.org/wiki/Bob_Kahn)) came up with a complete **protocol suite** or a **Networking Stack** for end to end communication. 

This protocol suite became popular as the **TCP / IP protocol suite**. The suite is the backbone of today's Internet. That is why, Vinton G Cerf and Bob Kahn are regarded as **Fathers of the Internet**. 

So, we will be discussing about this protocol suite in this article. 

The **TCP / IP Networking Stack** has 4 Layers: 

            |-------------------------------|
            |       Application Layer       |
            |-------------------------------|
            |        Transport Layer        |
            |-------------------------------|
            |         Network Layer         |
            |-------------------------------|
            |     Network Access Layer      |         
            |-------------------------------|

The **Network Access Layer** is actually the Physical Layer and  Data-Link Layer combined together. From now on, I will be refering to these 2 layers collectively as Network Access Layer. 

Other 3 layers - Network Layer, Transport Layer and Application Layer are 3 new layers.

Lets get right into it!

## Network Layer

At the Data-Link Layer, we saw how protocols help in connecting machines inside a network. In a similar manner, Network Layer protocols describe how networks can be connected, how a machine in one network can talk to a machine in a different network. 

The most successful Network Layer protocol is the **Internet Protocol(IP)** and is the IP in the TCP / IP suite. From now on, by default the Network Layer protocol used in this article is IP.

The current version of IP which is dominating the world is IP Version 4(**IPv4**). So, we will talk about IPv4. You will see why this is called IP Version 4 later in the article.

### IP Addresses

I am sure everyone of you would have heard of IP Addresses. It is a **Unique Address** given to a particular machine at the Network Layer. The way machines are identified by their Physical Addresses at Network Access Layer, they are identified by IP Addresses at Network Layer. 

As soon as a machine gets connected to the Network, the machine gets a **4-byte IP Address**. For our convinience, we represent the IP Address like this: **A.B.C.D**. A, B, C and D are all single bytes. This notation is known as **Dot Notation**. A few examples are 10.12.34.88, 0.0.0.0, 127.0.0.1, 192.168.0.2 etc.,

Let us take an example to see how IP helps in connecting multiple networks. 

Consider a network with 254 devices in it and all of them are connected to the switch. Consider 10 such networks. So, one such network looks like this: 

        |-----------|
        |  Switch1  |
        |-----------|
          | ......|
          D1     D254 


There are 10 such networks. 

Let us connect each of those 10 switches to another networking device R. R is a Router, a Network Layer Device. It helps in connecting machines from 2 different networks. The way a Switch works on Physical Addresses, a **Router works on IP Addresses**. The Router will see Source and Destination IP Addresses. 

            |-----------|
            |  Router   |
            |-----------|
              | ....  |
              S1      S10
              |
        -------------
        |  ......   |
        D1          D254

In the above diagram, only S1's network is shown. But all switches have their respective networks. 

Every device is assigned an IP Address. Say, they are assigned IP Addresses in the following manner. 

    Switch1
    -------

    D1 -    192.168.1.1
    D2 -    192.168.1.2
    D3 -    192.168.1.3
    .
    .
    D254 -  192.168.1.254

    
    Switch2
    -------

    D1 -    192.168.2.1
    D2 -    192.168.2.2
    D3 -    192.168.2.3
    .
    .
    .
    D254 -  192.168.2.254

    .
    .
    .
    .

    Switch10
    --------

    D1 -    192.168.10.1
    D2 -    192.168.10.2
    .
    .
    .
    D254 -  192.168.10.254

Note that when a device is connected at Network Layer(IP here), an NIC will have 2 identifiers - Physical Address at the Network Access Layer and IP Address at the Network Layer. 

Now, we can have a 2 situations here: 

1. If Source and Destination machines are in the same network. Eg: Source = S1-D1, Destination = S1-D99. 
2. If Source and Destination machines are in different networks. Eg: Source = S1-D1, Destination = S8-D123. 

Source just knows Destination's IP Address. Source does not know if Destination belongs to the same network it belongs to or a different network. 

In first case, the data doesn't have to go to the Router because both Source and Destination are in the same network. In second case, you must take the help of Network Layer because the 2 machines belong to different network. 

How exactly this is resolved is something we will see in the coming articles, where we deep dive into different protocols used to handle these situations. 

This is just one small example we took of network of networks and tried to understand how stuff happens. But, the real power of Router is not actually demonstrated here. It is a lot more powerful. Here, we had 10 small networks connected to a Router to make 1 big network. The world is full of such **big** networks and those networks can be in any part of the world. They all could be spread out in entirely different locations of the world. But, IP will be able to connect any 2 devices. That is something really powerful isn't it? 

When we are talking about 1 big network and how communication happens inside it, we have to talk about Network Access Layer also. Because the communication in the smaller networks don't need the Network Layer. But when we are talking about connecting those big networks, discussion mostly happens at the Network Layer because it is all about connecting multiple big networks. Here, we spoke about how 1 Router enables communication inside a big network. For multiple big networks to talk to each other, Routers talk to each other, they run different protocols and make it happen. 

We discussed that Network Layer(IP) is capable of transferring data across networks. So, have we obtained our ideal networking system? The answer is Yes, but with a few points to think on.

The first and most important problem is that, IP is **unreliable**. It provides what is known as **Best Effort Service**. What this means, when a Source pushes a packet into the Network Layer, IP doesn't gaurantee 100% that the packet will reach the destination. IP will just tell "I will try my level best, but I cannot give you a gaurantee". 

That feels totally irresponsible of it :P, but that is how it is able to scale up to the whole world. IP is able to connect the whole world, but it is coming at a cost. At the same time, it comes with a lot of amazing features which makes the Internet so robust and fault tolerant!

## Transport Layer

IP connects any 2 devices in any parts of the world. But that is actually still not enough. We need a finer control. Consider 2 machines A and B. A is a google server and machine B is your phone. Consider the following situations. 

* You open a browser on your phone. You will search for some data. That search query will go to A and A will send back the search results. You use IP Addresses for communication - pretty straightforward. 

* At the same time, You open your facebook app. You request for some data. Facebook server serves that data back to you. Even this communication happens through IP Addresses. 

There is a problem here. Consider a data packet coming from google server. It has Source as server's IP Address, Destination as your phone's IP Address. It comes to the Network Layer. But here, you have 2 processes running - one the browser and other is the facebook app. Where should the packet go? You and I know that the packet should go to the browser. But, how will your mobile phone know??

From this, we can conclude that it is not enough if we use IP Addresses and packet arrive at the device. The device has multiple processes(like browser, facebook app) running simultaneously. There should be a method for the device to decide to which the packet belongs to after it arrives. 

This is where Transport Layer comes in. It enables this **process to process** communication. So, the device knows to which process the packet belongs to. 

How did we distinguish between devices at the Network Access Layer? By using Physical Addresses - which are bunch of unique numbers. 

How did we distinguish between devices at the Network Layer? By using IP Addresses - again a bunch of unique numbers. 

Here, we have to distinguish between different processes connected to the network. This problem can be solved in the exact same way. Assign unique numbers to them. 

Here comes the concept of **ports** at the Transport Layer. A port is just a software entity to which a process using a network can bind to. It is not a physical port like the Ethernet port. It is just a method to distinguish between different processing using the internet. 

There are 2^16 = **65536** ports in a machine as of now. This means, in a single device, there can be a maximum of 65536 processes getting connected to the internet. 

The ports are numbered from 0 - 65535. 

Now, let us go back to our problem and see if it can be solved using ports. 

Suppose the browser is bound to port 12345. The Facebook app to port 23456. The packet is in the Network Layer. Now what should the Network Layer do? It can push the packet to the Transport Layer. 

We have bound the processes with ports. But in the packet, there is no such information about which port(or process) the packet belongs to. So, the confusion still remains. 

What can be done is add both Source and Destination Ports to the packet. So, now the packet would look something like this. 


    -----------------------------------------------------------------------------------------------------     
    |   Data    | Source Port   |   Destination Port |  Source IP Address   |   Destination IP Address  |    
    -----------------------------------------------------------------------------------------------------    

When the browser sends the request, Transport Layer binds the browser with a port, puts the source port(browser's port) and destination port(port to which server is connected on that server machine) into the packet. 

This way, the server would know which port the browser is bound to. So, when sending a packet back to the browser, it knows that the Destination Port is port to which browser is bound. 

In this manner, the problem is solved. 

Note that that one port can be bound to only one process. The port-process pair is unique. If it is not, the whole purpose of ports is defeated.

The basic functionality of Transport Layer is **process to process** communication.It goes beyond just delivering the packet to the device. It has to be delivered to the correct process. 

Similar to other layers, Transport Layer has a few protocols. The 2 most famous protocols are **TCP(Transmission Control Protocol)** and **UDP(User Datagram Protocol)**. 

TCP is built to be a reliable protocol because the underlying Internet Protocol is unreliable. TCP is the **most** used Transport Layer protocol at the moment. 

UDP is an unreliable protocol. But, it is used a lot of places. We will see that. 

Each of these protocols is meant for a specific purpose. It is mandatory for Transport Layer protocols to ensure Process to Process communication. Any other feature they add is their choice. 

At this point, I want to discuss about the name **TCP / IP Networking Stack**. The name is because IP is used at the Network Layer and TCP at the Transport Layer Protocol. They literally drives the complete Internet.

We will be discussing about each of these protocols in detail in future articles. 

Let us move onto the final layer. 

## Application Layer

The Application Layer is where you write applications. The whole **World Wide Web** runs in the Application Layer. Anything you access on your browser is the application Layer. 

You would have noticed **http**, **https** on your browser when you visit a website. **http** is an Application Layer protocol. There are multiple application layer protocols like **ftp(File Transport Protocol)**, **SMTP(Simple Mail Transfer Protocol)**. 

We will be discussing few of these protocols in the future. 

## Consolidation!

The **TCP / IP Networking Stack** has 4 Layers: 

            |-------------------------------|
            |       Application Layer       |
            |-------------------------------|
            |        Transport Layer        |
            |-------------------------------|
            |         Network Layer         |
            |-------------------------------|
            |     Network Access Layer      |         
            |-------------------------------|

It is important to see how we have added stuff at each layer along with data to make the Stack function properly. Let us have a look at it. 

                                                    ---------------------
                                                    |       Data        |
                                                    ---------------------
            |-------------------------------|       ------------------------------------------------
            |       Application Layer       |       |       Data        | Application Layer Header |
            |-------------------------------|       ------------------------------------------------

            |-------------------------------|       -------------------------------------------------------------------------
            |        Transport Layer        |       |       Data        | Application Layer Header | Transport Layer Header |
            |-------------------------------|       -------------------------------------------------------------------------
            
            |-------------------------------|       -------------------------------------------------------------------------------------------------
            |         Network Layer         |       |       Data        | Application Layer Header | Transport Layer Header | Network Layer Header  |
            |-------------------------------|       -------------------------------------------------------------------------------------------------
            
            |-------------------------------|       -------------------------------------------------------------------------------------------------------------------------------       
            |     Network Access Layer      |       |       Data        | Application Layer Header | Transport Layer Header | Network Layer Header  | Network Access Layer Header |        
            |-------------------------------|       -------------------------------------------------------------------------------------------------------------------------------        


There is just data in the beginning. The Application Layer adds a Header of it's own. 

Then that is passed to Transport Layer. The Transport Layer adds it's header. Note that Port Numbers are compulsory because it is the Transport Layer's job to ensure Process to Process communication. Anything else depends on the protocol. 

Then that is passed to Network Layer. It adds it's header. We will mostly talk about IP. So, we can say the it adds the IP Header. The IP Addresses are compulsory. Because that is the way 2 devices can talk to each other. The result of adding the IP Header is known as a **Packet**. 

Then the Packet is passed to the Network Access Layer. Here, we will mostly talk about Ethernet. So, it adds it's the Ethernet Header. The Physical Addresses are compulsory. The result of this process is a **Frame**. Packet + Ethernet Header = Frame. 


## An example

At this point, we have covered some fundamentals and I hope you have got some idea about the Networking Stack, different Layers, what they do, what specific problem each Layer solve. 

Now, we will take a proper example and use whatever we have discussed before and see how communication happens end to end. 

Let us consider a client(like your browser) and a server(like a web server) on the other hand serving data. Suppose the client is in Location A and server is in Location B. A wants to request some data from B. So, A wants to send a request packet. 

1. Note that all the data, requests etc., come at the Application Layer. The layers below it don't know about what that data is, what application layer protocol is being used etc., Suppose client wants a resource named **Resource1234**, the application layer would do the following: 

        -------------------------------------------------            
        |   Resource Name: Resource1234 | Type: Request |              
        -------------------------------------------------              

2. This is then sent to the Transport Layer. The Transport Layer adds it's header. Let us consider the most basic functionality of Transport Layer - Process to Process Communication. So, Transport Layer adds the Source and Destination Ports. The Source Port is the port client is bound to in client nachine. Destination Port is the port to which server is bound to in the server machine.

        ------------------------------------------------------------------------------             
        |   Resource Name: Resource1234 | Type: Request |   ClientPort  | ServerPort |              
        ------------------------------------------------------------------------------               

3. Now, this is sent to Network Layer. We are talking about IP. So, it will add Source and Destination IP Addresses. Here, Source IP Address is IP Address of Client machine. Destination IP Address is IP Address of server(final destination). 

        --------------------------------------------------------------------------------------------------------------------------                  
        |   Resource Name: Resource1234 | Type: Request |   ClientPort  | ServerPort | Client IP Address   |  Server IP Address  |                  
        --------------------------------------------------------------------------------------------------------------------------                   

4. Network Access Layer adds it's header. 

    * There is a very important point I want to discuss here. Here, the Source Physical Address will be client Physical Address. 

    * But, Destination Physical Address is **not** Physical Address of the server. You don't know server's Physical Address. Even if you know, there is nothing we can do because Physical Addresses are useful only for communication inside a network. If there has be a inter-network communication, Physical Address cannot be used. 

    * Destination Physical Address is the Physical Address of the **nearest Router**. As the Router and client machine are in the same network, there are protocols which help the client find out the Physical Address of the Router. 

    * This is a very important point to remember.

            -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------                   
            |   Resource Name: Resource1234 | Type: Request |   ClientPort  | ClientPort | Client IP Address   |   Server IP Address  | Source Physical Address | Destination Physical Address|                
            -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------                     

    * The frame is essentially this: 

            ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------                  
            |   Resource Name: Resource1234 | Type: Request |   ClientPort  | ClientPort | Client IP Address   |   Server IP Address  | Client's Physical Address | Nearest Router's Physical Address|                 
            ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------                   



5. Now, this is transmitted to the nearest Router using Network Access Layer(Because client and Router are in the same network). 

6. Now, the Router gets the Frame. 

    * The first thing it does is remove the Network Access Layer's Header, because it is not longer valid. 

    * The whole internet is a large number of Routers interconnected with each other. So, if this packet has to go to the server, it has to pass through multiple intermediate routers and then finally reach the router to which the server is connected. 

    * So, this Router is connected to multiple routers. It chooses the next router such that the packet follows the **shortest path** from here to the server. Afterall, we need the packet to reach really fast. 

    * The router chooses the next router based on that criteria. 

    * It passes the packet to it's Network Access Layer. 

    * Router's Network Access Layer add the header. Source Physical Address is this Router's Physical Address. Destination Physical Address is the next Router's Physical Address. 

    * And sends the frame to the next Router using Network Access Layer. 

    * How was this possible? These 2 routers belong to a network. As they both belong to the same network, they used Network Access Layer for communication. 

7. The 2nd Router gets the frame. 

    * The same process happens. It removes the Network Access Layer's Header. Finds the next best router. And sends it. 


8. Finally, the packet has reached the Router to which the server is connected. 

    * The Router packet with it. It looks at the Destination IP Address. It finds out the server's Physical Address using a few protocols available. 

    * It sends the frame to the server. 


9. The server gets this Frame: 


        ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------                 
        |   Resource Name: Resource1234 | Type: Request |   ClientPort  | ServerPort | Client IP Address   |   Server IP Address  | Nearest Router's Physical Address | Server's Physical Address|               
        ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------                 


10. The Network Access Layer does it's processing(error detection etc., ), it checks if Server's Physical Address is actually matching the Destination Physical Address in the Frame. If it is fine, that header is stripped. Else, the frame is discarded. 

11. The Network Layer receives the following. 

        --------------------------------------------------------------------------------------------------------------------------            
        |   Resource Name: Resource1234 | Type: Request |   ClientPort  | ServerPort | Client IP Address   |  Server IP Address  |                      
        --------------------------------------------------------------------------------------------------------------------------                         

    * It strips the IP Header and sends it to the Transport Layer. 

12. The Transport Layer receives the following. 

        ------------------------------------------------------------------------------                       
        |   Resource Name: Resource1234 | Type: Request |   ClientPort  | ServerPort |                           
        ------------------------------------------------------------------------------                           

    * Note that server is also just a process. So, even it will be bound to a port. 

    * Transport Layer will strip it's header and sends the rest to Application Layer. 

13. The Application Layer receives it. 

        -------------------------------------------------                    
        |   Resource Name: Resource1234 | Type: Request |                       
        -------------------------------------------------                             
    
    * It sees that someone is requesting for this particular resource. It will process this request. and create the response for the request. 

            ------------------------------------------------                                    
            |   Response: Data          |   Type: Response |                          
            ------------------------------------------------                        


Now, the journey of this is the as the packet from Client to Server. 

There are a few important things about this example: 

1. If you look at how a packet is transferred from Client to Server, it is a series of Layer-2 transmissions where source and destination Physical addresses are changing at every Router. But it is not just that. Each Router intelligently chooses which Router should the packet go next. 

2. When you are reading about networks, you will mostly read about how **packets** travel in the internet and not how **frames** travel in the internet. There is a reason for this. If you look at the above example, the [Data + TL Header + IP Header] never changes throughout it's journey from client to server. Meanwhile, the source and destination Physical Addresses are changing from one device to another. So, frame travels only from one device to another. But a packet goes from source to destination. 

I hope you have got a rough picture on how data travels around the internet, from one machine to another. We will do much deeper analysis in future articles and it will all be practicals along with a bit of theory. 

With that, let us end our discussion on TCP / IP Networking Stack. 

## A few interesting things!

### 1. About headers of Network Layer and Transport Layer

We discussed about Network Layer and Transport Layer and the headers each of these layers add. At Network Layer, we added Source and Destination IP Addresses and at Transport Layer, we added Source and Destination Ports. In reality, each header is just more that Source and Destination numbers. 

The IP Version4 adds a header of 20 bytes. It has Source and Destination IP Addresses but it has a lot of other things also. I did not want to discuss all that here because I wanted to convey just the basic idea of how IP works. 

The Same with the Transport Layer. For example, Transmission Control Protocol(TCP) adds a lot of more details than just Source and Destination Ports. As we discussed, it depends on the protocol, what it's aim is. But the minimum a Transport Layer protocol should do is Process to Process communication and I discussed only that. I did not want to go into complete details. 

We will take up each protocol in good detail in future articles. 


### 2. What are Internet Drafts and RFCs?

Internet Drafts and RFCs are documents which we will be using a lot in the future articles. So, I thought of introducing it here. 

If you want to develop a network protocol and want the whole world to use it, it has to be standardized by an authority called **IETF** - **Internet Engineering Task Force**. There are 2 authorities - IETF and IRTF. IRTF is **Internet Research Task Force**. 

An Internet Draft is a document where you put in all details, specifications etc., of the protocol you are developing and then submit it to IETF. They have working groups which will look at the Draft and suggest corrections, how can things be done better etc., So, an Internet-Draft is an evolving document. Once they give feedback, you modify the protocol accordingly and modify the Internet-Draft and you submit the revised document again. They probably will again give some feedback. This process repeats a number of times. 

Once they think the protocol is good to go, they change the status of the document from an Internet-Draft to what is known as **Request For Comments** - a **RFC**. Once this is done, your protocol is now standardized and it can be implemented in different systems. 

It takes years for an Internet-Draft document to get converted to an RFC. 

Once an RFC is published, it **never** changes. 

So, any protocol we talk about, any network protocol the world is using right now, every one of it has an RFC. It is the document which will give complete details about a particular protocol. 

Whenever we discuss any protocol, we will be referring to the Standard RFCs published by IETF, because they are first-hand information. 

### 3. History of TCP / IP

I have to tell you about the history of TCP / IP. It was first proposed as one single protocol. There were no TCP and IP. It was just called TCP(refer [RFC 675](https://tools.ietf.org/html/rfc675)) which stood for **Transmission Control Program**. 

Both IP and TCP were present as one single protocol. 

The initial Internet-Draft was presented to IETF. IETF felt the protocol was really heavy. And after 3 revisions, the protocol was divided into 2 parts - **IP(Internet Protocol)** and **TCP(Transmission Control Protocol)**. So, there were 2 Internet-Drafts presented - one for each protocol. They were converted to RFCs. 

They are [IP: RFC-791](https://tools.ietf.org/html/rfc791) and [TCP: RFC-793](https://tools.ietf.org/html/rfc793). 

After 3 revisions, the 4th version of the document was standardized to an RFC. This is the reason this version of IP is called IP Version 4. 

So, this is the TCP / IP protocol stack we have now. 

### 4. On examples used in this article

These examples are really simple examples compared to how complex the internet is and how it works. These examples were taken to convey just the basic idea. The TCP / IP stack is a lot more complex and we will dissect and understand all that in future articles. 


### 5. Where exactly is the TCP / IP Stack present?

The TCP / IP Stack is mixture of software and hardware. the Network Access Layer is pretty much the complete Hardware component of the stack. The rest of the 3 Layers are software layers. 

The Network Layer(IP) and Transport Layer(TCP, UDP) are implemented in the Operating System Kernel. 

The Application Layer is implemented completely in the userspace. The browser you use has implementations of most of the Application Layer protocols like http, ftp, smtp etc., 

Take a look at the following diagram: 

            |-------------------------------|
            |       Application Layer       |   --------------> Userspace Layer. Uses API provided by the OS
            |-------------------------------|
           ===================================  -------------> Application Programming Interface(API) - provided by the OS to use the Networking Stack
            |--------------------------------   ----------|
            |        Transport Layer        |             |
            |-------------------------------|             | --> Software present in  Kernel
            |         Network Layer         |             |
            |-------------------------------|   ----------|  
            |     Network Access Layer      |   --------------> Hardware(NIC) controlled by Kernel     
            |-------------------------------| 



So, the Operating System has the Networking Stack and this is how the name of this article was derived.  

## Conclusion

Oh my god! that was an amazing experience writing about the complete networking stack. I learnt a lot while I wrote both parts.  

Generally, people prefer the Top-Down approach of explaining the Networking Stack. That is, start at the Application Layer and slowly go down to other layers. It is actually easy because Application layer is something we work with day in and day out. Websites, Youtube etc., is all at the application layer. So, it is easy to explain. 

I wanted to try the Bottom-Up approach for a simple reason. That is how the stack evolved. First people were playing around with hardware, transmitting signals, encoding, decoding etc., And then came the Network and Transport Layer. Years later, the Application Layer(WWW). And I think this approach will force us think a lot of **why**s. Why exactly do we need another layer, could we do the job in the same layer and questions like that. And I feel such questions strengthen up our fundamentals. This is why, I like this approach.

If you feel if there are parts which are conveyed in a clear manner, feel free to let me know. 

I hope you have some idea about how the internet works. All the protocols I mentioned in this and previous article, let us take them up in a logical manner and discuss them in good detail. 

If you have any questions, suggestions or want to discuss something in more detail, feel free to leave a comment below. 

In the next article, we will look at how to write network programs using the Networking Stack. 

That is it for this article.

Thank you for reading :)

------------------------------------------------------------------------------------------
[Go to next article: Introduction to Network Programming - Part1](/404.html)                  
[Go to previous article: Operating System and Networking Stack - Part1](/packet/overflow/2019/02/01/operating-system-and-networking-stack-part1.html)                     
