from pathlib import Path
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
import math
import os
import random

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
ASSETS.mkdir(parents=True, exist_ok=True)
SANS = os.environ.get('PROFILE_FONT', 'DejaVuSans.ttf')
MONO = os.environ.get('PROFILE_MONO_FONT', 'DejaVuSansMono.ttf')
S = 2

@lru_cache(maxsize=64)
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

BG='#090d0e'; PANEL='#111719'; WHITE='#f3f2e8'; MUTE='#99aaa5'
LINE='#37463f'; YELLOW='#e7ff58'; GREEN='#cbed85'; CYAN='#8bded3'

def rect(d,box,fill,outline=None,width=1):
    d.rectangle(tuple(v*S for v in box),fill=fill,outline=outline,width=round(width*S))

def panel(d,x,y,w,h,accent=LINE,fill=PANEL,shadow='#030606'):
    # Chamfered corners and hard offset shadows keep the brutalist structure.
    pts=[(x,y),(x+w-14,y),(x+w,y+14),(x+w,y+h),(x+14,y+h),(x,y+h-14),(x,y)]
    line(d,[(px+5,py+5) for px,py in pts],shadow,4)
    d.polygon([(px*S,py*S) for px,py in pts[:-1]],fill=fill)
    line(d,pts,accent,1)
    for px,py,dx,dy in [(x,y,1,1),(x+w,y+h,-1,-1)]:
        line(d,[(px,py+dy*17),(px,py),(px+dx*24,py)],accent,2)

def hazard(d,x,y,w,h):
    rect(d,(x,y,x+w,y+h),YELLOW)
    for xx in range(round(x)-15,round(x+w),17):
        # Keep every stripe bounded by the panel.
        pts=[(max(x,xx),y+h),(min(x+w,xx+h),y),(min(x+w,xx+h+7),y),(min(x+w,xx+7),y+h)]
        if min(px for px,py in pts)>=x and max(px for px,py in pts)<=x+w:
            d.polygon([(px*S,py*S) for px,py in pts],fill=BG)

def atom(draw,t,cx,cy,r):
    scale=r/103
    for n in range(48):
        a=n*math.pi/24
        inner=(119 if n%4 else 115)*scale
        line(draw,[(cx+inner*math.cos(a),cy+inner*math.sin(a)),(cx+123*scale*math.cos(a),cy+123*scale*math.sin(a))],LINE,1)
    for j in range(3):
        a=j*math.pi/3
        def point(v):
            x=r*math.cos(v);y=r*.33*math.sin(v)
            return cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a)
        pts=[point(k*math.pi/90) for k in range(181)]
        line(draw,pts,'#657447',1)
        v=2*math.pi*(t+j/3)
        for k in range(20):
            u=v-k*.025
            x,y=point(u)
            circle(draw,x,y,1.1,'#718439' if k<9 else '#3e4c2c')
        x,y=point(v)
        circle(draw,x,y,8*scale,'#26361b')
        circle(draw,x,y,3.5*scale,YELLOW)
    circle(draw,cx,cy,30*scale,'#172118',YELLOW,1)
    # Optical centering includes the font's actual ink bounds.
    size=22*scale
    f=font(size,True);box=f.getbbox('JR')
    tx=cx-(box[0]+box[2])/(2*S);ty=cy-(box[1]+box[3])/(2*S)
    text(draw,(tx,ty),'JR',size,YELLOW,True)

LOOP_SECONDS = 24
FRAME_MS = 100
TRACE_ROWS = (40, 69, 98)
TRACE_COLORS = (YELLOW, CYAN, '#c2adff')
SIGNAL_POINTS = 439


def build_channels():
    rng = random.Random(94723)
    channels = []
    for channel in range(len(TRACE_ROWS)):
        bursts = []
        start = rng.uniform(0, .6)
        while start < LOOP_SECONDS:
            bursts.append((
                start, rng.uniform(.43, 2.3), rng.uniform(.09, .91),
                rng.uniform(-.11, .11), rng.uniform(.005, .041),
                rng.uniform(6, 24), rng.uniform(.19, .83) + channel*.10,
                rng.uniform(-.19, .19), rng.uniform(.4, 2.1), rng.random(),
            ))
            start += rng.uniform(.65, 1.15) if rng.random() < .12 else rng.uniform(.13, .49)
        channels.append(bursts)
    return channels


CHANNELS = build_channels()


def wave(draw, elapsed, left, right, top):
    for row, color, bursts in zip(TRACE_ROWS, TRACE_COLORS, CHANNELS):
        visible = []
        for start, duration, center, drift, width, height, freq, chirp, rate, phase in bursts:
            age = (elapsed - start) % LOOP_SECONDS
            if age >= duration:
                continue
            progress = age / duration
            gain = min(1, progress/.15, (1-progress)/.36)
            gain = gain*gain*(3-2*gain)
            visible.append((center+drift*progress, width, height*gain, freq,
                            chirp, phase+age*rate))
        points = []
        for index in range(SIGNAL_POINTS):
            u = index / (SIGNAL_POINTS-1)
            value = .8 * math.sin(math.tau*(3.1*u - elapsed/4 + row/30))
            value += .4 * math.sin(math.tau*(9.6*u + elapsed/3))
            for center, width, height, freq, chirp, phase in visible:
                offset = (u-center)/width
                if abs(offset) < 3.5:
                    cycles = freq*offset + chirp*offset**2/2 + phase
                    carrier = math.cos(math.tau*cycles)
                    ripple = .17*math.sin(math.tau*(2.6*cycles + .18*offset))
                    value += height*(carrier+ripple)*math.exp(-.5*offset**2)
            edge = min(1, 30*u, 30*(1-u))
            value = 18*math.tanh(value/18)*edge
            points.append((left+(right-left)*u, top+row+value))
        line(draw, points, color, 1.45)


