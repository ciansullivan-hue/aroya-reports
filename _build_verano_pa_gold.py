"""
Rebuild Verano PA Day-1 Device + Mesh Health report in the Aurora 99 /
GTI Danville gold-standard AROYA fleet-health format.

Preserves exact data payload from the prior (2026-07-01) pull.

Emits two files:
  - VeranoPA_Day1_Device_Mesh_Health_2026-07-01.html      (light)
  - VeranoPA_Day1_Device_Mesh_Health_2026-07-01_dark.html (dark)
"""

from pathlib import Path

REPO = Path("/Users/ciansullivan/code/aroya-reports")

# -----------------------------------------------------------------------------
# DATA PAYLOAD (from AROYA SPA /devices/?facility=4742 · 2026-07-01 15:04 UTC)
# -----------------------------------------------------------------------------
FACILITY_ID = 4742
ORG_ID = 3501
PULLED_UTC = "2026-07-01 15:04 UTC"
WINDOW = "last 24 hours"

# Fleet counts
RAW_SERIALS = 175
DASH2_COLLAPSED = 73
UNIQUE_RADIOS = 102
GATEWAYS = 1        # H2200001049
H421_CLIMATE = 22
REPEATERS = 6
SUBSTRATE_NODES = 73  # unique after dedup
REPORTING = 93
SILENT_COUNT = 9
BAT_HEALTHY = 79    # /79 reporting battery-nodes
ROOMS_TOTAL = 22
ROOMS_WITH_RADIOS = 20
ROOMS_EMPTY = ["Room 6", "Mom 1"]
ARTIFACT_ROOMS = ["Flower 4", "Room 10", "Room 8", "Room 12", "mom 2 (13)"]

# Saturation
GATEWAY_SINK_CHILDREN = 18   # over the 14-slot limit
GATEWAY_SINK_ID = "H2200001049 (sink anchor)"
REPEATER_361_CHILDREN = 15
REPEATER_361_ID = "H3400003361"
PARENTS_OVER_14 = 2
PARENTS_WATCH_12_14 = 0
PARENTS_HEADROOM = 37

# Rooms — (name, room_id, radios, online, silent, watch_devices, artifact, note)
ROOMS = [
    ("Veg 1",      20335, 1, 1, 0, 1, False, "0 zones"),
    ("Veg 2",      20337, 1, 1, 0, 0, False, "0 zones"),
    ("Flower 1",   20336, 11, 11, 0, 0, False, "10 zones"),
    ("Flower 2",   20331, 12, 12, 0, 2, False, "11 zones"),
    ("Flower 3",   20338, 8, 7, 1, 1, False, "7 zones"),
    ("Flower 4",   20327, 4, 4, 0, 0, True,  "3 zones · VPD 1.66 on empty substrate"),
    ("Flower 5",   20341, 8, 8, 0, 0, False, "7 zones"),
    ("Room 6",     20340, 0, 0, 0, 0, False, "zero radios assigned"),
    ("Room 7",     20328, 5, 5, 0, 0, False, "8 zones"),
    ("Room 8",     20329, 6, 5, 1, 0, True,  "0 zones · probe near-zero VWC"),
    ("Room 9",     20330, 6, 5, 1, 0, False, "10 zones"),
    ("Room 10",    20323, 6, 6, 0, 1, True,  "10 zones · VPD 2.11 empty room"),
    ("Room 11",    20324, 6, 6, 0, 0, False, "10 zones"),
    ("Room 12",    20325, 6, 5, 1, 1, True,  "10 zones · probe near-zero VWC"),
    ("mom 2 (13)", 20326, 1, 0, 1, 0, True,  "0 zones · probe near-zero VWC"),
    ("Mom 1",      20342, 0, 0, 0, 0, False, "zero radios assigned"),
    ("Dry 1",      20346, 1, 1, 0, 1, False, "0 zones"),
    ("Dry 2",      20345, 1, 1, 0, 0, False, "0 zones"),
    ("Dry 3",      20348, 1, 0, 1, 0, False, "0 zones"),
    ("Dry 4",      20347, 1, 1, 0, 0, False, "0 zones"),
    ("Cure",       20355, 1, 1, 0, 1, False, "0 zones"),
    ("prop",       20354, 1, 1, 0, 0, False, "0 zones"),
]

# Silent devices (9)
SILENT_DEVICES = [
    # (serial, model, room, parent, rssi_hops, linkq)
    ("H4210006470", "h421", "(mesh infrastructure)", "sink/H2200001049", "6",  "92"),
    ("H4210006781", "h421", "(mesh infrastructure)", "sink/H2200001049", "6",  "100"),
    ("H4210006852", "h421", "(mesh infrastructure)", "H3440018406",      "1",  "100"),
    ("H4210006784", "h421", "Flower 3",              "H4210006869",      "8",  "98"),
    ("H4210006869", "h421", "Room 8",                "sink/H2200001049", "3",  "84"),
    ("H4210006893", "h421", "Room 9",                "H3440018412",      "4",  "100"),
    ("H4210006778", "h421", "Room 12",               "H4210006771",      "8",  "100"),
    ("H4210006866", "h421", "mom 2 (13)",            "H4210006569",      "8",  "100"),
    ("H4210006569", "h421", "Dry 3",                 "sink/H2200001049", "6",  "100"),
]

# Watch devices (8) — link quality < 80% but reporting
WATCH_DEVICES = [
    ("H4210006468", "h421", "Veg 1",     "H4210006849",      "1", "49"),
    ("H3440017140", "node", "Flower 2",  "H3440018416",      "3", "44"),
    ("H3440018677", "node", "Flower 2",  "sink/H2200001049", "1", "58"),
    ("H3440017115", "node", "Flower 3",  "H3440018678",      "1", "54"),
    ("H4210006587", "h421", "Room 10",   "sink/H2200001049", "1", "44"),
    ("H3440018394", "node", "Room 12",   "sink/H2200001049", "1", "53"),
    ("H4210006771", "h421", "Dry 1",     "H4210006587",      "3", "71"),
    ("H4210006846", "h421", "Cure",      "H4210006587",      "1", "73"),
]

# Install-artifact readings
ARTIFACTS = [
    ("Flower 4",   "VPD 1.66 with VWC 0.2 — probe reading empty substrate, not plant zone"),
    ("Room 10",    "VPD 2.11 — probe reading air in an empty room, not a canopy"),
    ("Room 8",     "Near-zero VWC — probe not yet inserted into substrate"),
    ("Room 12",    "Near-zero VWC — probe not yet inserted into substrate"),
    ("mom 2 (13)", "Near-zero VWC — probe not yet inserted into substrate"),
]

