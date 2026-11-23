# Fair Knight — Ghouls 'n Ghosts (Genesis / Mega Drive) — Changelog

Source ROM: `Ghouls 'n Ghosts (USA, Europe).md`, 655,360 bytes,
MD5 `c61ff4bcdf10813c74f36ab57e29f646`, CRC32 `4f2561d5`.
Source and tooling are in the combined Fair Knight repo (`Genesis/`); there is no separate Genesis repo.

## v0.5 — options page fits the screen

### Plain-language overview
- The bottom line of the FAIR KNIGHT OPTIONS page ("A RESET PRESET   START EXIT") was cut off on TVs and in emulators that hide the screen edges.
- The setting description and the two help lines now sit higher, clear of the bottom edge. Nothing else changed.

### Engineer level
- TVs (and many emulators, to imitate them) hide roughly the outer 8 px of the picture ("overscan"). The page drew its last line in the last 8-px row of the 224-px screen, so it fell inside that hidden band.
- The page is drawn straight into a grid of 8x8 text cells, so the fix is just new row numbers: description row 24 → 20, help lines 26/27 → 23/24. The lowest text now ends 24 px above the bottom.
- **Tested**: `tools/t_menu.py` (every row, presets, reset, wrap, 0/59 idle frames changed, START back to OPTION); screenshots checked for leftover text.

### Deep technical
- `src/menu.s` `draw_all`: `move.w #24,d0` → `#20` (description), `#26` → `#23` and `#27` → `#24` (help lines). Plane A nametable `$C000`, rows are 128 bytes; `cls` still clears rows 0-27.
- Code size unchanged (2252 bytes); only those three immediates differ from v0.4.

## v0.4 — ladder safety; continues checked

### Plain-language overview
- **LADDER SAFETY ON**: when Arthur climbs over the top of a ladder he flashes and can't be hurt for 0.7 s, so an enemy waiting at the top can't hit him the instant he arrives.
  - KNIGHT and LEGEND have it on. ORIGINAL has it off.
- **Continues**: the Genesis game already has unlimited continues. After GAME OVER a CONTINUE screen counts down from 9; press START to keep going.
  - There's no menu on that screen, so there's nothing to preselect. Nothing was changed.

### Engineer level
- The game already has an "invincible for a while" mode: the one used after a hit. It wraps Arthur's normal behaviour, skips hit checks, blinks the sprite, and counts a timer down.
- Ladder safety switches that wrapper on for 42 frames when the "climbed over the top" step finishes. It only does so if no other wrapper is running, so a running hit-mercy is never shortened.
- **Tested**: synthetic test from the stage-1 start. Arthur is put into the ladder top-out state 12 frames before the enemy contact that normally hits him.
  - ON: invincible for 43 frames, no hit, X unchanged, back to normal afterwards.
  - OFF: hit at frame 233, thrown 80 px.
  - No in-game ladder test yet: the stage-select poke (`FFB22E`) didn't reliably load other stages headlessly.
- **Continues**: tested from a clean-ROM CONTINUE-screen state. 10 continues in a row on PRACTICE and 6 on PROFESSIONAL; the screen came back every time.

### Deep technical
- **Sites**: `$8F7C` and `$8F20` (8 bytes each), originally `move.l #$8596,$334C(a5)` (end of the ladder top-out state `$8F36`; climb state `$8D64`). Replaced by `jsr fk_ladder; nop`.
- **`fk_ladder`**: writes the original value. Then, if `FKB_LADDER` (FK_SET2 bit 0) = 0 and `$3338(a5)` = `$84EE` (plain wrapper), it sets `$3318(a5)` = 42, `$3317(a5)` = `$FF` and `$3338(a5)` = `$8CCA`.
- **Mercy wrapper `$8CCA`**:
  - Decrements `$3318`, blinks via `+$0C` bit 15 every 2 frames, and runs the inner behaviour `$334C`.
  - At 0 it clears `$3317` and restores `$3338` = `$84EE`.
  - `$84EE` checks `+$08` bit 2 (hit → `$8B98`) and bit 3 (death → `$A16A`). The mercy wrapper doesn't.
  - Enemy contact tests `$3317` at `$11020`.
- **Continue/difficulty**: difficulty is the word at `$FFFE94` (1 PRACTICE, 0 PROFESSIONAL); the option value table is `$252E`. Lives are at `$FFB044`.
- **Tests**: `tools/t_ladder.py`, `tools/t_cont.py` (`st_cont.bin`).

