#!/bin/sh
# package.sh VERSION  -> ${OUT:-./out}/genVERSION/ (ROM, IPS, BPS, MD5SUMS, src, tools, docs)
set -e
V=$1; G=$(cd "$(dirname "$0")/.." && pwd); O=${OUT:-./out}/gen$V
rm -rf "$O"; mkdir -p "$O/src" "$O/tools"
python3 "$G/tools/mkpatch.py" "$G/gng.md" "$G/out/fk.md" "$O/FairKnight-Genesis-v$V"
cp "$G/out/fk.md" "$O/Ghouls 'n Ghosts (USA, Europe) [Fair Knight Genesis v$V].md"
cp "$G"/src/*.py "$G"/src/*.s "$G"/src/*.inc "$O/src/"
cp "$G"/tools/*.py "$G"/tools/*.sh "$G"/lr.py "$G"/util.py "$G"/gtrace2.py "$G"/tools_ramsurvey.py "$O/tools/"
cp "$G/CHANGELOG.md" "$G/ROM-MAP.md" "$O/"
cd "$O" && md5sum *.md *.ips *.bps > MD5SUMS.txt && cat MD5SUMS.txt
