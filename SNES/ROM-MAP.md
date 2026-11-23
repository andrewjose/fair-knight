# Fair Knight SNES — ROM/RAM map (Enhanced Arthur v1.2 base)

Base `ea.sfc` MD5 3ca29fc2defbf638aeb0ea38036b7215: 2 MiB LoROM, SlowROM (map mode $20), SRAM 8 KB (cart $02, size $03).
Addresses are SNES (LoROM: file = (bank & $7F) * $8000 + (addr & $7FFF)). Findings are confirmed at runtime unless marked static.

## Free space
- Banks `$20-$3D` all zero (padding). Fair Knight uses bank `$38`. `$3E/$3F` are used by the base.
- SRAM `$70:1100-1FFF` unused by the base (base ends at `$70:10E2`). Fair Knight uses `$70:1F00-1F0D`.

## Code
| Address | What |
|---|---|
| `00:8B08` | BRK (object yield) handler; saves P/PC/PB to object DP `$02-$05`, JML `$02:827A` scheduler |
| `00:82CD` | NMI: `$02D5`/`$02D6` → `$212C`/`$212D` |
| `01:842A` | string-list printer (Y = list, DB set to 4); list = [count+flags][dest word][tile,attr]... 00 |
| `01:8848` | load hop/jump velocity set Y into DP `$16-$1C` |
| `01:D7CE-D7F7` | Arthur hit: velocity (D7ED), state 9 (D7F5) |
| `01:D878-D89B` | hit hop loop; on landing mercy `$2E`=`$7E` (D88C), back to normal (JMP CE4C) |
| `03:B92C-B975` | OPTION MODE object loop (rows via table `$B978`: B982, B9B1, B9B1, B9E0, BA08) |
| `03:BA08` | OPTION MODE EXIT row: L held + START → `$1FB4` (secret menu), `$1FB3` exit |
| `03:EA26` | boot: settings load `03:FE52`, then `$0CF2C5` |
| `03:FE52` / `03:FEE7` | base settings load / save (SRAM layout in CHANGELOG) |
| `04:96C8` | continue: BCD `$0290` -= 1 |
| `0C:F26A` / `0C:F246` | leaderboard board type from settings mask `$7EF329` → `$7EAF90` (0 CLEAN 1 MINIMAL 2 ENHANCED 3 OTHER) |
| `04:9756` | draw OPTION MODE labels (X = list index; pointer table `$00:DA9E`) |

## RAM
| Address | What |
|---|---|
| `$02A4` | lives |
| `$0290` | continue credits (BCD, 5 at start) |
| `$02BB` / `$02BC` | joypad new presses (low / high byte) |
| `$02D5` | main-screen layers shadow |
| `$0323` | text-buffer upload request (INC) |
| `$043C` | Arthur object DP: `$044A` armor, `$045B` X px, `$045E` Y, `$046A` mercy timer, `$0478` state (9 = hit) |
| `$091E` | OPTION MODE cursor (0-4) |
| `$1FB3` / `$1FB4` | OPTION MODE exit / secret flags |
| `$1FF0-$1FF6`, `$1FFA`, `$1FFC` | base secret settings (see CHANGELOG) |
| `$7F:9000` | text layer buffer (32 × 32 words) |
