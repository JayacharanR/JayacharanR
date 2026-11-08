from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import os

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
ASSETS.mkdir(parents=True, exist_ok=True)
SANS = os.environ.get('PROFILE_FONT', 'DejaVuSans.ttf')
MONO = os.environ.get('PROFILE_MONO_FONT', 'DejaVuSansMono.ttf')
S = 2

def font(size, bold=False, mono=False):
    f = ImageFont.truetype(MONO if mono else SANS, round(size*S))
    if not mono:
        try:
            axes = f.get_variation_axes()
            f.set_variation_by_axes([650 if a['name'] == b'Weight' and bold else a['default'] for a in axes])
        except OSError:
            pass
    return f

def canvas(w,h,bg):
    return Image.new('RGB',(w*S,h*S),bg)

def text(d,xy,t,size=18,fill='#eaeef3',bold=False,mono=False):
    d.text(tuple(round(v*S) for v in xy),t,font=font(size,bold,mono),fill=fill,stroke_width=0)

def line(d,pts,fill,width=1):
    d.line([(round(x*S),round(y*S)) for x,y in pts],fill=fill,width=round(width*S))

def circle(d,x,y,r,fill,outline=None,width=1):
    d.ellipse(((x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S),fill=fill,outline=outline,width=round(width*S))

def rr(d,box,fill,r=8,outline=None,width=1):
    d.rounded_rectangle(tuple(v*S for v in box),r*S,fill=fill,outline=outline,width=round(width*S))

def orbit(d,cx,cy,r,t=0,scale=1):
    green='#d5f773'
    for j in range(3):
        a=j*math.pi/3
        pts=[]
        for i in range(121):
            v=2*math.pi*i/120
            x=r*math.cos(v); y=r*.34*math.sin(v)
            pts.append((cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a)))
        line(d,pts,'#2c3936',1)
        v=2*math.pi*t+j*2.09
        x=r*math.cos(v); y=r*.34*math.sin(v)
        px=cx+x*math.cos(a)-y*math.sin(a); py=cy+x*math.sin(a)+y*math.cos(a)
        circle(d,px,py,8*scale,'#1b2a22')
        circle(d,px,py,3*scale,green)
    circle(d,cx,cy,21*scale,'#111a16','#384e3b')
    text(d,(cx-10*scale,cy-12*scale),'JR',17*scale,green,True)
    for dx,dy in [(-1,-1),(1,-1),(-1,1),(1,1)]:
        x=cx+dx*(r+17); y=cy+dy*(r+17)
        line(d,[(x,y+dy*7),(x,y),(x+dx*7,y)],'#435048',1)

def hero(mobile=False):
    w,h=(600,520) if mobile else (960,390)
    base=canvas(w,h,'#0c1013'); d=ImageDraw.Draw(base)
    for x in range(24,w,24):
        for y in range(20,h,24): circle(d,x,y,.65,'#242b2d')
    rr(d,(0,0,w-1,h-1),None,14,'#2a3235')
    margin=32 if mobile else 46
    text(d,(margin,27),'JAYACHARAN R',13,'#d5f773',True,True)
    text(d,(w-124,27),'[ BUILD / 01 ]',10,'#80908b',mono=True)
    title_y=83 if mobile else 89
    for i,s in enumerate(['Be kind.','Stay curious.']):
        text(d,(margin,title_y+i*(69 if mobile else 73)),s,61 if mobile else 67,'#f4f3ed',True)
    if mobile:
        text(d,(margin,468),'RETRIEVAL / CLOUD / WORLD MODELS',11,'#85928d',mono=True)
        center=(460,383); radius=64
        text(d,(margin,363),'BUILD THOUGHTFULLY.',11,'#d5f773',mono=True)
        text(d,(margin,389),'MEASURE HONESTLY.',11,'#d5f773',mono=True)
    else:
        line(d,[(46,330),(914,330)],'#293332')
        text(d,(46,350),'RETRIEVAL / CLOUD / WORLD MODELS',11,'#85928d',mono=True)
        text(d,(665,350),'BUILD. MEASURE. REFINE.',11,'#d5f773',mono=True)
        center=(777,186); radius=107
    frames=[]
    for n in range(60):
        im=base.copy(); draw=ImageDraw.Draw(im)
        orbit(draw,*center,radius,n/60,.85 if mobile else 1)
        # A quiet progress track makes the loop feel like a designed instrument.
        x0,y0=margin,(442 if mobile else 313)
        line(draw,[(x0,y0),(x0+92,y0)],'#344236',2)
        x=x0+92*(.5-.5*math.cos(2*math.pi*n/60))
        circle(draw,x,y0,2,'#d5f773')
        frames.append(im.resize((w,h),Image.Resampling.LANCZOS).convert('P',palette=Image.Palette.ADAPTIVE,colors=96))
    name='hero-mobile' if mobile else 'hero'
    frames[0].convert('RGB').save(ASSETS/f'{name}-still.png',optimize=True)
    frames[0].save(ASSETS/f'{name}.gif',save_all=True,append_images=frames[1:],duration=100,loop=0,optimize=True,disposal=1)

