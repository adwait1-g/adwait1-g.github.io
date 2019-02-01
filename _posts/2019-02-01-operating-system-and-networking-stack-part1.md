---
layout: post
title: Operating System and Networking Stack - Part1
categories: Packet Overflow
comments: true
---

Hello everyone!

Before we start the series, there are a few really important fundamentals like how exactly 2 devices communicate, what is an IP Address and many more fundamental questions. So, in this article, we will look into all those questions. 

## Overview

In today's world, We are surrounded by devices that are capable of talking to each other. There are laptops, mobile phones, smart devices etc., How are they able to talk to each other? What does the device(Eg: your Mobile phone) have which is enabling it to talk to other devices(like Youtube Server)? Does it need specialized hardware? Does it need software? What are the other things needed to enable this kind of Inter-device communication? 

Consider 2 devices **A** and **B** that are able to talk to each other. 

    ---------                                                   ---------
    |       |             Some magic happens!                   |       |
    |   A   |   <------------------------------------------->   |   B   |
    |       |                                                   |       |
    ---------                                                   ---------

This is where we are. So, starting with this, we will start digging in every direction possible and learn what that magic is.

Before we go ahead, the following is important.

When 2 people talk to each other, they both talk in a language that they both understand. The same rule applies when 2 machines talk to each other. Both of them have to agree on the same language(or same set of rules). It is technically known as a **Protocol**. Once that is done, each will understand what the other is talking. 

When 2 people talk, there might be violation of protocol . Suppose A and B are 2 people. A can understand Language L1 and can talk L2. B can understand language L2 and can talk L1. In this case, A can talk in L2 and B can talk in L1 and that way, share information. 

When machines talk to each other, they **must** follow the same protocol unless you build a protocol which can understand and talk multiple other protocols. 

When I tell 2 machines talk to each other, I mean there is sharing of data between those 2 machines. 

## Part 1

In this part, let us think how A and B would communicate? Different problems involved in it. 

Consider the situation where A wants to send a file to B. Note that the file(or data) is just a stream of **0**s and **1**s. As those 0s and 1s have to be **transmitted** from A to B, the first thing to be done is **encode**(convert) that stream of bits into **Electromagnetic Signals**. A transmits that signal and B receives it and **decodes**(convert back) it back to 0s and 1s hence getting the file. 

As we discussed earlier, both A and B have to decide on the same protocol - or the same encoding and decoding scheme, same frequency of the Signal etc., Basically, if they abide by a single **standard**  , they can talk to each other without any problems. 

If A and B are connected with a wire, the Signal can be travel through the wire and reach B. If A and B not connected with a wire, Air is the medium. The Signal should be transmitted into the air and B should receive it. 

If there are only 2 machines, they can probably talk to each other directly(have you heard of **Bluetooth**?). Consider a more realistic situation where there are multiple devices which want to talk to each other. 

There are different ways to connect them. They are known as Network topologies. Topology is basically a type of configuration of devices.

1. **Mesh Topology**: Connect every device to every other device. 

2. **Bus Topology**: All devices are connected to one single Bus / wire and that way, they can communicate with each other.

        |-------|                   |-------|                   |-------|                   |-------|
        |   A   |                   |   B   |                   |   C   |                   |   F   |
        |-------|                   |-------|                   |-------|                   |-------|
            |                           |                           |                           |
        ================================================================================================    
        ================================================================================================    
                        |                           |                           |
                    |-------|                   |-------|                   |-------|
                    |   D   |                   |   E   |                   |   G   |
                    |-------|                   |-------|                   |-------|

    * That huge wire to which all machines are connected to is the **Bus**. 

           
3. **Star Topology**: All devices are connected to one central device which helps in transferring data from one device to another. 

    
                    |-----------|
             W------|           |----- A 
             E------|  Central  |----- Q
             X------|  Device   |----- B
                    |-----------|

    * If A wants to send data to X, it sends it to the Central device. That Central device sends the data to X. 

    * This is a very efficient topology, but if the Central Device stops working, then the complete network is down. 

4. **Ring Topology**: Look at the following diagram

            A-----B-----C-------D
            |                   |
            J                   E 
            |                   |
            I-----H-----G-------F

    * It is literally a Ring. 

Each topology has it's own advantages and disadvantages. I will leave it to you to explore the them.

## Part 2

Knowing the different topologies, we can design better networking systems when there are multiple devices who would want to talk to each other.

Consider the same situation of A sending a file to B with the following diagram: 

    A ----------- ID0 -------------- Q
                    |--------------- W
                    |--------------- B
                    |--------------- T
                    |--------------- Y


This is a network.

This is a star topology, where ID0(Intermediate Device 0) is the Central Device to which all the devices are connected to. 

