| Fair Knight (Genesis) - options page data. Rows are table-driven: add a row = one entry + its strings.
        .equ NROWS, 7
        .equ ROW_EXIT, NROWS-1
| entry: label, value-pair index into vnames, kind (0 FK_SET bit, 1 FK_SET2 bit, 2 exit, 3 preset), bit, description
        .macro ROW label, vpair, kind, bit, desc0, desc1
        .word \label-strings, \vpair
        .byte \kind, \bit
        .word \desc0-strings, \desc1-strings, 0, 0, 0   | 16 bytes per row
        .endm
rows:
        ROW s_preset,  0,       3, 0,         d_preset, d_preset
        ROW s_knock,   V_KNOCK, 0, FKB_KNOCK, d_knock0, d_knock1
        ROW s_mercy,   V_MERCY, 0, FKB_MERCY, d_mercy0, d_mercy1
        ROW s_wdrop,   V_WDROP, 0, FKB_WDROP, d_wdrop0, d_wdrop1
        ROW s_air,     V_AIR,   0, FKB_AIR,   d_air0,   d_air1
        ROW s_ladder,  V_LADDER,1, FKB_LADDER,d_lad0,  d_lad1
        ROW s_exit,    0,       2, 0,         d_exit,   d_exit
d_presets: .word d_knight-strings, d_legend-strings, d_orig-strings, d_custom-strings
| value pairs: (value when the bit is 0, value when it is 1) as offsets into strings
        .equ V_KNOCK, 0
        .equ V_MERCY, 4
        .equ V_WDROP, 8
        .equ V_AIR, 12
        .equ V_LADDER, 16
vnames: .word s_off-strings,  s_on-strings          | KNOCKBACK: 0 = off (Fair Knight), 1 = on (original)
        .word s_long-strings, s_normal-strings      | MERCY TIME
        .word s_on-strings,   s_off-strings         | WEAPON DROP: 0 = on (Fair Knight)
        .word s_full-strings, s_off-strings         | AIR CONTROL: 0 = full (Fair Knight)
        .word s_on-strings,   s_off-strings         | LADDER SAFETY: 0 = on (Fair Knight)
s_presets: .word s_knight-strings, s_legend-strings, s_orig-strings
strings:
s_preset: .asciz "PRESET"
s_knock:  .asciz "KNOCKBACK"
s_mercy:  .asciz "MERCY TIME"
s_wdrop:  .asciz "WEAPON DROP"
s_air:    .asciz "AIR CONTROL"
s_full:   .asciz "FULL"
s_ladder: .asciz "LADDER SAFETY"
s_exit:   .asciz "EXIT"
s_off:    .asciz "OFF"
s_on:     .asciz "ON"
s_long:   .asciz "LONG"
s_normal: .asciz "NORMAL"
s_knight: .asciz "KNIGHT"
s_legend: .asciz "LEGEND"
s_orig:   .asciz "ORIGINAL"
s_custom: .asciz "CUSTOM"
s_blank:  .asciz ""
d_preset: .asciz ""
d_knight: .asciz "FAIR KNIGHT RECOMMENDED SETTINGS"
d_legend: .asciz "ORIGINAL HITS  NEW CONTROLS AND HELP"
d_orig:   .asciz "PLAYS LIKE THE ORIGINAL GAME"
d_custom: .asciz "YOUR OWN MIX - A RESETS THE PRESET"
d_knock0: .asciz "A HIT DOES NOT THROW YOU BACK"
d_knock1: .asciz "ORIGINAL - A HIT THROWS YOU BACK"
d_mercy0: .asciz "TWICE THE SAFE TIME AFTER A HIT"
d_mercy1: .asciz "ORIGINAL SAFE TIME AFTER A HIT"
d_wdrop0: .asciz "OLD WEAPON LANDS BACK TOWARD START"
d_wdrop1: .asciz "ORIGINAL - YOUR OLD WEAPON IS LOST"
d_air0:   .asciz "STEER LEFT AND RIGHT IN THE AIR"
d_air1:   .asciz "ORIGINAL - JUMPS CANNOT BE STEERED"
d_lad0:   .asciz "SAFE FOR A MOMENT AT A LADDER TOP"
d_lad1:   .asciz "ORIGINAL - NO SAFE TIME ON LADDERS"
d_exit:   .asciz "PRESS START TO RETURN"
s_title:  .asciz "FAIR KNIGHT OPTIONS"
s_hint:   .asciz "C BUTTON - FAIR KNIGHT OPTIONS"
s_help1:  .asciz "UP DOWN MOVE   LEFT RIGHT CHANGE"
s_help2:  .asciz "A RESET PRESET   START EXIT"
        .even
| ASCII $20-$5A -> the game's font tiles (0 = blank). No Q or Z in the font.
font:
        .word 0                                             | space
        .word 0x561,0,0,0,0,0,0,0,0,0,0,0                   | ! " # $ % & ' ( ) * + ,
        .word 0x560,0,0                                     | - . /
        .word 0x564,0x562,0x563,0x567,0x568,0x569,0x56A,0x56B,0x56C,0x56D   | 0-9 (0,3-9 second style)
        .word 0,0,0,0,0,0,0                                 | : ; < = > ? @
        .word 0x54B,0x54C,0x54D,0x54E,0x54F,0x550,0x551,0x552,0x553        | A-I
        .word 0x12C                                         | J
        .word 0x554,0x555,0x556,0x557,0x558,0x559           | K-P
        .word 0                                             | Q (none)
        .word 0x55A,0x55B,0x55C,0x55D                       | R-U
        .word 0x12D,0x55E,0x12E,0x55F                       | V W X Y
        .word 0                                             | Z (none)
