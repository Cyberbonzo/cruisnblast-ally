"""Restore native ELF linking metadata from the local dump's import records."""
from pathlib import Path
import struct,hashlib,json
from cruisn_elf import Elf
import sys
root=Path(sys.argv[1]).resolve()
(root/'source').mkdir(exist_ok=True)
src=root/'game/game';e=Elf(src);d=bytearray(e.d)
assert hashlib.sha256(d).hexdigest()=='cdb5f6b6797ea4ca0c3f76714cf65fa2c8b6602164c5babae0a729843ef8c3c9'
dynamic=next(p for p in e.ph if p[0]==2);pairs=[]
for o in range(dynamic[1],dynamic[1]+dynamic[4],8):
    tag,val=struct.unpack_from('<II',d,o)
    if not tag:break
    pairs.append((tag,val))
tags=dict(pairs);count=struct.unpack_from('<II',d,e.offset(tags[4]))[1]
# The dump captured stale heap pointers in BSS. Native startup must zero this
# range before running the original C++ constructors; relocations follow later.
bss_start=e.symbols['__bss_start']['address'];bss_end=tags[4]
assert bss_start==0x8ac2b24 and bss_end==0xa1a8c18
d[e.offset(bss_start):e.offset(bss_end)]=bytes(bss_end-bss_start)
# Select the existing non-cabinet startup path in this private test copy.
o=e.offset(0x081ae726)
assert d[o:o+10]==bytes.fromhex('c70578d9bd0801000000')
d[o+6:o+10]=bytes(4)
# Inherit the normal user scheduler. Cabinet realtime threads fail EPERM.
o=e.offset(0x084a63f4)
assert d[o:o+8]==bytes.fromhex('c744240401000000')
d[o+4:o+8]=bytes(4)
# Use the native SDL input path, without a cabinet RIO board.
o=e.offset(0x081b29ab)
assert d[o:o+10]==bytes.fromhex('c705e8d9bd0801000000')
d[o+6:o+10]=bytes(4)
# The no-dongle startup path has no hardware version to compare.
o=e.offset(0x08185450)
assert d[o:o+3]==bytes.fromhex('83ec2c')
d[o:o+3]=bytes.fromhex('31c0c3')
# This supplied dataset already contains plaintext programs. Its original
# name-length heuristic must not send those plaintext files to a dongle.
o=e.offset(0x088eb89f)
assert d[o:o+13]==b'programs_enc\0'
d[o:o+13]=b'programs\0'+bytes(4)
strings=bytearray(d[e.offset(tags[5]):e.offset(tags[5])+tags[10]])
syms=bytearray(d[e.offset(tags[6]):e.offset(tags[6])+count*16]);indices={}
for i in range(count):
    no,val,size,info,other,section=struct.unpack_from('<IIIBBH',syms,i*16)
    name=strings[no:strings.find(0,no)].decode('utf-8','replace')
    if name:indices[name]=i
    if section==0:struct.pack_into('<I',syms,i*16+4,0)
records=[]
for off in range(0x2182970,0x2186510,24):
    no,vo,target,weak,unused,kind=struct.unpack_from('<IIIIII',e.d,off)
    pos=0x217f604+no
    name=e.d[pos:e.d.index(b'\0',pos)].decode('ascii')
    records.append({'name':name,'target':target,'a':weak,'kind':kind})
assert len(records)==636
rel={};plt={}
for t,sz,out in [(17,18,rel),(23,2,plt)]:
    begin=e.offset(tags[t])
    for o in range(begin,begin+tags[sz],8):
        target,info=struct.unpack_from('<II',d,o);out[target]=info
for rec in records:
    name=rec['name']
    if name not in indices:
        i=len(syms)//16;indices[name]=i;no=len(strings);strings+=name.encode()+b'\0'
        syms+=struct.pack('<IIIBBH',no,0,0,0x22 if rec['a'] else 0x12,0,0)
    i=indices[name];table=plt if rec['kind']==7 else rel
    table[rec['target']]=(i<<8)|rec['kind']
    # Binding is eager; clear stale snapshot pointers before relocation.
    struct.pack_into('<I',d,e.offset(rec['target']),0)

