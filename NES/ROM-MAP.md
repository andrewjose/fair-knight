# Fair Knight — Ghosts 'n Goblins (USA) NES ROM map

Base ROM: `Ghosts'n Goblins (USA).nes`, 131,088 bytes, MD5 `80dcd911aaa221fd3de883d5128eb97c` (No-Intro, headered).
Header: NES 2.0, mapper 2 (UNROM), 8 × 16 KiB PRG, CHR-RAM, vertical mirroring.

Status tags: **confirmed** = checked at runtime (headless emulator / py65 trace); **static** = read from the disassembly, not yet runtime-checked; **likely** = strong guess, needs a check.

Session log
- 2026-11-14: first session. Tooling, core RAM map, Arthur's hit routine, knockback and mercy invincibility found; prototype 0 built and tested headless.
- 2026-11-15: v0.1. Moved to ca65 source (src/). Free-space + free-RAM survey, settings byte, far-call into bank 2, option-gated knockback and mercy, weapon drop, title MODE selector, CONTINUE default. Weapon/item code found (section 3.4). Correction: the knockback NOPs of proto0 are replaced by a rewritten hop routine; mercy compare moved (proto0 table in 3.3 is historical).
- 2026-11-15: v0.2. Title MODE row replaced by a full OPTIONS screen (section 3.7). Title Select/cursor logic moved to bank 2, freeing fixed-bank space at `$C4A5`. KEEP WEAPON dropped from the design (the original already keeps the weapon).
- 2026-11-15: v0.3. Ladder safety, air control, endgame aid, heart cursor; stage select for testing; free-RAM survey across all sections (section 3.8). Secret markers researched but not built (section 5).
- 2026-11-15: v0.4. Stage event lists decoded; hidden items are type `$11` (not `$20`). Secret markers (READY-screen list, sparkles, found bits), endgame cross moved to a fixed spot below the stage 6 boss (section 3.9).
- 2026-11-16: v0.5 finished: flyer push-out widened to 36 px, full test set re-run, v0.5 released.
- 2026-11-15: v0.5. Enemy generators, event spawner and Arthur's contact chain mapped. FAIR SPAWNS option (zombie cap, spawn telegraph, 32 px push-out for generator enemies), new code region `BANK2B` (section 3.10).

---

## 1. Plain-language summary

The game keeps everything about Arthur and the enemies in a set of parallel lists in memory, one slot per character; Arthur is always slot 0. When Arthur is hit, one routine in the always-loaded part of the ROM handles it: it takes his armor (or kills him), launches him into a short backward hop, and starts a mercy timer that makes him flash and ignore hits.

Prototype 0 changes two things in that routine:
- The backward part of the hop is removed, so Arthur hops straight up and lands where he was hit. He can no longer be knocked into a pit.
- The mercy timer counts to 60 instead of 30 (about 3.6 seconds instead of 1.8).

Both are confirmed in the emulator: same hit, same zombie, Arthur stays in place, and the flashing lasts twice as long.

### Options screen (v0.2)

The title menu has a fourth line, **OPTIONS**. Press Select until the cursor is on it, then Start. A screen lists PRESET, KNOCKBACK, MERCY TIME, WEAPON DROP and EXIT, with a one-line explanation of the highlighted line. Up/Down moves, Left/Right changes, Select resets to the preset, and Start (or A on EXIT) goes back to the title. Changing a single option shows the preset as CUSTOM. The cursor is a "!" because the game's font has no arrow.

### v0.3 additions

- **Ladder top:** when Arthur steps off the top of a ladder, the game runs a "step off" routine. Fair Knight adds a short invincibility there, using the same timer the game uses after a hit.
- **Jumps:** during a jump the game moves Arthur sideways a fixed step every tick, in the direction he took off. Fair Knight replaces that one step with its own version, which looks at the controller (ASSIST/FULL) or does exactly the original (OFF).
- **The endgame rule**, found in the code: when you finish stage 6 without the cross, the game sets the next section to stage 5. Fair Knight leaves that rule alone and makes a cross item appear in stage 6 instead.

### v0.4 additions

- **Where things appear.** Each part of a stage has a list in the ROM that says "when the screen gets here, create this thing at this spot". Hidden items are entries in those lists. A script reads all the lists and writes out a table of all 29 hidden items, which is built straight into the hack.
- **Secret markers.** The READY screen before each life lists each stage's hidden items: a grey heart for found, a dot for not found. With SPARKLES, each hidden spot also blinks in the level. A bigger star means duck there, and a red star means the item is harmful.
- **Endgame cross.** The cross now waits on the floor just below the stage 6 boss.

### v0.5 additions

- **Where enemies come from.** Two sources. The stage lists from v0.4 place most enemies at fixed spots. On top of that, seven small "generator" routines keep producing enemies in certain areas, like the endless zombies in stage 1. They run every game tick, one after another.
- **How a hit is decided.** Once per tick the game checks whether anything is touching Arthur and sets a "hit" flag. Arthur's own routine then reads that flag and takes his armor.
- **Fair spawns** hooks three places. It skips a zombie wave while 3 or more zombies are out. It gives every newly created enemy a ~20-frame grace period during which touching it doesn't count. And it pushes generator enemies that appear right next to Arthur out to 36 pixels, so they are still at least 32 pixels away after their first step.

## 2. For software engineers (no game-dev background)

**Memory.** The NES has 2 KB of RAM (`$0000-$07FF`). This game stores objects as *structure of arrays*: each property (X, Y, flags, timers) is its own 22-byte array, and an object is an index into all of them. Arthur is index 0, so `$05AF` is "X of object 0", `$05B0` is X of object 1, and so on.

**Code layout.** The cartridge has eight 16 KB banks. The last one (bank 7) is always mapped at `$C000-$FFFF`; any one of the other seven can be swapped into `$8000-$BFFF` by writing to the ROM area. Arthur's core logic (hit handling, movement helpers, status-flag helpers) lives in bank 7, which makes it easy to patch: hooks there are always reachable.

**Threads.** The game runs a small cooperative scheduler. Each object runs as a coroutine with its own stack and yields once per tick (`JSR $DB90` → yield). That's why the hit routine reads like a straight-line script ("hop up 6 steps, then fall until landing") rather than a per-frame state machine. The game logic runs once every 2 video frames (`$CD = 2`), and each object's coroutine runs roughly every 3 frames.

