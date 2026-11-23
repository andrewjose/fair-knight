# Fair Knight — Ghosts 'n Goblins (GBC) ROM map

Base ROM: `Ghosts'n Goblins (USA, Europe) (GB Compatible).gbc`, 1 MiB, MD5 `9b846e9a4eb6b80cdbc8e6c82f2b9e9e`.
Header: title `GHOSTSNGOBLAG9E`, CGB flag `$80` (GBC-enhanced, runs on DMG), cart type `$19` (MBC5, no RAM), ROM size `$05` (1 MiB). Global checksum is fixed by the build script.
Developer: Digital Eclipse (1999). The title menu has START GAME / OPTIONS / PASSWORD, so the game already has an options screen and password continues.

Status tags: **confirmed** = checked at runtime with the mGBA watchpoint tracer; **static** = from the disassembly only.

Session log
- 2026-11-15: first session. Tooling, Arthur's object layout, hit state, knockback and mercy timer found; prototype 0 built and tested.

---

## 1. Plain-language summary

The GBC port is a separate program from the NES game, written in Game Boy machine code, but it behaves the same. Arthur is the first entry in the game's list of characters. When he's hit, the game switches him into a "hit" state that makes him hop backward, and starts a 2-second invincibility timer.

Prototype 0 (`FairKnight-GBC-proto0.ips`):
- Arthur hops straight up when hit and lands where he was (no backward push).
- Invincibility after losing armor lasts 4 seconds instead of 2.

Both confirmed in the emulator: in the same stage 1 hit, Arthur's position doesn't change at all, and his flashing lasts 120 frames longer.

## 2. For software engineers

**Memory.** Work RAM is `$C000-$DFFF`. Each character is a 0x40-byte record; Arthur's is at `$C5A0`. Every frame the engine copies a record into fast "high RAM" (`$FF86-$FFC5`), runs that character's update function on the copy, then copies it back. So the same field has two addresses: `$C5AE` (stored) and `$FF94` (working copy).

**State machines.** Arthur's update function (`$2FEB`) reads his state number (`$FFA5`) and jumps through an 8-entry table at `$300B`. State 5 is "hit and hopping". Being hit is signalled with bits in a flags byte (`$FFA6`), and the state machine notices them.

**Code location.** Arthur's logic is in bank 0 (`$0000-$3FFF`), which is always mapped, like the NES fixed bank. Hooks there are easy to reach.

**How it was found.** RAM diffs under scripted input (PyBoy) gave the record layout. Then a small C program built on the mGBA library ran the game with write watchpoints and printed the instruction address behind every write. A hand-written SM83 disassembler (`sm83dis.py`) turned those addresses into code.

## 3. Deep technical reference

### 3.1 Arthur's record (`$C5A0`, working copy `$FF86`)

| Stored | Copy | Meaning | Status |
|---|---|---|---|
| `$C5A6-7` | `$FF8C-D` | Update function pointer (`$2FEB` for Arthur) | confirmed |
| `$C5A8-9` | `$FF8E-F` | Sprite/frame data pointer | static |
| `$C5AA` | `$FF90` | X coarse (world) | confirmed |
| `$C5AB` | `$FF91` | Y coarse | confirmed |
| `$C5AC` | `$FF92` | X fine (subpixel) | confirmed |
| `$C5AD` | `$FF93` | Y fine | confirmed |
| `$C5AE` | `$FF94` | Screen X (stage 1 start = `$50`) | confirmed |
| `$C5AF` | `$FF95` | Screen Y (`$60` standing) | confirmed |
| `$C5B4` | `$FF9A` | Sprite attribute flags (bit 0 = facing) | static |
| `$C5B5-8` | `$FF9B-E` | Animation script delay / pointer | confirmed |
| `$C5BF` | `$FFA5` | **State** (1 = normal, 5 = hit hop, 6 = dying, 7 = falling) | confirmed |
| `$C5C0` | `$FFA6` | Status flags: `$10` hit pending, `$20` mercy-invincible, `$40` dead/no armor path, `$80` on ladder (static) | confirmed for `$20` |
| `$C5C1` | `$FFA7` | Horizontal velocity (signed, fine units) | confirmed (`$F0` on hit) |
| `$C5C3` | `$FFA9` | Hop/jump step index (0..`$28`) | confirmed |

