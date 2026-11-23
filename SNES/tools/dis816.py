"""Linear 65816 disassembler with REP/SEP tracking. usage: dis.py ROM SNESADDR COUNT [m=1] [x=1]   (LoROM)"""
import sys
OPS={}
T="""00 BRK s1;01 ORA dxi;02 COP s1;03 ORA sr;04 TSB d;05 ORA d;06 ASL d;07 ORA dil;08 PHP;09 ORA #m;0A ASL A;0B PHD;0C TSB a;0D ORA a;0E ASL a;0F ORA al
10 BPL r;11 ORA diy;12 ORA di;13 ORA sriy;14 TRB d;15 ORA dx;16 ASL dx;17 ORA dily;18 CLC;19 ORA ay;1A INC A;1B TCS;1C TRB a;1D ORA ax;1E ASL ax;1F ORA alx
20 JSR a;21 AND dxi;22 JSL al;23 AND sr;24 BIT d;25 AND d;26 ROL d;27 AND dil;28 PLP;29 AND #m;2A ROL A;2B PLD;2C BIT a;2D AND a;2E ROL a;2F AND al
30 BMI r;31 AND diy;32 AND di;33 AND sriy;34 BIT dx;35 AND dx;36 ROL dx;37 AND dily;38 SEC;39 AND ay;3A DEC A;3B TSC;3C BIT ax;3D AND ax;3E ROL ax;3F AND alx
40 RTI;41 EOR dxi;42 WDM s1;43 EOR sr;44 MVP bm;45 EOR d;46 LSR d;47 EOR dil;48 PHA;49 EOR #m;4A LSR A;4B PHK;4C JMP a;4D EOR a;4E LSR a;4F EOR al
50 BVC r;51 EOR diy;52 EOR di;53 EOR sriy;54 MVN bm;55 EOR dx;56 LSR dx;57 EOR dily;58 CLI;59 EOR ay;5A PHY;5B TCD;5C JML al;5D EOR ax;5E LSR ax;5F EOR alx
60 RTS;61 ADC dxi;62 PER rl;63 ADC sr;64 STZ d;65 ADC d;66 ROR d;67 ADC dil;68 PLA;69 ADC #m;6A ROR A;6B RTL;6C JMP ai;6D ADC a;6E ROR a;6F ADC al
70 BVS r;71 ADC diy;72 ADC di;73 ADC sriy;74 STZ dx;75 ADC dx;76 ROR dx;77 ADC dily;78 SEI;79 ADC ay;7A PLY;7B TDC;7C JMP axi;7D ADC ax;7E ROR ax;7F ADC alx
80 BRA r;81 STA dxi;82 BRL rl;83 STA sr;84 STY d;85 STA d;86 STX d;87 STA dil;88 DEY;89 BIT #m;8A TXA;8B PHB;8C STY a;8D STA a;8E STX a;8F STA al
90 BCC r;91 STA diy;92 STA di;93 STA sriy;94 STY dx;95 STA dx;96 STX dy;97 STA dily;98 TYA;99 STA ay;9A TXS;9B TXY;9C STZ a;9D STA ax;9E STZ ax;9F STA alx
A0 LDY #x;A1 LDA dxi;A2 LDX #x;A3 LDA sr;A4 LDY d;A5 LDA d;A6 LDX d;A7 LDA dil;A8 TAY;A9 LDA #m;AA TAX;AB PLB;AC LDY a;AD LDA a;AE LDX a;AF LDA al
B0 BCS r;B1 LDA diy;B2 LDA di;B3 LDA sriy;B4 LDY dx;B5 LDA dx;B6 LDX dy;B7 LDA dily;B8 CLV;B9 LDA ay;BA TSX;BB TYX;BC LDY ax;BD LDA ax;BE LDX ay;BF LDA alx
C0 CPY #x;C1 CMP dxi;C2 REP #1;C3 CMP sr;C4 CPY d;C5 CMP d;C6 DEC d;C7 CMP dil;C8 INY;C9 CMP #m;CA DEX;CB WAI;CC CPY a;CD CMP a;CE DEC a;CF CMP al
D0 BNE r;D1 CMP diy;D2 CMP di;D3 CMP sriy;D4 PEI d;D5 CMP dx;D6 DEC dx;D7 CMP dily;D8 CLD;D9 CMP ay;DA PHX;DB STP;DC JML ail;DD CMP ax;DE DEC ax;DF CMP alx
E0 CPX #x;E1 SBC dxi;E2 SEP #1;E3 SBC sr;E4 CPX d;E5 SBC d;E6 INC d;E7 SBC dil;E8 INX;E9 SBC #m;EA NOP;EB XBA;EC CPX a;ED SBC a;EE INC a;EF SBC al
F0 BEQ r;F1 SBC diy;F2 SBC di;F3 SBC sriy;F4 PEA a;F5 SBC dx;F6 INC dx;F7 SBC dily;F8 SED;F9 SBC ay;FA PLX;FB XCE;FC JSR axi;FD SBC ax;FE INC ax;FF SBC alx"""
for e in T.replace('\n',';').split(';'):
    p=e.split(); OPS[int(p[0],16)]=(p[1],p[2] if len(p)>2 else '')
