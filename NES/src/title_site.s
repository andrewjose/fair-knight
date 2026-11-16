; Title loop, $C4A5-$C4CD (41 bytes) rewritten.
; - Per-tick title logic (Select cursor over 4 rows incl. OPTIONS, OPTIONS text) runs in bank 2 (FK id 1).
; - optgate: reached from the Start handler at $C458 (after Start is released). Cursor row 3 = OPTIONS:
;   clear the screen, then run the options screen one tick at a time (FK id 3) until it asks to leave,
;   then re-run title init at $C3DC (the same re-entry the attract demo uses).
.include "fk.inc"
.export optgate
.segment "TITLE"
        ldy #FKID_TITLE
        jsr FAR
        jmp $C4CE            ; rest of the original title tick (yield, demo timer)
optgate:
        lda $A3
        cmp #3
        beq @opt
        jmp $C53B            ; original: start/continue the game
@opt:   jsr $C62C            ; clear screen (rendering off, nametables, scroll, OAM)
@loop:  jsr $C336            ; yield one tick
        ldy #FKID_OPT
        jsr FAR              ; options screen tick; carry set = leave
        bcc @loop
        jmp $C3DC            ; back to the title screen
