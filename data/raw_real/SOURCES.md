# Real data provenance (data/raw_real/)

| File | Source | Retrieved | Notes |
|------|--------|-----------|-------|
| `gpp_province.csv` | สศช. (NESDC) ผลิตภัณฑ์ภาคและจังหวัด — `GPP-2024-On-Web-1995-2024.xlsx`, sheets NE/NO/SO/EA/WE/CE/BKK&VIC, block "Gross provincial product at current market prices" | 2026-10-06 | หน่วยต้นฉบับ ล้านบาท → แปลง ×1,000,000 เป็นบาท; ปี 2020–2023 เป็นค่าปรับปรุง (r), 2024 เป็นค่าเบื้องต้น (p, ไม่ใช้) |
| `population_province.csv` | ไฟล์เดียวกัน แถว "Population (1,000 persons)" | 2026-10-06 | ประมาณการประชากรของ สศช. (ใช้คำนวณ GPP ต่อหัว) พันคน → ×1,000 เป็นคน |
| `nesdc_gpp_extract.json` | ค่าที่สกัดจากไฟล์ข้างต้น (77 แถว) + checksum ผลรวมรายคอลัมน์ | 2026-10-06 | ตรวจแล้ว: ผลรวม GPP 77 จังหวัด = 16.89 / 15.66 / 16.18 / 17.38 / 17.99 ล้านล้านบาท (2019–2023) |

หน้าเผยแพร่: https://www.nesdc.go.th/info/gross-regional-and-provincial-product/
ไฟล์: https://www.nesdc.go.th/wp-content/uploads/2026/03/GPP-2024-On-Web-1995-2024.xlsx

GDP ประเทศในแดชบอร์ด = ผลรวม GPP 77 จังหวัด (ประมาณ GDP ราคาประจำปี) ไม่ใช่ตัวเลข GDP จากตารางบัญชีประชาชาติโดยตรง
