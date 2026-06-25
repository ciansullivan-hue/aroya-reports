#!/usr/bin/env python3
import json, sys, re, os
from collections import defaultdict, Counter

TMP='/Users/ciansullivan/code/aroya-reports/.tmp'
devices=[]
for p in range(1,12):
    with open(f'{TMP}/devices_p{p}.json') as f:
        d=json.load(f)
        devices.extend(d['results'])
print('TOTAL_RAW_DEVICES=', len(devices))

# Combined single JSON for archive
with open(f'{TMP}/powrhouse-devices-refresh.json','w') as f:
    json.dump({'count':len(devices),'results':devices,'pulled':'2026-06-24 12:57 PDT'}, f, indent=2)
print('WROTE combined JSON')

# Base-serial dedup: strip -N suffix
def base(s):
    if not s: return s
    return re.sub(r'-\d+$','', s)

by_base = {}  # base -> list of raw device entries
for d in devices:
    sn = d.get('serialNumber','')
    bs = base(sn)
    by_base.setdefault(bs, []).append(d)

print('UNIQUE_BASE_SERIALS=', len(by_base))
print('DASH2_PAIRS=', len(devices)-len(by_base))

# Pick a canonical representative per base (prefer the dash-less serial)
def pick_canon(entries):
    for e in entries:
        if '-' not in (e.get('serialNumber') or ''):
            return e
    return entries[0]

canon = {bs: pick_canon(es) for bs, es in by_base.items()}

# Build a serial-> base map and id-> base map for parent linking
id_to_base = {}
for bs, e in canon.items():
    id_to_base[e['id']] = bs

# Online by base: online if ANY of its variants is online
online_base = set()
for bs, es in by_base.items():
    if any(e.get('online') for e in es):
        online_base.add(bs)
print('UNIQUE_BASE_ONLINE=', len(online_base))

# Gateways
gateways = [e for e in devices if (e.get('modelKey')=='gateway') or (e.get('gateway') is None and e.get('nextHop') is None and (e.get('serialNumber','').startswith('H2100')))]
# Actually use modelKey or model_key
gateways = [e for e in devices if e.get('modelKey')=='gateway']
print('GATEWAYS=', len(gateways))
for g in gateways:
    print(' GW:', g['serialNumber'], 'id', g['id'], 'online', g.get('online'), 'gg', g.get('ggVersion'))

# nextHop = id of parent device. Count direct children (per immediate parent), base-serial deduped
children_of = defaultdict(set)  # parent_id -> set of child base serials
for bs, e in canon.items():
    nh = e.get('nextHop')
    if nh is not None:
        children_of[nh].add(bs)

# Map parent id -> serial for readability
id_to_serial = {e['id']: e.get('serialNumber') for e in devices}

# Saturation report
parent_stats = []
for pid, kids in children_of.items():
    psn = id_to_serial.get(pid, f'id{pid}')
    parent_stats.append((psn, pid, len(kids)))

parent_stats.sort(key=lambda x:-x[2])
print()
print('PARENT_SATURATION (top 20):')
for psn, pid, n in parent_stats[:20]:
    tier = '🔴🔴' if n>13 else ('🔴' if n==13 else ('🟠' if n>=11 else '🟢'))
    print(f'  {tier} {psn} (id {pid}) — {n} children')

# Aggregates
over13 = [(s,p,n) for s,p,n in parent_stats if n>13]
at13 = [(s,p,n) for s,p,n in parent_stats if n==13]
watch = [(s,p,n) for s,p,n in parent_stats if 11<=n<=12]
excess = sum(n-13 for _,_,n in over13)
print()
print(f'OVER13={len(over13)} AT13={len(at13)} WATCH(11-12)={len(watch)} EXCESS={excess}')
print(f'ONLINE_PCT={100.0*len(online_base)/len(by_base):.1f}%')

# Per-gateway summary
gw_summary=[]
# Direct children of gateway: those whose nextHop == gateway.id
for g in gateways:
    gid = g['id']
    gsn = g['serialNumber']
    hop1 = children_of.get(gid, set())
    # Total routing: all base serials whose route eventually goes to this gateway
    # Approximation: those with gateway field == gid
    route_total = set()
    for bs, e in canon.items():
        if e.get('gateway')==gid:
            route_total.add(bs)
    route_online = sum(1 for bs in route_total if bs in online_base)
    gw_summary.append({
        'serial': gsn, 'id': gid, 'online': g.get('online'),
        'gg': g.get('ggVersion'),
        'hop1': len(hop1),
        'route_total': len(route_total),
        'route_online': route_online,
    })

print()
print('PER-GATEWAY:')
for g in gw_summary:
    print(' ', g)

# Dump summary
summary = {
    'pulled_ts': '2026-06-24 12:57 PDT',
    'raw_serials': len(devices),
    'unique_radios': len(by_base),
    'dash2_pairs': len(devices)-len(by_base),
    'online_radios': len(online_base),
    'online_pct': round(100.0*len(online_base)/len(by_base),1),
    'gateways_total': len(gateways),
    'gateways_online': sum(1 for g in gateways if g.get('online')),
    'over13_count': len(over13),
    'at13_count': len(at13),
    'watch_count': len(watch),
    'excess_children': excess,
    'over13_parents': [{'serial': s, 'id':p, 'children': n, 'excess': n-13} for s,p,n in over13],
    'watch_parents': [{'serial': s, 'id':p, 'children': n} for s,p,n in watch],
    'at13_parents': [{'serial': s, 'id':p, 'children': n} for s,p,n in at13],
    'top_parents': [{'serial': s, 'id':p, 'children': n} for s,p,n in parent_stats[:25]],
    'per_gateway': gw_summary,
}
with open(f'{TMP}/mesh_summary.json','w') as f:
    json.dump(summary, f, indent=2)
print()
print('WROTE mesh_summary.json')
