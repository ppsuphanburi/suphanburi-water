# Suphanburi Water Watch

เว็บติดตามระดับน้ำจังหวัดสุพรรณบุรีแบบ static + GitHub Actions

## หลักการ
- ดึงข้อมูลจาก ThaiWater API
- กรองจังหวัดสุพรรณบุรีด้วย province_code = 72
- เริ่มสะสมข้อมูลตั้งแต่ workflow รอบแรก ไม่ backfill ข้อมูลเก่า
- เก็บ snapshot ล่าสุดทุกชั่วโมง
- หน้าเว็บอ่าน `data/water.json`
- เก็บย้อนหลังสูงสุด 7 วัน

## ติดตั้ง
1. สร้าง public repository ชื่อ `suphanburi-water`
2. อัปโหลดไฟล์ทั้งหมดจากชุดนี้
3. ไป Settings > Pages > Source = Deploy from a branch
4. Branch = main / folder = /(root)
5. ไป Actions และกด workflow `Collect Suphanburi Water Data` > Run workflow เพื่อเก็บรอบแรกทันที
6. หน้าเว็บจะอยู่ที่ https://ppsuphanburi-water.github.io/suphanburi-water/

หมายเหตุ: เว็บไซต์เป็นระบบแสดงข้อมูล ไม่ใช่ประกาศเตือนภัยอย่างเป็นทางการ
