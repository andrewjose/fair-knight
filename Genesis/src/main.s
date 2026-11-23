| Fair Knight (Genesis) - new code, placed in the expanded ROM area (section .fk -> $0A0000)
        .include "fk.inc"
        .section .fk,"ax"
        .globl fk_kbtab, fk_mercy

| ---- KNOCKBACK: replaces "lea $8C58(pc),a0 / move.w (a0)+,20(a1)" at $8BA6 in the hit handler.
| a1 = Arthur. Loads the hit-hop table (vx, vy, gravity, ax) from the original or the Fair Knight copy.
fk_kbtab:
        lea     0x8C58,a0               | original: vx 2.0, vy 4.25, gravity, ax 0
        btst    #FKB_KNOCK,FK_SET
        bne.s   1f
        lea     kbtab_fk(pc),a0         | Fair Knight: same hop, no sideways speed
1:      move.w  (a0)+,20(a1)
        rts
kbtab_fk:
        .word   0x0000,0x0440,0xFFC8,0x0000

| ---- MERCY TIME: replaces "move.w #120,$3318(a5)" at $8CBC (landing after a hit)
fk_mercy:
        move.w  #120,0x3318(a5)
        btst    #FKB_MERCY,FK_SET
        bne.s   1f
        move.w  #240,0x3318(a5)
1:      rts

| ---- WEAPON DROP: replaces "move.b 11(a1),d0 / jmp $13566" at $1B600 (weapon item touched).
| a1 = the item object being collected, a5 = $FF8000. $13566 swaps Arthur's weapon (+$2C) and saves
| the old one in +$2D. Fair Knight keeps the item object alive, turns it into the OLD weapon and
| relaunches it with the game's own item-pop physics (the values $1A876-$1A898 use when an enemy or
| chest drops an item), but always toward the stage start (lower world X).
| Only standard dropped items (+$30 = $1B1AA, handler table $1A7AC) are relaunched; the special
| flying item class at $1B2F0 (+$30 = $1B554) keeps the original behaviour.
        .globl fk_wdrop
fk_wdrop:
        move.b  11(a1),d0
        movea.l 0x32CE(a5),a0
        cmp.b   0x2C(a0),d0
        beq.s   9f                      | same weapon: original path (no swap)
        btst    #FKB_WDROP,FK_SET
        bne.s   9f                      | ORIGINAL behaviour
        cmpi.l  #0x1B1AA,0x30(a1)
        bne.s   9f                      | not a standard item object
        move.b  0x2C(a0),FK_TMP         | old weapon
        movem.l d2/a1,-(sp)
        jsr     0x13566
        movem.l (sp)+,d2/a1
        move.w  d2,0x40(a1)             | undo "collected" (the touch routine set $0400)
        move.b  FK_TMP,11(a1)
        move.l  a1,FK_DROPOBJ           | landing must not re-roll the weapon (see fk_wpick)
        move.b  #2,0x41(a1)             | substate 2: airborne ($1A942), lands into substate 4
        clr.b   0x42(a1)
        move.b  #16,0x0F(a1)
        move.w  #-0x0100,0x14(a1)       | 1 px/frame toward lower X
        move.w  #0x0400,0x16(a1)        | up 4 px/frame
        clr.w   0x18(a1)
        move.w  #-0x0050,0x1A(a1)       | gravity
        rts
9:      jmp     0x13566

| ---- WEAPON DROP, landing: replaces "moveq #0,d0 / movea.l $32CE(a5),a4" at $1AB1C.
| On landing an item object rolls a random weapon ($1AB1C-$1AB60). The relaunched old weapon must
| keep its type, so for that one object skip straight to "store weapon + set its animation" at $1AB62.
        .globl fk_wpick
fk_wpick:
        cmpa.l  FK_DROPOBJ,a1
        bne.s   1f
        clr.l   FK_DROPOBJ
        move.b  11(a1),d0
        jmp     0x1AB62
1:      moveq   #0,d0
        movea.l 0x32CE(a5),a4
        jmp     0x1AB22

| ---- AIR CONTROL FULL: replaces "cmpi.l #$1219A,$24(a1)" at $8AC6 in the airborne routine $8A72
| (jumps, falls and the hit hop all run it). Left/Right in the air set the sideways speed to the jump
| speed for the current armour (table $9196, stride 8, indexed by +$11); no sideways input keeps the
| current speed, so an untouched jump is the original arc. Vertical speed and gravity are not touched.
| The hit hop is excluded (continuation $3338(a5) = $8C60). Facing is left to the game's own mid-air
| turn code. The jump animation pointer encodes the travel direction ($1219A = +X, $1221A = -X) and
| $8AC6-$8B00 force vx to match it, so it is switched to follow the new sign.
| Exit: flags = the original cmpi, so the bne at $8ACE behaves as before.
        .globl fk_air
fk_air:
        movem.l d0-d1/a0,-(sp)
        btst    #FKB_AIR,FK_SET
        bne.s   9f                      | OFF (original)
        cmpi.l  #0x8C60,0x3338(a5)
        beq.s   9f                      | hit recoil: no steering
        move.b  0x32DC(a5),d0           | input: bit0 right, bit1 left
        andi.b  #3,d0
        beq.s   9f
        cmpi.b  #3,d0
        beq.s   9f
        moveq   #0,d1
        move.b  0x11(a1),d1
        lsl.w   #3,d1
        lea     0x9196,a0
        move.w  (a0,d1.w),d1            | jump speed for this armour
        btst    #1,d0
        beq.s   1f
        neg.w   d1
1:      move.w  d1,0x14(a1)
        cmpi.l  #0x1219A,0x24(a1)
        beq.s   2f
        cmpi.l  #0x1221A,0x24(a1)
        bne.s   9f
2:      move.l  #0x1219A,0x24(a1)
        tst.w   d1
        bpl.s   9f
        move.l  #0x1221A,0x24(a1)
9:      movem.l (sp)+,d0-d1/a0
        cmpi.l  #0x1219A,0x24(a1)
        rts

| ---- LADDER SAFETY: replaces "move.l #$8596,$334C(a5)" at $8F7C and $8F20 (end of the climb over a
| ladder top: Arthur becomes a standing character again). Gives the same invincibility the game uses
| after a hit (mercy wrapper $8CCA: no hit checks, blinking, $3317 = $FF) for 42 frames (0.7 s).
| Only when the plain behaviour wrapper $84EE is active, so a running hit-mercy is never shortened.
        .globl fk_ladder
fk_ladder:
        move.l  #0x8596,0x334C(a5)
        btst    #FKB_LADDER,FK_SET2
        bne.s   9f
        cmpi.l  #0x84EE,0x3338(a5)
        bne.s   9f
        move.w  #42,0x3318(a5)
        move.b  #0xFF,0x3317(a5)
        move.l  #0x8CCA,0x3338(a5)
9:      rts