There are 6 devices connected to ID0 - A and B are also there. Connected I mean there are 6 physical ports(holes) and the 6 devices are connected with the help of a wire. A needs to send a file to B. What will it do?

A simply sends the Signals to ID0. ID0 receives it and transmits that to all the devices connected to it(including A). It is a repeater. It's job is to repeat the signal it receives to all connected devices. Commercially, such devices which simply sends the data to all connected nodes is known as a **Hub**. 

So, B receives the Signal(hence the file). What is the problem with this approach? 

Problem is that the other devices are also receiving that file. Suppose that file is secret to A and B. You are a malicious machine connected to ID0. You get that file. That is the problem. Also, unnecessary signals in the network.

How do we solve this problem? 

When every networking device is manufactured, it is given a number, which can be used as the **Unique Identifier**. We can use those identifiers to solve this problem. Consider the topology now.


    A(12345) -----------  ID0 -------------- Q(45933)
                        |--------------- W(92749)
                        |--------------- B(71828)
                        |--------------- T(10138)
                        |--------------- Y(25582)


The manufacturer assigns unique numbers to all these 6 devices. A sends the signal to B. Will only B get the signal? probably not. Because our Intermediate Device is not aware of this unique identification. So, it has to store all this data. Look at the following table. 

    Intermediate Device 0

    Unique Device Number    |       Physical Port
                            |   
           12345            |           0
           45933            |           1
           92749            |           2
           71828            |           3
           10138            |           4
           25582            |           5


So, we had to upgrade our Intermediate Device so that it can store that table. So, our Intermediate Device is not a **hub** which simply sends signals to all devices connected. It is known as a **switch**. It is intelligent and it sends signals to the proper destination machine.

From here, let us call these Unique Identifiers as **Addresses**. 

If such a system should work, what are the changes to be done in the current system?

1. The Signal of just the file(data) is not enough now. We have to let the Intermediate Device know that this file should be sent to B or 71828 only. So, along with the file, we have to store the Destination Address also. Something like this. 

        |-----------------------|-------|
        |    File data          | 71828 |
        |-----------------------|-------|   


    * We have to store the Destination Address. 

    * A encodes the above into Signal. That Signal is sent to Intermediate Device. It decodes it and sees that Destination Address = 71828. It looks at the table above - to which physical port 71828 is connected to. It concludes that B(71828) is connected to physical port 3. So, Intermediate Device encodes it again and sends it to physical port 3. B (and only B) receives it. 

    * The problem is solved. 

To solve that problem, we had to do quite a bit of things. use the Unique Identifiers(Addresses) given to the machines, setup such a table in the Intermediate Device(memory overhead), add a few **definite** number of bytes in front of the data which is the destination address(transmission overhead) and finally some compute in finding out which Physical port a machine with some Identity connected to. 

Now, we no longer just send data. We also send useful information like Destination Address along with it which will help the switch to send the data to proper destination machine. 

You might have heard of the words header and footer. Header is something which comes first(before any data). Footer is something which comes at the last(after all the data). So, looking at the above diagram, we can conclude that we have a small **Header** connected to the data. The whole structure(Data + Destination Address) is called a **Data Frame**. 

Lets think further. Suppose B wants to know who sent the file? How will it know? 

Why does B want to know who sent the file? Suppose I am a malicious machine Q and sent a very similar looking file. B receives it and simply runs it. So, B just ran the malicious file. That is bad.

Simple solution is put the Source Address(Unique Identifier of sender) also. So, we put both Source and Destination Addresses. Now, this is what the Data Frame looks like.

    |-----------------------|---------------|---------------------|
    |    File data          |Source Address | Destination Address |
    |-----------------------|---------------|---------------------|

Now, the Header contains both Source and Destination Addresses. 

So, we have built a small working Computer Network here. Any 2 connected machines can talk to each other.

Now, is it all perfect and fine? 

There are a few things to think about. 

1. What happens when say all 6 devices send data simultaneously? The Signals might interfere with each other and data is lost. This is known as a **Collision**. So, how do we take care of collision?

2. The transmission medium will have noise(a lot of disturbance). So, if the Signal is modified by the surrounding noise, the receiver might not receive the same signal that the sender had transmitted. Such changes are seen as **bit errors** once signal is decoded back to binary form. Bit Error simply is a bit flip. 0 becoming 1 and 1 becoming 0 because of the noise. So, receiver doesn't every know what the correct data is right? It simply receives whatever destined to it. How do we tell that there are errors in data? 

So, how do we take care of the above things? We have to deal with Errors and Data Loss due to Collision. 

