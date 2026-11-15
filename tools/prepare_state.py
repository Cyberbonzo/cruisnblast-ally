from pathlib import Path
import shutil
import sys
r=Path(sys.argv[1]).resolve()
p=r/'game/g5/race/pmuser'
if p.is_file():
    assert p.stat().st_size==0
    backup=r/'source/pmuser-original-placeholder'
    assert not backup.exists()
    p.rename(backup)
p.mkdir(exist_ok=True)
for sub in ['adj','aud','prof','coredumps']:(p/sub).mkdir(exist_ok=True)
rules=r/'source/private-udev-rules';rules.mkdir(exist_ok=True)
shutil.copy2(r/'game/utils/10-usb-automount.rules',rules/'10-usb-automount.rules')
print('Private save directory and sandbox-only rules prepared.')
