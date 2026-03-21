import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json



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
 
    try:
        # --------------------------------------------------
        benefit_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".conditional-benefits .ccid-detail-tit a")
            )
        )
    
        # --------------------------------------------------
        benefit_btn.click()
    
        # --------------------------------------------------
        iframe = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "iframe[src*='payment.coupang.com']")
            )
        )
    
        # --------------------------------------------------
        print("iframe으로 전환")
        driver.switch_to.frame(iframe)
        time.sleep(2)
        

        benefits = driver.execute_script("""
            return window.__PRELOADED_STATE__.benefit.instantDiscountBenefitList;
        """)

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
                


    except Exception:
        pass
    
    
    return best_price/10000

#%%


print("테스트 시작:")

create_driver()



driver.get('https://www.coupang.com/vp/products/8563924172?itemId=24803637451&vendorItemId=91811310020')
time.sleep(3)

# 차단 체크
if check_denied():
    print("Access Denied")

# 품절 체크
if check_soldout():
    print("sold_out")

# 가격 추출
price = find_price()

if price:
    print(f"가격: {price} 만원")
else:
    print("가격 추출 실패")
driver.quit()