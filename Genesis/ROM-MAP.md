# Fair Knight — Ghouls 'n Ghosts (Genesis / Mega Drive) ROM map

Base ROM: `Ghouls 'n Ghosts (USA, Europe).md`, 640 KiB, MD5 `c61ff4bcdf10813c74f36ab57e29f646`.
Header: domestic name `DAI MAKAIMURA`, serial `GM 00004013-02`, checksum `$EBEE` (valid; the build script recomputes it), ROM `$000000-$09FFFF`, RAM `$FF0000-$FFFFFF`.
The `-02` serial suffix suggests a later revision; this MD5 is the reference for every patch either way.

Status tags: **confirmed** = checked at runtime (Genesis Plus GX + the Musashi replay tracer); **static** = from the disassembly only.

Session log
- 2026-11-15: first session. Tooling, Arthur's record, hit routine, knockback table and mercy timer found; prototype 0 built and tested.

---

## 1. Plain-language summary

Ghouls 'n Ghosts is the sequel, so the code is unrelated to the NES game, but the fairness problem is the same: a hit throws Arthur backward about 80 pixels, more than in the NES game. The backward speed comes from a small four-number table that the hit routine reads (sideways speed, upward speed, gravity, sideways slow-down). The invincibility after a hit is a single "120 frames" number.

Prototype 0 (`FairKnight-Genesis-proto0.ips`):
- Sideways speed in that table set to 0, so Arthur hops up in place.
- Mercy invincibility 120 → 240 frames (2 → 4 seconds).

Confirmed in the emulator: same hit in stage 1; original, Arthur slides 80 px left; prototype, his X never changes. Flashing ends at frame 515 instead of 395.

## 2. For software engineers

**Memory.** 64 KB of RAM at `$FF0000`. The game keeps a base pointer in register A5 = `$FF8000` and reaches most globals as `offset(A5)`. Characters are large records; Arthur's starts at `$FFB200`, and a pointer to it lives at `$FFB2CE`.

**Fixed-point physics.** Positions are 16.16 (X at `+$00`, Y at `+$04`, and Y counts up). Velocities are 8.8 words (`+$14` X, `+$16` Y). Walking right is `$01B3` ≈ 1.7 px/frame; the knockback was `$0200` = 2 px/frame for 40 frames.

**Continuations instead of states.** Arthur's current behaviour is a code address stored at `$3338(A5)`. Each frame the game jumps to it, and the routine replaces it to move to the next phase (hit → hop → land → mercy → normal).

**How it was found.** RAM diffs from a headless Genesis Plus GX (driven through its libretro interface from Python) located Arthur's record. Then a second 68000 emulator (Musashi via `machine68k`) loaded the same moment from the GPGX savestate (registers found by searching the state for A5 = `$FF8000`) and replayed frames while logging every RAM write with its instruction address. It reproduces GPGX's RAM exactly over 2 frames, apart from 4 bytes of stack junk.

## 3. Deep technical reference

### 3.1 RAM

| Address | Meaning | Status |
|---|---|---|
| A5 = `$FF8000` | Global base (set at `$1F00` / `$64A4` is `$FF0000` for boot; gameplay uses `$FF8000`) | confirmed (savestate registers) |
| `$FFB200` | Arthur record (pointer at `$FFB2CE`) | confirmed |
| `+$00.l` | X, 16.16 (stage 1 start `$00C0`) | confirmed |
| `+$04.l` | Y, 16.16, up is positive (ground `$0046`) | confirmed |
| `+$09.b` | Flags; bit 6 = facing | static |
| `+$0C.w` | Sprite attributes; bit 15 toggled for mercy flicker | confirmed |
| `+$14.w` | X velocity 8.8 | confirmed |
| `+$16.w` | Y velocity 8.8 | confirmed |
| `+$18.w` | Gravity | static |
| `+$1A.w` | X acceleration | static |
| `+$24.l` | Animation pointer | static |
| `$3318(A5)` = `$FFB318.w` | Mercy timer (frames) | confirmed |
| `$3322(A5)` | Flicker phase counter | confirmed |
| `$3326(A5)` | Saved sprite attributes during flicker | static |
| `$3338(A5)` | Arthur behaviour continuation (code address) | confirmed |
| `$334C(A5)` | Return continuation for sub-behaviours | static |

### 3.2 Code

| Address | What | Status |
|---|---|---|
| `$1DB2` | Main loop wait (CPU parked here at frame boundaries) | confirmed |
| `$8B98-$8C5A` | **Hit handler**: clears counters, loads `+$14/$16/$18/$1A` from the table at **`$8C58`**, sets animation, negates X velocity/accel when facing right (bit 6 of `+$09`) | confirmed |
| `$8C58` | Hit hop table: `0200 0440 FFC8 0000` (vx, vy, gravity, ax) | confirmed |
| `$8AD0-$8B38` | Hop physics per frame (vx += ax with sign clamp, vy += gravity with terminal clamp) | static |
| `$8CA4-$8D42` | Landing → mercy: **`move.w #120,$3318(a5)` at `$8CBC`**, then per frame `subq #1`, flicker by toggling `+$0C` bit 15 every 2 frames; at 0 continue at `$84EE` | confirmed |
| `$124B6` / `$12468` | Generic X/Y integration | confirmed |
| `$3AD22` | A different hop table (other branch values ±`$120`/`$200`/`$100`/`$EE0`), **not** the normal-hit knockback; probably a special case (e.g. a hit while on a slope or a specific enemy). Untouched for now | static |

### 3.3 Prototype 0

| File offset | Original | New | Effect |
|---|---|---|---|
| `0x8C58` | `02 00` | `00 00` | hit hop X velocity 0 |
| `0x8CBE` | `00 78` | `00 F0` | mercy 120 → 240 frames |
| `0x18E` | `EB EE` | recomputed | header checksum |

Patched MD5: `25e797699aef9689258a14c4b6341701`.

## 4. Tooling (rebuild steps)

```
apt-get install -y binutils-m68k-linux-gnu libretro-genesisplusgx
pip install --break-system-packages machine68k pillow numpy
```
- `lr.py` — minimal ctypes libretro frontend for `genesis_plus_gx_libretro.so`: `run(n,'RIGHT+A')`, `ram()` (68k byte order), `poke`, `save()`/`load()`, `shot()`. RetroPad A = jump, B = attack. One core per process.
- `gtrace.py` — Musashi replay from a GPGX 1.7.6 savestate (registers at state offset 144404: D0-D7, A0-A7, PC, SR as little-endian u32). VDP/IO reads are stubbed; VBlank (level 6) is injected each frame. `run(mc, frames, watch=[(lo,hi)])` returns `(frame, pc, addr, width, value)` for RAM writes.
- `dis68.sh START END` — `m68k-linux-gnu-objdump` over the ROM.
- `build/build_proto.py` — byte-asserted patcher + checksum fix.
- States: `st_play.bin` (stage 1, control just given), `st_hit.bin` (3 frames before the first hit when idle), `st_land.bin`.

## 5. Next

- Check what triggers the `$3AD22` hop and whether it also needs neutralising.
- The game already has an OPTION screen (difficulty Practice/Professional etc.): map it, then add Fair Knight rows there.
- Weapon variable and pickup, spawn routine, the armor/gold-armor system, timer, magic.
- Free space: the cart is 640 KiB; expanding to 1 MiB gives plenty of room. Save build: SRAM header block at `$1B0`.
