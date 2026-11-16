; Fair Knight v0.5 - FAIR SPAWNS (design change 3). Lives in PRG bank 2 with the other FK code.
;
; Three parts, all off when FK_PRESET bit 6 (FKP_FAIRSP) is set (ORIGINAL):
;  1. Zombie cap   - the stage 1 / 3A zombie generator ($8416) only starts a new wave while
;                    fewer than FS_ZCAP zombies (object type 0) are out.
;  2. Spawn tick   - once per logic tick, after the event spawner and all bank-2 generators have run,
;                    every new object gets a telegraph age (FS_TEL ticks) if its type is an enemy,
;                    and generator enemies that appeared within 32 px of Arthur are pushed out to 32 px.
;  3. Hit check    - Arthur's hit check ($E014, FK id 11): a touch only counts if something that is NOT
;                    in its telegraph window is near Arthur. Touches from enemies still telegraphing
;                    are cancelled, so a freshly spawned enemy can't hurt him for ~20 frames.
.include "fk.inc"
.export fk_zgen, fk_gen, fshit
FS_PUSH = 36
.segment "BANK2B"

; ---- 1. zombie cap: replaces "JSR $8416" at $8400 ------------------------
fk_zgen:
        lda FK_PRESET
        and #FKP_FAIRSP
        bne @go              ; original
        ldx #16
        ldy #0
@c:     lda $04F0,x
        beq @n
        lda $0631,x          ; type 0 = zombie
        bne @n
        iny
@n:     dex
        bne @c
        cpy #FS_ZCAP
        bcc @go
        rts                  ; at the cap: no wave this tick (the wave timer waits)
@go:    jmp $8416

; ---- 2. spawn tick: replaces "JSR $8748 / RTS" at $8412 ------------------
fk_gen: jsr $8748            ; last original generator
        lda FK_PRESET
        and #FKP_FAIRSP
        beq :+
        rts
:       ldx #16
@slot:  jsr nib_get          ; A = age nibble of slot X
        tay
        lda $04F0,x
        bne @act
        lda #0               ; slot empty: forget it
        beq @put
@act:   tya
        bne @old
        jsr nudge            ; new object: keep generator enemies 32 px away
        lda $0631,x
        jsr tel_ok
        lda #15              ; not an enemy type: settled at once
        bcc @put
        lda #FS_TEL
        bne @put
@old:   cmp #15
        beq @next
        sec
        sbc #1
        cmp #1
        bne @put
        lda #15
@put:   jsr nib_put
@next:  dex
        bne @slot
        rts

; nudge: X = new object. Generator enemy types within 32 px (and 48 px vertically) of Arthur
; are moved to FS_PUSH (36) px from him (so they are still >= 32 px after their first move), on the side they were already on.
nudge:  lda $0631,x
        ldy #NUDGE_N-1
@t:     cmp nudge_types,y
        beq @y
        dey
        bpl @t
@r:     rts
@y:     lda $0599,x
        sec
        sbc $0599
        tay
        lda $056D,x
        sbc $056D
        jsr lt48
        bcs @r
        lda $05AF,x
        sec
        sbc $05AF
        tay
        lda $0583,x
        sbc $0583
        pha
        jsr lt32
        pla
        bcs @r
        tay                  ; Y = dx high byte (bit 7 = object is left of Arthur)
        bmi @left
@right: lda $05AF
        clc
        adc #FS_PUSH
        sta $05AF,x
        lda $0583
        adc #0
        sta $0583,x
        rts
@left:  lda $0583            ; near the stage's left edge: use the right side
        bne :+
        lda $05AF
        cmp #FS_PUSH
        bcc @right
:       lda $05AF
        sec
        sbc #FS_PUSH
        sta $05AF,x
        lda $0583
        sbc #0
        sta $0583,x
        rts

; tel_ok: A = object type -> carry set if it gets a spawn telegraph (enemy types that are placed
; by the stage event lists or the bank-2 generators; not items, pots, platforms or bosses)
tel_ok: ldy #TEL_N-1
@t:     cmp tel_types,y
        beq @y
        dey
        bpl @t
        clc
        rts
@y:     sec
        rts

; ---- 3. Arthur hit check (FK id 11, replaces $E014) ----------------------
; In: X = Arthur's slot. Out: carry set = take the hit (as the original: Arthur flag bit 0).
fshit:  lda $04F0,x
        and #$01
        bne :+
        clc
        rts
:       lda FK_PRESET
        and #FKP_FAIRSP
        beq :+
        sec                  ; original
        rts
:       txa
        pha
        lda #0
        sta FK_HFL
        ldx #16
@s:     lda $04F0,x
        beq @nx
        lda $0631,x
        cmp #$10             ; items, hidden items and pots ($10-$12) never hurt
        bcc :+
        cmp #$13
        bcc @nx
:       cmp #$20             ; magician trigger
        beq @nx
        lda $05AF,x
        sec
        sbc $05AF
        tay
        lda $0583,x
        sbc $0583
        jsr lt24
        bcs @nx
        lda $0599,x
        sec
        sbc $0599
        tay
        lda $056D,x
        sbc $056D
        jsr lt40
        bcs @nx
        jsr nib_get
        cmp #2
        bcc @norm
        cmp #15
        bcs @norm
        lda #$01             ; an enemy still in its telegraph window is near
        bne @fl
@norm:  lda #$02             ; something else is near
@fl:    ora FK_HFL
        sta FK_HFL
@nx:    dex
        bne @s
        pla
        tax
        lda FK_HFL
        cmp #$01
        beq @cancel
        sec                  ; anything else near (or nothing found): the hit stands
        rts
@cancel:
        lda $04F0,x          ; drop the touch; it comes back next tick if the enemy is still there
        and #$FE
        sta $04F0,x
        clc
        rts

; ---- helpers ---------------------------------------------------------------
; nib_get: X = slot -> A = its age nibble (slot 16 shares nibble 0 with Arthur's slot). Y clobbered.
nib_get:
        txa
        and #$0F
        lsr a
        tay
        lda FK_AGE,y
        bcc @lo
        lsr a
        lsr a
        lsr a
        lsr a
@lo:    and #$0F
        rts
; nib_put: X = slot, A = new nibble value. Y clobbered, $25 scratch.
nib_put:
        sta $25
        txa
        and #$0F
        lsr a
        tay
        bcs @hi
        lda FK_AGE,y
        and #$F0
        ora $25
        sta FK_AGE,y
        rts
@hi:    lda $25
        asl a
        asl a
        asl a
        asl a
        sta $25
        lda FK_AGE,y
        and #$0F
        ora $25
        sta FK_AGE,y
        rts
; ltNN: 16-bit signed distance in A (high) : Y (low) -> carry clear if |d| < NN
.macro LTMAKE name, lim
name:   cmp #0
        beq :+
        cmp #$FF
        bne :++
        tya
        clc
        adc #lim
        bcc :++
        beq :++
        clc
        rts
:       cpy #lim
        rts
:       sec
        rts
.endmacro
LTMAKE lt24, 24
LTMAKE lt32, 32
LTMAKE lt40, 40
LTMAKE lt48, 48

; generator enemy types (bank 2 $8416-$880A): pushed out to 32 px when they appear too close
nudge_types: .byte $00,$03,$04,$06,$07,$14
NUDGE_N = * - nudge_types
; enemy types that get the spawn telegraph
tel_types:   .byte $00,$01,$02,$03,$04,$06,$07,$08,$0A,$0B,$0D,$0E,$0F,$14,$21,$32
TEL_N = * - tel_types
