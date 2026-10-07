# Thailand Government Budget Analytics Dashboard

แดชบอร์ดเชิงโต้ตอบ (Dash + d3) สำหรับวิเคราะห์ความสัมพันธ์ระหว่าง **งบประมาณแผ่นดิน – GDP/GPP – ผลสัมฤทธิ์ (Outcomes) – ข้อร้องเรียนของประชาชน** ระดับประเทศและ 77 จังหวัด ช่วง **ปีงบประมาณ 2019–2023 (พ.ศ. 2562–2566)**

> สถานะความคืบหน้าดูที่ [`PROJECT_STATUS.md`](PROJECT_STATUS.md)

## วิธีรัน

```bash
pip install -r requirements.txt
python app.py            # http://127.0.0.1:8060 (เปลี่ยนพอร์ตด้วย --port 9000) (สร้างข้อมูลตัวอย่างอัตโนมัติถ้ายังไม่มี data/raw)
python -m pytest -q      # ทดสอบ
```

> ตอนนี้ใช้ **ข้อมูลสังเคราะห์** (มี banner เตือนในแอป) จนกว่าจะนำข้อมูลจริงเข้า `data/raw/` ตาม [`docs/DATA_SCHEMA.md`](docs/DATA_SCHEMA.md)

## วัตถุประสงค์

1. ติดตามและประเมินประสิทธิภาพการจัดสรรงบประมาณ เทียบกับ GDP/GPP ผลลัพธ์ และข้อร้องเรียน ทั้งระดับประเทศและรายจังหวัด
2. วิเคราะห์ความไม่สอดคล้อง (Mismatch Analysis) — หาพื้นที่/ด้านที่งบสูงแต่ผลลัพธ์ต่ำหรือข้อร้องเรียนสูง เพื่อสนับสนุนการตัดสินใจเชิงนโยบาย

**ผู้ใช้เป้าหมาย:** ผู้บริหาร/นักนโยบาย, นักวิเคราะห์งบประมาณ (สำนักงบฯ/คลัง), ภาคประชาสังคมและประชาชน

## 6 ด้านมาตรฐาน (Standard Domains)

| # | ด้าน | Domain key |
|---|------|-----------|
| 1 | การศึกษาและการเรียนรู้ | `Education_Learning` |
| 2 | สาธารณสุขและการแพทย์ | `Healthcare_Medical` |
| 3 | โครงสร้างพื้นฐาน โยธา และคมนาคม | `Infrastructure_Transport` |
| 4 | การเกษตรและสิ่งแวดล้อม | `Agriculture_Environment` |
| 5 | การบริหารทั่วไป บุคลากร และความสงบเรียบร้อย | `Administration_Safety` |
| 6 | เศรษฐกิจ การท่องเที่ยว และการพัฒนาสังคม | `Economy_Tourism_Social` |

## ชุดข้อมูล (9 ชุด)

| ระดับ | ชุดข้อมูล | แหล่งหลัก |
|-------|-----------|-----------|
| ประเทศ | งบประมาณรายด้าน | GovSpend (DGA), สำนักงบประมาณ, data.go.th |
| ประเทศ | GDP (Current / CVM) | สศช. บัญชีประชาชาติ |
| ประเทศ | ผลลัพธ์/KPIs รายด้าน | eMENSCR (สศช.), สำนักงบประมาณ |
| ประเทศ | ข้อร้องเรียนรายด้าน | ศูนย์บริการประชาชน 1111 |
| จังหวัด | งบประมาณรวม | กรมบัญชีกลาง (CGD), GovSpend |
| จังหวัด | งบประมาณรายด้าน | OSMCE มหาดไทย, data.go.th |
| จังหวัด | GPP / GPP per capita | สศช. ผลิตภัณฑ์ภาคและจังหวัด |
| จังหวัด | ผลลัพธ์ / HAI Index | สศช., PBIC มหาดไทย |
| จังหวัด | ข้อร้องเรียนรายด้าน | ศูนย์ดำรงธรรม, 1111 |
| เสริม | ประชากรรายจังหวัด | กรมการปกครอง (stat.bora.dopa.go.th) |

รายละเอียดลิงก์ทั้งหมด: [`thailand_open_data_sources.md`](thailand_open_data_sources.md)

## Data Model (Star Schema)

- **Dim_Province** (`Province_ID`, ชื่อ TH/EN, Region, Lat/Long) · **Dim_Year** (`Fiscal_Year`) · **Dim_Domain** (`Domain_ID`, KPI name/unit)
- **Fact_Provincial_Data** — key: `Fiscal_Year + Province_ID + Domain_ID`; measures: `Budget_Amount`, `GPP_Amount`, `Outcome_Raw_Value`, `Outcome_Normalized_Score`, `Complaint_Count`, `Population`

กฎแปลงข้อมูล: แปลง พ.ศ.→ค.ศ., จัดชื่อจังหวัดตาม ISO 3166-2:TH/TIS 1099, คำนวณค่าต่อหัว (Budget/GPP/Complaints), Efficiency Ratio = Outcome / Budget, ยึด Fiscal Year เป็นหลักในการ align

