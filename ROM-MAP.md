# Fair Knight — Ghosts 'n Goblins (USA) NES ROM map

Base ROM: `Ghosts'n Goblins (USA).nes`, 131,088 bytes, MD5 `80dcd911aaa221fd3de883d5128eb97c` (No-Intro, headered).
Header: NES 2.0, mapper 2 (UNROM), 8 × 16 KiB PRG, CHR-RAM, vertical mirroring.

Status tags: **confirmed** = checked at runtime (headless emulator / py65 trace); **static** = read from the disassembly, not yet runtime-checked; **likely** = strong guess, needs a check.

Session log
- 2026-11-14: first session. Tooling, core RAM map, Arthur's hit routine, knockback and mercy invincibility found; prototype 0 built and tested headless.

---

## 1. Plain-language summary

The game keeps everything about Arthur and the enemies in a set of parallel lists in memory, one slot per character; Arthur is always slot 0. When Arthur is hit, one routine in the always-loaded part of the ROM handles it: it takes his armor (or kills him), launches him into a short backward hop, and starts a mercy timer that makes him flash and ignore hits.

Prototype 0 changes two things in that routine:
- The backward part of the hop is removed, so Arthur hops straight up and lands where he was hit. He can no longer be knocked into a pit.
- The mercy timer counts to 60 instead of 30 (about 3.6 seconds instead of 1.8).

Both are confirmed in the emulator: same hit, same zombie, Arthur stays in place, and the flashing lasts twice as long.

## 2. For software engineers (no game-dev background)

**Memory.** The NES has 2 KB of RAM (`$0000-$07FF`). This game stores objects as *structure of arrays*: each property (X, Y, flags, timers) is its own 22-byte array, and an object is an index into all of them. Arthur is index 0, so `$05AF` is "X of object 0", `$05B0` is X of object 1, and so on.

**Code layout.** The cartridge has eight 16 KB banks. The last one (bank 7) is always mapped at `$C000-$FFFF`; any one of the other seven can be swapped into `$8000-$BFFF` by writing to the ROM area. Arthur's core logic (hit handling, movement helpers, status-flag helpers) lives in bank 7, which makes it easy to patch: hooks there are always reachable.

**Threads.** The game runs a small cooperative scheduler. Each object runs as a coroutine with its own stack and yields once per tick (`JSR $DB90` → yield). That's why the hit routine reads like a straight-line script ("hop up 6 steps, then fall until landing") rather than a per-frame state machine. The game logic runs once every 2 video frames (`$CD = 2`), and each object's coroutine runs roughly every 3 frames.

**Status flags.** Arthur's state is a bit field at `$04F0`. Helper functions set, clear and test single bits (`$F2EB-$F34x`), like tiny getters and setters.

**How things were found.** Run the ROM headlessly, record all 2 KB of RAM every frame under scripted input (idle / hold Right / hold Left / jump), and look for bytes that change the way a known quantity should. Then rerun the same frames on a second, Python-based 6502 emulator that logs every memory write with the instruction address that made it. That points straight at the code responsible.

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

## 5. Next

1. Weapon ID and the pickup routine (for WEAPON DROP): record a run that picks up the stage 1 dagger/torch, find the weapon byte, trace its write.
2. Confirm the timer digits, lives, stage/checkpoint bytes.
3. Free-space survey of bank 7 and RAM (for the options bitfield).
4. Object spawn routine (FAIR SPAWNS).
5. Convert the prototype NOPs into option-gated hooks once the settings byte exists.
