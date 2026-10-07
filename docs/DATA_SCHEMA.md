# Real data schema (data/raw_real/)

> ปัจจุบันใช้เฉพาะข้อมูลจริง: `budget_province_domain.csv` (2023), `complaints_1111_province_type.csv`, `gpp_province.csv`, `population_province.csv` — ไม่มี `outcome_*` และไม่มีการสร้างข้อมูลสังเคราะห์/interpolate; ตารางด้านล่างคือ schema ของแต่ละชุดเมื่อมีข้อมูลจริงเพิ่ม

ไฟล์ CSV ที่ pipeline (`python -m utils.pipeline`) ต้องการ — ข้อมูลจริงจาก Open Data ต้องแปลงให้ตรง schema นี้
(พ.ศ. → ค.ศ., ชื่อจังหวัด → `Province_ID` แบบ ISO 3166-2:TH เช่น `TH-40`)

| ไฟล์ | คอลัมน์ | หมายเหตุ |
|------|---------|----------|
| `budget_province_domain.csv` | Fiscal_Year, Province_ID, Domain_ID, Budget_Amount | THB |
| `outcome_province_domain.csv` | Fiscal_Year, Province_ID, Domain_ID, Outcome_Raw_Value | KPI ดิบตามนิยาม BRD 4.1 (ทิศทาง "ยิ่งสูงยิ่งดี"; ตัวชี้วัดที่ยิ่งต่ำยิ่งดีให้กลับค่าก่อน) |
| `complaints_province_domain.csv` | Fiscal_Year, Province_ID, Domain_ID, Complaint_Count | จำนวนเรื่อง |
| `gpp_province.csv` | Fiscal_Year, Province_ID, GPP_Amount | THB |
| `population_province.csv` | Fiscal_Year, Province_ID, Population | คน |
| `gdp_national.csv` | Fiscal_Year, GDP_Amount | THB |
| `budget_national.csv` (optional) | Fiscal_Year, Domain_ID, Budget_Amount | ถ้าไม่มี จะรวมจากรายจังหวัด |
| `complaints_national.csv` (optional) | Fiscal_Year, Domain_ID, Complaint_Count | ถ้าไม่มี จะรวมจากรายจังหวัด |

`Domain_ID` = 1..6 ตาม `config.DOMAINS`. แถว/ปีที่ไม่มีข้อมูลจะเป็น NaN (UI แสดง "ไม่มีข้อมูล") — ไม่มีการ interpolate (`Is_Imputed` เป็น False เสมอ)

**ข้อแตกต่างจาก BRD:** GPP และ Population เป็นระดับ จังหวัด×ปี จึงแยกเป็น `fact_province_year` (BRD วางไว้ใน fact เดียว ซึ่งจะทำให้ SUM ซ้ำ 6 เท่า)
