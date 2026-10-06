# Project Status

อัปเดตล่าสุด: 2026-10-06

## สรุปสถานะ

| เฟส | งาน | สถานะ |
|-----|-----|-------|
| 0 | README จากเอกสารสเปค 3 ไฟล์ + commit | ✅ เสร็จ |
| 1 | Scaffold โครงสร้างโปรเจกต์ (`config.py`, `layouts/`, `callbacks/`, `utils/`, `data/`, `requirements.txt`) | ✅ เสร็จ |
| 2 | Data layer: `dim_province.csv` (77 จังหวัด), sample generator, pipeline (interpolate/normalize), loader | ✅ เสร็จ |
| 3 | Mismatch engine (`utils/mismatch.py`) + unit tests | ⬜ ยังไม่เริ่ม |
| 4 | App shell + Global filters (ปี / ด้าน / จังหวัด) | ⬜ ยังไม่เริ่ม |
| 5 | Tab 1: National Overview | ⬜ ยังไม่เริ่ม |
| 6 | Tab 2: Provincial Overview + cross-filtering | ⬜ ยังไม่เริ่ม |
| 7 | Tab 3: Mismatch Analysis | ⬜ ยังไม่เริ่ม |
| 8 | ทดสอบรวม / performance / ปรับ UI | ⬜ ยังไม่เริ่ม |
| 9 | นำข้อมูลจริงจาก Open Data เข้า pipeline | ⏸ รอผู้ใช้ดาวน์โหลดไฟล์ (ดูหมายเหตุ) |

## บันทึกความคืบหน้า

- **2026-10-06** — Phase 0: สร้าง `README.md` จาก `brd_dashboard_analysis_specification.md`, `antigravity_dashboard_handoff_spec.md`, `thailand_open_data_sources.md` และ commit (`c290a6d`)

- **2026-10-06** — Phase 1: scaffold + `config.py` (6 domains, สี, น้ำหนัก Mismatch) + `requirements.txt` (`d645d83`)
- **2026-10-06** — Phase 2: `utils/sample_data.py` (CSV สังเคราะห์ใน `data/raw/`), `utils/pipeline.py` (grid ครบ, linear interpolation + ธง `Is_Imputed` 108/2,310 แถว, Min-Max outcome ต่อด้าน, ตารางประเทศ), `utils/data_loader.py` (per-capita, complaint rate /100k, efficiency ratio), `docs/DATA_SCHEMA.md`

## หมายเหตุ / ข้อสมมติ

- แหล่ง Open Data ภาครัฐ (GovSpend, สศช., 1111, ฯลฯ) ต้องดาวน์โหลดด้วยตนเองและรูปแบบไฟล์ต่างกัน จึงพัฒนาด้วย **ข้อมูลตัวอย่างสังเคราะห์ (synthetic)** ที่มี schema ตรงกับ Fact table ใน BRD ก่อน และทำ loader ให้สลับเป็นข้อมูลจริงได้ (Phase 9) — ตัวเลขในแดชบอร์ดช่วงนี้ **ไม่ใช่ข้อมูลจริง**
- แยก `fact_province_year` (GPP, Population) ออกจาก `fact_province_domain` เพราะเป็นระดับจังหวัด×ปี ถ้าไว้ใน fact เดียวตาม BRD จะ SUM ซ้ำ 6 เท่า
- เมื่อสเปคสองฉบับต่างกัน ยึด BRD เป็นหลัก (3 tab ตาม Section 5) และเพิ่ม view จาก handoff spec (Top/Bottom 10, correlation heatmap) เป็นส่วนเสริม
