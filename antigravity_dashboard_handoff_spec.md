# 🚀 Handoff Specification: Thailand Public Data & Budgeting Analysis Dashboard

**Target System:** Antigravity AI / Dashboard Generation Agent  
**Project Name:** Thailand National & Provincial Budget vs. Performance & Complaints Analytics  
**Timeframe Alignment:** FY 2019 – 2023 (พ.ศ. 2562 – 2566)  
**Primary Language:** Thai / English (Bilingual UI)

---

## 1. Executive Summary & Dashboard Goal

เอกสารฉบับนี้จัดทำขึ้นเพื่อส่งต่อข้อกำหนด (Specification) ให้ระบบ Antigravity ดำเนินการสร้าง Interactive Dashboard สำหรับวิเคราะห์และเปรียบเทียบข้อมูลภาครัฐของประเทศไทย ย้อนหลัง 5 ปี (พ.ศ. 2562 - 2566) ใน 2 ระดับ:
1. **ระดับประเทศ (National Level):** วิเคราะห์ความเชื่อมโยงระหว่างงบประมาณรายจ่าย, ผลิตภัณฑ์มวลรวม (GDP), ตัวชี้วัดผลสัมฤทธิ์ (KPIs/Outcomes) และจำนวนเรื่องร้องเรียน
2. **ระดับจังหวัด (Provincial Level - 77 จังหวัด):** วิเคราะห์และจัดลำดับ (Ranking) งบประมาณจังหวัด, GPP/GPP per capita, ดัชนีผลลัพธ์ (HAI Index) และเรื่องร้องเรียนจำแนกรายพื้นที่

---

## 2. Standard 6 Target Domains (หมวดหมู่ข้อมูลมาตรฐาน 6 ด้าน)

ข้อมูลด้านงบประมาณ, ผลลัพธ์ และเรื่องร้องเรียนทั้งหมด จะต้องถูกจัดกลุ่มเข้าสู่ 6 ด้านมาตรฐานดังนี้:
1. **ด้านการศึกษาและการเรียนรู้** (Education & Learning)
2. **ด้านสาธารณสุขและการแพทย์** (Healthcare & Medical Public Services)
3. **ด้านโครงสร้างพื้นฐาน การโยธา และการคมนาคม** (Infrastructure, Public Works & Transportation)
4. **ด้านการเกษตรและสิ่งแวดล้อม** (Agriculture, Natural Resources & Environment)
5. **ด้านการบริหารงานทั่วไป บุคลากร และความสงบเรียบร้อย** (General Administration, Personnel & Public Safety)
6. **ด้านเศรษฐกิจ การท่องเที่ยว และการพัฒนาสังคม** (Economy, Tourism & Social Development)

---

## 3. Open Data Catalog & Download Links (แหล่งข้อมูลเปิดภาครัฐ)

