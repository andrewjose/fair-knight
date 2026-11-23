# Fair Knight GBC — changelog

Base: Ghosts'n Goblins (USA, Europe) (GB Compatible).gbc, MD5 9b846e9a4eb6b80cdbc8e6c82f2b9e9e, CRC32 AE024C23. Patches: IPS and BPS in each build folder. Source and tooling: the combined Fair Knight repo (`GBC/`).

## v0.11 — Red Arremer glitch fix, gentler camera (standard MD5 45bf9714fc82c75079a82274f30d34e3, Classic MD5 ac50e55c5a7bf97a32d30f85fbbcf7b7)
- **Player:**
  - **Red Arremer glitch fixed.** Hitting a Red Arremer made scraps of random sprites appear across the top of the screen and in the ground for a moment. This happened in every Fair Knight GBC version and with every option, including Classic and ORIGINAL; the unmodified game never does it. It's gone now.
  - **CAMERA AHEAD is easier on the eyes going backwards.** Walking left, the view now only eases back to the original centred position instead of swinging over to look ahead the other way, and it eases at half the old speed. The view follows the direction you're holding, not the way Arthur faces, so turning around to throw doesn't move the screen. Walking right still looks ahead as in v0.10.
- **Engineer:**
  - *Arremer glitch.* The game keeps its sprite animations as lists of frame numbers, each ended by an `$FF` byte. The very last list in the fixed bank (used when a Red Arremer is hit) was never given its own end byte: it ended exactly where the ROM's empty space began, and empty ROM is all `$FF`, so it worked by accident. Fair Knight's bank-0 helper code was placed starting at that byte, so the list ran on into our code and the game drew our instructions as animation frames. Fix: our code now starts one byte later, leaving that `$FF` in place. Found by reproducing it headlessly, confirming the clean ROM doesn't do it, then copying regions of the patched ROM into the clean one until the glitch appeared (it took only the first 32 bytes of the bank-0 free space).
  - *Camera.* The look-ahead target is now chosen from the held direction (Right → 54 px, Left → 80 px = the original centre, nothing held → keep the current target) instead of Arthur's facing, and moves 1 px every other frame. Walking backwards the scenery now scrolls at about 1.5× Arthur's speed for under a second, instead of 2×.
- **Technical:**
  - Bank 0 helper block moved from `.org 0:$3DF7` (was `$3DF6`). Original bytes `$3DF2-$3DF5` = `FF 2E 2F` + implicit terminator: the last animation list `2E 2F` relied on `$3DF6` = `$FF`. Bisection (clean ROM + patched ranges, stage 1 Red Arremer hit test): `$3DF6+$20` reproduces, `$3E16-$3FFF` and `$00BE+25` don't. Bank 0 free space now `$3DF7-$3FFA`, 5 bytes left (standard).
  - `h_cam`: `b` = target from `[$C0E0]` bit 4 (Right → `CAM_R` 54) / bit 5 (Left → `CAM_L` 80, was 106) / neither → current `FK_CAMT`; snap rule unchanged; easing only when `FK_CAMP` (`$DF0E`, new) is even after increment.
  - Tests: `/tmp`-style Red Arremer test (stage 1, invincible, lance at the Arremer every 10 frames, 400 frames, every frame screenshotted; detector counts frames with coloured sprite pixels in the top band): v0.10-equivalent build 29 frames of junk; clean ROM 0; v0.11 standard 0, Classic 0, ORIGINAL settings 0. Camera: walking left after right, camera moves 1-2 px per frame (Arthur 1 + easing 0.5 average); `t_camrun.py` stages 1-6 max step 2, stage 1 boss arena limit 3424 unchanged. Regression: `t_menu10`, `t_qs` (3 frames / 176 frames off), `t_hit` (knockback off / on), `t_ladder` (42 frames), `t_continue`, `t_endgame` (cross → `$C0C2` = 0) all as v0.10.