**Status flags.** Arthur's state is a bit field at `$04F0`. Helper functions set, clear and test single bits (`$F2EB-$F34x`), like tiny getters and setters.

**How things were found.** Run the ROM headlessly, record all 2 KB of RAM every frame under scripted input (idle / hold Right / hold Left / jump), and look for bytes that change the way a known quantity should. Then rerun the same frames on a second, Python-based 6502 emulator that logs every memory write with the instruction address that made it. That points straight at the code responsible.

**Options screen design (v0.2).** The always-mapped bank has almost no spare bytes, so the options screen is a ~20-byte loop in the fixed bank (*yield one tick, call the options handler in bank 2, repeat until it returns "leave"*). All logic and text live in bank 2. The handler never yields itself, because switching tasks while bank 2 is mapped would hand other tasks the wrong bank. Leaving the screen re-runs the title's own init routine (`$C3DC`), the same path the attract demo uses to return, so no title drawing code had to be written. Screen text goes through the game's PPU write queue (`$EECF`, buffer `$0720`); the queue ends just below the settings RAM, so the handler queues at most ~150 bytes per tick: the cursor column, the description line, and one more screen piece in rotation.

**Adding an option later.** Give it a bit in `FK_SET` (set = original), then append one entry to each `opt_*` table in `bank2.s` (mask, two value strings, two description strings) and a label to `lbl_*`. Row count, cursor range and drawing all follow `NOPT`.

**Stage event lists (v0.4).** Think of each stage section as having a script: a list of records sorted by scroll position. As the screen scrolls, a spawner reads the next record and, when its trigger position is reached, creates the object it describes. Enemies, items and hidden items all come from these lists. A hidden item is just an object type (`$11`) whose "idle" behaviour is "be invisible, and wait for Arthur to touch me (optionally while ducking)". Fair Knight never changes the lists. It reads them offline to build a lookup table, and hooks two moments in the hidden item's life: while waiting (draw a sparkle) and when revealed (record it as found).

## 3. Deep technical reference

### 3.1 RAM

| Address | Meaning | Status |
|---|---|---|
| `$00`, `$02+` | Scheduler task table / index | static |
| `$38` | PPUCTRL shadow | static |
| `$3D`, `$64` | Camera / scroll X (low) | confirmed (grows when the screen scrolls right) |
| `$4E` | Frame counter used by the scheduler wait (`$C39C`) | static |
| `$C8` | Current PRG bank shadow (mapper 2) | confirmed |
| `$CD` | Frames per logic tick (2) | static |
| `$BD` | If non-zero, any hit goes straight to the death path (`$E171`) | static; meaning unknown |
| `$D5-$D9` | Set on armor loss (`$D5=1`, `$D6-$D9=$FF`), likely the flying-armor-pieces effect | static |
| `$04F0,x` | Object status flags (Arthur = `$04F0`), see below | confirmed |
| `$0509,x` | Y (alternate / collision copy) | likely |
| `$0522,x`, `$053B,x` | Animation frame / anim mode | static |
| `$0554,x` | X relative position used in contact checks | static |
| `$056D,x`, `$0583,x` | Y high / X high (page) | static |
| `$0599,x` | Y position (Arthur `$0599`; 184 = standing on the stage 1 ground) | confirmed |
| `$05AF,x` | X position on screen (Arthur `$05AF`; scroll starts near 128, left clamp 69 at stage start) | confirmed |
| `$05DB,x` | X subpixel | static |
| `$05F1,x` | Motion/direction flags; on a hit set to `((~facing)&4)<<1 \| 4` (knockback direction) | confirmed |
| `$0607,x` | Jump/hop arc step counter (6 = start of the hit hop) | confirmed |
| `$061D,x`, `$0631,x` | Object type / sub-type flags | static |
| `$0647,x` | Mercy-invincibility counter: reset to 0 on hit, +1 per Arthur tick, invincibility ends at `#$1E` | confirmed |
| `$06FC` | Timer, ones digit of seconds (decrements every 60 frames) | confirmed; tens/minutes probably next to it |
| `$0715` | Lives, probably (3 → 2 at a death) | likely |
| `$07A6+`, `$07D8+` | PPU write queues flushed in NMI | static |

**`$04F0` (Arthur status bits).** Set with `$F305/$F309/$F30D/$F311/$F315/$F319/$F31D/$F321` (bits 0-7), cleared with `$F32A/$F32E/$F332/$F336/$F33A/$F33E/$F342/$F346`, tested with `$F2EB` (4), `$F2EF` (8), `$F2F3` (16), `$F2F7` (32), `$F2FB` (64), `$F2FF` (128).

| Bit | Meaning | Status |
|---|---|---|
| `$04` | Facing | static |
| `$08` | In hit / knockback | static |
| `$10` | Standing on a moving platform | static |
| `$20` | **No armor** (boxers). Set at the end of the first hit; a hit while it's set → death | confirmed |
| `$40` | Mercy invincibility active | static (cleared by `$E3B9` when the `$0647` counter hits the limit) |
| `$80` | Flicker phase (from `$0647` bit 1) | static |

### 3.2 Code

All addresses are bank 7 (fixed, `$C000-$FFFF`, file offset = `0x1C010 + (addr - $C000)`) unless noted.

| Address | What | Status |
|---|---|---|
| `$C008` | RESET | static |
| `$C0F0` | NMI: OAM DMA, PPU queue flush, frame counter | static |
| `$C37D-$C3BB` | Cooperative scheduler; waits at `$C39C` until `$4E >= $CD` | static |
| `$DB82` | Move object horizontally with speed `#$0C` in the `$05F1` direction (`JSR $F03E` + `$DBFB`) | confirmed |
| `$DB90` | Yield to the scheduler (`JSR $F181`, `JMP $E4E5`) | static |
| `$DF04 / $DF33 / $DF3C` | Hop/jump vertical step (up / peak / down) | static |
| `$DF62` | Wall check in the movement direction (carry set = blocked) | static |
| `$E171` | **Arthur hit handler.** `$BD≠0` → death. Bit `$20` set → death path (`$E1AC`). Otherwise armor loss: sets bits `$40`, clears `$01/$02`, sound `$1D`, armor effect `$D5-$D9`, then the hop (`$E1EE`), then sets bit `$20` | confirmed |
| `$E1EE-$E285` | Hit hop: `$0607 = 6`; rise loop `$E229` (wall check → `JSR $DB82` at **`$E22E`**), peak loop `$E24D` (**`$E252`**), fall loop `$E275` (`JSR $E286` at **`$E27A`**, which moves by `#$06`) | confirmed |
| `$E3B9-$E3DB` | Mercy timer: if bit `$40`, `INC $0647,x`; at **`CMP #$1E` (`$E3C4`)** clear bit `$40`; else set flicker bit `$80` from the counter | confirmed |
| `$F03E` | Add velocity (`$74/$78/$7C`, from a speed table at `$EFDA`) to X | static |
| `$F181` | Common per-tick update (called before yield) | static |

