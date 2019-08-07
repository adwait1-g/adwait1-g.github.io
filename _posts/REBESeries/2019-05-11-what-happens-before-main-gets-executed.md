---
title: What happens before main() gets executed?
categories: Reverse Engineering and Binary Exploitation Series
layout: post
comments: true
---

Hey fellow pwners!

Whenever we start writing a C/C++ program, the very first function we write is the ```main()``` function. We always think that the ```main()``` is the **entry point** of execution - meaning the first instruction of the main() function is the very first instruction executed after you do ```./a.out```. This is something we assume and is left unexplored. On the surface, it seems ass if ```main()``` is the entry point. But is it really the entry point? Because main() is also a function, something else should call it right. Who is calling it? What does that code do? Does it do anything other than calling main() ? 

In this post, we will look at what happens before ```main()``` is executed. We will look into every single thing in a sequential, meaningful manner and make sure you are able to see the whole process in a transparent manner.

This is the 19th post of this series. Create a directory named **post_19** in the **rev_eng_series** directory. 

Lets get started!

# Introduction

To understand the whole process of what happens before ```main()``` is executed, let us take up our favorite **Hello World!** program. We will be using the following program. 

```c
rev_eng_series/post_19: cat hello.c
#include<stdio.h>
int main() {
	
	printf("Hello World!\n");
	return 0;
}
```

Let us compile it to get an executable. We will be working on a 64-bit executable in this post.




































