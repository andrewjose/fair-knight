; Hidden items (object type $11, handler bank 4 $BB8C). Two 5-byte far calls replace original code:
;  SPARKSITE ($BB8C, 8 bytes): "LDA #$49 / STA $0522,X / JSR $F346" (invisible while waiting)
;      -> FK id 9 does that, or shows a sparkle (SECRETS = MAP+SPARKLES)
;  FOUNDSITE ($BBB9, 17 bytes): the touch-accepted path. Original:
;      LDA $061D,X / CMP #5 / BNE $BBCA / LDA $04F0 / AND #$20 / BNE $BBCA / JMP $F708
;      -> FK id 10 records the item as found and returns carry = (armor item while Arthur has armor)
.include "fk.inc"
.segment "SPARKSITE"
        ldy #FKID_SPARK
        jsr FAR
        nop
        nop
        nop
.segment "FOUNDSITE"
        ldy #FKID_SFOUND
        jsr FAR
        bcc @reveal
        jmp $F708
@reveal:
        nop                  ; falls through to $BBCA (LDA #$12 / STA $0631,X: reveal)
        nop
        nop
        nop
        nop
        nop
        nop
