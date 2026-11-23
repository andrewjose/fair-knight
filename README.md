# Fair Knight

A "fair" ROM hack of Ghosts 'n Goblins and its sequels: it keeps the challenge and removes the cheap deaths. It started on the NES and now has ports for the Game Boy Color (Ghosts 'n Goblins), Genesis / Mega Drive (Ghouls 'n Ghosts) and SNES (Super Ghouls 'n Ghosts).

This repo holds source and tooling only. It contains no ROMs, no game data and no built patches. Patches are published as GitHub release assets; you need your own clean dump to apply them.

## Status

All versions are **alpha**: tested headlessly in emulators, not yet on hardware.

| Platform | Version | What it changes | Base ROM (apply the patch to this) |
|---|---|---|---|
| NES | v0.5.3 (+ Classic) | Options menu with KNIGHT / LEGEND / ORIGINAL presets; no knockback, longer mercy time, weapon drop, air control, ladder safety, fair spawns, endgame aid (cross waits before the stage 6 boss), secret markers (READY-screen list, plus in-stage sparkles in the standard edition), CONTINUE preselected | `Ghosts'n Goblins (USA).nes` (iNES header), CRC32 `102A8B76`, MD5 `80dcd911aaa221fd3de883d5128eb97c` |
| GBC | v0.11 (+ Classic) | Fair Knight options page; knockback off, long mercy, weapon drop, air control, ladder safety, endgame aid, continue preselected, fair spawns, torch kill, secret markers, quick stand, look-ahead camera | `Ghosts'n Goblins (USA, Europe) (GB Compatible).gbc`, CRC32 `AE024C23`, MD5 `9b846e9a4eb6b80cdbc8e6c82f2b9e9e` |
| Genesis | v0.5 (+ Classic, identical) | Fair Knight options page (C on the OPTION screen); knockback off, long mercy, weapon drop, air control, ladder safety | `Ghouls 'n Ghosts (USA, Europe).md`, CRC32 `4F2561D5`, MD5 `c61ff4bcdf10813c74f36ab57e29f646` |
| SNES | v0.2 (+ Classic) | Fair Knight options page (X on OPTION MODE), knockback off, unlimited continues, Enhanced Arthur settings exposed as presets, saved in SRAM; leaderboard files knockback-off runs as OTHER | `Super Ghouls n Ghosts (Enhanced Arthur v1.2).sfc`, CRC32 `BA05AFB5`, MD5 `3ca29fc2defbf638aeb0ea38036b7215` |

**Classic** editions play the same but add no sparkles or other new markers inside the stages (secrets show only as the READY-screen list, or not at all). On Genesis there are no sparkles yet, so Classic is byte-identical to the standard build.

**SNES credit:** the SNES port is built on *Super Ghouls 'N Ghosts — Enhanced Arthur v1.2* by GoodLuckTrying (with work by FredYeye and Funghi, thanks to Zarby89). All of Enhanced Arthur's features are theirs. This repo contains only Fair Knight's own code; get Enhanced Arthur from its author's release and apply it to `Super Ghouls'n Ghosts (USA).sfc` (headerless, CRC32 `6AABA901`, MD5 `19b2d7a555ecef4c453a819e67e61574`) first.

Per-version details, test results and patched-ROM MD5s are in each platform's `CHANGELOG.md`.

## In plain terms

Ghosts 'n Goblins is famous for being hard, but a lot of that difficulty is unfair: hits knock you backwards into pits, enemies appear on top of you, picking up a bad weapon by accident ruins a run, and reaching the final boss without the cross sends you back a stage or two. Fair Knight fixes those things and leaves the rest alone:

- getting hit no longer throws you backwards, and you are safe for longer afterwards
- you can steer in the air
- picking up a weapon drops your old one behind you, so you can take it back
- the top of a ladder is safe for a moment
- enemies can't spawn right on top of you
- the cross you need for the final boss waits for you just before it
- hidden treasure can be marked (a list on the READY screen, and sparkles in the standard edition)
- unlimited continues, with CONTINUE already selected
- an options menu turns each change on or off; ORIGINAL plays exactly like the unmodified game

## For software engineers

Each platform folder has the same layout: `src/` (assembly patches), `tools/` (builder, patch maker, headless test scripts), `CHANGELOG.md` and `ROM-MAP.md`.

- The patches are written in assembly for each console's CPU (6502 on NES, SM83 on GBC, 68000 on Genesis, 65816 on SNES) and assembled with ca65/ld65, GNU as, or a small in-repo SM83 assembler (`GBC/tools/sm83asm.py`).
- Each `build.py` works like a careful binary patcher: it refuses to run unless the input ROM's MD5 matches, checks the original bytes (or a short hash) at every site it overwrites, and checks that "free" space really is empty. Builds are reproducible from source plus your own ROM.
- A "hook" replaces a few instructions in the original code with a call into new code placed in unused ROM space, a bit like monkey-patching a compiled binary. Settings are stored as "1 = original" bits so the power-on all-zero RAM state is the default preset without extra init code.
- `--classic` is a build-time feature flag: the same source builds both editions.
- `t_*.py` are scenario tests driven by headless emulator harnesses (scripted input, RAM checks, screenshots). The ORIGINAL preset is regression-tested against the clean ROM frame by frame.

## For ROM hackers

`ROM-MAP.md` (shared notes) and the per-platform `*/ROM-MAP.md` files document the RAM map, hooked routines, sites and free space used; the changelogs have the deep-technical section for each version (exact sites, original bytes, encodings, tests, dead ends).

```sh
# NES (ca65/ld65)
python3 NES/src/build.py "Ghosts'n Goblins (USA).nes" out.nes [--classic] [--save]
# GBC
python3 GBC/tools/build.py "Ghosts'n Goblins (USA, Europe) (GB Compatible).gbc" out.gbc [--classic]
# Genesis (m68k binutils)
python3 Genesis/src/build.py "Ghouls 'n Ghosts (USA, Europe).md" out.md
# SNES (ca65/ld65), base = Enhanced Arthur v1.2
python3 SNES/tools/build.py "Super Ghouls n Ghosts (Enhanced Arthur v1.2).sfc" out.sfc [--classic]
# IPS/BPS
python3 <platform>/tools/mkpatch.py CLEAN OUT PREFIX
```

Packaging scripts (`GBC/tools/stage.sh`, `Genesis/tools/package.sh`, `SNES/tools/package.py`) write into `$OUT` (default `./out`) or the directory given.
