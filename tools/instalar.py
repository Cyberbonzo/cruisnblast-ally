#!/usr/bin/env python3
"""Importa uma cópia própria e prepara somente dependências privadas."""
from pathlib import Path
import argparse,shutil,subprocess,sys,zipfile

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip',type=Path,required=True)
    parser.add_argument('--sdk',type=Path,required=True)
    parser.add_argument('--dest',type=Path,required=True)
    a=parser.parse_args();repo=Path(__file__).resolve().parents[1];dest=a.dest.expanduser().resolve()
    if dest==repo or dest.is_relative_to(repo):raise SystemExit('Use uma pasta privada fora do checkout público.')
    if (dest/'game').exists():raise SystemExit('O destino já contém um jogo. Preserve-o e escolha uma pasta vazia.')
    if not a.zip.is_file() or not a.sdk.is_file():raise SystemExit('ZIP próprio ou SDK não encontrado.')
    for folder in ['game','source','lib','logs']:(dest/folder).mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.zip) as archive:
        for entry in archive.infolist():
            name=entry.filename.replace('\\','/')
            target=(dest/'game'/name).resolve()
            if not target.is_relative_to(dest/'game') or ':' in name:raise ValueError('Caminho inválido no ZIP')
        archive.extractall(dest/'game')
    shutil.copy2(a.sdk,dest/'source/PhysX-2.8.1-original.tar.gz')
    for source in (repo/'source').iterdir():
        if source.suffix in ('.py','.c','.h'):shutil.copy2(source,dest/'source'/source.name)
    shutil.copy2(repo/'jogar.sh',dest/'jogar.sh')
    for script in ['rebuild_elf.py','fix_shaders.py','prepare_state.py','install_runtime.py']:
        subprocess.run([sys.executable,str(repo/'tools'/script),str(dest)],check=True)
    subprocess.run(['gcc','-m32','-shared','-fPIC','-nostdlib','-O2','-Wall','-o',str(dest/'lib/ally_compat.so'),str(dest/'source/cruisn_compat.c')],check=True)
    (dest/'jogar.sh').chmod(0o755);(dest/'game/cruisn-ally.elf').chmod(0o755)
    print('Preparado:',dest/'jogar.sh')

if __name__=='__main__':main()