### 3.3 Prototype 0 (`FairKnight-proto0.ips`)

| File offset | CPU | Original | New | Effect |
|---|---|---|---|---|
| `0x1E23E` | `$E22E` | `20 82 DB` | `EA EA EA` | no backward motion while rising |
| `0x1E262` | `$E252` | `20 82 DB` | `EA EA EA` | none at the peak |
| `0x1E28A` | `$E27A` | `20 86 E2` | `EA EA EA` | none while falling |
| `0x1E3D5` | `$E3C5` | `1E` | `3C` | mercy timer 30 → 60 ticks |

Patched ROM MD5: `b02f17467bea2b473717cd3f25a8583f`.

Test (headless, stage 1, idle from the first frame of play): original, Arthur is hit at frame 90, hops back ~33 px, dies at 381. Prototype, same hit, X unchanged until death; the `$0647` counter runs to 60 (ends ~frame 306 vs ~210).

In the final hack these become toggle-gated hooks (`KNOCKBACK`, `MERCY TIME`) rather than hard NOPs, and the SMART knockback mode replaces the NOPs with a ground probe before `JSR $DB82`.

### 3.4 Weapons and items (2026-11-15, confirmed at runtime)

| Address | What |
|---|---|
| `$053A` | Current weapon = sprite id of the HUD weapon icon (object slot 24): `$40` lance, `$42` dagger, `$44` torch, `$36` axe, `$4F` cross. Copy per player in `$C5,y` (`y = $BA`, current player). Kept through death and continue in the original. |
| `$0553` | HUD weapon icon anim mode |
| `$061D,x` (items) | Item kind: 0-3 treasure, 4 1UP, 5 armor, 6 torch, 7 axe, 8 dagger, 9 cross, 10 lance, 11 ?, 12 time down, 13 time up. Sprite from the table at bank 4 `$BB2D` (kind -> sprite id). |
| bank 4 `$BA09` | Item object loop: off-screen check (`$F0A3`), sprite from kind, touch test `$F68E` (no pickup while Arthur has bit `$01` or `$40`), then dispatch on kind at `$BA44`. Weapons fall through to `$BA63`. |
| bank 4 `$BA63` | Weapon pickup: `$C5,y` and `$053A` <- item sprite, `$0553` <- item anim mode, `JMP $BB27` (destroy item; `$BB2A` = keep looping). |
| `$E041-$E13D` | Throw: picks a free projectile slot (`$11-$13`), projectile type from `$053A` (`$23`-`$27`). |
| `$94` | Demo/attract flag (`$FF` in demo; weapon forced to lance). |
| `$A3` | Title cursor (0 1 PLAYER, 1 2 PLAYERS, 2 CONTINUE); cursor sprite Y in `$0509` (`$92/$A2/$B2`). `$BB` != 0 = a game can be continued. `$42` = buttons held (A `$80`, B `$40`, Select `$20`, Start `$10`, Up `$08`, Down `$04`, Left `$02`, Right `$01`). |
| `$EECF` | Queue a nametable write: `$25:$24` PPU address, `$23` length, `$22` rows, `($26)` source. Text: digits `$00-$09`, `A-Z` = `$0A-$23`, space `$FF`. |
| `$C3D2`… | Task entry table (RTS-style address-1 pointers). |
| `$C47B` area | Title loop also checks the hidden level-select button sequence (`$A7`, table `$C61C`). |

### 3.5 Free space (survey 2026-11-15)

- **Fixed bank 7** is almost full. Truly free: `$FFE8-$FFF9` (18, end padding), `$DA6A-$DA70` (7, padding before task entry `$DA71`), `$E562-$E568` (7, padding before task entry `$E569`). **Not free** despite looking empty: `$CA76-$CA95` (32 x `$FF` = source buffer for clearing a nametable row, read by `$CA63`), `$C84C-$C86B`/`$C8AB-$C8BD` (title text), `$F1A3+` (table), `$EB67+` (table). The v0.1 hop rewrite freed `$E27D-$E285` (9).
- **Switchable banks**: bank 2 `$89D1-$971D` (3405), bank 1 `$8B0F-$97FF` (3313), bank 0 `$B560-$BFFF` (2720), plus smaller runs. Banks 4 and 6 have none.
- **RAM**: `$07FA-$07FF` never written in ~45,000 frames of scripted play (title, stage 1, deaths, game over, continue) and not touched by the game-start path; cleared only by the power-on reset (the warm-reset path keeps RAM via the `$8B/$8C` = `$14/$22` signature). Other never-written areas are object-array tails, task-stack bottoms (`$0120+`, `$0140+`…) and player-2 data, so they were not used.

### 3.6 Fair Knight code layout (v0.2)

