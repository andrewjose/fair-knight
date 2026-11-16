; Fair Knight code in PRG bank 2 (free padding from $89D1).
.include "fk.inc"
.segment "BANK2"
.export fk_dispatch
fk_dispatch:
        jsr @go
        pla                  ; caller's bank pushed by FAR
        tay
        jmp FAR_TAIL
@go:    lda fk_hi,y
        pha
        lda fk_lo,y
        pha
        rts
fk_lo:  .byte <(wpick-1), <(title-1), <(tcur-1), <(opt-1), <(ladder-1), <(air12-1), <(air6-1), <(egsec-1), <(ready-1), <(spark-1), <(sfound-1), <(fshit-1)
fk_hi:  .byte >(wpick-1), >(title-1), >(tcur-1), >(opt-1), >(ladder-1), >(air12-1), >(air6-1), >(egsec-1), >(ready-1), >(spark-1), >(sfound-1), >(fshit-1)
.import fshit

; ---- WEAPON DROP -------------------------------------------------------
; Called from the item-pickup code (bank 4, $BA63) with X = item object slot.
; Returns carry set = destroy the item (original), clear = keep it (it now holds the old weapon).
wpick:  lda FK_SET
        and #FKS_WDROP
        bne @orig
        lda $053A            ; current weapon (HUD weapon sprite id)
        ldy #4
@find:  cmp wanim,y
        beq @swap
        dey
        bpl @find
@orig:  jsr take
        sec
        rts
@swap:  lda wkind,y
        pha
        jsr take             ; give Arthur the new weapon
        pla
        sta $061D,x          ; item now shows the old weapon
        lda #0
        sta $0607,x
        lda $05AF            ; always drop 24 px back toward the start of the stage (left),
        sec                  ; whichever way Arthur faces (Andrew, v0.5.1)
        sbc #24
        sta $05AF,x
        lda $0583
        sbc #0
        sta $0583,x
        clc
        rts
take:   ldy $BA              ; original pickup ($BA63-$BA73)
        lda $0522,x
        sta $00C5,y
        sta $053A
        lda $053B,x
        sta $0553
        rts
; weapon sprite id -> item kind ($061D) for: torch, axe, dagger, cross, lance
wanim:  .byte $44,$36,$42,$4F,$40
wkind:  .byte 6,7,8,9,10

; ---- shared helpers ------------------------------------------------------
; edge: FK_RET = buttons newly pressed since last call, FK_TMP = buttons now
edge:   lda FK_TMP
        eor #$FF
        and PAD
        sta FK_RET
        lda PAD
        sta FK_TMP
        rts
; prt: queue one nametable row write. In: $25:$24 = PPU address, $26/$27 = source, A = length.
prt:    sta $23
        lda #1
        sta $22
        jmp PPU_PRINT
; setsrc: $26/$27 = (ptr table lo/hi at Y). Caller loads A=lo, X=hi.
.macro SRC lo, hi
        lda lo
        sta $26
        lda hi
        sta $27
.endmacro
.macro AT addr
        lda #>(addr)
        sta $25
        lda #<(addr)
        sta $24
.endmacro

; ---- TITLE tick (FK id 1, from $C4A5) --------------------------------------
; Replaces the original Select handling ($C4A5-$C4CD): the cursor now has a 4th row, OPTIONS
; (cursor sprite Y $C2, nametable row 24). Also prints "OPTIONS" and resets the options-screen state.
title:  jsr edge
        lda #0
        sta FK_CUR
        sta FK_JOB
        lda #$FF
        sta FK_OCUR
        AT $230D             ; row 24, column 13, under CONTINUE
        SRC #<s_options, #>s_options
        lda #7
        jsr prt
        lda PAD              ; original Select repeat logic, cursor rows $92/$A2/$B2/$C2
        and #$20
        bne @held
        lda #$01
        sta $88
        rts
