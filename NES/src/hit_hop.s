; Arthur's hit hop ($E229-$E285 rewritten, same behaviour when knockback is on).
; Original: three separate loops (rise / peak / fall), each doing WALLCHK + move.
; New: rise loop + one combined peak/fall loop, and one shared knockback step that
; checks the KNOCKBACK option first. Saves ~10 bytes of the fixed bank.
.include "fk.inc"
.segment "HITHOP"
rise:   jsr kb12
        jsr HOP_UP
        jsr YIELD
        dec $0607,x
        bne rise
air:    jsr LANDCHK
        bcc @up
        jmp LANDED           ; landed (orig: JSR+RTS / JMP)
@up:    lda $0509,x
        cmp #$E0
        bcs done             ; off the top of the screen
        lda $0607,x
        cmp #$07
        bcs @fall
        jsr kb12             ; peak phase, steps 0-6
        jsr HOP_PEAK
        jsr YIELD
        inc $0607,x
        jmp air
@fall:  jsr kb6              ; falling phase
        jsr HOP_DOWN
        jsr YIELD
        jmp air
; knockback step: speed $0C (rise/peak) or $06 (fall), as in the original
kb12:   lda #$0C
        .byte $2C            ; BIT abs opcode: swallows the next LDA #
kb6:    lda #$06
        bit FK_SET
        bpl done             ; KNOCKBACK off -> no backward motion
        pha
        jsr WALLCHK
        pla
        bcs done             ; wall behind -> no motion (original)
        jmp $DB84            ; = JSR ADDVEL / JMP POSFIX
done:   rts
