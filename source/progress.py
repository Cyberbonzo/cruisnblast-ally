"""Private native saves: validate, back up atomically, restore damaged files."""
from pathlib import Path
import hashlib,json,os,struct,time,zipfile,io

PROFILE_SIZE=332
TABLE_SIZE=972008

def valid(name,data):
    if name=='ally-profile.bin':
        if len(data)!=PROFILE_SIZE:return False
        magic,expected=struct.unpack_from('<II',data)
        h=2166136261
        for b in data[8:]:h=((h^b)*16777619)&0xffffffff
        return magic==0x31504243 and h==expected and data[16:25]==b'24682468\0'
    if name=='player_tbl':
        return len(data)==TABLE_SIZE and struct.unpack_from('<IH',data)==(TABLE_SIZE,10)
    return bool(data) and len(data)<8*1024*1024

def atomic(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.tmp')
    with tmp.open('wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)
    fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)

class Progress:
    def __init__(self,root):
        self.state=Path(root)/'game/g5/race/pmuser'
        self.backups=Path(root)/'saves/backups'
        self.backups.mkdir(parents=True,exist_ok=True)
        self.digest=None

    def files(self):
        return [self.state/n for n in ('ally-profile.bin','player_tbl','ally-infinite-blast.cfg')]+sorted((self.state/'aud/save').glob('highscores.*.xml'))

    def restore(self):
        # Never roll back a valid current file, even when a backup is newer.
        for archive in sorted(self.backups.glob('*.zip'),reverse=True):
            try:
                with zipfile.ZipFile(archive) as z:
                    manifest=json.loads(z.read('manifest.json'))
                    for name,sha in manifest.items():
                        rel=Path(name)
                        if rel.is_absolute() or '..' in rel.parts:continue
                        dst=self.state/rel
                        old=dst.read_bytes() if dst.exists() else b''
                        if valid(name,old):continue
                        data=z.read(name)
                        if hashlib.sha256(data).hexdigest()!=sha or not valid(name,data):continue
                        if dst.exists():atomic(dst.with_name(dst.name+'.damaged-'+str(time.time_ns())),old)
                        atomic(dst,data)
                        print('ALLY restored save:',name,flush=True)
            except (OSError,ValueError,KeyError,zipfile.BadZipFile) as e:
                print('ALLY skipped unreadable backup:',archive.name,type(e).__name__,flush=True)

    def backup(self):
        entries={}
        for path in self.files():
            try:
                name=path.relative_to(self.state).as_posix()
                before=path.stat();data=path.read_bytes();after=path.stat()
                if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):return
                if not valid(name,data):return
                entries[name]=data
            except FileNotFoundError:continue
        if not entries:return
        hashes={name:hashlib.sha256(data).hexdigest() for name,data in entries.items()}
        digest=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
        if digest==self.digest:return
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
            for name,data in entries.items():z.writestr(name,data)
            z.writestr('manifest.json',json.dumps(hashes,sort_keys=True))
        atomic(self.backups/(str(time.time_ns())+'.zip'),out.getvalue())
        self.digest=digest
        for old in sorted(self.backups.glob('*.zip'))[:-8]:old.unlink()

    def safe_backup(self):
        try:self.backup()
        except OSError as e:print('ALLY backup failed:',e,flush=True)
