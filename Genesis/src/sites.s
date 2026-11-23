| Fair Knight (Genesis) - patch sites in the original ROM. Each section is placed at its address by build.py.
        .include "fk.inc"
        .section .s8ba6,"ax"            | hit handler: hop table load (8 bytes)
        jsr     fk_kbtab
        nop
        .section .s8cbc,"ax"            | landing: mercy timer (6 bytes)
        jsr     fk_mercy
        .section .s2408,"ax"            | OPTION screen loop: "move #$2300,sr / bsr $2440" (8 bytes)
        jsr     fk_opt
        nop
        .section .s1b600,"ax"           | weapon item touched: "move.b 11(a1),d0 / jmp $13566" (10 bytes)
        jmp     fk_wdrop
        nop
        nop
        .section .s1ab1c,"ax"           | item landing: random weapon roll (6 bytes)
        jmp     fk_wpick
        .section .s8ac6,"ax"            | airborne routine: "cmpi.l #$1219A,$24(a1)" (8 bytes)
        jsr     fk_air
        nop
        .section .s8f7c,"ax"            | ladder top-out (Up held): "move.l #$8596,$334C(a5)" (8 bytes)
        jsr     fk_ladder
        nop
        .section .s8f20,"ax"            | ladder top-out (other path): same instruction (8 bytes)
        jsr     fk_ladder
        nop
