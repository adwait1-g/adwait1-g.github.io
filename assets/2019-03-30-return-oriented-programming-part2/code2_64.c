#include<stdio.h>

char str[] = "/bin//sh";

void inst1() {

	asm("movq $0x3b, %rax");

}

void inst2() {

	asm("lea str, %rdi");
}

void inst3() {

	asm("movq $0, %rsi");
}

void inst4() {

	asm("movq $0, %rdx");
}

void inst5() {

	asm("syscall");
}

void func() {

	char buffer[100];
	gets(buffer);
}

int main() {

	func();

	return 0;
}
