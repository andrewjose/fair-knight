; Jump horizontal step, three sites: rise ($DE40) and peak ($DE86) use speed $0C, fall ($DEC9) speed $06.
; Original at each: JSR $DF5D / BCS +3 / JSR $DB82 (or $E286). Now a far call to the AIR handler.
.include "fk.inc"
.segment "AIRRISE"
        ldy #FKID_AIR12
        jsr FAR
        nop
        nop
        nop
.segment "AIRPEAK"
        ldy #FKID_AIR12
        jsr FAR
        nop
        nop
        nop
.segment "AIRFALL"
        ldy #FKID_AIR6
        jsr FAR
        nop
        nop
        nop
