# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 09:13:35 2026

@author: hj3le
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from notebook_recommender_api import recommend

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 테스트용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    samsung: int
    lg: int
    lenovo: int
    hp: int
    asus: int
    acer: int
    budget_min: int
    budget_max: int
    budget_prefer: int
    size: int
    weight: int
    battery: int
    graphic: int
    display: int
    window: int
    ips: int
    oled: int

@app.get("/ping")
def ping():
    return {"message": "ok"}

@app.post("/recommend")
def recommend_api(user_input: UserInput):
    result_df = recommend(user_input.dict())
    return {
        "items": result_df[
            ["link", "brand", "name", "price_current", "overall_score", "personal_score", "price_score"]
        ].to_dict(orient="records")
    }