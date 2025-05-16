from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def main():
    options = Options()
    options.add_argument("--headless=new")  # або "--headless" якщо стара версія ChromeDriver
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://rewards.microsoft.com/")

        print("Title:", driver.title)

        # Тут вставляй логіку фармінгу Microsoft Rewards або будь-які інші дії
        # Приклад:
        time.sleep(3)  # почекаємо поки сторінка завантажиться

        # Наприклад, шукаємо логін кнопку (приклад)
        login_button = driver.find_element(By.LINK_TEXT, "Sign in")
        login_button.click()

        time.sleep(5)  # даємо час на відкриття логіну

        print("Скрипт успішно запущений!")

    except Exception as e:
        print("Сталася помилка:", e)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
