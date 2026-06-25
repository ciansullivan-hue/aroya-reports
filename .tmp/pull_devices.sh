#!/bin/bash
set -e
cd /Users/ciansullivan/code/aroya-reports/.tmp
ACCESS=$(python3 -c 'import json;print(json.load(open("/Users/ciansullivan/.aroya/spa_token_app.json"))["access"])')
for p in 1 2 3 4 5 6 7 8 9 10 11; do
  curl -s -H "Authorization: Bearer $ACCESS" -H 'X-Facility: 3754' "https://api.aroya.io/devices/?facility=3754&page=$p" > devices_p$p.json
  echo -n "p$p: "
  python3 -c "import json;d=json.load(open('devices_p$p.json'));print('results=',len(d.get('results',[])),'count=',d.get('count'))"
done
echo ALL_DONE
