---
layout: post
title: Writing simple LLVM Passes
categories: rebeseries
comments: true
---

Hello everyone!

Today, a lot of security features are compiler-based solutions. It is generally a compiler **pass** which does something useful. Although I know the definition of what a pass is and also know how the end-result of a pass looks like, I don't know how to write one.

In this post (and in the next few posts), we will be exploring the LLVM project specifically from the point of view of writing passes.

## 1. Building the LLVM project

Before getting started, build the LLVM project and get ready. You can follow the steps present [here](https://llvm.org/docs/GettingStarted.html). My laptop has 4GB of RAM with 4 cores. When one of the shared libraries was being linked, my laptop froze and minutes later the linker process was killed. You might experience it. I did the following things to compile the project successfully.

1. Increase swap-space from 2GB to 5GB. You can follow [this](https://stackoverflow.com/questions/34858289/how-increasing-swap-size-allow-me-to-increase-the-heap-size) crazy stackoverflow answer.
2. I used "Unix Makefiles" to build the project. A simple **make** would build the project with debugs - that takes lot of memory while compiling. I couldn't not afford it. So I requested for a **release** build and to use the [gold](https://lwn.net/Articles/274859/) linker (which is supposed to be faster for ELF binaries than traditional [ld](https://linux.die.net/man/1/ld)).

```
llvm-project/build$ cmake -G "Unix Makefiles" ../llvm/ -DLLVM_USE_LINKER=gold -DCMAKE_BUILD_TYPE=Release
```

Ofcourse compiling it in Release mode means all the binaries are stripped and can't debug using gdb that easily. But goal now is just to use it and not explore it.

## 2. Writing a hello-world pass

The LLVM Documentation has a very good [tutorial](https://llvm.org/docs/WritingAnLLVMNewPMPass.html) for writing a simple pass. This sub-section will be about following it and writing that pass.

Call our pass **FuncList.pass** which lists all the functions defined in an IR file. It has 2 main files - a header file(**FuncList.h**) where we create a Pass class and declare functions related to that Pass. The other is the sourcefile(**FuncList.cpp**) where we define those functions declared in the Pass class. Once we are done with that, we should make the LLVM build system aware that we have a new pass here and it needs to compile it. For that, we have to add the sourcefile names and the Pass-name in a bunch of places (like build files etc.,). Once we have that, we can build it and test it out.

This does not involve writing an entirely new pass. This is a copy of the **HelloWorld.pass**.

# 2.1 Creating the Pass class - FuncList.h

Considering that our pass is a utility pass, place the **FuncList.h** in **llvm/include/Transforms/Utils/**. Let us create a class and define a **run()** function in it.

```cpp
//===-- FuncList.h - Example Transformations ------------------*- C++ -*-===//  
//                                                                              
// - Just a simple pass which lists all the functions defined in the binary.       
//                                                                              
//===----------------------------------------------------------------------===//
                                                                                
#ifndef LLVM_TRANSFORMS_UTILS_FUNCLIST_H                                        
#define LLVM_TRANSFORMS_UTILS_FUNCLIST_H                                        
                                                                                
#include "llvm/IR/PassManager.h"                                                
                                                                                
namespace llvm {                                                                
                                                                                
class FuncListPass : public PassInfoMixin<FuncListPass> {                       
public:                                                                         
  PreservedAnalyses run(Function &F, FunctionAnalysisManager &AM);              
};                                                                              
                                                                                
} // namespace llvm                                                             
                                                                                
#endif // LLVM_TRANSFORMS_UTILS_FUNCLIST_H
```

1. Start with the conditional compilation statements (```#ifndef```, ```#define``` etc.,) which makes sure that only one content of this header file is copied into the sourcefile it is included in.
2. Then include **llvm/IR/PassManager.h**.
3. Let us define the class inside the **llvm** namespace. 
4. And finally declare the ```run()``` function.

The ```run()``` function prints ```Function``` ```F```'s name.

That was about the header file. Let us go to the sourcefile.

# 2.2 Defining run() function

Create a sourcefile **FuncList.cpp** in **llvm/lib/Tranforms/Utils** directory. Include the **FuncList.h** header file. Then finally define the ```run()``` function.

```cpp
//===-- FuncList.cpp - Example Transformations --------------------------===//  
//                                                                              
// - A simple pass to learn!                                                    
//===----------------------------------------------------------------------===//
                                                                                
#include "llvm/Transforms/Utils/FuncList.h"                                     
                                                                                
using namespace llvm;                                                           
                                                                                
PreservedAnalyses FuncListPass::run(Function &F,                                
                                    FunctionAnalysisManager &AM) {              
  errs() << F.getName() << "\n";                                                
  return PreservedAnalyses::all();                                              
}
```

With that, we are ready with the code. Idea is that when some IR is fed into this pass, this pass should print out the list of functions defined in it.

# 2.3 Making LLVM build system aware

There are a few steps here.

1. Add our new pass into the Passes-list.
	- The **llvm/lib/Passes/PassRegistry.def** has list of all passes. Add ours as well.
	```
	326 FUNCTION_PASS("asan", AddressSanitizerPass(false, false, false))                
	327 FUNCTION_PASS("kasan", AddressSanitizerPass(true, false, false))                
	328 FUNCTION_PASS("msan", MemorySanitizerPass({}))                                  
	329 FUNCTION_PASS("kmsan", MemorySanitizerPass({0, false, /*Kernel=*/true}))        
	330 FUNCTION_PASS("tsan", ThreadSanitizerPass())                                    
	331 FUNCTION_PASS("memprof", MemProfilerPass())                                     
	332 FUNCTION_PASS("funclist", FuncListPass())   /* The new pass! */
	```
	- We have classified our pass as a Function Pass.

2. Include the headefile in **llvm/lib/Passes/PassBuilder.cpp** sourcefile. I think that header file of every pass present should be included here.

```cpp
 231 #include "llvm/Transforms/Utils/StripNonLineTableDebugInfo.h"                   
 232 #include "llvm/Transforms/Utils/SymbolRewriter.h"                               
 233 #include "llvm/Transforms/Utils/UnifyFunctionExitNodes.h"                       
 234 #include "llvm/Transforms/Utils/UnifyLoopExits.h"                               
 235 #include "llvm/Transforms/Vectorize/LoadStoreVectorizer.h"                      
 236 #include "llvm/Transforms/Vectorize/LoopVectorize.h"                            
 237 #include "llvm/Transforms/Vectorize/SLPVectorizer.h"                            
 238 #include "llvm/Transforms/Vectorize/VectorCombine.h"                            
 239                                                                                 
 240 #include "llvm/Transforms/Utils/FuncList.h" // The new pass!
