; Ladder top: Arthur steps off the top of a ladder ($DD90: JSR $E166 / JSR $DC5B / JMP $DB65).
; The two calls move into the FK handler (id 4), which can also start a brief invincibility.
.include "fk.inc"
.segment "LADDER"
        ldy #FKID_LADDER
        jsr FAR
        jmp STAND
        nop
