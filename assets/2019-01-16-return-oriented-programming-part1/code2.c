#include<stdio.h>

char str[] = "/bin//sh";

void inst1() {

	asm("movl $0xb, %eax");
	asm("ret");

}

void inst2() {

	asm("lea str, %ebx");
	asm("ret");
}

void inst3() {

	asm("movl $0, %ecx");
	asm("ret");
}

void inst4() {

	asm("movl $0, %edx");
	asm("ret");
}

void inst5() {

	asm("int $0x80");
	asm("ret");
}

int main() {

	char buffer[100];
	gets(buffer);

	return 0;
}
