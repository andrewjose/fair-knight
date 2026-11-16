; READY screen ($C971): after the lives digits are queued, the original turns rendering on
; (JSR $F17A), sets the 90-tick wait ($22/$23 = $5A/$00) and yields (JSR $C313).
; FK id 8 queues the secrets summary and does the first two; the yield stays here.
.include "fk.inc"
.segment "READYSITE"
        ldy #FKID_READY
        jsr FAR
        jsr $C313
        nop
        nop
        nop
        nop
        nop
        nop
