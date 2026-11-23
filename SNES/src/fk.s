; Fair Knight SNES - for Super Ghouls'n Ghosts Enhanced Arthur v1.2 (GoodLuckTrying)
; Assembled with ca65 (.p816). Each patch site is its own segment; tools/build.py
; generates the ld65 config, checks the original bytes at every site and writes the ROM.
.p816
.smart +
.a8
.i8
.include "fk.inc"
FKB = $380000          ; Fair Knight code bank (banks $20-$3D are blank in the base)

; ---------------------------------------------------------------- hook sites
.segment "S_KB"            ; 01:D7ED  JSL $018848 (hit: load Arthur's hop velocity)
        jsl FKB|fk_kb
.segment "S_CONT"          ; 04:96CC  SBC #$01 (continue counter, BCD) -> unlimited
        sbc #$00
.segment "S_BOOT"          ; 03:EA29  JSL $0CF2C5 (boot, right after the settings load)
        jsl FKB|fk_boot
.segment "S_OPTDRAW"       ; 03:B92E  JSL $049756 (OPTION MODE labels, X=0)
        jsl FKB|fk_optdraw
.segment "S_OPTIN"         ; 03:B939  LDA $02BB / ORA $02BC (OPTION MODE: any input this frame?)
        jsl FKB|fk_optin        ; (the BEQ $B937 after it is kept)
        nop
        nop

.segment "S_CLS"           ; 0C:F291  JSR $F246 / STA $7EAF90 (leaderboard board type)
        jsl FKB|fk_cls
        nop
        nop
        nop

; ---------------------------------------------------------------- FK bank
.segment "FKCODE"
; Knockback: after the game loads the hit-hop velocity, zero the horizontal part.
fk_kb:  jsl $018848
        pha
        lda f:FK_SET
        and #S_KNOCK
        bne :+
        stz $16                 ; Arthur's DP: horizontal speed (24-bit, $16-$18)
        stz $17
        stz $18
:       pla
        rtl

; Leaderboard board type (the base's 0C:F246, reproduced): A = settings bitmask ->
; 0 CLEAN, 1 MINIMAL, 2 ENHANCED, 3 OTHER. Knockback OFF counts like the base's
; "other" settings (bit 7), so such runs are never filed as CLEAN/MINIMAL/ENHANCED.
fk_cls: .a8
        .i8
        pha
        lda f:FK_SET
        and #S_KNOCK
        bne :+
        pla
        ora #$80
        bra @c
:       pla
@c:     cmp #$00
        beq @r0
        cmp #$08
        beq @r2
        sta f:$7EAFA6
        and #$9E
        bne @r3
        lda f:$7EAFA6
        bne @r1
@r3:    lda #3
        bra @s
@r0:    lda #0
        bra @s
@r1:    lda #1
        bra @s
@r2:    lda #2
@s:     sta f:$7EAF90
        rtl

; Boot: first run with no 'FK' signature -> apply the KNIGHT preset to everything.
fk_boot:
        jsl $0CF2C5
        php
        phb
        phk
        plb
        sep #$30
        lda f:FK_SIG
        cmp #$46
        bne @new
        lda f:FK_SIG+1
        cmp #$4B
        beq @ok
@new:   lda #0
        sta f:FK_PRE
        jsr apply_preset
        lda #$46
        sta f:FK_SIG
        lda #$4B
        sta f:FK_SIG+1
@ok:    plb
        plp
        rtl

; OPTION MODE: draw the original labels, then our hint line.
fk_optdraw:
        jsl $049756
        php
        phb
        phk
        plb
        rep #$10
        sep #$20
        lda #0
        sta f:FK_ACT            ; (SRAM: never left set by a reset)
        ldx #HINT_ROW*64+HINT_COL*2
        ldy #s_hint
        lda #ATR_LABEL
        jsr puts
        inc $0323               ; request the tilemap upload (DB=$38: $0000-$1FFF is WRAM)
        plb
        plp
        rtl

; OPTION MODE input, every frame with a new button press. While the FAIR KNIGHT page is
; open it eats the input (A = 0, so the game's BEQ loops back to its frame wait) - the
; option object only yields at its top level, so the page runs as a state machine.
fk_optin:
        .a8
        .i8
        lda f:FK_ACT
        bne @page
        lda f:$7E02BB
        bit #$40                ; X: open the page
        beq @no
        jsr page_open
        lda #0
        rtl
@page:  jsr page_input          ; A = 0 stay, 1 = closed (then let the game redraw its values)
        rtl
@no:    lda f:$7E02BB
        ora f:$7E02BC
        rtl

.include "page.s"
