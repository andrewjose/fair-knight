# Fair Knight

A "fair" ROM hack of Ghosts 'n Goblins: it keeps the challenge and removes the cheap deaths. The NES version comes first, with GBC (Ghosts 'n Goblins) and Genesis (Ghouls 'n Ghosts) ports in progress.

This repo holds source and tooling only. It contains no ROMs and no built patches; you need your own clean dump.

## In plain terms

The hack adds:

- air control
- markers for secret spots
- safer ladders
- fairer weapon pickups (your old weapon drops behind you)
- an endgame aid that puts the cross just before the stage 6 boss
- unlimited continues
- an options menu to switch each feature on or off

## For software engineers

- `NES/src/*.s` are 6502 assembly patches, assembled with ca65/ld65.
- `NES/src/build.py` assembles them and writes each one into the clean ROM at a fixed site (a bank plus a CPU address). Before writing, it checks the bytes it's replacing (a short SHA-1 per "code" region), or checks that the space is free ($FF for "free" regions). It refuses to build if the input ROM's MD5 doesn't match.
- `NES/tools` are headless test scripts. `emu.py` is the emulator harness, `t_*.py` are scenario tests, and the survey and trace scripts are research tools. `mkips.py` makes the IPS patch.
- `GBC/tools` and `Genesis/tools` hold the same kind of tooling for those ports: SM83 and 68k disassemblers, tracers, and prototype builders.

## For ROM hackers

`ROM-MAP.md` (shared notes) and the per-platform `*/ROM-MAP.md` files document the RAM map, the routines hooked and the free space used. `NES/CHANGELOG.md` lists what each version changed.

```sh
python3 NES/src/build.py "Ghosts'n Goblins (USA).nes" out.nes      # add --save for the save-enabled version
python3 NES/tools/mkips.py "Ghosts'n Goblins (USA).nes" out.nes FairKnight-NES.ips
```

Builds and patches go in `E:\Projects\Ghosts n Goblins Fair Knight\builds`, not in this repo.
