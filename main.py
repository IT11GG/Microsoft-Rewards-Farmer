import os
import json
import random
from playwright.sync_api import sync_playwright

ACCOUNTS_JSON = os.getenv("ACCOUNTS_JSON")
accounts = json.loads(ACCOUNTS_JSON)

SEARCH_TERMS = [
    "Україна", "Київ", "Python", "JavaScript", "NASA", "Космос", 
    "Подорожі", "Рецепти", "Технології", "Наука", "Фільми 2024",
    # Додайте інші терміни (50+ для різноманітності)
]

def run_account(page, username, password):
    # Логін
    page.goto("https://login.live.com")
    page.fill("input[name='loginfmt']", username)
    page.click("input[type='submit']")
    page.fill("input[name='passwd']", password)
    page.click("input[type='submit']")
    
    # Очікуємо успішного входу
    page.wait_for_selector("#id_n", timeout=10000)

    # Виконуємо 30-40 пошуків
    for _ in range(random.randint(30, 40)):
        term = random.choice(SEARCH_TERMS)
        page.goto(f"https://www.bing.com/search?q={term}")
        page.wait_for_timeout(random.randint(2000, 5000))  # Випадкова затримка

    # Перевірка балів (приклад)
    page.goto("https://rewards.microsoft.com")
    points = page.inner_text(".pointsCount") or "N/A"
    print(f"✅ {username}: {points} балів")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        
        for account in accounts:
            page = context.new_page()
            try:
                run_account(page, account["username"], account["password"])
            except Exception as e:
                print(f"❌ Помилка для {account['username']}: {str(e)}")
            finally:
                page.close()
                time.sleep(random.randint(5, 10))  # Пауза між акаунтами
        
        browser.close()

if __name__ == "__main__":
    main()
