"""Quick EDA on merged WDI data to find storylines."""
import pandas as pd, numpy as np, os

OUT = os.path.expanduser("~/workspace/wdi-project/data")
df = pd.read_csv(f"{OUT}/wdi_merged.csv")

AGG = {"AFE","AFW","ARB","CEB","CSS","EAP","EAR","EAS","ECA","ECS","EUU","FCS","HIC",
       "HPC","IBD","IBT","IDA","IDB","IDX","LCN","LDC","LIC","LMC","LMY","LTE","MAF",
       "MEA","MIC","MNA","NAC","OED","OSS","PRE","PSS","PST","SSA","SSF","SST","TEA",
       "TEC","TLA","TMN","TSA","TSS","UMC","WLD"}
c = df[~df["iso3"].isin(AGG)].copy()
print("real countries:", c["iso3"].nunique())

# coverage per indicator (latest year 2023, or 2022)
for ind in ["life_expectancy","gdp_per_capita","under5_mortality","literacy","poverty_215","population"]:
    for yr in (2023, 2022):
        n = c[c.year==yr][ind].notna().sum()
        if n > 0:
            print(f"{ind}: {n} countries with data in {yr}")
            break

def change(ind, y0=2000, y1=2022):
    piv = c.pivot_table(index=["iso3","country"], columns="year", values=ind)
    cols = [y for y in (y0, y1) if y in piv.columns]
    d = piv[cols].dropna()
    d["change"] = d[y1] - d[y0]
    return d.reset_index().sort_values("change", ascending=False)

print("\n--- Top 10 life-expectancy gainers 2000->2022 ---")
le = change("life_expectancy")
print(le[["country","change"]].head(10).to_string(index=False))
print("median gain:", round(le["change"].median(),1))

print("\n--- Top 10 under-5 mortality reducers 2000->2022 ---")
m = change("under5_mortality")
print(m[["country","change"]].head(10).to_string(index=False))

print("\n--- Poverty ($2.15/day) change 2000->latest available ---")
piv = c.pivot_table(index=["iso3","country"], columns="year", values="poverty_215")
for target in ["India","China","Bangladesh","Nigeria","Indonesia","Ethiopia"]:
    row = piv[piv.index.get_level_values("country")==target]
    if not row.empty:
        s = row.iloc[0].dropna()
        if len(s) >= 2:
            print(f"{target}: {s.iloc[0]:.1f}% ({int(s.index[0])}) -> {s.iloc[-1]:.1f}% ({int(s.index[-1])})")

print("\n--- Preston curve: GDP per capita vs life expectancy (2022) ---")
p = c[c.year==2022][["gdp_per_capita","life_expectancy"]].dropna()
print("countries:", len(p), "| corr:", round(p["gdp_per_capita"].corr(p["life_expectancy"]),3))
print("log-gdp corr:", round(np.log(p["gdp_per_capita"]).corr(p["life_expectancy"]),3))
# outliers: high GDP, low LE and vice versa
p2 = c[c.year==2022][["country","gdp_per_capita","life_expectancy"]].dropna()
p2["log_gdp"] = np.log(p2["gdp_per_capita"])
coef = np.polyfit(p2["log_gdp"], p2["life_expectancy"], 1)
p2["pred"] = coef[0]*p2["log_gdp"] + coef[1]
p2["resid"] = p2["life_expectancy"] - p2["pred"]
print("\nBiggest positive outliers (live longer than income predicts):")
print(p2.nlargest(8,"resid")[["country","gdp_per_capita","life_expectancy"]].to_string(index=False))
print("\nBiggest negative outliers:")
print(p2.nsmallest(8,"resid")[["country","gdp_per_capita","life_expectancy"]].to_string(index=False))

print("\n--- India snapshot ---")
ind = c[c.country=="India"].set_index("year")
for indn in ["life_expectancy","gdp_per_capita","under5_mortality","poverty_215","literacy"]:
    s = ind[indn].dropna()
    if len(s): print(f"{indn}: {s.iloc[0]:.1f} ({int(s.index[0])}) -> {s.iloc[-1]:.1f} ({int(s.index[-1])})")
