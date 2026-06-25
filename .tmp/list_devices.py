import json, re
from collections import defaultdict

devices=[]
for p in range(1,12):
    with open(f'/Users/ciansullivan/code/aroya-reports/.tmp/devices_p{p}.json') as f:
        devices.extend(json.load(f)['results'])

def base(s):
    return re.sub(r'-\d+$','', s or '')

by_base={}
for d in devices:
    by_base.setdefault(base(d['serialNumber']), []).append(d)

# Offline base radios
offline=[]
for bs, es in by_base.items():
    if not any(e.get('online') for e in es):
        e=es[0]
        offline.append({
            'sn':bs,'model':e.get('modelKey'),'room':e.get('room'),
            'battery':e.get('battery'),'rssi':e.get('rssi'),
            'parent_id':e.get('nextHop'),'gateway':e.get('gateway')
        })
print('OFFLINE_RADIOS=', len(offline))
for o in offline: print(' OFF', o)

# Low battery
low_bat=[]
for bs, es in by_base.items():
    bat = min([(e.get('battery') or 100) for e in es])
    if bat is not None and bat<=20:
        low_bat.append((bs, bat, es[0].get('modelKey')))
print()
print('LOW_BATTERY (<=20%):')
for b in sorted(low_bat, key=lambda x: x[1]): print(' BAT', b)

# Identify each over-13 parent's room and total children
id_to_serial={e['id']:e['serialNumber'] for e in devices}
id_to_room={e['id']:e.get('room') for e in devices}
id_to_zone={e['id']:e.get('zone') for e in devices}
id_to_gw={e['id']:e.get('gateway') for e in devices}
children_of=defaultdict(list)
canon={}
for bs, es in by_base.items():
    canon[bs] = es[0]
    nh = es[0].get('nextHop')
    if nh is not None:
        children_of[nh].append(bs)

# For each over-13 parent, name it: 'sink of gateway H...'
gw_id_to_serial={e['id']:e['serialNumber'] for e in devices if e.get('modelKey')=='gateway'}

print()
print('OVER-13 DETAIL:')
for pid in [124661, 152539, 152549, 222826, 163832]:
    n = len(children_of.get(pid, []))
    psn = id_to_serial.get(pid, f'id{pid}')
    room = id_to_room.get(pid)
    gw = id_to_gw.get(pid)
    gw_sn = gw_id_to_serial.get(gw, gw)
    # Is this id itself a gateway? 
    is_gw = pid in gw_id_to_serial
    role = 'gateway' if is_gw else ('sink/hop-1' if gw==pid else 'relay')
    # The sink of a gateway typically has the same numbered serial e.g. parent id 124661 paired with gateway id 124662
    print(f'  id {pid} sn {psn} room {room} gw {gw_sn} ({gw}) n_children={n}')
