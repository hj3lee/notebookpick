#!/usr/bin/env python3
"""auto_bot.py - 노트북픽 쿠팡 자동 가격 수집 봇 (고급 파싱 적용)
워드프레스 REST API 와 연동하여 크롤링 대상을 받고, 결과를 자동 반영합니다.
"""
import argparse
import json
import os
import sys
import time
import random
import logging
from datetime import datetime

try:
    import requests
except ImportError:
    print("requests 라이브러리가 없습니다. pip install requests 를 실행하세요.")
    sys.exit(1)
try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("undetected_chromedriver 라이브러리가 없습니다. pip install undetected-chromedriver selenium 을 실행하세요.")
    sys.exit(1)

# ── 설정 (환경변수 또는 아래 직접 수정) ──
WP_URL  = os.getenv("NBP_WP_URL", "https://hj3lee.mycafe24.com")  # 워드프레스 사이트 주소
API_KEY = os.getenv("NBP_API_KEY", "NBP_SECRET_BOT_9999")  # REST API 인증 키
SCHEDULE_TIME = os.getenv("NBP_SCHEDULE", "01:30")
PAGE_WAIT_MIN = 250   # 최소 대기
PAGE_WAIT_MAX = 350   # 최대 대기

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("auto_bot")

def get_targets(mode="all", split=None):
    """워드프레스에서 크롤링 대상 목록 수신"""
    url = f"{WP_URL.rstrip(chr(47))}/wp-json/nbp/v1/targets"
    params = {}
    if mode in ("office", "gaming"): params["type"] = mode
    if split in ("even", "odd"): params["split"] = split
    
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    targets = r.json()
    log.info(f"크롤링 대상 {len(targets)}개 수신 (mode={mode}, split={split})")
    return targets

def send_results(results):
    """크롤링 결과를 워드프레스에 전송"""
    url = f"{WP_URL.rstrip(chr(47))}/wp-json/nbp/v1/update-prices"
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    
    payload = []
    for r in results:
        item = {"post_id": r["post_id"], "is_soldout": r["is_soldout"]}
        if r.get("price") and not r["is_soldout"]: 
            item["price_current"] = r["price"]
        payload.append(item)
        
    if not payload:
        log.info("전송할 결과 없음")
        return
        
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    log.info(f"전송 완료: updated={data.get('updated',0)}, skipped={data.get('skipped',0)}")

# ==========================================
# 기존 고급 크롤링 로직 이식 부분
# ==========================================
def create_driver(version_main=146):
    """undetected_chromedriver 생성"""
    options = uc.ChromeOptions()
    # 경로가 다를 경우를 대비해 예외 처리 (기본 경로 삭제 시 알아서 찾음)
    # options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")                
    options.add_argument("--no-sandbox")               
    options.add_argument("--disable-dev-shm-usage")     
    options.add_argument("--disable-extensions")       
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--start-maximized")
    
    driver = uc.Chrome(options=options, version_main=version_main)
    driver.set_page_load_timeout(45)
    driver.set_script_timeout(30)
    return driver

def check_soldout(driver):
    restock_btn = driver.find_elements(By.CSS_SELECTOR, "button.prod-restock-notification-btn")
    out_of_stock = driver.find_elements(By.CSS_SELECTOR, ".oos-label, .soldout-text, .prod-not-find-wrap")
    if restock_btn or out_of_stock:
        return True
    return False

def check_denied(driver):
    if "Access Denied" in driver.title:
        return True
    return False

