import sys, importlib, subprocess, os
from clipedit import ACTIVE
from PIL import Image
m=importlib.import_module(sys.argv[1]); shots=m.shots
tw,th=180,320; cols=9; rows=(len(shots)+cols-1)//cols
S=Image.new('RGB',(cols*tw,rows*th))
for i,s in enumerate(shots):
    top,ah=ACTIVE.get(os.path.basename(s['src']).split('.')[0],(0,1080))
    z=s.get('z',1.0); ch=ah/z; cw=ch*9/16
    x0=min(max(s.get('xc',.5)*1920-cw/2,0),1920-cw); y0=top+min(max(s.get('yc',.5)*ah-ch/2,0),ah-ch)
    mid=s['start']+s['dur']*s.get('speed',1)/2
    subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{mid:.2f}','-i',s['src'],'-frames:v','1','-vf',f'crop={cw:.0f}:{ch:.0f}:{x0:.0f}:{y0:.0f},scale={tw}:{th}','/tmp/c.jpg'])
    S.paste(Image.open('/tmp/c.jpg'),((i%cols)*tw,(i//cols)*th))
S.save(f'qc/crops_{sys.argv[1]}.jpg',quality=85)
