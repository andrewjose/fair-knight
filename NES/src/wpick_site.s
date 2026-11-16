; Item pickup, weapon branch (bank 4, $BA63-$BA76): handled in bank 2.
.include "fk.inc"
.segment "WPICK"
        ldy #FKID_WPICK
        jsr FAR
        bcc @keep
        jmp $BB27            ; original: destroy item object
@keep:  jmp $BB2A            ; keep running the item (now the dropped weapon)
