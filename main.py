import os
import json
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Читаємо акаунти з секретів (GitHub Secrets)
ACCOUNTS_JSON = os.getenv("ACCOUNTS_JSON")
if not ACCOUNTS_JSON:
    print("❌ Помилка: змінна оточення ACCOUNTS_JSON не задана!")
    exit(1)

accounts = json.loads(ACCOUNTS_JSON)

SEARCH_TERMS = [...]  # Ваш список пошукових термінів

def init_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    return driver

def login(driver, username, password):
    try:
        driver.get("https://login.live.com/")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "loginfmt")))
        
        email_input = driver.find_element(By.NAME, "loginfmt")
        email_input.clear()
        email_input.send_keys(username)
        email_input.send_keys(Keys.RETURN)
        
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "passwd")))
        password_input = driver.find_element(By.NAME, "passwd")
        password_input.clear()
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "meControl")))
        return True
    except (NoSuchElementException, TimeoutException) as e:
        print(f"❌ Помилка логіну для {username}: {str(e)}")
        return False

def perform_searches(driver, username):
    print(f"🚀 Починаю фармінг Microsoft Rewards для {username}...")
    num_searches = random.randint(7, 12)
    searches = random.sample(SEARCH_TERMS, num_searches)

    for term in searches:
        try:
            driver.get(f"https://www.bing.com/search?q={term.replace(' ', '+')}")
            time.sleep(random.uniform(2, 5))
        except WebDriverException as e:
            print(f"⚠ Помилка пошуку для {username}: {str(e)}")
            continue

    points = get_points(driver)
    print(f"✅ Пошук завершено, балів: {points}")

def get_points(driver):
    try:
        driver.get("https://rewards.microsoft.com/")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.RewardsPointsCount, span.msportalfx-ux-fluent-text-5, span#id_rc")))
        
        selectors = [
            "div.RewardsPointsCount",
            "span.msportalfx-ux-fluent-text-5",
            "span#id_rc",
        ]
        for sel in selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, sel)
                points_text = elem.text.strip()
                if points_text:
                    return points_text
            except NoSuchElementException:
                continue
        return "Н/Д"
    except Exception as e:
        print(f"⚠ Помилка отримання балів: {str(e)}")
        return "Н/Д"

def main():
    driver = init_driver()
    try:
        for acc in accounts:
            username = acc.get("username")
            password = acc.get("password")

            if not username or not password:
                print("❌ Пропущено акаунт через відсутність username або password.")
                continue

            success = login(driver, username, password)
            if not success:
                continue

            try:
                perform_searches(driver, username)
            except WebDriverException as e:
                print(f"❌ Помилка WebDriver для {username}: {str(e)}")
                continue

            try:
                driver.get("https://login.live.com/logout.srf")
                time.sleep(3)
            except WebDriverException:
                pass
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
