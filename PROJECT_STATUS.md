# Project Status

อัปเดตล่าสุด: 2026-10-06 (Phase 0–8 เสร็จ, รอข้อมูลจริง Phase 9)

## สรุปสถานะ

| เฟส | งาน | สถานะ |
|-----|-----|-------|
| 0 | README จากเอกสารสเปค 3 ไฟล์ + commit | ✅ เสร็จ |
| 1 | Scaffold โครงสร้างโปรเจกต์ (`config.py`, `layouts/`, `callbacks/`, `utils/`, `data/`, `requirements.txt`) | ✅ เสร็จ |
| 2 | Data layer: `dim_province.csv` (77 จังหวัด), sample generator, pipeline (interpolate/normalize), loader | ✅ เสร็จ |
| 3 | Mismatch engine (`utils/mismatch.py`) + unit tests | ✅ เสร็จ (8 tests ผ่าน) |
| 4 | App shell + Global filters (ปี / ด้าน / จังหวัด) + banner ข้อมูลสังเคราะห์ | ✅ เสร็จ |
| 5 | Tab 1: National Overview (4 KPI cards + 4 กราฟ) | ✅ เสร็จ |
| 6 | Tab 2: Provincial Overview (choropleth 77 จังหวัด, bar, GPP line, radar, donut, ตารางจัดอันดับ) + cross-filtering | ✅ เสร็จ |
| 7 | Tab 3: Mismatch Analysis (scatter, bubble, GPP scatter, heatmap, Top 10, correlation heatmap) | ✅ เสร็จ |
| 8 | ทดสอบรวม / performance / ตรวจ UI ในเบราว์เซอร์ | ✅ เสร็จ (pytest 14 ผ่าน, callback ≤ 0.3 วินาที, ตรวจ UI ด้วย headless Chromium) |
| 9 | นำข้อมูลจริงจาก Open Data เข้า pipeline | ⏸ **ยังไม่ได้ทำ** — เครื่องมือของ Claude ดาวน์โหลดไฟล์จากเว็บภาครัฐไม่ได้ (ดู Phase 9 ด้านล่าง) |
| 10 | Data reference ใต้ทุกกราฟ + ป้ายสถานะ จริง/สังเคราะห์ | ✅ เสร็จ |

## บันทึกความคืบหน้า

- **2026-10-06** — Phase 0: สร้าง `README.md` จาก `brd_dashboard_analysis_specification.md`, `antigravity_dashboard_handoff_spec.md`, `thailand_open_data_sources.md` และ commit (`c290a6d`)

- **2026-10-06** — Phase 1: scaffold + `config.py` (6 domains, สี, น้ำหนัก Mismatch) + `requirements.txt` (`d645d83`)
- **2026-10-06** — Phase 2: `utils/sample_data.py` (CSV สังเคราะห์ใน `data/raw/`), `utils/pipeline.py` (grid ครบ, linear interpolation + ธง `Is_Imputed` 108/2,310 แถว, Min-Max outcome ต่อด้าน, ตารางประเทศ), `utils/data_loader.py` (per-capita, complaint rate /100k, efficiency ratio), `docs/DATA_SCHEMA.md`
- **2026-10-06** — Phase 3: `utils/mismatch.py` (normalize ต่อ ปี×ด้าน, สูตร BRD 4.2, Top-N พร้อมเหตุผลภาษาไทย) + `tests/` — pytest 8 passed
- **2026-10-06** — Phase 4–7: `app.py` (Dash + Bootstrap FLATLY, tab render ตาม active tab), `layouts/` (filters + 3 tabs), `callbacks/` (tab1–3), `utils/figures.py`, `utils/queries.py`, `data/geo/thailand_provinces.geojson` (ขอบเขต 77 จังหวัด, รหัสตรง `Province_ID` ครบ), `assets/style.css`
  - Cross-filtering: คลิกจังหวัดบนแผนที่หรือแถวในตาราง → ตั้งค่า dropdown จังหวัดกลาง → ทุกกราฟ Tab 2 อัปเดต (คลิกซ้ำ = กลับเป็นทั้งประเทศ); Tab 3 ไฮไลต์จังหวัดที่เลือก
  - ทดสอบ: pytest 14 passed (pipeline, mismatch, callbacks ทุก tab, HTTP endpoints); เวลาประมวลผล callback 0.12–0.29 วินาที (เกณฑ์ ≤ 1.5 วินาที)
- **2026-10-06** — Phase 8: ตรวจ UI ด้วย Chromium ถ่ายภาพ 3 tab ไม่มี JS error; พบ `go.Choropleth` ต้องโหลดแผนที่โลกจาก CDN → เปลี่ยนเป็น `go.Choroplethmap` (white-bg, ใช้ออฟไลน์ได้, ซูม/แพนได้, ต้อง plotly ≥ 5.24); จำกัดช่วงสีแผนที่ที่เปอร์เซ็นไทล์ 2–95 เพราะกรุงเทพฯ เป็น outlier
- **2026-10-06** — Phase 10: เพิ่ม `utils/sources.py` (registry 10 แหล่งข้อมูล + ลิงก์) และบรรทัด "แหล่งข้อมูล" ใต้ทุกกราฟ/KPI/ตาราง พร้อมป้าย **ข้อมูลจริง / ข้อมูลสังเคราะห์** ต่อชุดข้อมูล (ป้ายเป็น "จริง" ก็ต่อเมื่อชื่อชุดอยู่ใน `data/raw/real_sources.json`) + `tests/test_references.py`

