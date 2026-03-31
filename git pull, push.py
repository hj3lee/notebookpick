# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 06:46:31 2026

@author: hj3le
"""
import os

os.chdir(r"C:\notebookpick")

os.system("git add .")

os.system('git commit -m "update"')

os.system("git pull --rebase")

os.system("git push")