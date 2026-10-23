import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(viewport={'width': 1100, 'height': 980})
        await pg.goto('http://localhost:8765/'); await pg.wait_for_timeout(1500)
        box = await pg.locator('#wheel').bounding_box(); cx, cy = box['x']+box['width']/2, box['y']+box['height']/2
        await pg.mouse.click(cx, cy); await pg.keyboard.press('Enter')
        await pg.keyboard.press('ArrowDown'); await pg.keyboard.press('ArrowDown'); await pg.keyboard.press('ArrowDown'); await pg.keyboard.press('ArrowDown')
        await pg.keyboard.press('Enter'); await pg.wait_for_timeout(200); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(9000)
        await pg.screenshot(path='/workspace/ipod-clone/screenshot.png')
        print(await pg.evaluate('__pod.state()'))
        await pg.keyboard.press('Escape'); await pg.keyboard.press('Escape'); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
        await pg.screenshot(path='/workspace/ipod-clone/shots/main-with-nowplaying.png')
        await b.close()
asyncio.run(main())