## Phase 9 — สถานะข้อมูลจริง (ตรวจเมื่อ 2026-10-06)

- ข้อมูลทุกชุดในแดชบอร์ดตอนนี้ **ยังเป็นข้อมูลสังเคราะห์** ยกเว้นขอบเขตจังหวัด (GeoJSON) — ไม่ได้นำตัวเลขใดมาอ้างว่าเป็นข้อมูลจริง
- ที่ตรวจแล้ว: เชลล์ของ Claude เข้า data.go.th / สศช. / 1111 / ดำรงธรรม / DOPA ไม่ได้ (ถูกบล็อก) และเครื่องมืออ่านเว็บอ่านได้เฉพาะข้อความ ดาวน์โหลดไฟล์ XLSX ไม่ได้
- data.go.th มี GPP แยกเป็นรายจังหวัดคนละ dataset (เช่น นนทบุรี, ชัยนาท) ส่วนไฟล์รวม 77 จังหวัดอยู่ที่สศช. (Excel อนุกรมเวลา 2538–2565 ยังไม่เห็นปี 2566)
- **ไม่มีชุดข้อมูลเปิดสำเร็จรูป** ที่จัด งบประมาณ/ผลลัพธ์/ร้องเรียน รายจังหวัด×6 ด้านตามนิยามของ BRD — ต้องทำตาราง mapping หมวดงบ/หมวดเรื่องร้องเรียน → 6 ด้านเอง และเลือก KPI จริงต่อด้าน (ต้องตัดสินใจร่วมกับเจ้าของโครงการ)
- ลำดับที่ควรนำเข้าก่อน (ทำได้จริงและตรวจสอบได้): (1) GPP 77 จังหวัด (สศช.) (2) ประชากรรายจังหวัด (DOPA) (3) GDP ประเทศ (สศช.) (4) งบประมาณรวมรายจังหวัด (5) ร้องเรียน/ผลลัพธ์รายด้าน

## ขั้นถัดไป

1. ดาวน์โหลดข้อมูลจริงตาม `thailand_open_data_sources.md` → แปลงเป็น CSV ตาม `docs/DATA_SCHEMA.md` ลง `data/raw/` (ลบ `SAMPLE_DATA.flag`) → `python -m utils.pipeline` (Phase 9)
2. ยืนยันสูตร Mismatch (หาร B×C ด้วย 100) และนิยาม KPI รายด้านที่จะใช้จริงกับเจ้าของ BRD
3. (ถ้าต้องการ) Top/Bottom 10 chart, GDP growth vs Outcome, ทดสอบการคลิกแผนที่ใน browser จริง

## หมายเหตุ / ข้อสมมติ

- แหล่ง Open Data ภาครัฐ (GovSpend, สศช., 1111, ฯลฯ) ต้องดาวน์โหลดด้วยตนเองและรูปแบบไฟล์ต่างกัน จึงพัฒนาด้วย **ข้อมูลตัวอย่างสังเคราะห์ (synthetic)** ที่มี schema ตรงกับ Fact table ใน BRD ก่อน และทำ loader ให้สลับเป็นข้อมูลจริงได้ (Phase 9) — ตัวเลขในแดชบอร์ดช่วงนี้ **ไม่ใช่ข้อมูลจริง**
- แยก `fact_province_year` (GPP, Population) ออกจาก `fact_province_domain` เพราะเป็นระดับจังหวัด×ปี ถ้าไว้ใน fact เดียวตาม BRD จะ SUM ซ้ำ 6 เท่า
- สูตร Mismatch: พจน์ B×C ถ้าทั้งคู่อยู่ในสเกล 0–100 จะได้ 0–10,000 จึงหารด้วย 100 เพื่อให้คะแนนรวมอยู่ในช่วง 0–100 (ข้อสมมติ ควรยืนยันกับเจ้าของ BRD)
- `dash_table.DataTable` ถูกประกาศ deprecated ใน Dash รุ่นถัดไป อาจย้ายไป `dash-ag-grid` ภายหลัง
- GeoJSON ขอบเขตจังหวัดมาจาก chingchai/OpenGISData-Thailand ควรตรวจ licence ก่อนเผยแพร่ (ดู `data/geo/README.md`)
- เมื่อสเปคสองฉบับต่างกัน ยึด BRD เป็นหลัก (3 tab ตาม Section 5) และเพิ่ม view จาก handoff spec (Top/Bottom 10, correlation heatmap) เป็นส่วนเสริม
