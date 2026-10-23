# Builds data/library.json for the clone.
# Track list (playlist names/order, song ids, artist ids) comes from the reference page's index.json
# (path given by REF_INDEX; used only as a list of IDs). All metadata, preview URLs and artwork
# are resolved independently through the public iTunes lookup/search API.
import json, os, time, urllib.request, urllib.parse, sys
ref = json.load(open(os.environ.get('REF_INDEX', 'index.json')))
H = {'User-Agent': 'Mozilla/5.0'}
def get(path, params):
    url = 'https://itunes.apple.com/' + path + '?' + urllib.parse.urlencode(params)
    for a in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30) as r:
                return json.load(r).get('results', [])
        except Exception as e:
            print('retry', path, e, flush=True); time.sleep(15 * (a + 1))
    return []
song_ids = [s['id'] for s in ref['songs']]
artist_of = {s['id']: s['artistIds'] for s in ref['songs']}
found = {}
for i in range(0, len(song_ids), 150):
    batch = song_ids[i:i+150]
    for r in get('lookup', {'id': ','.join(batch), 'country': 'us', 'entity': 'song'}):
        if r.get('wrapperType') == 'track' and r.get('previewUrl'):
            found[str(r['trackId'])] = r
    print('lookup', i, len(found), flush=True); time.sleep(3.5)
missing = [s for s in ref['songs'] if s['id'] not in found]
print('missing after lookup', len(missing), flush=True)
for s in missing:   # fall back to a name search for tracks whose id no longer resolves
    res = get('search', {'term': s['artistName'] + ' ' + s['name'], 'entity': 'song', 'limit': 5, 'country': 'us'})
    res = [r for r in res if r.get('previewUrl') and r['trackName'].lower().startswith(s['name'].lower()[:10])]
    if res: found[s['id']] = res[0]; print('search ok', s['name'], flush=True)
    else: print('MISS', s['artistName'], '-', s['name'], flush=True)
    time.sleep(3.5)
songs = []
for sid in song_ids:
    r = found.get(sid)
    if not r: continue
    songs.append({'id': sid, 'name': r['trackName'], 'artist': r['artistName'], 'artistIds': artist_of[sid],
                  'album': r.get('collectionName', ''), 'art': r.get('artworkUrl100', ''), 'preview': r['previewUrl'],
                  'dur': r.get('trackTimeMillis', 0), 'explicit': r.get('trackExplicitness') == 'explicit'})
have = {s['id'] for s in songs}
# artist names resolved via lookup by artist id
aids = [a['id'] for a in ref['artists']]; aname = {}
for i in range(0, len(aids), 150):
    for r in get('lookup', {'id': ','.join(aids[i:i+150]), 'country': 'us'}):
        if r.get('wrapperType') == 'artist': aname[str(r['artistId'])] = r['artistName']
    time.sleep(3.5)
artists = []
for a in ref['artists']:
    ids = [x for x in a['songIds'] if x in have]
    if ids: artists.append({'id': a['id'], 'name': aname.get(a['id'], a['name']), 'songIds': ids})
playlists = [{'id': p['id'], 'name': p['name'], 'songIds': [x for x in p['songIds'] if x in have]} for p in ref['playlists']]
out = {'schema': 1, 'songs': songs, 'artists': artists, 'playlists': playlists}
json.dump(out, open('/workspace/ipod-clone/data/library.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('DONE songs', len(songs), 'artists', len(artists), [len(p['songIds']) for p in playlists], flush=True)