```

3. Finally, let us add our sourcefile into the CMake build system.
```
add_llvm_component_library(LLVMTransformUtils                                   
  AddDiscriminators.cpp                                                         
  AMDGPUEmitPrintf.cpp                                                          
  ASanStackFrameLayout.cpp                                                      
  AssumeBundleBuilder.cpp                                                       
  AutoInitRemark.cpp
  .
  .
  Utils.cpp
  ValueMapper.cpp
  VNCoercion.cpp
  FuncList.cpp
```

With that, we are done writing the pass.

# 2.4 Compiling and Testing

Let us build it.

```
llvm-project/build$ make -j2
```

We will be using the **opt** tool to test our pass.

Let us test it with the example given in the tutorial.

```
llvm-project/build$ ./bin/opt -disable-output -passes=funclist
define i32 @foo() {
  %a = add i32 2, 3
  ret i32 %a
}

define void @bar() {
  ret void
}
foo
bar
```

I entered the IR as input and got the function names "foo" and "bar" as output. It works when the IR is inside a file as well.

```
llvm-project/build$ cat ir.ll 
define i32 @foo() {
  %a = add i32 2, 3
  ret i32 %a
}

define void @bar() {
  ret void
}
```

And send it through out pass.

```
llvm-project/build$ ./bin/opt -disable-output ./ir.ll -passes=funclist
foo
bar
```

I urge you take examples of your own and try it out. You don't have to write IR directly. You can write C/C++ and generate the IR from it (use the **-S -emit-llvm** options).

With that, we have our first pass.

## 3. Listing all IR Instructions in a Function

Let us write a Pass which will list down all the instructions in a function - and it does the same for all functions in the IR file.

# 3.1 Init

We already have a pass which goes over all the functions in a given IR file. Let us extend it now. For each function, we need a way to list its instructions. To do this, we can modify our FuncListPass. Modify the same file OR make a copy and work in the copy. I will be working on a copy.

Create **FuncInst.cpp** in **llvm/lib/Transforms/Utils** and **FuncList.h** in **llvm/include/llvm/lib/Transforms/Utils** directory. Add the pass entry to **llvm/lib/Passes/PassRegistry.def**, add the header file to **llvm/lib/Passes/PassBuilder.cpp** and add the cpp sourcefile into **llvm/lib/Tranforms/Utils/CMakeLists.txt**. With that, we are ready. Let us start with the following:

```cpp
llvm-project/llvm/include/llvm/Transforms/Utils$ cat FuncInst.h 
//===-- FuncInst.h - Example Transformations --------------------*- C++ -*-===//
//
// - Lists all functions and instructions in it
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_TRANSFORMS_UTILS_FUNCINST_H
#define LLVM_TRANSFORMS_UTILS_FUNCINST_H

#include "llvm/IR/PassManager.h"

namespace llvm {

class FuncInstPass : public PassInfoMixin<FuncInstPass> {
public:
  PreservedAnalyses run(Function &F, FunctionAnalysisManager &AM);
};

} // namespace llvm

#endif // LLVM_TRANSFORMS_UTILS_FUNCINST_H
```

and the sourcefile.

```cpp
llvm-project/llvm/lib/Transforms/Utils$ cat FuncInst.cpp 
//===-- FuncInst.cpp - Example Transformations --------------------------===//
//
// - Lists all the functions and the instructions in it.
//===----------------------------------------------------------------------===//

#include "llvm/Transforms/Utils/FuncInst.h"

using namespace llvm;

PreservedAnalyses FuncInstPass::run(Function &F,
                                    FunctionAnalysisManager &AM) {
  errs() << F.getName() << "\n";
  return PreservedAnalyses::all();
}
```

For every function, we execute ```run()```. Currently, we are printing the function name. Now, let us see how we can print the instructions in it.

# 3.2 Operating on Functions

A function has several important members/attributes. Its name, return-type, arguments (if any) and finally the instructions. LLVM offers API to access them. It is described in [here](https://llvm.org/docs/ProgrammersManual.html#the-function-class). The header file related to this is **llvm/IR/Function.h**.

### 3.2.1 Function Return Type

Let us start with the return type. The ```Function``` class offers the function ```getReturnType()```. Dereferencing it would give a ```Type``` object. Let us use this function and print the function's return type. The ```run()``` function looks like this.

```cpp
    // Function name                                                            
    outs() << header << "\n";                                                   
    outs() << "Name: " << F.getName() << "\n";                                  
                                                                                
    // Return type                                                              
    outs() << "Return Type: " << *F.getReturnType() << "\n";
```

### 3.2.2 Function Arguments

A function can have one/more arguments. Simple iterators are exposed to access the arguments.

> Function::arg_iterator - Typedef for the argument list iterator
> Function::const_arg_iterator - Typedef for const_iterator.
> arg_begin(), arg_end(), arg_size(), arg_empty()

Declare a variable of type ```Function::arg_iterator```. Iterate over the arguments (starting from ```arg_begin()``` till ```arg_end()```). Let us print each argument.

```cpp
    // Arguments                                                                
	Function::arg_iterator arg_iter;
    outs() << "Arguments: ";                                             
    if (F.arg_size() == 0)                                                      
    {                                                                           
        outs() << "No Arguments" << "\n";                                       
    }                                                                           
    else                                                                        
    {                                                                           
        for (arg_iter = F.arg_begin(); arg_iter != F.arg_end(); arg_iter++)        
        {                                                                       
            outs() << *arg_iter;                                                
                                                                                
            if (arg_iter != F.arg_end())                                        
            {                                                                   
                outs() << ", ";                                                 
            }                                                                   
        }                                                                       
                                                                                
        outs() << "\n";                                                         
    }
```

With that, we have the arguments ready.

### 3.2.3 Basic blocks

A function is divided into one or more basic-blocks. LLVM provides API to iterate over those Basic-blocks.

```
Function::iterator - Typedef for basic block list iterator
Function::const_iterator - Typedef for const_iterator.
begin(), end(), size(), empty()
```

Declare a variable of type ```Function::iterator```. Iterate over the basic-blocks.

```cpp
	BasicBlock::iterator inst_iter;
	// BasicBlocks                                                              
    outs() << "IR: " << "\n";                                            
    for (bb_iter = F.begin(); bb_iter != F.end(); bb_iter++)                    
    {                                                                           
		// Print instructions
    }
```

What are present in a basic block? Instructions. Each basic-block has one/more instructions. LLVM provides API to iterate over these instructions - it can be found [here](https://llvm.org/docs/ProgrammersManual.html#the-basicblock-class).

```cpp
    // BasicBlocks                                                              
    outs() << i << ". IR: " << "\n";                                            
    for (bb_iter = F.begin(); bb_iter != F.end(); bb_iter++)                    
    {                                                                           
        // Each BB is made of one/more instructions.                            
        // Print them.                                                          
        for (inst_iter = (*bb_iter).begin(); inst_iter != (*bb_iter).end(); inst_iter++)
        {                                                                       
            outs() << *inst_iter << "\n";                                       
        }                                                                       
    }
```

The complete listing is present below. It is beautified a little bit.

```cpp
llvm-project/llvm/lib/Transforms/Utils$ cat FuncInst.cpp 
//===-- FuncInst.cpp - Example Transformations --------------------------===//
//
// - Lists all the functions and the instructions in it.
//===----------------------------------------------------------------------===//

#include "llvm/Transforms/Utils/FuncInst.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Type.h"
#include "llvm/IR/BasicBlock.h"

using namespace llvm;

PreservedAnalyses FuncInstPass::run(Function &F,
                                    FunctionAnalysisManager &AM) {	
	unsigned int i = 0;
	std::string header = "============================================================";
	Function::arg_iterator arg_iter;
	Function::iterator	bb_iter;
	BasicBlock::iterator inst_iter;

	// Function name
	outs() << header << "\n";
  	outs() << "Name: " << F.getName() << "\n";
	
	// Return type
	outs() << i << ". Return Type: " << *F.getReturnType() << "\n";
	i += 1;

	// Arguments
	outs() << i << ". Arguments: ";
	if (F.arg_size() == 0)
	{
		outs() << "No Arguments" << "\n";
	}
	else
	{
		for (arg_iter = F.arg_begin(); arg_iter != F.arg_end(); arg_iter++)
		{
			outs() << *arg_iter;
			
			if (arg_iter != F.arg_end())
			{
				outs() << ", ";
			}
		}

		outs() << "\n";
	}
	i += 1;
	
	// BasicBlocks
	outs() << i << ". IR: " << "\n";
	for (bb_iter = F.begin(); bb_iter != F.end(); bb_iter++)
	{
		// Each BB is made of one/more instructions.
		// Print them.
		for (inst_iter = (*bb_iter).begin(); inst_iter != (*bb_iter).end(); inst_iter++)
		{
			outs() << *inst_iter << "\n";	
		}
	}

  	return PreservedAnalyses::all();
}
```

# 3.3 Build and Test

Let us test the pass with the same example we used before.

```
llvm-pass/llvm-project/build$ ./bin/opt -disable-output ./ir.ll -passes=funcinst
============================================================
Name: foo
0. Return Type: i32
1. Arguments: No Arguments
2. IR: 
  %a = add i32 2, 3
  ret i32 %a
============================================================
Name: bar
0. Return Type: void
1. Arguments: No Arguments
2. IR: 
  ret void
```

Let us try it on an IR file generated by clang frontend. Consider the following C program.

```c
bin-rec/examples$ cat code1.c
void func1(int a, int b, char *buffer, unsigned int buf_size)
{
	int c = 10, d = a, e = b;
	unsigned int len = buf_size;
	char *ptr = buffer;
}


int main()
{
	int a = 10, b = 30;
	long int c = 2345;
	char buffer[100] = {0};

	func1(a, b, buffer, sizeof(buffer));
}
```

Compile it and generate the IR file.

```
bin-rec/examples$ clang-12 code1.c -o code1.ll -S -emit-llvm
```

Let us try to run our pass on **code1.ll**.

```
llvm-project/build$ ./bin/opt -disable-output ../../../bin-rec/examples/code1.ll -passes=funcinst
```

It doesn't work. Even our first pass which simply lists the function names doesn't work.

Why is it not working?

## 4. Modules

The passes we have written are function-passes. The pass works on a function OR a series of functions. I think it cannot understand a construct bigger than a function. Let us take a look at **code1.ll** - the IR generated by clang frontend.

```
; ModuleID = 'code1.c'
source_filename = "code1.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @func1(i32 %0, i32 %1, i8* %2, i32 %3) #0 {
  %5 = alloca i32, align 4
  %6 = alloca i32, align 4
  %7 = alloca i8*, align 8
  %8 = alloca i32, align 4
  .
  .
  .
  .
```

This is a [Module](https://llvm.org/docs/ProgrammersManual.html#the-module-class). This is what the documentation has to say about Modules.

> The Module class represents the top level structure present in LLVM programs. An LLVM module is effectively either a translation unit of the original program or a combination of several translation units merged by the linker. The Module class keeps track of a list of Functions, a list of GlobalVariables, and a SymbolTable. Additionally, it contains a few helpful member functions that try to make common operations easy.

So a Module one level above functions - in the hierarchy of structure. It can have functions, global variables etc., So to parse it, we need to write a ```MODULE_PASS``` using the API present [here](https://llvm.org/docs/ProgrammersManual.html#the-module-class).

# 4.1 Writing a MODULE_PASS

As discussed above, a module can have functions, global variables etc., We already have a simple function-pass which works. Let us use the same code in the module-pass. We will have to write a new function for global variables. Let us call the pass **ReadModulePass**. Create the necessary sourcefiles in necessary locations and add them to the required places - so that it compiles. Our ```ReadModulePass``` looks like this:

```cpp
llvm-project/llvm/include/llvm/Transforms/Utils$ cat ReadModule.h 
//===-- ReadModule.h - Example Transformations ----------------------------===//
//
// - A module reading pass (functions and global variables)
//===----------------------------------------------------------------------===//

#ifndef LLVM_TRANSFORMS_UTILS_READMODULE_H
#define LLVM_TRANSFORMS_UTILS_READMODULE_H

#include "llvm/IR/PassManager.h"

namespace llvm
{

class ReadModulePass : public PassInfoMixin<ReadModulePass>
{

public:
	PreservedAnalyses run(Module &M, ModuleAnalysisManager &AM);
	PreservedAnalyses runOnFunction(Function &F);
	PreservedAnalyses runOnGVariable(GlobalVariable &G);

}; // class ReadModulePass

} // namespace llvm

#endif // LLVM_TRANSFORMS_UTILS_READMODULE_H
```

We have 3 functions: ```run()```, ```runOnFunction()``` and ```runOnGVariable()```. The ```run()``` function is invoked when a Module is encountered. Inside ```run()```, we need to call the other two functions - whenever we encounter Functions and Global variables.

Defining these functions is not a hard task. the [Reference](https://llvm.org/docs/ProgrammersManual.html#the-module-class) manual clearly mentions the API available to us. To iterate over the functions present in a module, we can use the following:

> Module::iterator - Typedef for function list iterator
> Module::const_iterator - Typedef for const_iterator.
> begin(), end(), size(), empty()

We can use a loop from begin() to end(). We call our ```runOnFunction()``` inside the loop-body.

Similarly, the following can be used to iterate over the global variables present in a module.

> Module::global_iterator - Typedef for global variable list iterator
> Module::const_global_iterator - Typedef for const_iterator.
> global_begin(), global_end(), global_size(), global_empty()

Please try writing the functions on your own. The entire listing is present below.

```cpp
llvm-project/llvm/lib/Transforms/Utils$ cat ReadModule.cpp 
//===-- ReadModule.cpp - Example Transformations --------------------------===//
//
// - A module reading pass (functions and global variables)
//===----------------------------------------------------------------------===//

#include "llvm/Transforms/Utils/ReadModule.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Type.h"
#include "llvm/IR/BasicBlock.h"

using namespace llvm;

PreservedAnalyses ReadModulePass::run(Module &M,
                        	         ModuleAnalysisManager &AM)
{	
	Module::global_iterator gv_iter;
	Module::iterator func_iter;
	std::string header = "==================================================";

	// Go over the global variables first.
	for (gv_iter = M.global_begin(); gv_iter != M.global_end(); gv_iter++)
	{
		outs() << header << "\n";
		runOnGVariable(*gv_iter);
	}

	// Functions
	for (func_iter = M.begin(); func_iter != M.end(); func_iter++)
	{
		outs() << header << "\n";
		runOnFunction(*func_iter);
	}

	return PreservedAnalyses::all();
}

PreservedAnalyses ReadModulePass::runOnFunction(Function &F)
{
	unsigned int i = 0;
	Function::arg_iterator arg_iter;
	Function::iterator	bb_iter;
	BasicBlock::iterator inst_iter;

  	outs() << "Name: " << F.getName() << "\n";
	
	// Return type
	outs() << i << ". Return Type: " << *F.getReturnType() << "\n";
	i += 1;

	// Arguments
	outs() << i << ". Arguments: ";
	if (F.arg_size() == 0)
	{
		outs() << "No Arguments" << "\n";
	}
	else
	{
		for (arg_iter = F.arg_begin(); arg_iter != F.arg_end(); arg_iter++)
		{
			outs() << *arg_iter;
			
			if (arg_iter != F.arg_end())
			{
				outs() << ", ";
			}
		}

		outs() << "\n";
	}
	i += 1;
	
	// BasicBlocks
	outs() << i << ". IR: " << "\n";
	if (F.isDeclaration() == true)
	{
		outs() << "Declaration. No IR" << "\n";
	}
	else
	{
		for (bb_iter = F.begin(); bb_iter != F.end(); bb_iter++)
		{
			// Each BB is made of one/more instructions.
			// Print them.
			for (inst_iter = (*bb_iter).begin(); inst_iter != (*bb_iter).end(); inst_iter++)
			{
				outs() << *inst_iter << "\n";	
			}
		}
	}

  	return PreservedAnalyses::all();
}

PreservedAnalyses ReadModulePass::runOnGVariable(GlobalVariable &G)
{	
	outs() << G << "\n";
	return PreservedAnalyses::all();
}
```

Let us build this and test it on IR modules generated by the clang frontend. For the below program,

```c
llvm-project/build$ cat code1.c
int global_var = 12345;

void func1(int a, int b, char *buffer, unsigned int buf_size)
{
	int c = 10, d = a, e = b;
	unsigned int len = buf_size;
	char *ptr = buffer;
}


int main()
{
	int a = 10, b = 30;
	long int c = 2345;
	char buffer[100] = {0};

	func1(a, b, buffer, sizeof(buffer));
}
```

We get the following from our pass.

```
llvm-project/build$ clang-12 code1.c -o code1.ll -S -emit-llvm
llvm-project/build$ ./bin/opt -disable-output ./code1.ll -passes=read-module
==================================================
@global_var = dso_local global i32 12345, align 4
==================================================
Name: func1
0. Return Type: void
1. Arguments: i32 %0, i32 %1, i8* %2, i32 %3, 
2. IR: 
  %5 = alloca i32, align 4
  %6 = alloca i32, align 4
  %7 = alloca i8*, align 8
  %8 = alloca i32, align 4
  %9 = alloca i32, align 4
  %10 = alloca i32, align 4
  %11 = alloca i32, align 4
  %12 = alloca i32, align 4
  %13 = alloca i8*, align 8
  store i32 %0, i32* %5, align 4
  store i32 %1, i32* %6, align 4
  store i8* %2, i8** %7, align 8
  store i32 %3, i32* %8, align 4
  store i32 10, i32* %9, align 4
  %14 = load i32, i32* %5, align 4
  store i32 %14, i32* %10, align 4
  %15 = load i32, i32* %6, align 4
  store i32 %15, i32* %11, align 4
  %16 = load i32, i32* %8, align 4
  store i32 %16, i32* %12, align 4
  %17 = load i8*, i8** %7, align 8
  store i8* %17, i8** %13, align 8
  ret void
==================================================
Name: main
0. Return Type: i32
1. Arguments: No Arguments
2. IR: 
  %1 = alloca i32, align 4
  %2 = alloca i32, align 4
  %3 = alloca i64, align 8
  %4 = alloca [100 x i8], align 16
  store i32 10, i32* %1, align 4
  store i32 30, i32* %2, align 4
  store i64 2345, i64* %3, align 8
  %5 = bitcast [100 x i8]* %4 to i8*
  call void @llvm.memset.p0i8.i64(i8* align 16 %5, i8 0, i64 100, i1 false)
  %6 = load i32, i32* %1, align 4
  %7 = load i32, i32* %2, align 4
  %8 = getelementptr inbounds [100 x i8], [100 x i8]* %4, i64 0, i64 0
  call void @func1(i32 %6, i32 %7, i8* %8, i32 100)
  ret i32 0
==================================================
Name: llvm.memset.p0i8.i64
0. Return Type: void
1. Arguments: i8* %0, i8 %1, i64 %2, i1 %3, 
2. IR: 
Declaration. No IR
```

With that, we have a simple module-reading pass.

## 5. Conclusion

In this post, we saw how to write simple passes. We saw the hierarchy of classes. It starts with Modules - which contains GlobalVariables and Functions. Each Function has ReturnType, Arguments, BasicBlocks, Instructions etc.,

A detailed explanation of the hierarchy of classes is given [here](https://llvm.org/docs/ProgrammersManual.html#the-core-llvm-class-hierarchy-reference). This post is written entirely refering to it.

It should be observed that these were read-only passes. We did not change anything in the IR. We simply read it and output information which we felt important.

More interesting passes are the ones which change the IR. Optimizations to the IR tries to reduce the amount of IR - without changing any functionality - they are called Optimization Passes. Similarly, security hardening techniques are also implemented as passes which modify the IR. SafeStack, Stack-Cookie protection, ShadowCallStack etc., add code to the IR to make it more secure. They are put under **CodeGen** directory (CodeGen passes).

In the next article, we will be writing a few such passes.

With that, we come to the end of this article.

Thank you for reading :)
