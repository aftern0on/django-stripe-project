from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

import stripe

from .models import Item, Order


@api_view(['GET'])
def get_session_id(request, id):
    """
    Получение Stripe Session ID для оплаты выбранного товара

    Args:
        request: Объект запроса
        id (int): Идентификатор товара

    Returns:
        Response: JSON с session_id
    """

    # Получение товара по его идентификатору
    item = get_object_or_404(Item, id=id)

    # Создание сеанса оплаты Stripe
    # Это инструмент для реализации платежной системы на сайте
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.create(
        # Принимаемые методы оплаты, в данном случае - карта
        payment_method_types=['card'],
        # Перечисление товаров, включаемые в сеанс оплаты
        line_items=[{
            # Указание параметров ценника
            'price_data': {
                'currency': item.currency,  # Указание валюты
                'product_data': {  # Данные о товаре из модели
                    'name': item.name,
                    'description': item.description
                },
                # Цена в минимальных единицах, в нашем случае - копейки
                'unit_amount': int(item.price * 100),
            },
            # Количество единиц товара, включаемые в сеанс оплаты
            'quantity': 1,
        }],
        # Установлен режим проведения платежа
        mode='payment',
        success_url=request.build_absolute_uri(item.get_absolute_url()),
        cancel_url=request.build_absolute_uri(item.get_absolute_url())
    )

    return Response({'session_id': session.id})


@api_view(['GET'])
def get_payment_intent_session_id(request, id):
    """
    Реализация Stripe Payment

    Args:
        request: Объект запроса
        id (int): Идентификатор товара

    Returns:
        Response: JSON с session_id
    """

    # Получение товара по его идентификатору
    item = get_object_or_404(Item, id=id)

    # Создание сеанса оплаты Stripe
    # Это инструмент для реализации платежной системы на сайте
    stripe.api_key = settings.STRIPE_SECRET_KEY
    intent = stripe.PaymentIntent.create(
        amount=int(item.price * 100),
        currency=item.currency,
        description=f'{item.name}: {item.description}',
        payment_method_types=['card']
    )

    return Response({'client_secret': intent.client_secret})


@api_view(['GET'])
def get_order_session_id(request, id):
    """
    Получение Stripe Session ID для оплаты товаров в Order
    Метод аналогичен get_session_id

    Args:
        request: Объект запроса
        id (int): Идентификатор заказа

    Returns:
        Response: JSON с session_id
    """

    order = get_object_or_404(Order, id=id)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Указание параметров сессии
    # Конвертирую в доллары рубли (умножаю на 80) если ценник указан в долларах
    session_params = {
        'payment_method_types': ['card'],
        'line_items': [{
            'price_data': {
                'currency': 'rub',
                'product_data': {
                    'name': item.name,
                    'description': item.description
                },
                'unit_amount':
                    int((item.price * 100 * settings.USD_TO_RUB_VALUE) if item.currency == 'usd' else (item.price * 100))
            },
            'quantity': 1
        } for item in order.items.all()],  # Генерация списка со словарями для каждого заказа
        'mode': 'payment',
        'success_url': request.build_absolute_uri(order.get_absolute_url()),
        'cancel_url': request.build_absolute_uri(order.get_absolute_url())
    }

    # Указание скидки и налога если они указаны
    if order.discount:
        session_params['discounts'] = [{'coupon': order.discount.coupon_id}]
    if order.tax:
        # На данный момент я так и не выяснил как установить налоговый вычет к запросу
        # По некоторой информации, эта возможность еще дорабатывается разработчиками Stripe
        pass

    # Создание сессии
    session = stripe.checkout.Session.create(**session_params)
    return Response({'session_id': session.id})


@api_view(['GET'])
def get_order_detail(request, id):
    """
    Получение информации о заказе по его идентификатору
    Метод аналогичен методу get_item_detail

    Args:
        request (HttpRequest): Объект запроса
        id (int): Идентификатор заказа

    Returns:
        Response: Информация о товаре в виде JSON
    """

    # Получение информации о заказе по его id
    order = Order.objects.get(id=id)

    # Отправка страницы с информацией о заказе
    return render(request, 'stripe_app/order_detail.html', {'order': order})


@api_view(['GET'])
def get_item_detail(request, id):
    """
    Получение информации о товаре по его идентификатору

    Args:
        request (HttpRequest): Объект запроса
        id (int): Идентификатор товара

    Returns:
        Response: Информация о товаре в виде JSON
    """

    # Получение информации о товаре по id
    item = Item.objects.get(id=id)

    # Отправка страницы
    return render(request, 'stripe_app/item_detail.html', {'item': item})


@api_view(['GET'])
def get_item_detail_intent(request, id):
    """
    Получение информации о товаре по его идентификатору
    Используется метод Payment Intent

    Args:
        request (HttpRequest): Объект запроса
        id (int): Идентификатор товара

    Returns:
        Response: Информация о товаре в виде JSON
    """

    # Получение информации о товаре по id
    item = Item.objects.get(id=id)

    # Отправка страницы
    return render(request, 'stripe_app/item_intent_detail.html', {'item': item})



