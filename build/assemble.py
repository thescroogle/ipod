import base64, json
t = open('/workspace/ipod-clone/build/template.html').read()
font = base64.b64encode(open('/usr/share/fonts/truetype/sand-box/google/Pixelify Sans/PixelifySans-VariableFont_wght.ttf','rb').read()).decode()
lib = json.load(open('/workspace/ipod-clone/build/library.json'))
t = t.replace('__FONT__', font).replace('__LIB__', json.dumps(lib, ensure_ascii=False).replace('</', '<\\/'))
open('/workspace/ipod-clone/index.html','w').write(t)
print('ok', len(t))
