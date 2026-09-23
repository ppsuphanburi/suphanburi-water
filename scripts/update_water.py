import json, os
from datetime import datetime, timezone, timedelta
import urllib.request

API = "https://api-v3.thaiwater.net/api/v1/thaiwater30/provinces/waterlevel"
OUT = "data/water.json"
PROVINCE_CODE = "72"

def now_thai():
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=7))).isoformat(timespec="seconds")

def get_json(url):
    req=urllib.request.Request(url, headers={"User-Agent":"Suphanburi-Water-Watch/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

raw=get_json(API)
records=raw.get("data", [])
rows=[]
seen={}
for x in records:
    geo=x.get("geocode") or {}
    if str(geo.get("province_code")) != PROVINCE_CODE:
        continue
    st=x.get("station") or {}
    sid=str(st.get("id") or x.get("id") or "")
    dt=str(x.get("waterlevel_datetime") or "")
    if not sid:
        continue
    if sid not in seen or dt > seen[sid].get("waterlevel_datetime",""):
        seen[sid]=x

for x in seen.values():
    geo=x.get("geocode") or {}
    st=x.get("station") or {}
    rows.append({
        "station_id": st.get("id"),
        "name": st.get("tele_station_name") or st.get("station_name") or "ไม่ระบุสถานี",
        "waterlevel_datetime": x.get("waterlevel_datetime"),
        "waterlevel_msl": x.get("waterlevel_msl"),
        "waterlevel_m": x.get("waterlevel_m"),
        "diff_wl_bank": x.get("diff_wl_bank"),
        "diff_wl_bank_text": x.get("diff_wl_bank_text"),
        "status_text": x.get("situation_level") if isinstance(x.get("situation_level"), str) else x.get("diff_wl_bank_text"),
        "river_name": x.get("river_name"),
        "district": geo.get("amphoe_name"),
        "subdistrict": geo.get("tambon_name"),
        "province": geo.get("province_name"),
        "latitude": st.get("latitude"),
        "longitude": st.get("longitude"),
        "left_bank": st.get("left_bank"),
        "right_bank": st.get("right_bank"),
        "min_bank": st.get("min_bank")
    })
rows.sort(key=lambda x: (x["name"] or ""))

if os.path.exists(OUT):
    with open(OUT,"r",encoding="utf-8") as f:
        db=json.load(f)
else:
    db={"started_at":None,"last_collected_at":None,"snapshots":[]}

collected=now_thai()
if not db.get("started_at"):
    db["started_at"]=collected

db["last_collected_at"]=collected
db.setdefault("snapshots",[]).append({"collected_at":collected,"stations":rows})

# Keep the project lightweight: retain the last 7 days of collected snapshots.
db["snapshots"]=db["snapshots"][-168:]

os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(OUT,"w",encoding="utf-8") as f:
    json.dump(db,f,ensure_ascii=False,separators=(",",":"))