To take care of the first problem, we can solve it if we schedule the transmission of data. What this means is, literally put up a time table which will allot time interval for a particular connected machine to send. When it is sending, no one else should send. This is just a naive way to handle the problem. You can think of it like this. There is one huge channel. Only one can use it at a time. If multiple people use it, collision might happen and data is lost. There are multiple **Collision Detection** and **Collision Avoidance** Algorithms which can handle this.

There are Error Detection and Correction Algorithms that can be deployed to take care of second problem. 

For all this to be implemented, many other things are included into the header. 

Now, what is our position? 

This is a very important stage. 

At this point, you would have realized that networking indeed needs specialized hardware and software. 

There is a **dedicated** Hardware known as the **Network Interface Card(NIC)** which a machine should have. 

It does a lot of work. Given bunch of data, it is cut into smaller pieces, the header is added to each piece - which is a Data Frame. Now, this Data Frame is encoded and transmitted by Source's NIC. The Destination's NIC receives the data and decodes it back. Note that an NIC has both reception and transmission capabilities. 

Network Interface Card, the very name of the hardware says it is the  **Interface** between machine and Computer network outside. 

That part of NIC which manages the transmission and reception part is also known as the **Physical Layer**. It is called **Physical** because it is in direct contact with the Physical medium like air or copper wire into which the signals are transmitted. 

The other part like Addresses, Collision Detection/Avoidance, Error Detection and correction - all this is done by another part of NIC. The whole layer of hardware dealing with this is known as the **Data-Link Layer**.

So, NIC is a single piece of hardware which is logically partitioned into Physical Layer and Data-Link Layer.

It is named as **Data-Link** because takes care of Transferring Data in Links. The Link is nothing but the channel where Collisions might occur. 

The Data-Link Layer has a very strong relation with the Physical Layer. You can about it like this. The user wants to send some data. He/She sends it to the Data Link Layer. Data Link Layer takes that data, divides it into to pieces(if it is too huge to send in one go), add the required header information to each chunk and then send it to Physical Layer. Each of that chunk of data along with header is known as a **Data-Frame**. Physical Layer simply takes each frame, encodes it and sends it to the nearest repeater. 

At this point, this is what every device has in order to enable networking.

              Userspace   
        ------------------------------
        |       API                  | -----------> Interface between OS and Userspace
        --------------------------------------|
        |   Network Drivers(Software)|        |
        ------------------------------        |
        |  Data-Link Layer(Hardware) |        |---> Part of Operating System 
        |-----------------------------        |
        |  Physical layer(Hardware)  |        |
        ------------------------------ -------|


The Data-Link Layer and Physical Layer is typically 1 single device - the Network Interface Card. To manage any hardware, make it work, you would need software. That software is known as a **Driver**. It typically drives the NIC to function properly. 

This is the **Networking Stack** of the Operating System. It is called stack because one layer is stacked on the other layer. So, our Networking Stack as of now has 2 layers.

There is an API(Application Programming Interface) provided by the OS to the users to write programs which can make 2 machine communicate. 

I think we have discussed enough about these 2 layers. Let us move ahead!

## Part 3

We spoke about how Data-Frames are sent from an Input port to an output port. That action of transfering data-frames from Input Port to Output Port based on a definite logic is known as **switching**. As it was happening at the Data-Link Layer, it is known as **Link Layer Switching**. Such intermediate devices are known as **switches**. 

Now, with all this, do we have our ideal network where a lot of machines can be connected with ease? Let us investigate.

Consider the following scenario.

There are 2 networks N1 and N2. Machine A is part of N1 and B belongs N2. A wants to send a file to B. How will this happen?


    A --------|                                  |--------- B
    Q --------|                                  |--------- S
    W --------|---- SwitchN1        SwitchN2-----|--------- D
    E --------|                                  |--------- F
    R --------|                                  |--------- G


If A wants to send the file to any of the machines connected to SwitchN1, we know how it is done. But, A wants to send the file to B. 

From the diagram, we can tell that if we just connect SwitchN1 and SwitchN2, won't the problem be solved? 

Yes. But this will need some extra logic put into the switches. A sends the Frames to SwitchN1. It looks at it's Table and finds out there is no B in it. Now, the switch does not know what to do with that data frame. So, we have to write logic saying, if the destination address is not present in it's Table, send that data frame to SwitchN2 through their connection. So, it sends the Frames to SwitchN2. SwitchN2 looks at it's Table and B is present there, so all frames are sent to B. 

Suppose the file is divided into 100 data frames, a frame looked like this: 

    ---------------------------------------------------------------------------------
    |   Data piece - 87 |  Source(A's Address)  | Destination(B's Address)  |
    ---------------------------------------------------------------------------------

