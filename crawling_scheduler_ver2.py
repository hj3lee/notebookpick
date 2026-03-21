import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from datetime import datetime
import os
import glob
import pandas as pd
import schedule
import random


def create_driver(version_main=146):
    options = uc.ChromeOptions()

    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")                
    options.add_argument("--no-sandbox")               
    options.add_argument("--disable-dev-shm-usage")     
    options.add_argument("--disable-extensions")       
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--start-maximized")
    
    global driver, wait

    driver = uc.Chrome(options=options, version_main=version_main)

    driver.set_page_load_timeout(45)
    driver.set_script_timeout(30)
    wait = WebDriverWait(driver, 15)
    

def restart_driver():
    global driver, wait
    print("드라이버 재시작")
    try:
        driver.quit()
    except:
        pass
    time.sleep(5)
    create_driver()


def check_soldout():
    restock_btn = driver.find_elements(
    By.CSS_SELECTOR,
    "button.prod-restock-notification-btn"
)

    if restock_btn:
        return True

def check_denied():
    if "Access Denied" in driver.title:
        return True

def find_price():

    
    jsonld_elements = driver.find_elements(
        By.CSS_SELECTOR,
        "script[type='application/ld+json']"
    )
    
    sale_price = None

    for el in jsonld_elements:
            try:
                data = json.loads(el.get_attribute("innerText"))
        
                # Product 타입만 대상
                if data.get("@type") != "Product":
                    continue
        
                offers = data.get("offers", {})
        
                # 현재 판매가
                sale_price = int(offers.get("price")) if offers.get("price") else None
        
                break
        
            except Exception:
                    continue
    
    best_price = sale_price
    time.sleep(5)
 
    try:
        driver.switch_to.default_content()

        # --------------------------------------------------
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".conditional-benefits")
            )
        )
        print("[STEP 0] conditional-benefits 확인")

        click_ok = False
        iframe = None

        selectors = [
            ".conditional-benefits .ccid-detail-tit a[role='button']",
            ".conditional-benefits .ccid-detail-tit a",
            ".conditional-benefits .ccid-detail-tit .ccid-detail-help-icon",
        ]

        for selector in selectors:
            try:
                benefit_btn = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, selector)
                    )
                )
                print(f"[STEP 1] 버튼 찾기 성공: {selector}")

                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center', inline:'center'});",
                    benefit_btn
                )
                time.sleep(0.3)

                driver.execute_script("arguments[0].click();", benefit_btn)
                print(f"[STEP 2] 버튼 클릭 성공: {selector}")

                iframe = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "iframe[src*='payment.coupang.com']")
                    )
                )
                print("[STEP 3] iframe 찾기 성공")

                click_ok = True
                break

            except Exception as e:
                print(f"[STEP FAIL] {selector} / {type(e).__name__} / {e}")

        if not click_ok or iframe is None:
            raise Exception("카드혜택 버튼 클릭 후 iframe 생성 실패")

        # --------------------------------------------------
        driver.switch_to.frame(iframe)
        print("[STEP 4] iframe 전환 성공")
        time.sleep(2)

        benefits = driver.execute_script("""
            return window.__PRELOADED_STATE__?.benefit?.instantDiscountBenefitList || [];
        """)
        print(f"[STEP 5] JS 실행 성공, 데이터 개수: {len(benefits)}")
        # --------------------------------------------------
        simple_cards = []

        for item in benefits:
            card_name = item.get("cardName")
            discount_rate = int(item["discountAmount"]) if item.get("discountAmount") else None
            max_discount = int(item["maxDiscountAmount"]) if item.get("maxDiscountAmount") else None

            simple_cards.append([card_name, discount_rate, max_discount])

        

        for card_name, discount_rate, max_discount in simple_cards:

            # 이론 할인액
            discount_amount = int(sale_price * discount_rate / 100)
            discount_amount = min(discount_amount, max_discount)
        
            final_price = sale_price - discount_amount
        
            # 최저가 갱신
            if final_price < best_price:
                best_price = final_price
                print('최종 가격: {best_price}')
                


    except Exception:
        print('카드할인 정보 미확인')
        pass
    
    
    return best_price/10000

#%%

def main():
    
    global driver, wait

    os.chdir(r"C:\notebookpick")
    os.system("git fetch") 
    status = os.popen("git status -uno").read()
    if "behind" in status: 
        os.system("git pull")

    data_dir = r"C:\notebookpick\data\basedata"
    files = glob.glob(os.path.join(data_dir, "basedata_*.csv"))
    latest_file = r"C:\notebookpick\data\manualdata\_manuldata_benefit_test.csv"
    df = pd.read_csv(latest_file, encoding="cp949")
    df = df[df["not_selling"] == 0]
    
    page_wait1 = 10
    page_wait2 = 60
    batch_reset=40

    driver=None
    wait=None

    create_driver()

    for idx, row in df[df["market"] == "쿠팡"].iterrows():
    
        link = row["link"]
        if pd.isna(link):
            continue
    
        print(f"[{idx}] 접속:", link)
    
        # 40개마다 드라이버 리셋
        if idx > 0 and idx % batch_reset == 0:
            restart_driver()
            time.sleep(60)
    
        driver.get(link)
        time.sleep(page_wait1)
    
        if check_denied():
            df.at[idx, "sold_out"] = 2
            print("denied")
            time.sleep(page_wait2 * 2)
            restart_driver()
            continue
    
        if check_soldout():
            df.at[idx, "sold_out"] = 1
            print("sold_out")
    
        price = find_price()
    
        now_min = datetime.now().strftime("%Y-%m-%d %H:%M")
        df.at[idx, "price_current"] = price
        df.at[idx, "last_update"] = now_min
    
        print("  저장:", price, "만")
        time.sleep(page_wait2)
    
    
    driver.quit()
            
    mask = df["sold_out"].isna() | (df["sold_out"] == "")

    df.loc[mask, "discount_rate"] = (
        (df.loc[mask, "price_current"] / df.loc[mask, "price_reference"] - 1)
        .mul(100)
        .round(1)
        )

    now_str = datetime.now().strftime("%y%m%d_%H%M")
    save_dir = r"C:\notebookpick\data\crawldata"
    filename = f"{save_dir}\\crawldata_{now_str}.csv"


    df.to_csv(
        filename,
        index=False,
        encoding="utf-8-sig"
    )

    print('csv 저장 완료')
    
    
    os.chdir(r"C:\notebookpick")
    
    os.system("git fetch") 
    status = os.popen("git status -uno").read()
    if "behind" in status: 
        os.system("git pull --rebase")


    os.system("git add data/crawldata")
    os.system('git commit -m "크롤링 데이터 업데이트"')
    os.system("git push")



main()
schedule.every().hour.do(lambda: print(datetime.now().strftime("%m-%d %H:%M"), "정상작동중"))

while True:
	schedule.run_pending()
	time.sleep(1)