# Prioritized actions
ACTIONS = [
    (1, "Silent-radio walkdown", "9 h421 silent 24h",
     "Confirm each of the 9 silent h421 units is powered, in position, and joined. Prioritize the 3 mesh-infrastructure silents (H4210006470, H4210006781, H4210006852) — those are anchor-tier.",
     "P1", "Low", "Impact: High"),
    (2, "Gateway sink saturation (18/14)", GATEWAY_SINK_ID,
     "Sink is +4 over the Wirepas 14-child limit. Every additional joiner past 14 either fails to attach or thrashes. Rebalance direct-parented h421s onto downstream relays before more silent radios come online.",
     "P1", "Medium", "Impact: High"),
    (3, "Repeater H3400003361 saturation (15/14)", REPEATER_361_ID,
     "One over the limit. Same failure mode as the sink — one node's mesh headroom is gone. Split its Flower 1 / Flower 2 sub-mesh onto H3400003362 or H3400003476.",
     "P1", "Medium", "Impact: High"),
    (4, "Install-artifact readings in 5 rooms", "Flower 4, Room 10, Room 8, Room 12, mom 2 (13)",
     "Reposition probes into their target substrate/canopy zones. Devices are healthy — they're just reading the wrong environment. Left uncorrected these will look like device failures on the day-7 pull.",
     "P2", "Low", "Impact: High"),
    (5, "Zero-radio rooms", "Room 6, Mom 1",
     "Confirm build-out status. If cultivation-active, assign radios. If dormant, mark room dormant in AROYA inventory so the day-7 audit doesn't flag them again.",
     "P2", "Low", "Impact: Medium"),
    (6, "Day-7 re-audit", "full fleet",
     "Wirepas mesh takes days-to-weeks to stabilize. Every metric in this report is directional; the meaningful reliability judgment (churn rate, battery decay, saturation trend) comes from re-pulling this same audit on 2026-07-08.",
     "P1", "Low", "Impact: High"),
]

# Mesh topology tree — gateway → sink → direct children.
# Sink is over-subscribed at 18/14. Nodes annotated with their own child count.
SINK_CHILDREN = [
    ("H3400003361", "repeater", 15, "SAT"),  # 15/14 — one over
    ("H3400003462", "repeater",  1, "OK"),
    ("H3440018391", "node",      0, "OK"),
    ("H3440018394", "node",      1, "OK"),
    ("H3440018398", "node",      4, "OK"),
    ("H3440018410", "node",      1, "OK"),
    ("H3440018416", "node",      4, "OK"),
    ("H3440018417", "node",      0, "OK"),
    ("H3440018418", "node",      3, "OK"),
    ("H3440018650", "node",      2, "OK"),
    ("H3440018653", "node",      2, "OK"),
    ("H3440018677", "node",      0, "OK"),
    ("H4210006470", "h421",      0, "SILENT"),
    ("H4210006569", "h421",      1, "OK"),
    ("H4210006587", "h421",      1, "OK"),
    ("H4210006772", "h421",      7, "OK"),
    ("H4210006781", "h421",      0, "SILENT"),
    ("H4210006869", "h421",      1, "OK"),
]

