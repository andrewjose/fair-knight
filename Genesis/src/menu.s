| Fair Knight (Genesis) - FAIR KNIGHT options page, reached with C on the game's OPTION screen.
| Plane A nametable at $C000 (64x32 cells, 128 bytes per row). Text uses the game's own font tiles.
        .include "fk.inc"
        .section .fk,"ax"
        .globl fk_opt, fk_page
        .include "menudata.inc"
        .even

        .equ PAD_NEW,   0xFFF603        | buttons pressed this frame: 0 Up 1 Down 2 Left 3 Right 4 B 5 C 6 A 7 Start
        .equ WAITCNT,   0xFFF62A
        .equ WAITVB,    0x1DAA          | game routine: wait until WAITCNT reaches 0 (enables interrupts)
        .equ VDP_DATA,  0xC00000
        .equ VDP_CTRL,  0xC00004
        .equ PAL_HEAD,  0x4000          | cyan (the game's option headings)
        .equ PAL_VAL,   0x0000          | orange (selected value)
        .equ PAL_DIM,   0x2000          | brown (unselected)
        .equ ROW0,      5               | first option row
        .equ VALCOL,    23

| ---- hook in the OPTION screen loop (replaces "move #$2300,sr / bsr $2440" at $2408) -----------
| Runs with interrupts still masked: draw the hint line, then the original input handler, then C.
fk_opt:
        move.l  #0x40000003+((23*128+2*6)<<16),VDP_CTRL
        lea     s_hint(pc),a0
        move.w  #PAL_HEAD,d3
        moveq   #0,d1
        bsr     puts
        move.w  #0x2300,sr
        jsr     0x2440                  | original: move cursor / change values
        btst    #5,PAD_NEW              | C: open the FAIR KNIGHT page
        beq.s   1f
        bsr     fk_page
        addq.l  #4,sp                   | leave the option loop and re-enter the OPTION screen
        jmp     0x233C                  | (its init redraws the whole screen)
1:      rts

| ---- the page ------------------------------------------------------------------------------------
fk_page:
        movem.l d0-d7/a0-a6,-(sp)
        clr.b   FK_CUR
        move.w  #0x2700,sr
        bsr     cls
        bsr     draw_all
pg_loop:
        move.b  #8,WAITCNT
        jsr     WAITVB
        move.b  PAD_NEW,d7
        beq.w   pg_loop
        move.w  #0x2700,sr
        btst    #7,d7                   | Start: back to the OPTION screen
        bne.w   pg_exit
        btst    #0,d7
        beq.s   1f
        subq.b  #1,FK_CUR               | Up (wraps)
        bpl.s   2f
        move.b  #NROWS-1,FK_CUR
        bra.s   2f
1:      btst    #1,d7
        beq.s   3f
        addq.b  #1,FK_CUR               | Down (wraps)
        cmp.b   #NROWS,FK_CUR
        blo.s   2f
        clr.b   FK_CUR
2:      bsr     draw_all
        bra.s   pg_loop
3:      btst    #6,d7                   | A: reset everything to the current base preset
        beq.s   4f
        move.b  FK_PRESET,d0
        andi.b  #3,d0
        bsr     apply_preset
        bra.w   2b
4:      move.b  d7,d0
        andi.b  #0x0C,d0                | Left / Right change the highlighted row
        beq.w   pg_loop
        moveq   #0,d0
        move.b  FK_CUR,d0
        cmp.b   #ROW_EXIT,d0
        beq.s   5f
        tst.b   d0
        bne.s   6f
        move.b  FK_PRESET,d0            | PRESET row: cycle KNIGHT / LEGEND / ORIGINAL
        andi.b  #3,d0
        btst    #3,d7
        bne.s   7f
        subq.b  #1,d0                   | Left
        bpl.s   8f
        moveq   #2,d0
        bra.s   8f
7:      addq.b  #1,d0                   | Right
        cmp.b   #3,d0
        blo.s   8f
        moveq   #0,d0
8:      bsr     apply_preset
        bra.w   2b
6:      lsl.w   #4,d0                   | option row: toggle its bit, preset becomes CUSTOM
        lea     rows(pc),a1
        move.b  4(a1,d0.w),d1           | which byte (0 FK_SET, 1 FK_SET2)
        move.b  5(a1,d0.w),d2           | bit number
        lea     FK_SET,a2
        tst.b   d1
        beq.s   9f
        lea     FK_SET2,a2
9:      bchg    d2,(a2)
        ori.b   #0x80,FK_PRESET
        bra.w   2b
5:      bra.w   pg_loop
pg_exit:
        move.w  #0x2700,sr
        movem.l (sp)+,d0-d7/a0-a6
        rts

| d0 = preset 0..2 -> FK_SET/FK_SET2, FK_PRESET (custom flag cleared)
apply_preset:
        andi.w  #3,d0
        move.b  d0,FK_PRESET
        add.w   d0,d0
        lea     presets(pc),a0
        move.b  0(a0,d0.w),FK_SET
        move.b  1(a0,d0.w),FK_SET2
        rts
| KNIGHT, LEGEND, ORIGINAL: FK_SET, FK_SET2 (1 = original behaviour)
| LEGEND: original knockback and mercy, endgame aid off, secrets off; drop, air, spawns on; ladder off
presets: .byte 0x00,0x00, 0xE3,0x01, 0xFF,0xFF

| ---- drawing ---------------------------------------------------------------------------------------
cls:    move.l  #0x40000003,VDP_CTRL    | clear plane A rows 0-27 (64 cells each)
        move.w  #28*64-1,d1
1:      move.w  #0,VDP_DATA
        dbf     d1,1b
        rts

| d0.w = row, d1.w = col -> set VDP write address
at:     move.w  d0,d2
        lsl.w   #7,d2
        add.w   d1,d2
        add.w   d1,d2
        swap    d2
        clr.w   d2
        ori.l   #0x40000003,d2
        move.l  d2,VDP_CTRL
        rts

| a0 = ASCII string (0-terminated), d3 = attribute, d1 = pad to this many cells (0 = none)
puts:   moveq   #0,d4
1:      moveq   #0,d0
        move.b  (a0)+,d0
        beq.s   3f
        subi.b  #0x20,d0
        add.w   d0,d0
        lea     font(pc),a3
        move.w  0(a3,d0.w),d0
        beq.s   2f
        or.w    d3,d0
2:      move.w  d0,VDP_DATA
        addq.w  #1,d4
        bra.s   1b
3:      cmp.w   d1,d4
        bhs.s   4f
        move.w  #0,VDP_DATA
        addq.w  #1,d4
        bra.s   3b
4:      rts

draw_all:
        moveq   #2,d0                   | title
        moveq   #10,d1
        bsr     at
        lea     s_title(pc),a0
        move.w  #PAL_HEAD,d3
        moveq   #0,d1
        bsr     puts
        moveq   #0,d5                   | row index
dr_row: move.w  d5,d0
        add.w   d0,d0
        addi.w  #ROW0,d0
        moveq   #3,d1
        bsr     at
        move.w  d5,d6
        lsl.w   #4,d6
        lea     rows(pc),a1
        movea.l a1,a4
        adda.w  d6,a4                   | a4 = row entry
        move.w  #PAL_HEAD,d3
        cmp.b   FK_CUR,d5
        beq.s   1f
        move.w  #PAL_DIM,d3
1:      lea     strings(pc),a0
        adda.w  (a4),a0                 | label
        moveq   #18,d1
        bsr     puts
        move.w  d5,d0                   | value
        add.w   d0,d0
        addi.w  #ROW0,d0
        moveq   #VALCOL,d1
        bsr     at
        move.w  #PAL_VAL,d3
        cmp.b   FK_CUR,d5
        beq.s   2f
        move.w  #PAL_DIM,d3
2:      bsr     row_value               | a0 = value string
        moveq   #14,d1
        bsr     puts
        addq.w  #1,d5
        cmp.w   #NROWS,d5
        blo     dr_row
        move.w  #20,d0                  | description of the highlighted row
        moveq   #1,d1
        bsr     at
        moveq   #0,d0
        move.b  FK_CUR,d0
        lsl.w   #4,d0
        lea     rows(pc),a4
        adda.w  d0,a4
        bsr     row_desc
        move.w  #PAL_VAL,d3
        moveq   #38,d1
        bsr     puts
        move.w  #23,d0                  | help lines (kept clear of the bottom overscan)
        moveq   #1,d1
        bsr     at
        lea     s_help1(pc),a0
        move.w  #PAL_HEAD,d3
        moveq   #38,d1
        bsr     puts
        move.w  #24,d0
        moveq   #1,d1
        bsr     at
        lea     s_help2(pc),a0
        moveq   #38,d1
        bra     puts

| a4 = row entry -> a0 = value string for its current setting
row_value:
        lea     strings(pc),a0
        move.b  4(a4),d1
        cmp.b   #2,d1
        bne.s   1f
        lea     s_blank(pc),a0          | EXIT row: no value
        rts
1:      cmp.b   #3,d1
        bne.s   2f
        btst    #7,FK_PRESET            | PRESET row
        beq.s   3f
        lea     s_custom(pc),a0
        rts
3:      moveq   #0,d0
        move.b  FK_PRESET,d0
        andi.b  #3,d0
        add.w   d0,d0
        lea     s_presets(pc),a1
        lea     strings(pc),a0
        adda.w  0(a1,d0.w),a0
        rts
2:      move.b  5(a4),d2                | bit row: value 0 or 1
        lea     FK_SET,a1
        tst.b   d1
        beq.s   4f
        lea     FK_SET2,a1
4:      move.w  2(a4),d0                | off_on pair index
        btst    d2,(a1)
        beq.s   5f
        addq.w  #2,d0
5:      lea     vnames(pc),a1
        adda.w  d0,a1
        adda.w  (a1),a0
        rts

| a4 = row entry -> a0 = description of its current value
row_desc:
        lea     strings(pc),a0
        cmp.b   #3,4(a4)
        bne.s   1f
        moveq   #3,d0                   | PRESET row: describe the preset (or CUSTOM)
        btst    #7,FK_PRESET
        bne.s   2f
        move.b  FK_PRESET,d0
        andi.w  #3,d0
2:      add.w   d0,d0
        lea     d_presets(pc),a1
        adda.w  0(a1,d0.w),a0
        rts
1:      move.b  5(a4),d2
        lea     FK_SET,a1
        tst.b   4(a4)
        beq.s   3f
        lea     FK_SET2,a1
3:      moveq   #6,d0
        btst    d2,(a1)
        beq.s   4f
        moveq   #8,d0
4:      adda.w  0(a4,d0.w),a0
        rts
