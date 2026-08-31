import smtplib
import os
from dotenv import load_dotenv

# Указываем путь к .env (если файл не в той же папке)
env_path = os.path.join(os.path.dirname(__file__), 'chaikhana_project', '.env')
load_dotenv(env_path)

# Или просто загружаем из текущей папки
load_dotenv()

email = os.getenv('EMAIL_HOST_USER')
password = os.getenv('EMAIL_HOST_PASSWORD')

print(f"📧 Тестируем: {email}")

if not email or not password:
    print("❌ ОШИБКА: EMAIL_HOST_USER или EMAIL_HOST_PASSWORD не найдены в .env!")
    print("Проверь файл .env в папке chaikhana_project/")
    exit(1)

print(f"🔑 Пароль: {password[:4]}...{password[-4:]} (первые 4 и последние 4 символа)")

try:
    server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
    server.login(email, password)
    print("✅ Подключение к Яндексу успешно!")
    server.quit()
except Exception as e:
    print(f"❌ Ошибка: {e}")