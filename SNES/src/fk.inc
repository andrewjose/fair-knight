; ---- SRAM (bank $70; the base uses $0000-$10E2, $1100-$1FFF is unused)
FK_SIG   = $701F00          ; 'F','K' once initialised
FK_SET   = $701F02          ; Fair Knight settings, bit = 1 means original behaviour
FK_PRE   = $701F03          ; last chosen preset 0 KNIGHT 1 LEGEND 2 ORIGINAL
FK_CUR   = $701F04          ; page cursor row
FK_T     = $701F05          ; scratch
FK_ATR   = $701F06          ; puts attribute
S_KNOCK  = $01              ; knockback ON (original)
; ---- the base's settings (WRAM; bank $38 sees $0000-$1FFF as WRAM)
B_CHEST  = $1FF0
B_SLOW   = $1FF1
B_ARMOR  = $1FF2
B_ENH    = $1FF3
B_WEAP   = $1FF4            ; 0 OFF 1 COLLECT 2 DROP
B_SHIELD = $1FF5
B_1UP    = $1FF6
B_TRIP   = $1FFA
B_SWORD  = $1FFC
PAD_LO   = $02BB            ; newly pressed: A $80 X $40 L $20 R $10
PAD_HI   = $02BC            ; newly pressed: B $80 Y $40 Sel $20 Start $10 Up 8 Down 4 Left 2 Right 1
TILEBUF  = $7F9000          ; text BG tilemap buffer, 32 cells x 2 bytes per row
; ---- tiles/attributes of the game's menu font
ATR_TITLE = $1C
ATR_LABEL = $18             ; purple
ATR_VAL   = $00             ; orange
ATR_SEL   = $04             ; white (selected)
HINT_ROW = 2
HINT_COL = 3
.charmap $20,$45
.repeat 10,i
  .charmap $30+i,i
.endrepeat
.repeat 26,i
  .charmap $41+i,$0A+i
.endrepeat
FK_TMP   = $701F08          ; 16-bit scratch
FK_TMP2  = $701F0A          ; 16-bit scratch
FK_ROW   = $701F07          ; draw: row counter
FK_ACT   = $701F0C          ; 1 while the FAIR KNIGHT page is open
FK_TM    = $701F0D          ; saved main-screen layers ($02D5) while the page is open
