from django.core.management.base import BaseCommand
from users.models import User, Payment
from materials.models import Course, Lesson
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = "Заполняет таблицу платежей тестовыми данными"

    def handle(self, *args, **options):
        # Очищаем существующие платежи
        Payment.objects.all().delete()

        # Получаем пользователей (или создаем, если их нет)
        users = User.objects.all()
        if not users.exists():
            self.stdout.write(
                self.style.WARNING("Нет пользователей. Сначала создайте пользователей.")
            )
            return

        # Получаем курсы и уроки
        courses = list(Course.objects.all())
        lessons = list(Lesson.objects.all())

        if not courses and not lessons:
            self.stdout.write(
                self.style.WARNING(
                    "Нет курсов и уроков. Сначала создайте курсы и уроки."
                )
            )
            return

        payment_methods = ["cash", "transfer"]

        # Создаем тестовые платежи
        for i in range(10):
            user = random.choice(users)
            payment_date = datetime.now() - timedelta(days=random.randint(1, 30))

            # Случайно выбираем: оплата курса или урока
            if random.choice([True, False]) and courses:
                course = random.choice(courses)
                lesson = None
                amount = random.randint(3000, 10000)
            elif lessons:
                course = None
                lesson = random.choice(lessons)
                amount = random.randint(500, 3000)
            else:
                continue

            payment = Payment.objects.create(
                user=user,
                payment_date=payment_date,
                course=course,
                lesson=lesson,
                amount=amount,
                payment_method=random.choice(payment_methods),
            )

            self.stdout.write(self.style.SUCCESS(f"Создан платеж: {payment}"))

        self.stdout.write(self.style.SUCCESS("Тестовые платежи успешно созданы!"))
