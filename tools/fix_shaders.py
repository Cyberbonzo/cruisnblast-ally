"""Apply local GLSL compatibility transformation; game assets are not included."""
from pathlib import Path
import sys, shutil
root=Path(sys.argv[1])
p=root/'game/g5/shaders/include/frag_bloom.gls'
backup=root/'source/original-shaders/include/frag_bloom.gls'
backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists():shutil.copy2(p,backup)
data=backup.read_bytes()
assert data.count(b'out vec4 out_Bloom;')==1
p.write_bytes(data)
# GLSL 1.30 forbids mixing user outputs with gl_FragData, even when the
# mixed output comes from an unused function. Use an isolated include for
# legacy shaders; modern shaders keep their original output bindings.
legacy=p.with_name('frag_bloom_ally.gls')
legacy.write_bytes(data.replace(b'out vec4 out_Bloom;',b'#define out_Bloom gl_FragData[1]'))
changed=[]
shader_root=root/'game/g5/shaders'
for desc in shader_root.glob('*.shader'):
    contents=desc.read_bytes()
    if b'include/frag_bloom.gls' not in contents:continue
    fragments=[line.split(b':',1)[1].strip().decode() for line in contents.splitlines() if line.startswith(b'FragShader:')]
    if not any(b'gl_FragData' in (shader_root/f).read_bytes() for f in fragments):continue
    saved=root/'source/original-shaders'/desc.name
    if not saved.exists():shutil.copy2(desc,saved)
    desc.write_bytes(contents.replace(b'include/frag_bloom.gls',b'include/frag_bloom_ally.gls'))
    changed.append(desc.name)
print('Updated legacy bloom includes:',changed)
# Normalize all explicit color outputs to the existing framebuffer indices.
# This also covers shared sources containing conditional legacy branches.
for fragment in shader_root.rglob('*.gls'):
    if fragment.name=='frag_bloom_ally.gls':continue
    data=fragment.read_bytes()
    modified=data
    for name,index in [('out_Color',0),('out_Color0',0),('out_Color1',1),('out_Bloom',1)]:
        modified=modified.replace(('out vec4 '+name+';').encode(),('#define '+name+' gl_FragData['+str(index)+']').encode())
    if modified!=data:
        saved=root/'source/original-shaders'/fragment.relative_to(shader_root)
        saved.parent.mkdir(parents=True,exist_ok=True)
        if not saved.exists():shutil.copy2(fragment,saved)
        fragment.write_bytes(modified)