Globals: `$CAFB` = flicker phase (toggles 0/`$FF` every 8 frames), `$CAFC` = mercy timer (frames), `$C249/$C253` = camera.

### 3.2 Code (bank 0 unless noted)

| Address | What | Status |
|---|---|---|
| `$2581-$25EB` | Object loop: copy record to HRAM (`$2671`), call update via `$FF8C`, run physics, copy back (`$2735`) | confirmed |
| `$25C1-$25D7` | Horizontal physics with wall checks (`$2852`, `$288C`) | static |
| `$2A65` | Animation script step | confirmed |
| `$2FEB` | Arthur update; state table at `$300B`: 0 `$301B`, 1 `$3022`, 2 `$30EB`, 3 `$3187`, 4 `$3274`, **5 `$354F`**, 6 `$35D3`, 7 `$37C0` | confirmed |
| `$3342-$338B` | Hit taken with armor: flags `\|= $30`, `$CAFB = 0`, **`$CAFC = $78`** (`$3375`), knockback velocity **`$C5C1 = $F0`** (`$3387`) | confirmed |
| `$338D-$33AB` | Hit taken without armor (death): flags `\|= $60`, `$CAFC = $78`, velocity `$F0` (`$33A6`) | static |
| `$354F-$35D0` | State 5 hop: Y from table `$3232[$FFA9]`, **`CALL $3725` (`$35CD`)** for horizontal motion | confirmed |
| `$35E1-$360D` | Mercy countdown: while flag `$20`, `DEC $CAFC`, toggle `$CAFB` every 8 frames; at 0 clear `$20` | confirmed |
| `$3725` | Apply horizontal velocity `$FFA7` with wall checks | confirmed |
| `$37C0` | State 7 falling (also continues horizontal motion via `$3725` at `$3816`) | static |

### 3.3 Prototype 0

| File offset | Original | New | Effect |
|---|---|---|---|
| `0x35CD` | `CD 25 37` | `00 00 00` | no horizontal motion in the hit hop |
| `0x3387` | `3E F0` | `3E 00` | knockback velocity 0 (armor-loss hit) |
| `0x33A6` | `3E F0` | `3E 00` | knockback velocity 0 (death hit) |
| `0x3375` | `3E 78` | `3E F0` | mercy 120 → 240 frames |
| `0x14E-0x14F` | checksum | recomputed | |

Patched MD5: `bcb540bc2ec1a2a16e2d6dbdaf1b92e6`.
Test (mGBA, stage 1, idle): original, hit at frame 1639, X `$50` → `$29` over 38 frames, flicker ends at 1799. Prototype: X stays `$50`, flicker ends at 1919; zombies walk through Arthur during the window.

## 4. Tooling (rebuild steps)

```
apt-get install -y libmgba-dev
pip install --break-system-packages pyboy pillow numpy
gcc -O2 -o mtrace mtrace.c -lmgba -lm
```
- `mtrace ROM SCRIPT` — headless mGBA with write watchpoints (`watch ADDR` logs frame, address, old/new value, PC, bank, HL). Script commands: `wait N`, `hold KEYS N`, `shot F.ppm`, `peek`, `poke`, `dump ADDR LEN FILE`. Savestate loading didn't work in this build, so scripts boot from power-on: `bootpre.txt` reaches stage 1 at frame 1260 (START taps at 4, 6, 8, 10, 12 s).
- `sm83dis.py ROM BANK ADDR COUNT` — SM83 disassembler (written here; the mGBA library decoder mis-sizes 3-byte instructions).
- `gemu.py` / `grec.py` — PyBoy wrapper and RAM recorder (timing differs from mGBA: in PyBoy the first hit comes at frame 48 of `st_after.bin`).
- `build/build_proto.py` — byte-asserted patcher + checksum fix.

## 5. Next

