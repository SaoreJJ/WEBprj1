from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Создает группы модераторов'

    def handle(self, *args, **options):
        try:
            # Создаем группу модераторов
            moderator_group, created = Group.objects.get_or_create(name='moderators')

            if created:
                self.stdout.write(self.style.SUCCESS('Группа "moderators" создана'))
            else:
                self.stdout.write(self.style.WARNING('Группа "moderators" уже существует'))

            # Выводим информацию о группе
            self.stdout.write(f'ID группы: {moderator_group.id}')
            self.stdout.write(f'Имя группы: {moderator_group.name}')
            self.stdout.write(f'Количество пользователей: {moderator_group.user_set.count()}')
            self.stdout.write(f'Количество разрешений: {moderator_group.permissions.count()}')

            self.stdout.write(self.style.SUCCESS('Команда выполнена успешно!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))