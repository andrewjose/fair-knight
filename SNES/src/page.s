; ---------------------------------------------------------------- FAIR KNIGHT page
; Called from the OPTION MODE object (JSR from fk_optin). Runs its own loop, yielding a
; frame with the game's BRK #$00 (the object scheduler resumes after it), until START.
; Text goes into the game's text-layer buffer $7F9000; INC $0323 asks NMI to upload it.
NROWS   = 7
ROW_EXIT = 6
ROW0    = 5             ; first option row on screen (rows 2 apart)
LBLCOL  = 4
VALCOL  = 19
DESCROW = 20
.macro YIELD
        .byte $00,$00   ; BRK #$00: wait one frame
.endmacro

page_open:
        php
        phb
        phk
        plb
        sep #$20
        rep #$10
        lda #1
        sta f:FK_ACT
        lda $02D5               ; main-screen layers: text layer (BG3) only, so the
        sta f:FK_TM             ; ornament frame doesn't cover the page
        lda #$04
        sta $02D5
        lda #0
        sta f:FK_CUR
        jsr clear
        ldx #2*64+6*2
        ldy #s_title
        lda #ATR_TITLE
        jsr puts
        ldx #23*64+3*2
        ldy #s_help1
        lda #ATR_LABEL
        jsr puts
        ldx #24*64+3*2
        ldy #s_help2
        lda #ATR_LABEL
        jsr puts
        jsr draw
        inc $0323
        jsr tick
        plb
        plp
        rts

; one button press on the page. Out: A = 0 (page still open) or 1 (closed)
page_input:
        php
        phb
        phk
        plb
        sep #$20
        rep #$10
        lda PAD_HI
        bit #$10                ; START: back to OPTION MODE
        bne @exit
        bit #$08                ; Up
        beq @nu
        lda f:FK_CUR
        dec a
        bpl :+
        lda #NROWS-1
:       sta f:FK_CUR
        bra @moved
@nu:    bit #$24                ; Down / Select
        beq @nd
        lda f:FK_CUR
        inc a
        cmp #NROWS
        bne :+
        lda #0
:       sta f:FK_CUR
        bra @moved
@nd:    bit #$03                ; Left / Right
        beq @nl
        and #$01                ; 1 = Right
        jsr change
        bra @moved
@nl:    lda PAD_LO
        bit #$80                ; A: back to the chosen preset
        beq @stay
        jsr apply_preset
@moved: jsr draw
        inc $0323
        jsr tick
@stay:  lda #0
        sta PAD_LO
        sta PAD_HI
        plb
        plp
        lda #0
        rts
@exit:  lda f:FK_TM
        sta $02D5
        lda #0
        sta f:FK_ACT
        sta PAD_LO
        sta PAD_HI
        jsr clear
        sep #$30
        .i8
        ldx #0
        lda #$00                ; its pointer table ($DA9E) is read with DB = $00
        pha
        plb
        jsl $049756             ; the game's own OPTION MODE labels
        phk
        plb
        rep #$10
        .i16
        ldx #HINT_ROW*64+HINT_COL*2
        ldy #s_hint
        lda #ATR_LABEL
        jsr puts
        inc $0323
        jsr tick
        plb
        plp
        lda #1                  ; let the game run its value redraw ($BA29) with no input
        rts

        .a8
        .i16
tick:   php
        sep #$30
        lda #$37
        jsl $018053             ; menu cursor sound
        plp
        rts

; A = 1 for Right, 0 for Left; changes the row under the cursor
        .a8
        .i16
change: sta f:FK_T
        lda f:FK_CUR
        bne @c1
        lda f:FK_PRE            ; PRESET: cycle KNIGHT LEGEND ORIGINAL and apply
        jsr step3
        sta f:FK_PRE
        jmp apply_preset
@c1:    cmp #1
        bne @c2
        lda f:FK_SET
        eor #S_KNOCK
        sta f:FK_SET
        rts
@c2:    cmp #5
        beq @weap
        cmp #6
        beq @x
        rep #$20
        and #$00FF
        tax                     ; rows 2-4 toggle a base byte
        sep #$20
        lda rowvar-2,x
        rep #$20
        and #$00FF
        tax
        sep #$20
        lda B_CHEST,x
        eor #$01
        and #$01
        sta B_CHEST,x
        jmp save_base
@weap:  lda B_WEAP
        jsr step3
        sta B_WEAP
        jmp save_base
@x:     rts
; A = 0..2 -> A +/- 1 mod 3 (FK_T = 1: up)
        .a8
        .i16
step3:  pha
        lda f:FK_T
        beq @dn
        pla
        inc a
        cmp #3
        bcc @r
        lda #0
        rts
@dn:    pla
        dec a
        bpl @r
        lda #2
@r:     rts
rowvar: .byte B_CHEST-B_CHEST, B_ENH-B_CHEST, B_ARMOR-B_CHEST

; Apply preset FK_PRE (0-2) to the base's settings and ours, then save the base's SRAM.
        .a8
        .i16
apply_preset:
        php
        sep #$20
        rep #$10
        jsr pre_y
        ldx #0
@l:     lda pre_tab,y
        cmp #$FF                ; $FF: this preset leaves the setting alone
        beq @n
        sta B_CHEST,x
