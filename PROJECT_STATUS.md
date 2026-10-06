# Project Status

อัปเดตล่าสุด: 2026-10-06

## สรุปสถานะ

| เฟส | งาน | สถานะ |
|-----|-----|-------|
| 0 | README จากเอกสารสเปค 3 ไฟล์ + commit | ✅ เสร็จ |
| 1 | Scaffold โครงสร้างโปรเจกต์ (`app.py`, `layouts/`, `callbacks/`, `utils/`, `data/`) | ⬜ ยังไม่เริ่ม |
| 2 | Data layer: Dim tables (77 จังหวัด, 6 ด้าน, ปี) + sample data generator + loader | ⬜ ยังไม่เริ่ม |
| 3 | Mismatch engine (`utils/mismatch.py`) + unit tests | ⬜ ยังไม่เริ่ม |
| 4 | App shell + Global filters (ปี / ด้าน / จังหวัด) | ⬜ ยังไม่เริ่ม |
| 5 | Tab 1: National Overview | ⬜ ยังไม่เริ่ม |
| 6 | Tab 2: Provincial Overview + cross-filtering | ⬜ ยังไม่เริ่ม |
| 7 | Tab 3: Mismatch Analysis | ⬜ ยังไม่เริ่ม |
| 8 | ทดสอบรวม / performance / ปรับ UI | ⬜ ยังไม่เริ่ม |
| 9 | นำข้อมูลจริงจาก Open Data เข้า pipeline | ⏸ รอผู้ใช้ดาวน์โหลดไฟล์ (ดูหมายเหตุ) |

## บันทึกความคืบหน้า

- **2026-10-06** — Phase 0: สร้าง `README.md` จาก `brd_dashboard_analysis_specification.md`, `antigravity_dashboard_handoff_spec.md`, `thailand_open_data_sources.md` และ commit (`c290a6d`)

## หมายเหตุ / ข้อสมมติ

- แหล่ง Open Data ภาครัฐ (GovSpend, สศช., 1111, ฯลฯ) ต้องดาวน์โหลดด้วยตนเองและรูปแบบไฟล์ต่างกัน จึงพัฒนาด้วย **ข้อมูลตัวอย่างสังเคราะห์ (synthetic)** ที่มี schema ตรงกับ Fact table ใน BRD ก่อน และทำ loader ให้สลับเป็นข้อมูลจริงได้ (Phase 9) — ตัวเลขในแดชบอร์ดช่วงนี้ **ไม่ใช่ข้อมูลจริง**
- เมื่อสเปคสองฉบับต่างกัน ยึด BRD เป็นหลัก (3 tab ตาม Section 5) และเพิ่ม view จาก handoff spec (Top/Bottom 10, correlation heatmap) เป็นส่วนเสริม
