# Fair Knight (NES) — changelog

Base ROM: Ghosts'n Goblins (USA).nes, MD5 80dcd911aaa221fd3de883d5128eb97c.

## v0.5.3 — 2026-11-16  (FairKnight-NES-v0.5.3.ips, patched ROM MD5 44bfafdd69286d6253712462d0378a91)

**Plain language**
- Fixed: on the title screen, Select no longer stops on an empty row between 2 PLAYERS and OPTIONS. That blank row is where CONTINUE appears after a game over, and the cursor now skips it until then.

**For software engineers**
- The original US title keeps three cursor rows: 1 PLAYER, 2 PLAYERS and CONTINUE. The CONTINUE text is only drawn when there is a game to continue, but the cursor could still land on the blank row.
- Adding OPTIONS below it made the gap obvious. The Select handler now checks the game's "can continue" flag and jumps past that row while the flag is clear.

**Deep technical**
- `title` (FK id 1): after `INC $A3`, if `$A3` = 2 and `$BB` = 0, it adds another `$10` to the cursor Y and increments `$A3` again.
- A `CLC` is needed there because the preceding `CPY` sets carry; without it the cursor ended up at Y = `$C3`.
- Tests:
  - fresh boot: Select cycles rows 0 → 1 → 3 → 0;
  - after a real game over (lives `$0715` = 1, then let Arthur die): the title opens on CONTINUE and cycles 2 → 3 → 0 → 1;
  - `t_opt.to_options` now presses Select until `$A3` = 3;
  - `t_menu5.py` and `t_orig.py` give the same results as v0.5.2.
- Test note: poking `$0715` = 0 hangs the clean ROM as well (black screen), so use 1 to force a game over.

## v0.5.2 — 2026-11-16  (FairKnight-NES-v0.5.2.ips, patched ROM MD5 3a78687e1d1e2493c6995ac32e4d48ce)

**Plain language**
- AIR CONTROL now defaults to FULL in KNIGHT and LEGEND: hold the other direction mid-jump to turn back. ASSIST is still in the menu but needs polish.
- SECRETS now defaults to SPARKLES in KNIGHT. LEGEND and ORIGINAL keep secrets off.
- LEGEND's description now reads "ORIGINAL HITS  AIR CONTROL".

**For software engineers**
- Settings are inverted bits, so all-zero RAM at power-on is the KNIGHT preset with no init code.
- To make FULL and SPARKLES the power-on default, their encodings were swapped with ASSIST and MAP rather than adding initialisation code.
- The menu's value tables were reordered to match.

**Deep technical**
- `FKS_AIR` bits 3-2: 00 FULL, 01 ASSIST (`FKS_AIR_ASSIST` = `$04`), 11 OFF. The `air12`/`air6` handler now branches `CMP #FKS_AIR_ASSIST / BNE @full`.
- `FKS_SECRETS` bits 1-0: 00 SPARKLES (`FKS_SECRETS_SPARK` = `$00`), 01 MAP, 11 OFF.
- `VN`/`VD` value and description tables swapped for both rows. LEGEND preset `FK_SET`: `$DF` → `$D3`.
- Tests:
  - `t_air.py`: labels swapped; FULL reverses (lands at X 111 vs 202), ASSIST brakes.
  - `t_secrets.py`: setfk values swapped; duck, normal and red markers visible, OFF shows nothing, MAP list after a death.
  - `t_orig.py`: unchanged from v0.5.
  - Menu screenshots checked for KNIGHT and LEGEND.

## v0.5.1 — 2026-11-16  (FairKnight-NES-v0.5.1.ips, patched ROM MD5 9c121d448cfdb74d4f7612f7f5d66150)

**Plain language**
- Fixed: the options screen no longer flickers. It used to jump up and down every other frame.
- Changed: a dropped weapon now always lands back toward the start of the stage (to the left), whichever way Arthur faces.

**For software engineers**
- The NES can only safely write to the screen during a short window between frames, and the game switches the picture off while it does. The options screen queued about 120 tiles of text per update: the cursor column, the description and a chunk of the menu. That overran the window, so the picture switched back on late and the screen visibly jumped.
- The screen now draws incrementally: at most one piece per update, and only when something changed. Redrawing the cursor now means erasing one tile and drawing one, not rewriting a whole column.
- On an idle screen nothing is written at all.

