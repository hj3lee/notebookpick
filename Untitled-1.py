import os

os.chdir(r"C:\notebookpick")

os.system("git add data/crawldata")
os.system('git commit -m "크롤링 데이터 업데이트"')
os.system("git push")
