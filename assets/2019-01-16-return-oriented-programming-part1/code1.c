#include<stdio.h>
#include<unistd.h>

void getshell() {

	printf("Get Shell executed!\n");
	execve("/bin/sh", 0, 0);
}

int main() {

	char buffer[100];
	gets(buffer);
	
	return 0;
}

	
