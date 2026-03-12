from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse


def home(request):
    html = """
    <html>
        <head>
            <title>LMS API</title>
            <style>
                body { font-family: Arial; padding: 20px; }
                .endpoint { background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px; }
                code { background: #ddd; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>LMS API Сервер</h1>
            <p>Сервер успешно запущен! Доступные эндпоинты:</p>

            <div class="endpoint">
                <h3>Админ-панель:</h3>
                <code><a href="/admin/">/admin/</a></code>
            </div>

            <div class="endpoint">
                <h3>Курсы:</h3>
                <code><a href="/api/courses/">/api/courses/</a></code> - список курсов<br>
                <code>/api/courses/{id}/</code> - конкретный курс
            </div>

            <div class="endpoint">
                <h3>Уроки:</h3>
                <code><a href="/api/lessons/">/api/lessons/</a></code> - список уроков<br>
                <code>/api/lessons/{id}/</code> - конкретный урок
            </div>

            <p>Используйте Postman для отправки POST, PUT, DELETE запросов.</p>
        </body>
    </html>
    """
    return HttpResponse(html)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('materials.urls')),
    path('', home),  # Добавляем главную страницу
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)