def find_price(driver):
    """JSON-LD 및 카드할인 iframe 파싱 로직"""
    jsonld_elements = driver.find_elements(By.CSS_SELECTOR, "script[type='application/ld+json']")
    sale_price = None

    for el in jsonld_elements:
        try:
            data = json.loads(el.get_attribute("innerText"))
            if data.get("@type") != "Product":
                continue
            offers = data.get("offers", {})
            sale_price = int(offers.get("price")) if offers.get("price") else None
            break
        except Exception:
            continue
    
    # JSON-LD 실패 시 일반 텍스트에서 추출 시도 (Fallback)
    if sale_price is None:
        for sel in [".total-price strong", ".prod-sale-price .total-price", "span.total-price", ".prod-price-set .total-price"]:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                import re
                nums = re.sub(r"[^\d]", "", el.text.strip())
                if nums and int(nums) > 0: 
                    sale_price = int(nums)
                    break
            except: continue
            
    if sale_price is None:
        return None

    best_price = sale_price
    time.sleep(5)
    benefits = []

    try:
        # 카드 즉시할인 확인 로직
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".conditional-benefits")))
        benefit_btn = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".conditional-benefits a[role='button']")))

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", benefit_btn)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", benefit_btn)
        
        # iframe 전환 대기
        time.sleep(120) 

        iframe = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='payment.coupang.com']")))
        driver.switch_to.frame(iframe)
        time.sleep(2)

        benefits = driver.execute_script("""
            return window.__PRELOADED_STATE__?.benefit?.instantDiscountBenefitList || [];
        """)

        for item in benefits:
            discount_rate = int(item["discountAmount"]) if item.get("discountAmount") else 0
            max_discount = int(item["maxDiscountAmount"]) if item.get("maxDiscountAmount") else 1000000
            discount_amount = int(sale_price * discount_rate / 100)
            discount_amount = min(discount_amount, max_discount)
            final_price = sale_price - discount_amount

            if final_price < best_price:
                best_price = final_price

    except Exception:
        pass # 혜택 창이 없거나 열리지 않으면 기본 sale_price 반환

    return best_price


def run_crawl(mode="all", split=None):
    """메인 크롤링 실행부"""
    targets = get_targets(mode, split)
    if not targets:
        log.info("크롤링 대상이 없습니다.")
        return
        
    driver = create_driver()
    results = []
    batch_reset = 150
    
    try:
        for i, target in enumerate(targets):
            log.info(f"[{i+1}/{len(targets)}] {target['title']} ...")
            
            # 150개마다 드라이버 리셋 방지 로직
            if i > 0 and i % batch_reset == 0:
                log.info("드라이버 메모리 확보를 위해 재시작합니다...")
                try: driver.quit()
                except: pass
                time.sleep(10)
                driver = create_driver()
                
            try:
                driver.get(target["source_link"])
                time.sleep(random.uniform(5, 8)) # 기본 대기
                
                if check_denied(driver):
                    log.warning("Access Denied 발생. 30초 대기 후 드라이버 재시작")
                    time.sleep(30)
                    try: driver.quit()
                    except: pass
                    driver = create_driver()
                    continue
                
                if check_soldout(driver):
                    log.info("  -> 품절 (sold_out)")
                    results.append({"post_id": target["post_id"], "is_soldout": True, "price": None})
                    continue
                    
                final_price = find_price(driver)
                
                if final_price:
                    log.info(f"  -> 가격: {final_price:,}원")
                    results.append({"post_id": target["post_id"], "is_soldout": False, "price": final_price})
                else:
                    log.warning("  -> 가격 추출 실패")
                    
            except Exception as e:
                log.error(f"  -> 오류 발생: {e}")
                
            # 페이지 간 대기시간
            if i < len(targets) - 1:
                wait_time = random.uniform(PAGE_WAIT_MIN, PAGE_WAIT_MAX)
                log.info(f"  대기 {wait_time:.0f}초...")
                time.sleep(wait_time)
                
        # 워드프레스로 최종 전송
        if results:
            send_results(results)
            
    finally:
        try: driver.quit()
        except: pass
    log.info(f"크롤링 완료: 총 {len(results)}개 처리")

def main():
    parser = argparse.ArgumentParser(description="노트북픽 쿠팡 자동 가격 수집 봇")
    parser.add_argument("--mode", choices=["office", "gaming", "all"], default="office", help="크롤링 유형")
    parser.add_argument("--split", choices=["even", "odd"], default=None, help="ID 짝/홀수 분할")
    parser.add_argument("--schedule", action="store_true", help="매일 지정 시각 자동 반복")
    args = parser.parse_args()
    
    if args.schedule:
        log.info(f"스케줄 모드: 매일 {SCHEDULE_TIME}에 실행")
        import schedule
        schedule.every().day.at(SCHEDULE_TIME).do(run_crawl, mode=args.mode, split=args.split)
        while True:
            schedule.run_pending()
            time.sleep(30)
    else:
        run_crawl(args.mode, args.split)

if __name__ == "__main__":
    main()