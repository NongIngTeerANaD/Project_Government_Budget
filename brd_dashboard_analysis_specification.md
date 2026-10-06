# Business Requirements Document (BRD)
## Project: Thailand Budget, GDP, Outcome & Complaint Analytics Dashboard

---

## 1. Executive Summary & Objectives

### 1.1 วัตถุประสงค์ (Objectives)
1. **เพื่อติดตามและประเมินประสิทธิภาพการจัดสรรงบประมาณ:** เปรียบเทียบงบประมาณแผ่นดิน ผลิตภัณฑ์มวลรวม (GDP/GPP) ผลสัมฤทธิ์การดำเนินงาน (Outcomes) และข้อร้องเรียนของประชาชน ย้อนหลังในระดับประเทศและรายจังหวัด (77 จังหวัด)
2. **เพื่อวิเคราะห์ความไม่สอดคล้อง (Mismatch Analysis):** ค้นหาพื้นที่และยุทธศาสตร์ที่มีการจัดสรรงบประมาณสูง แต่ผลลัพธ์ต่ำ หรือยังมีข้อร้องเรียนสูง เพื่อเป็นข้อมูลสนับสนุนการตัดสินใจเชิงนโยบายและการจัดสรรงบประมาณในอนาคต

### 1.2 กลุ่มผู้ใช้งานเป้าหมาย (Target Users) & Use Cases
* **ผู้บริหาร/นักนโยบาย (Policy Makers & Executives):** ส่องภาพรวมระดับประเทศ ดูแนวโน้มสัดส่วนงบประมาณต่อ GDP และระบุยุทธศาสตร์ที่ควรเพิ่ม/ปรับลดงบประมาณ
* **สำนักงบประมาณ / กระทรวงการคลัง (Budget Analysts):** ตรวจสอบประสิทธิภาพการเบิกจ่ายงบประมาณระดับจังหวัด และวิเคราะห์ความคุ้มค่า (ROI/Efficiency) รายยุทธศาสตร์
* **ภาคประชาสังคมและประชาชน (Public & Civil Society):** ตรวจสอบความโปร่งใส ติดตามผลลัพธ์ของโครงการภาครัฐ และดูข้อร้องเรียนในพื้นที่ตนเอง

---

## 2. Standard Taxonomy (หมวดหมู่ข้อมูลมาตรฐาน 6 ด้าน)

งบประมาณ ผลสัมฤทธิ์ และข้อร้องเรียน ทั้งหมดจะถูกจัดหมวดหมู่เข้าสู่ 6 ด้านมาตรฐานดังนี้:
1. **ด้านการศึกษาและการเรียนรู้** (Education & Learning)
2. **ด้านสาธารณสุขและการแพทย์** (Healthcare & Medical Public Services)
3. **ด้านโครงสร้างพื้นฐาน การโยธา และคมนาคม** (Infrastructure, Public Works & Transportation)
4. **ด้านการเกษตรและสิ่งแวดล้อม** (Agriculture, Natural Resources & Environment)
5. **ด้านการบริหารงานทั่วไป บุคลากร และความสงบเรียบร้อย** (General Administration, Personnel & Public Safety)
6. **ด้านเศรษฐกิจ การท่องเที่ยว และการพัฒนาสังคม** (Economy, Tourism & Social Development)

---

## 3. Data Dictionary, Sources & Data Model

### 3.1 Data Dictionary & Sources

