; Fair Knight v0.5 hook sites for FAIR SPAWNS (see fairspawn.s)
.include "fk.inc"
.import fk_zgen, fk_gen
; bank 2 generator list: $8400 "JSR $8416" (zombie generator) -> zombie cap wrapper
.segment "GEN0"
        jsr fk_zgen
; bank 2 generator list end: $8412 "JSR $8748 / RTS" -> spawn tick (calls $8748 itself)
.segment "GENEND"
        jmp fk_gen
; fixed bank: Arthur's hit check $E014 (was JSR $F2E3 / BEQ / SEC / RTS / CLC / RTS)
.segment "HITCHK"
        ldy #FKID_FSHIT
        jmp FAR
        nop
        nop
        nop
        nop
