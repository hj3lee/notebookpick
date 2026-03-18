# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 06:46:31 2026

@author: hj3le
"""
import os

os.chdir(r"C:\notebookpick")

# 전체 변경 반영
os.system("git add .")

# 커밋 (변경 없으면 무시)
os.system('git commit -m "update"')

# 최신 반영 (rebase)
os.system("git pull --rebase")

# 푸시
os.system("git push")