| Where | What |
|---|---|
| `$07FA` FK_SET | Settings bits; **set = original behaviour**, so RAM 0 at power-on = KNIGHT. bit7 knockback, bit6 mercy, bit5 weapon drop. |
| `$07FB` FK_PRESET | bits 0-1: base preset 0 KNIGHT, 1 LEGEND, 2 ORIGINAL; bit 2: CUSTOM (changed by hand; Select restores the base) |
| `$07FC/$07FD` | buttons last tick / newly pressed (edge detection, title + options) |
| `$07FE` FK_CUR / `$07FF` FK_JOB | options screen cursor row / draw job (bit 7 = screen drawn, input enabled). Reset every title tick. |
| `$FFE8` FAR | `LDY #id / JSR $FFE8`: saves `$C7`, maps bank 2 (writes `$C7` first, then the bus-conflict table), jumps to the dispatcher at `$89D1`. Return path `$DA6A` restores the bank. A is clobbered, X kept, carry is the return value. |
| `$E229-$E27C` | Hit hop rewritten (rise loop + combined peak/fall loop, shared knockback step that tests bit 7) |
| `$E3B9-$E3DA` | Mercy tick rewritten; counter halved before the `#$1E` compare when bit 6 = 0 |
| bank 4 `$BA63` | Weapon pickup -> FK id 0 |
| `$C4A5-$C4C5` | Title tick -> FK id 1 (Select cursor over 4 rows, OPTIONS text, options-state reset), then `JMP $C4CE`; **optgate** (`$C4AD`): row 3 -> clear screen (`$C62C`), loop {yield `$C336`; FK id 3} until carry, then `JMP $C3DC` (title init); other rows -> `JMP $C53B` |
| `$C458` | Start handler tail `JMP $C53B` -> `JMP optgate` |
| `$C43B` | Title cursor init -> FK id 2 (CONTINUE default) |
| bank 2 `$89D1+` | FK dispatcher and handlers (source `src/bank2.s`) |

### 3.7 Title and options screen (v0.2)

| Item | Detail | Status |
|---|---|---|
| Title rows | Text at `$224D` (1 PLAYER), `$228D` (2 PLAYERS), `$22CD` (CONTINUE, drawn only if `$BB` != 0), **`$230D` OPTIONS** (new). Cursor sprite Y `$92/$A2/$B2/$C2` in `$0509`, row index `$A3`; original wrap compare `#$C2` -> `#$D2`. | confirmed |
| Start | `$C44B`: `JSR $EF20` (Start held), wait for release, then `$C458` -> optgate. | confirmed |
| `$C62C` | Clear screen: rendering off + yield (`$F171`), scroll reset, nametables (`$CA27/$CA2E`), OAM buffer (`$CA96`), rendering on. Object sprites (e.g. the title cursor) are not drawn on the cleared screen. | confirmed |
| `$C3DC` | Title init (re-entry used by the attract demo); ends by waiting for Start release, so leaving options with Start doesn't start a game. | confirmed |
| Layout | Header row 4 (`$2086`); rows at nametable rows 8, 10, 12, 14, 16 (label column 4 via `rowa_*`, value column 18); cursor column 2 drawn as a 9-tall vertical write from a sliding window (`curcol`); description row 23 (`$22E2`); help rows 26-27. | confirmed |
| Font | Digits `$00-$09`, A-Z `$0A-$23`, `$24` (c), `$25` !, `$26` ., `$27` heart (grey), space `$FF`; nothing arrow-like. Cursor glyph = `$25`. | confirmed (glyph survey) |
| PPU queue | `$EECF` appends `addr,len,data` per row to `$0720+$31`, `$FF` terminated; ends below `$07FA`. Per tick the options handler queues <= ~150 bytes. | static |

### 3.8 v0.3 (2026-11-15)

**Stage select (testing).** Action Replay `$00A7:0F` at the title (poke before pressing Start) shows a "STAGE n X" screen. A/B step the section `$AC`, Start begins. `tools/stagesel.py goto(rom, section, settle, fk)`.

| `$AC` | `$CF` | Section |
|---|---|---|
| 0, 1, 2 | 0 | Stage 1 A, B, C |
| 3-6 | 1 | Stage 2 |
| 7, 8 | 2 | Stage 3 (cave) |
| 9, 10 | 3 | Stage 4 |
| 11 | 4 | Stage 5 (ladder rooms) |
| 12 | 5 | Stage 6 |
| 13 | 6 | Final room (Astaroth) |

The value wraps after 13. `$CF` = stage index (confirmed). `$C2` = section progression counter; `$AA,x` = round (loop) counter, incremented when `$C2` passes 13 (static).

**Other RAM (from public Action Replay codes, partly confirmed).** `$06F6/$06F8/$06FA/$06FC` timer digits (`$06FC` and `$06FA` confirmed), `$0715/$0716` lives P1/P2, `$00AA` difficulty 0-4, `$00EB` no-enemies flag, `$00BF` complete-level flag, `$00A6` skip intro, `$00CD` logic speed.

**Endgame rule** (bank 7, stage-clear path `$D436`, confirmed): after the screen clears, if `$CF = 5` (stage 6) and the player's weapon `$C5,y` ≠ `$4F` (cross): `JSR $84DB` (bank 1, the message), then `$C2 = $0A`. The following `INC $C2` makes section 11 (stage 5). Otherwise play continues to section 13. `$D461`: section counter, round wrap at 14, game end on round 2.

**Ladders** (confirmed). The climb loop is at `$DC73`; `$DC3E` reads the ladder tile at Arthur's feet (`$BA-$CF` = ladder). At the top, `$DD65` waits at `$DD83` (pose `$1F`) for Up or Down: Down → climb down (`$DCD7`); Up → `$DD90`: `JSR $E166` (snap Y), `JSR $DC5B` (anim), `JMP $DB65` (standing state). Arthur takes no hits while waiting at `$DD83` (the loop doesn't call `$E014`).

**Jumps** (confirmed). Takeoff at `$DE0x`: pad `$CC & 3` → `$05F1 = $E307[pad] & $0C` (`$04` right, `$0C` left). A standing jump clears `$065D`. Per tick: rise loop `$DE2D` / peak loop `$DE5E` / fall loop `$DEA1`, each doing `JSR $DF5D` (`$065D` set? then wall check `$DF62` on the `$05F1` side) and then `JSR $DB82` (speed `$0C`) or `$E286` (speed `$06`). `$CC` = Arthur's pad copy (R `$01`, L `$02`, Down `$04`, Up `$08`, B `$40`, A `$80`).

**Object types.** `$0631,x` selects the per-tick handler through the table at bank 4 `$9CED` (2 bytes per type; loop `$9CC8` over slots 1-21). Type `$10` = item (`$BA09`); `$061D` = kind (9 = cross); pot items become type `$10` at `$BC94`. A free slot comes from `$DA18` (slots 1-16; carry set = none). Writing type/kind/sprite/position and then `$04F0,y = $40` spawns a working item (confirmed: the spawned cross is drawn and picked up normally).

**Fair Knight sites added in v0.3**

