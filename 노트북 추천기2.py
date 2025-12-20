# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 21:43:09 2025

@author: hj3le
"""

import pandas as pd
from datetime import datetime



#%% 1. 엑셀 불러오기
# 같은 폴더에 notebookdb.xlsx 가 있을 때
df = pd.read_excel("notebookdb.xlsx")

#%% 무게 적정값 계산(필요하다면 df_budget 내의 수식으로 전환가능)

# 화면 크기 그룹 정의
group_14 = df[df['화면크기'] == 14]
group_16 = df[df['화면크기'].isin([15.6, 16])]

# 무게 컬럼명 (본인의 df에 맞게 변경)
weight_col = '무게'   # 또는 '절대무게'

# 14인치
mean_14 = group_14[weight_col].mean()
median_14 = group_14[weight_col].median()
std_14 = group_14[weight_col].std()

# 15.6/16인치
mean_16 = group_16[weight_col].mean()
median_16 = group_16[weight_col].median()
std_16 = group_16[weight_col].std()


x1 = 14.0
y1 = median_14

x2 = 15.8          # 16 대신 15.8을 기준점으로 사용
y2 = median_16

# 기울기(m)와 절편(b) 계산
m = (y2 - y1) / (x2 - x1)
b = y1 - m * x1

weight_reference = {}

for i in range(int(13.0*10), int(19.0*10) + 1):
    size = i / 10.0
    w = m * size + b   # 1차함수 W(x)
    weight_reference[round(size, 1)] = round(w, 2)
    
#print("14.0인치 기준무게 →", weight_reference[14.0])
#print("15.1인치 기준무게 →", weight_reference[15.1])
#print("16.0인치 기준무게 →", weight_reference[16.0])
#print("13.3인치 기준무게 →", weight_reference[13.3])
#print("17.0인치 기준무게 →", weight_reference[17.0])

#%% 할인율 계산 함수
def calc_discount_ratio(row):
    """
    row: pandas DataFrame의 한 행(Series)
    
    반환:
        할인율(float): 예 -0.12  → -12%
        할인율표기(str): 예 "-12.0%"
    """
    if row['적정가'] == 0:
        return 0, "0.0%"
    
    ratio = (row['현재가격'] - row['적정가']) / row['적정가']
    return ratio


def calc_weight_diff_percent(row):
    size = row['화면크기']
    weight = row['무게']      # 예: 159, 135 같은 값
    
    # 기준무게 가져오기
    base = weight_reference.get(size)
    
    # 기준없거나 NaN 이면 결측 처리
    if base is None or pd.isna(weight):
        return None

    diff_ratio = (weight - base) / base  # 비율
    diff_percent = diff_ratio * 100      # %
    return diff_percent

df['무게_편차_%'] = df.apply(calc_weight_diff_percent, axis=1)

# 소수 한 자리로 반올림
df['무게_편차_%'] = df['무게_편차_%'].round(1)

#%% 전체 60개 노트북에 대해 필요한 컬럼 추가

ratio_list = []


for idx, row in df.iterrows():
    ratio = calc_discount_ratio(row)
    ratio_list.append(ratio)


# 결과 컬럼 추가
df['할인율'] = ratio_list

top10 = df.sort_values(by='할인율').head(10)




#%% 인풋 함수

def get_numeric_input(prompt_text):
    """숫자 입력을 강제하는 보조 함수"""
    while True:
        try:
            value = float(input(prompt_text))
            return value
        except ValueError:
            print("숫자로 입력하세요.")


def get_scale_input(prompt_text):
    """1~6점 척도 입력용 보조 함수"""
    while True:
        try:
            value = int(input(prompt_text))
            if 1 <= value <= 6:
                return value
            else:
                print("1~6 사이로 입력하세요.")
        except ValueError:
            print("숫자로 입력하세요.")
            
def get_screen_size_input(prompt_text):

    print("\n화면 크기 선호 선택 (1~5)")
    print("1: 작은 화면 강력 선호")
    print("2: 작은 화면 선호")
    print("3: 중립")
    print("4: 큰 화면 선호")
    print("5: 큰 화면 강력 선호")
    
    while True:
        try:
            value = int(input(prompt_text))
            if 1 <= value <= 5:
                return value
            else:
                print("1~5 사이로 입력하세요.")
        except ValueError:
            print("숫자로 입력하세요.")


def get_user_preferences():
    """
    사용자 인풋 전체를 받아 dict로 반환한다.
    - 예산 시작점
    - 예산 최고점
    - 선호 예산
    - 1~6점 척도: 화면 크기, 색역, 해상도/주사율, 무게, 배터리
    """

    print("=== 예산 입력 ===")
    budget_min = get_numeric_input("예산 시작점 (만원 단위 입력) : ")
    budget_max = get_numeric_input("예산 최고점 (만원 단위 입력) : ")
    budget_prefer = get_numeric_input("선호 예산점 (만원 단위 입력) : ")

    print("\n=== 1~6 점수 척도 입력 ===")
    size_score = get_screen_size_input("화면 크기 선호 (1~5) 입력: ")
    color_score = get_scale_input("색감 선호 (1~6) : ")
    resolution_score = get_scale_input("해상도/주사율 선호 (1~6) : ")
    weight_score = get_scale_input("무게 선호 (1~6) : ")
    battery_score = get_scale_input("배터리 선호 (1~6) : ")

    return {
        "budget_min": budget_min,
        "budget_max": budget_max,
        "budget_prefer": budget_prefer,
        "size": size_score,
        "color": color_score,
        "resolution": resolution_score,
        "weight": weight_score,
        "battery": battery_score
    }


#%% 점수계산 함수들

def price_score(optimal_price, current_price):
    
    "적정가 대비 현재가격의 할인율을 기반으로 -20점 ~ +20점 점수를 산출한다."

    # 할인율 계산 (양수 = 할인, 음수 = 비싸다)
    discount_ratio = (optimal_price - current_price) / optimal_price
    discount_percent = discount_ratio * 100 * 1.2  # % 변환

    # 점수 매핑 (예: -9% → +10.8점)
    score = discount_percent

    # 점수 범위 제한
    if score > 24:
        score = 24
    elif score < -24:
        score = -24

    return round(score, 2)


def budget_fit_scores(prices, budget_prefer):
    """
    예산 내 노트북들의 가격 리스트로부터 zero-sum 예산 적합성 점수 생성.
    보정 후 최종 점수를 1/2로 줄인다.
    """

    # 1) raw score
    raw = [-abs(p - budget_prefer) for p in prices]

    # 2) 평균
    mean_raw = sum(raw) / len(raw)

    # 3) zero-sum 변환
    zero_sum_scores = [r - mean_raw for r in raw]

    # 4) 스케일 조정 (1/2 배)
    budget_fit_score = [s * 0.25 for s in zero_sum_scores]

    return budget_fit_score


def weight_standard_scores(weight_diffs):
    """
    df['무게_편차_%'] 리스트로부터 zero-sum 무게 적합성 점수 생성.
    - 기준보다 가벼울수록(무게_편차_%가 음수일수록) 높은 점수가 되도록 설계.
    - budget_fit_scores와 같은 형식 유지.
    """

    raw = [-(w) for w in weight_diffs]
    mean_raw = sum(raw) / len(raw)
    zero_sum_scores = [r - mean_raw for r in raw]
    weight_standard_scores = [s * 0.25 for s in zero_sum_scores]

    return weight_standard_scores

def size_standard_scores(screen_sizes, size_pref):
    """
    화면크기 리스트와 사용자 선호(size_pref: 1~5)를 받아
    각 노트북의 화면크기 점수 리스트를 반환한다.
    (규칙은 네가 말한 그대로 적용)
    """
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
            # 15.1, 15.3 보정은 여기 나중에 추가

        # 4: 16인치 선호
        elif size_pref == 4:
            if s >= 16:
                score = +5
            elif s <= 14:
                score = -5
            # 15.1, 15.3 보정은 여기 나중에 추가

        # 1: 14인치 강력 선호
        elif size_pref == 1:
            if s <= 14:
                score = +10
            elif s >= 15.6:
                score = -10
            # 15.1, 15.3은 -2 적용할 거면 여기에서 처리

        # 5: 16인치 강력 선호
        elif size_pref == 5:
            if s >= 16:
                score = +10
            elif s <= 14:
                score = -10
            # 15.1, 15.3은 -2 적용할 거면 여기에서 처리

        scores.append(score)

    return scores

def color_standard_scores(color_values):
    """
    color_values: df_budget['패널'] 같은 리스트
    color_base  : 대표값(6.75)
    
    색역이 높을수록 좋은 점수를 주는 zero-sum 방식.
    weight_standard_scores와 동일한 구조 유지.
    """
    color_base=6.75
    raw = [(c - color_base) for c in color_values]
    mean_raw = sum(raw) / len(raw)
    zero_sum_scores = [r - mean_raw for r in raw]
    color_scores = [s * 1 for s in zero_sum_scores]

    return color_scores


def resolution_standard_scores(resolution_values):
    """
    resolution_values: df_budget['해상도'] 또는 점수화된 해상도 리스트
    resolution_base  : 대표 해상도값 (예: 평균값)
    해상도가 높을수록 좋은 점수를 주는 zero-sum 구조.
    color_standard_scores와 동일한 형태.
    """

    resolution_base = 6.6  # 필요 시 고정값으로도 설정 가능
    raw = [(r - resolution_base) for r in resolution_values]
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
        (df["현재가격"] >= budget_min_calc) &
        (df["현재가격"] <= budget_max_calc)
    ].copy()
    
    

    # 1) price_score 계산 (적정가 vs 현재가격)
    df_budget["price_score"] = df_budget.apply(
        lambda row: round(price_score(row["적정가"], row["현재가격"]), 2),
        axis=1)
    
    # 2) budget_fit_score 계산 (zero-sum)
    price_list = df_budget["현재가격"].tolist()
    budget_scores = budget_fit_scores(price_list, budget_prefer)
    df_budget["budget_fit_score"] = [round(s, 2) for s in budget_scores]
      
    # 3) size_score 계산
    screen_sizes = df_budget["화면크기"].tolist()
    size_scores = size_standard_scores(screen_sizes, prefs["size"])
    df_budget["size_score"] = size_scores
    
    # 4) Color_Score
    color_list = df_budget["패널"].tolist()
    color_multiple = multiple_map[prefs["color"]]
    df_budget["color_score"] = [round(s * color_multiple, 2) 
                                for s in color_standard_scores(color_list)]
    
    # 5) Resolution_Score 
    resolution_list = df_budget["해상도"].tolist()
    resolution_multiple = multiple_map[prefs["resolution"]]
    df_budget["resolution_score"] = [round(s * resolution_multiple, 2) 
                                     for s in resolution_standard_scores(resolution_list)]
    
    # 6) Weight_Score
    weight_list = df_budget["무게_편차_%"].tolist()
    weight_multiple = multiple_map[prefs["weight"]]
    df_budget["weight_score"] = [round(s * weight_multiple, 2) 
                                 for s in weight_standard_scores(weight_list)]




    # final_score = 소수 둘째 자리까지
    df_budget["final_score"] = (
        60
        + df_budget["price_score"]
        + df_budget["budget_fit_score"]
        + df_budget["weight_score"]
        + df_budget["size_score"]
        + df_budget["color_score"]
        + df_budget["resolution_score"]
        
    ).round(2)
    
    
    
    # 1) 최우선 배치할 컬럼 정의
    priority_cols = [
    "메인이름", 
    "서브이름", 
    "final_score",
    "price_score",
    "budget_fit_score",
    "size_score",
    "color_score",
    "resolution_score",
    "weight_score"
]
    
    # 2) 나머지 컬럼 자동 추출
    other_cols = [c for c in df_budget.columns if c not in priority_cols]
    
    # 3) 컬럼 순서 재배치
    df_budget = df_budget[priority_cols + other_cols]
    
    # 4) final_score 계산
    df_budget["final_score"] = (
        60
        + df_budget["price_score"]
        + df_budget["budget_fit_score"]
        + df_budget["weight_score"]
        + df_budget["size_score"]
        + df_budget["color_score"]
        + df_budget["resolution_score"]
    )
    
    # 5) 정렬 수행
    df_budget = df_budget.sort_values(
        by=["메인이름", "서브이름", "final_score"],
        ascending=[True, True, False]   # final_score는 내림차순
    )
    
    df_budget = df_budget.sort_values(
    by=["final_score"],
    ascending=False
)

    # === 엑셀 저장 ===
    timestamp = datetime.now().strftime("%m%d_%H%M")
    filename = f"notebook_result_{timestamp}.xlsx"
    df_budget.to_excel(filename, index=False)
    
    print(f"\n엑셀 저장 완료 → {filename}")
    
    return df_budget


#%% 실행

prefs = get_user_preferences()
calc_budget_based_scores(df, prefs)


#%% 실험

