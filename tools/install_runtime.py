from pathlib import Path
import tarfile,io,subprocess,shutil,json,hashlib
import sys
r=Path(sys.argv[1]).resolve();dst=r/'lib';dst.mkdir(exist_ok=True)
sdk=r/'source/PhysX-2.8.1-original.tar.gz'
with tarfile.open(sdk) as outer:
    for pkg in ['libphysx-2.8.1_4_i386.deb','libphysx-common_2.8.1-4_i386.deb']:
        data=outer.extractfile(pkg).read();deb=r/'source'/pkg;deb.write_bytes(data)
        inner=subprocess.check_output(['ar','p',str(deb),'data.tar.gz'])
        with tarfile.open(fileobj=io.BytesIO(inner),mode='r:gz') as files:
            for entry in files:
                if entry.isfile() and ('.so' in entry.name or 'copyright' in entry.name.lower()):
                    path=dst/Path(entry.name).name
                    path.write_bytes(files.extractfile(entry).read());print('Extracted',entry.name,flush=True)
            for entry in files.getmembers():
                if entry.issym() and '.so' in entry.name:
                    link=dst/Path(entry.name).name;target=Path(entry.linkname).name
                    if not link.exists():link.symlink_to(target)
steam=Path.home()/'.local/share/Steam/steamapps/common/SteamLinuxRuntime/steam-runtime/usr/lib/i386-linux-gnu'
for name in ['libglut.so.3','libSDL-1.2.so.0','libSDL2-2.0.so.0','libGLU.so.1']:
    target=steam/name
    assert target.is_file(),target
    link=dst/name
    if not link.exists():link.symlink_to(target)
print('Local dependencies ready. No system package installed.')

for name in ["libfmod.so.7","libfmodstudio.so.7"]:
    source=next((r/"game/utils").rglob(name))
    shutil.copy2(source,dst/name)
