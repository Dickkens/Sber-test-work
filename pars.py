import json
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_vins(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]


def load_processed_vins(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_processed_vins(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def login(driver, email, password):
    login_url = 'https://avtokompromat.ru/user/logpass.php'
    driver.get(login_url)

    try:
        # Ждем появления поля для ввода email
        email_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, 'email'))
        )
        email_input.clear()
        email_input.send_keys(email)

        # Ждем появления поля для ввода пароля
        password_input = driver.find_element(By.NAME, 'pass')
        password_input.clear()
        password_input.send_keys(password)

        # Ждем появления кнопки входа и нажимаем её
        submit_button = driver.find_element(By.CLASS_NAME, 'submit-btn')
        submit_button.click()

        # Ожидаем, что после авторизации появится элемент, указывающий на успешную загрузку следующей страницы
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'id_param'))
        )
        logging.info("Авторизация успешна!")
    except TimeoutException:
        logging.warning("Не удалось авторизоваться!")
        return False

    return True


def parse_vin(driver, vin):
    url = 'https://avtokompromat.ru/user/gosvin.php'
    driver.get(url)

    try:
        search_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'id_param'))
        )
        search_input.clear()
        search_input.send_keys(vin)

        search_button = driver.find_element(By.ID, 'id_knop_prov1')
        search_button.click()

        # Ждем появления блока владельцев
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'blok_gibdd2'))
        )

        owners_block = driver.find_element(By.ID, 'blok_gibdd2')
        logging.debug(f"Блок владельцев: {owners_block.text}")  # Выводим текст блока для отладки

        # Ищем все элементы p, содержащие слово "запис"
        owners = owners_block.find_elements(By.XPATH, ".//p[contains(text(), 'запис')]")

        if not owners:
            logging.warning(f'Нет данных о владельцах для VIN: {vin}')
            return None

        result = {
            "owners number": owners[0].text  # Например: "1 запись"
        }

        for idx, owner in enumerate(owners[1:], 1):
            # Получаем период владения, который находится после текста "запись"
            try:
                period = owner.find_element(By.XPATH, "./following-sibling::p[1]").text
                result[f"period of possession by owner №{idx}"] = f"{owner.text} - {period}"
            except Exception as e:
                logging.warning(f"Не удалось извлечь период для владельца {idx} на VIN {vin}: {str(e)}")

        logging.info(f"Данные найдены для VIN: {vin}")
        return result

    except TimeoutException:
        logging.warning(f"Не удалось найти данные для VIN: {vin}")
        return None


def main():
    vins = load_vins('VINs.txt')
    processed_vins = load_processed_vins('processed_vins.json')

    # Укажите свои данные для логина
    email = 'ewdaasdsad@yandex.ru'  # Замените на свой email
    password = 'K0kXHcvs'  # Замените на свой пароль

    options = Options()

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Процесс авторизации
    if not login(driver, email, password):
        logging.error("Не удалось пройти авторизацию. Завершаю программу.")
        driver.quit()
        return

    for vin in vins:
        if vin in processed_vins:
            logging.info(f"VIN уже обработан: {vin}")
            continue

        logging.info(f"Обработка VIN: {vin}")
        data = parse_vin(driver, vin)
        if data:
            processed_vins[vin] = data
            save_processed_vins('processed_vins.json', processed_vins)

    driver.quit()

    with open('result.json', 'w') as file:
        json.dump(processed_vins, file, ensure_ascii=False, indent=4)

    logging.info("Парсинг завершён.")


if __name__ == "__main__":
    main()
