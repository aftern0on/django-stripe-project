from django.urls import path
from . import views

urlpatterns = [
    path('buy/<int:id>/', views.get_session_id, name='get_session_id'),
    path('item/<int:id>', views.get_item_detail, name='get_item_detail'),
    path('buy_order/<int:id>', views.get_order_session_id, name='get_order_session_id'),
    path('order/<int:id>', views.get_order_detail, name='get_order_detail'),
    path('buy_intent/<int:id>', views.get_payment_intent_session_id, name='get_payment_intent'),
    path('item_intent/<int:id>', views.get_item_detail_intent, name='get_item_detail_intent')
]
