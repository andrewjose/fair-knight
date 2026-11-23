| Fair Knight (Genesis) - shared constants. GNU as, m68k MIT/Motorola mix, --register-prefix-optional.
| Settings live in RAM the game never touches after boot ($FF5A00 block; boot clears it to 0 = KNIGHT).
        .equ FK_RAM,     0xFF5A00
        .equ FK_SET,     FK_RAM+0     | byte: inverted option bits, 0 = Fair Knight behaviour
        .equ FK_PRESET,  FK_RAM+1     | byte: 0 KNIGHT, 1 LEGEND, 2 ORIGINAL, 3 CUSTOM
        .equ FK_SET2,    FK_RAM+2     | byte: more option bits (same scheme)
        .equ FK_CUR,     FK_RAM+3     | byte: FAIR KNIGHT page cursor
        .equ FK_DROPOBJ,FK_RAM+6     | long: item object relaunched by WEAPON DROP (keeps its weapon on landing)
        .equ FK_TMP,     FK_RAM+4     | word scratch
| FK_SET bits (1 = original game behaviour)
        .equ FKB_KNOCK,  0            | 0: no knockback on a hit
        .equ FKB_MERCY,  1            | 0: long mercy (240 frames)
        .equ FKB_WDROP,  2            | 0: old weapon dropped toward the stage start
        .equ FKB_AIR,    3            | 0: full air control
        .equ FKB_SPAWN,  4            | 0: fair spawns
        .equ FKB_ENDG,   5            | 0: endgame aid
        .equ FKB_SECR0,  6            | secrets: bits 7-6 = 00 SPARKLES, 01 MAP, 11 OFF
        .equ FKB_SECR1,  7
| FK_SET2 bits
        .equ FKB_LADDER, 0            | 0: ladder safety