PROJECTS=[
    dict(id='clean-backup',n='01',cat='LOCAL-FIRST MEDIA TOOLING',title='Clean-Backup',hook='A little order. A lot less clutter.',
         lines=['Rust-powered perceptual deduplication, on-device AI,','and a reversible workflow for your photo library.'],
         mobile=['Rust-powered perceptual deduplication,','on-device AI, and a reversible workflow','for your photo library.'],
         tags='RUST  /  PYTHON  /  ONNX',color='#d5f773',kind='media'),
    dict(id='wikimind',n='02',cat='RETRIEVAL & KNOWLEDGE SYSTEMS',title='WikiMind',hook='Answers with a paper trail.',
         lines=['Two-stage hybrid search over Wikipedia. Live updates,','reranking, and citation checks before an answer leaves.'],
         mobile=['Two-stage hybrid search over Wikipedia.','Live updates, reranking, and citation','checks before an answer leaves.'],
         tags='QDRANT  /  REDIS  /  LANGGRAPH',color='#8dd9ee',kind='rag'),
    dict(id='carbon-aware',n='03',cat='CARBON-AWARE INFRASTRUCTURE',title='Carbon-Aware Cloud',hook='Better placement. Explicit constraints.',
         lines=['A multi-region AKS scheduler pairing an LLM proposer','with deterministic checks and an optimization fallback.'],
         mobile=['A multi-region AKS scheduler pairing','an LLM proposer with deterministic','checks and an optimization fallback.'],
         tags='AZURE AKS  /  LLAMA 3  /  PULP  /  PYTHON',color='#c6b1ff',kind='cloud'),
    dict(id='auto-thinker',n='04',cat='WORLD MODELS / RESEARCH IN PROGRESS',title='Auto Thinker Engine',hook='Learning to see. Learning to decide.',
         lines=['Camera-based driving research in CARLA with JEPA','representations, DreamerV3, and multi-camera navigation.'],
         mobile=['Camera-based driving research in CARLA','with JEPA representations, DreamerV3,','and multi-camera navigation.'],
         tags='PYTORCH  /  JEPA  /  DREAMERV3  /  CARLA',color='#ffbd91',kind='drive'),
]

