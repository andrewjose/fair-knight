; =====================================================================================
; Fair Knight for Ghosts'n Goblins (GBC, USA/Europe)  -  source for tools/build.py
; Assembled by tools/sm83asm.py (syntax = what tools/sm83dis.py prints).
; Base ROM MD5 9b846e9a4eb6b80cdbc8e6c82f2b9e9e (MBC5, 1 MiB). The game's default ROM bank
; is 1; every bank holds its own number at $7FFF and the interrupt handlers restore the
; current bank from there, so code in bank FKB is interrupt-safe.
; =====================================================================================
FKB      = $20          ; Fair Knight code/data bank (banks $13-$3C are empty in the original)

; ---- WRAM (bank 1 of $D000-$DFFF; the game never switches SVBK and never touches $D7D2-$DFFF)
FK_SIG   = $DF00        ; 'F','K' once initialised (WRAM is random at power-on, not cleared)
FK_SET   = $DF02        ; settings, 1 = original behaviour (power-on 0 = KNIGHT)
FK_SET2  = $DF03        ; more settings (secrets, later)
FK_PRE   = $DF04        ; preset: 0 KNIGHT, 1 LEGEND, 2 ORIGINAL; bit7 = CUSTOM
FK_A     = $DF05        ; trampoline scratch
FK_BANK  = $DF06        ; caller's ROM bank (trampoline)
FK_CUR   = $DF07        ; page cursor row
FK_PAD   = $DF08        ; previous joypad (edge detect)
FK_T     = $DF09        ; scratch (2 bytes)
FK_STG   = $DF0B        ; stage index the found list belongs to ($FF = none)
FK_FC    = $DF0C        ; frame counter (sparkle twinkle)
FK_CAMT  = $DF0D        ; v0.10 camera: current target screen X for Arthur
FK_CAMP  = $DF0E        ; v0.11 camera: easing parity counter
FK_FND   = $DF10        ; found secrets, 64 bits ($DF10-$DF17), bit id = (param - $79CD) / 10
FK_MS    = $DF20        ; two 1-sprite metasprites in WRAM (normal, harmful): count, dy, dx, tile, attr
SPK_T    = $6F          ; sparkle tile: sprite tile $6F (VRAM bank 0) is blank in every stage; we draw ours there
PAL_N    = $07          ; OBJ palettes: 7 = white/green (normal), 6 = red (harmful)
PAL_H    = $06

; FK_SET bits (1 = original)
S_KNOCK  = $01          ; knockback ON
S_MERCY  = $02          ; mercy NORMAL
S_WDROP  = $04          ; weapon drop OFF
S_LADDER = $08          ; ladder safety OFF
S_AIR    = $10          ; air control OFF (original fixed arc)
S_SECR   = $20          ; secret markers OFF
S_ENDG   = $40          ; endgame aid OFF
S_SPAWN  = $80          ; fair spawns OFF
; FK_SET2 bits (1 = original): bits 1-0 = SECRETS (0 SPARKLES, 1 MAP, 3 OFF)
S2_QS    = $04          ; v0.10 quick stand OFF (crouch held while Left/Right held)
CAM_R    = 54           ; AHEAD target screen X facing right / left
CAM_L    = 80           ; v0.11: walking left eases back to the original centre
S2_CAM   = $08          ; v0.10 camera CENTER (original: Arthur held at screen X $50)

; ---- game routines / RAM (bank 0 unless noted)
PRINT    = $0841        ; hl=text d=col e=row b=attr c=len  (text in the currently mapped bank)
OAMDMA   = $FF80
READPAD  = $006B        ; -> [$C0E0]: bit0 A,1 B,2 Select,3 Start,4 Right,5 Left,6 Up,7 Down
CURSOR   = $101B        ; draw menu cursor sprite: hl = table of (x,y) pairs, index [$C1E9]
SFX      = $0213        ; menu "tick" sound
OPTCUR   = $C1E9        ; options-screen cursor
PAD      = $C0E0

; =====================================================================================
; Bank 0 free space $3DF6-$3FFF: trampolines and bank-0 helpers
; =====================================================================================
.org 0:$3DF7                    ; v0.11: $3DF6 stays $FF - it terminates the game's last animation list (2E 2F at $3DF4)
PRE:    ld [FK_A], a
        ld a, [$7FFF]
        ld [FK_BANK], a
        ld a, FKB
        ld [$2100], a
        ld a, [FK_A]
        ret
POST:   ld [FK_A], a            ; (ld never changes flags: handler flags survive)
        ld a, [FK_BANK]
        ld [$2100], a
        ld a, [FK_A]
        ret
T_init: call PRE
        call h_init
        jp POST
T_down: call PRE
        call h_down
        jp POST
T_up:   call PRE
        call h_up
        jp POST
T_sel:  call PRE
        call h_sel
        jp POST
T_lbl:  call PRINT               ; the original SOUNDFX label (bank $3E text, still mapped)
        call PRE
        call h_lbl
        jp POST
T_kbv:  call PRE
        call h_kbv
        jp POST
T_kbm:  call PRE
        call h_kbm
        jp POST
T_mer:  call PRE
        call h_mer
        jp POST
; options-screen cursor table, 3 rows (x, y): MUSIC, SOUNDFX, FAIR KNIGHT
OPTTAB: .db $20, $66, $20, $6E, $20, $76
; LCD off (wait for vblank line $91), as the game does at $01F1
LCDOFF: di                      ; the game's VBlank handler can outlast LY=$91, so mask it
@w:     ldh a, [$FF44]
        cp $90
        jr c, @w
        ldh a, [$FF40]
        and $7F
        ldh [$FF40], a
        ei
        ret
