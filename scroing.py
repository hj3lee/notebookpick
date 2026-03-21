from pathlib import Path
import pandas as pd
from datetime import datetime
#%%

folder = Path(r"C:\notebookpick\data\crawldata")
latest = sorted(folder.glob("crawldata_*.csv"), reverse=True)[0]
df = pd.read_csv(latest, encoding="utf-8-sig")


#%%

folder = Path(r"C:\notebookpick\data\basedata")
latest = sorted(folder.glob("basedata_*.csv"), reverse=True)[0]
df = pd.read_csv(latest, encoding="cp949")

#%%
# 1) 기준 그룹 정의
g14 = df[df["screen_size"] == 14]
g16 = df[df["screen_size"].isin([15.6, 16])]

mean_14 = g14['weight'].mean()
median_14 = g14['weight'].median()
std_14 = g14['weight'].std()

mean_16 = g16['weight'].mean()
median_16 = g16['weight'].median()
std_16 = g16['weight'].std()

print(f"14인치 평균, 중앙, 표준편차 {mean_14:.1f} {median_14:.1f} {std_14:.1f}")
print(f"16인치 평균, 중앙, 표준편차 {mean_16:.1f} {median_16:.1f} {std_16:.1f}")

x1, y1 = 14.0, median_14
x2, y2 = 15.8, median_16

m = (y2 - y1) / (x2 - x1)
b = y1 - m * x1

import numpy as np
weight_reference = {
	round(s, 1): round(m * s + b, 2)
	for s in np.arange(13.0, 19.1, 0.1)
}

sizes = [13.3, 14.0, 15.3, 16.0, 17.1, 18.0]

for s in sizes:
	print(f"{s}인치 →", weight_reference.get(s))