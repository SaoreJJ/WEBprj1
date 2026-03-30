import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_product(course_title):
    """Создает продукт в Stripe"""
    product = stripe.Product.create(
        name=course_title,
        type='service'
    )
    return product.id

def create_stripe_price(amount, product_id):
    """
    Создает цену в Stripe
    amount: сумма в рублях (целое число)
    """
    price = stripe.Price.create(
        unit_amount=amount * 100,  # в копейках
        currency='rub',
        product=product_id,
    )
    return price.id

def create_checkout_session(price_id, success_url, cancel_url):
    """Создает сессию оформления заказа"""
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.id, session.url