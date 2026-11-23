"""Make IPS and BPS patches. usage: mkpatch.py SRC TGT OUT_BASE  (writes OUT_BASE.ips and OUT_BASE.bps)"""
import sys, zlib

def ips(src, tgt):
    out = bytearray(b'PATCH'); i = 0; n = len(tgt)
    while i < n:
        if i < len(src) and src[i] == tgt[i]: i += 1; continue
        j = i
        if i + 16 <= n and tgt[i:i+16] == tgt[i:i+1] * 16:
            while j < n and j - i < 0xFFFF and tgt[j] == tgt[i] and not (j < len(src) and src[j] == tgt[j]): j += 1
        else:
            while j < n and j - i < 0xFFFF and not (j < len(src) and src[j] == tgt[j] and j + 1 < n and j + 1 < len(src) and src[j+1] == tgt[j+1]):
                j += 1
                if j + 16 <= n and tgt[j:j+16] == tgt[j:j+1] * 16: break
        if i == 0x454F46: i -= 1          # offset 'EOF' would end the patch early
        chunk = tgt[i:j]
        if len(chunk) > 8 and chunk.count(chunk[0]) == len(chunk):   # RLE
            out += i.to_bytes(3, 'big') + b'\0\0' + len(chunk).to_bytes(2, 'big') + chunk[:1]
        else:
            out += i.to_bytes(3, 'big') + len(chunk).to_bytes(2, 'big') + chunk
        i = j
    out += b'EOF'
    if len(tgt) != len(src): out += len(tgt).to_bytes(3, 'big')   # truncate/extend marker
    return bytes(out)

def num(v):
    o = bytearray()
    while True:
        x = v & 0x7F; v >>= 7
        if v == 0: o.append(0x80 | x); return o
        o.append(x); v -= 1

def bps(src, tgt):
    out = bytearray(b'BPS1') + num(len(src)) + num(len(tgt)) + num(0)
    i = 0; n = len(tgt); trel = 0
    while i < n:
        j = i
        if i < len(src) and src[i] == tgt[i]:
            while j < n and j < len(src) and src[j] == tgt[j]: j += 1
            out += num(((j - i - 1) << 2) | 0)          # SourceRead
        else:
            r = i
            while r < n and tgt[r] == tgt[i] and not (r < len(src) and src[r] == tgt[r]): r += 1
            if r - i >= 16:                                   # byte run: 1 TargetRead + TargetCopy
                out += num(0 << 2 | 1) + tgt[i:i+1]
                rel = i - trel; out += num(((r - i - 2) << 2) | 3) + num((abs(rel) << 1) | (rel < 0))
                trel = i + (r - i - 1); i = r; continue
            while j < n and not (j < len(src) and src[j] == tgt[j]):
                j += 1
                if j + 16 <= n and tgt[j:j+16] == tgt[j:j+1] * 16: break
            out += num(((j - i - 1) << 2) | 1) + tgt[i:j]  # TargetRead
        i = j
    out += zlib.crc32(src).to_bytes(4, 'little') + zlib.crc32(tgt).to_bytes(4, 'little')
    out += zlib.crc32(out).to_bytes(4, 'little')
    return bytes(out)

def apply_ips(src, p):
    t = bytearray(src); k = 5
    while p[k:k+3] != b'EOF':
        o = int.from_bytes(p[k:k+3], 'big'); l = int.from_bytes(p[k+3:k+5], 'big'); k += 5
        if l == 0:
            l = int.from_bytes(p[k:k+2], 'big'); d = p[k+2:k+3] * l; k += 3
        else:
            d = p[k:k+l]; k += l
        if len(t) < o + l: t += b'\0' * (o + l - len(t))
        t[o:o+l] = d
    k += 3
    if len(p) >= k + 3: t = t[:int.from_bytes(p[k:k+3], 'big')]
    return bytes(t)

def apply_bps(src, p):
    k = [4]
    def rd():
        d = 0; sh = 1
        while True:
            x = p[k[0]]; k[0] += 1; d += (x & 0x7F) * sh
            if x & 0x80: return d
            sh <<= 7; d += sh
    rd(); rd(); ml = rd(); k[0] += ml; o = bytearray(); tr = 0; sr = 0
    while k[0] < len(p) - 12:
        d = rd(); a = d & 3; l = (d >> 2) + 1
        if a == 0: o += src[len(o):len(o) + l]
        elif a == 1: o += p[k[0]:k[0] + l]; k[0] += l
        else:
            v = rd(); off = -(v >> 1) if v & 1 else (v >> 1)
            if a == 2:
                sr += off; o += src[sr:sr + l]; sr += l
            else:
                tr += off
                for _ in range(l): o.append(o[tr]); tr += 1
    return bytes(o)

if __name__ == '__main__':
    s = open(sys.argv[1], 'rb').read(); t = open(sys.argv[2], 'rb').read()
    a = ips(s, t); b = bps(s, t)
    assert apply_ips(s, a) == t, 'IPS self-check failed'
    assert apply_bps(s, b) == t, 'BPS self-check failed'
    open(sys.argv[3] + '.ips', 'wb').write(a); open(sys.argv[3] + '.bps', 'wb').write(b)
    print(f'ips {len(a)} bytes, bps {len(b)} bytes, self-check ok')
