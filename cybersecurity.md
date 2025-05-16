---
layout: page
title: On Cybersecurity
permalink: /cybersecurity/
comments: False
---

Hello,

I bachelor'd in Computer Science and was fascinated about cybersecurity for a long time.
I worked in the field of computer security for close to 6 years, 2 as an independent student researcher and close to 4 years at Cisco Systems as a software engineer in one of Cisco's Router Security team.
I worked on a range of subjects - starting from hardware/firmware security to OS security to network and infrastructure security. I started by understanding how code translates to 0s and 1s, the x86 assembly language to designing and working on software solutions that improved the overall security posture of critical infrastructure (the Internet, data-centers, enterprise networks).

1. A long series of posts on reverse engineering, binary exploitation and systems security: [here](/rebeseries-posts/).   
2. The Rust Programming Language interested me a lot. I ended up writing quite a bit about the language internals, lots of code and analysis, particularly on the Event-Driven Programming paradigm. You can find them [here](/rust-posts/).    
3. Network Packet Analysis: As a vowed network security enthusiast, I wrote an amateur network packet analysis tool to understanding various network protocols [here](/packetoverflow-posts/).    
4. In my ever continuing pursuit of understanding Operation Systems better, I wrote an ELF Parser, you can find it [here](/elfparser-posts/).   
6. I did a number of projects on malware analysis, cyber-intelligence, workshops and competitions in the field of computer security. You can find them all [here]().


5. Wrote 2 simple posts on how to setup a simple blog like this one. You can find them here: [Part1](/blogging/2018/11/27/setting-up-a-blog-using-jekyll-Part1.html), [Part2](/blogging/2018/11/27/setting-up-a-blog-using-jekyll-Part2.html).   



3. Malware Analysis, Cyber-Intelligence: I had a number of personal projects from analyzing pieces of malware(like a virus or a trojanhorse), to writing tools (based on concepts explained in various articles, research papers). You can find them [here](/2021/07/18/personal-projects.html).
4. There are some generic articles on computer systems and security [here](/2019/03/25/talks-and-workshops-mainpage.htm).

At one point, I decided to pursue an MBA, so I have switched to the management stream, and have a variety of interests in IT: Information Systems, IT Strategy for Businesses, Cyber-Risk Management, Cybersecurity in Finance and E-Commerce.
Follow this space if these topics interest you.

Cheers,   
Adwaith

-----------------------------------------------------------------------------------------------
PS: Back in the time, I had collected some resources in systems security. You will find a vaguely categorized list below. Hope it helps.

## 1. Binary Analysis, Traslation, Rewriting, Disassembly, Decompilation etc.,

# 1.1 Theses, Surveys

