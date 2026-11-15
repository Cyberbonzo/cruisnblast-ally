from pathlib import Path
import struct,json,re,sys
class Elf:
    def __init__(self,path):
        self.d=Path(path).read_bytes();assert self.d[:5]==b'\x7fELF\x01'
        phoff=struct.unpack_from('<I',self.d,28)[0]
        size,num=struct.unpack_from('<HH',self.d,42)
        self.ph=[struct.unpack_from('<IIIIIIII',self.d,phoff+i*size) for i in range(num)]
        dynamic=next(x for x in self.ph if x[0]==2)
        tags={}
        for o in range(dynamic[1],dynamic[1]+dynamic[4],8):
            tag,val=struct.unpack_from('<II',self.d,o)
            if tag==0:break
            tags[tag]=val
        syms=self.offset(tags[6]);strings=self.offset(tags[5]);self.symbols={}
        for o in range(syms,strings,16):
            no,value,size,info,other,section=struct.unpack_from('<IIIBBH',self.d,o)
            if no>=tags[10]:continue
            end=self.d.find(b'\0',strings+no);name=self.d[strings+no:end].decode('utf-8','replace')
            if name:self.symbols[name]={'address':value,'size':size,'section':section,'type':info&15}
    def offset(self,va):
        for kind,off,addr,_,fs,ms,flags,align in self.ph:
            if kind==1 and addr<=va<addr+fs:return off+va-addr
        raise ValueError(hex(va))