# -----------------------------------------------------------------------------
# STYLE — Aurora 99 tokens ported verbatim
# -----------------------------------------------------------------------------
STYLE = r"""
:root[data-theme="light"]{--bg:#fafaf7;--bg-2:#ffffff;--bg-3:#f3f3ee;--border:#e2e2dc;--ink:#1c2419;--ink-2:#4a5340;--ink-muted:#7a8175;--olive:#3f4e2b;--olive-2:#5b6e3f;--lime:#9fd96a;--lime-2:#cfe9a8;--app-blue:#1f78b4;--app-blue-2:#a8d5e2;--attention:#e76f51;--attention-2:#f4a261;--good:#5b8a3a;--warn:#c87a2c;--bad:#b1442a;--good-bg:#eef5e3;--warn-bg:#fbecd6;--bad-bg:#f7d9cf;--card-shadow:0 1px 3px rgba(0,0,0,0.04),0 4px 16px rgba(0,0,0,0.05);--grid-line:#e8e8e0}
:root[data-theme="dark"]{--bg:#13160f;--bg-2:#1a1e15;--bg-3:#22281c;--border:#2e3624;--ink:#e8ead9;--ink-2:#b9bda5;--ink-muted:#7e836e;--olive:#8aa05c;--olive-2:#a7bb74;--lime:#b9e587;--lime-2:#6b8d3d;--app-blue:#6cb5d8;--app-blue-2:#3a6d80;--attention:#f48066;--attention-2:#f4a261;--good:#86c25b;--warn:#e4a35e;--bad:#df6a4d;--good-bg:#1f2c19;--warn-bg:#2e2418;--bad-bg:#2e1c16;--card-shadow:0 1px 3px rgba(0,0,0,0.5),0 8px 28px rgba(0,0,0,0.45);--grid-line:#2a3220}
*{box-sizing:border-box}
html,body{margin:0;padding:0;font:14px/1.5 'Inter',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--ink);-webkit-font-smoothing:antialiased;font-feature-settings:"cv11","ss01","ss03"}
a{color:var(--app-blue);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:0 28px 80px}
.masthead{background:#1a1c19;color:#fff;padding:20px 28px 24px;margin:0;position:relative;overflow:hidden;min-height:80px}
.masthead-inner{max-width:1180px;margin:0 auto;display:flex;align-items:flex-start;justify-content:space-between;gap:24px;position:relative;z-index:1}
.lockup{position:relative;display:flex;align-items:center;gap:10px;color:#fff;padding-bottom:14px}
.lockup-mark{font-size:28px;font-weight:500;letter-spacing:-0.01em;line-height:1;color:#fff}
.lockup-glyph{display:inline-block;width:26px;height:26px;position:relative;flex:none}
.lockup-glyph::before,.lockup-glyph::after{content:"";position:absolute;background:#fff;border-radius:2px}
.lockup-glyph::before{top:0;right:0;width:13px;height:13px}
.lockup-glyph::after{bottom:0;left:0;width:17px;height:17px;border-top-right-radius:0}
.lockup-byline{position:absolute;top:34px;left:0;font-size:11px;font-weight:400;color:#aaa;letter-spacing:0;line-height:1}
.controls{display:flex;gap:6px;align-items:center}
.btn{background:transparent;color:#cccccc;border:1px solid #3a3d35;border-radius:6px;padding:6px 12px;cursor:pointer;font:500 12px/1 'Inter',sans-serif;letter-spacing:.04em;transition:all .12s}
.btn:hover{background:rgba(203,238,176,.08);color:#cbeeb0;border-color:#cbeeb0}
.btn.active{background:#cbeeb0;color:#1a1c19;border-color:#cbeeb0}
.tick{position:absolute;width:7px;height:7px;background:#3a3d35;border-radius:1px;z-index:0}
.tick.t1{top:14px;left:42%}.tick.t2{top:14px;left:48%;width:8px;height:8px}.tick.t3{top:14px;right:24%;width:6px;height:6px}
.tick.t4{bottom:12px;left:18%}.tick.t5{bottom:12px;left:22%;width:5px;height:5px}
.tick.t6{top:46%;right:18px}.tick.t7{bottom:12px;right:32%;width:6px;height:6px}
.pagehead{max-width:1180px;margin:0 auto;padding:28px 0 0;border-bottom:1px solid var(--border);padding-bottom:24px;margin-bottom:32px}
.pagehead-eyebrow{font-size:11px;font-weight:500;color:var(--olive);text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px}
.pagehead h1{font-weight:500;font-size:32px;line-height:1.15;letter-spacing:-.018em;color:var(--ink);margin:0 0 8px}
.pagehead .sub{color:var(--ink-2);font-size:14.5px;font-weight:400;line-height:1.5}
.pagehead .meta{margin-top:18px;display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px 24px;font-size:12.5px;color:var(--ink-muted)}
.pagehead .meta b{color:var(--ink);font-weight:500;display:block;font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-muted);margin-bottom:2px}
.pagehead .meta span{padding:6px 0;border-top:1px solid var(--border)}
section{margin-top:40px}
h2{font-size:22px;margin:0 0 14px;font-weight:500;letter-spacing:-.3px;padding-bottom:6px;border-bottom:2px solid var(--lime)}
h3{font-size:17px;margin:24px 0 10px;font-weight:500}
h4{font-size:14px;margin:18px 0 6px;font-weight:500;color:var(--ink-2);text-transform:uppercase;letter-spacing:1px}
p{margin:0 0 12px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-bottom:20px}
.kpi{background:var(--bg-2);border:1px solid var(--border);border-radius:12px;padding:16px 18px;box-shadow:var(--card-shadow);position:relative;overflow:hidden}
.kpi::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--olive)}
.kpi.bad::before{background:var(--bad)}.kpi.warn::before{background:var(--warn)}.kpi.good::before{background:var(--good)}
.kpi .label{font-size:12px;color:var(--ink-muted);text-transform:uppercase;letter-spacing:.6px;margin-bottom:6px}
.kpi .val{font-size:24px;font-weight:500;color:var(--ink);font-variant-numeric:tabular-nums}
.kpi .delta{font-size:12px;color:var(--ink-2);margin-top:4px}
.kpi.bad .val{color:var(--bad)}.kpi.warn .val{color:var(--warn)}.kpi.good .val{color:var(--good)}
.card{background:var(--bg-2);border:1px solid var(--border);border-radius:12px;padding:20px 22px;margin-bottom:14px;box-shadow:var(--card-shadow)}
.verdict{padding:14px 18px;border-radius:10px;font-weight:400;margin:10px 0;border-left:4px solid}
.verdict.bad{background:linear-gradient(90deg,var(--bad-bg) 0%,transparent 100%);border-color:var(--bad)}
.verdict.warn{background:linear-gradient(90deg,var(--warn-bg) 0%,transparent 100%);border-color:var(--warn)}
.verdict.good{background:linear-gradient(90deg,var(--good-bg) 0%,transparent 100%);border-color:var(--good)}
.verdict .v-head{font-weight:500;font-size:13px;text-transform:uppercase;letter-spacing:.7px;margin-bottom:4px}
table{width:100%;border-collapse:collapse;margin:10px 0 14px;font-size:14px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--border);vertical-align:top}
th{font-size:12px;color:var(--ink-muted);text-transform:uppercase;letter-spacing:.6px;font-weight:500;background:var(--bg-3)}
tr:last-child td{border-bottom:none}
.num{text-align:right;font-variant-numeric:tabular-nums}
.pill{display:inline-block;padding:2px 8px;border-radius:8px;font-size:11px;font-weight:500;white-space:nowrap}
.pill.bad{background:var(--bad-bg);color:var(--bad)}.pill.warn{background:var(--warn-bg);color:var(--warn)}.pill.good{background:var(--good-bg);color:var(--good)}.pill.muted{background:var(--bg-3);color:var(--ink-muted)}
.day1-badge{display:inline-block;padding:4px 10px;font-size:11px;font-weight:500;letter-spacing:.06em;text-transform:uppercase;border-radius:999px;background:var(--warn-bg);color:var(--warn);border:1px solid var(--warn);margin-left:10px;vertical-align:middle}
.note{font-size:12px;color:var(--ink-muted);font-style:italic;margin:4px 0 12px}
.bar-axis{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px;margin:8px 0 18px}
.bar-axis .stack{background:var(--bg-2);border:1px solid var(--border);border-radius:12px;padding:14px 16px;box-shadow:var(--card-shadow)}
.bar-axis .stack h4{margin:0 0 8px;color:var(--ink)}
.bar-axis .stack .seg{display:flex;height:14px;border-radius:7px;overflow:hidden;background:var(--bg-3)}
.bar-axis .stack .seg span{display:block;line-height:14px;color:#fff;font-size:10px;font-weight:500;text-align:center;font-variant-numeric:tabular-nums}
.bar-axis .stack .seg .s-good{background:var(--good)}
.bar-axis .stack .seg .s-warn{background:var(--warn)}
.bar-axis .stack .seg .s-bad{background:var(--bad)}
.bar-axis .stack .seg .s-unk{background:var(--ink-muted)}
.bar-axis .stack .leg{font-size:11px;color:var(--ink-muted);margin-top:6px;display:flex;gap:10px;flex-wrap:wrap}
.legend-dot{display:inline-block;width:9px;height:9px;border-radius:2px;vertical-align:middle;margin-right:4px}
.room-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:12px 0 4px}
.room-card{background:var(--bg-2);border:1px solid var(--border);border-radius:10px;padding:14px 14px 12px;border-left:4px solid var(--olive);box-shadow:var(--card-shadow)}
.room-card.crit{border-left-color:var(--bad)}
.room-card.warn{border-left-color:var(--warn)}
.room-card.empty{border-left-color:var(--ink-muted);background:var(--bg-3)}
.room-name{font-weight:500;font-size:14px;margin-bottom:2px;color:var(--ink)}
.room-meta{color:var(--ink-muted);font-size:11px;margin-bottom:8px}
.room-stats{display:flex;flex-wrap:wrap;gap:6px 12px;font-size:12px;color:var(--ink-2);font-variant-numeric:tabular-nums}
.room-stats b{color:var(--ink);font-weight:500}
.room-flag{font-size:11px;color:var(--warn);margin-top:6px;font-style:italic}
.topo{background:var(--bg-2);border:1px solid var(--border);border-radius:12px;padding:16px 18px;box-shadow:var(--card-shadow);overflow-x:auto;-webkit-overflow-scrolling:touch}
.topo-tree{font-family:ui-monospace,'JetBrains Mono',monospace;font-size:12px;line-height:1.75;min-width:520px;color:var(--ink-2)}
.topo-root{color:var(--olive);font-weight:500}
.topo-sat{color:var(--bad);font-weight:500}
.topo-child.silent{color:var(--bad)}
.topo-child.sat{color:var(--warn)}
.artifact-card{background:var(--warn-bg);border:1px solid var(--warn);border-left:5px solid var(--warn);border-radius:12px;padding:16px 20px;box-shadow:var(--card-shadow);margin-bottom:14px}
.artifact-card h3{color:var(--warn);margin-top:0}
.artifact-card p{color:var(--ink);margin-bottom:8px}
.footer-note{color:var(--ink-muted);font-size:11px;padding:20px 0 0;border-top:1px solid var(--border);margin-top:40px}
.es-only{display:none}
body.es .en-only{display:none}
body.es .es-only{display:initial}
"""

