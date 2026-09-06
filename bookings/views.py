from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from datetime import datetime
from .models import Table, Booking
from .serializers import TableSerializer, BookingSerializer, OrderSerializer  
from .notifications import send_telegram_notification


def index(request):
    """Главная страница с формой бронирования"""
    return render(request, 'bookings/index.html')

def cart(request):
    """Страница корзины"""
    return render(request, 'bookings/cart.html')

def checkout(request):
    """Страница оформления заказа"""
    return render(request, 'bookings/checkout.html')


@api_view(['GET'])
def available_tables(request):
    """
    GET /api/tables?date=2026-06-25&time=19:00
    Возвращает список свободных столов на указанные дату и время
    """
    try:
        # Получаем параметры из запроса
        date = request.GET.get('date')
        time = request.GET.get('time')
        
        # Проверяем, что дата и время переданы
        if not date or not time:
            return Response(
                {"error": "Необходимо указать date и time (например: ?date=2026-06-25&time=19:00)"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Парсим время (ожидаем формат "19:00" или "19:00:00")
            if len(time) == 5:  # "19:00"
                time = f"{time}:00"
            booking_time = datetime.strptime(time, "%H:%M:%S").time()
        except ValueError:
            return Response(
                {"error": "Неверный формат времени. Используйте HH:MM"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            booking_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Неверный формат даты. Используйте YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Находим все активные столы
        all_tables = Table.objects.filter(is_active=True)
        
        # Находим брони, которые пересекаются с запрошенным временем
        busy_table_ids = Booking.objects.filter(
            date=booking_date,
            time=booking_time,
            status__in=['new', 'confirmed']
        ).values_list('table_id', flat=True)
        
        # Фильтруем столы: исключаем занятые
        available_tables = all_tables.exclude(id__in=busy_table_ids)
        
        # Сериализуем и возвращаем результат
        serializer = TableSerializer(available_tables, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        # Логируем ошибку
        print(f"❌ Ошибка в available_tables: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
def create_booking(request):
    table_id = request.data.get('table')
    date = request.data.get('date')
    time = request.data.get('time')
    
    if time and len(time) == 5:
        time = f"{time}:00"
    
    existing_booking = Booking.objects.filter(
        table_id=table_id,
        date=date,
        time=time,
        status__in=['new', 'confirmed']
    ).exists()
    
    if existing_booking:
        return Response(
            {"error": "Этот столик уже забронирован на выбранное время"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Используем обновленный сериализатор
    serializer = BookingSerializer(data=request.data)
    if serializer.is_valid():
        booking = serializer.save()
        
        # Отправляем уведомление в Telegram
        try:
            from .notifications import send_telegram_notification
            send_telegram_notification(booking)
        except Exception as e:
            print(f"⚠️ Ошибка уведомления: {e}")
        
        return Response(
            {
                "message": "Бронирование успешно создано! Мы перезвоним вам для подтверждения.",
                "booking": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
def create_order(request):
    """API для создания заказа на доставку"""
    
    print("=" * 50)
    print("📥 Получен запрос на создание заказа")
    print(f"📥 Данные: {request.data}")
    
    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        order = serializer.save()
        print(f"✅ Заказ #{order.id} создан")
        
        # Отправляем уведомление в Telegram
        try:
            from .notifications import send_telegram_order_notification
            send_telegram_order_notification(order)
        except Exception as e:
            print(f"⚠️ Ошибка уведомления: {e}")
        
        return Response(
            {
                "message": f"Заказ #{order.id} успешно оформлен! Мы перезвоним вам для подтверждения.",
                "order": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    print(f"❌ Ошибка валидации: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)