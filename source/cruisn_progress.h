/* Own single-player persistence integration for the supported Linux build. */
#define PROFILE_SIZE 324
extern int memcmp(const void*,const void*,unsigned);
extern void *memcpy(void*,const void*,unsigned);
int ally_profile_valid,ally_profile_loaded,ally_profile_saves,ally_profile_error;
static unsigned char profile_previous[PROFILE_SIZE];
static int profile_active,profile_previous_valid;
static unsigned profile_tick;
static const char *profile_pin="24682468";
static const char *profile_file="/pm/g5/race/pmuser/ally-profile.bin";
static unsigned char *profile_data=(void*)0x08ccb180;
static unsigned profile_hash(const unsigned char *p){
    unsigned hash=2166136261u;
    for(unsigned i=0;i<PROFILE_SIZE;i++)hash=(hash^p[i])*16777619u;
    return hash;
}
static int profile_read(void *data){
    struct {unsigned magic,hash;unsigned char data[PROFILE_SIZE];} record;
    int fd=open(profile_file,0),ok=0;
    if(fd>=0){
        ok=read(fd,&record,sizeof(record))==sizeof(record);
        char extra;if(ok&&read(fd,&extra,1)!=0)ok=0;close(fd);
        ok=ok&&record.magic==0x31504243&&record.hash==profile_hash(record.data)
            &&!memcmp(record.data+8,profile_pin,9);
        if(ok)memcpy(data,record.data,PROFILE_SIZE);
    }
    return ok;
}
static int profile_snapshot(void){
    struct {unsigned magic,hash;unsigned char data[PROFILE_SIZE];} record;
    const char *temp="/pm/g5/race/pmuser/ally-profile.bin.tmp";
    record.magic=0x31504243;record.hash=profile_hash(profile_data);
    memcpy(record.data,profile_data,PROFILE_SIZE);
    int fd=open(temp,0x241,0600),ok=0;
    if(fd>=0){ok=write(fd,&record,sizeof(record))==sizeof(record)&&fsync(fd)==0;close(fd);}
    if(ok)ok=rename(temp,profile_file)==0;
    if(ok){int dir=open("/pm/g5/race/pmuser",0x10000);ok=dir>=0&&fsync(dir)==0;if(dir>=0)close(dir);}
    ally_profile_error=!ok;
    if(ok){memcpy(profile_previous,profile_data,PROFILE_SIZE);profile_previous_valid=1;ally_profile_saves++;}
    else fprintf(stderr,"ALLY profile snapshot failed; previous save retained\n");
    return ok;
}
static void profile_flush(void){
    if(!ally_profile_valid||!profile_active||memcmp(profile_data+8,profile_pin,9))return;
    if(profile_previous_valid&&!memcmp(profile_previous,profile_data,PROFILE_SIZE))return;
    /* The atomic sidecar remains recoverable even if native table writing fails. */
    if(!profile_snapshot())return;
    ((void(*)(void*,int))0x081d8430)(profile_data,1);
    profile_snapshot(); /* Include the native table's updated slot metadata. */
}
static void profile_native_save(void *data,int flag){
    if(data==profile_data&&profile_active&&!memcmp(profile_data+8,profile_pin,9))profile_snapshot();
    ((void(*)(void*,int))0x081d8430)(data,flag);
    if(data==profile_data&&profile_active&&!memcmp(profile_data+8,profile_pin,9))profile_snapshot();
}
static void profile_start(void *data){
    ((void(*)(void*))0x081d73f0)(data);
    if(!ally_profile_valid)return;
    ((void(*)(void*,const char*))0x081d79e0)(data,profile_pin);
    ally_profile_loaded=profile_read(data)?2:((unsigned char(*)(void*))0x081d8810)(data);
    if(!ally_profile_loaded)((void(*)(void*,const char*))0x081d76d0)(data,"ALLY");
    profile_active=1;profile_previous_valid=0;
    (*(unsigned short*)((unsigned char*)data+0x13e))++;
    profile_flush();
    fprintf(stderr,"ALLY profile automatic load=%d saves=%d\n",ally_profile_loaded,ally_profile_saves);
}
static void profile_end(void *data){
    profile_flush();profile_active=0;
    ((void(*)(void*))0x081d73f0)(data);
}
static void profile_pin_screen(void){
    /* Profile is already loaded before car selection; no PIN/stats prompt. */
    profile_flush();
}
static int profile_call_matches(unsigned at,unsigned target){
    unsigned char *p=(void*)at;
    return p[0]==0xe8&&at+5+*(unsigned*)(p+1)==target;
}
static void profile_call(unsigned at,void *target){
    *(unsigned*)(at+1)=(unsigned)target-at-5;
}
static void init_profile(void){
    const unsigned sites[]={0x0819878e,0x08198839,0x0819cbe0,0x0819d1dd,0x0819ce1f,0x0819d90c};
    const unsigned targets[]={0x081d73f0,0x081d73f0,0x0819b740,0x0819b740,0x081d8430,0x081d8430};
    ally_profile_valid=1;
    for(unsigned i=0;i<6;i++)if(!profile_call_matches(sites[i],targets[i]))ally_profile_valid=0;
    if(ally_profile_valid){
        profile_call(sites[0],profile_start);profile_call(sites[1],profile_end);
        profile_call(sites[2],profile_pin_screen);profile_call(sites[3],profile_pin_screen);
        profile_call(sites[4],profile_native_save);profile_call(sites[5],profile_native_save);
    }
    fprintf(stderr,"ALLY profile hook validation=%d\n",ally_profile_valid);
}
static void update_profile(void){
    unsigned (*now)(void)=next("SDL_GetTicks");unsigned tick=now();
    if(tick-profile_tick>=5000){profile_tick=tick;profile_flush();}
}