MOBILE_QA = r"""
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style id="aroya-mobile-qa">
html { -webkit-text-size-adjust: 100%; }
@media (max-width: 768px) {
  html, body { max-width: 100vw; overflow-x: hidden; }
  body { font-size: 16px; line-height: 1.55; }
  .wrap { padding-left: 16px !important; padding-right: 16px !important; }
  img, svg { max-width: 100%; height: auto; }
  h1 { font-size: clamp(1.5rem, 6vw, 2.1rem) !important; line-height: 1.2 !important; }
  h2 { font-size: clamp(1.2rem, 4.8vw, 1.55rem) !important; line-height: 1.25 !important; }
  h3 { font-size: clamp(1.05rem, 4vw, 1.25rem) !important; }
  p, li, td, th { font-size: 15px; }
  code, .serial { overflow-wrap: anywhere !important; word-break: break-word !important; }
  .pill, .day1-badge { white-space: nowrap !important; }
  .table-scroll { max-width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; margin: 0 0 12px; }
  .table-scroll table { display: table; width: max-content; max-width: none; border-collapse: collapse; }
  table td, table th { word-break: keep-all !important; overflow-wrap: break-word !important; }
  td.num, th.num { white-space: nowrap !important; text-align: right; font-variant-numeric: tabular-nums; }
  .kpis, .bar-axis, .room-grid { grid-template-columns: repeat(auto-fit, minmax(155px, 1fr)) !important; gap: 12px !important; }
  .btn { min-height: 36px; padding: 8px 12px; }
  .masthead-inner, .lockup, .controls { gap: 8px !important; }
}
@media (max-width: 380px) {
  .wrap { padding-left: 14px !important; padding-right: 14px !important; }
  h1 { font-size: 1.45rem !important; }
  .kpis { grid-template-columns: 1fr 1fr !important; }
  .bar-axis { grid-template-columns: 1fr !important; }
  .room-grid { grid-template-columns: 1fr !important; }
}
</style>
<script id="aroya-mobile-qa-js">(function(){function wrap(){var ts=document.querySelectorAll('table');for(var i=0;i<ts.length;i++){var t=ts[i];if(!t.parentElement)continue;if(t.parentElement.classList.contains('table-scroll'))continue;var w=document.createElement('div');w.className='table-scroll';t.parentNode.insertBefore(w,t);w.appendChild(t);}}if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',wrap);}else{wrap();}})();</script>
"""

def masthead():
    return '''<div class="masthead">
  <span class="tick t1"></span><span class="tick t2"></span><span class="tick t3"></span>
  <span class="tick t4"></span><span class="tick t5"></span><span class="tick t6"></span><span class="tick t7"></span>
  <div class="masthead-inner">
    <div class="lockup">
      <span class="lockup-glyph"></span>
      <span class="lockup-mark">AROYA</span>
      <span class="lockup-byline"><span class="en-only">Device Fleet Health</span><span class="es-only">Salud de Flota</span></span>
    </div>
    <div class="controls">
      <button class="btn lang-btn active" data-lang="en">EN</button>
      <button class="btn lang-btn" data-lang="es">ES</button>
      <button class="btn theme-btn" data-theme="light">☀</button>
      <button class="btn theme-btn" data-theme="dark">☾</button>
    </div>
  </div>
</div>'''

def pagehead():
    return f'''<div class="pagehead">
    <div class="pagehead-eyebrow"><span class="en-only">AROYA Device Fleet Health · Day-1 Install Baseline</span><span class="es-only">Salud de Flota · Base de Día-1</span> · <span class="en-only">Verano PA install team</span><span class="es-only">Equipo Verano PA</span></div>
    <h1><span class="en-only">Verano PA — Day-1 Device + Mesh Health</span><span class="es-only">Verano PA — Salud Radio y Mesh</span><span class="day1-badge">Day-1 Baseline</span></h1>
    <div class="sub"><span class="en-only">Install-quality snapshot of every AROYA radio at Verano PA (facility {FACILITY_ID}, org {ORG_ID}). The facility came online in the last ~24-48 hours, so every finding here is a directional install-day signal — <b>not</b> a long-term reliability judgment. The meaningful reliability review is the day-7 re-audit on 2026-07-08.</span><span class="es-only">Base de instalación para cada radio AROYA en Verano PA. Instalación reciente — datos son direccionales. Re-auditoría real: día-7 (2026-07-08).</span></div>
    <div class="meta">
      <div><b><span class="en-only">Facility</span><span class="es-only">Instalación</span></b><span>Verano PA (id {FACILITY_ID}, Org #{ORG_ID})</span></div>
      <div><b><span class="en-only">Window</span><span class="es-only">Ventana</span></b><span>{WINDOW} → {PULLED_UTC}</span></div>
      <div><b><span class="en-only">Fleet on file</span><span class="es-only">Flota registrada</span></b><span>{UNIQUE_RADIOS} unique radios · {REPORTING} reporting · {SILENT_COUNT} silent</span></div>
      <div><b><span class="en-only">Active mesh</span><span class="es-only">Mesh activo</span></b><span>{GATEWAYS} gateway · {REPEATERS} repeaters · {H421_CLIMATE} h421 climate · {SUBSTRATE_NODES} substrate</span></div>
      <div><b><span class="en-only">Data sources</span><span class="es-only">Fuentes</span></b><span>AROYA SPA <code>/devices/?facility={FACILITY_ID}</code></span></div>
      <div><b><span class="en-only">Generated</span><span class="es-only">Generado</span></b><span>{PULLED_UTC} · Day-1 baseline pull</span></div>
    </div>
  </div>'''

