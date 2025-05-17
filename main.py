import os
import json
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Читаємо акаунти з змінних оточення
ACCOUNTS_JSON = os.getenv("ACCOUNTS_JSON")
if not ACCOUNTS_JSON:
    print("❌ Помилка: змінна оточення ACCOUNTS_JSON не задана!")
    exit(1)

accounts = json.loads(ACCOUNTS_JSON)

# Список 120+ пошукових термінів
SEARCH_TERMS = [
    "Ukraine history", "Kyiv attractions", "Chernobyl disaster", "Ukrainian cuisine",
    "Python programming", "JavaScript tutorials", "Machine learning basics", "AI news",
    "SpaceX launches", "NASA discoveries", "Mars rover updates", "Black holes explained",
    "Healthy breakfast ideas", "Mediterranean diet", "Vegan recipes", "Keto diet plan",
    "Best movies 2024", "Oscar winners 2024", "Netflix new releases", "Disney+ shows",
    "Travel to Japan", "Europe backpacking tips", "Best beaches in Thailand", "Paris attractions",
    "Climate change facts", "Renewable energy sources", "Electric cars comparison", "Solar panels",
    "How to meditate", "Yoga for beginners", "Stress relief techniques", "Mindfulness exercises",
    "Stock market news", "Bitcoin price prediction", "NFT explained", "How to invest in stocks",
    "Premier League results", "NBA playoffs 2024", "Olympics 2024 schedule", "Tennis grand slams",
    "Latest tech gadgets", "iPhone 15 review", "Best laptops 2024", "Smart home devices",
    "World War 2 history", "Ancient Egypt facts", "Roman empire timeline", "Greek mythology",
    "How to learn Spanish", "French for beginners", "English grammar rules", "Japanese alphabet",
    "Digital marketing trends", "SEO best practices", "Social media strategies", "Email marketing tips",
    "Albert Einstein biography", "Marie Curie discoveries", "Nikola Tesla inventions", "Stephen Hawking theories",
    "Louvre museum virtual tour", "Van Gogh paintings", "Renaissance art", "Modern architecture",
    "Best smartphones 2024", "Android vs iOS", "Camera phone comparison", "Foldable phones",
    "Sustainable fashion", "Fast fashion impact", "Winter outfit ideas", "Summer fashion trends",
    "Italian pasta recipes", "Mexican food near me", "Indian curry dishes", "Chinese cooking techniques",
    "WWII documentaries", "Nature documentaries", "True crime series", "Science channel shows",
    "Benefits of reading", "Best fiction books 2024", "Non-fiction recommendations", "Book club ideas",
    "Photography tips", "Best DSLR cameras", "Lightroom tutorials", "Portrait photography",
    "Home workout routine", "Gym exercises for beginners", "Weight loss tips", "Muscle building diet",
    "Hubble telescope images", "International Space Station", "Solar system planets", "Astronomy for beginners",
    "Premier League transfers", "Champions League fixtures", "World Cup 2026 news", "Football tactics",
    "Mediterranean cruise tips", "Safari in Africa", "Ski resorts in Alps", "Caribbean islands guide",
    "Software development process", "Agile methodology", "Coding interview questions", "Git commands",
    "Healthy snack ideas", "Smoothie recipes", "Meal prep for week", "Detox drinks",
    "Programming challenges", "Leetcode solutions", "Hackerrank tips", "Code wars katas",
    "Mobile photography tricks", "Instagram reels ideas", "TikTok trends 2024", "YouTube SEO",
    "Ethical AI principles", "ChatGPT uses", "Deep learning explained", "Neural networks"
]

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
    except Exception as e:
        print(f"❌ Помилка логіну для {username}: {str(e)}")
        return False

def perform_searches(driver, username):
    print(f"🚀 Починаю фармінг Microsoft Rewards для {username}...")
    num_searches = random.randint(30, 35)  # Збільшено кількість пошуків
    searches = random.sample(SEARCH_TERMS, num_searches)

    for i, term in enumerate(searches, 1):
        try:
            driver.get(f"https://www.bing.com/search?q={term.replace(' ', '+')}")
            print(f"🔍 [{i}/{num_searches}] Пошук: {term}")
            time.sleep(random.uniform(2, 5))
        except Exception as e:
            print(f"⚠ Помилка пошуку: {str(e)}")
            continue

    points = get_points(driver)
    print(f"✅ {username}: Завершено {num_searches} пошуків. Балів: {points}")

def get_points(driver):
    try:
        driver.get("https://rewards.microsoft.com/")
        time.sleep(5)
        points = driver.find_element(By.CSS_SELECTOR, "mee-rewards-counter-animation").text
        return points or "Н/Д"
    except Exception:
        return "Н/Д"

def main():
    driver = init_driver()
    try:
        for acc in accounts:
            username = acc.get("username")
            password = acc.get("password")

            if not username or not password:
                print("❌ Пропущено акаунт через відсутність логіну/пароля")
                continue

            if not login(driver, username, password):
                continue

            perform_searches(driver, username)

            # Логаут
            try:
                driver.get("https://login.live.com/logout.srf")
                time.sleep(2)
            except Exception:
                pass
            
            print(f"🔄 Очікування між акаунтами...")
            time.sleep(random.randint(10, 20))
    finally:
        driver.quit()
        print("🏁 Роботу завершено")

if __name__ == "__main__":
    main()
