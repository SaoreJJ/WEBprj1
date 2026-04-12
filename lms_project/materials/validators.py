import re
from rest_framework import serializers


def validate_youtube_url(value):
    """
    Проверяет, что ссылка ведет на youtube.com
    """
    # Регулярное выражение для проверки YouTube ссылок
    youtube_pattern = r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$"

    if not re.match(youtube_pattern, value):
        raise serializers.ValidationError(
            "Разрешены только ссылки на YouTube (youtube.com или youtu.be)"
        )
    return value


# Альтернативный вариант - класс-валидатор
class YouTubeURLValidator:
    """
    Класс-валидатор для проверки YouTube ссылок
    """

    def __init__(self, field="video_link"):
        self.field = field

    def __call__(self, data):
        value = data.get(self.field)
        if value:
            youtube_pattern = r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$"
            if not re.match(youtube_pattern, value):
                raise serializers.ValidationError(
                    {
                        self.field: "Разрешены только ссылки на YouTube (youtube.com или youtu.be)"
                    }
                )
        return data