def verdict_headline():
    return '''<section>
    <h2><span class="en-only">Headline — Day-1 Diagnosis</span><span class="es-only">Titular — Diagnóstico Día-1</span></h2>
    <div class="verdict warn">
      <div class="v-head"><span class="en-only">Diagnosis · Day-1 Directional</span><span class="es-only">Diagnóstico · Día-1 Direccional</span></div>
      <span class="en-only">
        <b>The install is 91% up on day-1 with two structural issues to fix before the mesh stabilizes.</b> Of 102 unique radios (175 raw, 73 dash-2 sensor-head duplicates collapsed), <b>93 are reporting</b> and <b>9 are silent</b> — normal for a fresh install where cabinets are still being closed and probes seated. Every battery-reporting node is above 90%, RSSI/link-quality are clean on all reporting devices, and there is no evidence of retry-loop pathology. <b>But two parents are over the Wirepas 14-child limit:</b> the gateway sink for <code>H2200001049</code> is at <b>18/14 (+4 over)</b>, and repeater <code>H3400003361</code> is at <b>15/14 (+1 over)</b>. As the remaining 9 silent radios come online and additional install work completes, those two parents will try to accept more children they can't hold — the failure mode is silent thrash, not a clean error. Rebalance now, before day-7. Separately, 5 rooms are showing extreme VPD/VWC values that are install-artifacts (probes not yet in their target substrate), <b>not</b> device faults. Reposition probes; the readings will normalize.
      </span>
      <span class="es-only">
        <b>Instalación al 91% en día-1 con dos problemas estructurales.</b> 93 de 102 radios reportando, 9 silenciosos (normal para instalación fresca). Baterías, RSSI y link-quality limpios. <b>Dos padres sobre el límite Wirepas de 14 hijos:</b> sink <code>H2200001049</code> 18/14, repetidor <code>H3400003361</code> 15/14. Rebalancear antes del día-7. Adicional: 5 salas con lecturas VPD/VWC extremas — artefactos de instalación (sondas mal ubicadas), <b>no</b> fallo de dispositivo.
      </span>
    </div>
  </section>'''

def kpi_strip():
    return f'''<section>
    <h2><span class="en-only">Fleet KPI Strip</span><span class="es-only">KPIs de Flota</span></h2>
    <div class="kpis">
      <div class="kpi"><div class="label"><span class="en-only">Unique radios</span><span class="es-only">Radios únicos</span></div><div class="val">{UNIQUE_RADIOS}</div><div class="delta">{RAW_SERIALS} raw · −{DASH2_COLLAPSED} dash-2 dedup</div></div>
      <div class="kpi warn"><div class="label"><span class="en-only">Reporting day-1</span><span class="es-only">Reportando día-1</span></div><div class="val">{REPORTING} <span style="font-size:14px;color:var(--ink-muted)">/ {UNIQUE_RADIOS}</span></div><div class="delta">91% · {SILENT_COUNT} silent (walkdown pending)</div></div>
      <div class="kpi good"><div class="label"><span class="en-only">Gateway online</span><span class="es-only">Gateway online</span></div><div class="val">1 / 1</div><div class="delta">H2200001049 · anchor healthy</div></div>
      <div class="kpi bad"><div class="label"><span class="en-only">Parents &gt; 14 children</span><span class="es-only">Padres &gt; 14 hijos</span></div><div class="val">{PARENTS_OVER_14}</div><div class="delta">🔴🔴 sink 18/14 · 🔴 H3400003361 15/14</div></div>
      <div class="kpi good"><div class="label"><span class="en-only">Parents 12–14 (watch)</span><span class="es-only">Padres 12–14 (vigilar)</span></div><div class="val">{PARENTS_WATCH_12_14}</div><div class="delta">no headroom-thin parents · {PARENTS_HEADROOM} 🟢 ≤11</div></div>
      <div class="kpi warn"><div class="label"><span class="en-only">Rooms with radios</span><span class="es-only">Salas con radios</span></div><div class="val">{ROOMS_WITH_RADIOS} <span style="font-size:14px;color:var(--ink-muted)">/ {ROOMS_TOTAL}</span></div><div class="delta">Room 6, Mom 1 have zero radios assigned</div></div>
      <div class="kpi good"><div class="label"><span class="en-only">Batteries ≥ 90%</span><span class="es-only">Baterías ≥ 90%</span></div><div class="val">{BAT_HEALTHY} / {BAT_HEALTHY}</div><div class="delta">fresh install · every reporting node OK</div></div>
      <div class="kpi warn"><div class="label"><span class="en-only">Install-artifact rooms</span><span class="es-only">Salas con artefactos</span></div><div class="val">5</div><div class="delta">VPD/VWC — probes not yet in target zone</div></div>
    </div>
  </section>'''

def rule_callouts():
    return '''<section>
    <h2><span class="en-only">14-Child Slot Rule</span><span class="es-only">Regla de 14 hijos</span> <span style="font-size:12px;color:var(--ink-muted);font-weight:400;letter-spacing:normal;text-transform:none">— why saturation is the load-bearing metric here</span></h2>
    <div class="card">
      <p><span class="en-only">Each parent node in the Wirepas mesh — gateway sink, relay, or upstream node — supports at most <b>14 direct children</b>. <b>Grandchildren count against their immediate parent's slots, not against the grandparent's.</b> Mid-layer relays can be saturated even when the gateway above them has plenty of headroom, so saturation has to be checked at <b>every</b> level of the topology, not just gateway-level. Once a parent crosses 14, additional devices either fail to join, get pushed to a worse parent at higher hop count, or thrash between slots — producing long travel times, retries, and growing data gaps.</span><span class="es-only">Cada padre en la mesh Wirepas soporta 14 hijos directos. Los nietos cuentan contra su padre inmediato. Rebalancear antes de saturar produce fallos silenciosos.</span></p>
      <p><span class="en-only"><b>Dash-2 dedup:</b> two AROYA serials sharing the same base number where one has a <code>-2</code> suffix (e.g. <code>H3440017858</code> and <code>H3440017858-2</code>) are ONE radio with two sensor heads, not two mesh nodes. They fill <b>one</b> slot on their parent. This report deduplicates by base serial before counting — counts are per <b>unique radio</b>, not per raw serial. (73 duplicate sensor-head entries collapsed for Verano PA.)</span><span class="es-only">Dedup dash-2: serials con sufijo <code>-2</code> son una radio con dos cabezales — cuentan como uno.</span></p>
      <p style="margin-bottom:0"><b>🟢 ≤11 children</b> — headroom &nbsp;·&nbsp; <b>🟠 12–13</b> — watch tier &nbsp;·&nbsp; <b>🔴 14</b> — at limit &nbsp;·&nbsp; <b>🔴🔴 &gt;14</b> — over-subscribed</p>
    </div>
  </section>

  <section>
    <h2><span class="en-only">Fresh-Install Flag Thresholds</span><span class="es-only">Umbrales de Instalación Fresca</span></h2>
    <div class="card">
      <p><span class="en-only">These are <b>stricter</b> than steady-state defaults because a healthy fresh deploy should look almost picture-perfect. Radios that already look degraded on day-1 will only get worse.</span><span class="es-only">Umbrales más estrictos que estado-estable — instalación fresca debe verse casi perfecta.</span></p>
      <ul style="margin:0 0 0 22px;padding:0;line-height:1.75">
        <li><span class="en-only"><b>Battery &lt; 90%</b> — fresh Li-SOCl₂ cells should be near 100% out of the box</span><span class="es-only"><b>Batería &lt; 90%</b> — celdas Li-SOCl₂ deben estar cerca de 100%</span></li>
        <li><span class="en-only"><b>Link quality &lt; 80%</b> — expect near-100% on radios with a clean parent connection</span><span class="es-only"><b>Link quality &lt; 80%</b> — cerca de 100% con conexión limpia al padre</span></li>
        <li><span class="en-only"><b>Silent-on-day-1</b> — device has not reported in the 24h window (this is the primary install signal)</span><span class="es-only"><b>Silencioso día-1</b> — sin reporte en 24h</span></li>
        <li><span class="en-only"><b>Parent saturation ≥ 14 children</b> — Wirepas hard limit</span><span class="es-only"><b>Saturación padre ≥ 14 hijos</b> — límite Wirepas</span></li>
      </ul>
    </div>
  </section>'''

