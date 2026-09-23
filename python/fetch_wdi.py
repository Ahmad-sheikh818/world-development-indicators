"""Fetch World Development Indicators from the World Bank API (no key needed)."""
import requests, pandas as pd, time, os

BASE = "https://api.worldbank.org/v2/country/all/indicator"
OUT = os.path.expanduser("~/workspace/wdi-project/data")

INDICATORS = {
    "life_expectancy": "SP.DYN.LE00.IN",      # Life expectancy at birth, total (years)
    "gdp_per_capita": "NY.GDP.PCAP.CD",       # GDP per capita (current US$)
    "under5_mortality": "SH.DYN.MORT",        # Mortality rate, under-5 (per 1,000 live births)
    "literacy": "SE.ADT.LITR.ZS",             # Literacy rate, adult total (% of ages 15+)
    "population": "SP.POP.TOTL",              # Population, total
    "co2_total_kt": "EN.ATM.CO2E.KT",          # CO2 emissions (kt) -> per-capita computed later
    "poverty_215": "SI.POV.DDAY",             # Poverty headcount ratio at $2.15/day (%)
}

YEARS = "2000:2023"

def fetch(code):
    url = f"{BASE}/{code}"
    params = {"format": "json", "date": YEARS, "per_page": 20000}
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    payload = r.json()
    if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
        return pd.DataFrame()
    rows = []
    for rec in payload[1]:
        rows.append({
            "country": rec["country"]["value"],
            "iso3": rec.get("countryiso3code"),
            "year": int(rec["date"]),
            "value": rec["value"],
        })
    return pd.DataFrame(rows)

merged = None
for name, code in INDICATORS.items():
    df = fetch(code)
    if df.empty or "iso3" not in df.columns:
        print(f"{name}: EMPTY - skipped")
        continue
    df = df[df["iso3"].notna() & (df["iso3"] != "")]
    df.to_csv(f"{OUT}/wdi_{name}.csv", index=False)
    print(f"{name}: {len(df)} rows, {df['country'].nunique()} countries")
    d = df.rename(columns={"value": name})[["iso3", "country", "year", name]]
    merged = d if merged is None else merged.merge(d, on=["iso3", "country", "year"], how="outer")
    time.sleep(0.5)

merged.to_csv(f"{OUT}/wdi_merged.csv", index=False)
print("merged:", merged.shape)
print(merged.head(3).to_string())