def glyph(d,kind,x,y,c,muted,bg):
    if kind=='media':
        for dx,dy in [(0,0),(12,-12),(24,-24)]:
            rr(d,(x+dx,y+dy,x+dx+63,y+dy+76),bg,6,muted)
        line(d,[(x+31,y+33),(x+47,y+16),(x+62,y+34),(x+77,y+17)],c,2)
        circle(d,x+68,y-5,5,c)
        rr(d,(x+3,y+62,x+36,y+84),c,4)
        line(d,[(x+12,y+73),(x+18,y+78),(x+28,y+68)],bg,2)
    elif kind=='rag':
        for dx,dy in [(0,0),(14,-13),(28,-26)]:
            rr(d,(x+dx,y+dy,x+dx+47,y+dy+64),bg,5,muted)
            for yy in [14,24,34]: line(d,[(x+dx+10,y+dy+yy),(x+dx+35,y+dy+yy)],muted)
        circle(d,x+69,y+51,19,bg,c,2)
        line(d,[(x+82,y+65),(x+94,y+78)],c,3)
        text(d,(x+60,y+39),'[ ]',14,c,mono=True)
    elif kind=='cloud':
        for dy in [0,25,50]:
            rr(d,(x,y+dy,x+75,y+dy+18),bg,4,muted)
            circle(d,x+10,y+dy+9,2,c)
        line(d,[(x+90,y-20),(x+60,y+24),(x+81,y+24),(x+48,y+80),(x+64,y+35),(x+44,y+35),(x+90,y-20)],c,2)
    else:
        line(d,[(x+7,y+84),(x+33,y-24),(x+56,y-24),(x+89,y+84)],muted,2)
        for dy in [-14,9,32,55]: line(d,[(x+45,y+dy),(x+45,y+dy+10)],c,2)
        for dx,dy in [(-7,-9),(67,-9),(30,56)]:
            rr(d,(x+dx,y+dy,x+dx+25,y+dy+17),bg,3,c)
            circle(d,x+dx+12,y+dy+8,4,None,c)

def card(p,light=False,mobile=False):
    w,h=(600,355) if mobile else (960,227)
    bg='#f6f7f4' if light else '#101518'; fg='#172022' if light else '#f1f2ed'
    sub='#4c5b5b' if light else '#a8b4b1'; mute='#cad2ce' if light else '#33413e'
    accent={'#d5f773':'#577522','#8dd9ee':'#24748b','#c6b1ff':'#7857b3','#ffbd91':'#a85629'}.get(p['color']) if light else p['color']
    im=canvas(w,h,bg); d=ImageDraw.Draw(im)
    rr(d,(.5,.5,w-1,h-1),None,12,mute)
    if mobile:
        tx=28
        text(d,(tx,22),p['n']+' / '+p['cat'],11,accent,mono=True)
        text(d,(tx,61),p['title'],40,fg,True)
        text(d,(tx,112),p['hook'],25,fg)
        for i,t in enumerate(p['mobile']): text(d,(tx,157+i*33),t,28,sub)
        line(d,[(28,271),(572,271)],mute)
        text(d,(tx,293),p['tags'],13,accent,mono=True)
        text(d,(tx,322),'EXPLORE THE REPOSITORY',10,sub,mono=True)
        line(d,[(547,325),(565,307),(550,307),(565,307),(565,322)],accent,2)
    else:
        text(d,(30,22),p['n'],11,sub,mono=True)
        glyph(d,p['kind'],49,91,accent,mute,bg)
        tx=188
        text(d,(tx,22),p['cat'],11,accent,mono=True)
        text(d,(tx,47),p['title'],32,fg,True)
        text(d,(tx,95),p['hook'],20,fg)
        for i,t in enumerate(p['lines']): text(d,(tx,130+i*24),t,17,sub)
        text(d,(tx,194),p['tags'],10,accent,mono=True)
        line(d,[(908,65),(930,43),(912,43),(930,43),(930,61)],accent,2)
    suffix=('-mobile' if mobile else '')+('-light' if light else '')
    im.save(ASSETS/f"{p['id']}{suffix}.png",optimize=True)

hero(); hero(True)
for p in PROJECTS:
    for light in [False,True]:
        for mobile in [False,True]: card(p,light,mobile)
print('Generated',len(list(ASSETS.iterdir())),'assets')
