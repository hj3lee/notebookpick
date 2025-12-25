# -*- coding: utf-8 -*-
"""
Created on Sun Dec 21 08:06:05 2025

@author: hj3le
"""

from fastapi import FastAPI
from engine import calc_budget_based_scores, df
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 테스트 단계
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/recommend")
def recommend(prefs: dict):
    result_df = calc_budget_based_scores(df, prefs)
    result_df = result_df.fillna(0)
    return {
        "count": len(result_df),
        "results": result_df.to_dict(orient="records")

    }