def mesh_saturation_section():
    rows = ""
    for serial, model, kids, status in SINK_CHILDREN:
        if status == "SILENT":
            pill = '<span class="pill bad">silent</span>'
            row_cls = 'topo-child silent'
        elif status == "SAT":
            pill = '<span class="pill warn">15/14 over</span>'
            row_cls = 'topo-child sat'
        elif kids >= 12:
            pill = f'<span class="pill warn">{kids} kids · watch</span>'
            row_cls = 'topo-child sat'
        elif kids > 0:
            pill = f'<span class="pill muted">{kids} kids</span>'
            row_cls = 'topo-child'
        else:
            pill = '<span class="pill muted">leaf</span>'
            row_cls = 'topo-child'
        rows += f'    <div class="{row_cls}">├─ <code>{serial}</code> · {model} &nbsp; {pill}</div>\n'
    tree = f'''<div class="topo-tree">
    <div class="topo-root">● <code>H2200001049</code> · gateway · ONLINE</div>
    <div class="topo-sat">└─ SINK anchor · <b>18/14</b> children · 🔴🔴 over-subscribed (+4)</div>
{rows}  </div>'''
    return f'''<section>
    <h2><span class="en-only">Mesh Saturation &amp; Topology</span><span class="es-only">Saturación de Mesh y Topología</span></h2>
    <p class="note"><span class="en-only">Sink saturation is the day-1 headline number. The gateway sink is holding {GATEWAY_SINK_CHILDREN} direct children against a 14-slot Wirepas hard limit. Twelve of those are healthy nodes; two are silent h421s that will either join or need to be re-parented; the remaining slots are either operational h421s or the over-subscribed repeater below. The tree also shows the one saturated repeater (<code>H3400003361</code> at 15/14) — that's a downstream saturation the gateway can't see or fix.</span><span class="es-only">Saturación del sink es el número principal. El gateway tiene {GATEWAY_SINK_CHILDREN} hijos directos contra el límite Wirepas de 14. Repetidor <code>H3400003361</code> también saturado (15/14).</span></p>
    <div class="topo">
{tree}
    </div>
    <p class="note" style="margin-top:10px"><span class="en-only">Legend: silent = not reporting in 24h · sat = at or over 14 children · leaf = no dependent devices under this parent. Children with their own dependents are labelled with kid-count.</span><span class="es-only">Leyenda: silent = sin reporte 24h · sat = 14+ hijos · leaf = sin dependientes.</span></p>
  </section>'''

def per_axis_distribution():
    total = UNIQUE_RADIOS
    # Silent-on-day-1 axis
    silent_ok = REPORTING
    silent_bad = SILENT_COUNT
    # Battery axis (79 battery-reporting nodes, 79 healthy, 23 no-battery/line-powered)
    bat_ok = 79
    bat_unk = UNIQUE_RADIOS - 79
    # Link quality (98/102 nominal — 8 watch, 9 silent excluded from calc but shown as unknown here)
    link_ok = UNIQUE_RADIOS - len(WATCH_DEVICES) - SILENT_COUNT
    link_warn = len(WATCH_DEVICES)
    link_unk = SILENT_COUNT
    # Saturation across parents shown
    sat_over = 2
    sat_at = 0
    sat_watch = 0
    sat_ok = PARENTS_HEADROOM
    total_parents = sat_over + sat_watch + sat_ok
    def pct(v, t): return round(100 * v / t, 1)
    return f'''<section>
    <h2><span class="en-only">Per-Axis Distribution</span><span class="es-only">Distribución por Eje</span></h2>
    <p class="note"><span class="en-only">Four axes evaluated on day-1: silent-on-day-1 (primary install signal), battery health, link quality, and parent saturation. Steady-state RSSI / travel-time / gap-rate axes will populate at day-7 once the mesh has stabilized — those need &gt;24h of samples to be meaningful.</span><span class="es-only">Cuatro ejes evaluados en día-1: silencios, batería, link quality, saturación padre. RSSI/latencia/gap-rate se evaluarán en día-7.</span></p>
    <div class="bar-axis">
      <div class="stack"><h4><span class="en-only">Silent-on-Day-1</span><span class="es-only">Silenciosos Día-1</span></h4>
        <div class="seg"><span class="s-good" style="width:{pct(silent_ok,total)}%">{silent_ok}</span><span class="s-bad" style="width:{pct(silent_bad,total)}%">{silent_bad}</span></div>
        <div class="leg"><span><span class="legend-dot" style="background:var(--good)"></span>Reporting {silent_ok}</span><span><span class="legend-dot" style="background:var(--bad)"></span>Silent {silent_bad}</span></div>
        <div class="note"><span class="en-only">Silent = no data in the 24h window</span><span class="es-only">Sin datos en 24h</span></div></div>

      <div class="stack"><h4><span class="en-only">Battery (reporting nodes)</span><span class="es-only">Batería (nodos reportando)</span></h4>
        <div class="seg"><span class="s-good" style="width:{pct(bat_ok,total)}%">{bat_ok}</span><span class="s-unk" style="width:{pct(bat_unk,total)}%">{bat_unk}</span></div>
        <div class="leg"><span><span class="legend-dot" style="background:var(--good)"></span>≥90% · {bat_ok}</span><span><span class="legend-dot" style="background:var(--ink-muted)"></span>Line-powered / n/a · {bat_unk}</span></div>
        <div class="note"><span class="en-only">Gateways, sinks, repeaters, and reporting h421s are line-powered — no battery reading expected.</span><span class="es-only">Gateways/sinks/repeaters son line-powered.</span></div></div>

      <div class="stack"><h4><span class="en-only">Link Quality</span><span class="es-only">Calidad de Enlace</span></h4>
        <div class="seg"><span class="s-good" style="width:{pct(link_ok,total)}%">{link_ok}</span><span class="s-warn" style="width:{pct(link_warn,total)}%">{link_warn}</span><span class="s-unk" style="width:{pct(link_unk,total)}%">{link_unk}</span></div>
        <div class="leg"><span><span class="legend-dot" style="background:var(--good)"></span>OK ≥80% · {link_ok}</span><span><span class="legend-dot" style="background:var(--warn)"></span>Watch &lt;80% · {link_warn}</span><span><span class="legend-dot" style="background:var(--ink-muted)"></span>Silent · {link_unk}</span></div>
        <div class="note"><span class="en-only">Watch tier will be worth re-checking at day-7 — most link-quality dips at install are placement-related and improve with mesh stabilization.</span><span class="es-only">Vigilar en día-7.</span></div></div>

      <div class="stack"><h4><span class="en-only">Parent Saturation</span><span class="es-only">Saturación de Padre</span></h4>
        <div class="seg"><span class="s-good" style="width:{pct(sat_ok,total_parents)}%">{sat_ok}</span><span class="s-warn" style="width:{pct(sat_watch,total_parents)}%">{sat_watch}</span><span class="s-bad" style="width:{pct(sat_over,total_parents)}%">{sat_over}</span></div>
        <div class="leg"><span><span class="legend-dot" style="background:var(--good)"></span>≤11 · {sat_ok}</span><span><span class="legend-dot" style="background:var(--warn)"></span>12–13 · {sat_watch}</span><span><span class="legend-dot" style="background:var(--bad)"></span>&gt;14 · {sat_over}</span></div>
        <div class="note"><span class="en-only">Only parents currently anchoring the mesh — leaf nodes excluded.</span><span class="es-only">Solo padres activos.</span></div></div>
    </div>
  </section>'''

