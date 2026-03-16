import pandas as pd
from sklearn.linear_model import LinearRegression

# 1. CSV 읽기
path = r"C:/notebookpick/data/basedata/basedata_260315.csv"

try:
    df = pd.read_csv(path, encoding="utf-8-sig")
except:
    df = pd.read_csv(path, encoding="cp949")

df = df[["weight", "screen_size"]].dropna()

# 2. 회귀
X = df[["screen_size"]]
y = df["weight"]

model = LinearRegression()
model.fit(X, y)

a = model.intercept_
b = model.coef_[0]

print("회귀식:")
print(f"weight = {a:.4f} + {b:.4f} * screen_size")