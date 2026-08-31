from django.contrib import admin
from .models import Table, Booking, Order, OrderItem, BookingItem


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'name', 'capacity', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = ('table_number', 'name')


class BookingItemInline(admin.TabularInline):
    """Позиции брони (блюда) внутри брони"""
    model = BookingItem
    extra = 0
    readonly_fields = ('name', 'quantity', 'price', 'total')
    fields = ('name', 'quantity', 'price', 'total')
    can_delete = False
    
    def total(self, obj):
        return obj.total
    total.short_description = 'Сумма'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_phone', 'table', 'date', 'time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('client_name', 'client_phone')
    list_editable = ('status',)
    inlines = [BookingItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('name', 'quantity', 'price', 'total')
    fields = ('name', 'quantity', 'price', 'total')
    can_delete = False
    
    def total(self, obj):
        quantity = obj.quantity or 0
        price = obj.price or 0
        return quantity * price
    total.short_description = 'Сумма'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_name', 'client_phone', 'delivery_time', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at', 'payment_method')
    search_fields = ('client_name', 'client_phone', 'address')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'total_amount')
    
    fieldsets = (
        ('👤 Информация о клиенте', {
            'fields': ('client_name', 'client_phone', 'address')
        }),
        ('🕐 Доставка', {
            'fields': ('delivery_time', 'payment_method', 'comment')
        }),
        ('💰 Финансы', {
            'fields': ('total_amount', 'delivery_cost')
        }),
        ('📌 Статус', {
            'fields': ('status',)
        }),
        ('📅 Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    inlines = [OrderItemInline]
    
    def save_model(self, request, obj, form, change):
        if not obj.total_amount:
            items_total = sum(item.price * item.quantity for item in obj.items.all())
            obj.total_amount = items_total + obj.delivery_cost
        super().save_model(request, obj, form, change)
    
    actions = ['mark_as_confirmed', 'mark_as_cooking', 'mark_as_delivery', 'mark_as_completed']
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, f"{queryset.count()} заказов подтверждено")
    mark_as_confirmed.short_description = "✅ Подтвердить выбранные заказы"
    
    def mark_as_cooking(self, request, queryset):
        queryset.update(status='cooking')
        self.message_user(request, f"{queryset.count()} заказов в готовке")
    mark_as_cooking.short_description = "👨‍🍳 Отправить в готовку"
    
    def mark_as_delivery(self, request, queryset):
        queryset.update(status='delivery')
        self.message_user(request, f"{queryset.count()} заказов передано курьеру")
    mark_as_delivery.short_description = "🚚 Передать курьеру"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f"{queryset.count()} заказов доставлено")
    mark_as_completed.short_description = "✅ Отметить доставленными"