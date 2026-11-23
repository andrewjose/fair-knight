# Fair Knight — Super Ghouls 'n Ghosts (SNES) — Changelog

Built on **Super Ghouls 'N Ghosts — Enhanced Arthur v1.2 by GoodLuckTrying**
(`Super Ghouls n Ghosts (Enhanced Arthur v1.2).sfc`, MD5 `3ca29fc2defbf638aeb0ea38036b7215`, CRC32 `BA05AFB5`),
which itself is built on Super Ghouls'n Ghosts (USA) (MD5 `19b2d7a555ecef4c453a819e67e61574`, CRC32 `6AABA901`).
Enhanced Arthur's readme credits FredYeye (disassembly, 1-Up Fix and more) and Funghi (Sword port, powerup and
special attack), and thanks Zarby89. All of Enhanced Arthur's features are theirs; Fair Knight only adds the items
below and a front end that turns the fair setup on by default.
Source and tooling: the combined Fair Knight repo (`SNES/`). The repo ships only Fair Knight's own code and patches, never Enhanced Arthur's files.

## v0.2 — leaderboard knows about knockback

### Plain-language overview
- Enhanced Arthur keeps separate high-score boards (CLEAN, MINIMAL, ENHANCED, OTHER) depending on which helpers you use. Turning knockback off makes the game easier, so a run with KNOCKBACK OFF now always goes on the OTHER board, never CLEAN.
- KNIGHT and LEGEND runs were already on OTHER (they use Enhanced plus other helpers). ORIGINAL runs stay on CLEAN.

### Engineer level
- The base decides the board from a bitmask of its settings. Fair Knight replaces the small function that turns the bitmask into a board number with an identical copy that also sets the "other" bit when knockback is off.
- **Tested:** game over with all base settings off: knockback ON → board 0 (CLEAN), knockback OFF → board 3 (OTHER), checked on the leaderboard screen. v0.1 tests rerun (page, knockback, continues, ORIGINAL comparison): unchanged.

