from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

regions = [
    "서울", "경기도", "강원도", "인천", "대전", "세종", "충청북도", "충청남도",
    "대구", "경상북도", "경상남도", "부산", "광주", "전라북도", "전라남도", "울산", "제주"
]

all_results = []
visited_names = set()

def get_item_elements():
    return driver.find_elements(By.CSS_SELECTOR, "li.VLTHu.OW9LQ")

def scroll_until_end():
    last_count = -1
    while True:
        items = get_item_elements()
        if not items:
            break
        ActionChains(driver).move_to_element(items[-1]).perform()
        time.sleep(1)
        new_items = get_item_elements()
        if len(new_items) == last_count:
            break
        last_count = len(new_items)

for region in regions:
    print(f"\n====================== {region} 시작 ======================")
    url = f"https://map.naver.com/v5/search/{region} 풋살장"
    driver.get(url)
    time.sleep(3)

    try:
        iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#searchIframe")))
        driver.switch_to.frame(iframe)
    except:
        print(f"[ERROR] iframe 진입 실패: {region}")
        continue

    print("[INFO] searchIframe 진입 완료")

    page = 1
    while True:
        print(f"[INFO] 페이지 {page} 로딩 및 스크롤 중...")
        scroll_until_end()

        items = get_item_elements()
        print(f"[INFO] 항목 수: {len(items)}")

        for item in items:
            try:
                name = item.find_element(By.CSS_SELECTOR, "span.YwYLL").text
                if name in visited_names:
                    continue
                visited_names.add(name)

                address = item.find_element(By.CSS_SELECTOR, "span.Pb4bU").text

                try:
                    img = item.find_element(By.CSS_SELECTOR, "img.K0PDV")
                    img_url = img.get_attribute("src") or img.get_attribute("data-src")
                except:
                    img_url = ""

                print(f"📍 {name} | 📌 {address} | 🖼️ {img_url}")
                all_results.append([region, name, address, img_url])

            except Exception as e:
                print(f"[ERROR] 항목 처리 실패: {e}")
                continue

        # 다음 페이지 이동
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "a.flicking-arrow-next[aria-disabled='false']")
            driver.execute_script("arguments[0].click();", next_btn)
            page += 1
            time.sleep(2)

            driver.switch_to.default_content()
            iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#searchIframe")))
            driver.switch_to.frame(iframe)

        except:
            print("[INFO] 마지막 페이지 도달")
            break

driver.quit()

# 엑셀로 저장
df = pd.DataFrame(all_results, columns=["지역", "장소명", "주소", "이미지URL"])
df.to_excel("전국_풋살장_결과.xlsx", index=False)
print("[✅] 전국 풋살장 엑셀 저장 완료!")
