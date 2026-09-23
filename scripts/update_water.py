import json
import os
from datetime import datetime, timezone, timedelta
import urllib.request

API = "https://api-v3.thaiwater.net/api/v1/thaiwater30/provinces/waterlevel"
OUT = "data/water.json"
PROVINCE_CODE = "72"


def now_thai():
    return datetime.now(
        timezone.utc
    ).astimezone(
        timezone(timedelta(hours=7))
    ).isoformat(timespec="seconds")


def get_json(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Suphanburi-Water-Watch/1.0"
        }
    )

    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(
            r.read().decode("utf-8")
        )


def label(v):
    """
    แปลงข้อมูลชื่อที่ API อาจส่งมาเป็น
    string หรือ dictionary ให้เป็นข้อความภาษาไทย
    """

    if v is None:
        return ""

    if isinstance(v, str):
        return v

    if isinstance(v, (int, float)):
        return str(v)

    if isinstance(v, dict):

        # ภาษาไทย
        if v.get("th"):
            return label(v.get("th"))

        # ภาษาอังกฤษ
        if v.get("en"):
            return label(v.get("en"))

        # key ทั่วไป
        if v.get("name"):
            return label(v.get("name"))

        if v.get("label"):
            return label(v.get("label"))

        # เอาค่าตัวแรก
        values = list(v.values())

        if values:
            return label(values[0])

        return ""

    return str(v)


raw = get_json(API)

records = raw.get("data", [])

rows = []
seen = {}


# --------------------------------------------------
# เลือกเฉพาะสถานีจังหวัดสุพรรณบุรี
# และเอาข้อมูลล่าสุดของแต่ละสถานี
# --------------------------------------------------

for x in records:

    geo = x.get("geocode") or {}

    if str(geo.get("province_code")) != PROVINCE_CODE:
        continue

    st = x.get("station") or {}

    sid = str(
        st.get("id")
        or x.get("id")
        or ""
    )

    dt = str(
        x.get("waterlevel_datetime")
        or ""
    )

    if not sid:
        continue

    if (
        sid not in seen
        or dt > seen[sid].get(
            "waterlevel_datetime",
            ""
        )
    ):
        seen[sid] = x


# --------------------------------------------------
# สร้างข้อมูลสำหรับ dashboard
# --------------------------------------------------

for x in seen.values():

    geo = x.get("geocode") or {}
    st = x.get("station") or {}

    agency = x.get("agency") or {}

    rows.append({

        "id": x.get("id"),

        "datetime": x.get(
            "waterlevel_datetime"
        ),

        # ชื่อสถานี
        "name": label(
            st.get("tele_station_name")
            or st.get("station_name")
            or "ไม่ระบุสถานี"
        ),

        # พื้นที่
        "district": label(
            geo.get("amphoe_name")
        ),

        "subdistrict": label(
            geo.get("tambon_name")
        ),

        "province": label(
            geo.get("province_name")
        ),

        # ระดับน้ำ
        "waterlevel_msl": x.get(
            "waterlevel_msl"
        ),

        "waterlevel_m": x.get(
            "waterlevel_m"
        ),

        # ตลิ่ง
        "min_bank": st.get(
            "min_bank"
        ),

        "diff_wl_bank": x.get(
            "diff_wl_bank"
        ),

        "status_text": label(
            x.get("diff_wl_bank_text")
        ),

        # แม่น้ำ/คลอง
        "river_name": label(
            x.get("river_name")
        ),

        # พิกัด
        "lat": st.get("lat"),

        "long": st.get("long"),

        # ประเภทสถานี
        "station_type": label(
            x.get("station_type")
        ),

        # หน่วยงาน
        "agency": label(
            agency.get("agency_name")
            or agency
        ),
    })


# --------------------------------------------------
# เรียงชื่อสถานี
# --------------------------------------------------

rows.sort(
    key=lambda x: str(
        x.get("name") or ""
    )
)


# --------------------------------------------------
# โหลดฐานข้อมูลเดิม
# --------------------------------------------------

if os.path.exists(OUT):

    with open(
        OUT,
        "r",
        encoding="utf-8"
    ) as f:

        db = json.load(f)

else:

    db = {
        "started_at": None,
        "last_collected_at": None,
        "snapshots": []
    }


# --------------------------------------------------
# บันทึก snapshot ใหม่
# --------------------------------------------------

collected = now_thai()

if not db.get("started_at"):
    db["started_at"] = collected

db["last_collected_at"] = collected

db.setdefault(
    "snapshots",
    []
)

db["snapshots"].append({

    "collected_at": collected,

    "stations": rows

})


# --------------------------------------------------
# เก็บย้อนหลัง 7 วัน
# --------------------------------------------------

db["snapshots"] = db[
    "snapshots"
][-168:]


# --------------------------------------------------
# เขียน water.json
# --------------------------------------------------

os.makedirs(
    os.path.dirname(OUT),
    exist_ok=True
)

with open(
    OUT,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        db,
        f,
        ensure_ascii=False,
        separators=(",", ":")
    )

print(
    "Updated Suphanburi water data:",
    len(rows),
    "stations"
)
