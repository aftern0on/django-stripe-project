<h2>Техническое задание с использование Django + Stripe</h2>

Тестовое задание на [Google Docs](https://docs.google.com/document/d/1J_Zz65Pv4U2nVQ0XYk-JjeBwR3K6KBHMIqv2DBHMYDQ/edit?usp=sharing), сделал все включая бонусные.
1. Откройте где-нибудь консоль, введите `git clone https://github.com/aftern0on/django-stripe-project`
2. Зайдите в папку с проектом: `cd django-stripe-project`
3. Создайте в корневной папке .env файл с переменными `DJANGO_SECRET_KEY` и `STRIPE_SECRET_API_KEY`.
   Так как проект тестовый и конфиденциальность не особо важна (кроме stipe_api_key, но мне не жалко):
   ```env
   DJANGO_SECRET_KEY=django-insecure-7bmnh4l=fvtadu7os47p8#)p9xga#l_e3=7fh^%7uf1m-%vumh
   STRIPE_SECRET_API_KEY=sk_test_51OPTRBI94bcLY9kPrClMq43F70zKF35ZYFENl0wtvJG8T7TVMWBsShrbvUROag95p6AX6D0glb5qcXZ2YODVL3iW00ASkgg6Ad
   ```
5. Соберите образ docker: `docker build -t stripe .`
6. Запустите контейнер с Django-сервером: `docker run --name stripe -d -p 8000:8000 stripe`

Сервер заработает по адресу http://127.0.0.1:8000 в фоновом режиме
Состояние контейнера можно отслеживать при помощи команды `docker logs -f stripe` или в Docker Desktop

6. Зарегестрируйте пользователя: `docker exec -it stripe pipenv run python manage.py createsuperuser`, почту можно не вводить
7. Перейдите в http://127.0.0.1:8000/admin/ и введите данные регистрации
8. Создайте несколько товаров модели Items (цена не менее 0.33$), и заказов модели Orders. По желанию можно добавить к Order скидку.


* Чтобы купить товар, перейдите по http://127.0.0.1:8000/api/item/{id_товара}
* Чтобы купить заказ, перейдите по http://127.0.0.1:8000/api/order/{id_заказа}
* Чтобы купить товар с использование Payment Intent, перейдите по http://127.0.0.1:8000/api/item_intent/{id_товара}, данные карты для тестирования: `4242 4242 4242 4242`, любую будущую дату, любой почтовый индекс.