| Site | Bytes | Was | Now |
|---|---|---|---|
| `$DD90` | 9 | `JSR $E166 / JSR $DC5B / JMP $DB65` | `LDY #4 / JSR FAR / JMP $DB65 / NOP` (handler does the two calls + ladder safety) |
| `$DE40`, `$DE86` | 8 each | `JSR $DF5D / BCS +3 / JSR $DB82` | `LDY #5 / JSR FAR / NOP×3` (air, speed `$0C`) |
| `$DEC9` | 8 | `JSR $DF5D / BCS +3 / JSR $E286` | `LDY #6 / JSR FAR / NOP×3` (air, speed `$06`) |
| `$D3AD` | 3 | `LDA $06FC` (once per second, after the timer digits change) | `JSR $E562` |
| `$E562` | 7 (was padding) | — | `JSR $FFF5 / LDA $06FC / RTS` |
| `$FFF5` | 5 (was padding) | — | `LDY #7 / JMP FAR` (FK id 7 = endgame aid) |

**Settings.** `$07FA` bit 4 = ladder safety off. Bits 3-2 = air (`00` ASSIST, `01` FULL, `11` OFF). Bits 1-0 are reserved for SECRETS (`00` MAP, `01` MAP+SPARKLES, `11` OFF). `$07FB` bit 7 = endgame aid off. Presets: KNIGHT `$00/$00`, LEGEND `$DF/$81`, ORIGINAL `$FF/$82`.

**RAM `$04C0-$04C3`** (FK_SPD, FK_WANT, FK_AIRH, FK_EGCD). `tools/ramsurvey2.py` played random input in every stage-select section: `$04C0-$04D1` was never written and never non-zero. The only code references nearby are `$04D0,x`/`$04D1,x` (scheduler register saves, x = task offset) and two probable data bytes misread as code.

**Air handler** (bank 2 `air12`/`air6`). OFF does `JSR $DF5D; BCS; LDA spd; JSR $F03E; JMP $DBFB`, the same as `$DB82`/`$E286`. ASSIST: if `$065D` ≠ 0 and the opposite direction is held, `$065D = 0` (no sideways motion for the rest of the jump). FULL: direction held → want = `$04`/`$0C`. If not moving: start with a half-speed step (`FK_AIRH`). If moving the other way: stop this tick. Then wall check `$DF62` on the new side, then `$F03E` with speed (or speed/2) and `$DBFB`.

**Ladder handler.** `JSR $E166; JSR $DC5B`; if enabled, set `$04F0,x` bit `$40` and `$0647,x` = 18 (NORMAL mercy) or 36 (LONG). That's 12 mercy ticks; Arthur's mercy tick (`$E3B9`) then counts it down and flickers him. A longer running mercy isn't shortened.

**Endgame handler** (per second). Conditions: option on, `$CF = 5`, `$BD = 0`, not the attract demo (`$94`), `$053A` ≠ `$4F`, cooldown `$04C3` = 0, no cross item (type `$10`, kind 9) in slots 1-16, and Arthur's Y on a floor line (`Y & $0F = 8`). Then it spawns a cross 40 px ahead of Arthur (or behind him near the screen edge) at his Y, with a cooldown of 8 seconds.

**Fair spawns (v0.5).** Rather than edit seven enemy routines, Fair Knight watches the object table from the outside. After all spawners have run each tick, one pass over the 16 enemy slots notices any slot that is newly occupied and stamps it with an age (a 4-bit counter, eight bytes for all 16 slots). Arthur's hit check is wrapped: if the only thing touching him is still young, the hit is cancelled. It's like a middleware layer that filters events without touching the producers. The zombie cap is a guard clause in front of the zombie generator's call.

### 3.9 v0.4 (2026-11-15)

**Stage event lists** (confirmed). The pointer table is at `$8038 + 2*section` in the stage-data bank (`$C8`). Sections 0-6 use bank 1, 7-10 bank 2, and 11-13 bank 3. Each record is 8 bytes:

| Byte | Meaning |
|---|---|
| 0 | trigger (screen page / Y-high the camera must reach). `$80` ends the list |
| 1 | param, copied to `$061D` (item kind for types `$10`/`$11`) |
| 2 | object type, copied to `$0631` |
| 3, 4 | X low, X page |
| 5, 6 | Y low, Y high |
| 7 | initial `$04F0` flags (bit 0 on a type `$11` = duck required) |

Spawner: bank 7 `$D57C`/`$D596`; `$C1` = next event index, `$C2` = section; per-type init table at `$D5FB`.

**Hidden items: type `$11`** (handler bank 4 `$BB8C`, confirmed).
- While waiting it uses sprite `$49`, and `$F346` clears the draw bit.
- Touch test is `$F68E`. It ignores Arthur while his `$04F0` has bit `$40` (mercy) or bit `$01`.
- If the item's flags bit 0 is set, Arthur must be ducking (`$04F0` bit `$02`).
- Armor while already armored → `JMP $F708` (no reveal).
- On reveal (`$BBCA`) it becomes type `$12`, and the item appears 100 px up and falls.
- Kinds: 2 Yashichi, 3 King doll, 4 1UP, 5 armor, 6 torch, 7 axe, 9 cross, 10 lance, 11 doll variant, 12 time down (harmful, −30 s), 13 time up.

**Type `$20`** (handler `$BF0B`) is not a hidden item. It counts ticks of Arthur's *projectiles* (slots `$11-$13`) overlapping it up to 15, then reveals a white magician-like bonus (~2000 points) and becomes type `$35`. Not counted in the secret table.

**Trigger table** (`tools/secrets.csv`, generated by `tools/secrets_extract.py`; X/Y are world pixels):

