from rest_framework import serializers
from .models import Course, Lesson
from .validators import validate_youtube_url, YouTubeURLValidator


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        # Вариант 1: Использование валидатора в Meta
        validators = [YouTubeURLValidator(field="video_link")]

    # Вариант 2: Использование функции-валидатора для конкретного поля
    def validate_video_link(self, value):
        return validate_youtube_url(value)


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "preview",
            "description",
            "lessons_count",
            "lessons",
            "is_subscribed",
        ]

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.subscriptions.filter(user=request.user).exists()
        return False