## v0.10 — quick stand and camera (standard MD5 97d8f83b8aaca6f4e5a0b97d0fa387c5, Classic MD5 23bd9459e741a63986294e20687a29b5)
- **Player:** Two new lines on the Fair Knight page, in both editions.
  - **QUICKSTAND** (ON in KNIGHT and LEGEND, OFF in ORIGINAL). On the GBC, Arthur stayed crouched as long as you held Left or Right, so letting go of Down while already pushing a direction left him stuck low until you let go of the direction too. With QUICKSTAND on he stands up the moment Down is released and walks off about 3 frames later. Down+direction still turns him while crouched and Down+B still fires crouched.
  - **CAMERA** (AHEAD in KNIGHT and LEGEND, CENTER in ORIGINAL). The GBC screen is narrow and the original camera keeps Arthur dead centre, so enemies appear very close in front of him. AHEAD keeps him about a third of the way in from the side he is walking away from, so you see roughly 26 px more of what is coming. When he turns, the view glides across (about one pixel per frame, under a second). The camera never shows anything outside the level, Arthur still reaches every edge and boss door, and stage starts, respawns and the intro scene use the original camera.
  - Fair spawns: zombies now rise at least about 3 steps from Arthur (was 2), because AHEAD brings the back edge of the screen closer to him.
  - The page title moved up one line to make room for the two rows.
- **Engineer:**
  - *Quick stand.* The crouch state checks one bit mask of held buttons (Down, B, Left, Right) to decide whether to stay down. A 16-byte routine in a free gap of the fixed bank applies the same check without Left and Right when the option is on. It is called in place of the original load-and-mask, so the original branch right after it is untouched.
  - *Camera.* Every frame the game computes Arthur's position on screen and scrolls the background by "his X minus 80", clamped by its own scroll routine to the level and to a per-section left limit. The hook replaces "minus 80" with "minus a moving target": 54 facing right, 106 facing left, moved 1 px per frame. If Arthur is more than 16 px away from the target (he is pinned against a level edge, or just respawned) the target snaps to him, so the camera never jumps. Because only the requested scroll amount changes, the game's own clamping, tile streaming and sprite positioning (sparkles included) keep working unchanged. Only the per-frame call from the gameplay loop looks ahead; the hook checks its return address so stage setup and the intro scene keep the original camera.
  - *Menu.* Settings bytes are "1 = original", so the new options use two spare bits of the second settings byte; a row's mask byte `$Fx` now means "bit x of the second byte".