@held:  dec $88
        bne @r
        lda #$0A
        sta $88
        lda $0509
        clc
        adc #$10
        inc $A3
        ldy $A3              ; v0.5.3: skip the CONTINUE row while there is nothing to continue
        cpy #2               ; ($BB = 0: the original leaves that row blank until a game over)
        bne @chk
        ldy $BB
        bne @chk
        clc                  ; (CPY above set carry)
        adc #$10
        inc $A3
@chk:   cmp #$D2             ; orig #$C2 (3 rows)
        bcc @st
        lda #$00
        sta $A3
        lda #$92
@st:    sta $0509
@r:     rts

; ---- OPTIONS screen tick (FK id 3, from optgate's loop) ---------------------
; Rows: 0 PRESET, 1..NOPT options, NOPT+1 EXIT.
; Each option is a 2- or 3-value field in FK_SET ($07FA) or FK_PRESET ($07FB) (opt_reg 0/1),
; with the field values in opt_val (index 0 = the Fair Knight / KNIGHT value).
; To add an option: append one entry to every opt_* table and a label to lbl_*.
NPRESET  = 3
NOPT     = 8
NROWS    = NOPT+2
ROW_EXIT = NROWS-1
NJOBS    = NROWS+1           ; job 0 = header/help, jobs 1..NROWS = one row each
JOB_DRAWN = $80              ; FK_JOB bit7: whole screen drawn once (input enabled)
JOB_DIRTY = $40              ; FK_JOB bit6: cursor column + description need redrawing
JOB_MASK  = $3F              ; FK_JOB bits0-5: draw job, JOB_IDLE = nothing left to draw
JOB_IDLE  = $3F
ROW0     = 4                 ; nametable row of the PRESET line; rows are 2 apart (v0.5: 4, for 8 options)
optleave:
        sec
        rts
opt:    jsr edge
        bit FK_JOB           ; ignore input until the screen has been drawn once
        bmi :+
        jmp draw
:       lda FK_RET
        and #$10             ; Start: leave
        bne optleave
        lda FK_RET
        and #$80             ; A on EXIT: leave
        beq @noa
        lda FK_CUR
        cmp #ROW_EXIT
        beq optleave
@noa:   lda FK_RET
        and #$08             ; Up
        beq @nou
        dec FK_CUR
        bpl @nou
        lda #ROW_EXIT
        sta FK_CUR
@nou:   lda FK_RET
        and #$04             ; Down
        beq @nod
        inc FK_CUR
        lda FK_CUR
        cmp #NROWS
        bcc @nod
        lda #0
        sta FK_CUR
@nod:   lda FK_RET
        and #$0C             ; Up/Down moved the cursor: redraw cursor + description next
        beq @nodir
        lda FK_JOB
        ora #JOB_DIRTY
        sta FK_JOB
@nodir: lda FK_RET
        and #$20             ; Select: back to the base preset
        beq @nos
        lda FK_PRESET
        and #$03
        jsr setpre
        jmp redraw
@nos:   lda FK_RET
        and #$03             ; Left/Right
        bne :+
        jmp draw
:       ldy FK_CUR
        bne :+
        jmp @pre
:       cpy #ROW_EXIT
        bne :+
        jmp draw
:       jsr curidx           ; X = option, A = value index
        sta FK_RET+0         ; (FK_RET no longer needed this tick) keep idx
        lda FK_TMP
        and #$01             ; Right held -> +1, else (Left) -1
        bne @inc
        dec FK_RET
        bpl @setv
        lda opt_n,x
        sec
        sbc #1
        sta FK_RET
        jmp @setv
@inc:   inc FK_RET
        lda FK_RET
        cmp opt_n,x
        bcc @setv
        lda #0
        sta FK_RET
@setv:  txa                  ; value table index = 3*option + idx
        sta $23
        asl a
        adc $23
        adc FK_RET
        tay
        lda opt_mask,x
        eor #$FF
        sta $23
        lda opt_reg,x
        tax
        lda FK_SET,x
        and $23
        ora opt_val,y
        sta FK_SET,x
        lda FK_PRESET
        ora #FKP_CUSTOM
        sta FK_PRESET
        jmp redraw
@pre:   lda FK_PRESET
        and #$03
        tay
        lda FK_TMP
        lsr a                ; Right -> carry
        bcs @next
        dey
        bpl @setp
        ldy #NPRESET-1
        bne @setp
@next:  iny
        cpy #NPRESET
        bcc @setp
        ldy #0
@setp:  tya
        jsr setpre
redraw: lda FK_JOB           ; a value changed: restart the row refresh, and redraw cursor + description
        and #JOB_DRAWN
        ora #JOB_DIRTY|1
        sta FK_JOB
        jmp draw
; setpre: A = preset index -> FK_SET and FK_PRESET (base preset, CUSTOM cleared, endgame bit)
setpre: tay
        lda presets,y
        sta FK_SET
        tya
        ora presets2,y
        sta FK_PRESET
        rts
; curidx: Y = option row (1..NOPT) -> X = option index, A = current value index (0 if no match)
curidx: tya
        tax
        dex
        txa
        sta $23
        asl a
        adc $23              ; 3*option
        sta $22
        lda opt_reg,x
        tay
        lda FK_SET,y
        and opt_mask,x
        ldy $22
        cmp opt_val,y
        beq @i0
        cmp opt_val+1,y
        beq @i1
        cmp opt_val+2,y
        bne @i0
        lda #2
        rts
@i1:    lda #1
        rts
@i0:    lda #0
        rts

draw:
        lda FK_JOB           ; cursor/description dirty? that is this tick's only PPU work
        and #JOB_DIRTY
        bne @cur
        lda FK_JOB
        and #JOB_MASK
        cmp #JOB_IDLE
        bne @job
        clc                  ; nothing to draw: no PPU writes at all this tick
        rts
@cur:   lda FK_JOB
        and #<~JOB_DIRTY
        sta FK_JOB
        ; cursor: erase the heart at its old row, draw it at the new row (two 1-tile writes;
        ; a full 21-row column here pushed the NMI past vblank and made the screen jump)
        ldy FK_OCUR
        cpy #NROWS
        bcs @nold
        jsr curaddr
        SRC #<s_blank, #>s_blank
        lda #1
        jsr prt
@nold:  ldy FK_CUR
        sty FK_OCUR
        jsr curaddr
        SRC #<s_heart, #>s_heart
        lda #1
        jsr prt
        ; description of the highlighted row (row 24, column 2)
        AT $2302
        ldy FK_CUR
        jsr rowdesc
        lda #28
        jsr prt
        clc
        rts
@job:   ; one piece of the screen per tick (A = job)
        cmp #0
        bne @row
        AT $2046             ; header (row 2)
        SRC #<s_head, #>s_head
        lda #19
        jsr prt
        AT $2342
        SRC #<s_help1, #>s_help1
        lda #28
        jsr prt
        AT $2362
        SRC #<s_help2, #>s_help2
        lda #28
        jsr prt
        jmp @adv
@row:   sec
        sbc #1
        tay                  ; Y = row
        lda rowa_lo,y        ; label at column 4 of nametable row ROW0+2*row
        sta $24
        lda rowa_hi,y
        sta $25
        lda lbl_lo,y
        sta $26
        lda lbl_hi,y
        sta $27
        tya
        pha
        lda #13
        jsr prt              ; label (PPU_PRINT advanced $24/$25 by one row: undo)
        pla
        tay
        lda $24
        sec
        sbc #(32-14)         ; back one row, 14 columns right: value at column 18
        sta $24
        lda $25
        sbc #0
        sta $25
        jsr rowval
        lda #10
        jsr prt
@adv:   lda FK_JOB           ; next job; after the last one: screen drawn (input on), idle, cursor dirty
        and #JOB_MASK
        clc
        adc #1
        cmp #NJOBS
        bcc @keep
        lda #JOB_DRAWN|JOB_DIRTY|JOB_IDLE
        sta FK_JOB
        clc
        rts
@keep:  sta $23              ; (scratch)
        lda FK_JOB
        and #JOB_DRAWN|JOB_DIRTY
        ora $23
        sta FK_JOB
        clc
        rts

; rowval: $26/$27 = value text (10 chars) for row Y
rowval: tya
        bne @o
        jsr preidx
        tay
        lda pn_lo,y
        sta $26
        lda pn_hi,y
        sta $27
        rts
@o:     cpy #ROW_EXIT
        bne :+
        lda #<s_blank
        sta $26
        lda #>s_blank
        sta $27
        rts
:       jsr validx
        lda opt_vnlo,y
        sta $26
        lda opt_vnhi,y
        sta $27
        rts
; rowdesc: $26/$27 = 28-char description for row Y
rowdesc: tya
        bne @o
        jsr preidx
        tay
        lda pd_lo,y
        sta $26
        lda pd_hi,y
        sta $27
        rts
@o:     cpy #ROW_EXIT
        bne :+
        lda #<d_exit
        sta $26
        lda #>d_exit
        sta $27
        rts
:       jsr validx
        lda opt_vdlo,y
        sta $26
        lda opt_vdhi,y
        sta $27
        rts
; preidx: A = preset name index (3 = CUSTOM)
preidx: lda FK_PRESET
        and #FKP_CUSTOM
        beq :+
        lda #NPRESET
        rts
:       lda FK_PRESET
        and #$03
        rts
; validx: Y = option row -> Y = 3*option + current value index
validx: jsr curidx
        clc
        adc $22
        tay
        rts

; curaddr: Y = row -> $25:$24 = nametable address of that row's cursor cell (column 2)
curaddr: lda rowa_lo,y
        sec
        sbc #2
        sta $24
        lda rowa_hi,y
        sbc #0
        sta $25
        rts
rowa_lo:
.repeat NROWS, r
        .byte <($2000+(ROW0+2*r)*32+4)
.endrepeat
rowa_hi:
.repeat NROWS, r
        .byte >($2000+(ROW0+2*r)*32+4)
.endrepeat
; per preset: FK_SET (set bit = original behaviour) and FK_PRESET high bits (bit7 = endgame aid off, bit6 = fair spawns off)
;               KNIGHT LEGEND ORIGINAL
presets:  .byte $00,   $D3,   $FF   ; LEGEND: air FULL (bits3-2 = 00), secrets OFF
presets2: .byte $00,   $80,   $C0
.charmap $20, $FF
.repeat 10, i
  .charmap $30+i, i
.endrepeat
.repeat 26, i
  .charmap $41+i, $0A+i
.endrepeat
CURSOR = $27                 ; grey heart glyph (the font has no arrow; ROM-MAP 3.7)
s_options: .byte "OPTIONS"
s_head:  .byte "FAIR KNIGHT OPTIONS"
s_help1: .byte "UP DOWN MOVE  LEFT RIGHT SET"
s_help2: .byte "SELECT RESET  START EXIT    "
s_blank: .byte "          "
s_heart: .byte CURSOR
; row labels (13 chars): PRESET, options..., EXIT
lbl_lo: .byte <l_pre, <l_kb, <l_mer, <l_wd, <l_lad, <l_air, <l_end, <l_sec, <l_fs, <l_exit
lbl_hi: .byte >l_pre, >l_kb, >l_mer, >l_wd, >l_lad, >l_air, >l_end, >l_sec, >l_fs, >l_exit
l_pre:  .byte "PRESET       "
l_kb:   .byte "KNOCKBACK    "
l_mer:  .byte "MERCY TIME   "
l_wd:   .byte "WEAPON DROP  "
l_lad:  .byte "LADDER SAFETY"
l_air:  .byte "AIR CONTROL  "
l_end:  .byte "ENDGAME AID  "
l_sec:  .byte "SECRETS      "
l_fs:   .byte "FAIR SPAWNS  "
l_exit: .byte "EXIT         "
; preset names / descriptions: KNIGHT, LEGEND, ORIGINAL, CUSTOM
pn_lo:  .byte <p_kn, <p_le, <p_or, <p_cu
pn_hi:  .byte >p_kn, >p_le, >p_or, >p_cu
p_kn:   .byte "KNIGHT    "
p_le:   .byte "LEGEND    "
p_or:   .byte "ORIGINAL  "
p_cu:   .byte "CUSTOM    "
pd_lo:  .byte <pd_kn, <pd_le, <pd_or, <pd_cu
pd_hi:  .byte >pd_kn, >pd_le, >pd_or, >pd_cu
pd_kn:  .byte "FAIR KNIGHT RECOMMENDED     "
pd_le:  .byte "ORIGINAL HITS  AIR CONTROL  "
pd_or:  .byte "PLAYS LIKE THE ORIGINAL GAME"
pd_cu:  .byte "YOUR OWN MIX OF OPTIONS     "
d_exit: .byte "PRESS START OR A TO RETURN  "
;           KNOCKBACK      MERCY        WEAPON DROP   LADDER         AIR CONTROL    ENDGAME AID    SECRETS        FAIR SPAWNS
opt_reg:  .byte 0,             0,           0,            0,             0,             1,             0,             1
opt_mask: .byte FKS_KNOCKBACK, FKS_MERCY,   FKS_WDROP,    FKS_LADDER,    FKS_AIR,       FKP_ENDGAME,   FKS_SECRETS,   FKP_FAIRSP
opt_n:    .byte 2,             2,           2,            2,             3,             2,             3,             2
opt_val:  .byte $00,$80,0,     $00,$40,0,   $00,$20,0,    $00,$10,0,     $00,$04,$0C,   $00,$80,0,     $00,$01,$03,   $00,$40,0
.define VN v_off,v_on,v_off, v_long,v_norm,v_norm, v_on,v_off,v_off, v_on,v_off,v_off, v_full,v_asst,v_off, v_on,v_off,v_off, v_spark,v_map,v_off, v_on,v_off,v_off
.define VD d_kb0,d_kb1,d_kb1, d_me0,d_me1,d_me1, d_wd0,d_wd1,d_wd1, d_la0,d_la1,d_la1, d_ai1,d_ai0,d_ai2, d_en0,d_en1,d_en1, d_se1,d_se0,d_se2, d_fs0,d_fs1,d_fs1
opt_vnlo: .lobytes VN
opt_vnhi: .hibytes VN
opt_vdlo: .lobytes VD
opt_vdhi: .hibytes VD
v_on:   .byte "ON        "
v_off:  .byte "OFF       "
v_norm: .byte "NORMAL    "
v_long: .byte "LONG      "
v_asst: .byte "ASSIST    "
v_full: .byte "FULL      "
v_map:  .byte "MAP       "
v_spark:.byte "SPARKLES  "
d_kb0:  .byte "HITS DO NOT PUSH ARTHUR BACK"
d_kb1:  .byte "HITS KNOCK ARTHUR BACKWARD  "
d_me0:  .byte "LONGER SAFE TIME AFTER A HIT"
d_me1:  .byte "ORIGINAL SAFE TIME AFTER HIT"
d_wd0:  .byte "OLD WEAPON DROPS BEHIND YOU "
d_wd1:  .byte "NEW WEAPON REPLACES THE OLD "
d_la0:  .byte "SAFE MOMENT AT A LADDER TOP "
d_la1:  .byte "ORIGINAL LADDER TOPS        "
d_ai0:  .byte "HOLD BACK TO STOP A JUMP    "
d_ai1:  .byte "STEER FREELY WHILE JUMPING  "
d_ai2:  .byte "ORIGINAL FIXED JUMPS        "
d_en0:  .byte "CROSS WAITS BELOW THE BOSS  "
d_en1:  .byte "FIND THE CROSS YOURSELF     "
d_se0:  .byte "READY SCREEN LISTS SECRETS  "
d_se1:  .byte "SECRETS ALSO SPARKLE IN PLAY"
d_se2:  .byte "SECRETS ARE NOT SHOWN       "
d_fs0:  .byte "NO ENEMIES APPEAR ON ARTHUR "
d_fs1:  .byte "ORIGINAL ENEMY APPEARANCES  "

; ---- TITLE CURSOR: start on CONTINUE when a game can be continued ($BB != 0) ----
tcur:   lda #$1B             ; original init
        sta $0522
        lda #$01
        sta $053B
        sta $88
        lda $BB
        beq @top
        lda #$B2             ; cursor sprite on the CONTINUE row
        sta $0509
        lda #$02
        .byte $2C
@top:   lda #$00
        sta $A3
        rts

; ---- LADDER SAFETY (FK id 4, from $DD90: Arthur steps off a ladder top) -----------
; Runs the two original calls, then (option on) starts a short invincibility using the
; game's own mercy timer: bit $40 of $04F0 and counter $0647 set 12 ticks before the end.
ladder: jsr SNAPY
        jsr LADTOP_ANIM
        lda FK_SET
        and #FKS_LADDER
        bne @r
        lda #30-12           ; mercy ends at 30 (NORMAL) ...
        bit FK_SET
        bvs :+
        lda #60-24           ; ... or 60 (LONG: counter halved before the compare)
:       sta FK_WANT
        lda $04F0,x
        and #$40
        beq @set             ; not invincible yet
        lda $0647,x
        cmp FK_WANT
        bcc @r               ; already invincible for longer: keep it
@set:   lda FK_WANT
        sta $0647,x
        lda $04F0,x
        ora #$40
        sta $04F0,x
@r:     rts

; ---- AIR CONTROL (FK id 5 = rise/peak, speed $0C; id 6 = fall, speed $06) ----------
; Replaces JSR $DF5D / BCS +3 / JSR $DB82|$E286 in the jump loops. X = Arthur.
; $065D,x != 0: moving horizontally; $05F1,x: $04 right / $0C left (also the wall-check side).
; OFF reproduces the original exactly. ASSIST: holding the opposite direction stops the
; sideways motion for the rest of the jump (no reversing). FULL: steer either way; starting or
; reversing goes through a stopped tick and a half-speed tick (lower acceleration than walking).
air12:  lda #$0C
        .byte $2C
air6:   lda #$06
        sta FK_SPD
        lda FK_SET
        and #FKS_AIR
        cmp #FKS_AIR
        beq @orig
        cmp #FKS_AIR_ASSIST  ; v0.5.2: 00 = FULL (KNIGHT default), 04 = ASSIST, 0C = OFF
        bne @full
        lda $065D,x          ; ASSIST
        beq @orig            ; standing jump: as original
        ldy #$02             ; moving right: Left is "back"
        lda $05F1,x
        cmp #$0C
        bne :+
        ldy #$01             ; moving left: Right is "back"
:       tya
        and $CC
        beq @orig
        lda #0               ; brake: no sideways motion for the rest of this jump
        sta $065D,x
        rts
@orig:  jsr JUMPWALL
        bcs @r
@go:    lda FK_SPD
        jsr ADDVEL
        jmp POSFIX
@r:     rts
@full:  lda $CC
        and #$03
        beq @move            ; no direction held: keep the current motion
        cmp #$03
        beq @move
        lsr a                ; Right -> carry
        lda #$04
        bcs :+
        lda #$0C
:       sta FK_WANT
        lda $065D,x
        beq @start
        lda $05F1,x
        cmp FK_WANT
        beq @move
        lda #0               ; reversing: stop this tick
        sta $065D,x
        rts
@start: lda FK_WANT
        sta $05F1,x
        lda #1
        sta $065D,x
        sta FK_AIRH          ; first step at half speed
@move:  lda $065D,x
        beq @r
        jsr WALLCHK          ; wall check on the side we are moving to
        bcs @r
        lda FK_AIRH
        beq @go
        lda #0
        sta FK_AIRH
        lda FK_SPD
        lsr a
        jsr ADDVEL
        jmp POSFIX

; ---- ENDGAME AID (FK id 7, once per second from the stage timer) -----------------
; Rule (bank 7 $D436): clearing stage 6 ($CF = 5) without the cross ($C5,y / $053A = $4F)
; sends you back to section 11 (stage 5). With the option on, a cross item waits on the floor
; below the boss floor (world X EG_X, Y $1BA) whenever Arthur is near it without a cross and
; no cross item exists. It is re-created after a death or continue, never while he holds one.
egsec:  lda FK_PRESET
        bmi @r               ; option off
        lda $CF
        cmp #5
        bne @r
        lda $BD              ; dying / time up
        bne @r
        lda $94              ; attract demo
        bne @r
        lda $053A
        cmp #$4F
        beq @r               ; already holding the cross
        lda $056D            ; Arthur on the boss floor or the floor below it (Y $170-$1BF)
        cmp #1
        bne @r
        lda $0599
        cmp #$70
        bcc @r
        cmp #$C0
        bcs @r
        lda $0583            ; and within ~110 px of the spot, so it is on screen
        beq @p0
        cmp #1
        bne @r
        lda $05AF
        cmp #<(EG_X+110-256)
        bcc @near
@r:     rts
@p0:    lda $05AF
        cmp #EG_X-110
        bcc @r
@near:  ldy #1               ; a cross item already up here?
@lp:    lda $04F0,y
        beq @nx
        lda $0631,y
        cmp #$10
        bne @nx
        lda $061D,y
        cmp #9
        bne @nx
        lda $056D,y          ; only a cross up here counts (a dropped one
        cmp #1               ; lower in the tower may still be loaded)
        beq @r
@nx:    iny
        cpy #$11
        bne @lp
        jsr FREESLOT
        bcs @r
        lda #$10             ; item object
        sta $0631,y
        lda #9               ; cross
        sta $061D,y
        lda #$4F
        sta $0522,y
        lda #0
        sta $0607,y
        sta $0647,y
        sta $05F1,y
        sta $05DB,y
        sta $053B,y
        lda #<EG_X
        sta $05AF,y
        lda #>EG_X
        sta $0583,y
        lda #$BA
        sta $0599,y
        lda #1
        sta $056D,y
        lda #$40
        sta $04F0,y
        rts

; ---- SECRETS ---------------------------------------------------------------
.include "secrets.inc"
SPARK      = $56     ; small spark (hit-spark sprite, loaded in every stage tested)
SPARK_DUCK = $66     ; larger four-point star: duck here
bitm:   .byte $01,$02,$04,$08,$10,$20,$40,$80
; sigchk: clear the found bits once per power-on
sigchk: lda FK_SSIG
        cmp #$A5
        beq @r
        lda #0
        sta FK_SFOUND
        sta FK_SFOUND+1
        sta FK_SFOUND+2
        sta FK_SFOUND+3
        lda #$A5
        sta FK_SSIG
@r:     rts

; FK id 10 (bank 4 $BBB9, X = hidden item): Arthur touched it the right way (ducking if required).
; Mark it found, then return carry = original "armor item while Arthur already has armor" test.
sfound: jsr sigchk
        lda $94
        bne @cond            ; attract demo: don't record
        ldy #0
@lp:    lda sec_s,y
        cmp $C2
        bne @nx
        lda sec_xl,y
        cmp $05AF,x
        bne @nx
        lda sec_xh,y
        cmp $0583,x
        bne @nx
        lda sec_yh,y
        cmp $056D,x
        bne @nx
        tya
        and #7
        sty $22
        tay
        lda bitm,y
        pha
        lda $22
        lsr a
        lsr a
        lsr a
        tay
        pla
        ora FK_SFOUND,y
        sta FK_SFOUND,y
        jmp @cond
@nx:    iny
        cpy #NSEC
        bne @lp
@cond:  lda $061D,x
        cmp #5
        bne @no
        lda $04F0
        and #$20
        bne @no
        sec
        rts
@no:    clc
        rts

; FK id 9 (bank 4 $BB8C, X = hidden item, every tick while it waits).
; Original: invisible (sprite $49, draw bit cleared). SPARKLES: a twinkling spark at the spot,
; the larger star where you must duck, red palette for the harmful time-down item.
spark:  lda FK_SET
        and #FKS_SECRETS
        cmp #FKS_SECRETS_SPARK   ; v0.5.2: 00 = SPARKLES (KNIGHT default), 01 = MAP, 03 = OFF
        bne @orig
        lda $94
        bne @orig
        inc $0607,x
        lda $0607,x
        and #$08
        beq @orig            ; twinkle: hidden half the time
        lda #SPARK
        ldy $04F0,x
        tya
        lsr a                ; bit 0 = duck-only
        lda #SPARK
        bcc :+
        lda #SPARK_DUCK
:       sta $0522,x
        lda #0
        ldy $061D,x
        cpy #12              ; time down
        bne :+
        lda #1
:       sta $053B,x
        lda $04F0,x
        ora #$80
        sta $04F0,x
        rts
@orig:  lda #$49
        sta $0522,x
        jmp $F346

; FK id 8 (READY screen, after the lives digits): secrets summary, then the original
; "rendering on" and the 90-tick wait value. Rows 18-22:
;           HIDDEN ITEMS
;   1 ....  2 .....  3 .......
;   4 ....  5 ....  6 .....        (heart = found, dot = not found yet)
ready:  jsr sigchk
        lda FK_SET
        and #FKS_SECRETS
        cmp #FKS_SECRETS
        beq @out
        AT $224A
        SRC #<s_hid, #>s_hid
        lda #12
        jsr prt
        lda #0
        sta FK_TMP           ; stage
        sta FK_RET           ; item index
        lda #$22
        ldy #$83
        jsr sline
        lda #$22
        ldy #$C3
        jsr sline
@out:   jsr $F17A            ; original: rendering on
        lda #$5A             ; original wait: 90 ticks
        sta $22
        lda #0
        sta $23
        rts
; sline: one line of three stages straight into the PPU queue ($0720+$31; NMI skips it while $4F != 0)
; In: A = PPU address high, Y = low.
sline:  sty $24
        ldy #$FF
        sty $4F
        ldy $31
        sta $0720,y
        iny
        lda $24
        sta $0720,y
        iny
        sty $25              ; position of the length byte
        iny
        lda #3
        sta $26
@st:    ldx FK_TMP
        txa
        clc
        adc #1               ; stage digit
        sta $0720,y
        iny
        lda #$FF
        sta $0720,y
        iny
        lda st_cnt,x
        sta $27
        beq @sp
@sy:    jsr symbol
        sta $0720,y
        iny
        inc FK_RET
        dec $27
        bne @sy
@sp:    lda #$FF
        sta $0720,y
        iny
        sta $0720,y
        iny
        inc FK_TMP
        dec $26
        bne @st
        tya                  ; length = end - (length byte + 1)
        clc
        sbc $25
        ldx $25
        sta $0720,x
        lda #$FF
        sta $0720,y
        sty $31
        lda #0
        sta $4F
        rts
; symbol: A = heart if item FK_RET was found, else dot (Y kept)
symbol: tya
        pha
        lda FK_RET
        and #7
        tax
        lda bitm,x
        sta $22
        lda FK_RET
        lsr a
        lsr a
        lsr a
        tax
        lda FK_SFOUND,x
        and $22
        beq :+
        pla
        tay
        lda #$27             ; heart
        rts
:       pla
        tay
        lda #$26             ; dot
        rts
s_hid:  .byte "HIDDEN ITEMS"
