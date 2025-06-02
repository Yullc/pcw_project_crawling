from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

def search_and_crawl(region, keyword):
    driver.get("https://map.naver.com")
    time.sleep(3)

    try:
        search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.input_search")))
        search_box.clear()
        search_box.send_keys(f"{region} {keyword}")
        search_box.send_keys(Keys.ENTER)
        time.sleep(3)

        # iframe 진입
        iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#searchIframe")))
        driver.switch_to.frame(iframe)
        print(f"[INFO] {region} {keyword} 검색 iframe 진입 완료")

        results = []
        visited_names = set()

        def get_items():
            return driver.find_elements(By.CSS_SELECTOR, "li.Ki6eC.YPAJV")

        def scroll_until_end():
            last_count = -1
            while True:
                items = get_items()
                if not items:
                    break
                driver.execute_script("arguments[0].scrollIntoView(true);", items[-1])
                time.sleep(1)
                new_items = get_items()
                if len(new_items) == last_count:
                    break
                last_count = len(new_items)

        page = 1
        while True:
            print(f"[INFO] 페이지 {page} 스크롤 중...")
            scroll_until_end()

            items = get_items()
            print(f"[INFO] 항목 수: {len(items)}")

            for item in items:
                try:
                    name = item.find_element(By.CSS_SELECTOR, "span.t3s7S").text
                    if name in visited_names:
                        continue
                    visited_names.add(name)

                    elements = item.find_elements(By.CSS_SELECTOR, "span.ScFlJ")
                    address = ""

                    for el in elements:
                        text = el.text.strip()
                        if "구" in text or "동" in text or "로" in text:  # 주소 패턴
                            address = text
                            break

                    try:
                        img = item.find_element(By.CSS_SELECTOR, "img.K0PDV")
                        img_url = img.get_attribute("src") or img.get_attribute("data-src")
                    except:
                        img_url = ""

                    print(f"📍 {name} | 📌 {address} | 🖼️ {img_url}")
                    results.append([region, name, address, img_url])

                except Exception as e:
                    print(f"[ERROR] 항목 처리 실패: {e}")
                    continue

            # 다음 페이지
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

        driver.switch_to.default_content()
        return results

    except Exception as e:
        print(f"[ERROR] {region} {keyword} 실패: {e}")
        return []

regions = [
    "서울", "경기도", "강원도", "인천", "대전", "세종", "충청북도", "충청남도",
    "대구", "경상북도", "경상남도", "부산", "광주", "전라북도", "전라남도", "울산", "제주"
]

all_data = []
for region in regions:
    all_data += search_and_crawl(region, "축구장")  # ✅ "축구장"만 검색

df = pd.DataFrame(all_data, columns=["지역", "장소명", "주소", "이미지URL"])
df.to_excel("전국_축구장_결과.xlsx", index=False)
print("[✅] 전국 축구장 엑셀 저장 완료!")
driver.quit()
