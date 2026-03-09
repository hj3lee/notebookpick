import pandas as pd, glob

user_input = {
	"samsung": 1,          # 1~10
	"lg": 1,               # 1~10
	"lenovo": 1,           # 1~10
	"hp": 1,               # 1~10
	"asus": 1,             # 1~10
	"acer": 1,             # 1~10

	"budget_min": 40,      # 40~200, int
	"budget_max": 200,     # 40~200, int
	"budget_prefer": 130,  # 40~200, int

	"size": 3,             # 1~5, int

	"color": 3,            # 1~6, int
	"weight": 3,           # 1~6, int
	"battery": 3,          # 1~6, int
	"gaming": 3,           # 1~6, int

	"ips": 0,              # 0 or 1
	"oled": 0              # 0 or 1
}



files = glob.glob("data/crawldata/crawldata_*.csv")
df = pd.read_csv(sorted(files)[-1])
df = df[df["sold_out"].isna()]

if user_input["budget_max"] == 200:
	df = df[df["price_current"] >= user_input["budget_min"] * 0.9]
else:
	df = df[(df["price_current"] >= user_input["budget_min"] * 0.9) & (df["price_current"] <= user_input["budget_max"] * 1.1)]
    
brand_default = {"samsung":8, "lg":8, "hp":6, "lenovo":4, "asus":4, "acer":4}

df["brand_score"] = df["brand"].apply(
	lambda b: user_input.get(b, brand_default[b]) - brand_default[b]
).clip(-10, 10)

df["price_score"] = (df["discount_rate"] * 1.2).clip(-24, 24)


if user_input["budget_prefer"] == 200:
	df["budgetfit_score"] = (5 - ((200 - df["price_current"]).clip(lower=0) / 200) * 20).clip(-5, 5)
else:
	df["budgetfit_score"] = (5 - (abs(df["price_current"] - user_input["budget_prefer"]) / user_input["budget_prefer"]) * 20).clip(-5, 5)
    
