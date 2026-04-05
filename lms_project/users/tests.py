from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import User, Payment, Subscription
from materials.models import Course


class UserRegistrationTests(APITestCase):
    """Тесты для регистрации пользователей"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-register')
        self.token_url = reverse('token_obtain_pair')

    def test_register_user_success(self):
        """Тест успешной регистрации пользователя"""
        data = {
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'first_name': 'Иван',
            'last_name': 'Петров',
            'phone': '+79991234567',
            'city': 'Москва'
        }
        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'newuser@example.com')
        self.assertEqual(response.data['first_name'], 'Иван')
        self.assertEqual(User.objects.count(), 1)

    def test_register_user_duplicate_email(self):
        """Тест регистрации с уже существующим email"""
        User.objects.create_user(
            email='existing@example.com',
            password='pass123'
        )

        data = {
            'email': 'existing@example.com',
            'password': 'newpass123'
        }
        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_invalid_email(self):
        """Тест регистрации с невалидным email"""
        data = {
            'email': 'invalid-email',
            'password': 'testpass123'
        }
        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_weak_password(self):
        """Тест регистрации со слабым паролем (менее 6 символов)"""
        data = {
            'email': 'user@example.com',
            'password': '123'
        }
        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):
        """Тест успешного входа и получения токена"""
        User.objects.create_user(
            email='login@example.com',
            password='loginpass123'
        )

        data = {
            'email': 'login@example.com',
            'password': 'loginpass123'
        }
        response = self.client.post(self.token_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_invalid_credentials(self):
        """Тест входа с неверными учетными данными"""
        data = {
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(self.token_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PaymentTests(APITestCase):
    """Тесты для платежей"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.payment_url = reverse('payment-list')

    def test_create_payment_success(self):
        """Тест успешного создания платежа"""
        data = {
            'course': self.course.id,
            'amount': 5000,
            'payment_method': 'transfer'
        }
        response = self.client.post(self.payment_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(response.data['amount'], '5000.00')
        self.assertEqual(response.data['payment_method'], 'transfer')

    def test_create_payment_without_auth(self):
        """Тест создания платежа без авторизации"""
        self.client.logout()
        data = {
            'course': self.course.id,
            'amount': 5000,
            'payment_method': 'transfer'
        }
        response = self.client.post(self.payment_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_payments(self):
        """Тест получения списка платежей"""
        Payment.objects.create(
            user=self.user,
            course=self.course,
            amount=3000,
            payment_method='cash'
        )
        Payment.objects.create(
            user=self.user,
            course=self.course,
            amount=7000,
            payment_method='transfer'
        )

        response = self.client.get(self.payment_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_sees_only_own_payments(self):
        """Тест: пользователь видит только свои платежи"""
        other_user = User.objects.create_user(
            email='other@test.com',
            password='otherpass'
        )
        Payment.objects.create(
            user=other_user,
            course=self.course,
            amount=10000,
            payment_method='transfer'
        )
        Payment.objects.create(
            user=self.user,
            course=self.course,
            amount=2000,
            payment_method='cash'
        )

        response = self.client.get(self.payment_url)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['amount'], '2000.00')

    def test_filter_payments_by_course(self):
        """Тест фильтрации платежей по курсу"""
        course2 = Course.objects.create(
            title='Another Course',
            description='Another Description',
            owner=self.user
        )
        Payment.objects.create(
            user=self.user,
            course=self.course,
            amount=3000,
            payment_method='transfer'
        )
        Payment.objects.create(
            user=self.user,
            course=course2,
            amount=5000,
            payment_method='transfer'
        )

        response = self.client.get(f"{self.payment_url}?course={self.course.id}")

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['course'], self.course.id)

    def test_filter_payments_by_method(self):
        """Тест фильтрации платежей по способу оплаты"""
        Payment.objects.create(
            user=self.user,
            course=self.course,
            amount=3000,
            payment_method='cash'
        )
        Payment.objects.create(
            user=self.user,
            course=self.course,
            amount=5000,
            payment_method='transfer'
        )

        response = self.client.get(f"{self.payment_url}?payment_method=cash")

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['payment_method'], 'cash')

    def test_ordering_payments_by_date(self):
        """Тест сортировки платежей по дате"""
        from datetime import datetime, timedelta

        payment1 = Payment.objects.create(
            user=self.user,
            course=self.course,
            amount=1000,
            payment_method='transfer'
        )
        payment1.payment_date = datetime.now() - timedelta(days=5)
        payment1.save()

        payment2 = Payment.objects.create(
            user=self.user,
            course=self.course,
            amount=2000,
            payment_method='transfer'
        )
        payment2.payment_date = datetime.now()
        payment2.save()

        response = self.client.get(f"{self.payment_url}?ordering=-payment_date")

        self.assertEqual(response.data[0]['amount'], '2000.00')


