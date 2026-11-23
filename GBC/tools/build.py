#!/usr/bin/env python3
"""Build Fair Knight GBC:  build.py CLEAN.gbc OUT.gbc [--classic]
--classic builds the Classic edition (CLASSIC = 1): no in-stage sparkle markers, no new tile,
SECRETS row OFF/MAP only. Source lines between `.if NAME` / `.if !NAME` / `.else` / `.endif`
are kept or dropped by the preprocessor below before assembly.
Assembles src/fk.asm, checks every hook site against the original bytes (SITES) and that
every other chunk lands on $FF free space, writes the ROM and fixes the global checksum."""
import sys, os, re, hashlib
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
from sm83asm import Asm, file_off
CLEAN_MD5 = '9b846e9a4eb6b80cdbc8e6c82f2b9e9e'
SITES = {  # (bank, addr): original bytes at a hook site (must match before patching)
    (0, 0x016C): 'cdc405',          # boot: call $05C4
    (0x3E, 0x4A43): '3ce601',       # options Down: inc a / and $01
    (0x3E, 0x4A4D): '3de601',       # options Up:   dec a / and $01
    (0x3E, 0x4A1F): 'fae9c1',       # options A/Start: ld a,[$C1E9]
    (0x3E, 0x4A13): '21544a',       # options cursor table: ld hl,$4A54
    (0x3E, 0x42B5): 'cd4108',       # options labels: call $0841 (SOUNDFX)
    (0, 0x3387): '3ef0eac1c5',      # armor-loss hit: knockback speed
    (0, 0x33A6): '3ef0eac1c5',      # death hit: knockback speed
    (0, 0x35CD): 'cd2537',          # hit hop: horizontal motion
    (0, 0x3375): '3e78eafcca',      # armor-loss hit: mercy frames
    (0, 0x3201): 'fae0c0',         # jump state: ld a,[$C0E0]
    (0, 0x3819): 'fae0c0',         # fall state: ld a,[$C0E0]
    (0, 0x32C6): '3e01e0a5',       # ladder exit to standing
    (1, 0x72AB): '21d274',         # stage 6 boss spawner: ld hl,$74D2
    (0, 0x0EB2): 'eae9c1',         # title init: cursor row 0
    (1, 0x4B06): 'fab8c0',         # zombie generator: ld a,[$C0B8]
    (0, 0x3335): 'f08afe36',       # enemy touch: ldh a,[$FF8A] / cp $36
    (1, 0x4711): 'f0a9c3e706',      # weapon item collected: ldh a,[$FFA9] / jp $06E7
    (1, 0x74A3): '79eac2c0',    # stage 6 boss killed: ld a,c / ld [$C0C2],a
    (0, 0x05A6): 'cd9a38',      # gameplay loop: call $389A
    (1, 0x7997): 'f08bf602',    # hidden-item trigger: ldh a,[$FF8B] / or $02
    (0x3E, 0x4596): 'cd4108',   # READY screen: call PRINT
    (0, 0x3143): 'fae0c0e6b2',  # v0.10 crouch state: ld a,[$C0E0] / and $B2
    (0, 0x38F1): '7ad65057',    # v0.10 camera follow: ld a,d / sub $50 / ld d,a
}
def preprocess(text, defs):
    out, stack = [], []          # stack of (parent_active, this_branch_active)
    active = True
    for no, line in enumerate(text.splitlines(), 1):
        t = line.split(';', 1)[0].strip()
        m = re.match(r'^\.if\s+(!?)(\w+)$', t)
        if m:
            cond = bool(defs.get(m.group(2))) != (m.group(1) == '!')
            stack.append((active, cond)); active = active and cond
            out.append(''); continue
        if t == '.else':
            assert stack, f'.else without .if at line {no}'
            parent, cond = stack[-1]; stack[-1] = (parent, not cond); active = parent and not cond
            out.append(''); continue
        if t == '.endif':
            assert stack, f'.endif without .if at line {no}'
            active = stack.pop()[0]; out.append(''); continue
        out.append(line if active else '')
    assert not stack, 'unterminated .if'
    return '\n'.join(out)
def build(src_rom, out_rom, asm_files, defs=None):
    d = bytearray(open(src_rom, 'rb').read())
    assert hashlib.md5(d).hexdigest() == CLEAN_MD5, 'not the clean Ghosts n Goblins (USA, Europe) GBC ROM'
    a = Asm()
    text = preprocess('\n'.join(open(f).read() for f in asm_files), defs or {})
    a.assemble(text, 'src')
    used = []
    for bank, addr, data in a.chunks:
        o = file_off(bank, addr)
        if (bank, addr) in SITES:
            ob = bytes.fromhex(SITES[(bank, addr)])
            assert len(data) <= len(ob), f'hook at {bank:02X}:{addr:04X} too long ({len(data)} > {len(ob)})'
            assert d[o:o + len(ob)] == ob, f'site {bank:02X}:{addr:04X} has {d[o:o+len(ob)].hex()}'
        else:
            assert all(x == 0xFF for x in d[o:o + len(data)]), f'chunk {bank:02X}:{addr:04X}+{len(data)} is not free space'
            bank_end = 0x4000 if addr < 0x4000 else 0x7FFF   # keep $7FFF (bank number) intact
            assert addr + len(data) <= bank_end, f'chunk {bank:02X}:{addr:04X} overflows its bank'
            used.append((bank, addr, len(data)))
        d[o:o + len(data)] = data
    s = (sum(d) - d[0x14E] - d[0x14F]) & 0xFFFF
    d[0x14E], d[0x14F] = s >> 8, s & 0xFF
    open(out_rom, 'wb').write(d)
    for b, ad, n in used: print(f'  code/data {b:02X}:{ad:04X} {n} bytes')
    print(out_rom, hashlib.md5(d).hexdigest())
    return a
if __name__ == '__main__':
    root = os.path.dirname(here)
    args = [x for x in sys.argv[1:] if not x.startswith('--')]
    defs = {'CLASSIC': 1} if '--classic' in sys.argv else {}
    build(args[0], args[1], [os.path.join(root, 'src', 'fk.asm')], defs)