- **Technical:**
  - Quick stand: 0:`$3143` `FA E0 C0 E6 B2` (`ld a,[$C0E0] / and $B2`) → `call h_qs / nop / nop`. `h_qs` at 0:`$00BE` (bank 0 `$00BE-$00FF` is 66 bytes of `$FF` before the header): `FK_SET2` bit 2 clear → `and $82`, else `and $B2`; flags feed the original `jr nz,$3155` at `$3148`.
  - Camera: 0:`$38F1` `7A D6 50 57` (`ld a,d / sub $50 / ld d,a`, in camera routine `$38B5`) → `call T_cam / nop`. `T_cam` (0:`$00CE`) → `h_cam` (bank `$20`). AHEAD only when `$38B5` was called from 0:`$058E` (return address `$0591` at `[sp+6]` inside `h_cam`); other callers (0:`$04A0` intro loop, 0:`$0537/$053A` and 5:`$4118/$411B` stage setup) get the original math and reset the target `FK_CAMT` (`$DF0D`) to `$50`. Facing = `$C5C0` bit 0. Target 54/106, step 1 px/frame, snap when |X − target| > 16. Scroll is clamped by 0:`$1A54` (right: `$C214`, left: 0 and section limit `$C241`).
  - Fair spawn: `h_zx` window ±2 → ±3 blocks.
  - Settings: `FK_SET2` bit 2 = QUICKSTAND off, bit 3 = CAMERA CENTER. Presets `pre_set2` = `$00` / `$03` / `$0F`. `NROWS` 12, `ROW0` 2, title row 0, `curtab` from Y `$1E`.
  - Tests (standard and Classic unless noted):
    - `t_qs.py`: Down 30 → Down+Right 10 → release Down holding Right: QUICKSTAND on walks after 3 frames; off and clean ROM stay crouched for all 300 frames. Down+Left turns while crouched and Down+B stays crouched in all three.
    - `t_cam.py` / `t_camturn.py` (stage 1): walking right Arthur sits at screen X 54-55, walking left at 105; turnaround moves the camera 2 px/frame while Arthur glides 1 px/frame (frame-by-frame log in the test output); largest camera step in any test 2 px.
    - `t_camrun.py --fly` (invincible, pinned height): stage 1 end: camera stops at 3424 (level limit) with Arthur at screen X 124 in the boss arena, the same as CENTER and the clean ROM. Stages 2-6 run with the camera 26 px ahead of CENTER, step ≤ 2 px.
    - Lag: 600 of 600 game frames in 600 emulated frames, AHEAD and CENTER.
    - `t_spkcam.py` (standard): sparkle world X (sprite X + camera) constant while the camera moves and eases (stage 2: 1088 frames at X 1596; stage 4: 3 secrets constant; the only other values are the same sparkle +256 for 3 frames at the screen edge, 8-bit sprite X wrap).
    - `t_spawn2.py`: walking stage 1 with turns, closest zombie behind Arthur 99 px (AHEAD) / 60 px (CENTER).
    - `t_menu10.py`: rows, presets (SET, SET2) = (`$6B`,`$03`) LEGEND, (`$FF`,`$0F`) ORIGINAL, (`$00`,`$00`) KNIGHT; 1 distinct frame idle over 10; 5 distinct pictures over 4 inputs × 13 frames (one per state, no in-between frames).
    - `t_orig.py` (fixed: settings are now written after the boot init, and buttons are really held): ORIGINAL vs clean, 12000 frames identical idle. With input, the game's random generator mixes in the hardware timer (`$1245` `ldh a,[$FF04]`), so any added instruction shifts enemy randomness; this also applies to v0.9 (first divergence frame 1593/1368, the same as v0.10). With that one read replaced by `ld a,0` in both ROMs (test-only), ORIGINAL matches the clean ROM frame for frame through 8000 frames idle, scripted and crouch-scripted, until the first game over, where the only difference is the CONTINUE preselect.
    - Regression (standard): knockback (`t_hit`), mercy, air control (`t_air`), ladder (`t_ladder`, 42 frames), boss cross and torch (`t_endgame`, `t_endgame2`), fair spawns (`t_spawn` 0 within 32 px) unchanged from v0.9.

## v0.9 Classic — no sparkles (MD5 4c7b991849a0e43614325f77318135eb)
- **Player:** Same game and same Fair Knight options page as v0.9, but with no new graphics: the "+" sparkle markers (including the red frog marker) are gone. SECRETS offers only MAP (KNIGHT default) and OFF (LEGEND and ORIGINAL). With MAP, the READY screen still lists "SECRETS n OF N" in the game's own font.
- **Engineer:** One source builds both editions. `build.py --classic` defines `CLASSIC`, and a small preprocessor (`.if NAME` / `.if !NAME` / `.else` / `.endif`) drops the sparkle code, its tile upload and its gameplay-loop hook before assembly. The hook site keeps the original game bytes. The standard build is unchanged (byte-identical to v0.9).
- **Technical:**
  - Classic leaves 0:`$05A6` as the original `call $389A`. `T_spk`, `h_spk`, `spk_gfx` and `g_spk` are not assembled, so VRAM tile `$6F` (`$86F0`) is never written.
  - `FK_SET2` bits 1-0 in Classic: 0 = MAP (KNIGHT, power-on 0 under the inverted-bit scheme), 3 = OFF (LEGEND, ORIGINAL). Value 1 is never set by Classic; it reads as MAP if present. Right/Left toggle 0 ↔ 3.
  - Tests (`tools/t_classic.py` plus existing tools):
    - Tile-`$6F` OAM frames in stages 1/3/4: v0.9 84/104/513; Classic MAP 0/0/0; Classic OFF 0/0/0; clean ROM 0/0/0.
    - VRAM `$86F0` stays zero in Classic and in the clean ROM.
    - READY list: MAP "SECRETS 0 OF 3"; OFF none.
    - Menu: cycles [3,0,3,0,3,0], 1 distinct frame over 8.
    - `t_orig`: ORIGINAL vs clean, 6000 frames identical, idle and scripted.
    - KNIGHT v0.9 vs Classic (MAP and OFF), 4000 frames identical.
    - The standard build MD5 equals v0.9.