| ชื่อชุดข้อมูล | คำอธิบาย | แหล่งข้อมูลเปิด (Open Data Source) | ความถี่การอัปเดต |
| :--- | :--- | :--- | :--- |
| **National & Provincial Budget** | งบประมาณรายจ่ายจำแนกตามด้าน 6 ด้าน | [GovSpend (ภาษีไปไหน - DGA)](https://govspend.data.go.th) / [สำนักงบประมาณ](https://www.bb.go.th) | รายปี (Fiscal Year) |
| **National GDP & Provincial GPP** | ผลิตภัณฑ์มวลรวมประเทศ / จังหวัด และ GPP Per Capita | [สำนักงานสภาพัฒนาการเศรษฐกิจและสังคมแห่งชาติ (สศช.)](https://www.nesdc.go.th) | รายปี |
| **Domain Outcomes / KPIs** | ตัวชี้วัดผลลัพธ์รายด้าน (ดูรายละเอียดข้อ 4.1) | [ระบบ eMENSCR](https://emenscr.nesdc.go.th) / สพฐ. / สป.สธ. / สสช. | รายปี |
| **Public Complaints** | จำนวนเรื่องร้องเรียนจำแนกตามด้าน และจังหวัด | [ศูนย์บริการประชาชน 1111](https://www.1111.go.th) / [ศูนย์ดำรงธรรม มท.](https://www.damrongdham.moe.go.th) | รายเดือน / รายปี |
| **Population Data** | ประชากรราษฎรรายจังหวัด | [สำนักบริหารการทะเบียน กรมการปกครอง](https://stat.bora.dopa.go.th) | รายปี |

### 3.2 Data Model Architecture (Star Schema)

ข้อมูลจัดเก็บในรูปแบบ Fact Tables และ Dimension Tables โดยมี Primary Key เชื่อมโยงหลักคือ **`Province_ID` + `Fiscal_Year` + `Domain_ID`**

```
                  +-----------------------+
                  |    Dim_Province       |
                  +-----------------------+
                  | PK  Province_ID       |
                  |     Province_Name_TH  |
                  |     Province_Name_EN  |
                  |     Region            |
                  |     Lat / Long        |
                  +-----------+-----------+
                              |
                              | 1:N
                              v
+------------------+    +----------------------------------+    +------------------+
|    Dim_Year      |    |       Fact_Provincial_Data       |    |   Dim_Domain     |
+------------------+    +----------------------------------+    +------------------+
| PK  Fiscal_Year  |--->| FK1  Fiscal_Year                 |<---| PK  Domain_ID    |
+------------------+ N:1| FK2  Province_ID                 |1:N |     Domain_Name  |
                        | FK3  Domain_ID                   |    |     KPI_Name     |
                        |      Budget_Amount (THB)         |    |     KPI_Unit     |
                        |      GPP_Amount (THB)            |    +------------------+
                        |      Outcome_Raw_Value           |
                        |      Outcome_Normalized_Score    |
                        |      Complaint_Count             |
                        |      Population                 |
                        +----------------------------------+
```

---

## 4. Outcome KPIs Definition & Mismatch Calculation Formula

### 4.1 นิยามตัวชี้วัดผลสัมฤทธิ์รายด้าน (Domain Outcome KPIs)

| ด้านงบประมาณ | ตัวชี้วัดผลสัมฤทธิ์ (KPI) | หน่วยวัด | ทิศทางค่าที่ดี |
| :--- | :--- | :--- | :--- |
| **1. การศึกษาและการเรียนรู้** | คะแนนเฉลี่ยการทดสอบ O-NET/TPAT หรือ อัตราการเรียนต่อ | คะแนน (0-100) / % | ยิ่งสูงยิ่งดี ($+$) |
| **2. สาธารณสุขและการแพทย์** | อัตราบุคลากรทางการแพทย์ต่อประชากร หรือ อัตราการเข้าถึงบริการ | % หรือ ต่อประชากร 10k | ยิ่งสูงยิ่งดี ($+$) |
| **3. โครงสร้างพื้นฐาน โยธา คมนาคม** | ดัชนีคุณภาพถนน/การขนส่ง หรือ ความครอบคลุมสาธารณูปโภค | % ความครอบคลุม | ยิ่งสูงยิ่งดี ($+$) |
| **4. เกษตรและสิ่งแวดล้อม** | ดัชนีคุณภาพอากาศ (Days with Good AQI) / ผลผลิตต่อไร่ | % วันอากาศดี / บาทต่อไร่ | ยิ่งสูงยิ่งดี ($+$) |
| **5. บริหารทั่วไป และความสงบ** | อัตราคดีอาชญากรรมที่คลี่คลายได้ หรือ เวลาตอบสนองภัยพิบัติ | % / ชั่วโมง | ยิ่งสูงยิ่งดี ($+$) |
| **6. เศรษฐกิจ เที่ยว สังคม** | รายได้จากการท่องเที่ยวต่อหัว หรือ ดัชนีความยากจน (Poverty Rate) | บาท หรือ % (Inverted) | ยิ่งสูงยิ่งดี ($+$) |

### 4.2 สูตรการคำนวณ Mismatch Score (Tab 3)

เพื่อแปลงตัวแปรต่าง ๆ ให้เปรียบเทียบกันได้ จะใช้เทคนิค **Min-Max Normalization (Scale 0 - 100)** ก่อนคำนวณคะแนน Mismatch:

1. **Standard Normalization:**
   $$\text{Normalized\_Score} = \left( \frac{X - X_{\min}}{X_{\max} - X_{\min}} \right) \times 100$$

2. **ตัวแปรย่อยสำหรับการคำนวณ Mismatch:**
   * $B_{\text{capita}}$ = Normalization ของ งบประมาณต่อหัว (${\text{Budget}} / {\text{Population}}$)
   * $O_{\text{score}}$ = Normalization ของ ค่าผลลัพธ์การดำเนินงาน (Outcome Score)
   * $C_{\text{rate}}$ = Normalization ของ อัตราการร้องเรียนต่อประชากร (${\text{Complaints}} / {\text{Population}}$)
   * $G_{\text{capita}}$ = Normalization ของ GPP ต่อหัว (${\text{GPP}} / {\text{Population}}$)

3. **สูตร Mismatch Score (จังหวัด $i$, ด้าน $j$):**
   $$\text{Mismatch\_Score}_{i,j} = w_1 \cdot \max(0, B_{\text{capita}} - O_{\text{score}}) + w_2 \cdot (B_{\text{capita}} \times C_{\text{rate}}) + w_3 \cdot \max(0, B_{\text{capita}} - G_{\text{capita}})$$

   * *หมายเหตุ:* กำหนดน้ำหนักมาตรฐาน $w_1 = 0.4$ (งบสูงแต่ผลลัพธ์ต่ำ), $w_2 = 0.4$ (งบสูงแต่ร้องเรียนสูง), $w_3 = 0.2$ (งบไม่สอดคล้องกับขนาดเศรษฐกิจ)

---

## 5. Dashboard Layout & Functional Requirements

### 5.1 Global Filters (ตัวกรองกลางด้านบนระบบ)
* **Year Selector:** Dropdown/Slider เลือกระบุปีงบประมาณ (เช่น 2019 - 2023)
* **Domain Selector:** Multi-select Dropdown เลือกด้านงบประมาณ (1-6 ด้าน)
* **Province Selector (Tab 2 & 3):** Dropdown เลือกจังหวัด (ค่าเริ่มต้น: เลือกทั้งหมด 77 จังหวัด)

---

### 5.2 Tab 1: ภาพรวมระดับประเทศ (National Overview)
* **KPI Cards (สรุปค่าของปีที่เลือก):**
  1. งบประมาณรวมทั้งประเทศ (Trillion THB)
  2. GDP รวมประเทศ (Trillion THB)
  3. สัดส่วนงบประมาณต่อ GDP (%)
  4. จำนวนเรื่องร้องเรียนรวมทั้งประเทศ (Cases)
* **Visualizations:**
  1. **Bar Chart:** ปริมาณการใช้งบประมาณแยกตาม 6 ด้านในแต่ละปี
  2. **Dual-Axis Combo Chart:** ค่า GDP ประเทศ (Bar/Area) ซ้อนกับงบประมาณรวม (Line) เพื่อดูแนวโน้มการเติบโต
  3. **Grouped Line Chart:** ผลลัพธ์การใช้งบประมาณ (Outcome Score) แยกตาม 6 ด้านในแต่ละปี
  4. **Stacked Bar Chart:** จำนวนการร้องเรียนของประเทศแต่ละปี จำแนกตาม 6 ด้าน

---

### 5.3 Tab 2: ภาพรวมระดับจังหวัด (Provincial Overview)
* **Interactive Cross-Filtering Mechanism:** เมื่อผู้ใช้คลิกเลือกจังหวัดบนแผนที่ หรือในกราฟใด ๆ ทุกวิจิทใน Tab 2 จะต้องอัปเดตกรองข้อมูลเป็นของจังหวัดนั้นทันที
* **Visualizations:**
  1. **Choropleth Map (แผนที่ประเทศไทย 77 จังหวัด):** แสดงงบประมาณที่แต่ละจังหวัดได้รับตาม Color Scale
  2. **Horizontal Bar Chart:** การใช้งบประมาณแยกตาม 6 ด้านของจังหวัดที่เลือก
  3. **Line Chart:** ค่า GDP (GPP) ของจังหวัดย้อนหลังแต่ละปี
  4. **Radar/Bar Chart:** คะแนนผลลัพธ์การใช้งบประมาณรายด้านของจังหวัด
  5. **Donut Chart:** จำนวนการร้องเรียนของจังหวัด แยกตาม 6 ด้าน
  6. **Interactive Data Table:** จัดอันดับจังหวัด (Ranking) โดยผู้ใช้สามารถกด Sort เรียงตามตัวชี้วัดที่ต้องการได้ (งบประมาณ, GPP, ผลลัพธ์, ข้อร้องเรียน)

---

### 5.4 Tab 3: วิเคราะห์ความไม่สอดคล้อง (Mismatch Analysis)
* **Visualizations:**
  1. **Scatter Plot (Budget vs Outcome):** แกน X = งบประมาณต่อหัว, แกน Y = คะแนนผลลัพธ์ (Outcome) แยกสีตามภูมิภาค/ด้าน
  2. **Bubble Chart (Budget vs Complaints):** แกน X = งบประมาณรวม, แกน Y = จำนวนการร้องเรียน, ขนาด Bubble = ประชากร
  3. **Scatter Plot (Budget vs GPP):** แกน X = GPP จังหวัด, แกน Y = งบประมาณที่ได้รับ (สะท้อนว่าพื้นที่เศรษฐกิจเล็กได้งบเหมาะสมหรือไม่)
  4. **Heatmap Matrix (Province vs Domain Mismatch):** แสดงความร้อนของคะแนน Mismatch Score (แกน Y = 77 จังหวัด, แกน X = 6 ด้าน)
  5. **Summary Table (Top 10 Mismatch Priority List):** ตารางสรุป 10 อันดับแรกของ "จังหวัด x ด้าน" ที่ได้คะแนน Mismatch สูงสุด พร้อมระบุสาเหตุที่ควรทบทวนการจัดสรรงบประมาณ

---

## 6. Technical Architecture & Non-Functional Requirements

### 6.1 Technical Architecture Diagram

```
+-----------------------------------------------------------------------+
|                            USER BROWSER                               |
|                  Plotly Dash Frontend (React Components)              |
+-----------------------------------------------------------------------+
                                   ^
                                   | WebSockets / HTTP
                                   v
+-----------------------------------------------------------------------+
|                         PYTHON DASH BACKEND                           |
|  +-------------------+  +--------------------+  +------------------+  |
|  | Dash Callbacks    |  | Cross-Filtering    |  | Mismatch Engine  |  |
|  | (State Management)|  | Core Engine        |  | (Polars/Pandas)  |  |
|  +-------------------+  +--------------------+  +------------------+  |
+-----------------------------------------------------------------------+
                                   ^
                                   | SQL Queries / In-Memory DataFrames
                                   v
+-----------------------------------------------------------------------+
|                            DATA LAYER                                 |
|                  DuckDB / PostgreSQL / Parquet Files                  |
+-----------------------------------------------------------------------+
```

### 6.2 Tech Stack
* **Language:** Python 3.10+
* **Framework:** Plotly Dash (Dash Core Components, Dash HTML Components, Dash Bootstrap Components)
* **Data Processing:** Pandas / Polars / DuckDB
* **Visualization:** Plotly Express / Plotly Graph Objects

### 6.3 Non-Functional Requirements
1. **Performance:** แผงควบคุมต้องโหลดและตอบสนองการทำ Cross-filtering ภายในเวลาไม่เกิน 1.5 วินาที
2. **Usability & Responsiveness:** รองรับการแสดงผลความละเอียดหน้าจอมาตรฐาน Desktop (1920x1080) และ Laptop (1366x768)
3. **Maintainability:** โครงสร้างโค้ดต้องแยกส่วนชัดเจน (`app.py`, `layouts/`, `callbacks/`, `utils/mismatch.py`)

---

## 7. Data Risks, Limitations & Mitigation Strategies

| ข้อจำกัด/ความเสี่ยงของข้อมูล | ผลกระทบ | แนวทางแก้ไขและชดเชย (Mitigation Strategy) |
| :--- | :--- | :--- |
| **1. ข้อมูลบางจังหวัด/บางปีไม่ครบ (Missing Data)** | อาจทำให้การเปรียบเทียบข้ามปีหรือข้ามจังหวัดคลาดเคลื่อน | ใช้เทคนิค Linear Interpolation สำหรับปีที่หายไป หรือใส่สัญลักษณ์แจ้งเตือน `*Data Incomplete` ในหน้า UI |
| **2. ความเหลื่อมของปีงบประมาณกับปีปฏิทิน** | งบประมาณนับตามปีงบประมาณ (ก.ย.-ต.ค.) แต่ GDP/GPP นับตามปีปฏิทิน | กำหนดเกณฑ์มาตรฐาน Alignment ในระบบ Data Pipeline ให้ยึด Fiscal Year เป็นหลัก |
| **3. ความต่างของหน่วยวัด Outcome แต่ละด้าน** | ไม่สามารถนำมาเปรียบเทียบข้ามด้านได้โดยตรง | ใช้ **Min-Max Normalization (0-100 Score)** ก่อนนำไปเข้าสูตร Mismatch Score |
| **4. ข้อมูลร้องเรียนมี Bias จากความหนาแน่นประชากร** | จังหวัดใหญ่จะมียอดร้องเรียนสูงกว่าเสมอ | คำนวณเป็น **Complaint Rate per 100,000 Population** เสมอเมื่อทำการเปรียบเทียบ |

---

## 8. Handoff Instruction for Antigravity

```text
Antigravity, please build a production-grade Plotly Dash application in Python based on this BRD.
Key implementation tasks:
1. Setup a modular Dash app with 3 Tabs as specified in Section 5.
2. Implement cross-filtering callbacks across all charts within Tab 2 (map click -> updates all graphs).
3. Implement the Mismatch Score logic using the formula in Section 4.2 and display the Top 10 matrix in Tab 3.
4. Use clean, modern CSS/Dash Bootstrap Components for layout structure.
```