; Title init ($C43B-$C44A): cursor setup routed through FK so it starts on CONTINUE after a game over.
.include "fk.inc"
.segment "TCUR"
.org $C43B
        ldy #FKID_TCUR
        jsr FAR
        .res 11, $EA
