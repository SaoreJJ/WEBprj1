from rest_framework import viewsets, generics, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        """
        Настройка прав доступа в зависимости от действия
        """
        if self.action in ['list', 'retrieve']:
            # Просмотр доступен авторизованным пользователям
            permission_classes = [IsAuthenticated]
        elif self.action in ['create']:
            # Создание доступно только НЕ модераторам
            permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['update', 'partial_update']:
            # Изменение доступно модераторам ИЛИ владельцам
            permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action in ['destroy']:
            # Удаление доступно только владельцам (не модераторам)
            permission_classes = [IsAuthenticated, IsOwner, ~IsModerator]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # При создании автоматически назначаем владельца
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user

        # Модераторы видят все курсы
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()

        # Обычные пользователи видят только свои курсы
        return Course.objects.filter(owner=user)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            # Просмотр списка доступен всем авторизованным
            return [IsAuthenticated()]
        elif self.request.method == 'POST':
            # Создание доступно только НЕ модераторам
            return [IsAuthenticated(), ~IsModerator()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # При создании автоматически назначаем владельца
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user

        # Модераторы видят все уроки
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()

        # Обычные пользователи видят только свои уроки
        return Lesson.objects.filter(owner=user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            # Просмотр доступен всем авторизованным
            return [IsAuthenticated()]
        elif self.request.method in ['PUT', 'PATCH']:
            # Изменение доступно модераторам ИЛИ владельцам
            return [IsAuthenticated(), permissions.Or(IsModerator, IsOwner)]
        elif self.request.method == 'DELETE':
            # Удаление доступно только владельцам (не модераторам)
            return [IsAuthenticated(), IsOwner, ~IsModerator()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        # Модераторы видят все уроки
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()

        # Обычные пользователи видят только свои уроки
        return Lesson.objects.filter(owner=user)