**Deep technical**
- `FK_JOB` (`$07FF`) bits: 7 = drawn (input on); 6 = cursor/description dirty; 0-5 = job, with `$3F` meaning idle.
- `draw` does either the dirty cursor plus description, or one job, never both. The full-height `curcol` column write (21 single-tile queue entries per tick) is gone.
- The cursor is now two single-tile writes. The heart's row is tracked in `FK_OCUR` = `$04D1`, which is shared with the gameplay hit-check scratch and is never live at the same time; the title tick resets it to `$FF`.
- Measured with cynes: the first lit scanline is 17 on all 650 sampled frames, against 17/23/31 alternating in v0.5.
- Weapon drop (`wpick`): the facing branch on `$05F1` bit 3 is removed. The drop is always `$05AF - 24` (with borrow into `$0583`).
- Regression: `t_orig.py` is identical to v0.5 (the 600 idle frames match; the bot run has only the known frame-191 sampling artefact). `t_menu5.py` covers every row, value, wrap and exit.

## v0.5 — 2026-11-16  (FairKnight-NES-v0.5.ips, patched ROM MD5 01ff3aab2481623bd5fa37a5b418d6fc)

**Plain language**
- New FAIR SPAWNS option (ON in KNIGHT and LEGEND, OFF in ORIGINAL).
- No more than 3 graveyard zombies start rising at once. In a 2,500-frame stand-still test, at most 4 zombies were out at once, against 7 in the original.
- A newly appeared enemy can't hurt Arthur for about a third of a second (its "appear" animation is the warning).
- Enemies that fly in from the screen edge can't appear right next to Arthur any more: they now start at least 32 pixels away (original: 26).
- Graveyard zombies already rose at least 48 pixels away in the original, so that is unchanged.
- Red Arremer already hovers for about 12 frames before diving, which works as a warning, so it is untouched.
- ORIGINAL still plays exactly like the unmodified game. The game doesn't run any slower.

**For software engineers**
- Fair spawns doesn't touch the seven enemy "generator" routines. It wraps them.
- A guard clause in front of the zombie generator skips a wave while 3 or more zombies exist.
- After all spawners run each tick, one pass over the 16 object slots spots newly occupied slots and gives each an "age" (4 bits per slot, packed into 8 bytes).
- Arthur's hit check is wrapped like middleware: if the only thing touching him is still young, the hit is dropped for that tick and re-checked next tick.
- New generator enemies that appear within 32 px are moved to 36 px, on the side they came from.

**Deep technical**
- Sites: bank 2 `$8400` `JSR fk_zgen` (cap, `FS_ZCAP` = 3); bank 2 `$8412` `JMP fk_gen` (runs `$8748`, then the age pass); bank 7 `$E014` → FK id 11 `fshit`.
- RAM: ages at `$04C9-$04D0`, scratch `$04D1`; option bit `$07FB` bit 6.
- Code in the new region `BANK2B`, bank 2 `$BB67-$BE66`.
- Telegraph: `FS_TEL` = 8 ages ≈ 7 spawn ticks ≈ 21 frames. Measured first hit at 22 frames vs 7 in the clean ROM.
- Push-out: `FS_PUSH` = 36.
- Tests: `t_fs_dist.py`, `t_fs_tel2.py`, `t_play5.py`, `t_menu5.py`, `t_fs_lag.py`, `t_orig5.py`, `t_f191.py`, plus the v0.4 regression set `t_play.py`, `t_ladder.py`, `t_air.py`, `t_endgame2.py`, `t_secrets.py`. All pass.
- The single frame-191 `$04F0` difference in the 2,600-frame bot runs is a frame-cut sampling artefact. Full RAM is identical at frames 189, 190, 192 and 193.

## v0.4 — 2026-11-15  (FairKnight-NES-v0.4.ips, patched ROM MD5 5464919343d36f655b1e812c00ce91bb)

