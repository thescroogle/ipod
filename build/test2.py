import sys, time, math, json
from playwright.sync_api import sync_playwright
URL = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else '/tmp/t2'
import os; os.makedirs(OUT, exist_ok=True)
errs = []
def st(p): return p.evaluate('__pod.state()')
def drag(p, deg, steps=None, dur=0.6, r=0.85):
    b = p.locator('#wheel').bounding_box(); cx, cy = b['x']+b['width']/2, b['y']+b['height']/2; R = b['width']/2*r
    steps = steps or max(4, int(abs(deg)/5)); a0 = -90
    p.mouse.move(cx+R*math.cos(math.radians(a0)), cy+R*math.sin(math.radians(a0))); p.mouse.down()
    for i in range(1, steps+1):
        a = math.radians(a0+deg*i/steps); p.mouse.move(cx+R*math.cos(a), cy+R*math.sin(a)); time.sleep(dur/steps)
    p.mouse.up()
def press(p, zone, hold=0):
    b = p.locator('#wheel').bounding_box(); cx, cy = b['x']+b['width']/2, b['y']+b['height']/2; R = b['width']/2
    off = {'center':(0,0),'menu':(0,-.86),'next':(.86,0),'prev':(-.86,0),'play':(0,.86)}[zone]
    p.mouse.move(cx+off[0]*R, cy+off[1]*R); p.mouse.down(); time.sleep(hold or .05); p.mouse.up(); time.sleep(.15)
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--autoplay-policy=no-user-gesture-required'])
    p = br.new_page(viewport={'width': 460, 'height': 860})
    p.on('console', lambda m: m.type == 'error' and errs.append(m.text)); p.on('pageerror', lambda e: errs.append(str(e)))
    reqs = []; p.on('request', lambda r: reqs.append(r.url))
    p.goto(URL); p.wait_for_function('__pod.state().songs>0'); s = st(p); print('loaded', s['songs'], s['artists'], s['playlists'][:2])
    p.screenshot(path=f'{OUT}/boot.png')
    press(p, 'center'); print('main', st(p)['view'], p.inner_text('#view').split('\n'))
    press(p, 'center'); print('playlists', p.inner_text('#view').split('\n')[:4])
    press(p, 'center'); print('pl1', st(p)['title'], p.inner_text('#view').split('\n'))
    p.screenshot(path=f'{OUT}/aulani_pl.png')
    press(p, 'center'); time.sleep(3); s = st(p); print('play', s['view'], s['song'], s['playing'], s['t'], s['webAudio'])
    p.screenshot(path=f'{OUT}/np.png')
    v0 = st(p)['vol']; drag(p, 90); print('vol', v0, '->', st(p)['vol'], st(p)['np'])
    drag(p, -45); print('vol back', st(p)['vol'])
    press(p, 'menu'); press(p, 'menu'); press(p, 'menu'); press(p, 'menu'); print('after menus', st(p)['stack'], st(p)['sel'])
    # main remembered selection; go to Artists
    drag(p, 15, steps=4); print('sel', st(p)['sel'], st(p)['title']); press(p,'center'); print('artists', p.inner_text('#view').split('\n')[:3])
    t0 = st(p)['sel']; drag(p, 360, steps=60, dur=0.5); print('fast spin artists sel', t0, '->', st(p)['sel'])
    press(p,'menu'); drag(p, 30, steps=6); print('main sel', st(p)['sel']); press(p,'center'); press(p,'center'); print('about', p.inner_text('#view').split('\n'))
    p.screenshot(path=f'{OUT}/about.png')
    press(p, 'center', hold=5.3); print('brick', st(p)['view']); press(p,'center'); time.sleep(1); drag(p, 60); time.sleep(.5); p.screenshot(path=f'{OUT}/brick.png')
    press(p,'menu'); print('back from brick', st(p)['view'])
    press(p,'menu'); drag(p, 15*6, steps=24); print('settings sel', st(p)['sel'], p.inner_text('#view').split('\n')[-2:]); press(p,'center'); print('reset', st(p)['title'], p.inner_text('#view'))
    press(p,'center'); print('after cancel', st(p)['view'])
    # next track + crossfade near end
    press(p,'next'); time.sleep(1); print('next', st(p)['song'])
    p.evaluate("(()=>{const a=document.querySelectorAll('audio');})()")
    # idle -> now playing
    press(p,'menu'); press(p,'menu'); print('idle wait from', st(p)['view']); time.sleep(10.6); print('idle ->', st(p)['view'])
    p.evaluate("__pod.state()")
    ch0 = st(p)['ch']; p.evaluate("(()=>{})()")
    # seek near end to check crossfade
    p.evaluate("(()=>{})()")
    print('errors', errs)
    ext = sorted({r.split('/')[2] for r in reqs if r.startswith('http')})
    print('hosts', ext)
    br.close()
