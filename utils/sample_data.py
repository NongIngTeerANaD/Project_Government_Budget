"""Synthetic sample data generator.

Writes raw-style CSVs into data/raw/ using the SAME schema that the real open
datasets must be converted to (see docs/DATA_SCHEMA.md). Numbers are
SYNTHETIC - they only mimic realistic scales - and must not be read as facts.

Run:  python -m utils.sample_data
"""
import numpy as np
import pandas as pd

import config as C

SEED = 42
# national totals (THB) used only to give the synthetic data realistic scale
NATIONAL_GDP = dict(zip(C.FISCAL_YEARS, [16.9e12, 15.7e12, 16.2e12, 17.4e12, 17.9e12]))
NATIONAL_BUDGET = dict(zip(C.FISCAL_YEARS, [3.0e12, 3.2e12, 3.3e12, 3.1e12, 3.185e12]))
DOMAIN_BUDGET_SHARE = {1: 0.20, 2: 0.14, 3: 0.15, 4: 0.08, 5: 0.28, 6: 0.15}
# (low, high) of the raw KPI scale per domain
KPI_RANGE = {1: (30, 65), 2: (10, 40), 3: (60, 98), 4: (70, 100), 5: (40, 85), 6: (80, 99)}
# annual complaints per 100k population (typical level) per domain
COMPLAINT_BASE = {1: 12, 2: 18, 3: 40, 4: 20, 5: 30, 6: 15}

# well-known big / rich provinces (approx. population in millions, GPP-per-capita multiplier)
KNOWN = {
    "TH-10": (5.5, 3.6), "TH-11": (1.35, 3.0), "TH-12": (1.3, 1.4), "TH-13": (1.2, 1.5),
    "TH-20": (1.5, 3.2), "TH-21": (0.75, 6.0), "TH-74": (0.55, 3.0), "TH-83": (0.42, 2.2),
    "TH-30": (2.6, 0.9), "TH-40": (1.8, 1.0), "TH-50": (1.8, 1.1), "TH-34": (1.8, 0.7),
    "TH-41": (1.6, 0.8), "TH-84": (1.05, 1.3), "TH-90": (1.4, 1.1),
}
REGION_GPP_MULT = {"Central": 1.2, "East": 1.8, "North": 0.8, "Northeast": 0.65, "South": 1.0, "West": 1.1}


def generate(raw_dir=C.RAW_DIR, seed: int = SEED, missing_rate: float = 0.015) -> None:
    rng = np.random.default_rng(seed)
    prov = pd.read_csv(C.DATA_DIR / "dim_province.csv")
    n = len(prov)
    years = C.FISCAL_YEARS

    # --- static province traits -------------------------------------------------
    pop0 = np.array([KNOWN.get(p, (None,))[0] or rng.lognormal(np.log(0.55), 0.55) for p in prov.Province_ID]) * 1e6
    gpp_pc0 = np.array([
        100_000 * REGION_GPP_MULT[r] * (KNOWN[p][1] if p in KNOWN else rng.lognormal(0, 0.35))
        for p, r in zip(prov.Province_ID, prov.Region)
    ])
    real_pop, real_gpp = C.REAL_DIR / "population_province.csv", C.REAL_DIR / "gpp_province.csv"
    if real_pop.exists() and real_gpp.exists():  # keep synthetic parts consistent with the real GPP / population
        rp = pd.read_csv(real_pop).query("Fiscal_Year == @years[0]").set_index("Province_ID").Population
        rg = pd.read_csv(real_gpp).query("Fiscal_Year == @years[0]").set_index("Province_ID").GPP_Amount
        pop0 = rp.reindex(prov.Province_ID).to_numpy(float)
        gpp_pc0 = (rg / rp).reindex(prov.Province_ID).to_numpy(float)
    z_gpp = (np.log(gpp_pc0) - np.log(gpp_pc0).mean()) / np.log(gpp_pc0).std()
    quality = 0.45 * z_gpp + rng.normal(0, 0.9, n)  # latent "service quality" per province
    alloc_noise = rng.lognormal(0, 0.35, (n, len(C.DOMAIN_IDS)))
    is_bkk = (prov.Province_ID == "TH-10").to_numpy()

    rows_pop, rows_gpp, rows_bud, rows_out, rows_cmp = [], [], [], [], []
    for yi, y in enumerate(years):
        pop = pop0 * (1.003 ** yi)
        gpp = gpp_pc0 * pop * (1 + rng.normal(0, 0.02, n))
        gpp = gpp / gpp.sum() * NATIONAL_GDP[y]
        for i, pid in enumerate(prov.Province_ID):
            rows_pop.append((y, pid, int(pop[i])))
            rows_gpp.append((y, pid, float(gpp[i])))
        for di, d in enumerate(C.DOMAIN_IDS):
            w = pop ** 0.8 * alloc_noise[:, di] * np.where(is_bkk, 3.0, 1.0)
            bud = w / w.sum() * NATIONAL_BUDGET[y] * DOMAIN_BUDGET_SHARE[d]
            lo, hi = KPI_RANGE[d]
            lvl = 0.5 + 0.17 * quality + 0.08 * rng.normal(0, 1, n) + 0.015 * yi
            lvl += 0.04 * (np.log(bud / pop) - np.log(bud / pop).mean())
            out = lo + (hi - lo) * np.clip(lvl, 0.03, 0.97)
            rate = COMPLAINT_BASE[d] * rng.lognormal(0, 0.35, n) * np.exp(-0.25 * quality) * (1 + 0.1 * (yi == 2))
            cmp_ = rng.poisson(rate * pop / C.COMPLAINT_RATE_PER)
            for i, pid in enumerate(prov.Province_ID):
                rows_bud.append((y, pid, d, float(bud[i])))
                rows_out.append((y, pid, d, float(out[i])))
                rows_cmp.append((y, pid, d, int(cmp_[i])))

    k = ["Fiscal_Year", "Province_ID", "Domain_ID"]
    bud = pd.DataFrame(rows_bud, columns=k + ["Budget_Amount"])
    out = pd.DataFrame(rows_out, columns=k + ["Outcome_Raw_Value"])
    cmp_ = pd.DataFrame(rows_cmp, columns=k + ["Complaint_Count"])
    # inject missing values (data-risk #1 in BRD): drop a few rows entirely
    for df in (bud, out, cmp_):
        drop = rng.random(len(df)) < missing_rate
        df.drop(df.index[drop], inplace=True)

    raw_dir.mkdir(parents=True, exist_ok=True)
    bud.to_csv(raw_dir / "budget_province_domain.csv", index=False)
    out.to_csv(raw_dir / "outcome_province_domain.csv", index=False)
    cmp_.to_csv(raw_dir / "complaints_province_domain.csv", index=False)
    pd.DataFrame(rows_gpp, columns=["Fiscal_Year", "Province_ID", "GPP_Amount"]).to_csv(raw_dir / "gpp_province.csv", index=False)
    pd.DataFrame(rows_pop, columns=["Fiscal_Year", "Province_ID", "Population"]).to_csv(raw_dir / "population_province.csv", index=False)
    pd.DataFrame({"Fiscal_Year": years, "GDP_Amount": [NATIONAL_GDP[y] for y in years]}).to_csv(raw_dir / "gdp_national.csv", index=False)
    (raw_dir / "SAMPLE_DATA.flag").write_text("synthetic sample data - not real statistics\n")
    print(f"sample raw data written to {raw_dir}")


if __name__ == "__main__":
    generate()
