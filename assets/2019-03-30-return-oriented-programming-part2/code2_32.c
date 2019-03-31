#include<stdio.h>

char str[] = "/bin//sh";

void inst1() {

	asm("movl $0xb, %eax");

}

void inst2() {

	asm("lea str, %ebx");
}

void inst3() {

	asm("movl $0, %ecx");
}

void inst4() {

	asm("movl $0, %edx");
}

void inst5() {

	asm("int $0x80");
}

void func() {

	char buffer[100];
	gets(buffer);
}

int main() {

	func();

	return 0;
}
