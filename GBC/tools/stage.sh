#!/bin/sh
# stage.sh VER "main change" ROM  -> ${OUT:-./out}/rel/<folder>/ (ROM, IPS, BPS, MD5SUMS) + src/tools copy
set -e
cd "$(dirname "$0")/.."
D="Fair Knight GBC v$1 - $2"; O=${OUT:-./out}/rel/$D; mkdir -p "$O"
cp "$3" "$O/Ghosts'n Goblins (GBC) [Fair Knight v$1].gbc"
python3 tools/mkpatch.py tools/gng.gbc "$3" "$O/Fair Knight GBC v$1" >/dev/null
(cd "$O" && md5sum *.gbc *.ips *.bps > MD5SUMS.txt && echo "Source ROM: Ghosts'n Goblins (USA, Europe) (GB Compatible).gbc  MD5 9b846e9a4eb6b80cdbc8e6c82f2b9e9e  CRC32 AE024C23" >> MD5SUMS.txt)
mkdir -p ${OUT:-./out}/gbcsrc; cp src/fk.asm tools/*.py tools/*.sh ${OUT:-./out}/gbcsrc/ 2>/dev/null || true
echo "$O"; cat "$O/MD5SUMS.txt"
