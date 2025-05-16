import json
import time
import logging
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)

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

# Логін у Microsoft Rewards з явними очікуваннями
def login(driver, username, password):
    wait = WebDriverWait(driver, 15)

    try:
        driver.get("https://login.live.com")
        # Чекаємо на появу поля для введення емейлу
        email_input = wait.until(EC.presence_of_element_located((By.ID, "i0116")))
        email_input.clear()
        email_input.send_keys(username)

        next_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
        next_button.click()

        # Чекаємо на появу поля для введення паролю
        password_input = wait.until(EC.presence_of_element_located((By.ID, "i0118")))
        password_input.clear()
        password_input.send_keys(password)

        signin_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
        signin_button.click()

        # Чекаємо, поки не відбудеться редирект або з'явиться якийсь елемент, що підтверджує вхід
        time.sleep(5)  # Альтернативно можна додати чекання на конкретний елемент сторінки після логіну

        logging.info(f"Успішний логін для {username}")

    except TimeoutException:
        logging.error(f"Таймаут при логіні для {username} - елемент не знайдено або неактивний.")
        raise
    except Exception as e:
        logging.error(f"Помилка логіну для {username}: {e}")
        raise

# Фармінг балів
def farm_points(driver):
    wait = WebDriverWait(driver, 15)

    try:
        driver.get("https://rewards.microsoft.com")
        time.sleep(5)  # Коротке очікування для завантаження сторінки

        # Приклад фармінгу: шукаємо елементи пошуку і запускаємо пошук (потрібно адаптувати під актуальний сайт)
        search_boxes = driver.find_elements(By.CLASS_NAME, "search-box")
        for box in search_boxes:
            box.clear()
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
    wait = WebDriverWait(driver, 15)

    try:
        driver.get("https://rewards.microsoft.com/pointsbreakdown")
        # Чекаємо, поки з'явиться елемент балансу
        balance_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "points-balance")))
        balance_text = balance_element.text.replace(",", "").strip()
        balance = int(balance_text)
        return balance
    except TimeoutException:
        logging.error("Не вдалося знайти елемент балансу (таймаут)")
        return 0
    except Exception as e:
        logging.error(f"Помилка отримання балансу: {e}")
        return 0

# Вивід картки Overwatch
def redeem_overwatch_card(driver, username):
    wait = WebDriverWait(driver, 15)

    try:
        driver.get("https://rewards.microsoft.com/redeem")
        # Чекаємо поки з'явиться картка
        card_element = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(text(), 'Overwatch 200 Coins')]")
        ))
        card_element.click()
        time.sleep(3)

        redeem_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Redeem')]")
        ))
        redeem_button.click()

        # Чекаємо поки з'явиться код
        code_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "reward-code")))
        return code_element.text
    except TimeoutException:
        logging.error("Не вдалося знайти елемент картки Overwatch або кнопку виведення (таймаут)")
        return None
    except Exception as e:
        logging.error(f"Помилка виведення картки: {e}")
        return None

def main():
    try:
        with open("accounts.json", "r", encoding="utf-8") as f:
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
        username = account.get("username")
        password = account.get("password")

        if not username or not password:
            logging.warning(f"Пропущено акаунт з некоректними даними: {account}")
            continue

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
                except Exception:
                    pass

    send_discord_message("🏁 Фармінг завершено!")

if __name__ == "__main__":
    main()
