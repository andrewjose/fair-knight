; Fair Knight shared definitions (NES, Ghosts'n Goblins USA)
; ---- RAM (verified unused: never written in ~45k frames of play, survives game start/over)
FK_SET   = $07FA   ; settings byte 1. A SET bit means ORIGINAL behaviour, so power-on (RAM = 0) = Knight defaults
  FKS_KNOCKBACK = $80   ; bit7: 1 = original knockback, 0 = no knockback
  FKS_MERCY     = $40   ; bit6: 1 = original mercy time (30 ticks), 0 = long (60 ticks)
FK_SET2  = $07FB   ; settings byte 2 (reserved)
FK_TMP   = $07FC
FK_RET   = $07FD
; ---- game routines (bank 7, fixed)
YIELD      = $DB90   ; per-tick update + yield to scheduler
HOP_UP     = $DF04
HOP_PEAK   = $DF33
HOP_DOWN   = $DF3C
WALLCHK    = $DF62   ; carry set = blocked in move direction
ADDVEL     = $F03E   ; A = speed index, adds velocity to X
POSFIX     = $DBFB
LANDCHK    = $E3E3   ; carry set = landed
LANDED     = $E166
  FKS_WDROP     = $20   ; bit5: 1 = original weapon pickup (no drop), 0 = old weapon drops behind Arthur
; ---- far-call plumbing (fixed bank -> FK code in bank 2)
FAR        = $FFE8   ; LDY #id / JSR FAR   (A clobbered, X kept, carry returned)
FAR_TAIL   = $DA6A
FK_BANK    = 2
CUR_BANK   = $C7     ; game's current-bank shadow (NMI restores it)
; handler ids
FKID_WPICK = 0
FKID_TITLE = 1
FK_PRESET  = FK_SET2  ; preset index: 0 KNIGHT, 1 LEGEND, 2 ORIGINAL
PPU_PRINT  = $EECF    ; queue a nametable write: $25:$24 addr, $23 len, $22 rows, ($26) src
PAD        = $42      ; buttons held: A $80 B $40 Sel $20 Start $10 Up $08 Down $04 Left $02 Right $01
FKID_TCUR  = 2
FKID_OPT   = 3
FK_CUR     = $07FE   ; options screen: cursor row (title tick resets it)
FK_JOB     = $07FF   ; options screen: round-robin draw job (title tick resets it)
  FKP_CUSTOM = $04   ; FK_PRESET bit 2: settings were changed by hand (bits 0-1 keep the base preset)
; ---- v0.3 ----------------------------------------------------------------
  FKS_LADDER    = $10   ; bit4: 1 = original (no ladder-top safety), 0 = brief invincibility stepping off a ladder top
  FKS_AIR       = $0C   ; bits3-2: 00 FULL, 01 ASSIST, 11 OFF (original fixed arc)  [swapped in v0.5.2]
  FKS_AIR_ASSIST = $04
  FKS_SECRETS   = $03   ; bits1-0: 00 SPARKLES, 01 MAP, 11 OFF  [swapped in v0.5.2]
  FKP_ENDGAME   = $80   ; FK_PRESET bit7: 1 = original (no endgame aid), 0 = cross guaranteed in stage 6
FKID_LADDER = 4
FKID_AIR12  = 5
FKID_AIR6   = 6
FKID_SEC    = 7
FAR_SEC     = $FFF5   ; JSR here = far call with Y = FKID_SEC (5-byte stub after FAR)
; extra Fair Knight RAM (never written / never non-zero in a 14-section stage-select survey, ramsurvey2.py)
FK_SPD   = $04C0      ; air: speed for this step
FK_WANT  = $04C1      ; air: wanted direction ($04 right / $0C left)
FK_AIRH  = $04C2      ; air FULL: 1 = next step at half speed (acceleration)
FK_EGCD  = $04C3      ; endgame aid: seconds before another cross may appear
; game routines used by v0.3 handlers
SNAPY      = $E166    ; snap object Y to the 16-px grid (landing)
LADTOP_ANIM= $DC5B
STAND      = $DB65    ; Arthur standing/walking state
JUMPWALL   = $DF5D    ; jump: $065D moving? then wall check (carry set = no move)
FREESLOT   = $DA18    ; Y = free object slot 1..16, carry set = none
; ---- v0.4 ----------------------------------------------------------------
FKID_READY  = 8       ; READY screen: secrets summary (from $C9E2)
FKID_SPARK  = 9       ; hidden item waiting tick: sparkle (bank 4 $BB8C)
FKID_SFOUND = 10      ; hidden item touched: record it (bank 4 $BBB9)
FK_SFOUND   = $04C4   ; 4 bytes: one bit per hidden item (secrets.inc order), per power-on session
FK_SSIG     = $04C8   ; $A5 once FK_SFOUND has been cleared (RAM is random at power-on on hardware)
  FKS_SECRETS_SPARK = $00  ; FKS_SECRETS value for MAP+SPARKLES (v0.5.2: the default)
EG_X        = 214     ; endgame aid cross: stage 6, floor below the boss floor (world X 214, Y $1BA)
; ---- v0.5 FAIR SPAWNS ------------------------------------------------------
  FKP_FAIRSP  = $40   ; FK_PRESET bit6: 1 = original spawns, 0 = fair spawns
FKID_FSHIT  = 11      ; Arthur hit check ($E014): cancel touches from enemies still in their spawn telegraph
FK_AGE      = $04C9   ; 8 bytes: one nibble per object slot 1-16 (slot&15). 0 unseen, 2-14 telegraph ticks left, 15 settled
FK_HFL      = $04D1   ; hit-check scratch: bit0 telegraph object near Arthur, bit1 other object near
FS_TEL      = 8       ; telegraph length: 7 spawn ticks of 3 frames (about 21 frames)
FS_ZCAP     = 3       ; zombie waves start only while fewer than this many zombies are out (wave = up to 3 more)
FK_OCUR     = FK_HFL  ; options screen only: row where the cursor heart is drawn ($FF = none); gameplay reuses it as hit-check scratch