### What's new (plain language)
- **Endgame aid, fixed spot.** The cross no longer pops up in front of Arthur. It now waits on the floor just below the stage 6 boss, a few steps left of the last ladder, whenever Arthur doesn't already have it. If he dies or continues it's there again when he comes back. You still need the cross to finish; the aid just guarantees one is on the way. ORIGINAL, LEGEND and ENDGAME AID OFF keep the original "back to stage 5" rule.
- **Secret markers.** New menu line SECRETS:
  - MAP (KNIGHT default): the READY screen before each life lists every stage's hidden items. A grey heart means found, a dot means not yet. Example: `4 .♥♥.` = stage 4 has four, you've found the middle two.
  - SPARKLES: the same list, plus a small blinking spark in the level where each hidden item is triggered. A bigger four-point star means "duck here". A solid red star means the item is a bad one (the time-down Yashichi).
  - OFF (LEGEND, ORIGINAL): nothing shown, as in the original.
  - Found items are remembered until the console is switched off. They aren't saved.
- 29 hidden items in total: stage 1: 4, stage 2: 5, stage 3: 7, stage 4: 4, stage 5: 4, stage 6: 5, final room: none.

### For software engineers
- **Where the secrets come from.** Each stage section has an *event list* in ROM: 8-byte records that say "when the screen reaches page P, create object type T with parameter K at (X, Y)". Hidden items are type `$11`. A Python extractor (`tools/secrets_extract.py`) walks all 14 lists and writes both a CSV for people and an include file (`src/secrets.inc`) for the assembler, so the marker table is generated from the ROM rather than typed by hand.
- **Found tracking.** The game's own hidden-item code decides when an item is revealed. Fair Knight hooks that one moment (a far call), looks the item up in the generated table by section + X + Y, and sets a bit in a 4-byte bitfield in free RAM. A signature byte clears the bits once per power-on.
- **Sparkles** hook the item's "waiting" branch, which normally sets an invisible sprite. With SPARKLES on it sets a visible one on alternate 8-tick windows and picks a palette for harmful kinds. Hit-tests still use the same object, so behaviour is unchanged.
- **READY screen** gets one extra far call that queues three text rows into the game's PPU write queue before the original screen timer starts.
- **Endgame aid** keeps the once-per-second hook from v0.3 but now spawns at a fixed world position when Arthur is on the top two floors and near it. The "is there already a cross?" check only counts crosses on those floors (a dropped cross lower in the tower can stay loaded and would otherwise block it — caught in testing).

### Deep technical
ROM-MAP.md §3.9. New sites: bank 4 `$BB8C` (8 bytes, FK id 9 spark), bank 4 `$BBB9` (17 bytes, FK id 10 found), bank 7 `$C9E2` (14 bytes, FK id 8 READY). RAM `$04C4-$04C7` found bits, `$04C8` signature `$A5`. `$07FA` bits 1-0 SECRETS (`00` MAP, `01` SPARKLES, `11` OFF). Endgame cross at X 214, Y `$1BA` (floor y = 440). `$04C3` (old cooldown) is now unused.

### Tests (headless, cynes, screenshots checked)
- **ORIGINAL vs clean** (`t_orig.py`): 0 mismatches over the 600-frame idle and 2,600-frame bot runs.
- **Options screen** (`t_menu4.py`): every row and value including SECRETS MAP/SPARKLES/OFF, Select reset, wrap, exit.
- **Extractor** (`secrets_extract.py` + `t_secret_validate.py`): 29 triggers. Two were played for real in stage 4B: a duck trigger at X 1264 (cross) and a jump trigger at X 2160. Both revealed their item where the table says.
- **Secrets** (`t_secrets.py`): revealing those two set found bits 17 and 18. The bits survive a death. The READY screen shows `4 .♥♥.` in the right place. Sparkles appear for a duck spot (star), a normal spot (spark) and the stage 1 time-down spot (red star). OFF draws nothing and skips the list.
- **Endgame aid** (`t_endgame2.py`, from a stage 6 save state on floor 12 holding the lance):
  - KNIGHT: the cross appears at X 214 on the floor below the boss. It hasn't moved 2 s later.
  - Removed, it comes back within a second.
  - Walking over it picks it up. No new cross spawns while holding it.
  - Stage clear goes 12 → 13.
  - ORIGINAL and ENDGAME AID OFF: no cross, and clear goes 12 → 11 (the original rule).

