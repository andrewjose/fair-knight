; Once-per-second hook in the stage timer ($D3AD, reached right after the timer digits change).
; Original: LDA $06FC. Now JSR to a 7-byte stub in fixed-bank padding ($E562) that far-calls
; FK id 7 and then performs the original LDA (A and flags as before; Y is free here).
.include "fk.inc"
.segment "SECCALL"
        jsr secstub
.segment "SECSTUB"
secstub:
        jsr FAR_SEC
        lda $06FC
        rts
.segment "FARSEC"
        ldy #FKID_SEC
        jmp FAR
