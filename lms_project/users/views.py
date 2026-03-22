from rest_framework import viewsets, filters, generics, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Payment
from .serializers import UserSerializer, PaymentSerializer, UserRegistrationSerializer
from .permissions import IsModerator, IsOwner
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import UserPublicSerializer
from .permissions import IsOwnerProfile


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        # Для просмотра чужого профиля используем публичный сериализатор
        if self.action == 'retrieve' and self.request.user != self.get_object():
            return UserPublicSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            # Редактировать может только владелец профиля
            return [IsAuthenticated(), IsOwnerProfile()]
        return super().get_permissions()

    def get_queryset(self):
        # Пользователь может видеть только свой профиль в списке
        if self.action == 'list':
            return User.objects.filter(id=self.request.user.id)
        return super().get_queryset()


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