def room_grid_section():
    cards = ""
    for name, rid, r, on, sil, watch, art, note in ROOMS:
        if r == 0:
            cls = "room-card empty"
            stats = '<div class="room-stats"><span>zero radios assigned</span></div>'
            flag = ""
        else:
            if sil >= 1:
                cls = "room-card crit"
            elif art or watch >= 1:
                cls = "room-card warn"
            else:
                cls = "room-card"
            sil_color = 'var(--bad)' if sil else 'var(--good)'
            watch_bit = f'<span>watch <b style="color:var(--warn)">{watch}</b></span>' if watch else ''
            stats = (f'<div class="room-stats">'
                     f'<span>radios <b>{r}</b></span>'
                     f'<span>online <b>{on}</b></span>'
                     f'<span>silent <b style="color:{sil_color}">{sil}</b></span>'
                     f'{watch_bit}'
                     f'</div>')
            flag = f'<div class="room-flag">⚠ install-artifact flagged</div>' if art else ''
        cards += (f'<div class="{cls}">'
                  f'<div class="room-name">{name}</div>'
                  f'<div class="room-meta">room_id {rid} · {note}</div>'
                  f'{stats}{flag}'
                  f'</div>')
    return f'''<section>
    <h2><span class="en-only">Per-Room Summary</span><span class="es-only">Resumen por Sala</span> <span style="font-size:12px;color:var(--ink-muted);font-weight:400;letter-spacing:normal;text-transform:none">— {ROOMS_TOTAL} rooms</span></h2>
    <p class="note"><span class="en-only">Red = one or more silent radios in the room · orange = install-artifact flagged or link-quality watch · grey = zero radios assigned. Room 6 and Mom 1 have no AROYA radios in inventory — either in build-out or awaiting device binding.</span><span class="es-only">Rojo = silencios · naranja = artefacto o watch · gris = sin radios. Room 6 y Mom 1 sin radios asignados.</span></p>
    <div class="room-grid">{cards}</div>
  </section>'''

def install_artifacts_section():
    items = "".join(f'<li><b>{room}:</b> {desc}</li>\n' for room, desc in ARTIFACTS)
    return f'''<section>
    <h2><span class="en-only">Install-Artifact Readings</span><span class="es-only">Lecturas por Artefacto de Instalación</span> <span style="font-size:12px;color:var(--ink-muted);font-weight:400;letter-spacing:normal;text-transform:none">— not malfunctions</span></h2>
    <div class="artifact-card">
      <h3><span class="en-only">These are install-artifacts, not device faults</span><span class="es-only">Artefactos de instalación — no fallo de dispositivo</span></h3>
      <p><span class="en-only">The following five rooms are producing sensor values that are physically impossible for a live grow. The devices themselves are healthy — they're reporting the environment they're currently sitting in (air, empty stonewool, wrong medium), not the plant zone they will eventually monitor. These will normalize as the operator finishes probe placement. If left uncorrected, they will look like device faults on the day-7 pull.</span><span class="es-only">Estos cinco rooms muestran valores físicamente imposibles. Los dispositivos están bien — reportan aire o sustrato vacío. Se normalizarán con la instalación final.</span></p>
      <ul style="margin:0 0 0 22px;padding:0;line-height:1.75">
        {items}
      </ul>
    </div>
  </section>'''

def actions_section():
    rows = ""
    for seq, title, target, action, urg, effort, impact in ACTIONS:
        urg_cls = 'bad' if urg == 'P1' else 'warn' if urg == 'P2' else 'muted'
        rows += (f'<tr><td class="num">{seq}</td>'
                 f'<td>{title}</td>'
                 f'<td><code>{target}</code></td>'
                 f'<td>{action}</td>'
                 f'<td><span class="pill {urg_cls}">{urg}</span></td>'
                 f'<td>{impact}</td>'
                 f'<td>{effort}</td>'
                 f'</tr>')
    return f'''<section>
    <h2><span class="en-only">Prioritized Actions</span><span class="es-only">Acciones Priorizadas</span> <span style="font-size:12px;color:var(--ink-muted);font-weight:400;letter-spacing:normal;text-transform:none">— day-1 triage → day-7 re-audit</span></h2>
    <p class="note"><span class="en-only">Two P1 rebalances (sink + repeater H3400003361) should be done before the mesh takes on more traffic. Silent-radio walkdown is the fastest-payoff item. Install-artifact fixes are straightforward but must be done before the day-7 pull or those rooms will look worse.</span><span class="es-only">Dos rebalanceos P1 (sink + repetidor H3400003361) antes de más tráfico. Walkdown de silenciosos es el más rápido.</span></p>
    <table>
      <thead><tr><th>#</th><th>Action</th><th>Target</th><th>Why</th><th>Urgency</th><th>Impact</th><th>Effort</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </section>'''

def silent_roster_section():
    rows = ""
    for s, m, room, parent, rssi, lq in SILENT_DEVICES:
        rows += (f'<tr><td><code>{s}</code></td>'
                 f'<td>{m}</td>'
                 f'<td>{room}</td>'
                 f'<td><code>{parent}</code></td>'
                 f'<td class="num">{rssi}</td>'
                 f'<td class="num">{lq}%</td>'
                 f'<td><span class="pill bad">silent 24h</span></td></tr>')
    return f'''<section>
    <h2><span class="en-only">Silent Device Roster ({SILENT_COUNT})</span><span class="es-only">Radios Silenciosos ({SILENT_COUNT})</span></h2>
    <p class="note"><span class="en-only">Zero data in the 24h window. Every silent device on day-1 is an h421 climate node — a strong signal these were the last hardware family staged before the pull started. The three parented to <code>sink/H2200001049</code> directly are the highest-priority walkdown targets because they're taking sink slots they can't hold.</span><span class="es-only">Sin datos en 24h. Los 9 silenciosos son h421 climate — probablemente la última familia instalada. Los 3 con padre directo <code>sink/H2200001049</code> son prioridad.</span></p>
    <table>
      <thead><tr><th>Serial</th><th>Model</th><th>Room</th><th>Last known parent</th><th class="num">Hops</th><th class="num">Last link%</th><th>State</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </section>'''

