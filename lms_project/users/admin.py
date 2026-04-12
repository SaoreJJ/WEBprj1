from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django_celery_beat.admin import PeriodicTaskAdmin, IntervalScheduleAdmin, CrontabScheduleAdmin
from .models import User, Payment, Subscription


class CustomUserAdmin(UserAdmin):
    """
    Кастомная админка для модели User
    """
    list_display = ('email', 'first_name', 'last_name', 'phone', 'city', 'is_staff', 'is_active', 'last_login')
    list_filter = ('is_staff', 'is_active', 'city', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'city', 'avatar')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Админка для модели Payment
    """
    list_display = ('user', 'payment_date', 'amount', 'payment_method', 'course', 'lesson', 'status')
    list_filter = ('payment_method', 'payment_date', 'status')
    search_fields = ('user__email', 'course__title', 'lesson__title')
    raw_id_fields = ('user', 'course', 'lesson')
    readonly_fields = ('stripe_product_id', 'stripe_price_id', 'stripe_session_id', 'payment_url')

    fieldsets = (
        (None, {
            'fields': ('user', 'amount', 'payment_method')
        }),
        ('Stripe Information', {
            'fields': ('stripe_product_id', 'stripe_price_id', 'stripe_session_id', 'payment_url'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Админка для модели Subscription
    """
    list_display = ('user', 'course', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'course__title')
    raw_id_fields = ('user', 'course')
    readonly_fields = ('created_at',)


# Регистрация кастомной модели User
admin.site.register(User, CustomUserAdmin)

# Настройка админки для Celery Beat (если установлен django_celery_beat)
try:
    admin.site.unregister(PeriodicTask)
    admin.site.unregister(IntervalSchedule)
    admin.site.unregister(CrontabSchedule)


    @admin.register(PeriodicTask)
    class CustomPeriodicTaskAdmin(PeriodicTaskAdmin):
        list_display = ('name', 'task', 'enabled', 'interval', 'crontab', 'start_time', 'last_run_at')
        list_filter = ('enabled', 'task', 'interval', 'crontab')
        search_fields = ('name', 'task')


    @admin.register(IntervalSchedule)
    class CustomIntervalScheduleAdmin(IntervalScheduleAdmin):
        list_display = ('id', 'every', 'period')


    @admin.register(CrontabSchedule)
    class CustomCrontabScheduleAdmin(CrontabScheduleAdmin):
        list_display = ('id', 'minute', 'hour', 'day_of_month', 'month_of_year', 'day_of_week')

except ImportError:
    # django_celery_beat не установлен, пропускаем
    pass