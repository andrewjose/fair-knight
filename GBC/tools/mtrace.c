// mtrace: headless libmgba runner (GB/GBC/GBA) with write-watchpoints that log PC.
// usage: mtrace ROM SCRIPT   (commands: wait N | hold KEYS N | shot F.ppm | watch ADDR | unwatch_all |
//        peek ADDR | poke ADDR VAL | dump ADDR LEN FILE | state_save F | state_load F | quiet 0/1)
#include <mgba/core/core.h>
#include <mgba/core/log.h>
#include <mgba/core/serialize.h>
#include <mgba/debugger/debugger.h>
#include <mgba/internal/sm83/sm83.h>
#include <mgba/internal/gb/gb.h>
#include <mgba-util/vfs.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static struct mCore* core; static int frame=0; static struct mDebugger dbg; static uint32_t* buf; static unsigned W,H;
static void nolog(struct mLogger* l,int c,enum mLogLevel lv,const char* f,va_list a){(void)l;(void)c;(void)lv;(void)f;(void)a;}
static struct mLogger logger={.log=nolog};
static void entered(struct mDebugger* d, enum mDebuggerEntryReason r, struct mDebuggerEntryInfo* info){
  if(r==DEBUGGER_ENTER_WATCHPOINT && info){
    struct SM83Core* cpu=(struct SM83Core*)core->cpu; struct GB* gb=(struct GB*)core->board;
    printf("[%d] W %04X old=%02X new=%02X pc=%04X bank=%d hl=%04X\n",frame,info->address,info->type.wp.oldValue&0xFF,info->type.wp.newValue&0xFF,cpu->pc,gb->memory.currentBank,cpu->hl);
  }
  d->state=DEBUGGER_RUNNING;
}
static void paused(struct mDebugger* d){ d->state=DEBUGGER_RUNNING; }
static int keymask(const char* s){int m=0;char b[64];strncpy(b,s,63);b[63]=0;for(char*t=strtok(b,"+");t;t=strtok(NULL,"+")){
 if(!strcmp(t,"A"))m|=1;else if(!strcmp(t,"B"))m|=2;else if(!strcmp(t,"SELECT"))m|=4;else if(!strcmp(t,"START"))m|=8;
 else if(!strcmp(t,"RIGHT"))m|=16;else if(!strcmp(t,"LEFT"))m|=32;else if(!strcmp(t,"UP"))m|=64;else if(!strcmp(t,"DOWN"))m|=128;
 else if(!strcmp(t,"R"))m|=256;else if(!strcmp(t,"L"))m|=512;}return m;}
static void run(int n,int keys){core->setKeys(core,keys);for(int i=0;i<n;i++){mDebuggerRunFrame(&dbg);frame++;}core->setKeys(core,0);}
static void shot(const char* fn){FILE*f=fopen(fn,"wb");fprintf(f,"P6\n%u %u\n255\n",W,H);for(unsigned i=0;i<W*H;i++){uint32_t c=buf[i];fputc(c&0xFF,f);fputc((c>>8)&0xFF,f);fputc((c>>16)&0xFF,f);}fclose(f);}
int main(int argc,char**argv){
  mLogSetDefaultLogger(&logger);
  core=mCoreFind(argv[1]); core->init(core); mCoreInitConfig(core,NULL);
  core->desiredVideoDimensions(core,&W,&H); buf=malloc(W*H*4); core->setVideoBuffer(core,(void*)buf,W);
  mCoreLoadFile(core,argv[1]); core->reset(core);
  memset(&dbg,0,sizeof dbg); dbg.entered=entered; dbg.paused=paused; dbg.type=DEBUGGER_CUSTOM;
  mDebuggerAttach(&dbg,core); dbg.state=DEBUGGER_RUNNING;
  FILE* sf=fopen(argv[2],"r"); char line[512];
  while(fgets(line,sizeof line,sf)){
    char c[64]="",a1[256]="",a2[256]="",a3[256]=""; if(line[0]=='#')continue;
    int n=sscanf(line,"%63s %255s %255s %255s",c,a1,a2,a3); if(n<1)continue;
    if(!strcmp(c,"wait")) run(atoi(a1),0);
    else if(!strcmp(c,"hold")) run(atoi(a2),keymask(a1));
    else if(!strcmp(c,"shot")) shot(a1);
    else if(!strcmp(c,"watch")){struct mWatchpoint wp={0};wp.address=strtoul(a1,0,16);wp.segment=-1;wp.type=WATCHPOINT_WRITE;dbg.platform->setWatchpoint(dbg.platform,&wp);}
    else if(!strcmp(c,"peek")) printf("[%d] peek %s = %02X\n",frame,a1,core->busRead8(core,strtoul(a1,0,16)));
    else if(!strcmp(c,"poke")) core->rawWrite8(core,strtoul(a1,0,16),-1,strtoul(a2,0,16));
    else if(!strcmp(c,"dump")){FILE*o=fopen(a3,"wb");uint32_t ad=strtoul(a1,0,16);int ln=strtol(a2,0,16);for(int i=0;i<ln;i++)fputc(core->busRead8(core,ad+i),o);fclose(o);}
    else if(!strcmp(c,"state_save")){struct VFile* vf=VFileOpen(a1,O_CREAT|O_TRUNC|O_WRONLY);mCoreSaveStateNamed(core,vf,SAVESTATE_SAVEDATA);vf->close(vf);}
    else if(!strcmp(c,"state_load")){struct VFile* vf=VFileOpen(a1,O_RDONLY);mCoreLoadStateNamed(core,vf,SAVESTATE_SAVEDATA);vf->close(vf);}
    printf("[%d] %s",frame,line); fflush(stdout);
  }
  return 0;
}
