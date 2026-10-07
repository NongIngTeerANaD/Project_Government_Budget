"""Central configuration: domains, years, colours, paths."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
REAL_DIR = DATA_DIR / "raw_real"  # committed snapshots of real open data (the app also fetches fresh copies at start-up)
PROCESSED_DIR = DATA_DIR / "processed"

FISCAL_YEARS = [2019, 2020, 2021, 2022, 2023]  # CE (BE 2562-2566)
BE_OFFSET = 543

# Standard 6 domains (BRD section 2 / 4.1)
DOMAINS = [
    {"id": 1, "key": "Education_Learning", "name_th": "การศึกษาและการเรียนรู้",
     "name_en": "Education & Learning", "kpi": "Avg. O-NET/TPAT score", "unit": "score 0-100", "color": "#4C78A8"},
    {"id": 2, "key": "Healthcare_Medical", "name_th": "สาธารณสุขและการแพทย์",
     "name_en": "Healthcare & Medical", "kpi": "Medical staff per 10k pop.", "unit": "per 10k", "color": "#E45756"},
    {"id": 3, "key": "Infrastructure_Transport", "name_th": "โครงสร้างพื้นฐาน โยธา และคมนาคม",
     "name_en": "Infrastructure & Transport", "kpi": "Infrastructure coverage", "unit": "%", "color": "#F58518"},
    {"id": 4, "key": "Agriculture_Environment", "name_th": "เกษตรและสิ่งแวดล้อม",
     "name_en": "Agriculture & Environment", "kpi": "Days with good AQI", "unit": "%", "color": "#54A24B"},
    {"id": 5, "key": "Administration_Safety", "name_th": "บริหารทั่วไปและความสงบเรียบร้อย",
     "name_en": "Administration & Safety", "kpi": "Crime clearance rate", "unit": "%", "color": "#B279A2"},
    {"id": 6, "key": "Economy_Tourism_Social", "name_th": "เศรษฐกิจ การท่องเที่ยว และสังคม",
     "name_en": "Economy, Tourism & Social", "kpi": "1 - poverty rate (inverted)", "unit": "%", "color": "#EECA3B"},
]
DOMAIN_IDS = [d["id"] for d in DOMAINS]
DOMAIN_NAME_TH = {d["id"]: d["name_th"] for d in DOMAINS}
DOMAIN_NAME_EN = {d["id"]: d["name_en"] for d in DOMAINS}
DOMAIN_COLOR = {d["id"]: d["color"] for d in DOMAINS}

# Mismatch weights (BRD 4.2)
MISMATCH_WEIGHTS = {"w1": 0.4, "w2": 0.4, "w3": 0.2}

COMPLAINT_RATE_PER = 100_000  # BRD section 7 risk 4


GEOJSON_PATH = DATA_DIR / "geo" / "thailand_provinces.geojson"
# Real 1111 complaint problem types -> 6 standard domains (decision agreed with the project owner).
# Domains 1-3 (education / health / infrastructure) have NO matching 1111 category -> no real data (left empty, never filled).
COMPLAINT_TYPE_TO_DOMAIN = {
    "ทรัพยากรธรรมชาติและสิ่งแวดล้อม": 4,
    "เศรษฐกิจ": 6,
    "สังคมและสวัสดิการ": 6,
    "กฎหมาย": 5,
    "การร้องเรียนกล่าวโทษเจ้าหน้าที่ของรัฐ": 5,
    "การเมือง-การปกครอง": 5,
    "พ.ร.บ. อำนวยความสะดวก": 5,
}
REAL_COMPLAINT_YEARS = [2020, 2021, 2022, 2023]
REAL_COMPLAINT_DOMAINS = [4, 5, 6]


# Real budget (Bureau of the Budget, data.go.th "รายการจัดสรรงบประมาณระดับจังหวัด") -> 6 standard domains.
# ASSUMPTION (project decision, documented in data/raw_real/SOURCES.md): the open data lists allocations by ministry,
# so each ministry is mapped to one domain; Dept. of Public Works and Town & Country Planning (under Interior) -> domain 3.
BUDGET_MIN_TO_DOMAIN = {
    "กระทรวงศึกษาธิการ": 1, "กระทรวงการอุดมศึกษา วิทยาศาสตร์ วิจัยและนวัตกรรม": 1,
    "กระทรวงสาธารณสุข": 2, "สภากาชาดไทย": 2,
    "กระทรวงคมนาคม": 3, "กระทรวงพลังงาน": 3,
    "กระทรวงเกษตรและสหกรณ์": 4, "กระทรวงทรัพยากรธรรมชาติและสิ่งแวดล้อม": 4,
    "กระทรวงกลาโหม": 5, "กระทรวงยุติธรรม": 5, "กระทรวงมหาดไทย": 5, "สำนักนายกรัฐมนตรี": 5, "กระทรวงการคลัง": 5,
    "กระทรวงการต่างประเทศ": 5, "หน่วยงานของศาล": 5, "หน่วยงานขององค์กรอิสระและองค์กรอัยการ": 5, "หน่วยงานของรัฐสภา": 5,
    "ส่วนราชการในพระองค์": 5, "จังหวัดและกลุ่มจังหวัด": 5, "องค์กรปกครองส่วนท้องถิ่น": 5, "หน่วยงานอื่นของรัฐ": 5,
    "ส่วนราชการไม่สังกัดสำนักนายกรัฐมนตรี กระทรวง หรือทบวง และหน่วยงานภายใต้การควบคุมดูแลของนายกรัฐมนตรี": 5,
    "กระทรวงพาณิชย์": 6, "กระทรวงอุตสาหกรรม": 6, "กระทรวงการท่องเที่ยวและกีฬา": 6,
    "กระทรวงการพัฒนาสังคมและความมั่นคงของมนุษย์": 6, "กระทรวงแรงงาน": 6, "กระทรวงวัฒนธรรม": 6,
    "กระทรวงดิจิทัลเพื่อเศรษฐกิจและสังคม": 6, "ทุนหมุนเวียน": 6, "รัฐวิสาหกิจ": 6,
}
BUDGET_PUBLIC_WORKS_KEYWORD = "โยธาธิการ"  # agency name containing this under กระทรวงมหาดไทย -> domain 3
REAL_BUDGET_YEARS = [2023]  # the open data on data.go.th currently covers FY2566 (2023) only
