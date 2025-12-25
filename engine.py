# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 21:43:09 2025

@author: hj3le
"""

import pandas as pd
from datetime import datetime

#%% 1. 엑셀 불러오기
df = pd.read_excel("notebookdb2.xlsx")

weight_reference = {
	13.0:115.56,13.1:117.44,13.2:119.33,13.3:121.78,13.4:123.11,13.5:125.00,
	13.6:126.89,13.7:128.78,13.8:130.67,13.9:132.56,14.0:135.00,14.1:136.89,
	14.2:138.78,14.3:140.67,14.4:142.56,14.5:144.44,14.6:146.33,14.7:148.22,
	14.8:150.11,14.9:152.00,15.0:153.89,15.1:155.78,15.2:157.67,15.3:159.56,
	15.4:161.44,15.5:163.33,15.6:165.22,15.7:167.11,15.8:169.00,15.9:170.89,
	16.0:172.78,16.1:174.67,16.2:176.56,16.3:178.44,16.4:180.33,16.5:182.22,
	16.6:184.11,16.7:186.00,16.8:187.89,16.9:189.78,17.0:191.67,17.1:193.56,
	17.2:195.44,17.3:197.33,17.4:199.22,17.5:201.11,17.6:203.00,17.7:204.89,
	17.8:206.78,17.9:208.67,18.0:210.56,18.1:212.44,18.2:214.33,18.3:216.22,
	18.4:218.11,18.5:220.00,18.6:221.89,18.7:223.78,18.8:225.67,18.9:227.56,
	19.0:229.44
}

color_reference = 6.75
gaming_reference = 5
resolution_reference = 6.6


#%% 점수 계산 함수들

def price_score(price_reference, price_current):
	discount_ratio = (price_reference - price_current) / price_reference
	discount_percent = discount_ratio * 100 * 1.2

	score = discount_percent

	if score > 24:
		score = 24
	elif score < -24:
		score = -24

	return round(score, 2)


def budget_fit_scores(prices_current, budget_prefer):
	raw = [-abs(p - budget_prefer) for p in prices_current]
	mean_raw = sum(raw) / len(raw)
	zero_sum_scores = [r - mean_raw for r in raw]
	return [s * 0.25 for s in zero_sum_scores]


def weight_standard_scores(weight_diff_pct):
	raw = [-(w) for w in weight_diff_pct]
	mean_raw = sum(raw) / len(raw)
	zero_sum_scores = [r - mean_raw for r in raw]
	return [s * 0.25 for s in zero_sum_scores]


def screen_size_scores(screen_sizes, size_pref):
	scores = []

	for s in screen_sizes:
		if size_pref == 3:
			score = 0
		elif size_pref == 2:
			score = 5 if s <= 14 else -5 if s >= 15.6 else -2
		elif size_pref == 4:
			score = 5 if s >= 16 else -5 if s <= 14 else 2
		elif size_pref == 1:
			score = 10 if s <= 14 else -10 if s >= 15.6 else -3
		elif size_pref == 5:
			score = 10 if s >= 16 else -10 if s <= 14 else -3

		scores.append(score)

	return scores


def gaming_standard_scores(gaming):
	raw = [(g - gaming_reference) for g in gaming]
	mean_raw = sum(raw) / len(raw)
	zero_sum_scores = [r - mean_raw for r in raw]
	return zero_sum_scores


def color_standard_scores(color_values):
	raw = [(c - color_reference) for c in color_values]
	mean_raw = sum(raw) / len(raw)
	zero_sum_scores = [r - mean_raw for r in raw]
	return zero_sum_scores


def resolution_standard_scores(resolution_values):
	raw = [(r - resolution_reference) for r in resolution_values]
	mean_raw = sum(raw) / len(raw)
	zero_sum_scores = [r - mean_raw for r in raw]
	return zero_sum_scores


#%% 메인 스코어 계산 함수

def calc_budget_based_scores(df, prefs):
	budget_min = prefs["budget_min"]
	budget_max = prefs["budget_max"]
	budget_prefer = prefs["budget_prefer"]

	multiple_map = {1:-3, 2:-2, 3:-1, 4:1, 5:2, 6:3}

	budget_min_calc = budget_min * 0.9
	budget_max_calc = budget_max * 1.1

	df_budget = df[
		(df["price_current"] >= budget_min_calc) &
		(df["price_current"] <= budget_max_calc)
	].copy()

	df_budget["price_score"] = df_budget.apply(
		lambda r: price_score(r["price_reference"], r["price_current"]),
		axis=1
	)

	df_budget["budget_fit_score"] = [
		round(s, 2) for s in budget_fit_scores(
			df_budget["price_current"].tolist(),
			budget_prefer
		)
	]

	df_budget["screen_size_score"] = screen_size_scores(
		df_budget["screen_size"].tolist(),
		prefs["size"]
	)

	df_budget["color_gamut_score"] = [
		round(s * multiple_map[prefs["color"]], 2)
		for s in color_standard_scores(df_budget["color_gamut"].tolist())
	]

	df_budget["resolution_score"] = [
		round(s * multiple_map[prefs["resolution"]], 2)
		for s in resolution_standard_scores(df_budget["resolution"].tolist())
	]

	df_budget["weight_score"] = [
		round(s * multiple_map[prefs["weight"]], 2)
		for s in weight_standard_scores(df_budget["weight_diff_pct"].tolist())
	]

	df_budget["gaming_score"] = [
		round(s * multiple_map[prefs["gaming"]], 2)
		for s in gaming_standard_scores(df_budget["gaming_level"].tolist())
	]

	for key in ["touch","convertible","oled","ips","sd_slot","thunderbolt_usb4"]:
		if prefs[key]:
			tmp = df_budget[key] * 5
		else:
			tmp = df_budget[key] * 0

		df_budget[f"{key}_score"] = (tmp - tmp.mean()).round(2)

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

	df_budget = (
		df_budget
		.sort_values(by="final_score", ascending=False)
		.head(5)
		.reset_index(drop=True)
	)

	return df_budget





