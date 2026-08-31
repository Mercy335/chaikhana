from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('api/tables', views.available_tables, name='available_tables'),
    path('api/bookings', views.create_booking, name='create_booking'),
    path('api/orders/', views.create_order, name='create_order'),
]