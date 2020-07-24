global _start

section .text
_start:

  xor eax, eax           ; Clearing out EAX register
	xor ecx, ecx           ; Clearing out ECX register
	push eax               ; push for NULL termination
	push dword 0x68732f2f  ; push //sh
	push dword 0x6e69622f  ; push /bin
	mov ebx, esp           ; store address of TOS - /bin//sh
	mov al, 0x0b           ; store Syscall number for execve() = 11 OR 0x0b in AL
	int 0x80               ; Execute the system call 
