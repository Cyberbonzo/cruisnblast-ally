/* Own compatibility layer. No original game code or assets. */
typedef unsigned int U32;
extern void *dlsym(void *,const char *);
extern int fprintf(void *,const char *,...);
extern void *stderr;
extern char *getenv(const char *);
extern void *dlopen(const char*,int);
extern int open(const char*,int,...);
extern int read(int,void*,unsigned);
extern int close(int);
extern int write(int,const void*,unsigned);
extern int fsync(int);
extern int rename(const char*,const char*);
extern void _exit(int);
extern void *signal(int,void (*)(int));
static volatile int exit_requested;
static void leave_game(int ignored){(void)ignored;exit_requested=1;}
static void *next(const char *name){return dlsym((void*)-1,name);}
static void *sdl2,*pad;
static int (*padnum)(void),(*ispad)(int),(*init)(U32);
static void *(*padopen)(int);
static const char *(*padname)(void*);
static void (*padupdate)(void);
static short (*padaxis)(void*,int);
static unsigned char (*padbutton)(void*,int);
static float steering,throttle,brake;
static int previous[512],held[512],ticks;
static unsigned last_buttons;
static int pause_requested,paused;
int ally_infinite_boost=1,ally_blast_refills,ally_cheat_valid,ally_pause_selected;
unsigned ally_player_car;
static int cheat_save_error;
static const char *cheat_file="/pm/g5/race/pmuser/ally-infinite-blast.cfg";
static void save_cheat(void){
    const char *temp="/pm/g5/race/pmuser/ally-infinite-blast.cfg.tmp";
    char data[2]={ally_infinite_boost?'1':'0','\n'};
    int fd=open(temp,0x241,0600);cheat_save_error=1;
    if(fd>=0){int ok=write(fd,data,2)==2 && fsync(fd)==0;close(fd);if(ok&&rename(temp,cheat_file)==0)cheat_save_error=0;}
    fprintf(stderr,"ALLY infinite blast %s saved=%d\n",ally_infinite_boost?"ON":"OFF",!cheat_save_error);
}
static void init_cheat(void){
    static const unsigned char expected[7]={0x83,0xab,0xa4,0x0e,0,0,1};
    ally_cheat_valid=1;
    for(int i=0;i<7;i++)if(((volatile unsigned char*)0x08213a91)[i]!=expected[i])ally_cheat_valid=0;
    char value=0;int fd=open(cheat_file,0);
    if(fd>=0){if(read(fd,&value,1)==1&&(value=='0'||value=='1'))ally_infinite_boost=value=='1';close(fd);}
    else save_cheat();
    fprintf(stderr,"ALLY blast validation=%d enabled=%d\n",ally_cheat_valid,ally_infinite_boost);
}
static void update_cheat(void){
    ally_player_car=0;
    if(!ally_cheat_valid || paused || !*(int*)0x08a9c75c)return;
    if(((unsigned char(*)(void))0x0819bb00)())return;
    unsigned car=((unsigned(*)(void))0x081ddd80)();ally_player_car=car;
    if(!car || !ally_infinite_boost)return;
    int *charges=(int*)(car+0xea4);
    if(*charges>=0 && *charges<3){*charges=3;ally_blast_refills++;}
}
static void digital(int id,int down){
    int *p=((int*(*)(int))0x08271010)(id);
    if(!p)return;
    p[1]=down&&!previous[id];p[2]=!down&&previous[id];
    held[id]=down?(held[id]+16):0;p[3]=held[id];
    previous[id]=down;
}
static float ally_gas(void){return throttle;}
static float ally_steering(void){return steering;}
static void redirect(unsigned address,void *function){
    unsigned char *p=(void*)address;
    p[0]=0xe9;*(unsigned*)(p+1)=(unsigned)function-address-5;
}
static void controls(void){
    unsigned buttons=0;
    if(!sdl2){
        sdl2=dlopen("libSDL2-2.0.so.0",2);
        if(!sdl2)return;
        init=dlsym(sdl2,"SDL_InitSubSystem");
        padnum=dlsym(sdl2,"SDL_NumJoysticks");ispad=dlsym(sdl2,"SDL_IsGameController");
        padopen=dlsym(sdl2,"SDL_GameControllerOpen");padname=dlsym(sdl2,"SDL_GameControllerName");
        padupdate=dlsym(sdl2,"SDL_GameControllerUpdate");
        padaxis=dlsym(sdl2,"SDL_GameControllerGetAxis");padbutton=dlsym(sdl2,"SDL_GameControllerGetButton");
        init(0x2000);
    }
    if(!pad && (ticks%120)==0){
        for(int i=0;i<padnum();i++)if(ispad(i)){pad=padopen(i);if(pad)break;}
        if(pad)fprintf(stderr,"ALLY controller: %s\n",padname(pad));
    }
    ticks++;padupdate();
    steering=throttle=brake=0;
    if(pad){
        steering=padaxis(pad,0)/32767.0f;
        if(steering>-.12f&&steering<.12f)steering=0;
        else steering=steering>0?(steering-.12f)/.88f:(steering+.12f)/.88f;
        throttle=padaxis(pad,5)/32767.0f;brake=padaxis(pad,4)/32767.0f;
        if(throttle<.04f)throttle=0;
        if(brake<.04f)brake=0;
        for(int b=0;b<15;b++)if(padbutton(pad,b))buttons|=1u<<b;
    }
    /* Optional short-lived input file used only by the private verifier. */
    struct {unsigned magic,buttons;float steer,gas,brake;} test;
    int fd=open("/pm/g5/race/pmuser/ally-test-input.bin",0);
    if(fd>=0){if(read(fd,&test,sizeof(test))==sizeof(test)&&test.magic==0x414c4c59){buttons=test.buttons;steering=test.steer;throttle=test.gas;brake=test.brake;}close(fd);}
    if((buttons&64)&&!(last_buttons&64))pause_requested=1;
    if(paused){
        unsigned edge=buttons&~last_buttons;
        if(edge&((1u<<11)|(1u<<12)))ally_pause_selected^=1;
        if(edge&2)pause_requested=1;
        if(edge&1){
            if(ally_pause_selected && ally_cheat_valid){ally_infinite_boost=!ally_infinite_boost;save_cheat();}
            else if(!ally_pause_selected)pause_requested=1;
        }
    }
    last_buttons=buttons;
    if(paused){buttons=0;steering=throttle=brake=0;}
    digital(0x173,!!(buttons&5)); /* A confirms, X also activates Blast */
    digital(0x177,!!(buttons&(1<<1))); /* view */
    digital(0x178,!!(buttons&(1<<3))); /* tunes */
    digital(273,throttle>.1f || (buttons&(1<<11)));
    digital(274,brake>.1f || (buttons&(1<<12)));
    digital(276,(steering<-.3f)||(buttons&(1<<13)));
    digital(275,(steering>.3f)||(buttons&(1<<14)));
    digital(13,!!(buttons&1));
    digital(27,!!(buttons&(1<<4)));
}
#include "cruisn_progress.h"
#include "cruisn_pause.h"
static void setting(const char *group,const char *key,int value){
    ((int(*)(const char*,const char*,int))0x0825d7c0)(group,key,value);
    ((int(*)(const char*,const char*))0x0825e200)(group,key);
}
void SDL_GL_SwapBuffers(void){
    static int frames,configured;
    static void (*swap)(void);
    if(!swap)swap=next("SDL_GL_SwapBuffers");
    if(!configured){
        configured=1;
        init_cheat();
        init_profile();
        signal(15,leave_game);
        setting("hardware","cabType",1);
        setting("main","firstBoot",0);
        setting("playerCost","freeplay",1);
        setting("game","metric",1);
        setting("game","difficulty",0);
        *(int*)0x09c52cec=1;
        redirect(0x08192880,ally_steering);
        redirect(0x08193720,ally_gas);
    }
    *(void**)0x09c28538=controls;
    if(frames==300)setting("game","metric",1);
    if(frames<4){
        unsigned (*error)(void)=next("glGetError");
        void (*get)(unsigned,int*)=next("glGetIntegerv");
        const char *(*str)(unsigned)=next("glGetString");
        int viewport[4]={0},fbo=0;
        get(0x0ba2,viewport);get(0x8ca6,&fbo);
        fprintf(stderr,"ALLY frame=%d GL=%s err=%x vp=%d,%d,%d,%d fbo=%d DISPLAY=%s\n",frames,str(0x1f02),error(),viewport[0],viewport[1],viewport[2],viewport[3],fbo,getenv("DISPLAY"));
    }
    update_profile();
    if(exit_requested){profile_flush();_exit(0);}
    update_cheat();frames++;swap();
    if(pause_requested){pause_requested=0;pause_screen(swap);}
}
