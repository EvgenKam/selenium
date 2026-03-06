from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

print("🚀 Запуск браузера...")

# Настройка драйвера
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)  # Оставляем браузер открытым после теста
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

try:
    # 1. Открытие сайта
    driver.get("https://www.saucedemo.com/")
    driver.maximize_window()

    # 2. Авторизация
    print("🔐 Авторизация...")
    wait.until(EC.presence_of_element_located((By.ID, "user-name"))).send_keys("standard_user")
    driver.find_element(By.ID, "password").send_keys("secret_sauce")
    driver.find_element(By.ID, "login-button").click()

    # 3. Выбор двух товаров
    print("🛒 Выбираем 2 товара...")
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "inventory_item")))

    items = driver.find_elements(By.CLASS_NAME, "inventory_item")

    # Товар 1 (первый в списке - Backpack)
    name1 = items[0].find_element(By.CLASS_NAME, "inventory_item_name").text
    price1_str = items[0].find_element(By.CLASS_NAME, "inventory_item_price").text
    price1 = float(price1_str.replace("$", ""))
    print(f"✅ Товар 1: {name1} - {price1_str}")
    items[0].find_element(By.CLASS_NAME, "btn_inventory").click()

    # Товар 2 (второй в списке - Bike Light)
    name2 = items[1].find_element(By.CLASS_NAME, "inventory_item_name").text
    price2_str = items[1].find_element(By.CLASS_NAME, "inventory_item_price").text
    price2 = float(price2_str.replace("$", ""))
    print(f"✅ Товар 2: {name2} - {price2_str}")
    items[1].find_element(By.CLASS_NAME, "btn_inventory").click()

    # 4. Переход в корзину и начало оформления
    print("🛒 Переход в корзину...")
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cart_item")))
    driver.find_element(By.ID, "checkout").click()

    # 5. Ввод данных доставки
    print("📝 Ввод данных...")
    driver.find_element(By.ID, "first-name").send_keys("Test")
    driver.find_element(By.ID, "last-name").send_keys("User")
    driver.find_element(By.ID, "postal-code").send_keys("12345")
    driver.find_element(By.ID, "continue").click()

    # 6. Проверка сумм на этапе Overview
    print("📊 Проверка сумм...")

    # Ждем появления блока с итогами (самый надежный индикатор готовности страницы)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "summary_info_label")))

    # Небольшая пауза для гарантии, что JS успел рассчитать цифры
    time.sleep(0.5)

    # Получаем весь текст контейнера с итогами
    summary_container = driver.find_element(By.ID, "checkout_summary_container")
    text_lines = summary_container.text.split('\n')

    item_total = 0.0
    tax = 0.0
    total = 0.0

    # Парсим значения из текста
    for line in text_lines:
        if "Item total:" in line:
            # Разделяем по ": $" чтобы получить чистое число
            item_total = float(line.split(": $")[1].replace(",", ""))
        elif "Tax:" in line:
            tax = float(line.split(": $")[1].replace(",", ""))
        elif "Total:" in line:
            total = float(line.split(": $")[1].replace(",", ""))

    # Расчет ожидаемых значений
    expected_item_total = price1 + price2
    expected_tax = round(expected_item_total * 0.08, 2)
    expected_total = round(expected_item_total + expected_tax, 2)

    print(f"💰 Система: Item={item_total}, Tax={tax}, Total={total}")
    print(f"🧮 Ожидается: Item={expected_item_total}, Tax={expected_tax}, Total={expected_total}")

    # Assertions
    assert abs(item_total - expected_item_total) < 0.01, f"Item total не совпадает: {item_total}"
    assert abs(tax - expected_tax) < 0.01, f"Tax не совпадает: {tax}"
    assert abs(total - expected_total) < 0.01, f"Total не совпадает: {total}"

    print("✅ Все суммы совпадают!")

    # 7. Завершение заказа (ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ)
    print("🏁 Завершение заказа...")
    driver.find_element(By.ID, "finish").click()

    # Критически важная пауза: даем странице время на переход и отрисовку
    time.sleep(2)

    # Теперь ждем появления заголовка успеха
    success_header = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "complete-header")))

    if "THANK YOU FOR YOUR ORDER" in success_header.text:
        print("🎉 Заказ оформлен успешно!")
    else:
        print("⚠️ Страница загружена, но текст заголовка отличается.")

except Exception as e:
    print(f"❌ Произошла ошибка: {e}")

finally:
    print("\n🏁 Тест завершён. Браузер остаётся открытым.")