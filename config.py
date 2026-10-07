"""Central configuration: domains, years, colours, paths."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
REAL_DIR = DATA_DIR / "raw_real"  # real open-data extracts; take precedence over synthetic data/raw
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
SAMPLE_FLAG = RAW_DIR / "SAMPLE_DATA.flag"


def is_sample_data() -> bool:
    """True while the dashboard runs on synthetic data (flag written by utils.sample_data)."""
    return SAMPLE_FLAG.exists()


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