| Stage | Section | X | Y | Item | Condition |
|---|---|---|---|---|---|
| 1 | 1A | 752 | 48 | King doll | touch |
| 1 | 1A | 1808 | 148 | armor | touch |
| 1 | 1B | 2000 | 176 | time down (harmful) | duck |
| 1 | 1B | 2592 | 154 | Yashichi | touch |
| 2 | 2A | 80 | 256 | 1UP | touch |
| 2 | 2A | 496 | 154 | Yashichi | touch |
| 2 | 2B | 1584 | 144 | armor | touch |
| 2 | 2B | 2008 | 208 | torch | touch |
| 2 | 2C | 2640 | 320 | time up | touch |
| 3 | 3A | 840 | 840 | lance | touch |
| 3 | 3B | 2248 | 368 | King doll | touch |
| 3 | 3B | 2320 | 216 | armor | touch |
| 3 | 3B | 2632 | 90 | Yashichi | touch |
| 3 | 3B | 2824 | 584 | armor | duck |
| 3 | 3B | 2936 | 952 | doll variant | touch |
| 3 | 3B | 3000 | 952 | torch | touch |
| 4 | 4A | 544 | 56 | 1UP | touch |
| 4 | 4B | 1264 | 176 | cross | duck |
| 4 | 4B | 2160 | 160 | doll variant | touch |
| 4 | 4B | 2464 | 152 | King doll | touch |
| 5 | 5 | 512 | 1088 | 1UP | touch |
| 5 | 5 | 224 | 1192 | axe | touch |
| 5 | 5 | 632 | 912 | Yashichi | touch |
| 5 | 5 | 448 | 776 | armor | touch |
| 6 | 6 | 224 | 1456 | lance | touch |
| 6 | 6 | 160 | 1120 | cross | touch |
| 6 | 6 | 104 | 848 | armor | touch |
| 6 | 6 | 224 | 784 | torch | touch |
| 6 | 6 | 240 | 608 | axe | touch |

"Touch" spots are usually reached with a jump. Only 4B X 1264 (duck) and 4B X 2160 (jump) were played for real in testing. The rest come from the extractor.

**Fair Knight sites added in v0.4**

| Site | Bytes | Now |
|---|---|---|
| bank 4 `$BB8C` | 8 | `LDY #9 / JSR FAR / NOP×3` (spark: draws a sparkle, or does the original `LDA #$49 / STA $0522,x / JMP $F346`) |
| bank 4 `$BBB9` | 17 | `LDY #10 / JSR FAR / BCC reveal / JMP $F708 / NOP×7` (found: record bit; carry = armor-while-armored as before) |
| bank 7 `$C9E2` | 14 | `LDY #8 / JSR FAR / JSR $C313 / NOP×6` (READY: list, then `JSR $F17A`, `$22/$23 = $5A/$00`) |

**RAM.** `$04C4-$04C7` = found bits (index = row in `secrets.csv`). `$04C8` = signature `$A5`; if it's missing, the bits are cleared (once per power-on). Demo play (`$94`) doesn't record.

**Sparkle drawing.** `$0607,x` counts up; visible while bit 3 is set (8 ticks on / 8 off). Sprite `$56` (small hit-spark) or `$66` (four-point star) for duck spots. Both are in common sprite CHR in every stage tested. `$053B,x` = 1 (sprite palette 1, red) for kind 12, else 0. `$04F0,x` bit `$80` = draw. There's no down-arrow tile in common CHR.

**READY screen** (`$C971`). Lives are queued at `$21EF`, then the original `JSR $F17A`, timer `$22/$23`, `JSR $C313`. FK queues "HIDDEN ITEMS" at `$224A`, and rows at `$2283` (stages 1-3) and `$22C3` (stages 4-6). Each row is: digit, space, one symbol per secret (`$27` heart = found, `$26` dot = not), two spaces. Font: digits `$00-$09`, A-Z `$0A-$23`, space `$FF`. Rows are written directly into the PPU queue (`$0720+$31`, format addr-hi, addr-lo, len, data, `$FF` end) while `$4F` (NMI flush guard) is held.

**Endgame aid v0.4** (supersedes the v0.3 handler above). Runs once per second.
- Conditions:
  - option on, `$CF = 5`, `$BD = 0`, not demo
  - `$053A` ≠ `$4F` (not holding the cross)
  - Arthur `$056D = 1` and `$0599` in `$70-$BF` (floors y 376 and 440)
  - Arthur within ~110 px of X 214
  - no cross item (type `$10`, kind 9) with Y-high 1 in slots 1-16
- Then `FREESLOT`, and spawn type `$10`, kind 9, sprite `$4F`, X 214, Y `$1BA`, flags `$40`.
- The cooldown `$04C3` is no longer used.
- Nothing remembers that the cross was spawned, so after a death or continue it reappears when Arthur gets back up there.

**Stage 6 layout** (world Y of each floor, bottom to top): 1464, 1304, 1208, 1128, 1048, 952, 872, 792, 696, 616, 536, 440, 376. Ladder X per floor: 280, 178, 328, 112, 86, 118, 152, 357, 166, 356, 228, 196. The boss is on the top floor (y 376) at the right (X ≈ 400-430).

### 3.10 v0.5 fair spawns (2026-11-15)

**Spawn sources** (confirmed).
- **Event spawner:** bank 7 `$D57C` → `$D596`, reading the stage event lists from §3.9. It is called each logic tick, and then `$D57C` calls the generator dispatcher.
- **Generator dispatcher:** bank 2 `$8400` = `JSR $8416, $84E0, $8574, $8610, $867A, $880A, $8748 / RTS`.
  - Gates read from the code:

| Generator | Runs when (static) | Timer |
|---|---|---|
| `$8416` | section `$C2` = 0 or 7 (1A, 3A), Arthur X page < 5 | `$EA`, reload `$60 − $5B`. Zombie waves (type `$00`) |
| `$84E0` | stage `$CF` = 0, Arthur page 7-8 | |
| `$8574` | `$E2` < 3, section 4 | |
| `$8610` | section < 3, scroll page `$65` 9-11 | `$EA`, reload `$28 − $5B` |
| `$867A` | stage `$CF` = 4 (Arthur Y-high < 2) or 5 (`$DF`) | |
| `$8748` | stage `$CF` = 1, Arthur page 4 or 6-9 | `$0718`, reload `$70` |
| `$880A` | stage `$CF` = 4 (`$DF`, Y-high) | |

  - Types seen coming from generators in play: `$00` (zombie), `$03`, `$04` (edge flyer), `$06`, `$07`, `$14`.
  - `$CF` is the 0-based stage and `$C2` the section, as in §3.9.
- **Rising zombies** (type `$00`) already spawn at least 48 px from Arthur in the original (`t_fs_dist.py`, min |dx| 48 in sections 0 and 2). They are also harmless while they rise (64-79 frames). So the original "zombie on Arthur" problem is mostly about how many there are, not where they appear.
- **Edge flyers** (type `$04`, sections 11 and 12) can enter at |dx| 26 from Arthur.
- **Red Arremer** hovers for about 12 frames before each dive. That already works as a warning, so its AI and timing are untouched.