; redraw the title map + options rows (bank $3E code), then come back to bank FKB
REDRAW: ld a, $3E
        ld [$2100], a
        call $41C0              ; full 20x18 title map (logo) from bank $3E data
        call $432F              ; clear rows 9-17
        call $429C              ; MUSIC / SOUNDFX labels (+ FAIR KNIGHT via T_lbl)
        call $42B9              ; ON/OFF values
        ld a, FKB
        ld [$2100], a
        ret
; ---- weapon drop (runs in bank 1 context: item collect handler, HRAM = the item) -----
h_wpick:ld a, [FK_SET]
        and S_WDROP
        jr nz, @orig
        ld a, [$C0B6]           ; current weapon
        ld b, a
        ldh a, [$FFA9]          ; weapon in this item
        cp b
        jr z, @orig
        call $280B              ; a free object slot? (carry = none)
        jr c, @orig
        ld a, [$C0B6]
        ld c, a
        add a, a
        add a, a
        add a, a
        sub c                   ; 7 * old weapon
        add a, $A7              ; bank 1 weapon item descriptors at $49A7 (7 bytes each)
        ld e, a
        ld a, $49
        adc a, $00
        ld d, a
        ld a, [$C5AC]           ; Arthur X - 24 px  (X = hi*16 px + lo/16 px)
        sub $80
        ldh [$FF92], a
        ld a, [$C5AA]
        sbc a, $01
        jr nc, @x
        xor a                   ; clamp at the stage start
        ldh [$FF92], a
@x:     ldh [$FF90], a
        call $45D0              ; the game's own item spawner (bank 1); hl = new slot
        ld de, $0007
        add hl, de
        ldh a, [$FF91]          ; same height as the item being collected (it lies on the ground)
        ld [hl+], a
        inc hl
        ldh a, [$FF93]
        ld [hl], a
@orig:  ldh a, [$FFA9]          ; (the replaced instructions)
        jp $06E7
; ---- air control: Left/Right in the air set the horizontal speed (jump height unchanged) --
h_airf: ldh a, [$FFA6]          ; falling (state 7): no steering while in hit recoil / mercy
        and $20
        jr nz, h_air__o
h_air:  ld a, [FK_SET]          ; jumping (state 3)
        and S_AIR
        jr nz, @o
        ld a, [PAD]
        bit 5, a
        jr z, @r
        ld a, $F0               ; walking speed left
        jr @s
@r:     bit 4, a
        jr z, @o
        ld a, $10               ; walking speed right
@s:     ldh [$FFA7], a
@o:     ld a, [PAD]             ; (the replaced instruction)
        ret
; ---- ladder safety: stepping off the top of a ladder gives 42 frames (0.7 s) of mercy ----
h_lad:  ld a, $01               ; (replaced) state 1 = standing
        ldh [$FFA5], a
        ld a, [FK_SET]
        and S_LADDER
        ret nz
        ld a, [PAD]
        bit 6, a                ; Up held = left the ladder at the top (Down = bottom)
        ret z
        ldh a, [$FFA6]
        bit 5, a
        jr z, @set
        ld a, [$CAFC]           ; a longer mercy already running is kept
        cp 42
        ret nc
@set:   ldh a, [$FFA6]
        or $20
        ldh [$FFA6], a
        ld a, 42
        ld [$CAFC], a
        ret
; ---- endgame aid: when the stage 6 boss appears and Arthur has no cross, a cross item is
;      placed on the boss's floor 48 px toward the stage start (bank 1 context: boss spawner)
h_boss: push de
        ld a, [FK_SET]
        and S_ENDG
        jr nz, @out
        ld a, [$C0B6]
        cp $04                  ; already holding the cross
        jr z, @out
        ld hl, $C5A4            ; a cross item already in play?
        ld b, 32
@scan:  push hl
        inc hl
        bit 0, [hl]
        jr z, @nx
        ld de, $0018
        add hl, de
        ld a, [hl+]
        cp $C3
        jr nz, @nx
        ld a, [hl]
        cp $49
        jr nz, @nx
        pop hl
        jr @out
@nx:    pop hl
        ld de, $0020
        add hl, de
        dec b
        jr nz, @scan
        call $280B              ; free slot?
        jr c, @out
        ldh a, [$FF90]          ; $45D0 spawns at the current object's position: borrow it
        push af
        ldh a, [$FF91]
        push af
        ldh a, [$FF92]
        push af
        ld a, [$C5A0]           ; boss spawn X - 48 px
        sub $03
        jr nc, @x
        xor a
@x:     ldh [$FF90], a
        ld a, [$C5A1]           ; boss floor; items lie one unit higher
        dec a
        ldh [$FF91], a
        ld a, $80
        ldh [$FF92], a
        ld de, $49C3            ; cross item descriptor
        call $45D0
        pop af
        ldh [$FF92], a
        pop af
        ldh [$FF91], a
        pop af
        ldh [$FF90], a
@out:   pop de
        ld hl, $74D2            ; (replaced) boss template
        ret
; ---- title: after a game over the cursor starts on CONTINUE (continues are already unlimited)
h_tcur: ld a, [$C0A4]           ; v0.8: in every preset, ORIGINAL included (design decision)           ; CONTINUE row shown (set by the first game over)
        or a
        jr z, @z
        ld a, $03