SZ={'':0,'A':0,'s1':1,'dxi':1,'sr':1,'d':1,'dil':1,'a':2,'al':3,'r':1,'diy':1,'di':1,'sriy':1,'dx':1,'dily':1,'ay':2,'ax':2,'alx':3,'bm':2,'rl':2,'ai':2,'axi':2,'dy':1,'ail':2,'#1':1}
FMT={'s1':'#${:02X}','dxi':'(${:02X},X)','sr':'${:02X},S','d':'${:02X}','dil':'[${:02X}]','a':'${:04X}','al':'${:06X}','diy':'(${:02X}),Y','di':'(${:02X})','sriy':'(${:02X},S),Y','dx':'${:02X},X','dily':'[${:02X}],Y','ay':'${:04X},Y','ax':'${:04X},X','alx':'${:06X},X','dy':'${:02X},Y','ai':'(${:04X})','axi':'(${:04X},X)','ail':'[${:04X}]','#1':'#${:02X}'}
def off(a): return ((a>>16)&0x7F)*0x8000+(a&0x7FFF)
def dis(rom,a,n,m=1,x=1,out=print):
    for _ in range(n):
        o=off(a); op=rom[o]; mn,md=OPS[op]
        if md=='#m': sz=1 if m else 2
        elif md=='#x': sz=1 if x else 2
        else: sz=SZ[md]
        b=rom[o+1:o+1+sz]; v=int.from_bytes(b,'little') if sz else 0
        if md in('#m','#x'): s=('#${:02X}' if sz==1 else '#${:04X}').format(v)
        elif md=='r': s='${:04X}'.format((a+2+(v-256 if v>127 else v))&0xFFFF)
        elif md=='rl': s='${:04X}'.format((a+3+(v-65536 if v>32767 else v))&0xFFFF)
        elif md=='bm': s='${:02X},${:02X}'.format(b[1],b[0])
        elif md=='A': s='A'
        elif md=='': s=''
        else: s=FMT[md].format(v)
        if op==0xC2: m=0 if v&0x20 else m; x=0 if v&0x10 else x
        if op==0xE2: m=1 if v&0x20 else m; x=1 if v&0x10 else x
        out(f'{a>>16:02X}:{a&0xFFFF:04X}  {rom[o:o+1+sz].hex(" "):12s} {mn} {s}   m{m}x{x}')
        a=(a&0xFF0000)|((a+1+sz)&0xFFFF)
    return a
if __name__=='__main__':
    r=open(sys.argv[1],"rb").read(); a=int(sys.argv[2],16)
    dis(r,a,int(sys.argv[3]),int(sys.argv[4]) if len(sys.argv)>4 else 1,int(sys.argv[5]) if len(sys.argv)>5 else 1)
