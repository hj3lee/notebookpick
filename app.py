# -*- coding: utf-8 -*-
"""
Created on Sun Dec 21 08:06:05 2025

@author: hj3le
"""

from fastapi import FastAPI
from engine import calc_budget_based_scores, df

app = FastAPI()

@app.post("/recommend")
def recommend(prefs: dict):
    result_df = calc_budget_based_scores(df, prefs)
    return {
        "count": len(result_df),
        "results": result_df.to_dict(orient="records")
    }