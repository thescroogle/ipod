# Builds our own library data from the public iTunes Search API (no key).
import json, time, urllib.request, urllib.parse, re, sys
PL = json.load(open('/workspace/ipod-clone/build/playlists.json'))
def norm(s): return re.sub(r'[^a-z0-9]', '', s.lower().replace('&','and'))
def search(term):
    url = 'https://itunes.apple.com/search?' + urllib.parse.urlencode({'term':term,'entity':'song','limit':10,'country':'us'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=20) as r:
                return json.load(r).get('results', [])
        except Exception as e:
            print('retry', term, e, file=sys.stderr); time.sleep(10*(attempt+1))
    return []
songs, playlists = {}, []
for name, items in PL.items():
    ids = []
    for artist, title in items:
        res = [x for x in search(f'{artist} {title}') if x.get('previewUrl')]
        na, nt = norm(artist), norm(title)
        def score(x):
            s = 0
            if na[:6] in norm(x['artistName']): s += 2
            t = norm(x['trackName'])
            if t == nt: s += 3
            elif nt[:8] in t: s += 1
            if 'karaoke' in x['artistName'].lower() or 'tribute' in x.get('collectionName','').lower(): s -= 5
            if 'live' in x['trackName'].lower(): s -= 1
            return s
        res.sort(key=score, reverse=True)
        if res and score(res[0]) >= 3:
            x = res[0]; tid = str(x['trackId'])
            songs[tid] = {'id':tid,'name':x['trackName'],'artist':x['artistName'],'album':x['collectionName'],
                          'art':x.get('artworkUrl100',''),'preview':x['previewUrl'],'dur':x.get('trackTimeMillis',30000),'year':x.get('releaseDate','')[:4]}
            ids.append(tid); print('OK ', name, '|', x['artistName'], '-', x['trackName'])
        else:
            print('MISS', name, artist, title)
        time.sleep(3.2)
    playlists.append({'name':name,'songIds':ids})
json.dump({'songs':list(songs.values()),'playlists':playlists}, open('/workspace/ipod-clone/build/library.json','w'), ensure_ascii=False)
print('DONE', len(songs))
