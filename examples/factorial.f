PROGRAM FACTORIAL
INTEGER N, I, FAT
PRINT *, 'Enter a positive integer:'
READ *, N
FAT = 1
DO 10 I = 1, N
FAT = FAT * I
10 CONTINUE
PRINT *, 'Factorial of ', N, ': ', FAT
END