def hero(mobile=False):
    # The desktop crop matches the approved prototype. Mobile gives the
    # headline and atom more vertical space before the full-width trace.
    w,h=(600,506) if mobile else (960,482)
    base=canvas(w,h,BG)
    draw=ImageDraw.Draw(base)
    right=w-20
    bottom=h-6
    panel(draw,20,20,w-40,bottom-20)
    hazard(draw,21,21,w-42,7)
    text(draw,(46,43),'JAYACHARAN R',15 if mobile else 13,YELLOW,True,True)
    line(draw,[(46,78),(right-26,78)],LINE)
    for i,label in enumerate(('Be kind.','Stay curious.')):
        text(draw,(46,100+i*(64 if mobile else 76)),label,53 if mobile else 67,WHITE,True)
    text(draw,(49,311 if mobile else 291),'RETRIEVAL / CLOUD / WORLD MODELS',16 if mobile else 11,MUTE,mono=True)
    top=350 if mobile else 326
    trace_left,trace_right=69,right-42
    rect(draw,(47,top,right-27,top+122),'#0a1010',LINE)
    rect(draw,(47,top,53,top+122),YELLOW)
    for x in range(trace_left,trace_right+1,25):
        for y in range(top+22,top+111,18):
            circle(draw,x,y,.6,'#27372f')
    for row in TRACE_ROWS:
        line(draw,[(trace_left,top+row),(trace_right,top+row)],'#24322b')
    text(draw,(trace_left,top+10),'OSCILLATOR',12 if mobile else 8,MUTE,mono=True)
    frames=[]
    name='atomic-oscillator-mobile' if mobile else 'atomic-oscillator-desktop'
    palette=None
    for n in range(LOOP_SECONDS*1000//FRAME_MS):
        elapsed=6+n*FRAME_MS/1000
        image=base.copy()
        frame=ImageDraw.Draw(image)
        center=(472,219,76) if mobile else (772,191,103)
        atom(frame,elapsed/6,*center)
        wave(frame,elapsed,trace_left,trace_right,top)
        image=image.resize((w,h),Image.Resampling.LANCZOS).crop((16,16,w-16,h))
        if n==0:
            image.save(ASSETS/f'{name}-still.png',optimize=True)
            palette=image.quantize(colors=128)
        frames.append(image.quantize(palette=palette,dither=Image.Dither.NONE))
    frames[0].save(ASSETS/f'{name}.gif',save_all=True,append_images=frames[1:],duration=FRAME_MS,loop=0,optimize=True,disposal=1)
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


def card(project,light=False,mobile=False):
    w,h=(568,290) if mobile else (928,184)
    image=canvas(w,h,'#f4f6f1' if light else BG)
    draw=ImageDraw.Draw(image)
    surface,foreground,muted,border,shadow=(
        ('#f7f8f4','#172022','#45534e','#b6c1b8','#d4dbd2')
        if light else (PANEL,WHITE,MUTE,LINE,'#030606')
    )
    palette=('#577522','#24748b','#7857b3','#a85629') if light else (GREEN,CYAN,'#c6b1ff','#ffbd91')
    accent=palette[int(project['n'])-1]
    panel(draw,8,2,w-16,h-9,border,surface,shadow)
    rect(draw,(9,3,14,h-8),accent)
    rect(draw,(30,20,68,47),accent)
    text(draw,(38,24),project['n'],14,WHITE if light else BG,True,True)
    if mobile:
        text(draw,(81,23),project['cat'],12,accent,mono=True)
        text(draw,(30,61),project['title'],38,foreground,True)
        for i,description in enumerate(project['mobile']):
            text(draw,(30,122+i*32),description,25,muted)
        text(draw,(30,237),project['tags'],13,accent,mono=True)
    else:
        glyph(draw,project['kind'],41,84,accent,border,surface)
        text(draw,(174,17),project['cat'],10,accent,mono=True)
        text(draw,(174,39),project['title'],31,foreground,True)
        for i,description in enumerate(project['lines']):
            text(draw,(175,89+i*23),description,17,muted)
        text(draw,(175,147),project['tags'],10,accent,mono=True)
    x,y=w-40,34 if not mobile else 69
    line(draw,[(x-25,y+25),(x,y),(x-19,y),(x,y),(x,y+19)],accent,2)
    suffix=('-mobile' if mobile else '')+('-light' if light else '')
    image.save(ASSETS/f"atomic-{project['id']}{suffix}.png",optimize=True)


if __name__=='__main__':
    hero()
    hero(mobile=True)
    for project in PROJECTS:
        for light in (False,True):
            for mobile in (False,True):
                card(project,light,mobile)