## v0.9 — secrets (MD5 dfafe0ec370ea3fde899fe22c1bfce71)
- **Player:** New SECRETS line on the Fair Knight page: SPARKLES (KNIGHT default), MAP, or OFF (LEGEND and ORIGINAL).
  - **SPARKLES:** a small white-green "+" marks every hidden item you haven't found yet, at the spot where you have to jump or walk to make it appear. The one bad item (the frog curse) is marked with a red "+".
  - **SPARKLES and MAP:** the READY screen before each life shows "SECRETS n OF N" for the stage and the names of the ones you've found.
  - The GBC version has 30 hidden items (3/5/6/5/5/6), against the NES's 29 (4/5/7/4/4/5).
  - None of the GBC triggers needs a duck: they are touch zones. Duck stars are therefore never shown.
- **Engineer:** The hidden items are entries in each stage's object list. Each one is an invisible "trigger" object; when Arthur touches it, the game spawns an item somewhere nearby. We extracted all of them from the ROM into `secrets.csv` and a table compiled into the ROM. Three hooks do the work:
  - When a trigger fires, one bit is set in a 64-bit "found" set.
  - Every gameplay frame, before the game turns its sprite queue into hardware sprites, one sprite per unfound on-screen trigger is added to that queue, through the game's own sprite queue routine. Flicker, priority and the 40-sprite limit are therefore handled the game's way.
  - After the READY text is printed, the list is printed under it.

  The sparkle uses a sprite tile that is blank in every stage. We draw it there ourselves every 32 frames, one byte at a time, outside the LCD's busy mode.
- **Technical:**
  - Hooks: 0:`$05A6` (`call $389A`) → `T_spk`; 1:`$7997` (`ldh a,[$FF8B] / or $02`) → `T_sfnd`; 3E:`$4596` (`call PRINT`, READY) → `T_rdy`.
  - Found id = (param − `$79CD`)/10 (param = word at list entry +4), bitmap `$DF10-17`. The bitmap is cleared when the stage index differs from `FK_STG` `$DF0B` at READY.
  - Tile `$6F` (VRAM bank 0), OBJ palettes 7 / 6.
  - Tests (all on this build):
    - Stage 1: sparkle at OAM (68,162) for the armor trigger X 1872 Y 144, the same over 6 consecutive frames. The jump at X 1872 sets bit 2, the item appears, and the sparkle disappears.
    - READY with 2 forced finds: "SECRETS 2 OF 3 / MONEY ARMOR" in SPARKLES and MAP, nothing in OFF.
    - Stage 4: red marker on the frog trigger X 2176 in each of 70 consecutive frames.
    - Stage 3: sparkle at X 2240.
    - Page: Right cycles 0→1→3→0, Left reverses, the presets give `FK_SET2` 0/3/3, and the page shows 1 distinct frame over 8.
    - `t_orig`: 6000 frames identical, idle and scripted.
    - The v0.8 torch-win and continue tests still pass.

## v0.8 — torch kill + continue in every preset (MD5 09a4f0d5c5986d53296a38549ad1002b)
- **Player:** With ENDGAME AID on, killing the stage 6 boss with the torch now counts as a win, the same as the cross (the cross is still waiting near the boss). With the aid off, and in ORIGINAL, a torch kill still sends you back through stage 6. After a game over, the title cursor now starts on CONTINUE in every preset, ORIGINAL included.
- **Engineer:** When the boss dies, the game writes a flag that says "killed by the cross or not". A hook on that write forces "cross" when the aid is on. The continue hook no longer checks the preset. That makes it the one intended difference from the clean ROM in ORIGINAL, and it only shows after a game over.
- **Technical:** 1:`$74A3` (`79 EA C2 C0`, `ld a,c / ld [$C0C2],a`) → `call h_tkill / nop` (bank-0 handler: if `FK_SET & $40` = 0, then c = 0). `h_tcur` (0:`$0EB2`) drops the `FK_SET` check. Boss tests (`t_endgame2.py`, stage 6, boss spawned 4 blocks ahead, fire every 10 frames):
  - aid ON (`FK_SET` `$00`): torch → `$C0C2` = 0 (1349 frames); cross → 0 (605 frames)
  - aid OFF (`$40`): torch → 1 (865 frames); cross → 0
  - clean ROM: torch → 1; cross → 0

  Continue (`t_continue.py`): cursor row 3 with `FK_SET` `$00` and with `$FF`; clean ROM row 0. `t_orig.py` (power-on, no game over): idle and scripted, 6000 frames each, identical.