### 3.1 ข้อมูลระดับประเทศ (National Open Datasets)
1. **ปริมาณการใช้งบประมาณรายด้าน (National Budget Allocation):**
   * **คำอธิบาย:** ข้อมูลการจัดสรรและเบิกจ่ายงบประมาณรายจ่ายประจำปี รวบรวมตามยุทธศาสตร์และกลุ่มภารกิจ 6 ด้าน
   * **แหล่งข้อมูล:** [GovSpend - ระบบภาษีไปไหน (DGA)](https://govspend.data.go.th/) | [Data.go.th - ชุดข้อมูลงบประมาณ](https://data.go.th/dataset?q=%E0%B8%87%E0%B8%9A%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%A1%E0%B8%B2%E0%B8%93%E0%B8%A3%E0%B8%B2%E0%B8%A2%E0%B8%88%E0%B9%88%E0%B8%B2%E0%B8%A2)
2. **ค่า GDP ประเทศไทย (National GDP):**
   * **คำอธิบาย:** ผลิตภัณฑ์มวลรวมภายในประเทศ ทั้ง Current Prices และ Chain Volume Measures (CVM) รายปี
   * **แหล่งข้อมูล:** [สำนักงานสภาพัฒนาการเศรษฐกิจและสังคมแห่งชาติ (สศช.)](https://www.nesdc.go.th/main.php?filename=national_account) | [Data.go.th - GDP](https://data.go.th/dataset?q=GDP)
3. **ผลลัพธ์การใช้งบประมาณรายด้าน (National Outcomes/KPIs):**
   * **คำอธิบาย:** ตัวชี้วัดผลสัมฤทธิ์และผลประโยชน์จากการใช้งบประมาณรายยุทธศาสตร์
   * **แหล่งข้อมูล:** [ระบบติดตาม eMENSCR (สศช.)](https://emenscr.nesdc.go.th/) | [สำนักงบประมาณ](https://www.bb.go.th/topic-detail.php?id=8050&mid=542)
4. **จำนวนการร้องเรียนของประเทศรายด้าน (National Complaints):**
   * **คำอธิบาย:** สถิติเรื่องร้องทุกข์ร้องเรียนจำแนกตามหมวดหมู่เรื่อง 6 ด้าน
   * **แหล่งข้อมูล:** [ศูนย์บริการประชาชน 1111 (สำนักงานปลัดนายกรัฐมนตรี)](https://www.1111.go.th/) | [Data.go.th - เรื่องร้องเรียน 1111](https://data.go.th/dataset?q=1111)

### 3.2 ข้อมูลระดับจังหวัด (Provincial Open Datasets - 77 จังหวัด)
5. **ปริมาณการใช้งบประมาณรวมของจังหวัด (Provincial Total Budget):**
   * **คำอธิบาย:** งบประมาณรายจ่ายประจำปีที่จังหวัดได้รับจัดสรรรวมทุกแหล่งเงิน
   * **แหล่งข้อมูล:** [กรมบัญชีกลาง - CGD Portal](https://www.cgd.go.th/) | [GovSpend Data](https://govspend.data.go.th/)
6. **ปริมาณการใช้งบประมาณรายด้านของจังหวัด (Provincial Domain Budget):**
   * **คำอธิบาย:** งบประมาณพัฒนาจังหวัด/กลุ่มจังหวัด และงบกระทรวงลงพื้นที่ จำแนกราย 6 ด้าน
   * **แหล่งข้อมูล:** [ระบบสารสนเทศยุทธศาสตร์จังหวัด (OSMCE)](http://www.osmce.mointerior.go.th/) | [Data.go.th - งบพัฒนาจังหวัด](https://data.go.th/dataset?q=%E0%B8%87%E0%B8%9A%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%A1%E0%B8%B2%E0%B8%93%E0%B8%A3%E0%B8%B2%E0%B8%A2%E0%B8%88%E0%B9%88%E0%B8%B2%E0%B8%A2)
7. **ค่า GDP ของจังหวัด (GPP / GPP Per Capita):**
   * **คำอธิบาย:** ผลิตภัณฑ์มวลรวมจังหวัด และผลิตภัณฑ์มวลรวมต่อหัว รายจังหวัด 77 จังหวัด
   * **แหล่งข้อมูล:** [สศช. - ผลิตภัณฑ์ภาคและจังหวัด (GPP)](https://www.nesdc.go.th/main.php?filename=gross_regional) | [Data.go.th - GPP](https://data.go.th/dataset?q=GPP)
8. **ผลลัพธ์การใช้งบประมาณรายด้านของจังหวัด (Provincial Outcomes / HAI Index):**
   * **คำอธิบาย:** ดัชนีความก้าวหน้าของคน (Human Achievement Index) และตัวชี้วัดผลสัมฤทธิ์ระดับจังหวัด
   * **แหล่งข้อมูล:** [สศช. - รายงานดัชนี HAI](https://www.nesdc.go.th/) | [กระทรวงมหาดไทย - PBIC](http://www.pbic.mointerior.go.th/)
9. **จำนวนการร้องเรียนของจังหวัดรายด้าน (Provincial Complaints):**
   * **คำอธิบาย:** เรื่องร้องเรียนร้องทุกข์จำแนกตามจังหวัดและหมวดหมู่ความเดือดร้อน 6 ด้าน
   * **แหล่งข้อมูล:** [ศูนย์ดำรงธรรม กระทรวงมหาดไทย](https://www.damrongdham.moe.go.th/) | [ระบบ 1111 รายพื้นที่](https://www.1111.go.th/)

---

## 4. Dashboard Architecture & UI Layout Specs for Antigravity

Antigravity ควรออกแบบหน้า Dashboard ให้รองรับ Views ดังต่อไปนี้:

### Tab 1: Executive Overview (National Level)
* **KPI Cards:** Total Budget, National GDP, Overall Outcome Score, Total Complaints (2019-2023 Trend).
* **Charts:**
  * Stacked Bar Chart: งบประมาณรายด้าน 6 ด้าน ย้อนหลัง 5 ปี.
  * Dual-Axis Line Chart: ความสัมพันธ์ระหว่าง GDP Growth Rate vs Outcome Score Trend.
  * Donut Chart: สัดส่วนเรื่องร้องเรียน 6 ด้าน.

### Tab 2: Provincial Deep-Dive (77 Provinces Analytics)
* **Interactive Map / Heatmap:** แผนที่ประเทศไทยแสดงระดับ GPP หรือ งบประมาณที่ได้รับจัดสรรรายจังหวัด.
* **Provincial Comparison Matrix:** Scatter Plot เปรียบเทียบ `Budget per Capita` vs `GPP per Capita` หรือ `Outcome Score`.
* **Top/Bottom 10 Ranking Chart:** สรุป 10 จังหวัดแรกที่มีจำนวนเรื่องร้องเรียนสูงสุด/ต่ำสุด และงบประมาณที่ใช้.

### Tab 3: Domain Correlation & ROI Analysis
* **Bubble Chart:** แกน X = Budget, แกน Y = Outcome Index, ขนาด Bubble = Complaints, สี Bubble = Domain 6 ด้าน.
* **Correlation Heatmap:** ตารางแสดงค่า Pearson Correlation ระหว่าง Budget vs GPP vs Complaints.

---

## 5. Technical Data Pipeline Instructions for Antigravity

```json
{
  "handoff_task": "GENERATE_DASHBOARD",
  "data_pipeline": {
    "year_range": ["2019", "2020", "2021", "2022", "2023"],
    "entity_levels": ["National", "Provincial_77"],
    "domains": [
      "Education_Learning",
      "Healthcare_Medical",
      "Infrastructure_Transport",
      "Agriculture_Environment",
      "Administration_Safety",
      "Economy_Tourism_Social"
    ],
    "transformation_rules": [
      "Convert fiscal years (BE 2562-2566) to CE (2019-2023).",
      "Normalize province names using ISO 3166-2:TH / TIS 1099 standard.",
      "Calculate Per-Capita values for Budget, GPP, and Complaints using registered population data.",
      "Calculate Efficiency Ratio = Outcome Index / Budget Expenditure."
    ]
  }
}
```

---

## 6. Prompt Command for Antigravity Agent

```text
Antigravity, please ingest this Markdown Specification Document and build an interactive, production-ready Dashboard web application.
Ensure all 9 open data categories (National & Provincial level across 2019-2023) are correctly structured into the 6 target domains.
Implement Tabbed UI (Executive Overview, Provincial Deep-Dive, and Domain Correlation Analysis) with interactive filters for Years, Provinces, and Domains.
```