@n:     iny
        inx
        cpx #7
        bne @l
        lda pre_tab,y
        sta f:FK_SET
        jsr save_base
        plp
        rts
; Y = FK_PRE * 8 (FK_PRE clamped to 0-2)
        .a8
        .i16
pre_y:  lda f:FK_PRE
        cmp #3
        bcc :+
        lda #0
        sta f:FK_PRE
:       rep #$20
        and #$00FF
        asl a
        asl a
        asl a
        tay
        sep #$20
        rts
; A = FK_PRE if every setting matches that preset, else 3 (CUSTOM)
        .a8
        .i16
match_preset:
        php
        sep #$20
        rep #$10
        jsr pre_y
        ldx #0
@l:     lda pre_tab,y
        cmp #$FF
        beq @n
        cmp B_CHEST,x
        bne @c
@n:     iny
        inx
        cpx #7
        bne @l
        lda pre_tab,y
        cmp f:FK_SET
        bne @c
        plp
        lda f:FK_PRE
        rts
@c:     plp
        lda #3
        rts
; the base's own save (03:FEE7) for its seven secret settings: 'SG', values, sum
        .a8
        .i16
save_base:
        php
        sep #$20
        rep #$10
        lda #$53
        sta f:$700000
        lda #$47
        sta f:$700001
        lda #0
        sta f:FK_T
        ldx #6
@l:     lda B_CHEST,x
        cpx #4
        bcc @m1
        cpx #6
        bcc @m3
@m1:    and #$01
        bra @s
@m3:    and #$03
@s:     sta f:$700002,x
        clc
        adc f:FK_T
        sta f:FK_T
        dex
        bpl @l
        lda f:FK_T
        sta f:$700009
        plp
        rts

; X = buffer offset, Y = string ($FF-terminated, bank $38), A = attribute. Y ends past the $FF.
        .a8
        .i16
puts:   sta f:FK_ATR
@l:     lda a:0,y
        iny
        cmp #$FF
        beq @d
        sta f:TILEBUF,x
        lda f:FK_ATR
        sta f:TILEBUF+1,x
        inx
        inx
        bra @l
@d:     rts
        .a8
        .i16
clear:  ldx #0
@l:     lda #$45
        sta f:TILEBUF,x
        lda #0
        sta f:TILEBUF+1,x
        inx
        inx
        cpx #28*64
        bne @l
        rts

; A = row -> A = value index for that row
        .a8
        .i16
row_v:  cmp #0
        bne :+
        jmp match_preset
:       cmp #1
        bne :+
        lda f:FK_SET
        and #S_KNOCK
        rts
:       cmp #5
        bne :+
        lda B_WEAP
        cmp #3
        bcc @r
        lda #0
@r:     rts
:       cmp #6
        bne :+
        lda #0
        rts
:       rep #$20
        and #$00FF
        tax
        sep #$20
        lda rowvar-2,x
        rep #$20
        and #$00FF
        tax
        sep #$20
        lda B_CHEST,x
        and #$01
        rts

; draw every row, the highlighted row's value and its two-line description
        .a8
        .i16
draw:   lda #0
        sta f:FK_ROW            ; row counter
@row:   lda f:FK_ROW
        rep #$20
        and #$00FF
        asl a
        tax
        lda rowoff,x
        sta f:FK_TMP            ; screen offset of this row
        lda lbltab,x
        tay
        sep #$20
        ldx #0
        lda f:FK_ROW
        cmp f:FK_CUR
        bne :+
        ldx #1
:       lda atr_l,x
        pha
        rep #$20
        lda f:FK_TMP
        tax
        sep #$20
        pla
        jsr puts
        ; value
        lda f:FK_ROW
        jsr row_v               ; A = value index
        rep #$20
        and #$00FF
        asl a
        sta f:FK_TMP2
        lda f:FK_ROW
        and #$00FF
        asl a
        asl a
        asl a                   ; row * 8 (4 words per row)
        clc
        adc f:FK_TMP2
        tax
        lda nametab,x
        tay
        lda f:FK_TMP
        clc
        adc #(VALCOL-LBLCOL)*2
        tax
        sep #$20
        lda #ATR_VAL
        pha
        lda f:FK_ROW
        cmp f:FK_CUR
        bne :+
        pla
        lda #ATR_SEL
        pha
:       pla
        jsr puts
        ; description of the highlighted row
        lda f:FK_ROW
        cmp f:FK_CUR
        bne @nx
        rep #$20
        lda f:FK_TMP2
        sta f:FK_TMP2
        lda f:FK_ROW
        and #$00FF
        asl a
        asl a
        asl a
        clc
        adc f:FK_TMP2
        tax
        lda desctab,x
        tay
        ldx #DESCROW*64+3*2
        sep #$20
        lda #ATR_VAL
        jsr puts
        ldx #(DESCROW+1)*64+3*2
        lda #ATR_VAL
        jsr puts
@nx:    lda f:FK_ROW
        inc a
        sta f:FK_ROW
        cmp #NROWS
        beq :+
        jmp @row
:       rts
atr_l:  .byte ATR_LABEL, ATR_SEL

.include "pagedata.s"
