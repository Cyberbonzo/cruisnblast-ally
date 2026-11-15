from pathlib import Path
import os,sys,subprocess,resource
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
r=Path(__file__).resolve().parents[1]
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
os.execvp(cmd[0],cmd)
