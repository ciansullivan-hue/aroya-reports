import json, re
from collections import defaultdict, Counter

devices=[]
for p in range(1,12):
    with open(f'/Users/ciansullivan/code/aroya-reports/.tmp/devices_p{p}.json') as f:
        devices.extend(json.load(f)['results'])

def base(s):
    return re.sub(r'-\d+$','', s or '')

by_base={}
for d in devices:
    by_base.setdefault(base(d['serialNumber']), []).append(d)

# Per room: base radios, online
room_stats=defaultdict(lambda: {'total':0,'online':0,'serials':[]})
for bs, es in by_base.items():
    e=es[0]
    r=e.get('room')
    key=r if r else 'unassigned'
    room_stats[key]['total']+=1
    if any(x.get('online') for x in es):
        room_stats[key]['online']+=1
    room_stats[key]['serials'].append(bs)
print('PER_ROOM:')
for r,v in sorted(room_stats.items(), key=lambda x: (str(x[0]))):
    print(f'  room {r}: {v["online"]}/{v["total"]} online')

# Sample serials from gateway H2200001033 = id 222827 - to confirm growth
gw_serial_to_id = {'H2100004676':124662,'H2100005242':152540,'H2100005246':152550,'H2200001033':222827}
print()
print('Gateway H2200001033 tree (id 222827):')
under_222827=[]
for bs, es in by_base.items():
    e=es[0]
    if e.get('gateway')==222827:
        under_222827.append((bs, e.get('online'), e.get('nextHop'), e.get('modelKey'), e.get('room')))
print(f'  total in tree: {len(under_222827)}; online: {sum(1 for x in under_222827 if x[1])}')

# Also look at gateway H2100005246 tree change
print()
print('Gateway H2100005246 tree (id 152550):')
under_152550=[]
for bs, es in by_base.items():
    e=es[0]
    if e.get('gateway')==152550:
        under_152550.append(bs)
print(f'  total in tree: {len(under_152550)}; online: {sum(1 for bs in under_152550 if any(x.get("online") for x in by_base[bs]))}')

# And gateway H2100004676 tree
print()
print('Gateway H2100004676 tree (id 124662):')
under_124662=[]
for bs, es in by_base.items():
    e=es[0]
    if e.get('gateway')==124662:
        under_124662.append(bs)
print(f'  total in tree: {len(under_124662)}; online: {sum(1 for bs in under_124662 if any(x.get("online") for x in by_base[bs]))}')

print()
print('Gateway H2100005242 tree (id 152540):')
under_152540=[]
for bs, es in by_base.items():
    e=es[0]
    if e.get('gateway')==152540:
        under_152540.append(bs)
print(f'  total in tree: {len(under_152540)}; online: {sum(1 for bs in under_152540 if any(x.get("online") for x in by_base[bs]))}')

# Check WATCH parent H4210003243 (id 163832) - find its 11 children
print()
print('Watch parent H4210003243 (id 163832) children:')
kids=[]
for bs, es in by_base.items():
    if es[0].get('nextHop')==163832:
        kids.append((bs, es[0].get('online'), es[0].get('modelKey'), es[0].get('room')))
for k in kids: print(' ',k)

# New radios since morning (152 -> 153). Hard to know exactly without morning serial list. Just list all 153.
all_serials = sorted(by_base.keys())
with open('/Users/ciansullivan/code/aroya-reports/.tmp/all_unique_serials.txt','w') as f:
    for s in all_serials:
        e=by_base[s][0]
        f.write(f'{s}\t{e.get("modelKey")}\t{e.get("room")}\t{e.get("gateway")}\t{1 if any(x.get("online") for x in by_base[s]) else 0}\n')
print()
print(f'Wrote {len(all_serials)} unique serials list')
