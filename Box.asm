// Hack screen-fill program.
// Configure K below before submission: K = 0 in this template.
// The box begins at row K, is 20 rows tall, and is 16 pixels (one word) wide.

(MAIN)
    @KBD
    D=M
    @CLEAR
    D;JEQ

    // addr = SCREEN + 32*K = SCREEN (K is 0 in this template)
    @SCREEN
    D=A
    @addr
    M=D
    @20
    D=A
    @rows
    M=D
(DRAWROW)
    @addr
    A=M
    M=-1
    // Move from this one-word-wide box to the next screen row.
    @32
    D=A
    @addr
    M=D+M
    @rows
    MD=M-1
    @DRAWROW
    D;JGT
    @MAIN
    0;JMP

(CLEAR)
    // addr = SCREEN + 32*K = SCREEN (K is 0 in this template)
    @SCREEN
    D=A
    @addr
    M=D
    @20
    D=A
    @rows
    M=D
(CLEARROW)
    @addr
    A=M
    M=0
    @32
    D=A
    @addr
    M=D+M
    @rows
    MD=M-1
    @CLEARROW
    D;JGT
    @MAIN
    0;JMP