- Hit-path flags: confirm `$40` / `$80` meanings; find the collision code that sets `$FFA6` bit `$10`.
- The game's own OPTIONS menu and PASSWORD system: look at what's there before adding Fair Knight's menu (passwords may make unlimited continues partly redundant).
- Weapon variable and pickup routine, spawn routine, timer, lives.
- Free space: MBC5 at 1 MiB can grow to 2+ MiB; check for empty banks first. Save build: cart type `$1B` + RAM size byte.

---

## 6. Fair Knight v0.1-v0.9 (2026-11-16)

Session log
- 2026-11-16: options page, all gameplay options except SECRETS, continue preselect. Builds v0.1-v0.7 in `builds\`. Source `src\fk.asm`, built by `tools\build.py` (own SM83 assembler `tools\sm83asm.py`; every hook site byte-asserted).

### 6.1 Plain language
There's a FAIR KNIGHT row on the OPTIONS screen. It opens a page with a preset (KNIGHT, LEGEND, ORIGINAL, or CUSTOM once you change a line) and one line per option. ORIGINAL plays exactly like the unmodified cartridge, with one intended exception (v0.8): after a game over, the title cursor starts on CONTINUE.

### 6.2 For software engineers
- **Banks.** The cartridge is 64 banks of 16 KB, and only one switchable bank is visible at a time. The game stores each bank's number at `$7FFF` and its interrupt handlers save/restore it, so our code can switch banks safely. Most new code sits in empty bank `$20`. Small bank-0 "trampolines" save the caller's bank, switch to `$20`, call the handler, and switch back. Code that has to call the game's own bank-1 routines (the item spawner) lives directly in bank 0, which is always mapped.
- **Settings.** One byte, `FK_SET` (`$DF02`). A bit set to 1 means "original behaviour", so a fresh power-on (byte 0, signature written at boot) means KNIGHT. WRAM `$D7D2-$DFFF` is unused by the game (30k-frame write canary).
- **Hooks.** Each changed instruction is replaced with a `call` to our handler. The handler re-executes the replaced instruction, so with the option off the game runs the original code path. ORIGINAL is checked by running the clean ROM and the build side by side for 4,000 frames, idle and scripted, and comparing every frame: identical for every build v0.1-v0.8. The comparison starts from power-on and never reaches a game over, so it excludes only the CONTINUE preselect, which is the one intended ORIGINAL difference.
- **Objects.** 32 slots of `$20` bytes from `$C5A4`; slot 0 is Arthur. The update routine works on a copy in HRAM (`$FF8A-$FFA9`); a second buffer `$FFAA-$FFC9` is used to build new objects.

### 6.3 Deep technical

**Fair Knight WRAM:** `$DF00-01` sig 'FK', `$DF02` FK_SET, `$DF03` FK_SET2 (bits 1-0 SECRETS: 0 SPARKLES, 1 MAP, 3 OFF), `$DF04` preset (bit 7 CUSTOM), `$DF05-06` trampoline A/bank, `$DF07` page row, `$DF08` previous pad, `$DF09-0A` scratch, `$DF0B` FK_STG (stage of the found list), `$DF0C` frame counter, `$DF10-17` found bitmap, `$DF20-29` two WRAM metasprites (sparkle normal/red).

**FK_SET bits (1 = original):** `$01` knockback, `$02` mercy NORMAL, `$04` weapon drop off, `$08` ladder off, `$10` air OFF, `$20` secrets off (reserved), `$40` endgame aid off, `$80` fair spawns off. Presets: KNIGHT `$00`, LEGEND `$6B`, ORIGINAL `$FF`.

**Object record (slot base +n ↔ HRAM `$FF8A+n`):** +0 type, +1 flags (bit 0 active, bit 1 delete, bit 2 physics), +2/3 update ptr, +4/5 anim ptr, +6 X block (16 px), +7 Y block, +8 X fine (px = hi*16 + lo/16), +9 Y fine, +$10 sprite flags (`$FF9A`, bit 2 = no collision), +$19/$1A item descriptor (items), +$1B state (`$FFA5`), +$1C flags (`$FFA6`), +$1D velocity (`$FFA7`), +$1F param (`$FFA9`: item's weapon / boss HP).

**Hook sites (original bytes asserted by build.py):**

| Site | Original | Purpose |
|---|---|---|
| 0:`$016C` | `CD C4 05` | boot: init FK WRAM |
| 3E:`$4A13/$4A1F/$4A43/$4A4D/$42B5` | (see build.py) | OPTIONS: 3rd row FAIR KNIGHT, opens page |
| 0:`$3387`,`$33A6` | `3E F0 EA C1 C5` | knockback speed |
| 0:`$35CD` | `CD 25 37` | hit-hop horizontal motion |
| 0:`$3375` | `3E 78 EA FC CA` | mercy 120/240 frames |
| 1:`$4711` | `F0 A9 C3 E7 06` | weapon item collected → drop old weapon |
| 0:`$3201`,`$3819` | `FA E0 C0` | jump / fall input → air control |
| 0:`$32C6` | `3E 01 E0 A5` | ladder exit → 42-frame mercy at the top |
| 1:`$72AB` | `21 D2 74` | stage 6 boss spawner → cross item |
| 0:`$0EB2` | `EA E9 C1` | title init → cursor on CONTINUE (v0.8: every preset, ORIGINAL included) |
| 0:`$05A6` | `CD 9A 38` | gameplay frame, before OAM build → sparkle sprites (v0.9) |
| 1:`$7997` | `F0 8B F6 02` | hidden-item trigger touched → found bit (v0.9) |
| 3E:`$4596` | `CD 41 08` | READY text printed → secrets list (v0.9) |
| 1:`$74A3` | `79 EA C2 C0` | stage 6 boss dies → torch kill counts as win when ENDGAME AID on (v0.8) |
| 1:`$4B06` | `FA B8 C0` | zombie generator → skip if within 2 blocks |
| 0:`$3335` | `F0 8A FE 36` | enemy touch → rising zombie can't hurt |

**Free space used:** bank 0 `$3DF6-$3FFA` (516 of 522 bytes, nearly full: new bank-0 code needs another free area), bank `$20` `$4000-$451C`.

**Game facts found:**
- Weapon `$C0B6` (0 lance, 1 dagger, 2 torch, 3 axe, 4 cross). Projectile templates `$3D35+32w`, types 2-6. Weapon item descriptors bank 1 `$49A7+7w` (template, anim, collect handler `$470C`, weapon). Item spawner 1:`$45D0` (de = descriptor; position from current HRAM `$FF90-92`; returns hl = slot).
- Jump = state 3 (`$315B` start, ±`$10` speed if moving), fall = state 7, ladder = state 4 (`$3274`), shared exit `$32C6`. Walk speed max ±`$10`.
- **Endgame rule (real GBC rule):** the stage 6 boss (type `$20`, spawner 1:`$72AA`, hit handler 1:`$7470`, 8 HP in +$1F) only takes damage from torch (projectile type 4) or cross (type 6). When it dies, `$C0C2` = 0 if the killing shot was the cross, else 1. Stage clear (`$036D`): if stage index `$C0AD` = 5 and `$C0C2` ≠ 0 → scene 6, and stage 6 is played again (not stage 5 as on the NES). Verified: torch kill → `$C0C2` = 1; lance does no damage (HP stays 8).
- Stage index `$C0AD` (0-5 = stages 1-6, 6 = final), loop `$C0AE`, lives `$C0AC`, continue-available `$C0A4`. CONTINUE (`$0257` → `$06A7`) is unlimited in the original and keeps the stage; the title cursor `$C1E9` wraps over 3 or 4 rows with no blank row (bank 3E `$40F7/$410D`).
- Zombie generator 1:`$4AD4`: ~1 in 128 frames, already capped at 3 (`$C0B8`), columns camera + 14/1/10 blocks (`$4B03`), Y = `[$C5A1]+5`. Zombies are already harmless while rising (state < 2, ~60 frames) in the original.
- Global debug invincibility: `$C0A1` bit 1 (used by tests).
- Stage object lists: 6-byte records copied to `$C29E` (type, flags, X, Y, 2 params; bit 0/1 of flags = spawned/killed), spawned via table `$24D4` (type index → bank-1 spawner). This is where secret triggers should be found (next step).

**Dead ends / bugs fixed:** first LCD-off wait polled `LY == $91`. It hung because the game's VBlank handler runs past line 145 every frame. Fixed with `di` plus waiting for `LY >= $90`. `$0213` is "wait for button release", not a sound routine.

**Tests (tools\, PyBoy):** `t_menu.py` (page, presets, flicker = 1 distinct frame over 8), `t_hit.py`, `t_wdrop.py`, `t_air.py`, `t_ladder.py`, `t_endgame.py`, `t_continue.py`, `t_spawn.py`, `t_rise.py`, `t_orig.py` (ORIGINAL vs clean ROM), `t_stage.py` (start at any stage by poking `$C0AD` during the intro), `t_run.py` (auto-runner).

### 6.4 SECRETS (v0.9)

**Plain language.** Every stage hides items that only appear when Arthur jumps or walks into an invisible spot. With SPARKLES, a small "+" floats on each spot you haven't found yet. It is white-green, or red for the frog curse. The READY screen lists what you've found in the stage, with SPARKLES and with MAP. OFF is the original game.

**For software engineers.**
- **Level data.** Each stage is a list of 6-byte records (object type, flags, X, Y, a 16-bit parameter). The game spawns a record's object when the camera reaches it, like lazy loading. Type `$1A` records whose parameter block starts with `1B 7C` are hidden-item triggers.
- **Item kind.** It isn't stored as a number. The parameter block names a "reveal" routine, and that routine spawns an item whose pick-up routine has the effect. `tools/secrets_extract.py` follows that chain statically to label every trigger, and writes both `secrets.csv` and the table compiled into the ROM.
- **Sprites.** The game builds sprites in two steps: objects push "draw this metasprite at x,y" requests into a queue, and once per frame the queue is expanded into the 40 hardware sprite slots. We push our requests into the same queue, so we never fight the game over sprite slots. The metasprites live in WRAM, because the expander reads them from a different ROM bank than ours.

**Deep technical.**
- **Stage lists.** Pointer `$C228/9` in bank `[$C201]`, copied to `$C29E` at stage start. Records are 6 bytes, `$FE` marks a section break (also 6 bytes) and `$FF` ends the list. ROM locations per stage: 1 `0A:$6558`, 2 `0B:$53D0`, 3 `0D:$54E0`, 4 `0F:$5982`, 5 `10:$6EDE`, 6 `11:$6290`.
- **Trigger record.** Type `$1A` → spawner 1:`$790D`. Its parameter (bank 1, 10 bytes) is `[obj template $7C1B][item template $451C or $4518][1A 00][item X block][item Y block][reveal handler]`.
- **Trigger object.** Type `$3A`, update 1:`$7978`. On touch, 1:`$7997` copies the item X/Y to `$C59E` and jumps to the reveal handler. Touch zone ≈ the record's block, so most triggers need a jump.
- **Reveal handlers** (call 1:`$45D0` with a descriptor):

  | Handler | Descriptor | Effect | Name |
  |---|---|---|---|
  | `$4691` | `$4888` | score +`$0100` | MONEY |
  | `$46C1` | `$489D` | score +`$0050` | COINS |
  | `$46B0` | `$4896` | time +1:00 (`$0CA6`, minutes `$C0AF`, seconds `$C0B0`) | CLOCK |
  | `$46D2` | `$48A4` | lives +1 | 1UP |
  | `$46E0` | `$48AB` | `$06FB`: armor back on | ARMOR |
  | `$46A2` | `$488F` | `$CB00`=1 → `$3404`: about 10 s frog | FROG, harmful |
  | `$46EE`/`$46F4`/`$46FA`/`$4700`/`$4706` | `$49A7`+7w | weapon | LANCE / KNIFE / TORCH / AXE / CROSS |

- **GBC vs NES:** 30 vs 29. Per stage 3/5/6/5/5/6 vs 4/5/7/4/4/5. The GBC has no time-down item and no duck triggers. Its only harmful item is the frog curse: stage 3 X 2928 and stage 4 X 2176, at the positions of the NES "kind 11" item.
- **Sprite queue.** 0:`$2DB7` (hl = metasprite, d = screen X, e = screen Y, a bit 0 = flip). It appends a 5-byte entry to `$C9B0` (count `$CAF2`, max 64). The expander 0:`$2DF0` maps bank `[$C203]` and fills OAM `$C000`, alternating direction each frame when full. Metasprite format: count, then dy, dx, tile, attr per sprite.
- **Screen position.** `(block*16 − [$C255]/[$C256]) + 4`. Shown only when the block is within camera `$C251` +0..10 and `$C252` +0..8, and screen Y < 128 (status bar).
- **READY screen.** 3E:`$458B` prints "READY" (`$6D47`, font 0-9 A-Z = `$00-$23`, space `$FF`) at col 7 row 8 and the lives at row 10. We print at row 12 and rows 13-14 (3 names per row, 6 columns each).
- **Tile.** VRAM bank 0 tile `$6F` was blank in all 24 samples (6 stages × 4 points). `spk_gfx` writes it every 32 frames with `di` and a STAT mode < 2 check per byte, and restores VBK. Risk: a boss or effect that uses tile `$6F` would get a "+" in that 8×8 cell.
- **Dead ends.** Tiles `$74`/`$75` look like a "+" in stage 1 but belong to an enemy (crow) and differ per stage. OBJ palettes 0-3 render dim pink and 5 is dark; 7 (white-green) and 6 (red) read well in stages 1, 3 and 4.
- **Tests.** `t_secrets.py`, `t_secmenu.py`, `secrets_extract.py`; also the ad-hoc scenes listed in CHANGELOG v0.9.


## 7. CLASSIC build flag (v0.9 Classic, 2026-11-19)

- `python3 tools/build.py SRC OUT --classic` defines `CLASSIC` for the `build.py` preprocessor (`.if NAME`, `.if !NAME`, `.else`, `.endif`, nestable; removed lines become blanks so line numbers stay valid). Without the flag, the output is byte-identical to v0.9 (MD5 `dfafe0ec370ea3fde899fe22c1bfce71`).
- Under `.if !CLASSIC`:
  - the `T_spk` trampoline;
  - the 0:`$05A6` hook (Classic keeps the original `cd 9a 38`);
  - `h_spk`, `spk_gfx` and `g_spk`, so tile `$6F` is never uploaded.
- SECRETS in Classic: `FK_SET2` bits 1-0 = 0 MAP (KNIGHT and power-on default), 3 OFF (LEGEND and ORIGINAL). 1 is unused (shown as MAP). The menu strings are `s_sec`/`d_sec` Classic variants. `h_rdy` and the found-bit hook (`T_sfnd`) are unchanged.
- Test: `tools/t_classic.py ROM SET2 [shotprefix]` counts tile-`$6F` OAM frames and samples VRAM `$86F0` at the stage 1/3/4 trigger spots.

## 8. Crouch and camera (v0.10, 2026-11-19)

### 8.1 Plain language
Letting go of Down while holding a direction used to leave Arthur crouched; QUICKSTAND stands him up at once. The camera normally keeps Arthur in the middle of the narrow GBC screen; CAMERA AHEAD moves him toward the back so you see more of what's coming, and glides across when he turns.

### 8.2 For software engineers
- The crouch state is a per-frame handler (a state machine entry). Its "stay crouched?" test is a bitmask over the held-buttons byte. The original mask includes Left and Right, which is why a held direction pinned Arthur down. The fix swaps the mask through a tiny function in the fixed bank.
- The camera is a "follow" controller with no smoothing: every frame it asks the scroll routine to move by (Arthur's screen X − 80). The scroll routine clamps to the level (like clamping a viewport to a document) and streams one new 16-px column of tiles whenever the camera crosses a column boundary, so a frame must never ask for more than 16 px. AHEAD replaces the constant 80 with a target that moves 1 px per frame toward 54 (facing right) or 106 (facing left); it snaps the target to Arthur whenever he is more than 16 px off (pinned at a level edge, respawn), so requests stay small. Sprites, sparkles and enemy spawns all derive from the camera variables, so they follow automatically.
- Testing caveat: the random generator mixes in the hardware timer register, so the exact CPU time of any hook changes enemy randomness. Behaviour comparisons with the clean ROM therefore patch that one read in both ROMs (test-only).

### 8.3 Deep technical
- **Crouch, state 2 handler 0:`$30EB`.** `$30FA-$310C`: Left → `$36C4`, Right → `$36B0` (turn). `$310D`: A (bit 0) → attack latch `$FFA8` bit 0, `$315B`. `$312B`: B (bit 1) → `$360E` (crouch fire), latch bit 2. `$3143` `ld a,[$C0E0] / and $B2 / jr nz,$3155` (stay crouched while Down, B, Left or Right held); else stand (`$314A`…). v0.10 hook → `h_qs` 0:`$00BE`, mask `$82` (Down, B) when `FK_SET2` bit 2 = 0.
- **Camera, 0:`$38B5`.** Saves bank to `$C0E7`. d = Arthur screen X from (`$C5AA` − `$C251`)·16 + (`$C5AC`>>4) − `$C253`; e = screen Y likewise from `$C5AB`/`$C5AD`, `$C252`/`$C254`. `$38F1` d −= `$50`, `$38F5` e −= `$48`, `$38F9` `call $1A54`, restore bank.
  - Callers: 0:`$04A0` (intro/attract loop `$0491`), 0:`$0537`/`$053A` and 5:`$4118`/`$411B` (stage setup, LCD off, called twice), 0:`$058E` (gameplay frame, returns to `$0591`).
- **Scroll, 0:`$1A54`** (d = signed X request, e = signed Y request). X right clamp: cam + d + `[$C214]` (16-bit, = −max cam; stage 1 `$F2A0` → max 3424) must stay negative, else d is cut. X left: no move if cam = 0 or (cam>>4) < `[$C241]` (section left limit: stage 1 0 → 112 → 175 at the boss); otherwise clamp at 0. Y the same with `$C24B/C`, `$C216`. Then cam `$C249/A`, camY `$C24B/C` += d/e; column streaming when (cam>>4) ≠ (`$C24D`>>4): `$1BC2` (left) / `$1BE4` (right), one column per call; rows likewise via `$C24F`. `$1987` derives `$C251`/`$C253` (block/fine X), `$C252`/`$C254`, and SCX/SCY shadows `$C255`/`$C256` (written to `$FF43`/`$FF42` at the top of the loop).
- **Vertical scrolling** exists (stages 2, 4, 5, 6 climb; camY also moves during hit hops in stage 1). v0.10 leaves Y untouched.
- **Hook 0:`$38F1`** `7A D6 50 57` → `call T_cam / nop`. `h_cam` (bank `$20`): push hl, `ld hl,sp+6` → caller return; ≠ `$0591` or `FK_SET2` bit 3 set → `FK_CAMT` = `$50`, d −= `$50` (original). Else (bc saved): target b = 54 if `$C5C0` bit 0 (facing right) else 106; c = `FK_CAMT`; if (d − c + 16) ≥ 33 then c = d; c moves 1 toward b; `FK_CAMT` = c; d −= c.
- **Spawn columns** are camera-relative (zombie generator 1:`$4AD4`, columns camera + 14/1/10 blocks); `h_zx` window raised to ±3 blocks.
- **Free space used:** 0:`$00BE-$00D6` (25 of 66 bytes). Bank 0 helpers start at `$3DF7` since v0.11: `$3DF6` must stay `$FF` (it ends the game's last animation list `2E 2F`; using it caused the Red Arremer hit glitch). 5 bytes left (standard).
- **RNG:** 0:`$122F` (state `$C0E8-$C0EA`), mixes `ldh a,[$FF04]` at `$1245`. Test ROMs replace `F0 04` with `3E 00` there in both clean and build to compare logic without CPU-timing noise.
- **Tests:** `t_qs.py`, `t_cam.py`, `t_camturn.py`, `t_camrun.py` (`--fly`), `t_spkcam.py`, `t_spawn2.py`, `t_menu10.py`, `t_orig.py` (now holds buttons and sets ORIGINAL after `h_init`, adds a crouch script).
