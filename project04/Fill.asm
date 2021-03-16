// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

PSEUDO CODE
(LOOP)
    if RAM[KBD] == 0:
        fill = 0
    else:
        fill = -1
    for (i=0; i<256; i++):
        RAM[SCREEN + 32*i] = fill 
    goto LOOP

// fill = 0
// i = 0
// m = 256
// j = 0
// n = 512
// addr = SCREEN + 32*i

(START)
    @i
    M=0    // i=0
    @256
    D=A
    @m
    M=D    // m=256
    @SCREEN
    D=A
    @addr
    M=D    // addr = screen base address (16384)

    @KBD
    D=M    // read RAM[KBD]
    @BLACK
    D;JNE    // if RAM[KBD] != 0 goto BLACK

(WHITE)
    @fill
    M=0    // RAM[fill] = 0
    @LOOP
    0;JMP    // goto LOOP

(BLACK)
    @fill
    M=-1    // RAM[fill] = -1

(LOOP)    
    @i
    D=M
    @m
    D=D-M
    @START
    D;JEQ    // if i==m goto START

    @fill
    D=M
    @addr
    A=M     // select pixel at start of selected row
    M=D    // RAM[addr] = RAM[fill]

    @i
    M=M+1    // i++
    @32
    D=A
    @addr
    M=D+M    // addr += 32
    @LOOP
    0;JMP
