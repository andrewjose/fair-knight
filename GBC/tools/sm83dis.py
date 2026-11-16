#!/usr/bin/env python3
"""Minimal SM83 (Game Boy) disassembler. usage: sm83dis.py ROM BANK HEXADDR COUNT"""
import sys
R=['b','c','d','e','h','l','[hl]','a']; RP=['bc','de','hl','sp']; RP2=['bc','de','hl','af']
CC=['nz','z','nc','c']; ALU=['add a,','adc a,','sub','sbc a,','and','xor','or','cp']
ROT=['rlc','rrc','rl','rr','sla','sra','swap','srl']
def dis(b,pc):
    op=b[0]; x,y,z,p,q=op>>6,(op>>3)&7,op&7,(op>>4)&3,(op>>3)&1
    n=lambda:b[1]; nn=lambda:b[1]|b[2]<<8
    if op==0xCB:
        o=b[1]; xx,yy,zz=o>>6,(o>>3)&7,o&7
        return 2,[f'{ROT[yy]} {R[zz]}',f'bit {yy}, {R[zz]}',f'res {yy}, {R[zz]}',f'set {yy}, {R[zz]}'][xx]
    if x==1: return (1,'halt') if op==0x76 else (1,f'ld {R[y]}, {R[z]}')
    if x==2: return 1,f'{ALU[y]} {R[z]}'
    if x==0:
        if z==0:
            if y==0: return 1,'nop'
            if y==1: return 3,f'ld [${nn():04X}], sp'
            if y==2: return 2,'stop'
            if y==3: return 2,f'jr ${(pc+2+((n()^0x80)-0x80))&0xffff:04X}'
            return 2,f'jr {CC[y-4]}, ${(pc+2+((n()^0x80)-0x80))&0xffff:04X}'
        if z==1: return (3,f'ld {RP[p]}, ${nn():04X}') if q==0 else (1,f'add hl, {RP[p]}')
        if z==2: return 1,[ 'ld [bc], a','ld [de], a','ld [hl+], a','ld [hl-], a'][p] if q==0 else ['ld a, [bc]','ld a, [de]','ld a, [hl+]','ld a, [hl-]'][p]
        if z==3: return 1,f'{"inc" if q==0 else "dec"} {RP[p]}'
        if z==4: return 1,f'inc {R[y]}'
        if z==5: return 1,f'dec {R[y]}'
        if z==6: return 2,f'ld {R[y]}, ${n():02X}'
        return 1,['rlca','rrca','rla','rra','daa','cpl','scf','ccf'][y]
    # x==3
    if z==0:
        if y<4: return 1,f'ret {CC[y]}'
        return [(2,f'ldh [$FF{n():02X}], a'),(2,f'add sp, {(n()^0x80)-0x80}'),(2,f'ldh a, [$FF{n():02X}]'),(2,f'ld hl, sp{(n()^0x80)-0x80:+}')][y-4]
    if z==1:
        if q==0: return 1,f'pop {RP2[p]}'
        return 1,['ret','reti','jp hl','ld sp, hl'][p]
    if z==2:
        if y<4: return 3,f'jp {CC[y]}, ${nn():04X}'
        return [(1,'ld [$FF00+c], a'),(3,f'ld [${nn():04X}], a'),(1,'ld a, [$FF00+c]'),(3,f'ld a, [${nn():04X}]')][y-4]
    if z==3:
        if y==0: return 3,f'jp ${nn():04X}'
        if y==6: return 1,'di'
        if y==7: return 1,'ei'
        return 1,f'db ${op:02X}'
    if z==4: return (3,f'call {CC[y]}, ${nn():04X}') if y<4 else (1,f'db ${op:02X}')
    if z==5:
        if q==0: return 1,f'push {RP2[p]}'
        return (3,f'call ${nn():04X}') if p==0 else (1,f'db ${op:02X}')
    if z==6: return 2,f'{ALU[y]} ${n():02X}'
    return 1,f'rst ${y*8:02X}'
def off(bank,a): return a if a<0x4000 else bank*0x4000+a-0x4000
def listing(rom,bank,a,cnt):
    out=[]
    for _ in range(cnt):
        o=off(bank,a); ln,t=dis(rom[o:o+3],a); out.append(f'{bank:02X}:{a:04X}  {rom[o:o+ln].hex(" "):9s} {t}'); a+=ln
    return out
if __name__=='__main__':
    rom=open(sys.argv[1],'rb').read()
    print('\n'.join(listing(rom,int(sys.argv[2],0),int(sys.argv[3],16),int(sys.argv[4]))))
