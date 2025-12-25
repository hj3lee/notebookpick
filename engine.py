# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 21:43:09 2025

@author: hj3le
"""

import pandas as pd
from datetime import datetime

#%% 1. 엑셀 불러오기
# 같은 폴더에 notebookdb.xlsx 가 있을 때
df = pd.read_excel("notebookdb2.xlsx")

weight_reference = {13.0:115.56,13.1:117.44,13.2:119.33,13.3:121.78,13.4:123.11,13.5:125.00,
                    13.6:126.89,13.7:128.78,13.8:130.67,13.9:132.56,14.0:135.00,14.1:136.89,
                    14.2:138.78,14.3:140.67,14.4:142.56,14.5:144.44,14.6:146.33,14.7:148.22,
                    14.8:150.11,14.9:152.00,15.0:153.89,15.1:155.78,15.2:157.67,15.3:159.56,
                    15.4:161.44,15.5:163.33,15.6:165.22,15.7:167.11,15.8:169.00,15.9:170.89,
                    16.0:172.78,16.1:174.67,16.2:176.56,16.3:178.44,16.4:180.33,16.5:182.22,
                    16.6:184.11,16.7:186.00,16.8:187.89,16.9:189.78,17.0:191.67,17.1:193.56,
                    17.2:195.44,17.3:197.33,17.4:199.22,17.5:201.11,17.6:203.00,17.7:204.89,
                    17.8:206.78,17.9:208.67,18.0:210.56,18.1:212.44,18.2:214.33,18.3:216.22,
                    18.4:218.11,18.5:220.00,18.6:221.89,18.7:223.78,18.8:225.67,18.9:227.56,19.0:229.44}
color_reference = 6.75
gaming_reference = 5
resolution_reference=6.6


#%% 점수계산 함수들

def price_score(price_reference, price_current):
    
    "적정가 대비 현재가격의 할인율을 기반으로 -20점 ~ +20점 점수를 산출한다."

    # 할인율 계산(양수 = 할인)
    discount_ratio = (price_reference - price_current) / price_reference
    discount_percent = discount_ratio * 100 * 1.2  # % 변환

    # 점수 매핑 (예: -9% → +10.8점)
    price_score = discount_percent

    # 점수 범위 제한
    if price_score > 24:
        price_score = 24
    elif price_score < -24:
        price_score = -24

    return round(price_score, 2)


def budget_fit_scores(prices_current, budget_prefer):
    """
    예산 내 노트북들의 가격 리스트로부터 zero-sum 예산 적합성 점수 생성.
    보정 후 최종 점수를 1/2로 줄인다.
    """

    # 1) raw score
    raw = [-abs(p - budget_prefer) for p in prices_current]

    # 2) 평균
    mean_raw = sum(raw) / len(raw)

    # 3) zero-sum 변환
    zero_sum_scores = [r - mean_raw for r in raw]

    # 4) 스케일 조정 (1/2 배)
    budget_fit_score = [s * 0.25 for s in zero_sum_scores]

    return budget_fit_score


def weight_standard_scores(weight_diff_pct):
    """
    df['무게_편차_%'] 리스트로부터 zero-sum 무게 적합성 점수 생성.
    - 기준보다 가벼울수록(무게_편차_%가 음수일수록) 높은 점수가 되도록 설계.
    - budget_fit_scores와 같은 형식 유지.
    """

    raw = [-(w) for w in weight_diff_pct]
    mean_raw = sum(raw) / len(raw)
    zero_sum_scores = [r - mean_raw for r in raw]
    weight_standard_scores = [s * 0.25 for s in zero_sum_scores]

    return weight_standard_scores

def screen_size_scores(screen_sizes, size_pref):
    """
    화면크기 리스트와 사용자 선호(size_pref: 1~5)를 받아
    각 노트북의 화면크기 점수 리스트를 반환한다."""

    scores = []
    for s in screen_sizes:
        score = 0

        # 3: 중립
        if size_pref == 3:
            score = 0

        # 2: 14인치 선호
        elif size_pref == 2:
            if s <= 14:
                score = +5
            elif s >= 15.6:
                score = -5
            else: score = -2

        # 4: 16인치 선호
        elif size_pref == 4:
            if s >= 16:
                score = +5
            elif s <= 14:
                score = -5
            else: score = +2


        # 1: 14인치 강력 선호
        elif size_pref == 1:
            if s <= 14:
                score = +10
            elif s >= 15.6:
                score = -10
            else: score = -3


        # 5: 16인치 강력 선호
        elif size_pref == 5:
            if s >= 16:
                score = +10
            elif s <= 14:
                score = -10
            else: score = -3
            
        scores.append(score)

    return scores

def gaming_standard_scores(gaming):

    raw = [(g - gaming_reference) for g in gaming]
    mean_raw = sum(raw) / len(raw)
    zero_sum_scores = [r - mean_raw for r in raw]

    gaming_scores = [s * 1 for s in zero_sum_scores]  # scaling factor는 조정 가능
    return gaming_scores


def color_standard_scores(color_values):
    """

    색역이 높을수록 좋은 점수를 주는 zero-sum 방식.
    """
    raw = [(c - color_reference) for c in color_values]
    mean_raw = sum(raw) / len(raw)
    zero_sum_scores = [r - mean_raw for r in raw]
    color_scores = [s * 1 for s in zero_sum_scores]

    return color_scores


def resolution_standard_scores(resolution_values):
    """
    resolution_values: df_budget['해상도'] 또는 점수화된 해상도 리스트
    해상도가 높을수록 좋은 점수를 주는 zero-sum 구조.

    """


    raw = [(r - resolution_reference) for r in resolution_values]
    mean_raw = sum(raw) / len(raw)
    zero_sum_scores = [r - mean_raw for r in raw]

    resolution_scores = [s * 1 for s in zero_sum_scores]  # scaling factor는 조정 가능
    return resolution_scores



#%% 예산 범위 내 노트북 필터 + price_score / budget_fit_score 계산

# 이미 위에서 prefs 를 받은 상태라고 가정
# prefs = get_user_preferences()

def calc_budget_based_scores(df, prefs):
    """
    예산 정보(prefs)를 바탕으로:
    1) 예산 범위 내 노트북 필터링 (±10% 확장 범위 사용)
    2) price_score 계산
    3) budget_fit_score 계산
    
    4) 결과를 출력하고, 점수 컬럼이 추가된 df_budget을 반환한다.
    """

    budget_min = prefs["budget_min"]
    budget_max = prefs["budget_max"]
    budget_prefer = prefs["budget_prefer"]
    multiple_map = {1: -3, 2: -2, 3: -1, 4: 1, 5: 2, 6: 3}

    print("\n=== 예산 범위 내 노트북 필터링 ===")
    print(f"예산 범위: {budget_min:.0f}만 ~ {budget_max:.0f}만, 선호 예산: {budget_prefer:.0f}만")

    # 1) 계산용 예산 범위 (±10%)
    budget_min_calc = budget_min * 0.9
    budget_max_calc = budget_max * 1.1

    # 2) 예산 범위(현재가격 기준) 안에 있는 노트북만 선택
    df_budget = df[
        (df["price_current"] >= budget_min_calc) &
        (df["price_current"] <= budget_max_calc)
    ].copy()
    

    # 1) price_score 계산 (적정가 vs 현재가격)
    df_budget["price_score"] = df_budget.apply(
        lambda row: round(price_score(row["price_reference"], row["price_current"]), 2),
        axis=1)
    
    # 2) budget_fit_score 계산 (zero-sum)
    price_list = df_budget["price_current"].tolist()
    budget_scores = budget_fit_scores(price_list, budget_prefer)
    df_budget["budget_fit_score"] = [round(s, 2) for s in budget_scores]
      
    # 3) screen_size_score 계산
    screen_sizes = df_budget["screen_size"].tolist()
    size_scores = screen_size_scores(screen_sizes, prefs["size"])
    df_budget["screen_size_score"] = size_scores
    
    # 4) Color_gamut_Score
    color_list = df_budget["color_gamut"].tolist()
    color_multiple = multiple_map[prefs["color"]]
    df_budget["color_gamut_score"] = [round(s * color_multiple, 2) 
                                for s in color_standard_scores(color_list)]
    
    # 5) Resolution_Score 
    resolution_list = df_budget["resolution"].tolist()
    resolution_multiple = multiple_map[prefs["resolution"]]
    df_budget["resolution_score"] = [round(s * resolution_multiple, 2) 
                                     for s in resolution_standard_scores(resolution_list)]
    
    # 6) Weight_Score
    weight_list = df_budget["weight_diff_pct"].tolist()
    weight_multiple = multiple_map[prefs["weight"]]
    df_budget["weight_score"] = [round(s * weight_multiple, 2) 
                                 for s in weight_standard_scores(weight_list)]
    
    # 7) Gaming_Score
    gaming_list = df_budget["gaming_level"].tolist()
    gaming_multiple = multiple_map[prefs["gaming"]]
    df_budget["gaming_score"] = [round(s * gaming_multiple, 2)
                                 for s in gaming_standard_scores(gaming_list)]

    
    # 7) battery score
    
    # 8) touch score
    if prefs["touch"]:
    	_temp = df_budget["touch"] * 5
    else:
    	_temp = df_budget["touch"] * 0
    
    mean_val = _temp.mean()
    df_budget["touch_score"] = (_temp - mean_val).round(2)
    
    if prefs["convertible"]:
    	_temp = df_budget["convertible"] * 5
    else:
        _temp = df_budget["convertible"] * 0

    mean_val = _temp.mean()
    df_budget["convertible_score"] = (_temp - mean_val).round(2)
    
    if prefs["oled"]:
    	_temp = df_budget["oled"] * 5
    else:
    	_temp = df_budget["oled"] * 0
    mean_val = _temp.mean()
    df_budget["oled_score"] = (_temp - mean_val).round(2)

    if prefs["ips"]:
    	_temp = df_budget["ips"] * 5
    else:
    	_temp = df_budget["ips"] * 0
    
    mean_val = _temp.mean()
    df_budget["ips_score"] = (_temp - mean_val).round(2)

    if prefs["sd_slot"]:
    	_temp = df_budget["sd_slot"] * 5
    else:
        _temp = df_budget["sd_slot"] * 0

    mean_val = _temp.mean()
    df_budget["sd_slot_score"] = (_temp - mean_val).round(2)
    
    if prefs["thunderbolt_usb4"]:
    	_temp = df_budget["thunderbolt_usb4"] * 5
    else:
    	_temp = df_budget["thunderbolt_usb4"] * 0
    mean_val = _temp.mean()
    df_budget["thunderbolt_usb4_score"] = (_temp - mean_val).round(2)
        
    if prefs["window"]:
        _temp = df_budget["window"] *5
    else:
        _temp = df_budget["window"] *0
    df_budget["window_score"] = (_temp - mean_val).round(2)
        
    
    df_budget["final_score"] = (
	60
	+ df_budget["price_score"]
	+ df_budget["budget_fit_score"]
	+ df_budget["screen_size_score"]
	+ df_budget["color_gamut_score"]
	+ df_budget["resolution_score"]
	+ df_budget["weight_score"]
    + df_budget["gaming_score"]
	+ df_budget["touch_score"]
	+ df_budget["convertible_score"]
	+ df_budget["oled_score"]
	+ df_budget["ips_score"]
	+ df_budget["sd_slot_score"]
	+ df_budget["thunderbolt_usb4_score"]
    ).round(2)
    
    priority_cols = [
    "brand",
    "name",
    "variant",
    "final_score",

    "price_score",
    "budget_fit_score",
    "screen_size_score",
    "color_gamut_score",
    "resolution_score",
    "weight_score",
    "gaming_score",

    "touch_score",
    "convertible_score",
    "oled_score",
    "ips_score",
    "sd_slot_score",
    "thunderbolt_usb4_score"
]




    other_cols = [c for c in df_budget.columns if c not in priority_cols]
		# final_score 기준 내림차순 정렬 후 상위 5개만 선택
	df_budget = (
		df_budget
		.sort_values(by="final_score", ascending=False)
		.head(5)
		.reset_index(drop=True)
	)

	return df_budget





