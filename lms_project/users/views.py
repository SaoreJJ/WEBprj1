from rest_framework import viewsets, filters, generics, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import User, Payment, Subscription
from .serializers import UserSerializer, PaymentSerializer, UserRegistrationSerializer
from .permissions import IsModerator, IsOwner
from materials.models import Course


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Пользователь может видеть только свой профиль
        if self.action == 'list':
            return User.objects.filter(id=self.request.user.id)
        return super().get_queryset()

    def get_serializer_class(self):
        # Для просмотра чужого профиля используем публичный сериализатор
        if self.action == 'retrieve' and self.request.user != self.get_object():
            from .serializers import UserPublicSerializer
            return UserPublicSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsOwner()]
        return super().get_permissions()


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']

    def get_queryset(self):
        # Пользователь может видеть только свои платежи
        return Payment.objects.filter(user=self.request.user)


class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {"error": "Не указан ID курса"},
                status=400
            )

        course = get_object_or_404(Course, id=course_id)

        # Проверяем, есть ли уже подписка
        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            # Если подписка есть - удаляем
            subscription.delete()
            message = "Подписка удалена"
            subscribed = False
        else:
            # Если подписки нет - создаем
            Subscription.objects.create(user=user, course=course)
            message = "Подписка добавлена"
            subscribed = True

        return Response({
            "message": message,
            "subscribed": subscribed,
            "course_id": course.id,
            "course_title": course.title
        })