def align(v,a):return (v+a-1)//a*a
last=max((p for p in e.ph if p[0]==1),key=lambda p:p[2])
def append(data,alignment=16):
    raw=align(len(d),alignment);d.extend(bytes(raw-len(d)));d.extend(data)
    return last[2]+raw-last[1],raw
# Recognize plaintext by its actual header. Retain the original path for
# encrypted assets; unused development scripts in this dump are encrypted.
hookva,hookraw=append(bytes(43))
code=bytearray()
def jump(op,target):
    code.extend(op+struct.pack('<i',target-(hookva+len(code)+len(op)+4)))
jump(b'\x0f\x85',0x0828d091)
code+=bytes.fromhex('8b4424546681382f2f')
jump(b'\x0f\x85',0x0828d1f0)
code+=bytes.fromhex('8078020a')
jump(b'\x0f\x85',0x0828d1f0)
jump(b'\xe9',0x0828d091)
assert len(code)<=43
d[hookraw:hookraw+len(code)]=code
o=e.offset(0x0828d08b)
assert d[o:o+6]==bytes.fromhex('0f845f010000')
d[o:o+6]=b'\xe9'+struct.pack('<i',hookva-(0x0828d08b+5))+b'\x90'
strva,_=append(strings);symva,_=append(syms)
def elfhash(name):
    h=0
    for c in name:
        h=(h<<4)+c;g=h&0xf0000000
        if g:h^=g>>24
        h&=~g
    return h
buckets=[0]*4093;chains=[0]*(len(syms)//16)
for i in range(1,len(chains)):
    no=struct.unpack_from('<I',syms,i*16)[0]
    name=strings[no:strings.find(0,no)];b=elfhash(name)%len(buckets)
    chains[i]=buckets[b];buckets[b]=i
hashdata=struct.pack('<II',len(buckets),len(chains))+struct.pack('<'+'I'*(len(buckets)+len(chains)),*(buckets+chains))
hashva,_=append(hashdata)
reld=b''.join(struct.pack('<II',k,v) for k,v in rel.items());pltdata=b''.join(struct.pack('<II',k,v) for k,v in plt.items())
relva,_=append(reld);pltva,_=append(pltdata)
libcgot=next(x['target'] for x in records if x['name']=='__libc_start_main')
# Conventional i386 C runtime entry: argc/argv + dynamic-loader finalizer.
entry=bytes.fromhex('31ed5e89e183e4f0505452')
for v in [0,0x088e25d0]:entry+=b'\x68'+struct.pack('<I',v)
entry+=bytes.fromhex('5156')+b'\x68'+struct.pack('<I',0x08138730)
entry+=b'\xff\x15'+struct.pack('<I',libcgot)+b'\xf4'
entryva,_=append(entry)
updates={4:hashva,5:strva,6:symva,10:len(strings),17:relva,18:len(reld),23:pltva,2:len(pltdata)}
remove={0x6ffffffe,0x6fffffff,0x6ffffff0,0x6ffffffc,0x6ffffffd}
newpairs=[(t,updates.get(t,v)) for t,v in pairs if t not in remove]
newpairs.extend([(24,0),(0,0)])
dynbytes=b''.join(struct.pack('<II',*x) for x in newpairs);dynva,dynraw=append(dynbytes)
phoff=struct.unpack_from('<I',d,28)[0]
for i,p in enumerate(e.ph):
    if p==last:
        n=len(d)-p[1];struct.pack_into('<II',d,phoff+i*32+16,n,n)
    if p[0]==2:
        struct.pack_into('<IIIIIIII',d,phoff+i*32,2,dynraw,dynva,dynva,len(dynbytes),len(dynbytes),6,4)
struct.pack_into('<I',d,24,entryva)
target=root/'game/cruisn-ally.elf';target.write_bytes(d)
report={'original_sha256':hashlib.sha256(e.d).hexdigest(),'result_sha256':hashlib.sha256(d).hexdigest(),'imports_restored':len(records),'symbols':len(syms)//16,'entry':hex(entryva),'size':len(d),'changes':['Native ELF imports, entry and zeroed BSS','Normal user thread scheduling','SDL input instead of cabinet RIO','Offline startup without dongle version check'],'note':'Private derived executable only; no game or license files distributed.'}
(root/'source/elf-rebuild.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
