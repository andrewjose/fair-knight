; Mercy-invincibility tick ($E3B9-$E3DB rewritten, 35 -> 34 bytes).
; Counter $0647,x counts Arthur ticks since the hit; invincibility (bit $40 of $04F0,x)
; ends when it reaches 30. With MERCY = LONG the counter is halved before the compare (60 ticks).
.include "fk.inc"
.segment "MERCY"
        jsr $F2FB            ; bit $40 (invincible) set?
        beq @ret
        inc $0647,x
        lda $0647,x
        bit FK_SET
        bvs @cmp             ; original length
        lsr a
@cmp:   cmp #$1E
        bcc @flick
        jmp $F342            ; clear invincible bit
@flick: asl $04F0,x          ; flicker: bit 7 of $04F0,x = bit 0 of the counter
        lda $0647,x          ; (orig: JSR $F346 / ROR / ROR / AND / ORA / STA)
        lsr a
        ror $04F0,x
@ret:   rts