100 such frames travel from A to SwitchN1, then to SwitchN2 and finally reaching B. 

Okay. Now let us change the situation a little bit. Consider there are 100 such networks. A is in SwitchN1's network and B is in SwitchN100's network. A wants to send a file to B. How is it done?

In the previous situation, we just connected the 2 switches and problem was solved. But now, there are 100 switches. How do we connect all 100 of them? Even if we connect, SwitchN1 will have to send each of the other switches a copy of the file because switchN1 simply doesn't know where B is. This would be a huge waste of energy. Only 1 copy out of those 99 copies will be successful in reaching B. Rest all are discarded. This will also cause a lot of collision because there are a lot of un-necessary traffic in the network. 

This is a simple example. Consider the whole world population, with one mobile phone with each person getting connected to such a network. All the switches will go mad in no time!

So, how do we solve it? We need to minimize the energy lost(reduce frame replication) and the system should be able to handle such huge number of networks. 

Consider the following model: 

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

Let us continue our discussion in the next article.

## A few interesting things

### About Layer-2 protocols

2 very popular Layer-2 protocols are **Ethernet** and **WiFi**. If you say your machine supports Ethernet as a Data-Link Layer protocol, it means your machine has a **Ethernet Card** or **Ethernet Network Interface Card**. So, the protocol is implemented in the hardware itself. This is what I meant when I told the Data-Link Layer is implemented in the hardware itself.

Similarly, if your machine is able to use WiFi, it means your machine has a **WiFi Card** or **WiFi Network Interface Card**. 

There are other layer-2 protocols also like Point-to-Point Protocol(PPP), Token Ring etc., Each of these have their own Network Interface Cards. But they are not as widely used as Ethernet and WiFi. 

All the discussion in this article was done with Ethernet in mind. This is because Ethernet is the most used layer-2 protocol in the world. So, the switching, the Data-Frame structure etc., are all specific to Ethernet. I wanted to explain all the concepts without bringing in new technical terms.

We used an Intermediate Device called a **switch** to which all other devices are connected to. From this, it is evident that Ethernet is a Star Topology, The Switch being the Central device. But if you explore more about Ethernet, you will see that the complete network functions as if it were a **Bus Topology**. It is how Ethernet works. That is why, physically(according to the way devices are connected), Ethernet is Star Topology. But logically(the way the Ethernet actually functions), it is a Bus Topology. 

And The logical topology is the one we have to consider while discussing about Ethernet because that is how it is working. 

You would have heard / seen of LAN ports. You have a cable using which you will connect your machine's Ethernet Port to that LAN port. The protocol being used here is mostly Ethernet. It is important to note that Ethernet is used in **wired** networks.

If you want to go wireless, you can use **WiFi**. 

There are significant differences between WiFi and Ethernet and that will probably take up one complete post. So, let us leave it here for now.

### About the Address used

The Unique Identifier given by the manufacturer was used to connect multiple devices. That is also known as **Physical Address**, **MAC Address**. The Physical Address is **6-bytes** / **48-bits** long. 

### Can a single machine have multiple NICs?

Yes. Absolutely. In today's world, every laptop, desktop has atleast 2 NICs: Ethernet and WiFi - 2 most common ways one can get connected to the network.

So, it is important to understand that such an Address doesn't identify a device. It identifies a **Networking Device**, which is basically a Network Interface Card. So, a Physical Address should never be used to identify a device like laptop, phone etc., because each one can have multiple NICs and thus can have multiple Physical Addresses.

### Just something I remember

When I was a little kid(~2005), my father bought a new laptop. That laptop didn't have any NIC in it by default. But it had a physical port where we could insert any NIC we want. So, we went to the store, bought a WiFi NIC. NIC was removable at that time. That laptop was not capable of networking by itself but it had given a provision to support networking. We had to insert this NIC, install the necessary software required and then we were ready to go!

Fast forward to 2019. 

All machines come in with built-in NICs. They have become such an integral part of a device that it is integrated with the motherboard of the device. 

When someone buys a computer now, it is very natural to take it for granted that it has NICs. Generally, it will have atleast 2 NICs. One is the Ethernet Card and a WiFi Card.

## Conclusion

With this, I will end this article. 

In the next article, we will see what that Magic Device is and answer questions like does it need another Layer on top of Layer-2, how does that work etc., 

I hope you have got some idea on how networks work, the layered model of the Networking Stack.

Thank you for reading :)

--------------------------------------------------------------
[Go to next article: Operating System and Networking Stack - Part2](/packet/overflow/2019/02/01/operating-system-and-networking-stack-part2.html)            
[Go to previous article: Packet Overflow! - Introductory article](/packet/overflow/2019/01/27/packet-overflow.html)
