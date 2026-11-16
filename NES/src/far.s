; Far call into the Fair Knight bank. Lives in the fixed bank's end-of-bank padding ($FFE8, 13 bytes)
; and a 7-byte padding gap at $DA6A. Bank switching mirrors the game: write $C7 first, then the
; mapper (bus-conflict table at $C000+n), so an NMI in between restores the right bank.
.include "fk.inc"
.import fk_dispatch
.segment "FAR"
        lda CUR_BANK
        pha                  ; caller's bank
        lda #FK_BANK
        sta CUR_BANK
        sta $C000+FK_BANK
        jmp fk_dispatch
.segment "FARTAIL"
        sty CUR_BANK         ; Y = caller's bank (set by fk_dispatch)
        tya
        sta $C000,y
        rts