### Not done / limits
- No down-arrow sprite is loaded in every stage, so "duck here" is a bigger star rather than an arrow.
- The list is on the READY screen, not on the stage-intro map. The map screen is drawn by bank 1 code with no free room nearby; the READY screen was the cheapest place that shows before every life.
- Red depends on each stage's sprite palette 1. It's checked in stage 1 (the only harmful item) and stage 4.
- Not tested: whether a thrown weapon behaves differently passing through a sparkle. It shouldn't, because only the sprite id and the draw bit change, and the original object handler still runs.
- Type `$20` spots (shoot one place for a while to reveal a bonus magician, ~2000 points) aren't counted as secrets.

## v0.3 — 2026-11-15  (FairKnight-NES-v0.3.ips, patched ROM MD5 d9ac1420aef94df760d05589f45a96ca)

### What's new (plain language)
- **Ladder safety.** Stepping off the top of a ladder gives Arthur a short moment of invincibility (about 0.7 s, he flashes), so an enemy waiting at the top can't hit him the instant he arrives. Menu line LADDER SAFETY ON/OFF.
- **Air control.** Menu line AIR CONTROL:
  - ASSIST (KNIGHT default): during a running jump, hold the opposite direction to stop moving sideways. You can't turn around in the air.
  - FULL: steer freely in the air. Turning around passes through a stop and a slower step first, so jumps still feel heavy. A jump straight up can drift either way.
  - OFF: the original fixed jumps.
  - Jump height never changes, and being hit still throws you exactly as the KNOCKBACK setting says.
- **Endgame aid.** In the original, if you finish stage 6 without the cross you're sent back to stage 5. With ENDGAME AID ON (KNIGHT default), a cross appears in front of Arthur in stage 6 whenever he doesn't have one. If it scrolls away, another appears a few seconds later. The rule itself is unchanged: you still need the cross.
- **Menu cursor** is now the small grey heart.
- Presets: KNIGHT turns all three on (air = ASSIST). LEGEND and ORIGINAL turn them off.

### For software engineers
- Every new feature is a **far call** from a few patched bytes in the always-mapped bank into Fair Knight code in bank 2, so almost no fixed-bank space is used.
  - The ladder-top exit and the three jump "move sideways one step" sites each became `LDY #id / JSR FAR`. The bank-2 handler either repeats the original calls exactly (option off) or does the new behaviour.
  - That's why ORIGINAL still matches the clean ROM frame for frame: with an option off, the same routines run in the same order.
- The endgame aid runs **once per second** through a hook in the stage timer. It reuses the game's own object system: find a free slot, fill in an "item" object (type `$10`, kind 9 = cross), mark it active, and the game's item code handles drawing and pickup.
- The options screen is now **table-driven for 2- and 3-value options** stored in either settings byte. Adding the next option (SECRETS is reserved) is a table entry.
- New scratch RAM `$04C0-$04C3` comes from a survey of all 14 stage sections via the game's built-in stage select.

### Deep technical
ROM-MAP.md §3.8. New sites: `$DD90` (ladder top, FK id 4), `$DE40`/`$DE86`/`$DEC9` (jump steps, FK ids 5/6), `$D3AD` → stub `$E562` → `$FFF5` (per-second hook, FK id 7). Endgame rule: bank 7 `$D44E-$D45E`. Settings: `$07FA` bit 4 ladder, bits 3-2 air, `$07FB` bit 7 endgame.

### Tests (headless, cynes, screenshots checked)
- **ORIGINAL vs clean ROM** (`tools/t_orig.py`): 600-frame idle and 2,600-frame bot run from stage 1. Arthur X/Y/flags/arc, lives, weapon, mercy, timer, score and scroll were identical on every frame (0 mismatches). The bot run includes jumps, so the air-control sites are exercised.
- **Ladder** (`tools/t_ladder.py`, stage 5 section 11, enemies cleared): clean and ORIGINAL climb identically with no invincibility. KNIGHT climbs identically and is invincible for 42 frames from the step-off (frame 79); screenshots show Arthur flashing at the ladder top.
- **Air control** (`tools/t_air.py`, stage 1), world-X distance over the jump:

  | Mode | Running jump, then hold Left | Standing jump, then hold Right |
  |---|---|---|
  | Clean | +76 | 0 |
  | OFF | +76 (identical) | 0 |
  | ASSIST | +16, stops | 0 |
  | FULL | −15, reverses | +66 |

  All modes land on the same frame (41), so jump height is unchanged.
