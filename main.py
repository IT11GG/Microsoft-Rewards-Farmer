import os
import json
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

# Читаємо акаунти з секретів (GitHub Secrets)
ACCOUNTS_JSON = os.getenv("ACCOUNTS_JSON")
if not ACCOUNTS_JSON:
    print("❌ Помилка: змінна оточення ACCOUNTS_JSON не задана!")
    exit(1)

accounts = json.loads(ACCOUNTS_JSON)

# Список ~100 пошукових термінів для рандомізації
SEARCH_TERMS = [
    "Ukraine history", "Latest tech news", "Python programming", "Space exploration",
    "Healthy recipes", "Best movies 2025", "Travel tips Europe", "Climate change effects",
    "How to meditate", "Stock market today", "Football scores", "AI breakthroughs",
    "Gardening for beginners", "Machine learning tutorials", "Electric cars",
    "Famous paintings", "Yoga exercises", "Cryptocurrency trends", "Quantum computing",
    "World landmarks", "Music festivals", "Healthy lifestyle tips", "Photography ideas",
    "Mobile app development", "Top novels 2024", "Movie reviews", "Web design trends",
    "Mediterranean diet benefits", "History of computers", "New programming languages",
    "SpaceX launches", "Virtual reality games", "Basketball highlights", "Climate policy",
    "Travel safety tips", "Learning languages online", "Digital marketing strategies",
    "Famous scientists", "Art museums", "Best smartphones", "Sustainable energy",
    "Coffee brewing methods", "Mental health awareness", "Cloud computing basics",
    "Top universities", "Latest gadgets", "Fashion trends 2025", "World cuisine recipes",
    "Historical documentaries", "Meditation benefits", "Tech startups", "Cooking hacks",
    "Science fiction books", "Photography techniques", "DIY home projects", "Electric bikes",
    "Travel photography", "Online courses", "Music theory basics", "Astronomy facts",
    "Sports news", "Mediterranean travel", "Software development life cycle",
    "Healthy snacks", "Coding challenges", "Mobile photography tips", "AI ethics",
    "Wildlife conservation", "Gaming consoles", "Fitness programs", "Space telescopes",
    "Blockchain technology", "Fashion designers", "Outdoor activities", "Nutrition facts",
    "Movie trailers", "Tech reviews", "Public speaking tips", "Gardening tools",
    "Mindfulness exercises", "Robotics competitions", "Digital art tutorials",
    "Renewable resources", "Coding bootcamps", "Astronaut training", "World cultures",
    "Healthy desserts", "Travel blogs", "Fitness gadgets", "Software testing",
    "Painting styles", "Music instruments", "Photography contests", "Car reviews",
    "Mobile games", "Yoga poses", "Science news", "Financial planning", "Space missions"
]

def init_driver():
    options = Options()
    options.add_argument("--headless")  # безголовий режим
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    return driver

def login(driver, username, password):
    driver.get("https://login.live.com/")
    time.sleep(2)

    # Ввод емейлу
    email_input = driver.find_element(By.NAME, "loginfmt")
    email_input.clear()
    email_input.send_keys(username)
    email_input.send_keys(Keys.RETURN)
    time.sleep(3)

    # Ввод пароля
    password_input = driver.find_element(By.NAME, "passwd")
    password_input.clear()
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)

    # Можливе підтвердження безпеки - пропускаємо тут

    # Перевірка успішного входу: перевіряємо, чи є елемент профілю
    try:
        driver.find_element(By.ID, "meControl")
        return True
    except NoSuchElementException:
        return False

def perform_searches(driver, username):
    print(f"🚀 Починаю фармінг Microsoft Rewards...")
    print(f"📧 Обробка акаунта: {username}")

    # Вибір рандомної кількості пошуків від 7 до 12
    num_searches = random.randint(7, 12)
    searches = random.sample(SEARCH_TERMS, num_searches)

    for term in searches:
        driver.get(f"https://www.bing.com/search?q={term.replace(' ', '+')}")
        time.sleep(random.uniform(2, 5))

    points = get_points(driver)
    print(f"✅ Пошук завершено кількість балів на цьому аккаунті: {points}")

def get_points(driver):
    try:
        driver.get("https://rewards.microsoft.com/")
        time.sleep(5)
        # Спробуємо кілька селекторів, бо сайт може змінюватись
        selectors = [
            "div.RewardsPointsCount",  # клас, де можуть показуватися бали
            "span.msportalfx-ux-fluent-text-5",  # інший можливий селектор
            "span#id_rc",  # інший варіант
        ]
        points_text = None
        for sel in selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, sel)
                points_text = elem.text.strip()
                if points_text:
                    break
            except NoSuchElementException:
                continue
        return points_text if points_text else "Н/Д"
    except Exception:
        return "Н/Д"

def main():
    driver = init_driver()

    for acc in accounts:
        username = acc.get("username")
        password = acc.get("password")

        if not username or not password:
            print(f"❌ Пропущено акаунт через відсутність username або password.")
            continue

        success = login(driver, username, password)
        if not success:
            print(f"❌ Помилка логіну для {username}")
            continue

        perform_searches(driver, username)
        # Логаут
        driver.get("https://login.live.com/logout.srf")
        time.sleep(3)

    driver.quit()

if __name__ == "__main__":
    main()