class SubscriptionTests(APITestCase):
    """Тесты для подписок на курс"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.subscribe_url = reverse('subscribe')

    def test_create_subscription_success(self):
        """Тест успешного создания подписки"""
        data = {'course_id': self.course.id}
        response = self.client.post(self.subscribe_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(response.data['subscribed'])
        self.assertTrue(Subscription.objects.filter(
            user=self.user, course=self.course
        ).exists())

    def test_remove_subscription_success(self):
        """Тест успешного удаления подписки"""
        Subscription.objects.create(user=self.user, course=self.course)

        data = {'course_id': self.course.id}
        response = self.client.post(self.subscribe_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(response.data['subscribed'])
        self.assertFalse(Subscription.objects.filter(
            user=self.user, course=self.course
        ).exists())

    def test_subscription_without_course_id(self):
        """Тест подписки без указания ID курса"""
        data = {}
        response = self.client.post(self.subscribe_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_subscription_to_nonexistent_course(self):
        """Тест подписки на несуществующий курс"""
        data = {'course_id': 999}
        response = self.client.post(self.subscribe_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscription_without_auth(self):
        """Тест подписки без авторизации"""
        self.client.logout()
        data = {'course_id': self.course.id}
        response = self.client.post(self.subscribe_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_double_subscription(self):
        """Тест: повторная подписка удаляет существующую"""
        data = {'course_id': self.course.id}

        response1 = self.client.post(self.subscribe_url, data, format='json')
        self.assertEqual(response1.data['message'], 'Подписка добавлена')

        response2 = self.client.post(self.subscribe_url, data, format='json')
        self.assertEqual(response2.data['message'], 'Подписка удалена')

        self.assertFalse(Subscription.objects.filter(
            user=self.user, course=self.course
        ).exists())


class UserProfileTests(APITestCase):
    """Тесты для профиля пользователя"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            phone='+79991234567',
            city='Moscow'
        )
        self.other_user = User.objects.create_user(
            email='other@test.com',
            password='otherpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.users_url = reverse('user-list')

    def test_user_can_view_own_profile(self):
        """Тест: пользователь может просматривать свой профиль"""
        response = self.client.get(self.users_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], 'user@test.com')

    def test_user_can_update_own_profile(self):
        """Тест: пользователь может редактировать свой профиль"""
        url = reverse('user-detail', args=[self.user.id])
        data = {'first_name': 'UpdatedName', 'city': 'SPb'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'UpdatedName')
        self.assertEqual(self.user.city, 'SPb')

    def test_user_cannot_update_other_profile(self):
        """Тест: пользователь не может редактировать чужой профиль"""
        url = reverse('user-detail', args=[self.other_user.id])
        data = {'first_name': 'Hacked'}
        response = self.client.patch(url, data, format='json')

        self.assertIn(response.status_code, [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ])

    def test_user_sees_only_own_profile_in_list(self):
        """Тест: в списке пользователей виден только свой профиль"""
        response = self.client.get(self.users_url)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], 'user@test.com')