- **Endgame** (`tools/t_endgame.py`, stage 6 = section 12; stage finished with Action Replay `$BF=1`):
  - Clean and ORIGINAL with no cross go section 12 → 11 (sent back).
  - KNIGHT gets a cross item 40 px ahead of Arthur, picks it up, and goes 12 → 13 (screen "STAGE 7").
- **Menu** (`tools/t_menu3.py`): every row and value both ways (AIR cycles 3 values), presets, CUSTOM, Select reset, wrap, EXIT no-op, return to the title.
- KNIGHT idle hit/death run is identical to v0.2.

### Not done
- **Secret markers.** No menu row. The hidden-item trigger system isn't mapped yet; see ROM-MAP §5. StrategyWiki's NES page only gives vague positions for stage 1, so it can't serve as a cross-check by itself.
- Wall collision under FULL air control is checked in code (the wall test follows the current direction), but no wall jump was tested headlessly.

## v0.2 — 2026-11-15  (FairKnight-NES-v0.2.ips, patched ROM MD5 dead31dfaac9cfc7e0cba35171e78414)

### What's new (plain language)
- **Full OPTIONS screen.** The title menu now has a fourth line, OPTIONS (it replaces v0.1's MODE line). Press Select until the cursor is on OPTIONS, then Start.
  - Lines: PRESET (KNIGHT / LEGEND / ORIGINAL, shows CUSTOM after you change something by hand), KNOCKBACK (ON/OFF), MERCY TIME (NORMAL/LONG), WEAPON DROP (ON/OFF), EXIT.
  - Up/Down moves, Left/Right changes the highlighted line, Select resets everything to the preset, Start (or A on EXIT) returns to the title.
  - The line near the bottom explains whatever is highlighted.
  - The cursor is a "!" because the game's font has no arrow.
- Only options that already work are listed; new ones will be added to this screen as they're built.
- KEEP WEAPON is no longer planned: the original game already keeps your weapon when you continue.
- The options screen is reachable from the title only, not from the pause screen (see "Not yet").

### For software engineers
- The fixed (always-mapped) bank had about 40 spare bytes, so the options screen is a tiny loop there: yield one game tick, call the options handler in bank 2, repeat until it says "leave", then re-enter the title through the game's own title-init routine (the same path the attract demo uses). All menu logic, text and tables are in bank 2.
- The title's Select/cursor handling (originally 41 bytes in the fixed bank) was moved into bank 2 as part of the per-tick title handler, which freed the space for the loop.
- Menu rows are table-driven: one bit, two value strings and two descriptions per option. Adding an option is a table entry, not new code.
- The handler only queues a few short nametable writes per tick, because the game's PPU write queue sits right below the settings RAM and an overflow would corrupt it.

### Deep technical
ROM-MAP.md §3.6-3.7. New/changed sites: `$C4A5-$C4C5` (title tick -> FK id 1, optgate at `$C4AD`), `$C458` (`JMP optgate`), FK id 3 = options tick (bank 2). RAM: `$07FB` bit 2 = CUSTOM, `$07FE` cursor, `$07FF` draw job.

### Tests (headless, cynes, screenshots checked)
- Menu: every row visited, every value changed both ways, preset cycling both directions with wraparound, CUSTOM shown after a manual change, Select restores the base preset (KNIGHT and LEGEND), Up/Down wrap, Left/Right ignored on EXIT, Start returns to the title (cursor back on 1 PLAYER, OPTIONS row present) — `tools/t_menu.py`.
- Settings chosen in the menu, then a real 1-player game from the title (`tools/t_play.py`, 700 idle frames into stage 1): KNIGHT no knockback / mercy 60; CUSTOM (knockback ON, drop OFF) 27 knockback steps / mercy 60; LEGEND and ORIGINAL 27 steps / mercy 30.
- Weapon drop from the menu: KNIGHT drops the lance 24 px behind Arthur on a torch pickup; with WEAPON DROP OFF no weapon item is left.
- ORIGINAL vs clean ROM: 600-frame idle hit/death and 2,600-frame bot run with a torch pickup — Arthur position/flags/lives/weapon/mercy/timer/score identical every frame and the pickup on the same frame; remaining differences are CPU scratch/stack and OAM bytes, the same set as v0.1. v0.2 vs v0.1 in ORIGINAL and LEGEND: byte-identical RAM over 2,600 frames (KNIGHT: one stack byte on 3 frames).
- Attract demo still starts from the new title.

### Not yet
Pause-menu access to options, SMART knockback, SQUIRE preset (needs gold armor), weapon-drop pit check, and everything after (fair spawns, air control, timer/gold armor/boss HP/ladder, checkpoints + endgame fix, single quest, stage select / map skip / ending flow / ready-screen fixes, secret markers, save build).

## v0.1 — 2026-11-15  (FairKnight-NES-v0.1.ips, patched ROM MD5 ea2bf9d9c8d0a696899941772a5441bc)

### What's new (plain language)
- **MODE on the title screen.** Under the menu there's a new line, "MODE KNIGHT". Press Left or Right to switch between KNIGHT, LEGEND and ORIGINAL before you start.
  - KNIGHT (default): no knockback, long invincibility after a hit, weapon drop.
  - LEGEND: original knockback and invincibility, weapon drop on.
  - ORIGINAL: plays exactly like the unmodified game.
- **No knockback** (KNIGHT): a hit costs your armor but Arthur hops in place instead of flying backward.
- **Longer invincibility** (KNIGHT): about twice as long after a hit.
- **Weapon drop** (KNIGHT, LEGEND): when you pick up a weapon, your old one lands about 24 pixels behind Arthur. Walk back to take it again (which drops the other one), or leave it.
- **CONTINUE is pre-selected** on the title screen after a game over.
- Continues: the original US game already has unlimited continues and already keeps your weapon through deaths and continues, so nothing needed changing there.

### For software engineers
- The patch is now built from assembly source (`src/`, ca65) by `build.py`, which verifies the clean ROM's MD5, checks a SHA-1 of every block of original code it overwrites, and checks that "free" blocks really are empty. Builds are reproducible.
- Settings live in one RAM byte with inverted bits (a set bit = original behaviour). RAM is zero at power-on, so the default preset needs no initialisation code — useful because the always-mapped part of the ROM has only ~40 free bytes.
- New features run in a mostly empty bank via a 20-byte "far call" stub: callers pass a function id in Y, the stub remembers which bank was mapped, switches, dispatches through a jump table, and switches back. The game's NMI restores the bank from a RAM shadow, so the stub always updates the shadow before touching the mapper.
- Two original routines (the hit hop and the mercy timer) were rewritten more compactly to make room for option checks; in ORIGINAL mode they behave identically (headless comparison against the clean ROM over 600 frames of a hit/death sequence and 2,600 frames of scripted play: same events on the same frames; only CPU-timing scratch bytes differ).

### Deep technical
See ROM-MAP.md §3.4-3.6. Hooks: `$E229-$E27C` (hop), `$E3B9-$E3DA` (mercy), bank 4 `$BA63` (pickup, FK id 0), `$C4A5` (title Select, FK id 1), `$C43B` (title cursor, FK id 2). FAR `$FFE8`, return `$DA6A`, handlers bank 2 `$89D1+`. RAM `$07FA-$07FF`.

### Tests (all headless, cynes, screenshots checked)
- ORIGINAL mode vs clean ROM: idle-hit-death run (600 frames) and bot run with a torch pickup (2,600 frames): identical game events.
- KNIGHT: Arthur's X unchanged by the hit; mercy counter reaches 60 (original 30).
- Each preset started from the title: KNIGHT 1 X change (death), LEGEND/ORIGINAL 27 knockback steps, mercy 30.
- Weapon drop: torch picked up -> lance item 24 px behind Arthur; walking back swaps again; HUD icon follows (screenshots).
- Title: MODE row cycles both ways, Select still moves the cursor; after a game over the cursor starts on CONTINUE and Start continues.

### Not yet
SMART knockback, pause-menu options and per-option menu, fair spawns, air control, timer/gold armor/boss HP/ladder options, extra checkpoints and endgame fix, single quest, stage select / map skip / ending flow / ready-screen fixes, secret markers, save build. The dropped weapon can land over a pit (no ground probe yet).

## proto0 — 2026-11-14
No knockback + mercy 30 -> 60 as hard byte patches (superseded).