## v0.7 — fair spawns (MD5 1b6819bb8967f8702d05231ffe654486)
- **Player:** Zombies no longer rise right under Arthur (they always come up at least about 2 steps away).
- **Engineer:** The zombie generator picks one of three columns relative to the camera. A hook skips the spawn when that column is within 2 blocks (32 px) of Arthur, and the generator retries later. The game already caps zombies at 3 and makes rising zombies harmless.
- **Technical:** 1:`$4B06` → `h_zx`; 0:`$3335` → `h_touch`. Standing in column 1 for 6,000 frames: ORIGINAL 9 of 28 zombies at 0 px, KNIGHT 0 of 28 (nearest 144 px).

## v0.6 — continue preselected (dc27d65713cfde83205065a944af7d1a)
- **Player:** After a game over the title cursor starts on CONTINUE. Continues were already unlimited.
- **Engineer:** The title init writes cursor row 0. The hook writes 3 when the CONTINUE row exists and any option is non-original.
- **Technical:** 0:`$0EB2` → `h_tcur`. KNIGHT: row 3, START → stage 2 with 3 lives. ORIGINAL: row 0.

## v0.5 — endgame aid (68b0474299f6d3738b42e241c9882807)
- **Player:** The stage 6 boss can only be hurt by the torch or the cross, and only a cross kill lets you go on (a torch kill makes you replay stage 6). If you don't have the cross, one now lies on the floor a few steps before the boss.
- **Engineer:** A hook on the boss's spawn routine calls the game's own item spawner with the cross descriptor. It does this only when Arthur has no cross and no cross item exists.
- **Technical:** 1:`$72AB` → `h_boss`; item at boss X−48 px, Y−1. Test: KNIGHT spawns the item, pick-up, 235 frames of fire kill the boss, `$C0C2` = 0.

## v0.4 — ladder safety (5af193484c999a6633a90ab9d56d5d34)
- **Player:** Stepping off the top of a ladder gives 0.7 s of safety (Arthur flashes).
- **Technical:** 0:`$32C6` → `h_lad`; sets `$FFA6|$20`, `$CAFC`=42 unless a longer mercy is running. Stage 1 ladder (X 728): KNIGHT 42 mercy frames, ORIGINAL/clean 0.

## v0.3 — air control (52bb63973dc7442dc2d2c80aaed2a754)
- **Player:** You can steer jumps and falls; jump height doesn't change. No steering while flashing after a hit.
- **Technical:** 0:`$3201`/`$3819` → `h_air`/`h_airf`; Left/Right set speed ∓/±`$10`, no input keeps speed. Standing jump + Right: +35 px (ORIGINAL 0), peak 37 px and 42 frames both. Running jump reversed: −34 px (ORIGINAL +42).

## v0.2 — weapon drop (93459563777c5794cc205a59c13c789d)
- **Player:** Grabbing a new weapon leaves your old one on the ground about 24 px back toward the stage start, so you can go back for it.
- **Technical:** 1:`$4711` → `h_wpick`; old weapon item via `$45D0` at Arthur X−24 px, at the collected item's height. Test: dagger pick-up drops a lance at −26 px, and walking back swaps them again.

## v0.1 — options + knockback (4f54001a3435b273ffd4f65909502799)
- **Player:** FAIR KNIGHT row on OPTIONS with presets (KNIGHT/LEGEND/ORIGINAL/CUSTOM), Select = reset to preset, B/Start = back. KNOCKBACK OFF and MERCY LONG (4 s).
- **Engineer:** The page draws with the LCD off (no flicker: 8 consecutive frames identical) and redraws the title on exit.
- **Technical:** see ROM-MAP §6. Stage 1 hit: KNIGHT stays at X `$50`; ORIGINAL `$50`→`$29`, matching the clean ROM.

## Not done yet
- Fair spawns for flyers (entering from the screen edge onto Arthur).
- AIR CONTROL ASSIST.
