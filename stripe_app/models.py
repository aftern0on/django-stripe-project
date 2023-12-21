import stripe
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.urls import reverse
from django.conf import settings


class Item(models.Model):
    """
    Модель, представляющая товар

    Attributes:
        name (CharField): Наименование товара
        description (TextField): Описание товара
        price (DecimalField): Цена товара
        currency (CharField): Валюта для оплаты на выбор между рублем и долларом
    """

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(
        max_length=3, choices=[('usd', 'дол.'), ('rub', 'руб.')], default='rub')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('get_item_detail', args=[str(self.id)])


class Order(models.Model):
    """
    Модель заказа, который хранит в себе список товаров и общую их стоимость

    Attributes:
        name (CharField): Наименование заказа
        description (TextField): Описание заказа
        items (ManyToManyField): список заказываемых объектов
        total_price (DecimalField): сумма всех товаров
    """

    name = models.CharField(max_length=255, default="Пример наименования заказа")
    description = models.TextField(default="Пример описания заказа")
    items = models.ManyToManyField('Item', related_name='orders')
    total_price = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True,
        help_text='Рассчитается автоматически (без учета налога и скидок), цена в руб.')
    discount = models.ForeignKey('Discount', on_delete=models.SET_NULL, blank=True, null=True)
    tax = models.ForeignKey('Tax', on_delete=models.SET_NULL, blank=True, null=True)

    def calculate_total_price(self):
        """
        Расчет стоимости заказа исходя из стоимости каждого предмета
        """

        summary = 0
        for item in self.items.all():
            # Конвертировать рубли в доллары при расчете суммарной стоимости
            print(item.currency)
            summary += (item.price * settings.USD_TO_RUB_VALUE) if item.currency == 'usd' else item.price
        self.total_price = summary
        self.save()

    def get_absolute_url(self):
        return reverse('get_item_detail', args=[str(self.id)])


class Discount(models.Model):
    """
    Модель скидки для Order

    Attributes:
        name (CharField): поле наименования скидки
        percentage (DecimalField): процент скидки
    """

    name = models.CharField(max_length=255, blank=True, null=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    coupon_id = models.TextField(blank=True, null=True, help_text='Создается автоматически')

    def remove_coupon(self):
        # Удаление старого купона, если был создан
        if self.coupon_id:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe.Coupon.delete(self.coupon_id)

    def save(self, *args, **kwargs):
        # Создание купона скидки после создания объекта скидки
        self.remove_coupon()
        stripe.api_key = settings.STRIPE_SECRET_KEY
        coupon = stripe.Coupon.create(percent_off=self.percentage)
        self.coupon_id = coupon.id
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.remove_coupon()
        super().delete(*args, **kwargs)

    def __str__(self):
        if self.name:
            return f"{self.percentage}% - {self.name}"
        else:
            return f"{self.percentage}%"


class Tax(models.Model):
    """
    Модель налогового вычета для Order

    Attributes:
        name (CharField): поле наименования налогового вычета
        percentage (DecimalField): процент налогового вычета
    """

    name = models.CharField(max_length=255, blank=True, null=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    rate_id = models.TextField(blank=True, null=True, help_text='Создается автоматически')

    def remove_rate(self):
        # Деактивация старого купона (не понял как удалить), если был создан
        if self.rate_id:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe.TaxRate.modify(self.rate_id, active=False)

    def save(self, *args, **kwargs):
        # Создание налогового вычета после создания объекта налога
        self.remove_rate()
        stripe.api_key = settings.STRIPE_SECRET_KEY
        rate = stripe.TaxRate.create(
            display_name='VAT' if self.name is None else self.name,
            inclusive=False,
            percentage=self.percentage)
        self.rate_id = rate.id
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.remove_rate()
        super().delete(*args, **kwargs)

    def __str__(self):
        if self.name:
            return f"{self.percentage}% - {self.name}"
        else:
            return f"{self.percentage}%"


@receiver(m2m_changed, sender=Order.items.through)
def update_total_price(sender, instance: Order, **kwargs):
    """
    Функция, вызываемая при обновлении Items модели Order
    В этом случае проводится расчет общей стоимости заказа

    Attributes:
        instance (Order): объект модели заказа
    """

    if kwargs['action'] in ['post_add', 'post_remove', 'post_clear']:
        instance.calculate_total_price()