**Contact chain** (confirmed). `$F5A0` → `$F5E3` → `$F687` → `$F68E` sets Arthur's `$04F0` bit 0 (touched). Arthur's hit check `$E014` (called from 8 sites) tests that bit and goes on to the hit routine.

**Fair Knight v0.5 sites**

| Site | Bytes | Original SHA-1 | Now |
|---|---|---|---|
| bank 2 `$8400` | 3 | `9bf34b49` | `JSR fk_zgen` (zombie cap, then `JMP $8416`) |
| bank 2 `$8412` | 3 | `07c89a1f` | `JMP fk_gen` (`JSR $8748`, then the age pass) |
| bank 7 `$E014` | 9 | `e632d2b4` | `LDY #11 / JMP FAR / NOP×4` (FK id 11 `fshit`, carry = hit) |

New code region `BANK2B`: bank 2 `$BB67-$BE66` (`$300`, `$208` used). The build asserts it is all `$FF`. A py65 replay of 1,680 frames across all 14 sections on the clean ROM never read bank 2 `$BB67-$BFFF` (`t_cover_b2.py`).

**RAM**
- `$04C9-$04D0`: age nibbles for slots 1-16, two slots per byte (slot & 15). The low nibble is the even slot.
  - 0: unseen.
  - 2-14: telegraph ticks left.
  - 15: settled.
- `$04D1`: hit-check scratch.
  - Bit 0: a telegraphing object is near Arthur.
  - Bit 1: a settled object is near him.
- `$07FB` bit 6 (`FKP_FAIRSP`): 1 = original spawns.
  - Presets: KNIGHT 0, LEGEND 0, ORIGINAL 1.

**Logic** (`src/fairspawn.s`)
- **Zombie cap.** Count active type `$00` objects in slots 1-16. If there are ≥ `FS_ZCAP` (3), return without calling `$8416`, so its wave timer `$EA` waits. A wave then adds up to 3 more.
- **Age pass** (after `$8748`, slots 16..1):
  - Empty slot → 0.
  - New (nibble 0, active) → `nudge`. Then `FS_TEL` (8) if the type is in the telegraph list, else 15.
  - Otherwise decrement, and jump 1 → 15.
  - The pass runs once per spawn tick, about every 3 frames, so 7 ticks ≈ 21 frames.
  - Telegraph list: `$00 $01 $02 $03 $04 $06 $07 $08 $0A $0B $0D $0E $0F $14 $21 $32`. Bosses, platforms, items (`$10-$12`) and the `$20` magician spot are not in it.
