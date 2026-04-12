from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .paginators import CoursePaginator, LessonPaginator
from users.permissions import IsNotModerator, IsOwner
from django.utils import timezone
from datetime import timedelta
from users.tasks import send_course_update_notification, send_lesson_update_notification

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by("id")
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        elif self.action in ["create"]:
            return [IsAuthenticated(), IsNotModerator()]
        elif self.action in ["update", "partial_update"]:
            return [IsAuthenticated()]
        elif self.action in ["destroy"]:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moderators").exists():
            return Course.objects.all().order_by("id")
        return Course.objects.filter(owner=user).order_by("id")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def perform_update(self, serializer):
        """
        При обновлении курса отправляем уведомления подписчикам
        """
        course = self.get_object()

        # Сохраняем старые значения для сравнения
        old_title = course.title
        old_description = course.description

        # Сохраняем новые данные
        serializer.save()

        # Определяем, какие поля были изменены
        updated_fields = []
        if course.title != old_title:
            updated_fields.append('название')
        if course.description != old_description:
            updated_fields.append('описание')

        # Отправляем уведомление, если есть изменения
        if updated_fields:
            # Дополнительное задание: проверка на 4 часа
            last_update = getattr(course, 'last_update', None)
            if last_update:
                four_hours_ago = timezone.now() - timedelta(hours=4)
                if last_update > four_hours_ago:
                    # Не отправляем уведомление, если прошло меньше 4 часов
                    return

            # Сохраняем время последнего обновления
            course.last_update = timezone.now()
            course.save(update_fields=['last_update'])

            # Асинхронная отправка уведомлений
            send_course_update_notification.delay(course.id, updated_fields)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all().order_by("id")
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        elif self.request.method == "POST":
            return [IsAuthenticated(), IsNotModerator()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moderators").exists():
            return Lesson.objects.all().order_by("id")
        return Lesson.objects.filter(owner=user).order_by("id")


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all().order_by("id")
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        elif self.request.method in ["PUT", "PATCH"]:
            return [IsAuthenticated()]
        elif self.request.method == "DELETE":
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        """
        При обновлении урока отправляем уведомления подписчикам курса
        """
        lesson = self.get_object()
        old_title = lesson.title
        old_description = lesson.description

        serializer.save()

        updated_fields = []
        if lesson.title != old_title:
            updated_fields.append('название')
        if lesson.description != old_description:
            updated_fields.append('описание')

        if updated_fields:
            # Асинхронная отправка уведомлений
            send_lesson_update_notification.delay(
                lesson.id,
                lesson.course.id,
                updated_fields
            )

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moderators").exists():
            return Lesson.objects.all().order_by("id")
        return Lesson.objects.filter(owner=user).order_by("id")
