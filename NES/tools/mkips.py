import sys
a=open(sys.argv[1],'rb').read(); b=open(sys.argv[2],'rb').read(); out=open(sys.argv[3],'wb')
out.write(b'PATCH'); i=0
while i<len(b):
    if i<len(a) and a[i]==b[i]: i+=1; continue
    j=i
    while j<len(b) and (j>=len(a) or a[j]!=b[j]) and j-i<0xFFFF: j+=1
    if i==0x454F46: i-=1
    out.write(i.to_bytes(3,'big')+(j-i).to_bytes(2,'big')+b[i:j]); i=j
out.write(b'EOF')