@z:     ld [OPTCUR], a
        ret
; ---- fair spawns (bank 1 context) -----------------------------------------------------
h_zx:   ld a, [FK_SET]          ; zombie generator, d = X block of the new zombie
        and S_SPAWN
        jr nz, @o
        ld a, [$C5AA]
        ld b, a
        ld a, d
        sub b
        add a, $03
        cp $07                  ; within 3 blocks (about 48 px) of Arthur: no zombie this time (v0.10: was 2;
                                ; with CAMERA AHEAD the screen's back edge is 54 px behind Arthur)
        jr nc, @o
        pop hl
        ret
@o:     ld a, [$C0B8]           ; (replaced)
        ret
h_touch:ld a, [FK_SET]          ; enemy touches Arthur (HRAM = the enemy)
        and S_SPAWN
        jr nz, @o
        ldh a, [$FF8A]
        cp $08                  ; a zombie...
        jr nz, @o
        ldh a, [$FFA5]
        cp $02                  ; ...still rising out of the ground can't hurt
        jr nc, @o
        pop hl                  ; return from the touch routine ($32D1)
        ret
@o:     ldh a, [$FF8A]          ; (replaced)
        cp $36
        ret
; ---- endgame aid, torch kill (bank 1 context: boss death, c = 0 cross kill / 1 other)
h_tkill:ld a, [FK_SET]
        and S_ENDG
        jr nz, @o
        ld c, $00               ; aid on: a torch kill counts as a win too
@o:     ld a, c                 ; (replaced) ld a,c / ld [$C0C2],a
        ld [$C0C2], a
        ret
; ---- secrets (v0.9)
.if !CLASSIC
T_spk:  call $389A              ; (replaced) gameplay frame, before the OAM build at $2DF0
        call PRE
        call h_spk
        jp POST
.endif
T_sfnd: call PRE                ; bank 1: hidden-item trigger touched
        call h_sfnd
        jp POST
T_rdy:  call PRINT              ; (replaced) READY text, bank $3E
        call PRE
        call h_rdy
        jp POST
B0END:

; ---- v0.10: bank 0 free space $00BE-$00FF (66 bytes of $FF before the cart header) ----
.org 0:$00BE
; quick stand (crouch state 2, $3143): the game stays crouched while ([PAD] & $B2) != 0, i.e.
; Down, B, Left or Right held. ON drops Left/Right from that mask ($82): releasing Down with a
; direction held stands Arthur up. Flags from the AND are the result (caller: jr nz,$3155).
h_qs:   ld a, [FK_SET2]
        and S2_QS
        ld a, [PAD]
        jr nz, @o
        and $82
        ret
@o:     and $B2                 ; (replaced) original mask
        ret
T_cam:  call PRE                ; camera follow ($38F1): d = Arthur's screen X -> scroll request
        call h_cam
        jp POST
B0LOW:

; ---- hook sites --------------------------------------------------------------------
.org 0:$016C                    ; boot: call $05C4  ->  init our WRAM, then $05C4
        call T_init
.org $3E:$4A43                  ; options Down: inc a / and $01  ->  3 rows
        call T_down
.org $3E:$4A4D                  ; options Up:   dec a / and $01  ->  3 rows
        call T_up
.org $3E:$4A1F                  ; options A/Start: ld a,[$C1E9]  ->  row 2 opens our page
        call T_sel
.org $3E:$4A13                  ; options cursor table: ld hl,$4A54 -> 3-row table
        ld hl, OPTTAB
.org $3E:$42B5                  ; options labels: last PRINT also draws "FAIR KNIGHT"
        call T_lbl
.org 0:$3387                    ; armor-loss hit: ld a,$F0 / ld [$C5C1],a (knockback speed)
        call T_kbv
        nop
        nop
.org 0:$33A6                    ; death hit: same
        call T_kbv
        nop
        nop
.org 0:$35CD                    ; hit hop (state 5): call $3725 (horizontal motion)
        call T_kbm
.org 0:$3201                    ; jump (state 3): ld a,[$C0E0] before the facing update
        call h_air
.org 0:$3819                    ; fall (state 7): same
        call h_airf
.org 0:$32C6                    ; ladder exit: ld a,$01 / ldh [$FFA5],a
        call h_lad
        nop
.org 1:$72AB                    ; stage 6 boss spawner: ld hl,$74D2
        call h_boss
.org 0:$0EB2                    ; title init: ld [$C1E9],a (cursor row 0)
        call h_tcur
.org 1:$4B06                    ; zombie generator: ld a,[$C0B8]
        call h_zx
.org 0:$3335                    ; enemy touch: ldh a,[$FF8A] / cp $36
        call h_touch
        nop
.org 1:$4711                    ; weapon item collected: ldh a,[$FFA9] / jp $06E7
        jp h_wpick
.org 1:$74A3                    ; stage 6 boss killed: ld a,c / ld [$C0C2],a (1 = replay stage 6)
        call h_tkill
        nop
.if !CLASSIC                    ; Classic edition: no sparkle markers, so this site stays original
.org 0:$05A6                    ; gameplay loop: call $389A (before the OAM build)
        call T_spk
.endif
.org 1:$7997                    ; hidden-item trigger touched: ldh a,[$FF8B] / or $02
        call T_sfnd
        nop
.org $3E:$4596                  ; READY screen: call PRINT ("READY")
        call T_rdy
.org 0:$3375                    ; armor-loss hit: ld a,$78 / ld [$CAFC],a (mercy frames)
        call T_mer
        nop
        nop
.org 0:$3143                    ; crouch state: ld a,[$C0E0] / and $B2 (stay crouched?)
        call h_qs
        nop
        nop
.org 0:$38F1                    ; camera follow: ld a,d / sub $50 / ld d,a
        call T_cam
        nop

; =====================================================================================
; Bank FKB
; =====================================================================================
.org FKB:$4000
h_init: push af
        ld a, [FK_SIG]
        cp $46
        jr nz, @new
        ld a, [FK_SIG+1]
        cp $4B
        jr z, @ok
@new:   ld a, $46
        ld [FK_SIG], a
        ld a, $4B
        ld [FK_SIG+1], a
        xor a
        ld [FK_SET], a
        ld [FK_SET2], a
        ld [FK_PRE], a
@ok:    ld a, $FF
        ld [FK_STG], a
        pop af
        jp $05C4

; options screen, 3 rows
h_down: inc a
        cp $03
        ret c
        xor a
        ret
h_up:   dec a
        cp $03
        ret c
        ld a, $02
        ret
h_lbl:  ld hl, s_fk
        ld d, $05
        ld e, $0D
        ld b, $08
        ld c, 11
        jp PRINT
h_sel:  ld a, [OPTCUR]          ; (the instruction we replaced)
        cp $02
        ret nz
        call page
        ld a, $02
        ld [OPTCUR], a
        ld a, $FF               ; makes the caller's "cp 0 / cp 1" fall through to ret
        ret

; ---- gameplay ------------------------------------------------------------------------
h_kbv:  ld a, [FK_SET]          ; knockback speed: $F0 (original) or 0
        bit 0, a
        ld a, $F0
        jr nz, @st
        xor a
@st:    ld [$C5C1], a
        ret
h_kbm:  push af                 ; hit hop horizontal motion only when knockback is ON
        ld a, [FK_SET]
        bit 0, a
        jr z, @no
        pop af
        jp $3725
@no:    pop af
        ret
h_mer:  ld a, [FK_SET]          ; mercy frames after losing armor: 120 or 240
        bit 1, a
        ld a, $78
        jr nz, @st
        ld a, $F0
@st:    ld [$CAFC], a
        ret
; ---- v0.10 camera. In: d = Arthur's screen X. Out: d = horizontal scroll request (the
;      game's $1A54 clamps it to the level). CENTER = original (X - $50). AHEAD: Arthur's
;      target X is 54 facing right / 106 facing left, eased 1 px per frame. If Arthur is more
;      than 16 px from the target (level edge clamp, respawn) the target snaps to him first, so
;      the camera never jumps.
h_cam:  push hl
        ld hl, sp+6             ; [sp]=hl, +2 ret to T_cam, +4 ret to $38F4, +6 = $38B5's caller
        ld a, [hl+]
        cp $91
        jr nz, @c
        ld a, [hl]
        cp $05
        jr nz, @c               ; only the gameplay frame ($058E, returns to $0591) looks ahead:
        ld a, [FK_SET2]         ; stage setup and the intro scene keep the original camera
        and S2_CAM
        jr z, @ah
@c:     ld a, $50               ; CENTER / not gameplay: original, and AHEAD restarts from $50
        ld [FK_CAMT], a
        pop hl
        ld a, d                 ; (replaced) ld a,d / sub $50 / ld d,a
        sub $50
        ld d, a
        ret
@ah:    push bc
        ld a, [FK_CAMT]
        ld c, a
        ld b, a                 ; v0.11: no direction held = hold the current target
        ld a, [PAD]             ; the target follows the held direction, not the facing,
        bit 4, a                ; so turning to throw doesn't swing the view
        jr z, @nr
        ld b, CAM_R             ; Right: look ahead
@nr:    bit 5, a
        jr z, @t
        ld b, CAM_L             ; Left (backwards): only back to the centre
@t:     ld a, d
        sub c
        add a, $10
        cp $21                  ; |X - target| <= 16 ?
        jr c, @e
        ld c, d                 ; no: snap the target to Arthur
@e:     ld hl, FK_CAMP          ; v0.11: ease every other frame (0.5 px/frame)
        inc [hl]
        bit 0, [hl]
        jr nz, @s
        ld a, c
        cp b
        jr z, @s
        jr c, @i
        dec c
        jr @s
@i:     inc c
@s:     ld a, c
        ld [FK_CAMT], a
        ld a, d
        sub c
        ld d, a
        pop bc
        pop hl
        ret

; =====================================================================================
; Fair Knight options page
; =====================================================================================
NROWS    = 12                   ; PRESET ... SECRETS, QUICKSTAND, CAMERA, EXIT
ROW0     = 2                    ; first list row on screen (v0.10: was 3, title moved to row 0)
COLV     = 12                   ; value column
A_LBL    = $08                  ; text attributes (same as the game's menu: cyan / yellow)
A_VAL    = $0A

page:   xor a
        ld [FK_CUR], a
        ld a, $FF
        ld [FK_PAD], a          ; ignore the A/Start press that opened the page
        call LCDOFF
        ld e, $00               ; clear all 18 rows
@clr:   push de
        ld hl, s_blank
        ld d, $00
        ld b, A_LBL
        ld c, 20
        call PRINT
        pop de
        inc e
        ld a, e
        cp 18
        jr nz, @clr
        ld hl, s_title
        ld d, $04
        ld e, $00
        ld b, A_VAL
        ld c, 11
        call PRINT
        ld hl, s_help
        ld d, $00
        ld e, $11
        ld b, A_VAL
        ld c, 20
        call PRINT
        ld c, $00               ; labels
@lbl:   push bc
        call rowptr             ; hl -> row record
        ld a, [hl+]
        ld h, [hl]
        ld l, a                 ; hl = label text (10 chars)
        pop bc
        push bc
        ld a, c
        add a, ROW0
        ld e, a
        ld d, $01
        ld b, A_LBL
        ld c, 10
        call PRINT
        pop bc
        inc c
        ld a, c
        cp NROWS
        jr nz, @lbl
        call values
        call desc
        ldh a, [$FF40]
        or $80
        ldh [$FF40], a
@loop:  halt
        nop
        call OAMDMA
        call READPAD
        ld a, [FK_CUR]
        ld [OPTCUR], a
        ld hl, curtab
        call CURSOR
        ld a, [PAD]
        ld b, a
        ld a, [FK_PAD]
        cpl
        and b                   ; newly pressed
        ld c, a
        ld a, b
        ld [FK_PAD], a
        ld a, c
        bit 6, a                ; Up
        jr z, @nu
        ld a, [FK_CUR]
        dec a
        cp NROWS
        jr c, @su
        ld a, NROWS-1
@su:    ld [FK_CUR], a
        call SFX
        call desc
        jr @loop
@nu:    bit 7, a                ; Down
        jr z, @nd
        ld a, [FK_CUR]
        inc a
        cp NROWS
        jr c, @sd
        xor a
@sd:    ld [FK_CUR], a
        call SFX
        call desc
        jr @loop
@nd:    bit 2, a                ; Select: back to the base preset
        jr z, @ns
        ld a, [FK_PRE]
        and $7F
        call setpre
        call SFX
        call values
        jr @loop
@ns:    bit 1, a                ; B: leave
        jr nz, @exit
        bit 3, a                ; Start: leave
        jr nz, @exit
        and $31                 ; A, Right, Left: change the value (A on EXIT leaves)
        jr z, @loop
        ld a, [FK_CUR]
        cp NROWS-1
        jr z, @exit
        ld a, c
        call change
        call SFX
        call values
        jp @loop
@exit:  call SFX
        call LCDOFF
        call $2D95              ; clear the sprite buffer
        call REDRAW
        ldh a, [$FF40]
        or $80
        ldh [$FF40], a
        ret

; hl -> record of row c  (records: label ptr, mask, value0 ptr, value1 ptr, desc ptr = 9 bytes)
rowptr: ld hl, rows
        ld a, c
        ld b, a
        add a, a
        add a, a
        add a, a
        add a, b                ; *9
        add a, l
        ld l, a
        ret nc
        inc h
        ret

; change row FK_CUR; a = pressed buttons (bit5 Left -> previous value)
change: ld b, a
        ld a, [FK_CUR]
        or a
        jr nz, @opt
        ld a, [FK_PRE]          ; PRESET row: cycle KNIGHT/LEGEND/ORIGINAL
        and $7F
        bit 5, b
        jr nz, @prev
        inc a
        cp $03
        jr c, @set
        xor a
        jr @set
@prev:  dec a
        cp $03
        jr c, @set
        ld a, $02
@set:   jp setpre
@opt:   ld e, b                 ; buttons (rowptr clobbers b)
        ld c, a
        call rowptr
        inc hl
        inc hl
        ld b, [hl]              ; mask
        ld a, b
        cp $FE
        jr z, @sec
        cp $F0
        jr c, @s0
        and $0F                 ; $Fx: FK_SET2 bit
        ld b, a
        ld a, [FK_SET2]
        xor b
        ld [FK_SET2], a
        jr @cu
@s0:    ld a, [FK_SET]
        xor b
        ld [FK_SET], a
@cu:
        ld a, [FK_PRE]
        or $80                  ; CUSTOM
        ld [FK_PRE], a
        ret

@sec:   ld a, [FK_SET2]         ; SECRETS: SPARKLES 0 -> MAP 1 -> OFF 3 (Left reverses)
        and $03
.if CLASSIC                     ; Classic: MAP 0 <-> OFF 3 (value 1 never set; shown as MAP)
        cp $03
        ld a, $03
        jr nz, @sw
        xor a
        jr @sw
.endif
        bit 5, e
        jr nz, @sl
        inc a
        cp $02
        jr nz, @s1
        inc a
@s1:    and $03
        jr @sw
@sl:    dec a
        cp $02
        jr nz, @s3
        dec a
@s3:    and $03
@sw:    ld b, a
        ld a, [FK_SET2]
        and $FC
        or b
        ld [FK_SET2], a
        ld a, [FK_PRE]
        or $80
        ld [FK_PRE], a
        ret

; a = preset 0-2: load its settings
setpre: ld [FK_PRE], a
        ld c, a
        ld b, $00
        ld hl, pre_set
        add hl, bc
        ld a, [hl]
        ld [FK_SET], a
        ld hl, pre_set2
        add hl, bc
        ld a, [hl]
        ld [FK_SET2], a
        ret

; print every row's value
values: ld c, $00
@v:     push bc
        ld a, c
        add a, ROW0
        ld e, a
        ld a, c
        or a
        jr nz, @o
        ld a, [FK_PRE]          ; preset name
        bit 7, a
        jr z, @pn
        ld a, $03               ; CUSTOM
@pn:    and $03
        add a, a
        add a, a
        add a, a                ; *8
        ld hl, s_pre
        add a, l
        ld l, a
        jr nc, @pr
        inc h
        jr @pr
@o:     call rowptr
        inc hl
        inc hl
        ld a, [hl+]             ; mask
        cp $FE                  ; SECRETS row: 3 values from FK_SET2 bits 1-0
        jr z, @sec
        ld b, a
        cp $F0                  ; $Fx: FK_SET2 bit x (EXIT $FF shows blanks either way)
        ld a, [FK_SET]
        jr c, @m
        ld a, b
        and $0F
        ld b, a
        ld a, [FK_SET2]
@m:     and b
        jr z, @v0
        inc hl
        inc hl
@v0:    ld a, [hl+]
        ld h, [hl]
        ld l, a
        jr @pr
@sec:   ld a, [FK_SET2]
        and $03
        cp $03
        jr nz, @s2
        dec a
@s2:    add a, a
        add a, a
        add a, a
        ld hl, s_sec
        add a, l
        ld l, a
        jr nc, @pr
        inc h
@pr:    ld d, COLV
        ld b, A_VAL
        ld c, 8
        call PRINT
        pop bc
        inc c
        ld a, c
        cp NROWS
        jr nz, @v
        ret

; two description lines for the current row (rows 14-15)
desc:   ld a, [FK_CUR]
        ld c, a
        call rowptr
        ld de, $0007
        add hl, de
        ld a, [hl+]
        ld h, [hl]
        ld l, a
        push hl
        ld d, $00
        ld e, $0E
        ld b, A_LBL
        ld c, 20
        call PRINT
        pop hl
        ld de, 20
        add hl, de
        ld d, $00
        ld e, $0F
        ld b, A_LBL
        ld c, 20
        jp PRINT

curtab: .db $05, $1E, $05, $26, $05, $2E, $05, $36, $05, $3E, $05, $46, $05, $4E, $05, $56, $05, $5E, $05, $66, $05, $6E, $05, $76

rows:   .dw l_pre
        .db $00
        .dw s_pre, s_pre
        .dw d_pre
        .dw l_knock
        .db S_KNOCK
        .dw v_off, v_on
        .dw d_knock
        .dw l_mercy
        .db S_MERCY
        .dw v_long, v_normal
        .dw d_mercy
        .dw l_wdrop
        .db S_WDROP
        .dw v_drop, v_lost
        .dw d_wdrop
        .dw l_air
        .db S_AIR
        .dw v_full, v_off
        .dw d_air
        .dw l_lad
        .db S_LADDER
        .dw v_on, v_off
        .dw d_lad
        .dw l_endg
        .db S_ENDG
        .dw v_on, v_off
        .dw d_endg
        .dw l_spawn
        .db S_SPAWN
        .dw v_on, v_off
        .dw d_spawn
        .dw l_sec
        .db $FE
        .dw s_sec, s_sec
        .dw d_sec
        .dw l_qs
        .db $F0 | S2_QS          ; $Fx = FK_SET2 bit (x)
        .dw v_on, v_off
        .dw d_qs
        .dw l_cam
        .db $F0 | S2_CAM
        .dw v_ahead, v_center
        .dw d_cam
        .dw l_exit
        .db $FF
        .dw v_none, v_none
        .dw d_exit

pre_set:  .db $00, $6B, $FF     ; KNIGHT, LEGEND, ORIGINAL
pre_set2: .db $00, $03, $0F     ; v0.10: ORIGINAL also sets S2_QS, S2_CAM

s_fk:    .db "FAIR KNIGHT"
s_title: .db "FAIR KNIGHT"
s_help:  .db "SELECT RESET  B EXIT"
s_blank: .db "                    "
s_pre:   .db "KNIGHT  LEGEND  ORIGINALCUSTOM  "
l_pre:   .db "PRESET    "
l_knock: .db "KNOCKBACK "
l_mercy: .db "MERCY TIME"
l_wdrop: .db "OLD WEAPON"
l_air:   .db "AIR CTRL  "
l_lad:   .db "LADDER TOP"
l_endg:  .db "BOSS CROSS"
l_spawn: .db "FAIR SPAWN"
l_sec:   .db "SECRETS   "
l_qs:    .db "QUICKSTAND"
l_cam:   .db "CAMERA    "
l_exit:  .db "EXIT      "
.if CLASSIC
s_sec:   .db "MAP     MAP     OFF     "   ; Classic: FK_SET2 bits1-0 = 0 MAP (KNIGHT), 3 OFF
.else
s_sec:   .db "SPARKLESMAP     OFF     "
.endif
v_on:    .db "ON      "
v_off:   .db "OFF     "
v_long:  .db "LONG    "
v_normal:.db "NORMAL  "
v_none:  .db "        "
v_full:  .db "FULL    "
v_drop:  .db "DROPPED "
v_lost:  .db "LOST    "
v_ahead: .db "AHEAD   "
v_center:.db "CENTER  "
d_pre:   .db "LEFT RIGHT CHANGES  "
         .db "ALL SETTINGS AT ONCE"
d_knock: .db "OFF HOPS IN PLACE   "
         .db "WHEN ARTHUR IS HIT  "
d_mercy: .db "LONG DOUBLES THE    "
         .db "SAFE TIME AFTER HITS"
d_wdrop: .db "LEFT BEHIND YOU WHEN"
         .db "YOU GRAB A NEW ONE  "
d_air:   .db "STEER LEFT OR RIGHT "
         .db "DURING A JUMP       "
d_lad:   .db "SHORT SAFE MOMENT AT"
         .db "THE TOP OF A LADDER "
d_endg:  .db "A CROSS WAITS NEAR  "
         .db "BOSS  TORCH WINS TOO"
d_spawn: .db "NO ZOMBIES RISING   "
         .db "RIGHT UNDER ARTHUR  "
.if CLASSIC
d_sec:   .db "MAP LISTS FOUND     "
         .db "SECRETS AT READY    "
.else
d_sec:   .db "SPARKLES MARK HIDDEN"
         .db "ITEMS  MAP LIST ONLY"
.endif
d_qs:    .db "STAND UP AS SOON AS "
         .db "DOWN IS LET GO      "
d_cam:   .db "AHEAD SHOWS MORE OF "
         .db "THE WAY YOU FACE    "
d_exit:  .db "BACK TO THE OPTIONS "
         .db "                    "

; =====================================================================================
; SECRETS (v0.9): found list, READY-screen list, sparkles
; =====================================================================================
; hl -> this stage's secrets table
sec_list:ld a, [$C0AD]
        cp $07
        jr c, @o
        ld a, $06
@o:     add a, a
        ld hl, sec_tab
        add a, l
        ld l, a
        jr nc, @n
        inc h
@n:     ld a, [hl+]
        ld h, [hl]
        ld l, a
        ret
; d = id -> hl = bitmap byte, a = bit mask (b clobbered)
bitad:  ld a, d
        and $07
        inc a
        ld b, a
        ld a, $80
@s:     rlca
        dec b
        jr nz, @s
        ld b, a
        ld a, d
        srl a
        srl a
        srl a
        and $07
        add a, $10
        ld l, a
        ld h, $DF
        ld a, b
        ret
; d = id -> nz if found (bc, de kept; hl clobbered)
isfound:push bc
        call bitad
        and [hl]
        pop bc
        ret
; hidden-item trigger touched (bank 1, HRAM = trigger object, [$FFA3/4] -> its stage-list entry)
h_sfnd: push bc
        push de
        push hl
        ldh a, [$FFA3]
        ld l, a
        ldh a, [$FFA4]
        ld h, a
        inc hl
        inc hl
        inc hl
        inc hl
        ld a, [hl+]
        ld h, [hl]
        sub $CD                 ; param - $79CD
        ld l, a
        ld a, h
        sbc a, $79
        ld h, a
        jr c, @x
        ld d, $00
@dv:    ld a, l
        sub $0A
        ld e, a
        ld a, h
        sbc a, $00
        jr c, @dn
        ld h, a
        ld l, e
        inc d
        jr @dv
@dn:    ld a, d
        cp $40
        jr nc, @x
        call bitad
        or [hl]
        ld [hl], a
@x:     pop hl
        pop de
        pop bc
        ldh a, [$FF8B]          ; (replaced)
        or $02
        ret
; READY screen (after "READY" is printed, LCD off): new stage -> clear found; list found secrets
h_rdy:  ld a, [$C0AD]
        ld b, a
        ld a, [FK_STG]
        cp b
        jr z, @same
        ld a, b
        ld [FK_STG], a
        ld hl, FK_FND
        xor a
        ld c, $08
@cl:    ld [hl+], a
        dec c
        jr nz, @cl
@same:  ld a, [FK_SET2]
        and $03
        cp $03
        ret z
        xor a
        ld [FK_T], a            ; found
        ld [FK_T+1], a          ; total
        call sec_list
@lp:    ld a, [hl+]
        cp $FF
        jr z, @sum
        inc hl
        ld a, [hl+]
        ld d, a                 ; id
        ld a, [hl+]
        ld e, a                 ; kind
        ld a, [FK_T+1]
        inc a
        ld [FK_T+1], a
        push hl
        call isfound
        jr z, @nf
        ld a, e
        and $7F
        ld c, a
        add a, a
        add a, c
        add a, a                ; *6
        ld hl, sec_nm
        add a, l
        ld l, a
        jr nc, @h
        inc h
@h:     ld a, [FK_T]
        ld c, $0D               ; row 13, 3 names per row
@r:     cp $03
        jr c, @c
        sub $03
        inc c
        jr @r
@c:     ld b, a
        add a, a
        add a, b
        add a, a
        inc a
        ld d, a
        ld e, c
        ld b, $08
        ld c, $06
        call PRINT
        ld a, [FK_T]
        inc a
        ld [FK_T], a
@nf:    pop hl
        jr @lp
@sum:   ld a, [FK_T+1]
        or a
        ret z
        ld hl, s_secr
        ld d, $03
        ld e, $0C
        ld b, $08
        ld c, $08
        call PRINT
        ld hl, FK_T             ; found count, already a font digit (0-9)
        ld d, $0B
        ld e, $0C
        ld b, $08
        ld c, $01
        call PRINT
        ld hl, s_of
        ld d, $0C
        ld e, $0C
        ld b, $08
        ld c, $04
        call PRINT
        ld hl, FK_T+1
        ld d, $10
        ld e, $0C
        ld b, $08
        ld c, $01
        jp PRINT
.if !CLASSIC                    ; Classic edition: sparkle markers and their tile compiled out
; every gameplay frame: queue a sparkle sprite at each unfound secret trigger on screen
h_spk:  ld a, [FK_SET2]
        and $03
        ret nz
        ld a, [FK_FC]
        inc a
        ld [FK_FC], a
        and $1F
        call z, spk_gfx         ; (re)write the sparkle tile every 32 frames (stage loads may clear it)
        ld a, $01
        ld [FK_MS], a
        ld [FK_MS+5], a
        xor a
        ld [FK_MS+1], a
        ld [FK_MS+2], a
        ld [FK_MS+6], a
        ld [FK_MS+7], a
        ld a, SPK_T
        ld [FK_MS+3], a
        ld [FK_MS+8], a
        ld a, PAL_N
        ld [FK_MS+4], a
        ld a, PAL_H
        ld [FK_MS+9], a
        call sec_list
@lp:    ld a, [hl+]
        cp $FF
        ret z
        ld b, a                 ; X block
        ld a, [hl+]
        ld c, a                 ; Y block
        ld a, [hl+]
        ld d, a                 ; id
        ld a, [hl+]
        ld e, a                 ; kind (bit 7 harmful)
        push hl
        call isfound
        jr nz, @nx
        ld a, [$C251]
        ld l, a
        ld a, b
        sub l
        cp $0B
        jr nc, @nx
        ld a, [$C252]
        ld l, a
        ld a, c
        sub l
        cp $09
        jr nc, @nx
        ld a, b
        swap a
        and $F0
        ld l, a
        ld a, [$C255]           ; SCX
        cpl
        inc a
        add a, l
        add a, $04
        ld d, a                 ; screen X
        ld a, c
        swap a
        and $F0
        ld l, a
        ld a, [$C256]           ; SCY
        cpl
        inc a
        add a, l
        add a, $04
        cp $80                  ; keep clear of the status bar
        jr nc, @nx
        ld l, a
        ld a, e
        ld e, l                 ; screen Y
        ld hl, FK_MS
        bit 7, a
        jr z, @q
        ld hl, FK_MS+5
@q:     xor a
        call $2DB7              ; queue (hl = metasprite, d = X, e = Y)
@nx:    pop hl
        jr @lp
; write the 16-byte sparkle tile to VRAM bank 0 tile SPK_T, one byte per non-mode-3 moment
spk_gfx:ldh a, [$FF4F]
        push af
        xor a
        ldh [$FF4F], a
        ld hl, $8000 + SPK_T * 16
        ld de, g_spk
        ld c, $10
        di
@w:     ldh a, [$FF41]
        and $02
        jr nz, @w
        ld a, [de]
        ld [hl+], a
        inc de
        dec c
        jr nz, @w
        ei
        pop af
        ldh [$FF4F], a
        ret
g_spk:  .db $10, $10, $10, $10, $10, $10, $EE, $FE, $10, $10, $10, $10, $10, $10, $00, $00
.endif
; ---- secrets table (generated by tools/secrets_extract.py; trigger X block, Y block, id = (param-$79CD)/10, name index|$80 harmful)
sec_tab:.dw sec_s1, sec_s2, sec_s3, sec_s4, sec_s5, sec_s6, sec_none
sec_s1:
        .db $2F, $03, $00, $00
        .db $A1, $0A, $01, $01
        .db $75, $09, $02, $04
        .db $FF
sec_s2:
        .db $04, $0F, $03, $03
        .db $1E, $0B, $04, $01
        .db $7D, $0D, $05, $08
        .db $63, $15, $06, $04
        .db $A4, $14, $07, $02
        .db $FF
sec_s3:
        .db $34, $32, $0E, $06
        .db $A4, $06, $0F, $01
        .db $8C, $16, $10, $00
        .db $B7, $39, $11, $85
        .db $BB, $39, $12, $08
        .db $90, $0E, $1F, $04
        .db $FF
sec_s4:
        .db $22, $04, $20, $03
        .db $88, $0C, $21, $85
        .db $9A, $0A, $22, $00
        .db $77, $0C, $24, $04
        .db $4C, $0B, $23, $08
        .db $FF
sec_s5:
        .db $0F, $39, $30, $09
        .db $27, $28, $31, $01
        .db $1F, $32, $32, $03
        .db $0D, $43, $33, $08
        .db $1E, $16, $34, $04
        .db $FF
sec_s6:
        .db $0E, $57, $35, $06
        .db $0D, $2F, $36, $08
        .db $0F, $25, $37, $09
        .db $09, $43, $38, $0A
        .db $14, $33, $39, $04
        .db $1D, $16, $3A, $0A
        .db $FF
sec_none:.db $FF
; item names, READY-screen font (0-9, A-Z = $0A-$23, space $FF), 6 chars each
sec_nm: .db $16, $18, $17, $0E, $22, $FF, $0C, $18, $12, $17, $1C, $FF, $0C, $15, $18, $0C, $14, $FF, $01, $1E, $19, $FF, $FF, $FF, $0A, $1B, $16, $18, $1B, $FF, $0F, $1B, $18, $10, $FF, $FF, $15, $0A, $17, $0C, $0E, $FF, $14, $17, $12, $0F, $0E, $FF, $1D, $18, $1B, $0C, $11, $FF, $0A, $21, $0E, $FF, $FF, $FF, $0C, $1B, $18, $1C, $1C, $FF
s_secr: .db $1C, $0E, $0C, $1B, $0E, $1D, $1C, $FF
s_of:   .db $FF, $18, $0F, $FF
FKEND:
