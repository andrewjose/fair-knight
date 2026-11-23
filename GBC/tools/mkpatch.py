"""mkpatch.py CLEAN OUT BASENAME -> BASENAME.ips and BASENAME.bps (simple, self-verified)."""
import sys, zlib
def ips(a, b):
    out = bytearray(b'PATCH'); i = 0
    while i < len(b):
        if a[i] == b[i]: i += 1; continue
        j = i
        while j < len(b) and a[j] != b[j] and j - i < 0xFFFF: j += 1
        if i == 0x454F46: i -= 1  # avoid 'EOF' offset
        out += i.to_bytes(3, 'big') + (j - i).to_bytes(2, 'big') + b[i:j]; i = j
    return bytes(out + b'EOF')
def num(n):
    o = bytearray()
    while True:
        x = n & 0x7F; n >>= 7
        if n == 0: o.append(0x80 | x); return o
        o.append(x); n -= 1
def bps(a, b):
    out = bytearray(b'BPS1') + num(len(a)) + num(len(b)) + num(0); i = 0
    while i < len(b):
        j = i; same = a[i] == b[i]
        while j < len(b) and (a[j] == b[j]) == same: j += 1
        out += num(((j - i - 1) << 2) | (0 if same else 1))
        if not same: out += b[i:j]
        i = j
    for x in (zlib.crc32(a), zlib.crc32(b)): out += x.to_bytes(4, 'little')
    out += zlib.crc32(out).to_bytes(4, 'little'); return bytes(out)
def apply_ips(a, p):
    a = bytearray(a); i = 5
    while p[i:i+3] != b'EOF':
        o = int.from_bytes(p[i:i+3], 'big'); n = int.from_bytes(p[i+3:i+5], 'big'); a[o:o+n] = p[i+5:i+5+n]; i += 5 + n
    return bytes(a)
if __name__ == '__main__':
    a = open(sys.argv[1], 'rb').read(); b = open(sys.argv[2], 'rb').read(); base = sys.argv[3]
    assert len(a) == len(b)
    p = ips(a, b); assert apply_ips(a, p) == b
    open(base + '.ips', 'wb').write(p); open(base + '.bps', 'wb').write(bps(a, b))
    print('ok', len(p), 'bytes IPS')
def apply_bps(a, p):
    i = 4
    def rd():
        nonlocal i; d = 0; s = 1
        while True:
            x = p[i]; i += 1; d += (x & 0x7F) * s
            if x & 0x80: return d
            s <<= 7; d += s
    rd(); tl = rd(); m = rd(); i += m; out = bytearray()
    while i < len(p) - 12:
        d = rd(); n = (d >> 2) + 1; act = d & 3
        if act == 0: out += a[len(out):len(out)+n]
        elif act == 1: out += p[i:i+n]; i += n
        else: raise ValueError
    assert len(out) == tl; return bytes(out)
