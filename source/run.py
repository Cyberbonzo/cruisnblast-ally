from pathlib import Path
import os,sys,subprocess,resource,signal,fcntl
from progress import Progress
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
r=Path(__file__).resolve().parents[1]
lock=(r/'game/g5/race/pmuser/ally-session.lock').open('w')
try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:raise SystemExit('Cruisn Blast is already running')
progress=Progress(r)
progress.restore()
progress.safe_backup()
cmd=['bwrap','--tmpfs','/']
for path in ['/usr','/etc','/var','/run','/tmp','/sys']:cmd+=['--ro-bind',path,path]
for target,path in [('usr/bin','/bin'),('usr/sbin','/sbin'),('usr/lib','/lib'),('usr/lib64','/lib64'),('var/home','/home')]:cmd+=['--symlink',target,path]
cmd+=['--dev-bind','/dev','/dev','--proc','/proc','--bind',str(r/'game'),'/pm','--chdir','/pm','--setenv','HOME','/pm','--setenv','DISPLAY',':1','--setenv','LD_LIBRARY_PATH',str(r/'lib')]
cmd+=['--bind',str(r/'source/private-udev-rules'),'/etc/udev/rules.d']
cmd+=['--setenv','SDL12COMPAT_OPENGL_SCALING','0','--setenv','MESA_SHADER_CACHE_DIR','/pm/g5/race/pmuser/mesa-cache','--setenv','LD_PRELOAD',str(r/'lib/ally_compat.so')]
game=['/pm/cruisn-ally.elf','-f1920x1080']
if '--debug' in sys.argv:cmd+=['gdb','-batch','-x',str(r/'source/debug.gdb'),'--args']+game
else:cmd+=game
os.environ.pop('LD_PRELOAD',None)
child=subprocess.Popen(cmd)
def stop(signum,frame):
    if child.poll() is None:child.send_signal(signum)
signal.signal(signal.SIGTERM,stop)
signal.signal(signal.SIGINT,stop)
try:
    while True:
        try:code=child.wait(timeout=5);break
        except subprocess.TimeoutExpired:progress.safe_backup()
finally:progress.safe_backup()
raise SystemExit(code)
