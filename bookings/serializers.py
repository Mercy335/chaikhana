from rest_framework import serializers
from .models import Table, Booking, Order, OrderItem, BookingItem

class TableSerializer(serializers.ModelSerializer):
    """Сериализатор для столов"""
    
    class Meta:
        model = Table
        fields = ['id', 'table_number', 'name', 'capacity']
        # fields = '__all__'  # если хочешь все поля

class BookingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingItem
        fields = ['name', 'quantity', 'price']


class BookingSerializer(serializers.ModelSerializer):
    items = BookingItemSerializer(many=True, required=False)
    
    class Meta:
        model = Booking
        fields = '__all__'
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        booking = Booking.objects.create(**validated_data)
        
        for item_data in items_data:
            BookingItem.objects.create(booking=booking, **item_data)
        
        return booking


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'client_name', 'client_phone', 'address',
            'delivery_time', 'payment_method', 'comment',
            'status', 'total_amount', 'delivery_cost',
            'created_at', 'items'
        ]
        read_only_fields = ['status', 'total_amount', 'created_at']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Считаем сумму
        subtotal = sum(item['price'] * item['quantity'] for item in items_data)
        delivery_cost = validated_data.get('delivery_cost', 150)
        total = subtotal + delivery_cost
        
        # Создаем заказ
        order = Order.objects.create(
            total_amount=total,
            **validated_data
        )
        
        # Создаем позиции заказа
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order