- **Nudge.** For types `$00 $03 $04 $06 $07 $14` with |dy| < 48 and |dx| < 32 from Arthur, set X to Arthur ± `FS_PUSH` (36) on the side the object was on (right side near the stage's left edge). 36 rather than 32 because edge flyers move ~3 px toward Arthur in the same frame; with 32 they ended the frame at 29 px (changed 2026-11-16).
- **`fshit`** (replaces `$E014`):
  - Arthur bit 0 clear → no hit.
  - Option off → hit, as the original.
  - Otherwise scan slots 1-16, skipping types `$10-$12` and `$20`, within |dx| < 24 and |dy| < 40.
  - If only telegraphing objects are near, clear bit 0 and return no hit. Otherwise return a hit.
  - X is preserved.

**Measured** (v0.5 ROM MD5 `01ff3aab2481623bd5fa37a5b418d6fc`; telegraph, cap, menu, equivalence and v0.4 regressions re-run on this build 2026-11-16)
- Zombies out at once, stage 1A, 2,500 random-walk frames:
  - Original: max 7.
  - KNIGHT: max 4.
- Zombies through the real menu (`t_play5.py`):
  - KNIGHT: max 4, average 2.7.
  - FAIR SPAWNS OFF or ORIGINAL: max 7, average 4.7.
- **Telegraph** (`t_fs_tel2.py`, a zombie placed on Arthur with its age reset):
  - First hit after 22 frames with fair spawns, vs 7 frames in clean and ORIGINAL.
  - A zombie walking past within its window doesn't hit.
  - One placed on him that stays hits once the window ends.
- **Edge flyers:** type `$04` entering at dx 26 is pushed to 36 at the spawn tick and is 32-38 px away at the end of its first frame.
- **Spawn distance per section** (`t_fs_dist.py`, 2,500 random-walk frames per section, Arthur kept alive by a mercy poke; distance = |dx| on the spawn frame, generator types only):

| Section | Original min |dx| | KNIGHT min |dx| | Max zombies original / KNIGHT |
|---|---|---|---|
| 0 (1A graveyard) | 48 | 48 | 7 / 4 |
| 2 | 48 | 48 | 1 / 1 |
| 11 (edge flyers) | 26 | 33 | 2 / 2 |
| 12 (edge flyers) | 26 | 32 | 0 / 0 |
| 1, 4, 5 | only the READY-screen objects at dx 0 (see below) | same | 2 / 2 |

- **CPU:** ORIGINAL adds ~0 cycles per frame. Fair spawns on adds ~520 cycles per frame (~1.7 % of a frame) with the same objects on screen. In the stage 1 graveyard run (`t_fs_lag.py`), KNIGHT is actually lighter than the clean ROM because fewer zombies are out: idle time 62.6 % vs 51.8 % of each frame, and frames with < 500 idle cycles 13/119 vs 40/119. No new lag.
- **Equivalence** (`t_orig.py`, `t_orig5.py`):
  - ORIGINAL vs clean: 0 differences over the 600 idle frames.
  - KNIGHT with FAIR SPAWNS OFF vs v0.4 KNIGHT: also 0 over the 600 idle frames.
  - Bot runs of 2,600 frames: 1 difference each, at frame 191 (`$04F0`/`$04F3` swapped, `$0554`). Full RAM is identical at frames 189, 190, 192 and 193 (`t_f191.py`).
    - Cause: the far call at `$E014` adds a few cycles, so the frame cut lands at a different point inside the game's slot-shuffling code. It's a sampling artefact, not a gameplay change.
- `t_fs_dist.py` also lists type `$00` objects at dx 0 / dy 0 in sections 1, 4, 5 and 11. Those are the READY-screen objects after the random walk falls into a pit (screenshot checked), not enemies.

## 4. Tooling (rebuild steps — the workspace resets)

```
apt-get install -y cc65                     # da65 disassembler, ca65 assembler
pip install --break-system-packages cynes py65 pillow numpy
```

- `emu.py` — cynes wrapper: `run(frames, 'R+A')`, `ram()`, `peek/poke`, `shot(png)`.
- `rec.py` — boot to stage 1 (`boot()`), per-frame RAM recording, `fresh()` from `st_play.npy`, `grid()` contact sheets.
- `trace.py` — py65 replay that matches cynes exactly (0 RAM diffs over 2 frames). `run_frames(cynes_state, n)` logs every RAM write with its (PC, bank). cynes save layout: CPU A/X/Y at bytes 1-3, SP at 5, PC at 6-7, RAM at offset 25570.
- `build_proto.py` — applies prototype patches to the clean ROM with byte asserts. `mkips.py` makes the IPS.
- Disassembly: split the PRG into 8 banks, `da65 -S 0x8000` for banks 0-6, `-S 0xC000` for bank 7.

Note: the boot timing to stage 1 isn't the same every run (`boot()` uses ~1200 frames); always start experiments from the saved `st_play.npy` state.

- `src/` — ca65 source and `build.py CLEAN.nes OUT.nes` (needs ca65/ld65 from cc65). Every overwritten site is checked against a SHA-1 of the original bytes, and every "free" region must be all `$FF`, so the build refuses a wrong ROM or a clash.
- `bot.py` — scripted stage-1 player (walk/throw/jump, keeps armor) used to reach item pickups; `t_hit.py` — hit/knockback/mercy regression.
- `t_opt.py` (reach the options screen from power-on), `t_menu.py ROM` (navigate every row, change every value, Select reset, wraparound, exit; prints RAM and makes a contact sheet), `t_play.py` (set options through the menu, start a game, check knockback/mercy in play).

- v0.5 tools: `t_fs_dist.py ROM` (spawn distances, original vs KNIGHT), `t_fs_firsthit.py`, `t_fs_tel.py`/`t_fs_tel4.py`/`t_fs_tel2.py` (telegraph; build their test ROMs as the scripts say), `t_fs_lag.py` (py65 idle cycles), `t_menu5.py` (menu incl. FAIR SPAWNS), `t_play5.py` (zombie cap via the menu), `t_orig5.py` (ORIGINAL vs clean and FS OFF vs v0.4; needs `v04.nes`), `t_f191.py`, `t_cover_b2.py`, `spawnlog.py`, `tr2.py`, `callwho.py` (find the code that sets a RAM bit).
- v0.4 tools: `secrets_extract.py ROM [CSV] [INC]` (writes `secrets.csv` and `src/secrets.inc`; run it before building), `gnav.py` (world navigation with 'mercy' travel and 'clear' modes), `t_secret_validate.py`, `t_secrets.py`, `t_endgame2.py` (needs `g6_11.npy`, a stage 6 floor-12 save state made from the clean ROM with `explore6.py`/`step.py`), `t_menu4.py`, `sprsurvey.py`.
- v0.3 tools: `stagesel.py` (stage select), `ramsurvey2.py` (all-sections RAM survey), `t_orig.py` (ORIGINAL vs clean, 600 + 2,600 frames), `t_ladder.py`, `t_air.py`, `t_endgame.py`, `t_menu3.py`. States `st_ladder.npy` and `st_s11.npy` are made by these scripts from the clean ROM.

## 5. Next

0. Fair spawns follow-ups: tune `FS_ZCAP`/`FS_TEL` after playtesting; decide if bosses or platform enemies need a telegraph; a visible blink during the telegraph (currently invisible, it only makes the enemy harmless).

1. Pause-menu access to the options screen.
2. SMART knockback (ground probe), weapon-drop ground probe, SQUIRE preset with gold armor.
3. Remaining design items: timer options, boss HP, extra checkpoints, single quest, Ghosts 'n Goblins + style QoL, save build.
4. Secrets: optionally mark the type-`$20` magician spots; optionally a map-screen version of the list.

### Secret markers — research notes (v0.3, superseded by §3.9)

- **StrategyWiki (NES).** Stage 1 lists four hidden items: King doll (jump off a tombstone after the first Green Monster), extra armor (jump on the right bank after crossing the water), a bad Yashichi (duck between the ponds while Flying Knights are near; −30 s), and a good Yashichi (a jump spot in part 2). No exact NES positions are given, so it can confirm counts and kinds but not coordinates.
- **(Wrong guess, corrected in v0.4: hidden items are type `$11`.) Probable trigger object: type `$20`**, handler bank 4 `$BF0B`. It's invisible while waiting (`$0522 = 0`). It counts ticks of Arthur overlapping it (`$F5F9`) up to 15, then plays sound `$10`, moves up 16 px and becomes visible (sprite `$74`/`$84`). In random stage 1 play it sat in a slot most of the time with `$061D = 3`. Still to do: confirm that it's the hidden-item trigger, find where these objects are placed (the stage object lists), decode the per-stage list to get positions and kinds, and find the duck/jump conditions.
- **Plan once mapped.** An extractor script makes the per-stage table (stage, X, kind, condition) for an include file. Found bits go in `$04C4-$04CF` (8 stages × up to 12 triggers fits; a signature byte clears them at power-on). Map icons would go in the stage-intro map routine (bank 1), and sparkles in the type-`$20` waiting branch (draw a sprite instead of `$0522 = 0`).


## Editions: standard and Classic (build flag, 2026-11-19)

`src/build.py CLEAN OUT [--save] [--classic]`. `--classic` defines `CLASSIC=1` for every source file. In `bank2.s`:
- `spark` (FK id 9, hook at bank 4 `$BB8C`) keeps only the original invisible-item path. No sparkle, duck-star or red-star sprites are ever drawn.
- The SECRETS row in the options tables (`opt_n`/`opt_val`/VN/VD) offers MAP (`$00`) and OFF (`$03`).

Everything else is identical. Without the flag the output is byte-identical to the standard release (v0.5.3 MD5 `44bfafdd69286d6253712462d0378a91`; Classic MD5 `fce9db81dff36652e079501004b3a6b2`). Test: `tools/t_classic.py ROM`.