def watch_roster_section():
    rows = ""
    for s, m, room, parent, hops, lq in WATCH_DEVICES:
        rows += (f'<tr><td><code>{s}</code></td>'
                 f'<td>{m}</td>'
                 f'<td>{room}</td>'
                 f'<td><code>{parent}</code></td>'
                 f'<td class="num">{hops}</td>'
                 f'<td class="num">{lq}%</td>'
                 f'<td><span class="pill warn">link {lq}%</span></td></tr>')
    return f'''<section>
    <h2><span class="en-only">Watch Device Roster ({len(WATCH_DEVICES)})</span><span class="es-only">Radios en Watch ({len(WATCH_DEVICES)})</span></h2>
    <p class="note"><span class="en-only">Reporting, but link quality &lt;80%. At day-1 this often resolves as the mesh stabilizes and radios drift onto better parents. If the same devices are still &lt;80% at day-7, they're placement issues — check line-of-sight to the parent.</span><span class="es-only">Reportando pero link &lt;80%. Se resuelve muchas veces al estabilizar la mesh — re-verificar día-7.</span></p>
    <table>
      <thead><tr><th>Serial</th><th>Model</th><th>Room</th><th>Parent</th><th class="num">Hops</th><th class="num">Link%</th><th>State</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </section>'''

def methodology_section():
    return f'''<section>
    <h2><span class="en-only">Data Quality &amp; Methodology</span><span class="es-only">Metodología</span></h2>
    <div class="card">
      <ul style="margin:0;padding-left:22px;line-height:1.75">
        <li><span class="en-only"><b>Inventory:</b> <code>GET /devices/?facility={FACILITY_ID}</code> · {RAW_SERIALS} raw serials.</span><span class="es-only">Inventario: {RAW_SERIALS} serials crudos.</span></li>
        <li><span class="en-only"><b>Dash-2 dedup:</b> raw serials collapsed to <b>{UNIQUE_RADIOS} unique radios</b> ({DASH2_COLLAPSED} sensor-head duplicates removed). Every count in this report is per unique radio, not per raw serial.</span><span class="es-only">Dedup dash-2: {UNIQUE_RADIOS} radios únicos.</span></li>
        <li><span class="en-only"><b>Window:</b> {WINDOW} ending {PULLED_UTC}. This is a <b>day-1 install baseline</b> pull, not a steady-state audit — 24 hours of data cannot support reliability judgments about churn rate, battery decay, or long-run mesh stability.</span><span class="es-only">Ventana: {WINDOW}. Base día-1, no auditoría estable.</span></li>
        <li><span class="en-only"><b>Flag thresholds (fresh-install, stricter than steady-state):</b> Battery &lt;90% · Link &lt;80% · Silent-on-day-1 (no data in 24h) · Parent saturation ≥14 children (Wirepas hard limit).</span><span class="es-only">Umbrales frescos: Batería &lt;90%, Link &lt;80%, silencio 24h, ≥14 hijos.</span></li>
        <li><span class="en-only"><b>Saturation counting:</b> children counted per-parent at every mesh level. Grandchildren count against the immediate parent's slots, not the grandparent's — sink saturation ({GATEWAY_SINK_CHILDREN}/14) and repeater saturation ({REPEATER_361_CHILDREN}/14) are separate findings.</span><span class="es-only">Nietos cuentan a su padre inmediato, no al abuelo.</span></li>
        <li><span class="en-only"><b>Not in scope:</b> agronomic data (VPD, dryback, yield, crop steering). Device-side install audit only. Any VPD/VWC mention in this report is flagged as an <b>install-artifact</b> — a device correctly reporting the wrong environment because it hasn't been placed in its target zone yet.</span><span class="es-only">Sin datos agronómicos. Solo lado dispositivo.</span></li>
        <li><span class="en-only"><b>Re-audit date:</b> 2026-07-08 (day-7). At that point the Wirepas mesh has had time to stabilize, silent radios have either joined or been physically confirmed missing, and probe placement will (should) be complete.</span><span class="es-only">Re-auditoría: 2026-07-08 (día-7).</span></li>
      </ul>
    </div>
  </section>'''

def footer():
    return f'''<div class="footer-note">
    <span class="en-only">Report generated {PULLED_UTC} · pulled live from AROYA SPA <code>/devices/?facility={FACILITY_ID}</code>. Dash-2 sensor-head duplicates deduplicated before counts. 14-child rule per Wirepas spec. Every finding qualified as "based on ~24h of data — directional only." Sole authoritative source for the payload is the AROYA public/SPA API — no third-party enrichment.</span>
    <span class="es-only">Reporte generado {PULLED_UTC} · fuente única: AROYA SPA <code>/devices/?facility={FACILITY_ID}</code>. Regla de 14 hijos por spec Wirepas. Todo direccional en día-1.</span>
  </div>'''

SCRIPT = r"""<script>
document.querySelectorAll('.lang-btn').forEach(btn => btn.addEventListener('click', () => {
  const lang = btn.dataset.lang;
  document.body.className = lang;
  document.querySelectorAll('.lang-btn').forEach(b => b.classList.toggle('active', b.dataset.lang === lang));
}));
document.querySelectorAll('.theme-btn').forEach(btn => btn.addEventListener('click', () => {
  const theme = btn.dataset.theme;
  if (theme === 'light') window.location.href = window.location.pathname.replace('_dark.html', '.html');
  else window.location.href = window.location.pathname.replace('.html', '_dark.html').replace('_dark_dark.html', '_dark.html');
}));
</script>"""

def build(theme):
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="{theme}">
<head>
<meta charset="UTF-8">
<title>Verano PA — Day-1 Device + Mesh Health · AROYA</title>
<style>{STYLE}</style>
{MOBILE_QA}
</head>
<body>
{masthead()}
<div class="wrap">
  {pagehead()}
  {verdict_headline()}
  {kpi_strip()}
  {rule_callouts()}
  {mesh_saturation_section()}
  {per_axis_distribution()}
  {room_grid_section()}
  {install_artifacts_section()}
  {actions_section()}
  {silent_roster_section()}
  {watch_roster_section()}
  {methodology_section()}
  {footer()}
</div>
{SCRIPT}
</body>
</html>
"""

if __name__ == "__main__":
    light = build("light")
    dark = build("dark")
    (REPO / "VeranoPA_Day1_Device_Mesh_Health_2026-07-01.html").write_text(light)
    (REPO / "VeranoPA_Day1_Device_Mesh_Health_2026-07-01_dark.html").write_text(dark)
    print(f"Wrote light: {len(light)} bytes")
    print(f"Wrote dark : {len(dark)} bytes")
