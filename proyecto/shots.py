import os, glob
from playwright.sync_api import sync_playwright
U={'psblog':'https://blog.playstation.com/2026/07/01/physical-disc-production-ending-in-january-2028-for-new-games-releasing-on-playstation-consoles/',
   're3':'https://github.com/GTAmodding/re3','skycraft':'https://github.com/chasmlol/SkyCraft',
   'sm64code':'https://github.com/n64decomp/sm64/blob/master/src/game/mario.c'}
exe=(glob.glob('/opt/pw-browsers/chromium-*/chrome-linux*/chrome')+glob.glob('/opt/pw-browsers/chromium'))[0]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=exe,proxy={'server':os.environ['HTTPS_PROXY']})
    pg=b.new_page(viewport={'width':1600,'height':1000},device_scale_factor=1.5)
    for k,u in U.items():
        if os.path.exists(f'gfx/shot_{k}.png'): continue
        try:
            pg.goto(u,wait_until='load',timeout=60000); pg.wait_for_timeout(2500)
            if k=='psblog':
                el=pg.get_by_text('Physical game disc production',exact=False).first
                el.scroll_into_view_if_needed(); pg.evaluate("window.scrollBy(0,-250)")
                el.evaluate("e=>{e.style.background='rgba(255,220,0,.45)'}")
            if k=='sm64code': pg.evaluate("window.scrollBy(0,700)"); pg.wait_for_timeout(1500)
            pg.screenshot(path=f'gfx/shot_{k}.png'); print(k,'ok',pg.title()[:70])
        except Exception as e: print(k,'FAIL',str(e)[:200])
    b.close()