## Mismatch Score

Min-Max normalize (0–100) ตัวแปร $B_{capita}$, $O_{score}$, $C_{rate}$, $G_{capita}$ แล้วคำนวณ ต่อ (จังหวัด *i*, ด้าน *j*):

```
Mismatch = 0.4 * max(0, B - O) + 0.4 * (B * C) + 0.2 * max(0, B - G)
```

ข้อร้องเรียนใช้เป็น **อัตราต่อประชากร 100,000 คน** เสมอ

## ฟีเจอร์ของแดชบอร์ด

**Global filters:** ปี (2019–2023) · ด้าน (multi-select) · จังหวัด (default 77 จังหวัด)

- **Tab 1 – National Overview:** KPI cards (งบรวม, GDP, งบ/GDP %, ข้อร้องเรียน), bar งบรายด้าน, dual-axis GDP vs งบ, line ผลลัพธ์รายด้าน, stacked bar ข้อร้องเรียน
- **Tab 2 – Provincial Overview:** choropleth 77 จังหวัด + cross-filtering ทุกกราฟ, horizontal bar งบรายด้าน, line GPP, radar ผลลัพธ์, donut ข้อร้องเรียน, ตารางจัดอันดับ sort ได้
- **Tab 3 – Mismatch Analysis:** scatter งบต่อหัว vs ผลลัพธ์, bubble งบ vs ร้องเรียน, scatter GPP vs งบ, heatmap จังหวัด×ด้าน, Top 10 Mismatch Priority List
- (จาก handoff spec) Top/Bottom 10 ranking, correlation heatmap (Pearson: Budget–GPP–Complaints), ROI/Efficiency

## สถาปัตยกรรมและ Tech Stack

Python 3.10+ · Dash (เซิร์ฟเวอร์ + ส่งข้อมูล) · Pandas/DuckDB/Parquet (data layer) · d3.js v7 (วาดแผนที่/กราฟฝั่งเบราว์เซอร์ ฝังไว้ใน `assets/d3.min.js` ใช้ออฟไลน์ได้)

โครงสร้างโค้ดปัจจุบัน:

```
app.py                  # Dash: เสิร์ฟหน้า + ส่ง payload ให้ assets/dashboard.js
assets/dashboard.js     # UI: 3 แท็บ, แผนที่ซูมได้, กราฟ, แอนิเมชัน
assets/dashboard.css    # ธีมมืด, เวทีขนาดคงที่ 1600x900 ย่อ/ขยายพอดีหน้าจอ
assets/d3.min.js        # d3 v7.9 (ISC license) ฝังไว้ในโปรเจกต์
utils/payload.py        # สร้าง JSON จากตารางที่ประมวลผลแล้ว + ป้ายข้อมูลจริง/สังเคราะห์
utils/live_fetch.py     # ดึงเรื่องร้องเรียน 1111 สดจาก data.go.th (cache + fallback)
utils/pipeline.py, mismatch.py, queries.py, data_loader.py, sources.py
data/                   # raw_real (ข้อมูลจริง), raw (สังเคราะห์), processed (parquet), geo
```

หน้าจอ: แผนที่ประเทศไทยตรงกลาง (ซูม/เลื่อนได้เฉพาะแผนที่), KPI/กราฟเส้น/โดนัท/แท่ง/พื้นที่/เรดาร์/scatter/heatmap รอบด้าน, ตัวกรองปี, ปุ่ม "แหล่งข้อมูล", ใต้ทุกกราฟมีแหล่งข้อมูลและป้ายจริง/สังเคราะห์, สีแดงใช้เฉพาะแจ้งเตือนเรื่องร้องเรียน

## Non-Functional Requirements

- ตอบสนอง cross-filtering ≤ 1.5 วินาที
- รองรับ Desktop 1920×1080 และ Laptop 1366×768
- UI สองภาษา (ไทย/อังกฤษ), โครงสร้างโค้ดแยกส่วนชัดเจน

## ความเสี่ยงข้อมูลและแนวทางรับมือ

| ความเสี่ยง | แนวทาง |
|-----------|--------|
| ข้อมูลบางจังหวัด/ปีไม่ครบ | Linear interpolation หรือแสดง `*Data Incomplete` |
| ปีงบประมาณ ≠ ปีปฏิทิน | ยึด Fiscal Year ใน pipeline |
| หน่วย Outcome ต่างกัน | Min-Max Normalization 0–100 |
| ร้องเรียนเอนเอียงตามประชากร | ใช้ rate ต่อ 100,000 คน |

## เอกสารในโปรเจกต์

| ไฟล์ | เนื้อหา |
|------|---------|
| `brd_dashboard_analysis_specification.md` | BRD: taxonomy, data model, สูตร Mismatch, layout, NFR, risks |
| `antigravity_dashboard_handoff_spec.md` | Handoff spec: data catalog, pipeline JSON, view เพิ่มเติม |
| `thailand_open_data_sources.md` | รายการลิงก์ชุดข้อมูล Open Data 2562–2566 |
| `PROJECT_STATUS.md` | ความคืบหน้าการพัฒนา |
