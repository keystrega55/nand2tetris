// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

@i
M=0    // i = 0
@sum
M=0    // sum = 0
@R1
D=M
@limit
M=D    // limit = RAM[R1]

@R0    // if (R0 == 0) goto END
D=M
@STOP
D;JEQ

@R1    // if (R1 == 0) goto STOP
D=M
@STOP
D;JEQ

@R0
D=M
@R1
D=D-M    // if (R0 < R1) -> limit = R0, incrementor = R1
@ELSE
D;JLT

@R0
D=M
@incrementor
M=D
@R1
D=M
@limit
M=D
@LOOP
0;JMP

(ELSE)
    @R0
    D=M
    @limit
    M=D
    @R1
    D=M
    @incrementor
    M=D

(LOOP)    // while i < limit -> sum = (sum + RAM[R0])
@i
D=M
@limit
D=D-M
@STOP
D;JEQ    // if i >= limit goto STOP

@incrementor
D=M
@sum
M=D+M    // sum = sum + incrementor
@i
M=M+1    // i++
@LOOP
0;JMP

(STOP)    // R2 = sum
@sum
D=M
@R2
M=D

(END)    // infinite loop
    @END
    0;JMP