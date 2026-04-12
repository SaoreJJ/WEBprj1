from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import Group
from users.models import User, Subscription
from materials.models import Course, Lesson


class LessonTests(APITestCase):
    def setUp(self):
        # Создаем пользователей
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        self.moderator = User.objects.create_user(
            email="moderator@test.com",
            password="modpass123",
            first_name="Mod",
            last_name="User",
        )

        # Создаем группу модераторов
        moderator_group, _ = Group.objects.get_or_create(name="moderators")
        self.moderator.groups.add(moderator_group)

        self.other_user = User.objects.create_user(
            email="other@test.com", password="otherpass123"
        )

        # Создаем курс
        self.course = Course.objects.create(
            title="Test Course", description="Test Description", owner=self.user
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            title="Test Lesson",
            description="Test Lesson Description",
            video_link="https://www.youtube.com/watch?v=test123",
            course=self.course,
            owner=self.user,
        )

        # Настраиваем клиенты
        self.client = APIClient()

    def test_create_lesson_with_valid_youtube_url(self):
        """Тест создания урока с корректной YouTube ссылкой"""
        self.client.force_authenticate(user=self.user)
        url = reverse("lesson-list")
        data = {
            "title": "New Lesson",
            "description": "Description",
            "video_link": "https://www.youtube.com/watch?v=valid123",
            "course": self.course.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lesson_with_invalid_url(self):
        """Тест создания урока с некорректной ссылкой (не YouTube)"""
        self.client.force_authenticate(user=self.user)
        url = reverse("lesson-list")
        data = {
            "title": "New Lesson",
            "description": "Description",
            "video_link": "https://vimeo.com/123456",
            "course": self.course.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("video_link", str(response.data))

    def test_lesson_list_pagination(self):
        """Тест пагинации списка уроков"""
        self.client.force_authenticate(user=self.user)

        # Создаем 15 уроков
        for i in range(15):
            Lesson.objects.create(
                title=f"Lesson {i}",
                description="Test",
                video_link="https://www.youtube.com/watch?v=test",
                course=self.course,
                owner=self.user,
            )

        url = reverse("lesson-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)

    def test_moderator_can_view_any_lesson(self):
        """Тест: модератор может просматривать любые уроки"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse("lesson-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_moderator_can_edit_any_lesson(self):
        """Тест: модератор может редактировать любой урок"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse("lesson-detail", args=[self.lesson.id])
        data = {"title": "Updated by Moderator"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated by Moderator")

    def test_moderator_cannot_delete_lesson(self):
        """Тест: модератор не может удалять уроки"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse("lesson-detail", args=[self.lesson.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_their_lesson(self):
        """Тест: владелец может удалить свой урок"""
        self.client.force_authenticate(user=self.user)
        url = reverse("lesson-detail", args=[self.lesson.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_user_cannot_delete_lesson(self):
        """Тест: другой пользователь не может удалить чужой урок"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse("lesson-detail", args=[self.lesson.id])
        response = self.client.delete(url)

        # Ожидаем 403 или 404
        self.assertIn(
            response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        )


class SubscriptionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com", password="testpass123"
        )

        self.other_user = User.objects.create_user(
            email="other@test.com", password="otherpass123"
        )

        self.course = Course.objects.create(
            title="Test Course", description="Test Description", owner=self.user
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_subscription(self):
        """Тест создания подписки"""
        url = reverse("subscribe")
        data = {"course_id": self.course.id}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка добавлена")
        self.assertTrue(response.data["subscribed"])

    def test_remove_subscription(self):
        """Тест удаления подписки"""
        # Сначала создаем подписку
        Subscription.objects.create(user=self.user, course=self.course)

        url = reverse("subscribe")
        data = {"course_id": self.course.id}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")
        self.assertFalse(response.data["subscribed"])

    def test_subscription_without_course_id(self):
        """Тест подписки без указания ID курса"""
        url = reverse("subscribe")
        data = {}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscription_to_nonexistent_course(self):
        """Тест подписки на несуществующий курс"""
        url = reverse("subscribe")
        data = {"course_id": 999}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_course_serializer_shows_subscription_status(self):
        """Тест: сериализатор курса показывает статус подписки"""
        url = reverse("course-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("is_subscribed", response.data["results"][0])
