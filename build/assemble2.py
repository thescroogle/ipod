import json, base64, os, shutil
B = os.path.dirname(os.path.abspath(__file__))
font = base64.b64encode(open('/usr/share/fonts/truetype/sand-box/google/Pixelify Sans/PixelifySans-VariableFont_wght.ttf','rb').read()).decode()
css = open(f'{B}/base.css').read() + open(f'{B}/extra.css').read()
tpl = open(f'{B}/app.html').read().replace('__CSS__', css).replace('__FONT__', font)
LIBP = f'{B}/library_full.json' if os.path.exists(f'{B}/library_full.json') else f'{B}/../data/library.json'
lib = json.load(open(LIBP))
OUT = os.environ.get('OUT', f'{B}/../dist')

def song(s, src=None):
    o = {k: s[k] for k in ('id','name','artist','album','art','preview','dur','explicit')}
    o['art'] = o['art'].replace('100x100bb', '600x600bb'); o['src'] = src
    return o

def write(outdir, title, theme, playlists, extra_songs=(), pinned=()):
    os.makedirs(outdir, exist_ok=True)
    byid = {s['id']: s for s in lib['songs']}
    ids = []
    for p in playlists:
        for i in p['songIds']:
            if i not in ids: ids.append(i)
    songs = list(extra_songs) + [song(byid[i]) for i in ids if i in byid]
    have = {s['id'] for s in songs}
    artists = list(pinned) + [{'id': a['id'], 'name': a['name'], 'songIds': [i for i in a['songIds'] if i in have]} for a in lib['artists']]
    artists = [a for a in artists if a['songIds']]
    data = {'schema': 2, 'theme': theme, 'playlists': playlists, 'artists': artists, 'songs': songs}
    json.dump(data, open(f'{outdir}/songs.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    open(f'{outdir}/index.html', 'w').write(tpl.replace('__TITLE__', title))
    print(outdir, len(songs), 'songs', len(artists), 'artists', [p['name'] for p in playlists])

# --- public GitHub Pages build: the full reference library
write(OUT, 'Pod', {'background': '#161617'}, lib['playlists'])

# --- Aulani build (optional; needs an iTunes artist lookup saved at AULANI_LOOKUP)
AL = os.environ.get('AULANI_LOOKUP', '/tmp/aul_lookup.json')
if not os.path.exists(AL): raise SystemExit(0)
al = json.load(open(AL))['results']
tracks = sorted([r for r in al if r.get('wrapperType') == 'track'], key=lambda r: r['releaseDate'], reverse=True)
aul = [{'id': str(r['trackId']), 'name': r['trackName'], 'artist': r['artistName'], 'album': r['collectionName'],
        'art': r['artworkUrl100'].replace('100x100bb', '600x600bb'), 'preview': r['previewUrl'], 'dur': r['trackTimeMillis'],
        'explicit': r['trackExplicitness'] == 'explicit', 'src': None, 'released': r['releaseDate'][:10],
        'genre': r['primaryGenreName'], 'appleMusic': r['trackViewUrl'].split('?')[0]} for r in tracks]
hits = [p for p in lib['playlists'] if p['name'].endswith('Hits: 2001')]
pls = [{'id': 'aulani', 'name': 'Aulani Design Lab', 'songIds': [s['id'] for s in aul]}] + hits
write('/workspace/ipod-aulani', 'Aulani Design Lab \u2014 Pod', {'background': '#0B0B0C', 'accent': '#D4A574', 'label': 'Aulani Design Lab', 'title': 'Aulani Design Lab \u2014 Pod'},
      pls, aul, [{'id': '1738602198', 'name': 'Aulani Design Lab', 'pinned': True, 'songIds': [s['id'] for s in aul]}])