## v0.3 — air control

### Plain-language overview
- **AIR CONTROL FULL**: in the original, a jump is locked in the moment you press the button. Now Left/Right steer Arthur in the air.
  - Steering covers turning around mid-jump and pushing forward out of a standing jump.
  - The jump height is unchanged.
  - If you don't touch the pad, the jump is exactly the original one.
- Getting hit still throws you the same way; you can't steer out of a hit.
- KNIGHT and LEGEND have it set to FULL. ORIGINAL has it OFF.

### Engineer level
- All of Arthur's airborne frames (jump, fall, hit hop) run one routine.
- The patch runs inside it before the physics step. If Left or Right is held, it sets the sideways speed to the normal jump speed in that direction. Otherwise it leaves the speed alone.
- The game stores the direction of travel twice: once in the speed and once in which jump animation is playing.
  - It "corrects" the speed to match the animation every frame. That's the same class of bug as the NES report where reversing made Arthur drop straight down.
  - So the patch swaps the animation to match the new direction.
- The hit hop is recognised by the routine that's in control at the time, and is skipped.
- **Tested** from the stage-1 start:
  - Jump right then hold Left at frame 10: X goes +17 then back to −70 by frame 57, against +40 with OFF.
  - The height curve is identical in both (peak 36 px), so there's no drop.
  - A neutral jump steered right gives +9 px by frame 10 (0 with OFF). An untouched jump gives the same X/Y as the clean ROM.
  - A hit while holding Left gives the same −39 px with FULL and OFF.
  - ORIGINAL vs clean: 0 differing frames over idle 600, bot 3000 and the 400-frame weapon-pickup run.

### Deep technical
- **`$8AC6` (8 bytes)**: the original `cmpi.l #$1219A,$24(a1)` is replaced by `jsr fk_air; nop`. `fk_air` ends by re-executing the cmpi, so the `bne` at `$8ACE` sees the original flags.
- **Conditions**: `FKB_AIR` = 0, `$3338(a5)` ≠ `$8C60` (the hit continuation, which clears `$32DC` and jumps to `$8A72`), and the input `$32DC(a5)` & 3 is exactly 1 (right) or 2 (left).
- **Speed**: vx = ±word at `$9196 + 8*armour(+$11)` (`$0100`/`$01E6`).
- **Animation**: if `+$24` is `$1219A` or `$1221A`, it's set to `$1219A` for vx ≥ 0 and `$1221A` for vx < 0. The code at `$8AC6`-`$8B00` negates vx/ax when they disagree with the animation.
- **Not changed**:
  - The fall-speed clamp at `$8B22` (vx → ±`$100` once vy ≤ −`$500`) is untouched.
  - Facing is left to the original mid-air turn code at `$8A72`-`$8AC4`.
  - Wall collision is by vx sign in `$124AE`, so it follows the steering.
- **Input byte `$32DC(a5)`**: bit0 R, bit1 L, bit2 D, bit3 U, bit4 fire, bit5 jump. `$32DD` is the previous frame.
- **Test**: `tools/t_air.py`.

## v0.2 — weapon drop

### Plain-language overview
- **WEAPON DROP ON**: when you pick up a new weapon, your old one is not lost.
  - It pops out and lands a short way back toward where the stage began.
  - Walk back over it to swap again, or leave it.
  - It always goes backwards along the stage, never ahead of you, so you won't run into it by accident.
- KNIGHT and LEGEND have it on. ORIGINAL has it off.

