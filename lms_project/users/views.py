from rest_framework import viewsets, filters, generics, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import User, Payment, Subscription
from .serializers import UserSerializer, PaymentSerializer, UserRegistrationSerializer
from .permissions import IsModerator, IsNotModerator, IsOwner
from materials.models import Course

# Импорты для Stripe (если добавляли)
import stripe


# Для сервисных функций (если добавляли Stripe)
# from .stripe_service import create_stripe_product, create_stripe_price, create_checkout_session


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list':
            return User.objects.filter(id=self.request.user.id)
        return super().get_queryset()

    def get_serializer_class(self):
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
        return Payment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)
        # Если нужно интегрировать Stripe - раскомментируйте ниже
        # if payment.course and payment.payment_method == 'stripe':
        #     product_id = create_stripe_product(payment.course.title)
        #     price_id = create_stripe_price(payment.amount, product_id)
        #     session_id, payment_url = create_checkout_session(
        #         price_id=price_id,
        #         success_url=f"{settings.FRONTEND_URL}/payment-success/",
        #         cancel_url=f"{settings.FRONTEND_URL}/payment-cancel/"
        #     )
        #     payment.stripe_product_id = product_id
        #     payment.stripe_price_id = price_id
        #     payment.stripe_session_id = session_id
        #     payment.payment_url = payment_url
        #     payment.save()

    # Для проверки статуса (дополнительное задание)
    # @action(detail=True, methods=['get'], url_path='check-status')
    # def check_status(self, request, pk=None):
    #     payment = self.get_object()
    #     if not payment.stripe_session_id:
    #         return Response({'error': 'No Stripe session associated'}, status=400)
    #     try:
    #         session = stripe.checkout.Session.retrieve(payment.stripe_session_id)
    #         payment.status = session.payment_status
    #         payment.save()
    #         return Response({'status': payment.status, 'payment_intent': session.payment_intent})
    #     except stripe.error.StripeError as e:
    #         return Response({'error': str(e)}, status=400)


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
        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            subscription.delete()
            message = "Подписка удалена"
            subscribed = False
        else:
            Subscription.objects.create(user=user, course=course)
            message = "Подписка добавлена"
            subscribed = True

        return Response({
            "message": message,
            "subscribed": subscribed,
            "course_id": course.id,
            "course_title": course.title
        })