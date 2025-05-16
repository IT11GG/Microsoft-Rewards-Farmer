import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import ms_rewards_farmer  # Імпортуємо основну логіку з репозиторію

# Discord вебхук
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1372966997155123271/UTEW897KukaozKJsTK0xNb-S2oI9t9IXPHd4WwFudJCrldOc-ZXmBPv_mkJWGSo38W8K"

# Відправка повідомлення в Discord
def send_discord_message(content, ping_everyone=False):
    data = {"content": content}
    if ping_everyone:
        data["content"] = "@everyone " + content
    requests.post(DISCORD_WEBHOOK, json=data)

# Отримання балансу акаунта
def get_account_balance(driver):
    driver.get("https://rewards.microsoft.com/pointsbreakdown")
    time.sleep(5)
    balance_element = driver.find_element(By.CLASS_NAME, "points-balance")
    return int(balance_element.text.replace(",", ""))

# Вивід картки Overwatch
def redeem_overwatch_card(driver, username):
    driver.get("https://rewards.microsoft.com/redeem")
    time.sleep(5)
    # Знаходимо картку Overwatch (200 монет за 2000 балів)
    card_element = driver.find_element(By.XPATH, "//div[contains(text(), 'Overwatch 200 Coins')]")
    card_element.click()
    time.sleep(3)
    redeem_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Redeem')]")
    redeem_button.click()
    time.sleep(10)
    # Отримуємо код (припустимо, він відображається на сторінці)
    code_element = driver.find_element(By.CLASS_NAME, "reward-code")
    code = code_element.text
    return code

def main():
    # Завантаження акаунтів із файлу
    with open("accounts.json", "r") as f:
        accounts = json.load(f)

    # Налаштування Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    send_discord_message("🚀 Починаю фармінг Microsoft Rewards...")

    for account in accounts:
        username = account["username"]
        password = account["password"]
        send_discord_message(f"📧 Обробка акаунта: {username}")

        driver = webdriver.Chrome(options=chrome_options)
        try:
            # Логін і фармінг (використовуємо логіку з репозиторію)
            ms_rewards_farmer.login(driver, username, password)
            ms_rewards_farmer.farm_points(driver)

            # Отримання балансу
            balance = get_account_balance(driver)
            send_discord_message(f"💰 Баланс {username}: {balance} балів")

            # Перевірка на вивід картки
            if balance >= 2000:
                send_discord_message(f"🎮 Виявлено достатньо балів для {username}! Вивожу картку Overwatch...")
                code = redeem_overwatch_card(driver, username)
                send_discord_message(f"✅ Успішно виведено картку Overwatch для {username}! Код: `{code}`", ping_everyone=True)
            else:
                send_discord_message(f"⚠️ Недостатньо балів для {username} (потрібно 2000, є {balance})")

        except Exception as e:
            send_discord_message(f"❌ Помилка для {username}: {str(e)}")
        finally:
            driver.quit()

    send_discord_message("🏁 Фармінг завершено!")

if __name__ == "__main__":
    main()
