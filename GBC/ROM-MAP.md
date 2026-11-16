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
