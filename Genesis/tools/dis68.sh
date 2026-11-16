#!/bin/sh
# dis68.sh START END  (file offsets = 68k addresses for this cart)
m68k-linux-gnu-objdump -D -b binary -m m68k:68000 --start-address=$1 --stop-address=$2 gng.md | tail -n +8
