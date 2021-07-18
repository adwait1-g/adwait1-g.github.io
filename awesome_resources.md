---
layout: page
title: Awesome Resources
permalink: /awesome_resources/
---

These are a few resources I have used to explore various fields in Computer Science. Hope it helps :)

## TPM, Firmware, BIOS, UEFI, BootLoaders etc.,

Here are a few interesting resources which explore the Pre-OS state of a box.

1. UEFI
	1. [UEFI-EDK2 Training](https://github.com/tianocore-training/Tianocore_Training_Contents/wiki): In-depth training on UEFI. Best way to get started with UEFI.
	2. [EDK2](https://github.com/tianocore/edk2): Firmware development environment for UEFI specifications. In short, one can build a virtual firmware, run it on VM, write UEFI applications, run and test them in that VM.
	3. [EDK2 documents](https://github.com/tianocore/tianocore.github.io/wiki/EDK-II-Documents): Lists all the documents related to EDK2. It has everything from getting started to writing hello-world UEFI programs to training/courses on UEFI.
	4. [Introduction to EFI programming](http://www.rodsbooks.com/efi-programming/) by Roderick Smith.
	5. [x86asm.net - Introduction to UEFI](http://x86asm.net/articles/introduction-to-uefi/index.html)
	6. [EFI Tutorial](https://github.com/safayetahmedatge/efitutorial)
	7. Books on UEFI by its creators: [Harnessing the UEFI Shell](/assets/firmware-security/Harnessing-the-UEFI-shell-Moving-the-platform-beyond-DOS.pdf), [Beyond BIOS](/assets/firmware-security/Beyond-BIOS-Developing-with-the-UEFI.pdf). The first book is an amazing starter. Second one does a deep dive.
	8. [osdev.org UEFI wiki](https://wiki.osdev.org/UEFI)
	9. [Remote debugging UEFI programs with gdb](https://wiki.osdev.org/Debugging_UEFI_applications_with_GDB)

2. Firmware-Security, Reversing etc.,
	1. [www.firmwaresecurity.com](https://firmwaresecurity.com/)
	2. [The BIOS blog by Darmawan Salihun](http://bioshacking.blogspot.com/): Insane blog, extremely rich.
	3. [Pinczakko's blog](https://sites.google.com/site/pinczakko/): Another crazy blog
	4. [Vincent Zimmer's blog on firmware, UEFI etc.,](http://vzimmer.blogspot.com/2015/06/firmware-related-blogs.html)
	5. [Satoshi's note](http://standa-note.blogspot.com)

3. TPM
	1. [TCG's summary on TPM](https://trustedcomputinggroup.org/resource/trusted-platform-module-tpm-summary/)
	2. [SWTPM](https://github.com/stefanberger/swtpm)
	3. [tpm2 software](https://tpm2-software.github.io/)

4. Other related stuff
	1. [Coreboot](https://github.com/coreboot/coreboot): An opensource alternative to proprietary BIOS used by various vendors.
	2. [LinuxBoot](https://www.linuxboot.org/): Linux as firmware.
	3. [System Management BIOS (SMBIOS)](https://www.dmtf.org/standards/smbios/)
	4. [SeaBIOS](https://github.com/coreboot/seabios): Opensource implementation of x86 legacy BIOS.

5. Firmware, BIOS samples
	1. [Dell downloads](https://www.dell.com/support/home/en-in?app=drivers): Dell publishes System BIOS for a variety of its products. Gold Mine
	2. [HP software downloads](https://support.hp.com/in-en/drivers): Firmware for a bunch of HP products can be downloaded from here.

The following is a small list of really amazing websites I have come across and have worked on a few things present in those websites. 

1. [Reverse Engineering for Beginners(RE4B)](https://beginners.re/) : This book is the best if you want to get started with Reverse Engineering. Loads of examples related multiple Architectures like x86, ARM, mips, multiple Compilers - gcc, MSVC. 

1. [challenges.re](https://challenges.re) - If you want to get started with Reverse Engineering and Binary Exploitation, this website is the best way to start!

2. [cryptopals.com](http://cryptopals.com) - Best Crypto site I have come across. Has programming exercises related to different cryptographic algorithms, different attacks on those algorithms. 

3. [projecteuler.net](https://projecteuler.net/) - If you are into Number Theory, Math, Programming, this is one of the best websites to go to!

4. [crypto101.io](https://crypto101.io) - It is a introductory course on cryptography available in the form of a book. 

5. [https://yurichev.com/mirrors/DCC_decompilation_thesis.pdf](An amazing PhD thesis which talks about Reverse-Compilation/Decompilation Techniques) - I believe there are all the details needed to write a decompiler!

6. [Reverse Engineering using the Linux Operating System](http://reverse.lostrealm.com/)

## Linux Systems Programming

I was searching for a few systems programming projects. I found these.

1. [Angrave's System Programming](https://github.com/angrave/SystemProgramming/wiki): This is probably the best resource to get started with Linux systems programming. Its just too good! 

2. [University of Georgia's Systems Programming Course](http://cobweb.cs.uga.edu/~rwr/CS1730/projs.html)

3. [University of Wisconsin-Madison's Operating Systems course](http://pages.cs.wisc.edu/~dusseau/Classes/CS537-F07/projects.html)


## Computer Networks

### Network Programming

1. [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/) - One of the best guides for Network Programming in C. 


### Kernel Bypass Techniques

These articles (in this order) helped me understand Kernel Bypass techniques better

1. [Diving into Linux Networking  Stack](http://beyond-syntax.com/blog/2011/03/diving-into-linux-networking-i/) - A gentle introduction of how Network Driver interacts with NIC. 
2. [Inproving Linux Networking Performance](https://lwn.net/Articles/629155/) - This article clearly explains what are the problems with the current(2015) Linux Network Stack and a few suggestions to improve it's performance
3. [What is Kernel Bypass?](https://blog.cloudflare.com/kernel-bypass/) - An amazing article which will help you understand Kernel Bypass techniques which will help improve performance of packet IO. 
4. [netmap - A fast packet I/O Framework](http://info.iet.unipi.it/~luigi/netmap/) - The official website of **netmap**. 
5. [netmap: a novel framework for fast packet I/O](https://www.usenix.org/system/files/conference/atc12/atc12-final186.pdf) - netmap's official paper. Just amazing!
6. [DPDK - Data Plane Development Kit](https://www.dpdk.org/) - Official website of **DPDK**
7. [Impressive Packet Processing Performance Enables Greater Workload Consolidation](http://media15.connectedsocialmedia.com/intel/06/13251/Intel_DPDK_Packet_Processing_Workload_Consolidation.pdf) - Paper explaining DPDK
8. [Zero Copy Networking](https://old.lwn.net/Articles/726917/) - An interesting concept which helps in improving Network Stack performance
9. [Comparision of High Performance Packet IO Frameworks](https://www.net.in.tum.de/publications/papers/gallenmueller_ancs2015.pdf) - An amazing paper which will compare leading fast packet IO frameworks
