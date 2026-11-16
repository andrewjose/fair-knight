; Start handler tail ($C458): JMP $C53B -> JMP optgate (title_site.s), which forwards to $C53B
; unless the cursor is on OPTIONS.
.include "fk.inc"
.import optgate
.segment "STARTGO"
        jmp optgate
