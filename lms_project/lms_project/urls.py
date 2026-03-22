from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet, PaymentViewSet
from materials.views import CourseViewSet, LessonListCreateView, LessonRetrieveUpdateDestroyView

# Создаем единый роутер для всех ViewSet
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # Уроки оставляем как есть, потому что они используют generic views
    path('api/lessons/', LessonListCreateView.as_view(), name='lesson-list'),
    path('api/lessons/<int:pk>/', LessonRetrieveUpdateDestroyView.as_view(), name='lesson-detail'),
    path('api/auth/', include('users.urls')),  # Все эндпоинты авторизации
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)