### Deep technical
- Site `0C:F291` `20 46 F2 8F 90 AF 7E` (JSR `$F246` / STA `$7EAF90`) → JSL `fk_cls` + 3 NOP. `fk_cls` ORs `$80` into the mask when FK_SET bit 0 = 0, then reproduces `0C:F246` (0 → 0, 8 → 2, `mask & $9E` ≠ 0 → 3, else 1; stores the mask in `$7EAFA6` on the general path) and stores the board in `$7EAF90`. The mask comes from `$7EF329` (+ bit 0 from `$7EF328` bit 5) at `0C:F26A`; bit 7 is the base's own "shield PERM" flag (`0C:F237`), which already means OTHER.
- Unlimited continues are not part of the board decision (the base doesn't track continues).

## v0.1 — FAIR KNIGHT options page, knockback, unlimited continues

### Plain-language overview
- **New page:** on the OPTION MODE screen press **X** ("X FOR FAIR KNIGHT OPTIONS") to open FAIR KNIGHT OPTIONS.
  - PRESET: KNIGHT / LEGEND / ORIGINAL (CUSTOM appears when you change something by hand; **A** puts the preset back).
  - KNOCKBACK, plus four of Enhanced Arthur's own settings so they don't need the hidden L+START menu: CHEST HINTS, ENHANCED, BETTER ARMOR, WEAPON (OFF / COLLECT / DROP).
  - Left/Right changes, Up/Down moves, START goes back. The page hides the blue frame so the text is readable.
- **KNIGHT is the default** the first time the game is switched on: chest hints, Enhanced controls, better armor, weapon collecting, and no knockback.
  - LEGEND: the same help, but hits work like the original (knockback on, armor not stepped down).
  - ORIGINAL: everything off, plays like the original game (the Classic edition differs only in chest hints, see below).
- **KNOCKBACK OFF:** when you're hit, Arthur still hops and flashes, but straight up: he isn't thrown backwards into a pit or another enemy.
- **Unlimited continues:** the CREDIT number on the CONTINUE screen no longer goes down. CONTINUE is already the highlighted choice after a game over.
- Settings are saved with the game's own save (battery SRAM), so they stay after switching off.
- **Classic edition:** identical, except no preset turns chest hints (the sparkles) on. Fair Knight adds no new graphics in either edition.

### Engineer level
- The game runs most screens as cooperative "objects": each object's code loops and calls a one-frame "yield" (the `BRK` instruction). The yield saves only the program counter, not the call stack, so code can only yield at the object's top level. The FAIR KNIGHT page therefore runs as a small state machine inside the OPTION MODE object's input check: while the page is open, our hook consumes every button press and reports "no input" back to the game, so the game's own menu never sees it.
- Text is written into the game's off-screen copy of the text layer (a WRAM buffer that the vertical-blank interrupt copies to video memory when a flag is set), using the game's own font tiles, so nothing new is drawn.
- Settings: the base already saves its secret-menu settings in SRAM with a signature and checksum. Fair Knight writes the same bytes (same format, so the base menu and leaderboard read them normally) and keeps its own byte, signature and preset in an SRAM area the base never uses. On first boot (no Fair Knight signature) it applies KNIGHT.
- Knockback: when Arthur is hit, the game loads a "hop" velocity (horizontal + vertical) from a table. The hook calls the original loader, then zeroes the horizontal part when knockback is off.
- Continues: the counter is decremented with a BCD subtract of 1; it's now a subtract of 0.
- Mercy (invulnerability after a hit) was not changed: the base already gives 126 frames (2.1 s) after landing, plus the hop itself, which is longer than the ~2 s target.
- **Tested** (headless Snes9x core, scripted input, screenshots read):
  - page: open, every row, presets cycle and apply, CUSTOM detection, A reset, weapon 0/1/2, exit back to OPTION MODE with labels and values intact, base secret menu shows the same values, SRAM signature/checksum valid, settings survive a reboot;
  - knockback: same zombie hit at frame 1019 in stage 1: base Arthur X 128 → 73 over 60 frames; Fair Knight X stays 128 (hop is vertical only); with KNOCKBACK ON identical to base;
  - continues: base CREDIT 5 → 4 after CONTINUE, Fair Knight stays 5; CONTINUE preselected;
  - ORIGINAL settings vs the unpatched base, 2,100–4,000 frames of scripted play: identical except 4 isolated frames where a background column is drawn one frame apart (sub-frame timing from the extra code at boot/hit; the game state never diverges).
- Leaderboard: the base files runs by its own settings only. KNIGHT and LEGEND land in **OTHER** (Enhanced + more). Knockback is not seen by the classifier: ORIGINAL base settings with KNOCKBACK OFF would be filed as CLEAN (fixed in v0.2).

### Deep technical
- Free space: banks `$20-$3D` are zero-filled padding in the 2 MiB base; Fair Knight code/data is in bank `$38` (`$38:8000`, file `0x1C0000`, ~2.3 KB). Build asserts the bank is blank.
- Hook sites (build.py asserts original bytes):

  | Site | Original | New | Purpose |
  |---|---|---|---|
  | `01:D7ED` | `22 48 88 01` JSL `$018848` | JSL `fk_kb` | hit hop velocity (`$16-$18` horizontal, `$19-$1B` vertical, Arthur DP `$043C`) |
  | `04:96CC` | `E9 01` SBC #1 | `E9 00` | continue credits `$0290` (BCD) |
  | `03:EA29` | `22 C5 F2 0C` JSL `$0CF2C5` | JSL `fk_boot` | boot, right after the base's settings load `03:FE52` |
  | `03:B92E` | `22 56 97 04` JSL `$049756` | JSL `fk_optdraw` | OPTION MODE labels (X=0, DB=0: pointer table `$00:DA9E`) + our hint row 2 |
  | `03:B939` | `AD BB 02 0D BC 02` | JSL `fk_optin`, NOP, NOP | OPTION MODE "any new press" test (the `BEQ $B937` after it is kept) |
- RAM/SRAM:
  - Base secret settings `$7E:1FF0-1FF6` = chest hints, slower timer, better armor, enhanced, weapon (0 OFF, 1 COLLECT, 2 DROP), shield (0-2), 1-up fix; tripping `$1FFA`, sword `$1FFC`. Saved by `03:FEE7` to `$70:0000` 'SG', `$70:0002-0008` (masked: indices 4-5 `&3`, others `&1`), sum at `$70:0009`; main options `$1FD9-1FDC` → `$70:000A-000E`. `fk_page` reproduces the 'SG' + 7 bytes + sum part.
  - Fair Knight SRAM `$70:1F00` 'F','K'; `1F02` FK_SET (bit 0 = knockback ON); `1F03` preset; `1F04-1F0D` page scratch (cursor, temp, active flag, saved `$02D5`). Base SRAM use ends at `$70:10E2`.
  - Joypad new presses `$02BB` (A `$80` X `$40` L `$20` R `$10`) and `$02BC` (B `$80` Y `$40` Sel `$20` Start `$10` Up 8 Down 4 Left 2 Right 1). OPTION MODE cursor: object DP `$090F`, `$0F` → `$091E`.
  - Text layer buffer `$7F:9000` (32×32 entries, `tile | attr<<8`), upload request `INC $0323`. Font: tiles `0-9` digits, `$0A-$23` A–Z, `$45` blank. Attributes: `$1C` title red, `$18` purple, `$00` orange, `$04` white.
  - Main-screen layers shadow `$02D5` (NMI → `$212C`); OPTION MODE uses `$05`; the page sets `$04` (BG3 text only) and restores it.
  - Object yield = `BRK #$00`: handler `00:8B08` pops P/PC/PB into the object's DP `$02-$05` and jumps to the scheduler; the stack is not preserved, hence the state-machine page.
  - Arthur object DP `$043C`: X px `$045B`, Y `$045E`, state `$0478` (9 = hit hop), mercy `$046A` (`$2E`, set to `$7E` at `01:D88C` on landing).
- Presets (`pre_tab`, `$FF` = leave alone): KNIGHT chest 1 (Classic 0), armor 1, enhanced 1, weapon 1, FK_SET 0; LEGEND chest 1 (Classic 0), armor 0, enhanced 1, weapon 1, FK_SET 1; ORIGINAL all seven base bytes 0, FK_SET 1. Tripping and sword are never touched. The shown preset is computed by comparing the current values with the remembered preset's table (else CUSTOM).
- Tools: `tools/build.py` (ca65/ld65; one memory area per site, generated config), `tools/mkdata.py` (page text/tables), `tools/package.py`, `tools/mkpatch.py`; tests `t_page.py`, `t_kb.py`, `t_cont.py`, `t_orig.py`, `t_persist.py`, `t_secret.py`; `lr.py` (ctypes libretro frontend for the Debian `libretro-snes9x` core), `nav.py`, `dis816.py` (65816 disassembler with REP/SEP tracking).
- Dead ends: running the page as its own loop with `BRK` yields inside a JSL crashed the game (stack not preserved by the yield) and corrupted SRAM byte 0; calling `$049756` with DB=$38 printed nothing (its pointer table is read with DB=0).
- Not done yet: ladder safety (not yet checked whether SGnG ladders have the top-of-ladder problem), fair spawns, endgame aid.
