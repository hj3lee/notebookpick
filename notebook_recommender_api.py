import pandas as pd, glob



def recommend(user_input):
    df_crawl = pd.read_csv(
        sorted(glob.glob("data/crawldata/crawldata_*.csv"))[-1],
        encoding="utf-8-sig"
    )
    df_crawl = df_crawl[df_crawl["sold_out"].isna()]
    
    
    
    df_manual = pd.read_csv(
        sorted(glob.glob("data/manualdata/manualdata_*.csv"))[-1],
        encoding="utf-8-sig"
    )
    
    df = pd.concat([df_crawl, df_manual], ignore_index=True)
    
    #budget_check
    if user_input["budget_max"] == 200:
    	df = df[df["price_current"] >= user_input["budget_min"] * 0.9]
    else:
    	df = df[(df["price_current"] >= user_input["budget_min"] * 0.9) & (df["price_current"] <= user_input["budget_max"] * 1.1)]

    
    
    brand_default = {"SAMSUNG":8, "LG":8, "HP":6, "Lenovo":4, "ASUS":4, "acer":4}
    
    df["brand_score"] = df["brand"].apply(
    	lambda b: (user_input.get(b, brand_default.get(b, 0)) - brand_default.get(b, 0)) * 2.5
    ).clip(-10, 10)
    
        #price_score
    df["price_score"] = (
        df["discount_rate"] * -1.2
    ).clip(-50, 24).round(2)
    
    # budgetfit_score
    df["budgetfit_score"] = (
        (
            # 조건 분기 포함한 원점수 계산
            5 - (
                (
                    (200 - df["price_current"]).clip(lower=0) / 200
                )
                if user_input["budget_prefer"] == 200
                else (
                    abs(df["price_current"] - user_input["budget_prefer"])
                    / user_input["budget_prefer"]
                )
            ) * 20
        )
        .pipe(lambda x: x - x.mean())
        .clip(-10, 10)
        .round(2)
    )
    #size_score
    df["size_score"] = 0
    
    if user_input["size"] != 3:
    	df.loc[df["screen_size"] <= 14, "size_score"] = [10,5,0,-5,-10][user_input["size"]-1]
        df.loc[df["screen_size"] >= 15.6, "size_score"] = [-10,-5,0,5,10][user_input["size"]-1]
        df.loc[(df["screen_size"] > 14) & (df["screen_size"] < 15.6), "size_score"] = [-3,0,0,2,1][user_input["size"]-1]
        
    #weight, battery, grahpic, display score
    standard_mult = [-2,-1,0,1,2,3]
    
    
    df["weight_score"] = (
        (-0.2 * df["weight_diff_pct"] * standard_mult[user_input["weight"] - 1])
        .pipe(lambda x: x - x.mean())
        .clip(-10, 15)
        .round(2)
    )
    
    df["battery_score"] = (
        (df["battery_time_centered"] * standard_mult[user_input["battery"] - 1])
        .pipe(lambda x: x - x.mean())
        .clip(-10, 10)
        .round(2)
    )
    
    df["graphic_score"] = (
        (df["graphic_centered"] * standard_mult[user_input["graphic"] - 1])
        .pipe(lambda x: x - x.mean())
        .clip(-10, 10)
        .round(2)
    )
    
    df["display_score"] = (
        (df["display_centered"] * standard_mult[user_input["display"] - 1])
        .pipe(lambda x: x - x.mean())
        .clip(-10, 10)
        .round(2)
    )
    
    df["budgetfit_score"] = (
        df["budgetfit_score"]
        .pipe(lambda x: x - x.mean())
        .clip(-10, 10)
        .round(2)
    )
    
    
    #ips, oled, window score
    df["ips_score"] = 0
    if user_input["ips"] == 1:
        df["ips_score"] = df["screen_type"].apply(lambda x: 5 if x == "ips" else -5)
    
    df["oled_score"] = 0
    if user_input["oled"] == 1:
        df["oled_score"] = df["screen_type"].apply(lambda x: 5 if x == "oled" else -5)
    
    df["window_score"] = 0
    if user_input["window"] == 1:
    	df["window_score"] = df["window"].apply(lambda x: 5 if x == 1 else -5)
        
    
    
    df["personal_score"] = (
        df["brand_score"]
        + df["budgetfit_score"]
        + df["size_score"]
        + df["weight_score"]
        + df["battery_score"]
        + df["graphic_score"]
        + df["display_score"]
        + df["ips_score"]
        + df["oled_score"]
        + df["window_score"]
    ).round(2)
    df["overall_score"] = (50+df["personal_score"] + df["price_score"]).round(2)
    
    result_df = df.sort_values("overall_score", ascending=False).head(15)
    
    return result_df[["link", "brand", "name", "price_current", "overall_score", "personal_score", "price_score"]]


