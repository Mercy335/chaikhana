from django.db import models

# Create your models here.

class Table(models.Model):
    """Модель стола в чайхане"""
    table_number = models.IntegerField(verbose_name="Номер стола", unique=True)
    name = models.CharField(max_length=100, verbose_name="Название стола", blank=True)
    capacity = models.IntegerField(verbose_name="Вместимость (чел)")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def __str__(self):
        return f"Стол #{self.table_number} ({self.capacity} чел)"

    class Meta:
        verbose_name = "Стол"
        verbose_name_plural = "Столы"


class Booking(models.Model):
    """Модель бронирования"""
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('confirmed', 'Подтверждена'),
        ('canceled', 'Отменена'),
        ('completed', 'Завершена'),
    ]

    table = models.ForeignKey(Table, on_delete=models.CASCADE, verbose_name="Стол")
    client_name = models.CharField(max_length=100, verbose_name="Имя клиента")
    client_phone = models.CharField(max_length=20, verbose_name="Телефон")
    guests_count = models.IntegerField(verbose_name="Количество гостей")
    date = models.DateField(verbose_name="Дата бронирования")
    time = models.TimeField(verbose_name="Время бронирования")
    duration_hours = models.IntegerField(default=2, verbose_name="Длительность (часов)")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"{self.client_name} - Стол #{self.table.table_number} ({self.date} {self.time})"

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ['-date', '-time']  # Сортировка: сначала новые


class Order(models.Model):
    """Модель заказа на доставку"""
    
    STATUS_CHOICES = [
        ('new', '🆕 Новый'),
        ('confirmed', '✅ Подтвержден'),
        ('cooking', '👨‍🍳 Готовится'),
        ('delivery', '🚚 Передан курьеру'),
        ('completed', '✅ Доставлен'),
        ('canceled', '❌ Отменен'),
    ]
    
    PAYMENT_CHOICES = [
        ('cash', 'Наличные'),
        ('card', 'Карта'),
        ('transfer', 'Перевод'),
    ]
    
    client_name = models.CharField(max_length=100, verbose_name="Имя клиента")
    client_phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.TextField(verbose_name="Адрес доставки")
    delivery_time = models.TimeField(verbose_name="Время доставки")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash', verbose_name="Способ оплаты")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Сумма заказа")
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=150, verbose_name="Стоимость доставки")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    def __str__(self):
        return f"Заказ #{self.id} - {self.client_name} ({self.delivery_time})"
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Модель позиции в заказе"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    name = models.CharField(max_length=200, verbose_name="Название блюда")
    quantity = models.IntegerField(default=1, verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    
    def __str__(self):
        return f"{self.name} x{self.quantity} = {self.total} ₽"
    
    @property
    def total(self):
        quantity = self.quantity or 0
        price = self.price or 0
        return quantity * price
    
    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"


class BookingItem(models.Model):
    """Позиция в брони (блюда к брони)"""
    booking = models.ForeignKey(
        'Booking', 
        on_delete=models.CASCADE, 
        related_name='items', 
        verbose_name="Бронирование"
    )
    name = models.CharField(max_length=200, verbose_name="Название блюда")
    quantity = models.IntegerField(default=1, verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    
    def __str__(self):
        return f"{self.name} x{self.quantity} = {self.total} ₽"
    
    @property
    def total(self):
        quantity = self.quantity or 0
        price = self.price or 0
        return quantity * price
    
    class Meta:
        verbose_name = "Позиция брони"
        verbose_name_plural = "Позиции броней"