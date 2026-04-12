import os
from celery import Celery
from celery.schedules import crontab

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')

# Создаем экземпляр приложения Celery
app = Celery('lms_project')

# Загружаем настройки из Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим и регистрируем задачи в приложениях
app.autodiscover_tasks()

# Настройка периодических задач (Celery Beat)
app.conf.beat_schedule = {
    'block-inactive-users': {
        'task': 'users.tasks.check_and_block_inactive_users',
        'schedule': crontab(hour=0, minute=0),  # Запуск каждый день в полночь
        'options': {
            'expires': 3600,
        },
    },
}

# Настройка временной зоны
app.conf.timezone = 'UTC'

# Настройка результата задач
app.conf.result_expires = 86400  # Результаты хранятся 24 часа
app.conf.task_track_started = True
app.conf.task_time_limit = 30 * 60  # 30 минут
app.conf.task_soft_time_limit = 25 * 60  # 25 минут


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')