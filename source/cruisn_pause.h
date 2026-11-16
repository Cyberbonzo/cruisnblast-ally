/* Small locally drawn pause screen; no copyrighted artwork or fonts. */
extern int usleep(unsigned);
static void (*gBegin)(unsigned),(*gEnd)(void),(*gVertex)(float,float),(*gColor)(float,float,float);
static void quad(float x,float y,float w,float h){gVertex(x,y);gVertex(x+w,y);gVertex(x+w,y+h);gVertex(x,y+h);}
static const unsigned char letters[26][7]={
{14,17,17,31,17,17,17},{30,17,17,30,17,17,30},{14,17,16,16,16,17,14},{30,17,17,17,17,17,30},
{31,16,16,30,16,16,31},{31,16,16,30,16,16,16},{14,17,16,23,17,17,15},{17,17,17,31,17,17,17},
{31,4,4,4,4,4,31},{7,2,2,2,18,18,12},{17,18,20,24,20,18,17},{16,16,16,16,16,16,31},
{17,27,21,21,17,17,17},{17,25,25,21,19,19,17},{14,17,17,17,17,17,14},{30,17,17,30,16,16,16},
{14,17,17,17,21,18,13},{30,17,17,30,20,18,17},{15,16,16,14,1,1,30},{31,4,4,4,4,4,4},
{17,17,17,17,17,17,14},{17,17,17,17,17,10,4},{17,17,17,21,21,21,10},{17,17,10,4,10,17,17},
{17,17,10,4,4,4,4},{31,1,2,4,8,16,31}};
static void label(const char *s,float x,float y,float scale){
    gBegin(7);
    for(;*s;s++,x+=6*scale)if(*s>='A'&&*s<='Z'){
        const unsigned char *p=letters[*s-'A'];
        for(int row=0;row<7;row++)for(int col=0;col<5;col++)if(p[row]&(16>>col))quad(x+col*scale,y+row*scale,scale,scale);
    }
    gEnd();
}
static void pause_screen(void (*swap)(void)){
    void (*push)(unsigned)=next("glPushAttrib"),(*pop)(void)=next("glPopAttrib");
    void (*get)(unsigned,int*)=next("glGetIntegerv"),(*use)(unsigned)=next("glUseProgram");
    void (*bind)(unsigned,unsigned)=next("glBindFramebuffer");
    void (*matrix)(unsigned)=next("glMatrixMode"),(*pushm)(void)=next("glPushMatrix"),(*popm)(void)=next("glPopMatrix"),(*identity)(void)=next("glLoadIdentity");
    void (*ortho)(double,double,double,double,double,double)=next("glOrtho");
    void (*disable)(unsigned)=next("glDisable"),(*active)(unsigned)=next("glActiveTexture");
    void (*viewport)(int,int,int,int)=next("glViewport");
    void (*clearcolor)(float,float,float,float)=next("glClearColor"),(*clear)(unsigned)=next("glClear");
    int (*poll)(void*)=next("SDL_PollEvent");
    int (*master)(void*,void**)=next("FMOD_System_GetMasterChannelGroup");
    int (*mute)(void*,int)=next("FMOD_ChannelGroup_SetPaused");
    void *group=0;int program=0,fbo=0,mode=0,vp[4],sim=*(int*)0x08a9c75c;
    if(master&&mute&&*(void**)0x09c5a99c)master(*(void**)0x09c5a99c,&group);
    if(group)mute(group,1);
    *(int*)0x08a9c75c=0;
    paused=1;ally_pause_selected=0;fprintf(stderr,"ALLY PAUSE entered clock=%llu\n",*(unsigned long long*)0x09d87c78);
    gBegin=next("glBegin");gEnd=next("glEnd");gVertex=next("glVertex2f");gColor=next("glColor3f");
    get(0x8b8d,&program);get(0x8ca6,&fbo);get(0x0ba0,&mode);get(0x0ba2,vp);
    push(0xfffff);use(0);bind(0x8d40,0);viewport(0,0,1920,1080);
    matrix(0x1701);pushm();identity();ortho(0,1920,1080,0,-1,1);
    matrix(0x1700);pushm();identity();
    disable(0xb71);disable(0xb50);disable(0xb44);disable(0xc11);disable(0xbe2);disable(0xbc0);
    for(int i=0;i<8;i++){active(0x84c0+i);disable(0xde1);}active(0x84c0);
    clearcolor(.025f,.035f,.065f,1);
    while(!pause_requested){
        clear(0x4000);gColor(.95f,.65f,.08f);gBegin(7);quad(320,245,1280,7);gEnd();
        gColor(1,1,1);label("PAUSED",600,310,20);
        gColor(.14f,.21f,.32f);gBegin(7);quad(350,500+ally_pause_selected*110,1220,85);gEnd();
        gColor(1,1,1);label("RESUME",410,520,7);
        label("CHEATS  INFINITE BLAST",410,630,6);
        gColor(.95f,.65f,.08f);label(!ally_cheat_valid?"ERROR":ally_infinite_boost?"ON":"OFF",1320,630,6);
        gColor(.65f,.72f,.85f);label("DPAD SELECT   A CONFIRM   B START RESUME",350,780,5);
        label("X BLAST    RT GAS    LT BRAKE",455,870,6);
        if(cheat_save_error){gColor(1,.3f,.2f);label("SETTING SAVE FAILED",620,950,5);}
        swap();unsigned char event[64];while(poll(event)){}
        controls();usleep(16000);
    }
    matrix(0x1700);popm();matrix(0x1701);popm();matrix(mode);pop();use(program);bind(0x8d40,fbo);viewport(vp[0],vp[1],vp[2],vp[3]);
    /* Skip paused wall time in the game's accumulated simulation clock. */
    *(unsigned long long*)0x09c32cc0=((unsigned long long(*)(void))0x084a6820)();
    *(unsigned long long*)0x09c32cb0=((unsigned long long(*)(void))0x084a6940)();
    *(int*)0x08a9c75c=sim;
    if(group)mute(group,0);
    paused=0;pause_requested=0;
    fprintf(stderr,"ALLY PAUSE resumed clock=%llu\n",*(unsigned long long*)0x09d87c78);
}