1. [Robust Low-Overhead Binary Rewriting: Design, Extensibility and Customizability - 2021](https://drum.lib.umd.edu/handle/1903/27241). [(backup)](/assets/papers/robust-low-overhead-binary-rewriting-design-extensibility-and-customizability-2021-university-of-maryland.pdf).
2. [Dynamic Binary Lifting and Recompilation - 2020](https://escholarship.org/uc/item/4gd0b9ht). [(backup)](dynamic-binary-lifting-and-recompilation-2020-anil-uci.pdf).
2. [Scalable Validation of Binary Lifters - 2020](https://www.ideals.illinois.edu/handle/2142/107968). [(backup)](/assets/papers/scalable-validation-of-binary-lifters-2020-sandeep-dasgupta-uiuc.pdf)
3. [Increasing the Performance of Symbolic Execution by compiling Symbolic Handling into Binaries - 2020](https://www.eurecom.fr/en/publication/6331). [(backup)](/assets/papers/increasing-the-performance-of-symbolic-execution-by-compiling-symbolic-handling-into-binaries-2020-poeplau-eurecom.pdf).
4. [From Hack to Elaborate Technique - A Survey on Binary Rewriting - 2019](https://doi.org/10.1145/3316415). [(backup)](/assets/papers/from-hack-to-elaborate-technique-a-survey-on-binary-rewriting-june-2019.pdf).
5. [Type Inference on Executables - 2016](https://dl.acm.org/doi/10.1145/2896499): A survey on the type inference problem in binaries. [(backup)](/assets/papers/type-inference-on-executables-2016.pdf).
6. [Analyzing and Securing Binaries Through Static Disassembly - 2017](https://mistakenot.net/): PhD Thesis of Daniel Andriesse at VU Amsterdam. [(backup)](/assets/papers/analyzing-and-securing-binaries-through-static-disassembly-2017-daniel-andriesse-vu-amsterdam.pdf).
7. [Building a Base towards Cyber-autonomy - 2017](https://escholarship.org/uc/item/2gt7v61r): Prof. Yan's PhD Thesis. [(backup)](/assets/papers/building-a-base-for-cyber-autonomy-2017-prof-yan-ucsb.pdf).
8. [Abstraction Recovery for Scalable Static Binary Analysis - 2014](https://figshare.com/articles/thesis/Abstraction_Recovery_for_Scalable_Static_Binary_Analysis/6714434/1). [(backup)](/assets/papers/abstraction-recovery-for-scalable-static-binary-analysis-2014-ej-schwartz-cmu.pdf).
9. [Deep Analysis of Binary Code to Recover Program Structure - 2014](https://drum.lib.umd.edu/handle/1903/15449). [(backup)](/assets/papers/deep-analysis-of-binary-code-to-recover-program-structure-el-2014-el-wazeer-uni-of-maryland.pdf).
10. [Static Analysis of x86 Executables - 2010](https://infoscience.epfl.ch/record/167546?ln=en): PhD Thesis of Johannes Kinder at TU Darmstadt. [(backup)](/assets/papers/static-analysis-of-x86-executables-johannes-kinder-2010-tu-darmstadt.pdf).
11. [Reverse Compilation Techniques - 1994](https://yurichev.com/mirrors/DCC_decompilation_thesis.pdf): PhD Thesis of Christina Cifuentes. An amazing thesis to understand decompilation in detail. [(backup)](/assets/papers/reverse-compilation-techniques-christina-cifuentes-1994.pdf).

## 2. Reversing, Malware Analysis, Memory Forensics, Exploit Dev etc.,

# 2.1 Theses, Surveys

1. [Binary Analysis for Linux and IoT Malware - 2020](https://www.eurecom.fr/en/publication/6364). [(backup)](/assets/papers/binary-analysis-of-linux-and-iot-malware-2020-cozzi-eurecom.pdf).
2. [Advances in Memory Forensics - 2019](https://www.eurecom.fr/en/publication/5967). [(backup)](/assets/papers/advances-in-memory-forensics-2019-fabio-pagani-eurecom.pdf).
3. [Advances in Modern Malware and Memory Analysis - 2015](https://www.eurecom.fr/en/publication/4686). [(backup)](/assets/papers/advances-in-modern-malware-and-memory-analysis-2015-mariano-eurecom.pdf).

# 2.2 Books, websites and other resources

1. [Reverse Engineering for Beginners(RE4B)](https://beginners.re/) : This book is the best if you want to get started with Reverse Engineering. Loads of examples related multiple Architectures like x86, ARM, mips, multiple Compilers - gcc, MSVC. 
2. [challenges.re](https://challenges.re) - If you want to get started with Reverse Engineering and Binary Exploitation, this website is the best way to start!

## 3. TPM, Firmware, BIOS, UEFI, BootLoaders etc.,

# 3.1 Theses, Surveys

1. [Towards System-wide Dynamic Analysis of Embedded Systems - 2020](https://www.eurecom.fr/en/publication/6284). [(backup)](/assets/papers/towards-system-wide-security-analysis-of-embedded-systems-2020-nassim-eurecom.pdf).
2. [Dynamic Binary Firmware Analysis - Challenges and Solutions - 2019](https://www.eurecom.fr/en/publication/5969). [(backup)](/assets/papers/dynamic-binary-firmware-analysis-challenges-and-solutions-2019-marius-muench-eurecom.pdf).
3. [Large Scale Security Analysis of Embedded Devices' Firmware - 2015](https://www.eurecom.fr/en/publication/4685). [(backup)](/assets/papers/large-scale-security-analysis-of-embedded-devices-firmware-2015-andrei-costin-eurecom.pdf).
4. [Development of novel Dynamic Binary Analysis techniques for Security Analysis of Embedded Devices - 2015](). [(backup)](/assets/papers/dev-of-novel-dynamic-binary-analysis-techniques-for-the-security-analysis-of-embedded-devices-2015-jonas-eurecom.pdf).

# 3.2 Books and other resources

## 4. UEFI
	1. [UEFI-EDK2 Training](https://github.com/tianocore-training/Tianocore_Training_Contents/wiki): In-depth training on UEFI. Best way to get started with UEFI.
	2. [EDK2](https://github.com/tianocore/edk2): Firmware development environment for UEFI specifications. In short, one can build a virtual firmware, run it on VM, write UEFI applications, run and test them in that VM.
	3. [EDK2 documents](https://github.com/tianocore/tianocore.github.io/wiki/EDK-II-Documents): Lists all the documents related to EDK2. It has everything from getting started to writing hello-world UEFI programs to training/courses on UEFI.
	4. [Introduction to EFI programming](http://www.rodsbooks.com/efi-programming/) by Roderick Smith.
	5. [x86asm.net - Introduction to UEFI](http://x86asm.net/articles/introduction-to-uefi/index.html)
	6. [EFI Tutorial](https://github.com/safayetahmedatge/efitutorial)
	7. Books on UEFI by its creators: [Harnessing the UEFI Shell](/assets/firmware-security/Harnessing-the-UEFI-shell-Moving-the-platform-beyond-DOS.pdf), [Beyond BIOS](/assets/firmware-security/Beyond-BIOS-Developing-with-the-UEFI.pdf). The first book is an amazing starter. Second one does a deep dive.
	8. [osdev.org UEFI wiki](https://wiki.osdev.org/UEFI)
	9. [Remote debugging UEFI programs with gdb](https://wiki.osdev.org/Debugging_UEFI_applications_with_GDB)

## 5. Firmware-Security, Reversing etc.,
	1. [www.firmwaresecurity.com](https://firmwaresecurity.com/)
	2. [The BIOS blog by Darmawan Salihun](http://bioshacking.blogspot.com/): Insane blog, extremely rich.
	3. [Pinczakko's blog](https://sites.google.com/site/pinczakko/): Another crazy blog
	4. [Vincent Zimmer's blog on firmware, UEFI etc.,](http://vzimmer.blogspot.com/2015/06/firmware-related-blogs.html)
	5. [Satoshi's note](http://standa-note.blogspot.com)

## 6. TPM
	1. [TCG's summary on TPM](https://trustedcomputinggroup.org/resource/trusted-platform-module-tpm-summary/)
	2. [SWTPM](https://github.com/stefanberger/swtpm)
	3. [tpm2 software](https://tpm2-software.github.io/)

## 7. Other related stuff
	1. [Coreboot](https://github.com/coreboot/coreboot): An opensource alternative to proprietary BIOS used by various vendors.
	2. [LinuxBoot](https://www.linuxboot.org/): Linux as firmware.
	3. [System Management BIOS (SMBIOS)](https://www.dmtf.org/standards/smbios/)
	4. [SeaBIOS](https://github.com/coreboot/seabios): Opensource implementation of x86 legacy BIOS.
	5. [Linux from scratch's About firmware](https://www.linuxfromscratch.org/blfs/view/svn/postlfs/firmware.html): This article has links to several amazing articles/github repositories in it.
	6. [Intel's repository of processor microcode](https://github.com/intel/Intel-Linux-Processor-Microcode-Data-Files)

## 8. Firmware, BIOS samples
	1. [Dell downloads](https://www.dell.com/support/home/en-in?app=drivers): Dell publishes System BIOS for a variety of its products. Gold Mine
	2. [HP software downloads](https://support.hp.com/in-en/drivers): Firmware for a bunch of HP products can be downloaded from here.

## 9. Crypto, Math

1. [cryptopals.com](http://cryptopals.com) - Best Crypto site I have come across. Has programming exercises related to different cryptographic algorithms, different attacks on those algorithms. 
2. [crypto101.io](https://crypto101.io) - It is a introductory course on cryptography available in the form of a book. 
3. [projecteuler.net](https://projecteuler.net/) - If you are into Number Theory, Math, Programming, this is one of the best websites to go to!

## 10. Linux Systems Programming

1. [Angrave's System Programming](https://github.com/angrave/SystemProgramming/wiki): This is probably the best resource to get started with Linux systems programming. Its just too good! 
2. [University of Georgia's Systems Programming Course](http://cobweb.cs.uga.edu/~rwr/CS1730/projs.html)
3. [University of Wisconsin-Madison's Operating Systems course](http://pages.cs.wisc.edu/~dusseau/Classes/CS537-F07/projects.html)

## 11. Computer Networks

1. [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/) - One of the best guides for Network Programming in C. 

## 12. Kernel Bypass Techniques

These articles (in this order) helped me understand Kernel Bypass techniques better

1. [Diving into Linux Networking  Stack](http://beyond-syntax.com/blog/2011/03/diving-into-linux-networking-i/) - A gentle introduction of how Network Driver interacts with NIC. 
2. [Inproving Linux Networking Performance](https://lwn.net/Articles/629155/) - This article clearly explains what are the problems with the current(2015) Linux Network Stack and a few suggestions to improve it's performance
3. [What is Kernel Bypass?](https://blog.cloudflare.com/kernel-bypass/) - An amazing article which will help you understand Kernel Bypass techniques which will help improve performance of packet IO. 
4. [netmap - A fast packet I/O Framework](http://info.iet.unipi.it/~luigi/netmap/) - The official website of **netmap**. 
5. [netmap: a novel framework for fast packet I/O](https://www.usenix.org/system/files/conference/atc12/atc12-final186.pdf) - netmap's official paper. Just amazing!
6. [DPDK - Data Plane Development Kit](https://www.dpdk.org/) - Official website of **DPDK**
7. [Impressive Packet Processing Performance Enables Greater Workload Consolidation](http://media15.connectedsocialmedia.com/intel/06/13251/Intel_DPDK_Packet_Processing_Workload_Consolidation.pdf) - Paper explaining DPDK
8. [Zero Copy Networking](https://old.lwn.net/Articles/726917/) - An interesting concept which helps in improving Network Stack performance
9. [Comparision of High Performance Packet IO Frameworks](https://www.net.in.tum.de/publications/papers/gallenmueller_ancs2015.pdf) - An amazing paper which will compare leading fast packet IO frameworks.
