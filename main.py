import json
import time
import logging
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('farmer.log'), logging.StreamHandler()]
)

# Discord вебхук
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1372966997155123271/UTEW897KukaozKJsTK0xNb-S2oI9t9IXPHd4WwFudJCrldOc-ZXmBPv_mkJWGSo38W8K"

# Відправка повідомлення в Discord
def send_discord_message(content, ping_everyone=False):
    try:
        data = {"content": content}
        if ping_everyone:
            data["content"] = "@everyone " + content
        response = requests.post(DISCORD_WEBHOOK, json=data)
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Не вдалося надіслати повідомлення в Discord: {e}")

# Логін у Microsoft Rewards
def login(driver, username, password):
    try:
        driver.get("https://login.live.com")
        time.sleep(2)
        driver.find_element(By.ID, "i0116").send_keys(username)
        driver.find_element(By.ID, "idSIButton9").click()
        time.sleep(2)
        driver.find_element(By.ID, "i0118").send_keys(password)
        driver.find_element(By.ID, "idSIButton9").click()
        time.sleep(5)  # Чекаємо на логін
        logging.info(f"Успішний логін для {username}")
    except Exception as e:
        logging.error(f"Помилка логіну для {username}: {e}")
        raise

# Фармінг балів
def farm_points(driver):
    try:
        driver.get("https://rewards.microsoft.com")
        time.sleep(5)
        # Припускаємо, що фармінг включає кліки по завданнях (потрібно адаптувати під актуальну структуру сайту)
        search_boxes = driver.find_elements(By.CLASS_NAME, "search-box")
        for box in search_boxes:
            box.send_keys("test search")
            time.sleep(2)
            box.submit()
            time.sleep(5)
        logging.info("Фармінг завершено")
    except Exception as e:
        logging.error(f"Помилка фармінгу: {e}")
        raise

# Отримання балансу акаунта
def get_account_balance(driver):
    try:
        driver.get("https://rewards.microsoft.com/pointsbreakdown")
        time.sleep(5)
        balance_element = driver.find_element(By.CLASS_NAME, "points-balance")
        return int(balance_element.text.replace(",", ""))
    except NoSuchElementException:
        logging.error("Не вдалося знайти елемент балансу")
        return 0
    except Exception as e:
        logging.error(f"Помилка отримання балансу: {e}")
        return 0

# Вивід картки Overwatch
def redeem_overwatch_card(driver, username):
    try:
        driver.get("https://rewards.microsoft.com/redeem")
        time.sleep(5)
        card_element = driver.find_element(By.XPATH, "//div[contains(text(), 'Overwatch 200 Coins')]")
        card_element.click()
        time.sleep(3)
        redeem_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Redeem')]")
        redeem_button.click()
        time.sleep(10)
        code_element = driver.find_element(By.CLASS_NAME, "reward-code")
        return code_element.text
    except NoSuchElementException:
        logging.error("Не вдалося знайти елемент картки Overwatch або кнопку виведення")
        return None
    except Exception as e:
        logging.error(f"Помилка виведення картки: {e}")
        return None

def main():
    try:
        with open("accounts.json", "r") as f:
            accounts = json.load(f)
    except Exception as e:
        logging.error(f"Не вдалося завантажити accounts.json: {e}")
        send_discord_message(f"❌ Не вдалося завантажити accounts.json: {e}")
        return

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    send_discord_message("🚀 Починаю фармінг Microsoft Rewards...")

    for account in accounts:
        username = account["username"]
        password = account["password"]
        send_discord_message(f"📧 Обробка акаунта: {username}")

        driver = None
        try:
            driver = webdriver.Chrome(options=chrome_options)
            login(driver, username, password)
            farm_points(driver)

            balance = get_account_balance(driver)
            send_discord_message(f"💰 Баланс {username}: {balance} балів")

            if balance >= 2000:
                send_discord_message(f"🎮 Виявлено достатньо балів для {username}! Вивожу картку Overwatch...")
                code = redeem_overwatch_card(driver, username)
                if code:
                    send_discord_message(f"✅ Успішно виведено картку Overwatch для {username}! Код: `{code}`", ping_everyone=True)
                else:
                    send_discord_message(f"❌ Не вдалося вивести картку Overwatch для {username}")
            else:
                send_discord_message(f"⚠️ Недостатньо балів для {username} (потрібно 2000, є {balance})")

        except WebDriverException as e:
            logging.error(f"Помилка WebDriver для {username}: {e}")
            send_discord_message(f"❌ Помилка WebDriver для {username}: {e}")
        except Exception as e:
            logging.error(f"Помилка обробки {username}: {e}")
            send_discord_message(f"❌ Помилка для {username}: {e}")
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    send_discord_message("🏁 Фармінг завершено!")

if __name__ == "__main__":
    main()
