import asyncio, json, sys
from playwright.async_api import async_playwright
URL = 'http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(viewport={'width': 520, 'height': 860}, device_scale_factor=2)
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
        await pg.goto(URL); await pg.wait_for_timeout(1500)
        await pg.screenshot(path='/workspace/ipod-clone/shots/1-boot.png')
        st = lambda: pg.evaluate('__pod.state()')
        box = await pg.locator('#wheel').bounding_box()
        cx, cy, R = box['x'] + box['width']/2, box['y'] + box['height']/2, box['width']/2
        # real mouse press on centre button -> main menu
        await pg.mouse.click(cx, cy); await pg.wait_for_timeout(300)
        print('after center', await st())
        await pg.screenshot(path='/workspace/ipod-clone/shots/2-main.png')
        # circular drag clockwise on wheel ring (~60 degrees => 4 ticks)
        import math
        r = R * 0.55
        await pg.mouse.move(cx + r*math.cos(-math.pi/2), cy + r*math.sin(-math.pi/2)); await pg.mouse.down()
        for i in range(1, 21):
            a = -math.pi/2 + i * (math.radians(48)/20)
            await pg.mouse.move(cx + r*math.cos(a), cy + r*math.sin(a))
        await pg.mouse.up(); await pg.wait_for_timeout(200)
        print('after cw drag 48deg', await st())
        # counter-clockwise drag back 48deg
        await pg.mouse.move(cx + r*math.cos(0), cy + r*math.sin(0)); await pg.mouse.down()
        for i in range(1, 21):
            a = -i * (math.radians(48)/20)
            await pg.mouse.move(cx + r*math.cos(a), cy + r*math.sin(a))
        await pg.mouse.up(); await pg.wait_for_timeout(200)
        print('after ccw drag', await st())
        # mouse wheel + arrow keys
        await pg.mouse.move(cx, cy); await pg.mouse.wheel(0, 80); await pg.wait_for_timeout(100)
        print('after mousewheel', await st())
        await pg.keyboard.press('ArrowUp'); await pg.keyboard.press('ArrowUp'); print('after arrows', await st())
        # open Playlists -> Pop Hits
        await pg.mouse.click(cx, cy); await pg.wait_for_timeout(200)
        await pg.screenshot(path='/workspace/ipod-clone/shots/3-playlists.png')
        await pg.keyboard.press('ArrowDown'); await pg.keyboard.press('ArrowDown')
        await pg.mouse.click(cx, cy); await pg.wait_for_timeout(200)
        print('in playlist', await st())
        await pg.screenshot(path='/workspace/ipod-clone/shots/4-tracks.png')
        await pg.mouse.click(cx, cy); await pg.wait_for_timeout(2500)
        print('playing', await st())
        await pg.screenshot(path='/workspace/ipod-clone/shots/5-nowplaying.png')
        # touch-like drag on now playing -> volume
        await pg.mouse.move(cx + r, cy); await pg.mouse.down()
        for i in range(1, 16):
            a = -i * (math.radians(60)/15)
            await pg.mouse.move(cx + r*math.cos(a), cy + r*math.sin(a))
        await pg.mouse.up(); await pg.wait_for_timeout(150)
        print('volume', await st())
        await pg.screenshot(path='/workspace/ipod-clone/shots/6-volume.png')
        # next button (right ring)
        await pg.mouse.click(cx + R*0.86, cy); await pg.wait_for_timeout(800)
        print('after next', await st())
        # play/pause (bottom ring)
        await pg.mouse.click(cx, cy + R*0.86); await pg.wait_for_timeout(300)
        print('after pause', await st())
        # menu twice -> main shows Now Playing
        await pg.mouse.click(cx, cy - R*0.86); await pg.mouse.click(cx, cy - R*0.86); await pg.wait_for_timeout(200)
        await pg.mouse.click(cx, cy - R*0.86); await pg.wait_for_timeout(200)
        print('after menus', await st())
        await pg.mouse.click(cx, cy + R*0.86); await pg.wait_for_timeout(1500)
        await pg.screenshot(path='/workspace/ipod-clone/shots/7-main-nowplaying.png')
        # search: Songs -> Search iTunes, type via keyboard, DONE
        await pg.keyboard.press('ArrowDown'); await pg.keyboard.press('ArrowDown'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(100)
        await pg.keyboard.press('Enter'); await pg.wait_for_timeout(100)
        print('search?', await st())
        for ch in 'DAFT': await pg.keyboard.press(ch.lower())
        await pg.keyboard.press('ArrowDown')
        await pg.screenshot(path='/workspace/ipod-clone/shots/8-search.png')
        await pg.keyboard.press('ArrowUp'); await pg.keyboard.press('ArrowUp'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(3000)
        print('results', await st())
        await pg.screenshot(path='/workspace/ipod-clone/shots/9-results.png')
        # touch emulation test
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=3, is_mobile=True, has_touch=True)
        m = await ctx.new_page(); await m.goto(URL); await m.wait_for_timeout(1200)
        bx = await m.locator('#wheel').bounding_box(); mcx, mcy = bx['x']+bx['width']/2, bx['y']+bx['height']/2
        await m.touchscreen.tap(mcx, mcy); await m.wait_for_timeout(300)
        cdp = await ctx.new_cdp_session(m); rr = bx['width']/2*0.55
        pts = [(mcx + rr*math.cos(-math.pi/2 + i*math.radians(3)), mcy + rr*math.sin(-math.pi/2 + i*math.radians(3))) for i in range(0, 21)]
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': pts[0][0], 'y': pts[0][1]}]})
        for x, y in pts[1:]:
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x, 'y': y}]})
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        await m.wait_for_timeout(200)
        print('mobile touch drag 60deg', await m.evaluate('__pod.state()'))
        await m.screenshot(path='/workspace/ipod-clone/shots/10-mobile.png')
        print('ERRORS', errs)
        await b.close()
asyncio.run(main())
