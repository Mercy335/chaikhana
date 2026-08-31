import requests
from django.conf import settings


def send_telegram_notification(booking):
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        print("❌ Telegram не настроен")
        return False
    
    # Формируем список блюд
    items_text = ""
    total = 0
    for item in booking.items.all():
        items_text += f"{item.name} × {item.quantity} — {item.total} ₽\n"
        total += item.total
    
    if items_text:
        items_text = f"\n📦 *Заказ блюд:*\n{items_text}💳 *Итого:* {total} ₽\n"
    else:
        items_text = "\n📦 *Без заказа блюд*\n"
    
    message = f"""
🆕 *НОВАЯ БРОНЬ В ЧАЙХАНЕ!*

👤 *Клиент:* {booking.client_name}
📞 *Телефон:* {booking.client_phone}
🍽 *Стол:* #{booking.table.table_number} ({booking.table.name})
👥 *Гостей:* {booking.guests_count}
📅 *Дата:* {booking.date}
🕐 *Время:* {booking.time}
{items_text}
📌 *Статус:* {booking.get_status_display()}
    """
    
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': settings.TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print("✅ Telegram уведомление отправлено")
            return True
        else:
            print(f"❌ Ошибка Telegram: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при отправке в Telegram: {e}")
        return False


def send_email_notification(booking):
    """Отправка уведомления на Email (опционально)"""
    # Если Email не настроен - пропускаем
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_RECIPIENT:
        print("⚠️ Email не настроен")
        return False
    
    # ... код для Email (если будет нужен) ...
    pass


def send_all_notifications(booking):
    """Отправка всех уведомлений"""
    telegram_sent = send_telegram_notification(booking)
    email_sent = send_email_notification(booking)
    
    if telegram_sent or email_sent:
        print("✅ Уведомления отправлены")
    else:
        print("⚠️ Уведомления не отправлены")
    
    return telegram_sent or email_sent

def send_telegram_order_notification(order):
    """Отправка уведомления о новом заказе в Telegram"""
    
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        print("❌ Telegram не настроен")
        return False
    
    # Собираем позиции заказа
    items_text = ""
    for item in order.items.all():
        items_text += f"{item.name} × {item.quantity} — {item.total} ₽\n"
    
    message = f"""
🆕 *НОВЫЙ ЗАКАЗ #{order.id}*

👤 *Клиент:* {order.client_name}
📞 *Телефон:* {order.client_phone}
📍 *Адрес:* {order.address}
🕐 *Доставка:* {order.delivery_time}
💳 *Оплата:* {order.get_payment_method_display()}

📦 *Состав заказа:*
{items_text}

💰 *Сумма:* {order.total_amount} ₽
🚚 *Доставка:* {order.delivery_cost} ₽
💳 *Итого:* {order.total_amount + order.delivery_cost} ₽

📌 *Статус:* {order.get_status_display()}
    """
    
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': settings.TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print(f"✅ Telegram уведомление о заказе #{order.id} отправлено")
            return True
        else:
            print(f"❌ Ошибка Telegram: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при отправке в Telegram: {e}")
        return False