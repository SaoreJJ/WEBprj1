from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.utils import timezone


@shared_task
def send_course_update_notification(course_id, updated_fields):
    """Отправляет уведомления подписчикам курса"""
    from .models import Subscription
    from materials.models import Course

    try:
        course = Course.objects.get(id=course_id)
        subscriptions = Subscription.objects.filter(course=course)

        if not subscriptions.exists():
            return f"No subscribers for course {course.title}"

        subject = f"Обновление курса: {course.title}"
        message = f"Курс '{course.title}' был обновлен. Обновленные поля: {', '.join(updated_fields)}"

        recipient_list = [sub.user.email for sub in subscriptions]

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipient_list,
            fail_silently=False,
        )

        return f"Sent {len(recipient_list)} notifications"

    except Course.DoesNotExist:
        return f"Course {course_id} not found"


@shared_task
def send_lesson_update_notification(lesson_id, course_id, updated_fields):
    """Отправляет уведомления подписчикам курса об обновлении урока"""
    from .models import Subscription
    from materials.models import Course, Lesson

    try:
        course = Course.objects.get(id=course_id)
        lesson = Lesson.objects.get(id=lesson_id)
        subscriptions = Subscription.objects.filter(course=course)

        if not subscriptions.exists():
            return f"No subscribers for course {course.title}"

        subject = f"Обновление урока в курсе: {course.title}"
        message = f"Урок '{lesson.title}' в курсе '{course.title}' был обновлен. Обновленные поля: {', '.join(updated_fields)}"

        recipient_list = [sub.user.email for sub in subscriptions]

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipient_list,
            fail_silently=False,
        )

        return f"Sent {len(recipient_list)} notifications"

    except (Course.DoesNotExist, Lesson.DoesNotExist) as e:
        return f"Error: {e}"


@shared_task
def check_and_block_inactive_users():
    """Блокирует неактивных пользователей"""
    from .models import User

    month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(
        last_login__lt=month_ago,
        is_active=True,
        is_superuser=False
    )

    blocked_count = inactive_users.update(is_active=False)

    return f"Blocked {blocked_count} inactive users"