### Engineer level
- The weapon you touch is an ordinary game object. Normally, touching it swaps Arthur's weapon and marks the object for deletion.
- The patch keeps the object alive instead and rewrites its contents to the old weapon.
- It then hands the object back to the game's own "item pops out of a chest" physics, with the sideways speed forced toward the stage start. Because the existing physics are reused, the landing, ground collision and pick-up rules all come from the original game.
- One extra hook was needed. A landing item normally re-rolls a random weapon (that's how chest items decide what they are). The patch skips the roll for the one object it relaunched.
- **Tested**: from a state just before the first stage-1 weapon pickup (lance → dagger).
  - In KNIGHT, the lance hops 25 px back and lands 33 px behind Arthur, just outside the 24 px pick-up box.
  - Walking back picks the lance up again, and the dagger drops in its place.
  - ORIGINAL matches the clean ROM on every frame of the same 400-frame run.

### Deep technical
- **`$1B600` (10 bytes)**: the original `move.b 11(a1),d0; jmp $13566` is replaced by `jmp fk_wdrop; nop; nop`.
  - `$13566` is the weapon swap. Its argument is d0 = new weapon; it writes Arthur `+$2D` = old and `+$2C` = new.
  - The touch routine `$1B560` has already set object `+$40` = `$0400` (collect), with the previous value in d2.
  - `fk_wdrop` runs only for a different weapon, with `FKB_WDROP` = 0 and object `+$30` = `$1B1AA` (the standard item class whose substate table is `$1A7AC`). In that case it:
    - saves d2/a1, calls `$13566`, and restores `+$40` from d2;
    - sets `+$0B` = old weapon and `+$41` = 2 (airborne, `$1A942`), `+$42` = 0, `+$0F` = 16;
    - sets vx `+$14` = `-$0100`, vy `+$16` = `$0400`, `+$18` = 0, gravity `+$1A` = `-$0050`. These are the pop values from `$1A876`-`$1A898`, with vx sign fixed;
    - stores a1 in `FK_DROPOBJ` (`$FF5A06`).
- **`$1AB1C` (6 bytes)**: the original `moveq #0,d0; movea.l $32CE(a5),a4` is replaced by `jmp fk_wpick`.
  - This is the item's "landed" step: it rolls a weapon from the table at `$1AAF4`, using `$13070` RNG and avoiding the last roll `$6C54(a5)`.
  - `fk_wpick` jumps to `$1AB62` with d0 = `+$0B` when a1 = `FK_DROPOBJ`, which stores the weapon and sets the animation from `$1ABD6`. Otherwise it replays the two instructions and continues at `$1AB22`.
- **Not covered**: the special flying item class at `$1B2F0` (`+$30` = `$1B554`, flies to `$6E86`/`$6E88`) keeps the original swap, without a drop.
- **Weapon ids** (Arthur `+$2C`): 0 lance, 2 dagger confirmed in game. The fire-routine table is at `$13506`, indexed by `+$11` and `+$2C`.
- **Tests**:
  - `tools/t_wdrop2.py` uses `st_wd.bin`, a clean-ROM state that also loads into FK builds.
  - `tools/t_parity_wd.py` covers ORIGINAL vs clean across the pickup and the walk back: 0 of 400 frames differ.

## v0.1 — options page, knockback, mercy time

### Plain-language overview
- The game's OPTION screen now shows "C BUTTON - FAIR KNIGHT OPTIONS". Press C to open a new page of settings.
  - Up/Down picks a row and Left/Right changes it.
  - A resets the current preset, and START goes back.
- There are three presets:
  - **KNIGHT** (the default): the recommended fair settings.
  - **LEGEND**: hits work as in the original game; the new controls and help go here as they're added.
  - **ORIGINAL**: plays exactly like the unmodified game.
- Changing any single row turns the preset into **CUSTOM**.
- **KNOCKBACK OFF**: getting hit no longer throws Arthur backwards, so you don't get knocked into a pit. He still loses his armour.
- **MERCY TIME LONG**: after a hit you are safe for twice as long, 4 seconds instead of 2.
- Nothing is saved, the same as the original game. Settings reset to KNIGHT at power-on.

### Engineer level
- **Size**: the ROM is grown from 640 KiB to 1 MiB. The original image has no usable free space, so all new code lives in the added area at `$0A0000`. The header's "ROM end" field and the cartridge checksum are rewritten so emulators and flash carts accept it.
- **Hooking**: hooks work like monkey-patching a compiled binary.
  - A few original instructions are overwritten with a call (`JSR`) into the new code.
  - The new code does what the overwritten instructions did, then optionally something different, and returns.
  - Every overwritten site is checked byte-for-byte by the build script. If the source ROM differs, the build stops rather than producing a broken image.
- **Settings storage**: a 4-byte block of unused work RAM at `$FF5A00`. Bits are *inverted* (1 = original behaviour). The console clears RAM at boot, so all bits are 0 and the defaults come up as KNIGHT with no extra code.
- **Options page**: the page is drawn straight into the background tilemap.
  - It reuses the letter tiles the game already has in video memory for its own options screen, so no new graphics were needed.
  - All drawing happens during the game's own frame-wait loop with interrupts masked, the same way the original screen draws. That rules out tearing or flicker: in an idle test, 0 of 59 frames changed.
- **Testing**: done headlessly with Genesis Plus GX through libretro.
  - Scripted button presses and RAM reads, with screenshots checked by eye.
  - **ORIGINAL vs the clean ROM**: the RAM was compared on every frame, over a 600-frame idle run and a 3,000-frame random-input run. 0 frames differed, ignoring stack scratch.

### Deep technical
- **Build**:
  - `src/build.py ../gng.md ../out/fk.md` assembles `src/*.s` with GNU as (`m68k-linux-gnu-as -m68000 --register-prefix-optional`).
  - Each `.sXXXX` section is linked at its patch address and `.fk` is linked at `$A0000`.
  - The script asserts the original bytes and an equal-length patch at each site, and pads to 1 MiB with `$FF`.
  - It then writes `$000FFFFF` at `$1A4` and the checksum (sum of big-endian words `$200`..end) at `$18E`.
- **Patch sites**:

  | Site | Original bytes | Original instructions | Replacement |
  |---|---|---|---|
  | `$8BA6` | `41FA00B0 33580014` | `lea $8C58(pc),a0; move.w (a0)+,$14(a1)` | `jsr fk_kbtab; nop` |
  | `$8CBC` | `3B7C0078 3318` | `move.w #120,$3318(a5)` | `jsr fk_mercy` |
  | `$2408` | `46FC2300 61000032` | `move #$2300,sr; bsr $2440` (OPTION loop input) | `jsr fk_opt; nop` |

  - `$8BA6`: the hit handler `$8B98` loads the hop table `$8C58` = `0200 0440 FFC8 0000` (vx, vy, gravity, ax). KNOCKBACK OFF substitutes `0000 0440 FFC8 0000`: same vertical hop, no horizontal throw.
  - `$8CBC`: the mercy timer is set on landing. LONG writes 240.
  - `$2408`: `fk_opt` draws the hint and polls C (bit 5 of `$FFF603`, newly-pressed). If C is pressed, it runs `fk_page`, then re-enters the OPTION init at `$233C`.
- **RAM**: `$FF5A00` holds `FK_SET`, inverted:
  - bit 0 knockback, bit 1 mercy, bit 2 weapon drop, bit 3 air control, bit 4 spawns, bit 5 endgame, bits 6-7 secrets.
  - `$FF5A01` is `FK_PRESET` (0/1/2, bit 7 = CUSTOM), `$FF5A02` is `FK_SET2` (bit 0 ladder), `$FF5A03` is the page cursor.
  - The block was chosen by a long-session never-written survey and a canary test: it survives title, options, stage start and 15k frames, and is cleared at boot.
- **Presets** (FK_SET, FK_SET2): KNIGHT `00,00`, LEGEND `E3,01`, ORIGINAL `FF,FF`.
- **Font**: page text maps ASCII onto existing VRAM tiles; see `src/menudata.inc`.
  - A-I = `$54B-$553`, K-P = `$554-$559`, R-U = `$55A-$55D`, W = `$55E`, Y = `$55F`, J = `$12C`, V = `$12D`, X = `$12E`.
  - Digits are `$562-$56D` (not contiguous); `-` = `$560`, `!` = `$561`.
  - Q and Z have no tile and are avoided in the text.
- **Not changed**: `$3AD22` was investigated as a possible second knockback. It's an enemy/scripted routine that launches Arthur by direction (vx ±`$120`/`$200`/`$100`/`$EE0`, vy `$300`), not the damage hop, so it was left unchanged.
- **Tests**:
  - `tools/t_core.py` covers knockback and mercy per setting, plus the ORIGINAL-vs-clean parity check.
  - `tools/t_menu.py` covers the page: presets, toggles, reset, wrap, flicker, exit.
  - `tools/t_play.py` is end to end: preset chosen on the page → title → 1 PLAYER → first hit. Results:

    | Preset | FK_SET | Horizontal movement in 20 frames after the hit | Blink span |
    |---|---|---|---|
    | KNIGHT | `00` | 0 px | 240 frames |
    | LEGEND | `E3` | −40 px | 120 frames |
    | ORIGINAL | `FF` | −40 px | 120 frames |

- **Savestates** are build-specific (GPGX 1.7.6: RAM at file offset 16, VRAM at 74789, both as byte-swapped words). The tools navigate from power-on instead.
