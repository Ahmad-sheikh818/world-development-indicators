"""Generate the four headline charts for the WDI project README."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

OUT = os.path.expanduser("~/workspace/wdi-project")
df = pd.read_csv(f"{OUT}/data/wdi_merged.csv")
IMG = f"{OUT}/images"; os.makedirs(IMG, exist_ok=True)

AGG = {"AFE","AFW","ARB","CEB","CSS","EAP","EAR","EAS","ECA","ECS","EUU","FCS","HIC",
       "HPC","IBD","IBT","IDA","IDB","IDX","LCN","LDC","LIC","LMC","LMY","LTE","MAF",
       "MEA","MIC","MNA","NAC","OED","OSS","PRE","PSS","PST","SSA","SSF","SST","TEA",
       "TEC","TLA","TMN","TSA","TSS","UMC","WLD"}
c = df[~df["iso3"].isin(AGG)].copy()

plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})

def change(ind, y0=2000, y1=2022):
    piv = c.pivot_table(index=["iso3","country"], columns="year", values=ind)
    d = piv[[y0,y1]].dropna()
    d["delta"] = d[y1]-d[y0]
    return d.reset_index()

# 1. Life expectancy gainers
d = change("life_expectancy").sort_values("delta", ascending=False)
top = d.head(12).iloc[::-1]
fig, ax = plt.subplots(figsize=(9, 6))
ax.barh(top["country"], top["delta"], color="#2a7f62")
ax.axvline(d["delta"].median(), color="#c0392b", ls="--", lw=1.5,
           label=f"Median country: +{d['delta'].median():.1f}y")
ax.set_xlabel("Gain in life expectancy, 2000 → 2022 (years)")
ax.set_title("Where life expectancy grew fastest (2000–2022)")
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(f"{IMG}/life-expectancy-gainers.png", dpi=150); plt.close(fig)

# 2. Child mortality reducers
d = change("under5_mortality")
d["drop"] = d[2000]-d[2022]
top = d.sort_values("drop", ascending=False).head(10).iloc[::-1]
fig, ax = plt.subplots(figsize=(9, 6))
ax.barh(top["country"], top["drop"], color="#2471a3")
ax.set_xlabel("Fall in under-5 deaths per 1,000 live births, 2000 → 2022")
ax.set_title("Biggest drops in child mortality (2000–2022)")
fig.tight_layout(); fig.savefig(f"{IMG}/child-mortality-decline.png", dpi=150); plt.close(fig)

# 3. Poverty divergence
piv = c.pivot_table(index="year", columns="country", values="poverty_215")
countries = ["India","China","Bangladesh","Indonesia","Nigeria"]
fig, ax = plt.subplots(figsize=(10, 6))
for co in countries:
    s = piv[co].dropna()
    ax.plot(s.index, s.values, marker="o", ms=4, lw=2, label=co)
ax.set_ylabel("Share of population under $2.15/day (%)")
ax.set_title("Extreme poverty: Asia's escape vs Nigeria's stall")
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(f"{IMG}/poverty-divergence.png", dpi=150); plt.close(fig)

# 4. Preston curve
p = c[c.year==2022][["country","gdp_per_capita","life_expectancy"]].dropna()
p = p[p.gdp_per_capita > 0]
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(np.log10(p["gdp_per_capita"]), p["life_expectancy"], s=18, alpha=0.55, color="#5d6d7e")
for label in ["Sri Lanka","Lebanon","Nicaragua","Nigeria","Equatorial Guinea","Lesotho",
              "India","China","United States","Rwanda"]:
    r = p[p.country==label]
    if not r.empty:
        ax.annotate(label, (np.log10(r["gdp_per_capita"].iloc[0]), r["life_expectancy"].iloc[0]),
                    fontsize=9, xytext=(5,5), textcoords="offset points")
ax.set_xlabel("GDP per capita, 2022 (log scale, US$)")
ax.set_ylabel("Life expectancy, 2022 (years)")
ax.set_title("The Preston curve: richer usually means longer-lived — but not always")
fig.tight_layout(); fig.savefig(f"{IMG}/preston-curve.png", dpi=150); plt.close(fig)

print("charts done:", sorted(os.listdir(IMG)))
